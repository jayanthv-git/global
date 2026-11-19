from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from ..db import get_db
from ..auth import participant, actor
from ..models import Referral, Provider, Assessment, Followup, now
from ..services.crypto import encrypt, decrypt
from ..services.consent import require_consent, audit, SCOPES
from ..services.crisis import create_escalation, triggers
router=APIRouter(prefix='/api')
class ReferralInput(BaseModel):
    provider_id:str
    physical_context:str=Field(default='',max_length=2000)
class ReferralStatus(BaseModel):
    status:Literal['accepted','booked','attended','lapsed']
def serialized(r):
    return {k:getattr(r,k) for k in ('id','provider_id','status','created_at','accepted_at','booked_at','attended_at')}
def own(db,id,who):
    row=db.get(Referral,id)
    if not row or row.user_id!=who.user_id: raise HTTPException(404,'Referral not found')
    return row
@router.get('/referrals')
def referrals(who=Depends(participant),db=Depends(get_db)):
    return [serialized(r) for r in db.scalars(select(Referral).where(Referral.user_id==who.user_id).order_by(Referral.created_at.desc()))]
@router.post('/referrals',status_code=201)
def create(body:ReferralInput,who=Depends(participant),db=Depends(get_db)):
    if not db.get(Provider,body.provider_id): raise HTTPException(404,'Provider not found')
    row=Referral(user_id=who.user_id,provider_id=body.provider_id,context_encrypted=encrypt(body.physical_context))
    db.add(row); db.flush()
    event=create_escalation(db,who.user_id,triggers(text=body.physical_context))
    audit(db,who.user_id,who.id,'referral.suggested',row.id)
    if event: audit(db,who.user_id,who.id,'crisis.created',event.id)
    db.commit()
    return {**serialized(row),'escalation_id':event.id if event else None}
@router.patch('/referrals/{id}')
def update(id:str,body:ReferralStatus,who=Depends(participant),db=Depends(get_db)):
    row=own(db,id,who)
    allowed={'suggested':['accepted','lapsed'],'accepted':['booked','lapsed'],'booked':['attended','lapsed'],'attended':[],'lapsed':[]}
    if body.status not in allowed[row.status]: raise HTTPException(409,'Invalid referral transition')
    row.status=body.status
    if body.status!='lapsed': setattr(row,body.status+'_at',now())
    audit(db,who.user_id,who.id,'referral.'+body.status,row.id)
    db.commit()
    return serialized(row)
@router.get('/providers/referrals/{id}/summary')
def summary(id:str,scopes:str=Query(default='scores,physical_context,followups'),who=Depends(actor),db=Depends(get_db)):
    row=db.get(Referral,id)
    if not row or who.role!='provider' or who.grantee!=row.provider_id:
        raise HTTPException(404,'Referral not found')
    fields=set(scopes.split(','))
    if not fields or not fields.issubset(SCOPES): raise HTTPException(422,'Unknown scope')
    require_consent(db,row.user_id,who,'care_handoff',fields,'referral:'+id)
    result={'referral_id':row.id,'status':row.status,'synthetic':True,'scope':sorted(fields)}
    if 'physical_context' in fields: result['physical_context']=decrypt(row.context_encrypted)
    if 'scores' in fields:
        result['scores']=[{'instrument':a.instrument,'score':a.score,'band':a.band,'created_at':a.created_at,'placeholder':True} for a in db.scalars(select(Assessment).where(Assessment.user_id==row.user_id).order_by(Assessment.created_at))]
    if 'followups' in fields:
        result['followups']=[{'seen':f.seen,'note':decrypt(f.note_encrypted),'created_at':f.created_at} for f in db.scalars(select(Followup).where(Followup.referral_id==row.id).order_by(Followup.created_at))]
    return result
