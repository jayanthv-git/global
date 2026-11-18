from sqlalchemy import select
from ..models import Provider, PathwayRule
from ..settings import config
RULES=config('pathways.yaml')
PROVIDERS=[
 ('self','Quiet Steps','self_help','free','online',False),
 ('community','Neighbour Circle','community','free','in_person',False),
 ('primary','Palm Primary Care','primary_care','free','in_person',True),
 ('tele','Bridge Telehealth','tele_mental_health','paid','online',True),
 ('specialist','Horizon Specialist','specialist','paid','in_person',True),
]
def seed_providers(db):
    for id,name,step,cost,channel,physical in PROVIDERS:
        if not db.get(Provider,id):
            db.add(Provider(id=id,name=name,step=step,languages=['en','ar'],cost=cost,channel=channel,physical_context=physical,
                eligibility='Demo adults 18+. Eligibility must be confirmed with a real service.',
                next_step='Create a demo referral and choose what to share. No real booking is made.'))
    if not db.get(PathwayRule,RULES['version']):
        db.add(PathwayRule(version=RULES['version'],definition=RULES))
    db.commit()

def options(db,band,language,cost,urgency,physical,channel):
    steps=list(RULES['steps'][band])
    if physical and 'primary_care' not in steps: steps.insert(0,'primary_care')
    if urgency=='soon' and 'primary_care' not in steps: steps.insert(0,'primary_care')
    result=[]
    for p in db.scalars(select(Provider)).all():
        reasons=[]
        if p.step not in steps: reasons.append('outside_suggested_step')
        if language not in p.languages: reasons.append('language_unavailable')
        if cost!='any' and p.cost!=cost: reasons.append('cost_mismatch')
        if channel!='any' and p.channel!=channel: reasons.append('channel_mismatch')
        if physical and not p.physical_context: reasons.append('physical_context_review_needed')
        result.append({'id':p.id,'name':p.name,'step':p.step,'cost':p.cost,'channel':p.channel,
                       'eligible':not reasons,'reasons':reasons,'fictional':True,
                       'eligibility_key':'provider_eligibility','next_step_key':'provider_next_step'})
    result.sort(key=lambda p:(not p['eligible'],p['step'] not in steps))
    return {'options':result,'rule_version':RULES['version'],'rule_status':RULES['status'],'band':band,
            'crisis':urgency=='urgent','guidance_key':'urgent_guidance' if urgency=='urgent' else None}
