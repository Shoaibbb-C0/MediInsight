"""OSM discovery: only location is sent upstream; specialty filtering stays local."""
import datetime
import json
import math
import os
import re
import sqlite3
import time
from contextlib import closing
from urllib.parse import urlencode, urlsplit
import httpx
from fastapi import HTTPException
from app.core.config import data_directory
from app.services.location_service import haversine_distance_km
from app.services.snapshot_discovery import resolve_snapshot

SPECIALTIES = {
    'general physician': None,
    'endocrinology clinic': {'endocrinology'},
    'nephrology clinic': {'nephrology'},
    'cardiology clinic': {'cardiology'},
    'hematology clinic': {'haematology', 'hematology'},
    'gastroenterology clinic': {'gastroenterology'},
    'rheumatology clinic': {'rheumatology'},
}
ATTRIBUTION = {'provider': '© OpenStreetMap contributors', 'providerUri': 'https://www.openstreetmap.org/copyright'}


def safe_url(value):
    if not isinstance(value, str) or len(value) > 2048: return None
    try: parts = urlsplit(value)
    except ValueError: return None
    if parts.scheme not in {'https', 'http'} or not parts.hostname or parts.username or parts.password: return None
    return value


def capabilities(place_id, phone, website):
    # Contact links do not transmit a report or create an appointment.
    result = []
    if phone: result.append({'type': 'call', 'url': 'tel:'+phone, 'evidence': 'OSM contact:phone/phone tag'})
    if website: result.append({'type': 'website', 'url': website, 'evidence': 'OSM contact:website/website tag'})
    return result


def cache_connection():
    folder = data_directory()
    folder.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(folder / 'osm_discovery.sqlite3', timeout=2)
    conn.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, expires REAL, payload TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS limits (service TEXT PRIMARY KEY, next REAL, day INTEGER, count INTEGER)')
    return conn


async def upstream_json(service, method, url, cache_key, ttl, **kwargs):
    """Persistent bounded cache and cross-worker limits on ONE shared filesystem.

    Public mode requires one deployment replica. Never rotate mirrors to evade
    limits. A rejected search is retried by a later explicit patient action.
    """
    try:
        with closing(cache_connection()) as conn:
            now = time.time()
            with conn:
                conn.execute('BEGIN IMMEDIATE')
                row = conn.execute('SELECT payload FROM cache WHERE key=? AND expires>?', (cache_key, now)).fetchone()
                if row: return json.loads(row[0])
                row = conn.execute('SELECT next,day,count FROM limits WHERE service=?', (service,)).fetchone()
                day = int(now // 86400)
                count = row[2] if row and row[1] == day else 0
                # Deliberately below public limits; aggregate across all users.
                if (row and row[0] > now) or count >= (500 if service == 'geocode' else 100):
                    raise HTTPException(429, 'Location/provider search limit reached. Please try later.', headers={'Retry-After': '60'})
                conn.execute('INSERT OR REPLACE INTO limits VALUES(?,?,?,?)', (service, now + (1.1 if service == 'geocode' else 5), day, count + 1))
        user_agent = os.getenv('OSM_USER_AGENT', 'Simplifier2.0/1.0 (+https://github.com/Shoaibbb-C0/Simplifier2.0)')
        if len(user_agent) < 12 or '\n' in user_agent or '\r' in user_agent: raise HTTPException(503, 'OSM identification configuration is invalid.')
        async with httpx.AsyncClient(timeout=httpx.Timeout(25, connect=5), follow_redirects=False) as client:
            async with client.stream(method, url, headers={'User-Agent': user_agent, 'Accept': 'application/json'}, **kwargs) as response:
                if response.status_code in {429, 509}:
                    # Shared cooldown survives process restarts, without retry storms.
                    with closing(cache_connection()) as conn, conn:
                        conn.execute('UPDATE limits SET next=? WHERE service=?', (time.time()+60, service))
                    raise HTTPException(429, 'Location/provider search limit reached. Please try later.', headers={'Retry-After': '60'})
                if not response.is_success: raise HTTPException(503, 'Location/provider service temporarily unavailable. Please try later.')
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > 8_000_000: raise ValueError('Response too large')
                data = json.loads(content)
        expected = list if service == 'geocode' else dict
        if not isinstance(data, expected) or (service == 'facilities' and (not isinstance(data.get('elements'), list) or data.get('remark'))): raise ValueError('Incomplete upstream response')
        with closing(cache_connection()) as conn, conn:
            conn.execute('DELETE FROM cache WHERE expires<=?', (time.time(),))
            conn.execute('INSERT OR REPLACE INTO cache VALUES(?,?,?)', (cache_key, time.time()+ttl, json.dumps(data)))
            conn.execute('DELETE FROM cache WHERE key NOT IN (SELECT key FROM cache ORDER BY expires DESC LIMIT 300)')
        return data
    except (httpx.HTTPError, ValueError, OSError, sqlite3.Error):
        raise HTTPException(503, 'Location/provider service temporarily unavailable. Please try later.') from None


def endpoint(name, default):
    value = os.getenv(name, default)
    if not safe_url(value) or not value.startswith('https://'): raise HTTPException(503, 'OSM service configuration is invalid.')
    return value


def valid_point(lat, lng):
    return all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (lat, lng)) and -90 <= lat <= 90 and -180 <= lng <= 180


