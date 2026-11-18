import hashlib
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from .db import get_db
from .models import Identity
security=HTTPBearer(auto_error=False)
def token_hash(token): return hashlib.sha256(token.encode()).hexdigest()
def actor(credentials: HTTPAuthorizationCredentials | None = Depends(security), db=Depends(get_db)):
    if not credentials: raise HTTPException(401,'Authentication required')
    identity=db.scalar(select(Identity).where(Identity.token_hash==token_hash(credentials.credentials)))
    if not identity: raise HTTPException(401,'Invalid session')
    return identity
def participant(identity=Depends(actor)):
    if identity.role != 'participant': raise HTTPException(403,'Participant session required')
    return identity
def clinician(identity=Depends(actor)):
    if identity.role != 'clinician': raise HTTPException(403,'Simulated clinician session required')
    return identity
