import re
import unicodedata
from ..models import Escalation
from ..settings import config
RULES = config('pathways.yaml')
def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))
def triggers(instrument=None, responses=None, text='', urgent=False):
    reasons=[]
    if urgent: reasons.append('urgent_button')
    if instrument == 'PHQ-9' and responses and len(responses) == 9 and responses[8] > 0:
        reasons.append('phq9_item9')
    normalized=normalize(text)
    if any(re.search(r'(?<!\w)' + re.escape(normalize(phrase)) + r'(?!\w)',normalized) for phrases in RULES['crisis_keywords'].values() for phrase in phrases):
        reasons.append('explicit_keyword')
    return reasons

def create_escalation(db, user_id, reasons):
    if not reasons: return None
    event=Escalation(user_id=user_id, trigger=','.join(reasons))
    db.add(event)
    db.flush()
    return event

def guidance():
    return {'guidance_key':'urgent_guidance','staffing':'SIMULATED_CLINICIAN',
            'human_online':False,'hotlines':config('hotlines.yaml')['hotlines'],
            'warning':'NEEDS_VERIFICATION','real_emergency_dispatch':False}