async def discover_providers(query=None, lat=None, lng=None, radius_m=10000, specialty='general physician', language='en', sort_by='nearest'):
    if sort_by != 'nearest': raise HTTPException(422, 'Only nearest sorting is available.')
    if specialty not in SPECIALTIES or language not in {'en','hi','mr'}: raise HTTPException(422, 'Unsupported specialty or language.')
    if not isinstance(radius_m, int) or not 1000 <= radius_m <= 50000: raise HTTPException(422, 'Choose a radius from 1 to 50 km.')
    label = 'Selected coordinates'
    if query is not None:
        query = query.strip()
        if not 2 <= len(query) <= 120 or any(ord(c) < 32 for c in query) or not all(c.isalnum() or c.isspace() or c in ",.-'()" or '\u0900' <= c <= '\u097f' for c in query) or (query.isdigit() and (len(query) != 6 or query[0] == '0')):
            raise HTTPException(422, 'Enter a valid place or six-digit Indian PIN.')
    local = resolve_snapshot(query,lat,lng)
    if local: return snapshot_result(local,radius_m,specialty,language)
    if os.getenv('OSM_DISCOVERY_ENABLED', 'true').lower() != 'true': raise HTTPException(503, 'Live location/provider service is disabled. Covered Mumbai snapshot searches remain available.')
    if query is not None:
        params = {'format':'jsonv2', 'addressdetails':1, 'countrycodes':'in', 'limit':3, 'accept-language':language}
        params.update({'postalcode':query, 'country':'India'} if query.isdigit() else {'q':query, 'featureType':'settlement'})
        url = endpoint('OSM_NOMINATIM_URL', 'https://nominatim.openstreetmap.org/search')
        data = await upstream_json('geocode','GET',url,'geo:'+url+json.dumps(params,sort_keys=True),86400,params=params)
        if not data: raise HTTPException(404, 'Location not found. Try a nearby town or PIN.')
        if len(data) != 1: raise HTTPException(422, 'Location is ambiguous. Include state or use a precise PIN.')
        item = data[0]
        if not isinstance(item,dict) or not isinstance(item.get('address'),dict) or item['address'].get('country_code') != 'in': raise HTTPException(422, 'Choose a location in India.')
        try: lat, lng = float(item['lat']), float(item['lon']); label = str(item['display_name'])[:500]
        except (ValueError,TypeError,KeyError): raise HTTPException(503, 'Location/provider service temporarily unavailable. Please try later.') from None
    if not valid_point(lat,lng): raise HTTPException(422, 'Enter a city/PIN or allow a valid location.')
    local = resolve_snapshot(None,lat,lng)
    if local: return snapshot_result(local,radius_m,specialty,language)
    # Quantize location before transmission/cache; never send identity or specialty.
    lat,lng = round(lat,3),round(lng,3)
    url = endpoint('OSM_OVERPASS_URL', 'https://overpass-api.de/api/interpreter')
    around = f'(around:{radius_m},{lat},{lng})'
    q = f'[out:json][timeout:20][maxsize:8388608];(nwr["amenity"~"^(hospital|clinic|doctors)$"]{around};nwr["healthcare"~"^(hospital|clinic|doctor|centre)$"]{around};);out center tags 250;'
    data = await upstream_json('facilities','POST',url,'osm:'+url+q,600,data={'data':q})
    providers = normalize_providers(data['elements'][:250],lat,lng,radius_m,specialty,language,label)
    return {'providers':providers[:50],'resolved_location':{'query':query or 'Coordinates','display_name':label,'city':label,'coordinates':{'lat':lat,'lng':lng},'is_approximate':True},'searched_radius_m':radius_m, 'results_limited':len(data['elements']) >= 250 or len(providers)>50}


