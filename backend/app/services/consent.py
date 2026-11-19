from fastapi import HTTPException
from sqlalchemy import select
from ..models import Consent, AuditLog
SCOPES={'scores','physical_context','followups'}
def audit(db,user_id,actor,action,resource):
    db.add(AuditLog(user_id=user_id,actor=actor,action=action,resource=resource))
def require_consent(db,user_id,identity,purpose,scopes,resource,*,operational=False):
    """Only gate for third-party patient content. No cached permissions."""
    if identity.role not in ('provider','clinician'):
        raise HTTPException(403,'Third-party session required')
    grantee=identity.grantee or identity.id
    active=db.scalars(select(Consent).where(Consent.user_id==user_id,Consent.grantee==grantee,Consent.purpose==purpose,Consent.revoked_at.is_(None))).all()
    allowed=set().union(*(set(c.scope) for c in active)) if active else set()
    if operational:
        # A queue must remain actionable without disclosing any patient fields.
        # The same gate checks live consent, but only marker-only reads are allowed.
        if identity.role!='clinician' or scopes:
            raise HTTPException(403,'Operational access cannot include patient fields')
        audit(db,user_id,identity.id,'read.operational_only',resource)
        db.commit()
        return False  # No permission to read patient content is granted.
    if not scopes or not set(scopes).issubset(allowed):
        audit(db,user_id,identity.id,'read.denied',resource)
        db.commit()
        raise HTTPException(403,'Active consent is required for each requested field')
    audit(db,user_id,identity.id,'read.allowed',resource+':'+','.join(sorted(scopes)))
    db.commit()
    return True
