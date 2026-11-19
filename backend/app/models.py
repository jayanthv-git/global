import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, event, DDL
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def now():
    return datetime.now(timezone.utc)
def uid():
    return str(uuid.uuid4())
class UTCDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True
    def process_bind_param(self,value,dialect):
        if value is None: return None
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    def process_result_value(self,value,dialect):
        return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value
class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    age_band: Mapped[str] = mapped_column(String(32), default='25-44')
    gender: Mapped[str] = mapped_column(String(32), default='not_stated')
    nationality: Mapped[str] = mapped_column(String(32), default='not_stated')
    language: Mapped[str] = mapped_column(String(8), default='en')
    geography: Mapped[str] = mapped_column(String(40), default='Abu Dhabi')
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    cohort: Mapped[bool] = mapped_column(Boolean, default=False)
class Identity(Base):
    __tablename__ = 'identities'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    role: Mapped[str] = mapped_column(String(20))
    grantee: Mapped[str | None] = mapped_column(String(50), nullable=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
class Assessment(Base):
    __tablename__ = 'assessments'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    instrument: Mapped[str] = mapped_column(String(12))
    instrument_version: Mapped[str] = mapped_column(String(40), default='placeholder-1')
    responses_encrypted: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer)
    band: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=now)
class Consent(Base):
    __tablename__ = 'consents'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    purpose: Mapped[str] = mapped_column(String(40))
    grantee: Mapped[str] = mapped_column(String(50))
    scope: Mapped[list] = mapped_column(JSON)
    granted_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=now)
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
class Provider(Base):
    __tablename__ = 'providers'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    step: Mapped[str] = mapped_column(String(40))
    languages: Mapped[list] = mapped_column(JSON)
    cost: Mapped[str] = mapped_column(String(20))
    channel: Mapped[str] = mapped_column(String(20))
    physical_context: Mapped[bool] = mapped_column(Boolean, default=False)
    eligibility: Mapped[str] = mapped_column(Text)
    next_step: Mapped[str] = mapped_column(Text)
class Referral(Base):
    __tablename__ = 'referrals'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    provider_id: Mapped[str] = mapped_column(ForeignKey('providers.id'))
    status: Mapped[str] = mapped_column(String(20), default='suggested')
    context_encrypted: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=now)
    accepted_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    booked_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    attended_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
class Escalation(Base):
    __tablename__ = 'escalations'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    trigger: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default='open')
    claimed_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=now)
    claimed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    contacted_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    resolution_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
class Followup(Base):
    __tablename__ = 'followups'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    referral_id: Mapped[str] = mapped_column(ForeignKey('referrals.id'))
    note_encrypted: Mapped[str] = mapped_column(Text)
    seen: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=now)
class PathwayRule(Base):
    __tablename__ = 'pathway_rules'
    version: Mapped[str] = mapped_column(String(40), primary_key=True)
    definition: Mapped[dict] = mapped_column(JSON)
    loaded_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=now)
class AuditLog(Base):
    __tablename__ = 'audit_log'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), nullable=True, index=True)
    actor: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(60))
    resource: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=now)
class AdverseEvent(Base):
    __tablename__ = 'adverse_events'
    id: Mapped[str] = mapped_column(String(40), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    category: Mapped[str] = mapped_column(String(40))
    note_encrypted: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=now)

for operation in ('UPDATE', 'DELETE'):
    event.listen(AuditLog.__table__, 'after_create', DDL(
        f"CREATE TRIGGER audit_no_{operation.lower()} BEFORE {operation} ON audit_log "
        "BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END"
    ).execute_if(dialect='sqlite'))
event.listen(AuditLog.__table__, 'after_create', DDL('''
CREATE OR REPLACE FUNCTION reject_audit_mutation() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'audit_log is append-only'; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER audit_immutable BEFORE UPDATE OR DELETE ON audit_log
FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation();
''').execute_if(dialect='postgresql'))
