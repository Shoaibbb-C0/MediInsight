from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from collections import defaultdict, deque
import os
import time
from app.core import auth
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

# Fail-closed production check
settings.validate_production()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Medical laboratory report understanding backend for patients",
    version="0.1.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[value.strip() for value in os.getenv("CORS_ORIGINS", "http://127.0.0.1:3001,http://localhost:3000,http://127.0.0.1:3000").split(",") if value.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

_limits = defaultdict(deque)

@app.middleware("http")
async def identity_and_privacy(request: Request, call_next):
    if not request.url.path.startswith("/api/") or request.method == "OPTIONS":
        return await call_next(request)
    origin=request.headers.get("origin")
    allowed=[item.strip() for item in os.getenv("CORS_ORIGINS","http://127.0.0.1:3001,http://localhost:3000,http://127.0.0.1:3000").split(",")]
    if origin and origin not in allowed:
        return JSONResponse({"detail":"Origin not allowed."},status_code=403)
    try:
        limit=(settings.MAX_FILE_SIZE_MB+1)*1024*1024
        if int(request.headers.get("content-length",0)) > limit:
            return JSONResponse({"detail":"Upload exceeds request limit."},status_code=413)
    except ValueError:
        return JSONResponse({"detail":"Invalid content length."},status_code=400)
    public=request.url.path in ['/api/v1/auth/configuration','/api/v1/auth/login','/api/v1/auth/refresh','/api/v1/auth/logout']
    owner_token=access_token=None
    try:
        identity=(request.client.host if request.client else 'unknown') if public else await auth.resolve_identity(request)
        owner_token=auth.owner_context.set(identity)
        access_token=auth.token_context.set(getattr(request.state,'access_token',''))
        now=time.monotonic(); bucket=_limits[(identity,'upload' if request.url.path.endswith('/upload') else 'api')]
        while bucket and bucket[0] < now-60: bucket.popleft()
        if len(bucket) >= (30 if auth.production() else 5000):
            return JSONResponse({"detail":"Too many requests. Try again shortly."},status_code=429,headers={'Retry-After':'60'})
        bucket.append(now)
        if len(_limits)>10000:
            for key in list(_limits):
                if not _limits[key] or _limits[key][-1] < now-60: del _limits[key]
        response=await call_next(request)
        response.headers.update({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'})
        cookie=getattr(request.state,'development_cookie',None)
        if cookie: response.set_cookie('simplifier_dev',cookie,max_age=86400,**auth.cookie_options())
        return response
    except HTTPException as exc:
        return JSONResponse({'detail':exc.detail},status_code=exc.status_code,headers={'Cache-Control':'no-store'})
    finally:
        if owner_token is not None: auth.owner_context.reset(owner_token)
        if access_token is not None: auth.token_context.reset(access_token)

from app.core.body_limit import RequestBodyLimit
app.add_middleware(RequestBodyLimit)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }
