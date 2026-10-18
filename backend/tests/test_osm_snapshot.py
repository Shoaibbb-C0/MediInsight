import asyncio
import json
from pathlib import Path
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.services import provider_discovery as service
from app.services import snapshot_discovery as local

@pytest.fixture
def no_network(monkeypatch):
    async def fail(*args,**kwargs):raise AssertionError('Covered search attempted upstream access')
    monkeypatch.setattr(service,'upstream_json',fail)
    monkeypatch.setenv('OSM_DISCOVERY_ENABLED','false')

@pytest.mark.parametrize('place',['Mumbai','Colaba','Dadar','Bandra','Andheri','Borivali','Dahisar','Mulund','Ghatkopar','Kurla','Chembur','Navi Mumbai','Thane','Panvel','Kalyan','Dombivli','मुंबई','ठाणे','पनवेल','Mumbai, Maharashtra, India','South Mumbai','Central Mumbai','Western Suburbs','Eastern Suburbs','Kalyan-Dombivli','Bandra, Mumbai'])
def test_region_search_is_real_snapshot_without_network(no_network,place):
    result=asyncio.run(service.discover_providers(query=place,radius_m=10000))
    assert result['data_source']=='osm_snapshot' and result['snapshot_version']=='mumbai-v1'
    assert result['snapshot_retrieved_at'] and result['providers']
    for p in result['providers']:
        assert p['id'].startswith('osm:') and p['maps_url'].startswith('https://www.openstreetmap.org/')
        assert p['source']=='external_discovery' and p['available_slots']==[]
        assert p['rating'] is None and p['user_rating_count'] is None
    assert [p['distance_km'] for p in result['providers']]==sorted(p['distance_km'] for p in result['providers'])

@pytest.mark.parametrize('lat,lng',[(18.9067,72.8147),(19.25,72.86),(19.18,72.96),(19.03,73.02),(19.22,72.98),(18.99,73.12),(19.24,73.13)])
def test_gps_and_radius_are_offline(no_network,lat,lng):
    result=asyncio.run(service.discover_providers(lat=lat,lng=lng,radius_m=5000))
    assert result['data_source']=='osm_snapshot'
    assert not result['resolved_location']['is_approximate']
    assert all(p['distance_km']<=5 for p in result['providers'])

@pytest.mark.parametrize('pin',['400001','400014','400050','400058','400066','400080','400601','410206'])
def test_indexed_postal_codes_are_offline_and_explicitly_approximate(no_network,pin):
    result=asyncio.run(service.discover_providers(query=pin))
    assert result['data_source']=='osm_snapshot' and result['resolved_location']['pincode']==pin
    assert result['resolved_location']['is_approximate'] is True


def test_missing_regional_pin_is_not_fabricated_or_sent_upstream(no_network):
    pins={p['pincode'] for p in local.snapshot()['pincodes']}
    pin=next(str(p) for p in range(400001,400999) if str(p) not in pins)
    with pytest.raises(HTTPException) as e:asyncio.run(service.discover_providers(query=pin))
    assert e.value.status_code==422


def test_source_tags_are_required_for_specialty(no_network):
    result=asyncio.run(service.discover_providers(query='Mumbai',radius_m=50000,specialty='cardiology clinic'))
    raw={f"osm:{p['type']}/{p['id']}":p for p in local.snapshot()['facilities']}
    assert result['specialty_data_sparse'] is True
    for p in result['providers']:
        tags=raw[p['id']]['tags']
        assert 'cardiology' in tags.get('healthcare:speciality',tags.get('healthcare:specialty','')).split(';')
    general=asyncio.run(service.discover_providers(query='Mumbai',radius_m=50000))
    assert general['total_matches']>=result['total_matches']


def test_raw_tags_preserve_missing_data_and_provenance(no_network):
    data=local.snapshot()
    assert len(data['source_sha256'])==64 and data['license']=='ODbL-1.0'
    assert len(data['facilities'])>100
    assert data['unnamed_facilities']>0
    raw=next(p for p in data['facilities'] if p['tags'].get('name') and not p['tags'].get('phone') and not p['tags'].get('contact:phone'))
    providers=service.normalize_providers([raw],raw['lat'],raw['lon'],1000,'general physician','en','Snapshot',data['retrieved_at'])
    assert len(providers)==1 and providers[0]['phone'] is None
    assert not any(o['type']=='call' for o in providers[0]['consultation_options'])


def test_boundary_is_disclosed_and_does_not_expand_live(no_network):
    result=asyncio.run(service.discover_providers(lat=19.49,lng=73.34,radius_m=50000))
    assert result['coverage_edge'] and result['data_source']=='osm_snapshot'


@pytest.mark.parametrize('query',['Pune','411001'])
def test_outside_region_retains_live_adapter(monkeypatch,query):
    calls=[]
    async def fake(kind,*args,**kwargs):
        calls.append(kind)
        return [{'lat':'18.52','lon':'73.85','display_name':'Pune, India','address':{'country_code':'in'}}] if kind=='geocode' else {'elements':[]}
    monkeypatch.setattr(service,'upstream_json',fake)
    monkeypatch.setenv('OSM_DISCOVERY_ENABLED','true')
    result=asyncio.run(service.discover_providers(query=query))
    assert calls==['geocode','facilities'] and result['providers']==[]
    assert result.get('data_source')!='osm_snapshot'


def test_authenticated_report_endpoint_exposes_snapshot_metadata(no_network):
    response=TestClient(app).get('/api/v1/reports/rep_demo_fixture/doctors?city=Mumbai&specialty_id=general_physician')
    assert response.status_code==200
    value=response.json()
    assert value['data_source']=='osm_snapshot' and value['is_demo_mode'] is False
    assert value['total_count']>=len(value['providers']) and value['coverage_notice']
