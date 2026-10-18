"""Owner-scoped durable state. Production requests use the user's JWT and Supabase RLS."""
import json
import os
import sqlite3
from collections.abc import MutableMapping
from pathlib import Path
from contextlib import contextmanager
import httpx
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.core.auth import owner_context,token_context,production,configured
from app.core.config import data_directory

class OwnedStore(MutableMapping):
    def __init__(self,namespace): self.namespace=namespace
    @contextmanager
    def connection(self):
        conn = None
        try:
            folder = data_directory()
            folder.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(folder / 'patient_state.sqlite3', timeout=10)
            conn.execute('CREATE TABLE IF NOT EXISTS state (owner TEXT NOT NULL, namespace TEXT NOT NULL, key TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(owner,namespace,key))')
            with conn: yield conn
        except (OSError, sqlite3.Error):
            raise HTTPException(503, 'Local persistence unavailable. Check the private data directory.') from None
        finally:
            if conn is not None: conn.close()
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
            if method == "GET" and not result.content: raise ValueError("Missing persistence body")
            rows = result.json() if result.content else []
            if not isinstance(rows,list) or any(not isinstance(row,dict) or not all(name in row for name in ['state_key','payload']) or not isinstance(row.get('payload'),dict) for row in rows):
                raise ValueError('Unexpected persistence response')
            return rows
        except (httpx.HTTPError,ValueError): raise HTTPException(503,'Secure persistence unavailable.') from None
    def __getitem__(self,key):
        if production() or configured():
            rows=self.remote('GET',key)
            if not rows: raise KeyError(key)
            return rows[0]['payload']
        with self.connection() as conn: row=conn.execute('SELECT payload FROM state WHERE owner=? AND namespace=? AND key=?',(owner_context.get(),self.namespace,key)).fetchone()
        if row is None: raise KeyError(key)
        try:
            value = json.loads(row[0])
            if not isinstance(value,dict): raise ValueError()
            return value
        except ValueError: raise HTTPException(503,"Saved state is unreadable. Restore it from a private backup.") from None
    def __setitem__(self,key,value):
        value=jsonable_encoder(value)
        if production() or configured(): self.remote('POST',payload={'owner_id':owner_context.get(),'namespace':self.namespace,'state_key':key,'payload':value});return
        with self.connection() as conn: conn.execute('INSERT INTO state VALUES(?,?,?,?) ON CONFLICT(owner,namespace,key) DO UPDATE SET payload=excluded.payload',(owner_context.get(),self.namespace,key,json.dumps(value)))
    def __delitem__(self,key):
        if production() or configured(): self.remote('DELETE',key);return
        with self.connection() as conn:
            cursor=conn.execute('DELETE FROM state WHERE owner=? AND namespace=? AND key=?',(owner_context.get(),self.namespace,key))
            if not cursor.rowcount: raise KeyError(key)
    def __iter__(self):
        if production() or configured(): return iter([row['state_key'] for row in self.remote('GET')])
        with self.connection() as conn: rows=conn.execute('SELECT key FROM state WHERE owner=? AND namespace=?',(owner_context.get(),self.namespace)).fetchall()
        return iter([row[0] for row in rows])
    def __len__(self): return len(list(iter(self)))
