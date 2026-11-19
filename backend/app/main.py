from contextlib import asynccontextmanager
from fastapi import FastAPI
from .db import init_db, Session
from .services.pathways import seed_providers
from .routers import checkin, privacy, referrals, demo, operations, progress
@asynccontextmanager
async def lifespan(app):
    if not app.dependency_overrides:
        init_db()
        with Session() as db:
            seed_providers(db)
            from data.generate import seed_cohort
            seed_cohort(db)
    yield
app=FastAPI(title='Saha • local wellbeing demo',lifespan=lifespan)
app.include_router(checkin.router)
app.include_router(privacy.router)
app.include_router(referrals.router)
app.include_router(demo.router)
app.include_router(operations.router)
app.include_router(progress.router)
@app.get('/api/health')
def health(): return {'status':'ok','mode':'LOCAL_SYNTHETIC_DEMO'}

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from urllib.parse import urlparse
from .settings import ROOT
app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','testserver'])
@app.middleware('http')
async def local_boundaries(request:Request,call_next):
    origin=request.headers.get('origin')
    if request.method not in ('GET','HEAD','OPTIONS') and origin and urlparse(origin).netloc != request.headers.get('host'):
        return JSONResponse({'detail':'Cross-origin writes are disabled'},status_code=403)
    response=await call_next(request)
    if request.url.path.startswith('/api'):
        response.headers['Cache-Control']='no-store'
        response.headers['Pragma']='no-cache'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    return response
if (ROOT/'frontend/dist').exists():
    app.mount('/',StaticFiles(directory=ROOT/'frontend/dist',html=True),name='frontend')
