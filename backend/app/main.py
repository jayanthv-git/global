from contextlib import asynccontextmanager
from fastapi import FastAPI
from .db import init_db, Session
from .services.pathways import seed_providers
from .routers import checkin, privacy, referrals, demo, operations, progress
@asynccontextmanager
async def lifespan(app):
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
