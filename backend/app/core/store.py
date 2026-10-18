"""Owner-scoped durable state. Production requests use the user's JWT and Supabase RLS."""
import json
import os
import sqlite3
from collections.abc import MutableMapping
from pathlib import Path
import httpx
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.core.auth import owner_context,token_context,production

class OwnedStore(MutableMapping):
    def __init__(self,namespace): self.namespace=namespace
    def connection(self):
        folder=Path(os.getenv('APP_DATA_DIR',str(Path(__file__).resolve().parents[2]/'data')))
        folder.mkdir(parents=True,exist_ok=True)
        conn=sqlite3.connect(folder/'patient_state.sqlite3',timeout=10)
        conn.execute('CREATE TABLE IF NOT EXISTS state (owner TEXT NOT NULL, namespace TEXT NOT NULL, key TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(owner,namespace,key))')
        return conn
    def remote(self,method,key=None,payload=None):
        token=token_context.get()
        if not token: raise HTTPException(401,'Verified authentication required.')
        params={'owner_id':'eq.'+owner_context.get(),'namespace':'eq.'+self.namespace}
        if key is not None: params['state_key']='eq.'+key
        headers={'apikey':os.environ['SUPABASE_PUBLISHABLE_KEY'],'Authorization':'Bearer '+token,'Prefer':'return=representation'}
        if method=='POST': params={'on_conflict':'owner_id,namespace,state_key'};headers['Prefer']='resolution=merge-duplicates,return=representation'
        try:
            result=httpx.request(method,os.environ['SUPABASE_URL'].rstrip('/')+'/rest/v1/patient_app_state',params=params,headers=headers,json=payload,timeout=15)
            if not result.is_success: raise HTTPException(503,'Secure persistence unavailable. Check migrations and RLS.')
            return result.json() if result.content else []
        except (httpx.HTTPError,ValueError): raise HTTPException(503,'Secure persistence unavailable.') from None
    def __getitem__(self,key):
        if production():
            rows=self.remote('GET',key)
            if not rows: raise KeyError(key)
            return rows[0]['payload']
        with self.connection() as conn: row=conn.execute('SELECT payload FROM state WHERE owner=? AND namespace=? AND key=?',(owner_context.get(),self.namespace,key)).fetchone()
        if row is None: raise KeyError(key)
        return json.loads(row[0])
    def __setitem__(self,key,value):
        value=jsonable_encoder(value)
        if production(): self.remote('POST',payload={'owner_id':owner_context.get(),'namespace':self.namespace,'state_key':key,'payload':value});return
        with self.connection() as conn: conn.execute('INSERT INTO state VALUES(?,?,?,?) ON CONFLICT(owner,namespace,key) DO UPDATE SET payload=excluded.payload',(owner_context.get(),self.namespace,key,json.dumps(value)))
    def __delitem__(self,key):
        if production(): self.remote('DELETE',key);return
        with self.connection() as conn:
            cursor=conn.execute('DELETE FROM state WHERE owner=? AND namespace=? AND key=?',(owner_context.get(),self.namespace,key))
            if not cursor.rowcount: raise KeyError(key)
    def __iter__(self):
        if production(): return iter([row['state_key'] for row in self.remote('GET')])
        with self.connection() as conn: rows=conn.execute('SELECT key FROM state WHERE owner=? AND namespace=?',(owner_context.get(),self.namespace)).fetchall()
        return iter([row[0] for row in rows])
    def __len__(self): return len(list(iter(self)))
