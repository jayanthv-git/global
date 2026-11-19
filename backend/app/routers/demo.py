import secrets
from typing import Literal
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from ..db import get_db
from ..models import User, Identity, Provider
from ..auth import token_hash
router=APIRouter(prefix='/api/demo')
class DemoSession(BaseModel):
    persona:Literal['adult','crisis','clinician','provider']='adult'
    provider_id:str='primary'
@router.post('/session')
def session(body:DemoSession,db=Depends(get_db)):
    # Deliberately open role selector for the LOCAL SYNTHETIC demonstration only.
    if body.persona=='provider' and not db.get(Provider,body.provider_id): raise HTTPException(404,'Unknown provider')
    user_id='demo-'+body.persona if body.persona in ('adult','crisis') else None
    if user_id and not db.get(User,user_id):
        db.add(User(id=user_id)); db.flush()
    token=secrets.token_urlsafe(32)
    id='session-'+secrets.token_hex(10)
    db.add(Identity(id=id,user_id=user_id,role='participant' if user_id else body.persona,
        grantee=body.provider_id if body.persona=='provider' else None,token_hash=token_hash(token)))
    db.commit()
    return {'token':token,'user_id':user_id,'role':body.persona,'synthetic':True}
