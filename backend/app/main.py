from contextlib import asynccontextmanager
from fastapi import FastAPI
from .db import init_db, Session
from .services.pathways import seed_providers
from .routers import checkin
@asynccontextmanager
async def lifespan(app):
    init_db()
    with Session() as db: seed_providers(db)
    yield
app=FastAPI(title='Saha • local wellbeing demo',lifespan=lifespan)
app.include_router(checkin.router)
@app.get('/api/health')
def health(): return {'status':'ok','mode':'LOCAL_SYNTHETIC_DEMO'}