def normalize_providers(elements,lat,lng,radius_m,specialty,language,label,retrieved_at=None):
    providers = []; seen = set()
    for item in elements:
        if not isinstance(item,dict): continue
        tags = item.get('tags',{}); point = item.get('center') or item
        if not isinstance(tags,dict) or not isinstance(point,dict) or item.get('type') not in {'node','way','relation'} or not isinstance(item.get('id'),int): continue
        if not (tags.get('amenity') in {'hospital','clinic','doctors','dentist'} or tags.get('healthcare') in {'hospital','clinic','doctor','centre','dentist','health_post','physiotherapist'}): continue
        if tags.get('disused') == 'yes' or tags.get('abandoned') == 'yes': continue
        a,b=point.get('lat'),point.get('lon')
        if not valid_point(a,b): continue
        distance = haversine_distance_km(lat,lng,a,b)
        if distance*1000 > radius_m: continue
        spec = tags.get('healthcare:speciality', tags.get('healthcare:specialty',''))
        source_specs = {s.strip().lower() for s in str(spec).split(';')}
        if SPECIALTIES[specialty] is not None and not source_specs.intersection(SPECIALTIES[specialty]): continue
        identity = f"{item['type']}/{item['id']}"
        if identity in seen: continue
        seen.add(identity)
        name = tags.get('name:'+language) or tags.get('name')
        if not isinstance(name,str) or not name.strip(): continue  # Never invent facility names.
        phone = tags.get('contact:phone') or tags.get('phone')
        phone = re.sub(r'[\s().-]', '', phone.split(';')[0]) if isinstance(phone,str) else ''
        if not re.fullmatch(r'\+?\d{7,15}',phone): phone = None
        website = safe_url(tags.get('contact:website') or tags.get('website'))
        address = ', '.join(str(tags[k])[:200] for k in ['addr:housenumber','addr:street','addr:suburb','addr:city','addr:postcode'] if tags.get(k))
        source_url = 'https://www.openstreetmap.org/'+identity
        providers.append({'id':'osm:'+identity,'name':name[:250],'clinic_name':name[:250], 'specialty':str(spec)[:250] if spec else tags.get('healthcare',tags.get('amenity')), 'specialty_id':'source_category', 'city':label,'address':address,'coordinates':{'lat':a,'lng':b},'distance_km':round(distance,2),'phone':phone,'phone_available':bool(phone),'website':website,'maps_url':source_url,'directions_url':'https://www.openstreetmap.org/directions?'+urlencode({'to':f'{a},{b}'}),'rating':None,'user_rating_count':None,'source':'external_discovery','verification_status':'source_listed','booking_capability':'external_request','available_slots':[],'consultation_options':capabilities(identity,phone,website),'attributions':[ATTRIBUTION],'last_updated':retrieved_at or datetime.datetime.now(datetime.timezone.utc).isoformat()})
    providers.sort(key=lambda p:(p['distance_km'],p['id']))
    return providers


def snapshot_result(local,radius_m,specialty,language):
    data,location=local
    point=location['coordinates']
    providers=normalize_providers(data['facilities'],point['lat'],point['lng'],radius_m,specialty,language,location['display_name'],data['retrieved_at'])
    west,south,east,north=data['bounds']
    edge_distance=min(haversine_distance_km(point['lat'],point['lng'],point['lat'],west),haversine_distance_km(point['lat'],point['lng'],point['lat'],east),haversine_distance_km(point['lat'],point['lng'],south,point['lng']),haversine_distance_km(point['lat'],point['lng'],north,point['lng']))
    return {'providers':providers[:100],'resolved_location':location,'searched_radius_m':radius_m,'results_limited':len(providers)>100,'total_matches':len(providers),'data_source':'osm_snapshot','snapshot_version':data['version'],'snapshot_retrieved_at':data['retrieved_at'],'coverage_notice':data['coverage_description'],'coverage_edge':edge_distance*1000<radius_m,'specialty_data_sparse':specialty!='general physician','snapshot_facility_count':len(data['facilities'])}
