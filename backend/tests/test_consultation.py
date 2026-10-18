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


@pytest.mark.parametrize('sort_by,expected', [('top_rated',['popular','few_reviews','lower_rating','unrated']),('nearest',['lower_rating','few_reviews','popular','unrated'])])
def test_google_ratings_sort_returned_nearby_matches(monkeypatch,sort_by,expected):
    places=[]
    for identity,rating,count,offset in [('lower_rating',4.2,500,.001),('few_reviews',4.8,2,.002),('popular',4.8,100,.003),('unrated',None,None,.004)]:
        item={'id':identity,'displayName':{'text':identity},'formattedAddress':'Test address','location':{'latitude':19+offset,'longitude':73},'businessStatus':'OPERATIONAL'}
        if rating is not None: item.update(rating=rating,userRatingCount=count)
        places.append(item)
    calls=mock_google(monkeypatch,places=places)
    result=asyncio.run(service.discover_providers(query='Panvel',sort_by=sort_by))
    assert [provider['id'] for provider in result['providers']]==expected
    assert result['providers'][-1]['rating'] is None
    assert 'places.rating' in calls[1].headers['X-Goog-FieldMask']
    assert 'places.userRatingCount' in calls[1].headers['X-Goog-FieldMask']


@pytest.mark.parametrize('canonical,specialty,query',[('glucose_fasting','endocrinology','endocrinology clinic'),('creatinine_serum','nephrology','nephrology clinic'),('cholesterol_total','cardiology','cardiology clinic')])
def test_panvel_search_defaults_to_report_relevant_specialty(monkeypatch,canonical,specialty,query):
    from app.api.endpoints.reports import REPORTS_DB
    REPORTS_DB['test_report']={'extractions':[{'canonical_name':canonical,'name':'Private test measurement','value':'140','unit':'mg/dL','status':'high','requires_verification':False}],'answers':[]}
    calls=mock_google(monkeypatch)
    response=TestClient(app).get('/api/v1/reports/test_report/doctors?city=Panvel')
    assert response.status_code==200
    assert response.json()['selected_specialty_id']==specialty
    assert calls[0].url.params['address']=='Panvel'
    assert json.loads(calls[1].content)['textQuery']==query
    assert all('Private test measurement' not in request.content.decode() for request in calls)
    assert response.json()['sort_by']=='top_rated'


def test_uncertain_results_do_not_choose_a_specialist():
    from app.services.specialty_recommender import generate_specialty_recommendations
    recommendations=generate_specialty_recommendations([{'canonical_name':'glucose_fasting','status':'needs_review','requires_verification':False}])
    assert [item.specialty_id for item in recommendations]==['general_physician']


@pytest.mark.parametrize('place',['Panvel','New Panvel','Karjat','Mangaon','Digras'])
def test_smaller_locations_are_forwarded_without_mumbai_default(monkeypatch,place):
    calls=mock_google(monkeypatch)
    asyncio.run(service.discover_providers(query=place))
    assert calls[0].url.params['address']==place


@pytest.mark.parametrize('query',['123','000000','1234567'])
def test_invalid_indian_pin_is_rejected(monkeypatch,query):
    calls=mock_google(monkeypatch)
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query=query))
    assert error.value.status_code==422
    assert calls==[]


def test_partial_location_requires_clarification(monkeypatch):
    client_type=httpx.AsyncClient
    monkeypatch.setenv('GOOGLE_MAPS_SERVER_KEY','test-key')
    monkeypatch.setattr(service.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(lambda request:httpx.Response(200,json={'status':'OK','results':[{'partial_match':True}]})),**kwargs))
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query='Ambiguous village'))
    assert error.value.status_code==422


@pytest.mark.parametrize('status',[401,403,500])
def test_google_auth_or_service_failure_is_controlled(monkeypatch,status):
    mock_google(monkeypatch,status=status)
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query='Panvel'))
    assert error.value.status_code==503


def test_no_contact_or_rating_is_invented(monkeypatch):
    mock_google(monkeypatch,places=[{'id':'no_contact','location':{'latitude':19.001,'longitude':73.0}}])
    result=asyncio.run(service.discover_providers(query='Panvel'))
    item=result['providers'][0]
    assert item['phone'] is None and item['rating'] is None and item['user_rating_count'] is None
    assert item['consultation_options']==[] and item['available_slots']==[]


def test_google_network_failure_does_not_leak_provider_key(monkeypatch):
    client_type=httpx.AsyncClient
    monkeypatch.setenv('GOOGLE_MAPS_SERVER_KEY','test-private-key')
    def unavailable(request):raise httpx.ConnectError('private upstream details')
    monkeypatch.setattr(service.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(unavailable),**kwargs))
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query='Panvel'))
    assert error.value.status_code==503
    assert 'test-private-key' not in error.value.detail and 'private upstream' not in error.value.detail
