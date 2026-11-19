import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.models import Base, User, Identity
from backend.app.db import get_db
from backend.app.auth import token_hash
from backend.app.main import app
from backend.app.services.pathways import seed_providers
@pytest.fixture
def db(monkeypatch):
    from cryptography.fernet import Fernet
    monkeypatch.setenv("FIELD_ENCRYPTION_KEY",Fernet.generate_key().decode())
    engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    @event.listens_for(engine,'connect')
    def fk(conn,_): conn.execute('PRAGMA foreign_keys=ON')
    Base.metadata.create_all(engine)
    session=sessionmaker(bind=engine,expire_on_commit=False)()
    for id in ('alice','bob'): session.add(User(id=id))
    session.flush()
    for id,role,user,grantee in [('alice','participant','alice',None),('bob','participant','bob',None),('clinician','clinician',None,None),('provider','provider',None,'primary')]:
        session.add(Identity(id=id,role=role,user_id=user,grantee=grantee,token_hash=token_hash(id)))
    session.commit()
    seed_providers(session)
    yield session
    session.close(); engine.dispose()
@pytest.fixture
def client(db):
    app.dependency_overrides[get_db]=lambda:db
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()
def headers(actor='alice'): return {'Authorization':f'Bearer {actor}'}
