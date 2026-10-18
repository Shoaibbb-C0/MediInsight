import pytest
import pymupdf
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.core import auth

pytestmark=pytest.mark.real_identity

def pdf():
    doc=pymupdf.open();page=doc.new_page();page.insert_text((40,60),'Fasting Blood Glucose : 124.5 mg/dL (70 - 99 mg/dL)');return doc.tobytes()

def test_sessions_isolate_medical_reports_and_consultation_pdfs(monkeypatch):
    monkeypatch.delenv('SUPABASE_URL',raising=False);monkeypatch.delenv('SUPABASE_PUBLISHABLE_KEY',raising=False)
    first=TestClient(app);second=TestClient(app)
    report_id=first.post('/api/v1/reports/upload',files={'file':('one.pdf',pdf(),'application/pdf')}).json()['report_id']
    assert first.get(f'/api/v1/reports/{report_id}/summary').status_code==200
    assert second.get(f'/api/v1/reports/{report_id}/summary').status_code==404
    assert second.get('/api/v1/reports/history/list').json()['reports']==[]
    assert second.get(f'/api/v1/reports/{report_id}/doctors?city=Panvel').status_code==404
    assert first.get(f'/api/v1/reports/{report_id}/doctors').json()['location_required'] is True
    assert second.post('/api/v1/consultation/pdf',json={'report_id':report_id,'consent_to_include_report':True}).status_code==404
    assert first.get('/api/v1/reports/history/list').json()['reports'][0]['id']==report_id
    assert first.post('/api/v1/auth/logout').status_code==200
    assert first.get(f'/api/v1/reports/{report_id}/summary').status_code==404

def test_production_requires_verified_identity(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT','production')
    monkeypatch.setenv('SUPABASE_URL','https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','test-public-key')
    client=TestClient(app)
    assert client.get('/api/v1/reports/history/list').status_code==401
    client_type=httpx.AsyncClient
    monkeypatch.setattr(auth.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(lambda request:httpx.Response(401,json={})),**kwargs))
    assert client.get('/api/v1/reports/history/list',headers={'Authorization':'Bearer forged-token'}).status_code==401

def test_verified_identity_comes_from_auth_server_not_user_input(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL','https://example.supabase.co');monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','test-public-key')
    client_type=httpx.AsyncClient
    def handle(request):
        assert request.url.path=='/auth/v1/user'
        assert request.headers['authorization']=='Bearer test-token'
        return httpx.Response(200,json={'id':'verified-user','user_metadata':{'user_id':'attacker-chosen'}})
    monkeypatch.setattr(auth.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(handle),**kwargs))
    response=TestClient(app).get('/api/v1/auth/session?user_id=attacker-chosen',headers={'Authorization':'Bearer test-token'})
    assert response.json()['user_id']=='verified-user'

def test_browser_origin_rejected_before_medical_processing():
    response=TestClient(app).post('/api/v1/reports/upload',headers={'Origin':'https://untrusted.example'})
    assert response.status_code==403


def test_nutrition_consultation_and_deletion_respect_owner(monkeypatch):
    monkeypatch.setenv('AUTH_MODE','local')
    first=TestClient(app);second=TestClient(app)
    report_id=first.post('/api/v1/reports/upload',files={'file':('owned.pdf',pdf(),'application/pdf')}).json()['report_id']
    payload={'report_id':report_id,'age_group':'adult','allergies':['none'],'known_conditions':[],'dietary_preference':'vegetarian','user_id':'client-forged-owner'}
    response=first.post(f'/api/v1/reports/{report_id}/nutrition/generate',json=payload)
    assert response.status_code==200
    plan=response.json()
    assert plan['user_id']!='client-forged-owner'
    assert second.get(f'/api/v1/reports/{report_id}/nutrition/plan').status_code==404
    assert second.get(f'/api/v1/consultation/preparation/{report_id}').status_code==404
    assert second.get(f'/api/v1/reports/{report_id}/nutrition/pdf').status_code==404
    assert second.post('/api/v1/reports/nutrition/swap',json={'plan_id':plan['plan_id'],'day_number':1,'meal_type':'breakfast','new_meal_id':plan['days'][0]['breakfast']['alternatives'][0]['id']}).status_code==404
    assert second.delete(f'/api/v1/reports/{report_id}').status_code==404
    assert first.delete(f'/api/v1/reports/{report_id}').status_code==200
    assert first.get(f'/api/v1/reports/{report_id}/summary').status_code==404
    assert first.get(f'/api/v1/reports/{report_id}/nutrition/plan').status_code==404
