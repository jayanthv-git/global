from datetime import timedelta
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import select
from ..auth import participant
from ..db import get_db
from ..models import Assessment,Followup,Referral,now
from ..services.crypto import encrypt,decrypt
from ..services.consent import audit
from ..services.crisis import triggers,create_escalation
from ..settings import config
router=APIRouter(prefix='/api')
@router.get('/assessments/trend')
def trend(instrument:Literal['PHQ-9','GAD-7','WHO-5']='PHQ-9',who=Depends(participant),db=Depends(get_db)):
    rows=db.scalars(select(Assessment).where(Assessment.user_id==who.user_id,Assessment.instrument==instrument).order_by(Assessment.created_at)).all()
    points=[];previous=None
    threshold=config('pathways.yaml')['change_thresholds'][instrument]
    for row in rows:
        delta=row.score-previous.score if previous and previous.instrument_version==row.instrument_version else None
        points.append({'id':row.id,'created_at':row.created_at,'score':row.score,'band':row.band,'instrument_version':row.instrument_version,
                       'delta':delta,'change_flag':abs(delta)>=threshold if delta is not None else None})
        previous=row
    audit(db,who.user_id,who.id,'assessment.trend_read',instrument);db.commit()
    return {'instrument':instrument,'points':points,'threshold':threshold,'threshold_status':'UNVERIFIED','method':'absolute_score_difference_not_validated_RCI','synthetic':True}
class FollowupInput(BaseModel):
    referral_id:str
    seen:bool
    note:str=Field(default='',max_length=2000)
@router.post('/followups',status_code=201)
def followup(body:FollowupInput,who=Depends(participant),db=Depends(get_db)):
    r=db.get(Referral,body.referral_id)
    if not r or r.user_id!=who.user_id: raise HTTPException(404,'Referral not found')
    f=Followup(user_id=who.user_id,referral_id=r.id,seen=body.seen,note_encrypted=encrypt(body.note))
    db.add(f);db.flush()
    event=create_escalation(db,who.user_id,triggers(text=body.note))
    audit(db,who.user_id,who.id,'followup.created',f.id)
    if event: audit(db,who.user_id,who.id,'crisis.created',event.id)
    db.commit()
    return {'id':f.id,'created_at':f.created_at,'escalation_id':event.id if event else None}
@router.get('/followups')
def history(referral_id:str,who=Depends(participant),db=Depends(get_db)):
    r=db.get(Referral,referral_id)
    if not r or r.user_id!=who.user_id: raise HTTPException(404,'Referral not found')
    rows=db.scalars(select(Followup).where(Followup.referral_id==r.id).order_by(Followup.created_at)).all()
    due=(rows[-1].created_at if rows else r.created_at)+timedelta(days=7)
    return {'items':[{'id':f.id,'seen':f.seen,'note':decrypt(f.note_encrypted),'created_at':f.created_at} for f in rows],
            'due_at':due,'overdue':due.replace(tzinfo=None)<=now().replace(tzinfo=None),'interval_status':'UNVERIFIED_DEMO_INTERVAL'}
