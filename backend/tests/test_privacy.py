import pytest
from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.exc import DatabaseError
from backend.app.models import AuditLog, Identity, Consent
from backend.app.services.consent import require_consent
from .conftest import headers

def test_guard_revocation_immediate(client,db):
    provider=db.get(Identity,'provider')
    with pytest.raises(HTTPException): require_consent(db,'alice',provider,'care_handoff',['scores'],'test')
    r=client.post('/api/consents',headers=headers(),json={'grantee':'primary','scope':['scores']})
    assert r.status_code==201
    assert require_consent(db,'alice',provider,'care_handoff',['scores'],'test')
    with pytest.raises(HTTPException): require_consent(db,'alice',provider,'care_handoff',['physical_context'],'test')
    assert client.delete('/api/consents/'+r.json()['id'],headers=headers()).status_code==200
    with pytest.raises(HTTPException): require_consent(db,'alice',provider,'care_handoff',['scores'],'test')
    assert len(db.scalars(select(AuditLog).where(AuditLog.action=='read.denied')).all())==3
@pytest.mark.parametrize('sql',["UPDATE audit_log SET action='tampered'","DELETE FROM audit_log"])
def test_audit_immutable_raw_sql(db,sql):
    db.add(AuditLog(user_id='alice',actor='alice',action='test',resource='test')); db.commit()
    with pytest.raises(DatabaseError,match='append-only'):
        db.execute(text(sql)); db.commit()
    db.rollback()
    assert db.scalar(select(AuditLog)).action=='test'
def test_consent_owner_isolation(client):
    c=client.post('/api/consents',headers=headers(),json={'grantee':'primary','scope':['scores']}).json()
    assert client.delete('/api/consents/'+c['id'],headers=headers('bob')).status_code==404
    assert client.get('/api/consents',headers=headers('bob')).json()==[]

def test_access_history_identifies_role_and_grantee(client,db):
    provider=db.get(Identity,'provider')
    with pytest.raises(HTTPException): require_consent(db,'alice',provider,'care_handoff',['scores'],'test')
    row=client.get('/api/audit',headers=headers()).json()[0]
    assert row['actor_role']=='provider' and row['grantee']=='primary'

def test_operational_gate_never_grants_patient_content(db):
    reviewer=db.get(Identity,'clinician')
    assert require_consent(db,'alice',reviewer,'care_handoff',[],'queue:demo',operational=True) is False
    with pytest.raises(HTTPException): require_consent(db,'alice',reviewer,'care_handoff',['scores'],'queue:demo',operational=True)
    with pytest.raises(HTTPException): require_consent(db,'alice',db.get(Identity,'provider'),'care_handoff',[],'test')
