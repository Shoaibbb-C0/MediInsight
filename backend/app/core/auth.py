"""Verified server identities and isolated development sessions; no client-supplied user IDs."""
import hashlib
import hmac
import os
import secrets
from contextvars import ContextVar
import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

owner_context=ContextVar('owner',default='local_default_patient')
token_context=ContextVar('access_token',default='')
DEV_SECRET=secrets.token_bytes(32)
router=APIRouter()

def configured(): return bool(os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_PUBLISHABLE_KEY'))
def production(): return os.getenv('ENVIRONMENT','development')=='production'
def cookie_options(): return {'httponly':True,'secure':production(),'samesite':'strict','path':'/'}

def development_owner(cookie):
    if cookie:
        value,_,signature=cookie.partition('.')
        if len(value)==64 and hmac.compare_digest(hmac.new(DEV_SECRET,value.encode(),hashlib.sha256).hexdigest(),signature): return 'dev_'+value,cookie
    value=secrets.token_hex(32)
    return 'dev_'+value,value+'.'+hmac.new(DEV_SECRET,value.encode(),hashlib.sha256).hexdigest()

async def resolve_identity(request):
    if configured():
        token=request.cookies.get('simplifier_access','')
        bearer=request.headers.get('authorization','')
        if bearer.startswith('Bearer '): token=bearer[7:]
        if not token: raise HTTPException(401,'Sign in to access medical reports.')
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                result=await client.get(os.environ['SUPABASE_URL'].rstrip('/')+'/auth/v1/user',headers={'apikey':os.environ['SUPABASE_PUBLISHABLE_KEY'],'Authorization':'Bearer '+token})
            if result.status_code!=200: raise HTTPException(401,'Session expired. Sign in again.')
            user=result.json()
            if not user.get('id'): raise HTTPException(401,'Invalid session.')
            request.state.access_token=token
            return user['id']
        except httpx.HTTPError: raise HTTPException(503,'Authentication service unavailable.') from None
    if production(): raise HTTPException(503,'Authentication is not configured.')
    owner,cookie=development_owner(request.cookies.get('simplifier_dev'))
    request.state.development_cookie=cookie
    return owner

class Login(BaseModel):
    email:str=Field(min_length=3,max_length=254)
    password:str=Field(min_length=1,max_length=200)

async def exchange(payload, response, grant):
    if not configured(): raise HTTPException(503,'Supabase authentication is not configured.')
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            result=await client.post(os.environ['SUPABASE_URL'].rstrip('/')+'/auth/v1/token',params={'grant_type':grant},headers={'apikey':os.environ['SUPABASE_PUBLISHABLE_KEY']},json=payload)
        if result.status_code!=200: raise HTTPException(401,'Sign-in or session refresh failed.')
        session=result.json()
        response.set_cookie('simplifier_access',session['access_token'],max_age=session.get('expires_in',3600),**cookie_options())
        response.set_cookie('simplifier_refresh',session['refresh_token'],max_age=30*86400,**cookie_options())
        response.headers['Cache-Control']='no-store'
        return {'signed_in':True}
    except httpx.HTTPError: raise HTTPException(503,'Authentication service unavailable.') from None

@router.get('/configuration')
async def configuration(): return {'configured':configured(),'sign_in_required':configured() or production(),'development_mode':not configured() and not production()}

@router.post('/login')
async def login(payload:Login,response:Response): return await exchange(payload.model_dump(),response,'password')

@router.post('/refresh')
async def refresh(request:Request,response:Response):
    token=request.cookies.get('simplifier_refresh')
    if not token: raise HTTPException(401,'Sign in again.')
    return await exchange({'refresh_token':token},response,'refresh_token')

@router.get('/session')
async def session(): return {'signed_in':configured(),'development_mode':not configured(),'user_id':owner_context.get()}

@router.post('/logout')
async def logout(request:Request,response:Response):
    token=request.cookies.get('simplifier_access')
    if configured() and token:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                result=await client.post(os.environ['SUPABASE_URL'].rstrip('/')+'/auth/v1/logout',headers={'apikey':os.environ['SUPABASE_PUBLISHABLE_KEY'],'Authorization':'Bearer '+token})
            if result.status_code not in [200,204,401]: raise HTTPException(503,'Sign-out could not be verified.')
        except httpx.HTTPError: raise HTTPException(503,'Sign-out service unavailable.') from None
    for name in ['simplifier_access','simplifier_refresh','simplifier_dev']: response.delete_cookie(name,path='/',secure=production(),httponly=True,samesite='strict')
    return {'signed_out':True}
