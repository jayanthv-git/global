from collections import defaultdict
from statistics import mean
from sqlalchemy import select
from ..models import User,Referral,Followup,Assessment,Escalation,AdverseEvent
from ..settings import config
DIMENSIONS={'all','age_band','gender','nationality','language','geography'}
MINIMUM=config('pathways.yaml')['minimum_aggregate_size']
def elapsed(later,earlier):
    # SQLite discards tzinfo; all persisted datetimes are UTC.
    return (later.replace(tzinfo=None)-earlier.replace(tzinfo=None)).total_seconds()
def aggregate(db,dimension='all',minimum=None):
    threshold=max(10,minimum if minimum is not None else MINIMUM)
    if dimension not in DIMENSIONS: raise ValueError('Unsupported dimension')
    users=db.scalars(select(User).where(User.cohort.is_(True),User.synthetic.is_(True))).all()
    groups=defaultdict(list)
    for u in users: groups['all' if dimension=='all' else getattr(u,dimension)].append(u.id)
    results=[]
    for group,ids in sorted(groups.items()):
        if len(ids)<threshold: continue
        refs=db.scalars(select(Referral).where(Referral.user_id.in_(ids))).all()
        followups=db.scalars(select(Followup).where(Followup.user_id.in_(ids))).all()
        escalations=db.scalars(select(Escalation).where(Escalation.user_id.in_(ids))).all()
        assessments=db.scalars(select(Assessment).where(Assessment.user_id.in_(ids)).order_by(Assessment.created_at)).all()
        adverse=set(db.scalars(select(AdverseEvent.user_id).where(AdverseEvent.user_id.in_(ids))).all())
        # One contribution per participant, not per visit.
        def rate(success,denominator):
            if len(denominator)<threshold: return None
            a=len(success); b=len(denominator)-a
            if 0<a<threshold or 0<b<threshold: return None
            return round(100*a/len(denominator),1)
        referred={r.user_id for r in refs}
        funnel={state:rate({r.user_id for r in refs if getattr(r,state+'_at') is not None},referred) for state in ['accepted','booked','attended']}
        by_ref={r.id:r for r in refs}; follow_times=defaultdict(list)
        for f in followups:
            if f.referral_id in by_ref: follow_times[f.user_id].append(elapsed(f.created_at,by_ref[f.referral_id].created_at)/3600)
        def avg(values): return round(mean(values),2) if len(values)>=threshold else None
        changes={}
        for instrument in ['PHQ-9','GAD-7','WHO-5']:
            visits=defaultdict(list)
            for a in assessments:
                if a.instrument==instrument: visits[a.user_id].append(a.score)
            changes[instrument]=avg([scores[-1]-scores[0] for scores in visits.values() if len(scores)>=2])
        contact_times=defaultdict(list)
        for e in escalations:
            if e.contacted_at: contact_times[e.user_id].append(elapsed(e.contacted_at,e.created_at)/60)
        crisis_users={e.user_id for e in escalations}
        resolved={u for u in crisis_users if all(e.status=='resolved' for e in escalations if e.user_id==u)}
        results.append({'group':group,'participants':len(ids),'handoff':{'suggested':100.0 if len(referred)>=threshold else None,**funnel},
          'followup_hours':avg([min(x) for x in follow_times.values()]),'symptom_change':changes,
          'crisis_completion':rate(resolved,crisis_users),'human_contact_minutes':avg([min(x) for x in contact_times.values()]),
          'adverse_event_participants':len(adverse) if len(adverse)>=threshold and len(ids)-len(adverse)>=threshold else None})
    return {'synthetic':True,'label':'SYNTHETIC DATA','seed':1042,'dimension':dimension,'minimum':threshold,'groups':results}
