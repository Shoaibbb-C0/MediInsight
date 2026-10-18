"""Official Google APIs only. No medical documents or patient details leave this adapter."""
import datetime
import json
import os
from urllib.parse import urlencode, urlsplit
import httpx
from fastapi import HTTPException
from app.services.location_service import haversine_distance_km

PLACES_URL = 'https://places.googleapis.com/v1/places:searchText'
FIELDS = ','.join('places.' + name for name in ['id','displayName','formattedAddress','location','internationalPhoneNumber','websiteUri','googleMapsUri','primaryTypeDisplayName','regularOpeningHours','businessStatus','attributions'])


def safe_url(value):
    if not isinstance(value, str): return None
    parts = urlsplit(value)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
        return None
    return value


def capabilities(place_id, phone, website):
    options = []
    if phone:
        options.append({'type':'call','label':'Call Doctor/Clinic','url':'tel:'+''.join(c for c in phone if c.isdigit() or c=='+'),'evidence':'Google Maps listing phone number'})
    if website:
        options.append({'type':'website','label':'Contact Clinic','url':website,'evidence':'Provider website supplied by Google Maps'})
    path = os.getenv('PROVIDER_CAPABILITIES_FILE')
    if path:
        try:
            with open(path, encoding='utf-8-sig') as source: registry=json.load(source)
        except (OSError, ValueError):
            raise HTTPException(503, 'Provider capabilities configuration is invalid.')
        entry = registry.get(place_id, {})
        evidence = safe_url(entry.get('source_url'))
        try:
            reviewed=datetime.date.fromisoformat(entry.get('reviewed_at',''))
            recent=0 <= (datetime.datetime.now(datetime.timezone.utc).date()-reviewed).days <= 90
        except ValueError: recent=False
        if evidence and recent:
            for kind, key, label in [('clinic_visit','clinic_request_url','Book Clinic Visit / Request'),('online','online_consultation_url','Online Consultation'),('external_booking','booking_url','External Booking')]:
                url = safe_url(entry.get(key))
                if url: options.append({'type':kind,'label':label,'url':url,'evidence':evidence,'reviewed_at':entry['reviewed_at']})
            number = entry.get('whatsapp_number', '')
            if entry.get('whatsapp_consultation_supported') is True and number.startswith('+') and number[1:].isdigit() and 8 <= len(number[1:]) <= 15:
                options.append({'type':'whatsapp','label':'WhatsApp Consultation','url':f'https://wa.me/{number[1:]}?'+urlencode({'text':'Hello, I would like to enquire about a consultation. Please share your availability.'}),'evidence':evidence})
    return options


async def google_json(client, method, url, **kwargs):
    try:
        response = await client.request(method,url,**kwargs)
        if response.status_code == 429: raise HTTPException(429, 'Provider search quota reached. Please try later.')
        if not response.is_success: raise HTTPException(503, 'Location/provider service unavailable. Check server API configuration.')
        data = response.json()
        if not isinstance(data, dict): raise ValueError('Unexpected response')
        return data
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, 'Location/provider service unavailable. Please try later.') from None


async def discover_providers(query=None, lat=None, lng=None, radius_m=10000, specialty='general physician', language='en'):
    key = os.getenv('GOOGLE_MAPS_SERVER_KEY')
    if not key: raise HTTPException(503, 'Live provider search is not configured. GOOGLE_MAPS_SERVER_KEY is required.')
    if not query and (lat is None or lng is None): raise HTTPException(422, 'Enter a city/PIN or allow your location.')
    async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
        label = query or 'Your selected location'
        if query:
            query = query.strip()
            if len(query)>120 or (query.isdigit() and (len(query)!=6 or query[0]=='0')): raise HTTPException(422, 'Enter a valid place or six-digit Indian PIN.')
            data = await google_json(client,'GET','https://maps.googleapis.com/maps/api/geocode/json',params={'address':query,'components':'country:IN','key':key,'language':language})
            if data.get('status')=='ZERO_RESULTS': raise HTTPException(404, 'Location not found. Try a nearby town or PIN.')
            if data.get('status')!='OK' or not data.get('results'): raise HTTPException(503, 'Geocoding unavailable. Check API enablement and billing.')
            result=data['results'][0]
            if not any('country' in item.get('types',[]) and item.get('short_name')=='IN' for item in result.get('address_components',[])): raise HTTPException(422,'Choose a location in India.')
            lat=result['geometry']['location']['lat']; lng=result['geometry']['location']['lng']; label=result['formatted_address']
        if not (-90 <= lat <= 90 and -180 <= lng <= 180): raise HTTPException(422,'Invalid coordinates.')
        providers=[]; searched_radius=radius_m
        for search_radius in sorted(set([radius_m,min(radius_m*2,50000)])):
            searched_radius=search_radius
            data=await google_json(client,'POST',PLACES_URL,headers={'X-Goog-Api-Key':key,'X-Goog-FieldMask':FIELDS},json={'textQuery':specialty,'languageCode':language,'regionCode':'IN','pageSize':20,'locationBias':{'circle':{'center':{'latitude':lat,'longitude':lng},'radius':float(search_radius)}}})
            providers=[]
            for place in data.get('places',[]):
                if place.get('businessStatus') in ['CLOSED_PERMANENTLY','CLOSED_TEMPORARILY']: continue
                point=place.get('location',{})
                if 'latitude' not in point or 'longitude' not in point: continue
                distance=haversine_distance_km(lat,lng,point['latitude'],point['longitude'])
                if distance*1000 > search_radius: continue
                phone=place.get('internationalPhoneNumber'); website=safe_url(place.get('websiteUri')); place_id=place.get('id')
                if not place_id: continue
                maps=safe_url(place.get('googleMapsUri')) or 'https://www.google.com/maps/search/?'+urlencode({'api':1,'query':place.get('formattedAddress',''),'query_place_id':place_id})
                providers.append({'id':place_id,'name':place.get('displayName',{}).get('text','Healthcare provider'),'clinic_name':place.get('displayName',{}).get('text','Healthcare provider'),'specialty':place.get('primaryTypeDisplayName',{}).get('text','Healthcare business listing; specialty unverified'),'specialty_id':'source_category','city':label,'address':place.get('formattedAddress','Address not supplied'),'coordinates':{'lat':point['latitude'],'lng':point['longitude']},'distance_km':distance,'phone':phone,'phone_available':bool(phone),'website':website,'maps_url':maps,'directions_url':'https://www.google.com/maps/dir/?'+urlencode({'api':1,'destination':f"{point['latitude']},{point['longitude']}",'destination_place_id':place_id}),'opening_hours':place.get('regularOpeningHours',{}).get('weekdayDescriptions',[]),'source':'external_discovery','verification_status':'source_listed','booking_capability':'external_request','available_slots':[],'consultation_options':capabilities(place_id,phone,website),'attributions':place.get('attributions',[]),'last_updated':datetime.datetime.now(datetime.timezone.utc).isoformat()})
            if len(providers)>=3: break
    return {'providers':sorted(providers,key=lambda item:item['distance_km']),'resolved_location':{'query':query or 'Coordinates','display_name':label,'city':label,'coordinates':{'lat':lat,'lng':lng},'is_approximate':bool(query)},'searched_radius_m':searched_radius}
