from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from ..auth import participant
from ..db import get_db
from ..models import Assessment, AuditLog, Escalation
from ..schemas import AssessmentInput, CrisisInput
from ..services.scoring import score, DEFINITIONS
from ..services.crypto import encrypt
from ..services.crisis import triggers, create_escalation, guidance
from ..services.pathways import options
router=APIRouter(prefix='/api')
@router.get('/instruments')
def instruments(): return DEFINITIONS
@router.get('/crisis/guidance')
def crisis_guidance(): return guidance()
@router.post('/crisis')
def crisis(body:CrisisInput,who=Depends(participant),db=Depends(get_db)):
    event=create_escalation(db,who.user_id,triggers(text=body.text,urgent=body.urgent))
    if event: db.add(AuditLog(user_id=who.user_id,actor=who.id,action='crisis.created',resource=event.id))
    db.commit()
    return {'escalation_id':event.id if event else None,**guidance()}
@router.post('/assessments',status_code=201)
def assess(body:AssessmentInput,who=Depends(participant),db=Depends(get_db)):
    try: result=score(body.instrument,body.responses)
    except ValueError as e: raise HTTPException(422,str(e))
    row=Assessment(user_id=who.user_id,instrument=body.instrument,score=result['score'],band=result['band'],responses_encrypted=encrypt({'answers':body.responses,'text':body.text}))
    db.add(row)
    event=create_escalation(db,who.user_id,triggers(body.instrument,body.responses,body.text))
    db.flush()
    db.add(AuditLog(user_id=who.user_id,actor=who.id,action='assessment.created',resource=row.id))
    if event: db.add(AuditLog(user_id=who.user_id,actor=who.id,action='crisis.created',resource=event.id))
    db.commit()
    return {**result,'id':row.id,'created_at':row.created_at,'escalation_id':event.id if event else None,'crisis':guidance() if event else None}
@router.get('/navigation/options')
def navigation(language:Literal['en','ar']='en',cost:Literal['any','free','paid']='any',urgency:Literal['routine','soon','urgent']='routine',physical:bool=False,channel:Literal['any','online','in_person']='any',who=Depends(participant),db=Depends(get_db)):
    latest=db.scalar(select(Assessment).where(Assessment.user_id==who.user_id).order_by(Assessment.created_at.desc()))
    if not latest: raise HTTPException(409,'Complete a demo check-in first')
    result=options(db,latest.band,language,cost,urgency,physical,channel)
    pending=db.scalar(select(Escalation.id).where(Escalation.user_id==who.user_id,Escalation.status!='resolved'))
    result['open_escalation']=bool(pending)
    return result
