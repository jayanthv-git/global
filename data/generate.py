"""Reproducible logical records. Encryption nonces and UUIDs intentionally vary."""
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from backend.app.models import User, Assessment, Referral, Followup, Escalation, AdverseEvent
from backend.app.services.crypto import encrypt
from backend.app.services.scoring import score
SEED=1042
BASE=datetime(2026,11,1,9,tzinfo=timezone.utc)
def cohort(seed=SEED,n=120):
    rng=random.Random(seed)
    for i in range(n):
        yield {'id':f'synthetic-{seed}-{i:03d}','age_band':['18-24','25-44','45-64'][i%3],
          'gender':['female','male','not_stated'][(i//3)%3],'nationality':['Emirati','other'][i%2],
          'language':['en','ar'][(i//2)%2],'geography':['Abu Dhabi','Al Ain','Al Dhafra'][(i//5)%3],
          'initial':rng.randint(7,20),'change':rng.randint(-6,4),'status':rng.choice(['suggested','accepted','booked','attended','attended']),
          'followup_hours':rng.randint(12,120),'crisis':i%2==0,'resolved':i%4==0,'contact_minutes':rng.randint(4,90),'adverse':i%11==0}
def answers(total,n,maximum): return [min(maximum,max(0,total-i*maximum)) for i in range(n)]
def seed_cohort(db,seed=SEED,n=120):
    if db.scalar(select(User.id).where(User.cohort.is_(True))): return
    for row in cohort(seed,n):
        id=row['id']; user=User(**{k:row[k] for k in ['id','age_band','gender','nationality','language','geography']},synthetic=True,cohort=True)
        db.add(user); db.flush()
        for instrument,count,maximum in [('PHQ-9',9,3),('GAD-7',7,3),('WHO-5',5,5)]:
            for visit in range(2):
                total=max(0,min(count*maximum,row['initial']+(row['change'] if visit else 0)))
                response=answers(total,count,maximum); result=score(instrument,response)
                db.add(Assessment(user_id=id,instrument=instrument,score=result['score'],band=result['band'],responses_encrypted=encrypt({'answers':response,'text':''}),created_at=BASE+timedelta(days=visit*14)))
        r=Referral(user_id=id,provider_id='primary',status=row['status'],context_encrypted=encrypt('Synthetic physical-health context'),created_at=BASE,
           accepted_at=BASE+timedelta(hours=1) if row['status']!='suggested' else None,
           booked_at=BASE+timedelta(hours=12) if row['status'] in ['booked','attended'] else None,
           attended_at=BASE+timedelta(days=5) if row['status']=='attended' else None)
        db.add(r); db.flush()
        db.add(Followup(user_id=id,referral_id=r.id,seen=row['status']=='attended',note_encrypted=encrypt('Synthetic follow-up'),created_at=BASE+timedelta(hours=row['followup_hours'])))
        if row['crisis']:
            db.add(Escalation(user_id=id,trigger='synthetic_fixture',status='resolved' if row['resolved'] else 'claimed',claimed_by='synthetic-clinician',created_at=BASE,
                claimed_at=BASE+timedelta(minutes=2),contacted_at=BASE+timedelta(minutes=row['contact_minutes']),
                resolved_at=BASE+timedelta(hours=3) if row['resolved'] else None,resolution_encrypted=encrypt('Synthetic resolution') if row['resolved'] else None))
        if row['adverse']: db.add(AdverseEvent(user_id=id,category='missed_followup',note_encrypted=encrypt('Synthetic adverse event'),created_at=BASE+timedelta(days=7)))
    db.commit()
if __name__=='__main__':
    from backend.app.db import init_db,Session
    from backend.app.services.pathways import seed_providers
    init_db()
    with Session() as db: seed_providers(db); seed_cohort(db)
    print('Synthetic cohort ready; seed 1042, 120 participants. Existing cohort is retained.')
