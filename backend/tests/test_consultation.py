import asyncio
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.services import provider_discovery as service

CITIES=['Mumbai','Pune','Thane','Kalyan','Nashik','Nagpur','Chhatrapati Sambhajinagar','Kolhapur','Solapur','Amravati','Yavatmal','Pusad','Nanded','Ratnagiri','Gadchiroli','Panvel']

def facility(identity=1, offset=.001, **tags):
    return {'type':'node','id':identity,'lat':19+offset,'lon':73.,'tags':{'name':'Fixture clinic','healthcare':'clinic','phone':'+91 1234567890','website':'https://example.org/clinic',**tags}}

def mock_osm(monkeypatch,elements=None,status=200,geo=None):
    calls=[]; client_type=httpx.AsyncClient
    def handle(request):
        calls.append(request)
        if '/search' in str(request.url):
            return httpx.Response(200,json=geo if geo is not None else [{'lat':'19','lon':'73','display_name':'Requested place, Maharashtra, India','address':{'country_code':'in'}}])
        return httpx.Response(status,json={'elements':elements if elements is not None else [facility()]})
    monkeypatch.setattr(service.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(handle),**kwargs))
    return calls

@pytest.mark.parametrize('city',CITIES)
def test_discovery_preserves_requested_location(monkeypatch,city):
    calls=mock_osm(monkeypatch)
    result=asyncio.run(service.discover_providers(query=city))
    assert calls[0].url.params['q']==city
    assert calls[0].url.params['featureType']=='settlement'
    assert calls[0].url.params['countrycodes']=='in'
    assert 'Simplifier' in calls[0].headers['User-Agent']
    item=result['providers'][0]
    assert item['id']=='osm:node/1' and item['verification_status']=='source_listed'
    assert item['available_slots']==[] and item['rating'] is None
    assert {v['type'] for v in item['consultation_options']}=={'call','website'}
    assert 'openstreetmap.org' in item['directions_url']
    assert all('report' not in str(r.url)+r.content.decode() for r in calls)

@pytest.mark.parametrize('status,expected',[(429,429),(509,429),(403,503),(500,503),(504,503)])
def test_service_failures(monkeypatch,status,expected):
    calls=mock_osm(monkeypatch,status=status)
    with pytest.raises(HTTPException) as error: asyncio.run(service.discover_providers(query='Panvel'))
    assert error.value.status_code==expected
    assert len(calls)==2


def test_empty_results_do_not_expand_or_fabricate(monkeypatch):
    calls=mock_osm(monkeypatch,elements=[])
    result=asyncio.run(service.discover_providers(query='Pusad',radius_m=5000))
    assert result['providers']==[] and result['searched_radius_m']==5000 and len(calls)==2


def test_contact_validation_no_invented_fields(monkeypatch):
    calls=mock_osm(monkeypatch,elements=[facility(phone='invalid',website='javascript:alert(1)'),{'type':'node','id':2,'lat':19.,'lon':73.,'tags':{'healthcare':'doctor'}}, {'type':'node','id':3,'tags':{'name':'No coordinates','healthcare':'doctor'}}])
    item=asyncio.run(service.discover_providers(query='Panvel'))['providers'][0]
    assert item['phone'] is None and item['website'] is None
    assert item['consultation_options']==[] and item['available_slots']==[]
    assert item['address']=='' and item['rating'] is None


def test_nearest_only_and_way_centers(monkeypatch):
    far=facility(2,.02);far['type']='way';far['center']={'lat':far.pop('lat'),'lon':far.pop('lon')}
    mock_osm(monkeypatch,elements=[far,facility(),facility(3,.9)])
    result=asyncio.run(service.discover_providers(lat=19.,lng=73.))
    assert [v['id'] for v in result['providers']]==['osm:node/1','osm:way/2']
    with pytest.raises(HTTPException):asyncio.run(service.discover_providers(lat=19.,lng=73.,sort_by='top_rated'))

@pytest.mark.parametrize('canonical,specialty',[('glucose_fasting','endocrinology'),('creatinine_serum','nephrology'),('cholesterol_total','cardiology')])
def test_report_specialty_remains_local(monkeypatch,canonical,specialty):
    from app.api.endpoints.reports import REPORTS_DB
    REPORTS_DB['test_report']={'extractions':[{'canonical_name':canonical,'name':'Private measurement','value':'140','unit':'mg/dL','status':'high','requires_verification':False}],'answers':[]}
    calls=mock_osm(monkeypatch,elements=[facility(**{'healthcare:speciality':specialty}),facility(2,.002),facility(3,.003,**{'healthcare:speciality':'dentistry'})])
    response=TestClient(app).get('/api/v1/reports/test_report/doctors?city=Panvel')
    assert response.status_code==200
    data=response.json()
    assert data['selected_specialty_id']==specialty and data['sort_by']=='nearest'
    assert len(data['providers'])==1
    assert all(specialty not in r.content.decode() and 'Private measurement' not in r.content.decode() for r in calls)

