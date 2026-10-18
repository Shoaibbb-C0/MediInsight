"""Bundled OSM snapshot and offline place/PIN routing. No network calls."""
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from fastapi import HTTPException
from app.services.location_service import haversine_distance_km

SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / 'data/osm/mumbai-v1.json'


def normalize(value):
    return ' '.join(re.sub(r'[^\w\s]', ' ', unicodedata.normalize('NFKC',value).casefold()).split())


@lru_cache(maxsize=1)
def snapshot():
    try:
        data=json.loads(SNAPSHOT_PATH.read_text(encoding='utf-8'))
        if data.get('version')!='mumbai-v1' or not data.get('facilities') or len(data.get('bounds',[]))!=4:raise ValueError()
        return data
    except (OSError,ValueError,TypeError):
        raise HTTPException(503,'The bundled OSM snapshot is unavailable. Restore the versioned dataset; no substitute listings were used.') from None


def in_coverage(lat,lng,data):
    if not isinstance(lat,(int,float)) or not isinstance(lng,(int,float)):return False
    west,south,east,north=data['bounds']
    return south <= lat <= north and west <= lng <= east


def resolve_snapshot(query=None,lat=None,lng=None):
    data=snapshot()
    if query is None:
        if not in_coverage(lat,lng,data):return None
        return data, {'query':'Coordinates','display_name':'Mumbai region — selected GPS coordinates','city':'','coordinates':{'lat':lat,'lng':lng},'is_approximate':False}
    value=normalize(query)
    if query.isdigit():
        point=next((p for p in data['pincodes'] if p['pincode']==query and p['pincode'].startswith(('400','401','410','421')) and p['source_count']>=2),None)
        if point:
            return data, {'query':query,'display_name':f'PIN {query} — approximate OSM address-tag center','city':'','pincode':query,'coordinates':{'lat':point['lat'],'lng':point['lng']},'is_approximate':True}
        # Mumbai/Thane PIN requests stay offline even when the snapshot lacks tags.
        if query.startswith('400'):
            raise HTTPException(422,'This regional PIN is not indexed in the OSM snapshot. Use a listed locality or GPS; no postal location was invented.')
        return None
    # Strip only explicit state/country qualifiers, never an arbitrary city suffix.
    for suffix in [' maharashtra india',' maharashtra',' india',' महाराष्ट्र भारत',' महाराष्ट्र',' भारत']:
        if value.endswith(suffix):value=value[:-len(suffix)].strip();break
    # Administrative region aliases use OSM-derived anchors, not invented clinics.
    aliases={'greater mumbai':'mumbai','bombay':'mumbai','मुंबई':'mumbai','बृहन्मुंबई':'mumbai','navi mumbai':'navi mumbai','नवी मुंबई':'navi mumbai','thane':'thane','ठाणे':'thane','panvel':'panvel','पनवेल':'panvel','kalyan dombivli':'kalyan dombivli','kalyan dombivali':'kalyan dombivli','कल्याण डोंबिवली':'kalyan dombivli','dombivali':'dombivli'}
    aliases.update({'south mumbai':'colaba','central mumbai':'dadar','western suburbs':'andheri','eastern suburbs':'ghatkopar','दक्षिण मुंबई':'colaba','मध्य मुंबई':'dadar','पश्चिमी उपनगर':'andheri','पूर्वी उपनगर':'ghatkopar'})
    parts=[normalize(p) for p in query.split(',')]
    qualifiers={normalize(v) for v in ['Mumbai','Greater Mumbai','Maharashtra','India','मुंबई','महाराष्ट्र','भारत']}
    if len(parts)>1 and all(p in qualifiers for p in parts[1:]):value=parts[0]
    aliases={normalize(k):normalize(v) for k,v in aliases.items()}
    value=aliases.get(value,value)
    matches=[p for p in data['places'] if value in {normalize(n) for n in [p['name'],*p['aliases']]}]
    if not matches:
        # OSM often maps East/West suburbs instead of one broad locality node.
        # Combine only explicit directional variants, never arbitrary substrings.
        variants={value+' '+d for d in ['east','west','north','south']}
        directional=[p for p in data['places'] if p['type'] in {'suburb','quarter','town'} and any(normalize(n) in variants for n in [p['name'],*p['aliases']])]
        if directional:
            first=directional[0]
            if any(haversine_distance_km(first['lat'],first['lng'],p['lat'],p['lng'])>15 for p in directional):raise HTTPException(422,'This locality is ambiguous. Use a precise PIN or GPS.')
            return data, {'query':query,'display_name':query+' — approximate OSM directional-locality center','city':query,'coordinates':{'lat':sum(p['lat'] for p in directional)/len(directional),'lng':sum(p['lng'] for p in directional)/len(directional)},'is_approximate':True}
    if matches:
        rank={'city':0,'town':1,'suburb':2,'quarter':3,'neighbourhood':4,'village':5,'hamlet':6,'locality':7}
        matches.sort(key=lambda p:rank.get(p['type'],8));best=matches[0]
        peers=[p for p in matches if rank.get(p['type'],8)==rank.get(best['type'],8)]
        if any(haversine_distance_km(best['lat'],best['lng'],p['lat'],p['lng'])>5 for p in peers):
            raise HTTPException(422,'This locality is ambiguous in the OSM snapshot. Use GPS or a precise indexed PIN.')
        return data, {'query':query,'display_name':best['name']+' — OSM locality center','city':best['name'],'coordinates':{'lat':best['lat'],'lng':best['lng']},'is_approximate':True}
    if any(word in value.split() for word in ['mumbai','thane','panvel','kalyan','dombivli','मुंबई','ठाणे','पनवेल']):
        raise HTTPException(422,'This regional locality is not indexed in the OSM snapshot. Use a nearby listed locality, PIN or GPS.')
    return None
