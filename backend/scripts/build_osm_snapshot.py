"""Build the redistributable Mumbai OSM snapshot from a Geofabrik PBF.
Tool-only dependency: pip install osmium==4.3.2. Not used by the web server.
No Overpass/Nominatim bulk requests. Run from repository root.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import osmium

BOUNDS = [72.75, 18.85, 73.35, 19.50]  # west, south, east, north
CATEGORIES = {'hospital','clinic','doctors','dentist','doctor','centre','health_post','physiotherapist'}

def medical(tags):
    return tags.get('amenity') in {'hospital','clinic','doctors','dentist'} or tags.get('healthcare') in CATEGORIES

def inside(lat, lon):
    return BOUNDS[0] <= lon <= BOUNDS[2] and BOUNDS[1] <= lat <= BOUNDS[3]

def names(tags):
    return sorted({v.strip() for k,v in tags.items() if k in {'name','name:en','name:hi','name:mr','old_name','alt_name','official_name','short_name'} for v in v.split(';') if v.strip()})

class Relations(osmium.SimpleHandler):
    def __init__(self):
        super().__init__(); self.items={};self.ways=set();self.nodes=set()
    def relation(self,r):
        tags=dict(r.tags)
        if medical(tags):
            members=[(m.type,m.ref) for m in r.members if m.type in {'n','w'}]
            self.items[r.id]=(tags,members)
            self.ways.update(ref for t,ref in members if t=='w')
            self.nodes.update(ref for t,ref in members if t=='n')

class Extract(osmium.SimpleHandler):
    def __init__(self, relations):
        super().__init__();self.relations=relations;self.facilities=[];self.places=[];self.pins={};self.members={};self.skipped_unnamed=0
    def consume(self,kind,identity,tags,lat,lon):
        if not inside(lat,lon):return
        name=tags.get('name') or tags.get('name:en') or tags.get('name:mr') or tags.get('name:hi')
        if medical(tags):
            if not name:self.skipped_unnamed+=1
            # Retain unnamed source elements for coverage accounting; UI skips them.
            self.facilities.append({'type':kind,'id':identity,'lat':round(lat,7),'lon':round(lon,7),'tags':tags,'osm_url':f'https://www.openstreetmap.org/{kind}/{identity}'})
        if name and tags.get('place') in {'city','town','village','suburb','quarter','neighbourhood','hamlet','locality'}:
            self.places.append({'name':name,'aliases':names(tags),'lat':round(lat,7),'lng':round(lon,7),'type':tags['place'],'osm_url':f'https://www.openstreetmap.org/{kind}/{identity}'})
        for pin in tags.get('addr:postcode','').replace(',',';').split(';'):
            pin=pin.strip()
            if len(pin)==6 and pin.isdigit() and pin[0]!='0':
                self.pins.setdefault(pin,[]).append([lat,lon,f'https://www.openstreetmap.org/{kind}/{identity}'])
    def node(self,n):
        if not n.location.valid():return
        lat,lon=n.location.lat,n.location.lon
        if n.id in self.relations.nodes:self.members[('n',n.id)]=(lat,lon)
        self.consume('node',n.id,dict(n.tags),lat,lon)
    def way(self,w):
        tags=dict(w.tags)
        needed=w.id in self.relations.ways
        if not needed and not medical(tags) and not tags.get('place') and not tags.get('addr:postcode'):return
        points=[(n.lat,n.lon) for n in w.nodes if n.location.valid()]
        if not points:return
        lat=(min(v[0] for v in points)+max(v[0] for v in points))/2
        lon=(min(v[1] for v in points)+max(v[1] for v in points))/2
        if needed:self.members[('w',w.id)]=(lat,lon)
        self.consume('way',w.id,tags,lat,lon)
    def finish_relations(self):
        for identity,(tags,members) in self.relations.items.items():
            points=[self.members[m] for m in members if m in self.members]
            if points:self.consume('relation',identity,tags,sum(p[0] for p in points)/len(points),sum(p[1] for p in points)/len(points))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('pbf');parser.add_argument('--output',default='backend/app/data/osm/mumbai-v1.json');parser.add_argument('--retrieved-at');parser.add_argument('--source-last-modified',required=True)
    args=parser.parse_args();p=Path(args.pbf)
    relations=Relations()
    for obj in osmium.FileProcessor(str(p)).with_filter(osmium.filter.EntityFilter(osmium.osm.RELATION)).with_filter(osmium.filter.KeyFilter('amenity','healthcare')):
        relations.relation(obj)
    print('Medical relation references collected',flush=True)
    handler=Extract(relations)
    for obj in osmium.FileProcessor(str(p)).with_locations().with_filter(osmium.filter.KeyFilter('amenity','healthcare','place','addr:postcode')):
        if obj.is_node():handler.node(obj)
        elif obj.is_way():handler.way(obj)
    print('Tagged places, PIN addresses and facilities extracted',flush=True)
    # Relation-only members may have no medical tags of their own.
    if relations.ways or relations.nodes:
        ids=relations.ways | relations.nodes
        for obj in osmium.FileProcessor(str(p)).with_locations().with_filter(osmium.filter.IdFilter(ids)):
            if obj.is_node() and obj.id in relations.nodes and obj.location.valid():
                handler.members[('n',obj.id)]=(obj.location.lat,obj.location.lon)
            elif obj.is_way() and obj.id in relations.ways:
                points=[(n.lat,n.lon) for n in obj.nodes if n.location.valid()]
                if points:handler.members[('w',obj.id)]=((min(p[0] for p in points)+max(p[0] for p in points))/2,(min(p[1] for p in points)+max(p[1] for p in points))/2)
    handler.finish_relations()
    pins=[]
    for code,points in sorted(handler.pins.items()):
        pins.append({'pincode':code,'lat':round(sum(p[0] for p in points)/len(points),7),'lng':round(sum(p[1] for p in points)/len(points),7),'source_count':len(points),'osm_url':points[0][2],'is_approximate':True})
    data={'version':'mumbai-v1','retrieved_at':args.retrieved_at or datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),'source_url':'https://download.geofabrik.de/asia/india/western-zone-latest.osm.pbf','source_last_modified':args.source_last_modified,'source_sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'license':'ODbL-1.0','attribution':'© OpenStreetMap contributors; extract by Geofabrik','bounds':BOUNDS,'coverage_description':'Rectangular regional extract covering Greater Mumbai (Colaba–Dahisar–Mulund), Navi Mumbai, Thane, Panvel and Kalyan-Dombivli; includes nearby localities. OSM is incomplete.','coordinate_method':'Node location; way bounding-box center; relation member centers. PIN centers averaged from OSM address tags, not official postal boundaries.','unnamed_facilities':handler.skipped_unnamed,'facilities':sorted(handler.facilities,key=lambda v:(v['type'],v['id'])),'places':sorted(handler.places,key=lambda v:v['name']),'pincodes':pins}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({'facilities':len(data['facilities']),'unnamed':data['unnamed_facilities'],'places':len(data['places']),'pincodes':len(pins),'bytes':out.stat().st_size}))
if __name__=='__main__':main()
