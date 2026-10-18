import asyncio
import json
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.services import provider_discovery as service

CITIES=['Mumbai','Pune','Thane','Kalyan','Nashik','Nagpur','Chhatrapati Sambhajinagar','Kolhapur','Solapur','Amravati','Yavatmal','Pusad','Nanded','Ratnagiri','Gadchiroli']

def mock_google(monkeypatch,places=None,status=200):
    calls=[]; client_type=httpx.AsyncClient
    def handle(request):
        calls.append(request)
        if 'geocode' in str(request.url):
            return httpx.Response(200,json={'status':'OK','results':[{'formatted_address':'Requested place, Maharashtra, India','address_components':[{'types':['country'],'short_name':'IN'}],'geometry':{'location':{'lat':19.0,'lng':73.0}}}]})
        return httpx.Response(status,json={'places':places if places is not None else [{'id':'test_place','displayName':{'text':'Fixture clinic'},'formattedAddress':'Fixture address','location':{'latitude':19.001,'longitude':73.0},'internationalPhoneNumber':'+911234567890','websiteUri':'https://example.org/clinic','businessStatus':'OPERATIONAL'}]})
    monkeypatch.setattr(service.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(handle),**kwargs))
    monkeypatch.setenv('GOOGLE_MAPS_SERVER_KEY','test-server-key')
    return calls

@pytest.mark.parametrize('city',CITIES)
def test_consultation_discovery_preserves_requested_maharashtra_location(monkeypatch,city):
    calls=mock_google(monkeypatch)
    result=asyncio.run(service.discover_providers(query=city))
    assert calls[0].url.params['address']==city
    provider=result['providers'][0]
    assert provider['verification_status']=='source_listed'
    assert provider['available_slots']==[]
    assert {item['type'] for item in provider['consultation_options']}=={'call','website'}
    assert all('report' not in str(request.url) for request in calls)
    assert 'test-server-key' not in json.dumps(result)
    body=json.loads(calls[1].content)
    assert set(body)=={'textQuery','languageCode','regionCode','pageSize','locationBias'}
    assert 'test_place' in provider['directions_url']

def test_no_key_no_fake_providers(monkeypatch):
    monkeypatch.delenv('GOOGLE_MAPS_SERVER_KEY',raising=False)
    with pytest.raises(HTTPException) as exc:asyncio.run(service.discover_providers(query='Pusad'))
    assert exc.value.status_code==503

def test_provider_rate_limit_is_not_success(monkeypatch):
    mock_google(monkeypatch,status=429)
    with pytest.raises(HTTPException) as exc:asyncio.run(service.discover_providers(query='Nagpur'))
    assert exc.value.status_code==429

def test_zero_results_remain_empty_and_expand(monkeypatch):
    calls=mock_google(monkeypatch,places=[])
    result=asyncio.run(service.discover_providers(query='Pusad',radius_m=5000))
    assert result['providers']==[]
    assert result['searched_radius_m']==10000
    assert len(calls)==3

def test_only_evidenced_extra_consultation_types(monkeypatch,tmp_path):
    path=tmp_path/'capabilities.json'
    path.write_text(json.dumps({'p':{'source_url':'https://example.org/consultation','reviewed_at':__import__('datetime').date.today().isoformat(),'booking_url':'https://example.org/book','online_consultation_url':'https://example.org/video','whatsapp_number':'+911234567890','whatsapp_consultation_supported':True}}))
    monkeypatch.setenv('PROVIDER_CAPABILITIES_FILE',str(path))
    options=service.capabilities('p',None,None)
    assert {item['type'] for item in options}=={'external_booking','online','whatsapp'}
    assert all('report' not in item['url'] and 'glucose' not in item['url'] for item in options)
    assert service.capabilities('unknown',None,None)==[]
    assert service.safe_url('javascript:alert(1)') is None

def test_consultation_pdf_requires_explicit_consent():
    with TestClient(app) as client:
        prep=client.get('/api/v1/consultation/preparation/rep_demo_fixture')
        assert prep.status_code==200
        assert prep.json()['sharing_status']=='not_shared'
        assert prep.json()['booking_status']=='not_booked'
        assert client.post('/api/v1/consultation/pdf',json={'report_id':'rep_demo_fixture'}).status_code==403
        response=client.post('/api/v1/consultation/pdf',json={'report_id':'rep_demo_fixture','consent_to_include_report':True})
        assert response.status_code==200
        assert response.content.startswith(b'%PDF')
        assert response.headers['X-Report-Sharing']=='not-shared'
