from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import select
from ..auth import clinician, actor
from ..db import get_db
from ..models import Escalation,User,AdverseEvent,now
from ..services.crypto import encrypt
from ..services.consent import audit
from ..services.metrics import aggregate,elapsed
from ..settings import config
router=APIRouter(prefix='/api')
def owner(who): return who.grantee or who.id
@router.get('/clinician/queue')
def queue(who=Depends(clinician),db=Depends(get_db)):
    # Operational task markers only. No user identifiers, triggers, health records or contact details.
    rows=db.scalars(select(Escalation).join(User).where(User.cohort.is_(False)).order_by(Escalation.created_at.desc())).all()
    result=[]
    for e in rows:
        result.append({k:getattr(e,k) for k in ['id','status','created_at','claimed_at','contacted_at','resolved_at']}|{'mine':e.claimed_by==owner(who),'elapsed_minutes':round(elapsed(now(),e.created_at)/60,1)})
        audit(db,e.user_id,who.id,'queue.operational_read',e.id)
    db.commit()
    return {'simulated':True,'target_minutes':config('pathways.yaml')['review_target_minutes'],'target_status':'UNVERIFIED','tasks':result}
class Resolution(BaseModel):
    note:str=Field(min_length=3,max_length=2000)
@router.post('/clinician/escalations/{id}/claim')
def claim(id:str,who=Depends(clinician),db=Depends(get_db)):
    from sqlalchemy import update
    changed=db.execute(update(Escalation).where(Escalation.id==id,Escalation.status=='open').values(status='claimed',claimed_by=owner(who),claimed_at=now())).rowcount
    if changed!=1: db.rollback(); raise HTTPException(409,'Task is not open')
    e=db.get(Escalation,id); audit(db,e.user_id,who.id,'crisis.claimed',id); db.commit()
    return {'status':'claimed'}
def claimed_task(db,id,who):
    e=db.get(Escalation,id)
    if not e or e.status!='claimed' or e.claimed_by!=owner(who): raise HTTPException(409,'Claim this task first')
    return e
@router.post('/clinician/escalations/{id}/contact')
def contact(id:str,who=Depends(clinician),db=Depends(get_db)):
    e=claimed_task(db,id,who)
    if not e.contacted_at:
        e.contacted_at=now();audit(db,e.user_id,who.id,'crisis.contact_simulated',id);db.commit()
    return {'status':'contacted','simulated':True}
@router.post('/clinician/escalations/{id}/resolve')
def resolve(id:str,body:Resolution,who=Depends(clinician),db=Depends(get_db)):
    e=claimed_task(db,id,who)
    if not e.contacted_at: raise HTTPException(409,'Record human contact before resolution')
    if not body.note.strip(): raise HTTPException(422,'Resolution note required')
    e.status='resolved';e.resolved_at=now();e.resolution_encrypted=encrypt(body.note)
    audit(db,e.user_id,who.id,'crisis.resolved_by_human',id);db.commit()
    return {'status':'resolved'}
class AdverseInput(BaseModel):
    escalation_id:str
    category:Literal['missed_followup','incorrect_route','technical_failure']
    note:str=Field(min_length=3,max_length=2000)
@router.post('/clinician/adverse-events',status_code=201)
def adverse(body:AdverseInput,who=Depends(clinician),db=Depends(get_db)):
    e=db.get(Escalation,body.escalation_id)
    if not e or e.claimed_by!=owner(who): raise HTTPException(403,'Only the task owner can record an event')
    row=AdverseEvent(user_id=e.user_id,category=body.category,note_encrypted=encrypt(body.note))
    db.add(row);db.flush();audit(db,e.user_id,who.id,'adverse_event.created',row.id);db.commit()
    return {'id':row.id,'simulated':True}
@router.get('/metrics/aggregate')
def metrics(dimension:Literal['all','age_band','gender','nationality','language','geography']='all',who=Depends(actor),db=Depends(get_db)):
    if who.role!='clinician': raise HTTPException(403,'Simulated clinician session required')
    return aggregate(db,dimension)

@router.get('/clinician/adverse-events')
def adverse_log(who=Depends(clinician),db=Depends(get_db)):
    rows=db.scalars(select(AdverseEvent).join(User).where(User.cohort.is_(False)).order_by(AdverseEvent.created_at.desc())).all()
    result=[]
    for row in rows:
        result.append({'id':row.id,'category':row.category,'created_at':row.created_at})
        audit(db,row.user_id,who.id,'adverse_event.operational_read',row.id)
    db.commit()
    return {'simulated':True,'items':result}
