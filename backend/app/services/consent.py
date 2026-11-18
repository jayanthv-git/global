from fastapi import HTTPException
from sqlalchemy import select
from ..models import Consent, AuditLog
SCOPES={'scores','physical_context','followups'}
def audit(db,user_id,actor,action,resource):
    db.add(AuditLog(user_id=user_id,actor=actor,action=action,resource=resource))
def require_consent(db,user_id,identity,purpose,scopes,resource):
    """Only gate for third-party patient content. No cached permissions."""
    if identity.role not in ('provider','clinician'):
        raise HTTPException(403,'Third-party session required')
    grantee=identity.grantee or identity.id
    active=db.scalars(select(Consent).where(Consent.user_id==user_id,Consent.grantee==grantee,Consent.purpose==purpose,Consent.revoked_at.is_(None))).all()
    allowed=set().union(*(set(c.scope) for c in active)) if active else set()
    if not set(scopes).issubset(allowed):
        audit(db,user_id,identity.id,'read.denied',resource)
        db.commit()
        raise HTTPException(403,'Active consent is required for each requested field')
    audit(db,user_id,identity.id,'read.allowed',resource+':'+','.join(sorted(scopes)))
    db.commit()
    return True
