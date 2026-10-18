import json
import os
import subprocess
import sys
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core import auth

CLIENT_TYPE = httpx.AsyncClient
pytestmark = pytest.mark.real_identity


def configure(monkeypatch, handler):
    monkeypatch.setenv("AUTH_MODE", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "test-public-key")
    client_type = CLIENT_TYPE
    monkeypatch.setattr(auth.httpx, "AsyncClient", lambda **kwargs: client_type(transport=httpx.MockTransport(handler), **kwargs))


def test_configuration_without_cloud_does_not_access_network(monkeypatch):
    monkeypatch.setenv("AUTH_MODE", "local")
    def forbidden(*args, **kwargs): raise AssertionError("unexpected cloud request")
    monkeypatch.setattr(auth.httpx, "AsyncClient", forbidden)
    response = TestClient(app).get("/api/v1/auth/configuration")
    assert response.status_code == 200
    assert response.json() == {"configured":False,"sign_in_required":False,"development_mode":True}
    assert response.headers['cache-control'] == 'no-store'


@pytest.mark.parametrize("values", [
    {"SUPABASE_URL":"https://example.supabase.co"},
    {"SUPABASE_URL":"not-a-url","SUPABASE_PUBLISHABLE_KEY":"test-public-key"},
    {"SUPABASE_URL":"https://example.supabase.co/path","SUPABASE_PUBLISHABLE_KEY":"test-public-key"},
    {"SUPABASE_URL":"https://example.supabase.co","SUPABASE_PUBLISHABLE_KEY":"sb_secret_never-use-this"},
])
def test_malformed_auth_configuration_is_controlled_not_anonymous(monkeypatch, values):
    for key,value in values.items(): monkeypatch.setenv(key,value)
    client = TestClient(app)
    response = client.get('/api/v1/auth/configuration')
    assert response.status_code == 503
    assert 'configuration is invalid' in response.json()['detail']
    assert client.get('/api/v1/reports/history/list').status_code == 503
    assert not client.cookies.get('simplifier_dev')
    assert 'sb_secret' not in response.text


def test_login_refresh_logout_secure_cookies(monkeypatch):
    monkeypatch.setenv('ENVIRONMENT','production')
    calls=[]
    def handle(request):
        calls.append(request)
        if request.url.path.endswith('/user'): return httpx.Response(200,json={'id':'verified-user'})
        if request.url.path.endswith('/logout'): return httpx.Response(204)
        if request.url.params['grant_type']=='refresh_token':
            assert json.loads(request.content)=={'refresh_token':'refresh-one'}
            return httpx.Response(200,json={'access_token':'access-two','refresh_token':'refresh-two','expires_in':1800})
        return httpx.Response(200,json={'access_token':'access-one','refresh_token':'refresh-one','expires_in':3600})
    configure(monkeypatch,handle)
    client=TestClient(app,base_url='https://testserver')
    response=client.post('/api/v1/auth/login',json={'email':'test@example.org','password':'test-password'})
    assert response.status_code==200
    assert 'access-one' not in response.text
    assert all('HttpOnly' in cookie and 'Secure' in cookie and 'SameSite=strict' in cookie for cookie in response.headers.get_list('set-cookie'))
    assert client.get('/api/v1/auth/session').json()['user_id']=='verified-user'
    assert client.post('/api/v1/auth/refresh').status_code==200
    assert client.cookies['simplifier_access']=='access-two'
    assert client.post('/api/v1/auth/logout').status_code==200
    assert not list(client.cookies)
    assert client.get('/api/v1/auth/session').status_code==401


@pytest.mark.parametrize('payload',[{}, {'access_token':'one'}, [], {'access_token':'one','refresh_token':'two','expires_in':'bad'}])
def test_malformed_upstream_session_does_not_raise_500(monkeypatch,payload):
    configure(monkeypatch,lambda request:httpx.Response(200,json=payload))
    response=TestClient(app).post('/api/v1/auth/login',json={'email':'test@example.org','password':'pw'})
    assert response.status_code==503
    assert not response.headers.get_list('set-cookie')


def test_auth_network_failure_and_expired_refresh(monkeypatch):
    def unavailable(request): raise httpx.ConnectError('private upstream details')
    configure(monkeypatch,unavailable)
    client=TestClient(app)
    response=client.post('/api/v1/auth/login',json={'email':'test@example.org','password':'pw'})
    assert response.status_code==503 and 'private upstream' not in response.text
    assert client.post('/api/v1/auth/refresh').status_code==401
    configure(monkeypatch,lambda request:httpx.Response(401))
    assert client.get('/api/v1/auth/session',headers={'Authorization':'Bearer expired'}).status_code==401


@pytest.mark.parametrize('extra',[{'AUTH_MODE':'local'},{'SUPABASE_URL':'bad','SUPABASE_PUBLISHABLE_KEY':'public'},{'CORS_ORIGINS':'*'}])
def test_bad_production_configuration_refuses_startup(extra):
    env={**os.environ,'SIMPLIFIER_LOAD_DOTENV':'0','ENVIRONMENT':'production','SUPABASE_URL':'https://example.supabase.co','SUPABASE_PUBLISHABLE_KEY':'test-public-key','CORS_ORIGINS':'https://app.example',**extra}
    result=subprocess.run([sys.executable,'-c','from app.main import app'],env=env,cwd='backend',capture_output=True,text=True)
    assert result.returncode != 0
    assert 'PRODUCTION CONFIG ERROR' in result.stderr


def test_local_identity_survives_new_process_and_is_not_shared(tmp_path,monkeypatch):
    monkeypatch.setenv('AUTH_MODE','local')
    identity,cookie=auth.development_owner(None)
    env={**os.environ,'PYTHONPATH':'backend'}
    result=subprocess.run([sys.executable,'-c',"import sys; from app.core.auth import development_owner; print(development_owner(sys.argv[1])[0])",cookie],env=env,capture_output=True,text=True)
    assert result.returncode==0
    assert result.stdout.strip()==identity
    assert auth.development_owner(None)[0]!=identity