@pytest.mark.parametrize('query',['123','000000','1234567','<script>','x','a\nplace'])
def test_invalid_query_does_not_reach_upstream(monkeypatch,query):
    calls=mock_osm(monkeypatch)
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query=query))
    assert error.value.status_code==422 and calls==[]

@pytest.mark.parametrize('geo,expected',[([],404),([{'lat':'19','lon':'73'},{'lat':'20','lon':'74'}],422),([{'lat':'19','lon':'73','address':{'country_code':'us'}}],422)])
def test_missing_or_ambiguous_locations(monkeypatch,geo,expected):
    mock_osm(monkeypatch,geo=geo)
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query='Ambiguous village'))
    assert error.value.status_code==expected


def test_pin_cache_survives_repeated_calls_and_language_specialty_not_sent(monkeypatch):
    calls=mock_osm(monkeypatch)
    for _ in range(2):asyncio.run(service.discover_providers(query='410206'))
    assert len(calls)==2
    assert calls[0].url.params['postalcode']=='410206' and 'q' not in calls[0].url.params


def test_global_rate_limit_prevents_upstream_call(monkeypatch):
    calls=mock_osm(monkeypatch)
    asyncio.run(service.discover_providers(query='Panvel'))
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query='Pune'))
    assert error.value.status_code==429 and len(calls)==2


def test_upstream_timeout_controlled(monkeypatch):
    client_type=httpx.AsyncClient
    def fail(request):raise httpx.ReadTimeout('private upstream detail')
    monkeypatch.setattr(service.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(fail),**kwargs))
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query='Panvel'))
    assert error.value.status_code==503 and 'private' not in error.value.detail


def test_disabled_service_and_bad_coordinates(monkeypatch):
    calls=mock_osm(monkeypatch)
    for coords in [(float('nan'),73),(19,None),(100,73)]:
        with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(lat=coords[0],lng=coords[1]))
        assert error.value.status_code==422
    monkeypatch.setenv('OSM_DISCOVERY_ENABLED','false')
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(query='Panvel'))
    assert error.value.status_code==503 and calls==[]


def test_partial_overpass_is_not_empty_success(monkeypatch):
    client_type=httpx.AsyncClient
    monkeypatch.setattr(service.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'elements':[],'remark':'runtime timeout'})),**kwargs))
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(lat=19.,lng=73.))
    assert error.value.status_code==503


def test_consultation_pdf_requires_explicit_consent():
    with TestClient(app) as client:
        prep=client.get('/api/v1/consultation/preparation/rep_demo_fixture')
        assert prep.status_code==200 and prep.json()['sharing_status']=='not_shared'
        assert prep.json()['booking_status']=='not_booked'
        assert client.post('/api/v1/consultation/pdf',json={'report_id':'rep_demo_fixture'}).status_code==403
        response=client.post('/api/v1/consultation/pdf',json={'report_id':'rep_demo_fixture','consent_to_include_report':True})
        assert response.status_code==200 and response.content.startswith(b'%PDF')
        assert response.headers['X-Report-Sharing']=='not-shared'


def test_uncertain_results_do_not_choose_a_specialist():
    from app.services.specialty_recommender import generate_specialty_recommendations
    recs=generate_specialty_recommendations([{'canonical_name':'glucose_fasting','status':'needs_review','requires_verification':False}])
    assert [v.specialty_id for v in recs]==['general_physician']

@pytest.mark.parametrize('radius',[999,50001])
def test_radius_bounds_before_network(monkeypatch,radius):
    calls=mock_osm(monkeypatch)
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(lat=19.,lng=73.,radius_m=radius))
    assert error.value.status_code==422 and calls==[]


def test_daily_limit_is_persistent(monkeypatch):
    calls=mock_osm(monkeypatch)
    with service.closing(service.cache_connection()) as conn, conn:
        conn.execute('INSERT INTO limits VALUES(?,?,?,?)',('facilities',0,int(service.time.time()//86400),100))
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(lat=19.,lng=73.))
    assert error.value.status_code==429 and calls==[]


def test_malformed_upstream_body_is_service_error(monkeypatch):
    client_type=httpx.AsyncClient
    monkeypatch.setattr(service.httpx,'AsyncClient',lambda **kwargs:client_type(transport=httpx.MockTransport(lambda r:httpx.Response(200,content=b'not JSON')),**kwargs))
    with pytest.raises(HTTPException) as error:asyncio.run(service.discover_providers(lat=19.,lng=73.))
    assert error.value.status_code==503
