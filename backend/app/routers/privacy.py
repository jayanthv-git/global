from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from ..auth import participant
from ..db import get_db
from ..models import Consent, Provider, AuditLog, Identity, now
from ..services.consent import audit
router=APIRouter(prefix='/api')
class ConsentInput(BaseModel):
    grantee: str
    purpose: Literal['care_handoff']='care_handoff'
    scope: list[Literal['scores','physical_context','followups']]=Field(min_length=1)
@router.post('/consents',status_code=201)
def grant(body:ConsentInput,who=Depends(participant),db=Depends(get_db)):
    if not db.get(Provider,body.grantee): raise HTTPException(404,'Unknown provider')
    c=Consent(user_id=who.user_id,grantee=body.grantee,purpose=body.purpose,scope=sorted(set(body.scope)))
    db.add(c); db.flush()
    audit(db,who.user_id,who.id,'consent.granted',c.id)
    db.commit()
    return serialize(c)
def serialize(c):
    return {k:getattr(c,k) for k in ('id','grantee','purpose','scope','granted_at','revoked_at')}
@router.get('/consents')
def list_consents(who=Depends(participant),db=Depends(get_db)):
    return [serialize(c) for c in db.scalars(select(Consent).where(Consent.user_id==who.user_id).order_by(Consent.granted_at.desc()))]
@router.delete('/consents/{id}')
def revoke(id:str,who=Depends(participant),db=Depends(get_db)):
    c=db.get(Consent,id)
    if not c or c.user_id!=who.user_id: raise HTTPException(404,'Consent not found')
    if not c.revoked_at:
        c.revoked_at=now()
        audit(db,who.user_id,who.id,'consent.revoked',c.id)
        db.commit()
    return serialize(c)
@router.get('/audit')
def audit_history(who=Depends(participant),db=Depends(get_db)):
    rows=[]
    for x in db.scalars(select(AuditLog).where(AuditLog.user_id==who.user_id).order_by(AuditLog.created_at.desc())):
        identity=db.get(Identity,x.actor)
        row={k:getattr(x,k) for k in ('id','actor','action','resource','created_at')}
        row.update(actor_role=identity.role if identity else 'system',grantee=identity.grantee if identity else None)
        rows.append(row)
    return rows
