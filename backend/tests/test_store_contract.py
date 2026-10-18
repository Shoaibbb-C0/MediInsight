import json
import httpx
import pytest
from fastapi import HTTPException
from app.core.auth import owner_context, token_context
from app.core.store import OwnedStore


def test_production_store_passes_patient_jwt_and_never_service_role(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT','production')
    monkeypatch.setenv('SUPABASE_URL','https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','public-key')
    calls=[]
    def handle(method,url,**kwargs):
        calls.append((method,url,kwargs))
        assert kwargs['headers']['Authorization']=='Bearer patient-token'
        assert kwargs['headers']['apikey']=='public-key'
        assert 'service_role' not in str(kwargs)
        if method=='POST':
            assert kwargs['json']['owner_id']=='patient-a'
            assert kwargs['json']['namespace']=='reports'
        else:
            assert kwargs['params']['owner_id']=='eq.patient-a'
        if method=='GET': return httpx.Response(200,json=[{'state_key':'r','payload':{'report_id':'r'}}])
        return httpx.Response(200,json=[])
    monkeypatch.setattr(httpx,'request',handle)
    owner=owner_context.set('patient-a');token=token_context.set('patient-token')
    try:
        store=OwnedStore('reports')
        store['r']={'report_id':'r'}
        assert store['r']=={'report_id':'r'}
        assert list(store)==['r']
        del store['r']
    finally: owner_context.reset(owner);token_context.reset(token)
    assert {call[0] for call in calls}=={'GET','POST','DELETE'}


@pytest.mark.parametrize('payload',[{},None,[{}],[{'state_key':'r'}]])
def test_malformed_cloud_state_is_controlled(monkeypatch,payload):
    monkeypatch.setenv('ENVIRONMENT','production')
    monkeypatch.setenv('SUPABASE_URL','https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','public-key')
    monkeypatch.setattr(httpx,'request',lambda *args,**kwargs:httpx.Response(200,json=payload))
    token=token_context.set('patient-token')
    try:
        with pytest.raises(HTTPException) as error: OwnedStore('reports')['r']
        assert error.value.status_code==503
    finally: token_context.reset(token)


def test_local_store_reopens_and_keeps_patient_namespaces_separate():
    owner=owner_context.set('patient-a')
    try:
        OwnedStore('reports')['r']={'source_value':'124.5'}
        OwnedStore('nutrition')['p']={'report_id':'r'}
        assert OwnedStore('reports')['r']=={'source_value':'124.5'}
        owner_context.set('patient-b')
        assert list(OwnedStore('reports'))==[]
        assert list(OwnedStore('nutrition'))==[]
        owner_context.set('patient-a')
        assert OwnedStore('nutrition')['p']['report_id']=='r'
    finally: owner_context.reset(owner)
