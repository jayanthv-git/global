import pytest
from sqlalchemy import select
from backend.app.models import Escalation,Assessment
from backend.app.services.crisis import triggers
from backend.app.services.crypto import decrypt
from .conftest import headers
@pytest.mark.parametrize('item9',[1,2,3])
def test_item9_always_escalates(client,db,item9):
    r=client.post('/api/assessments',headers=headers(),json={'instrument':'PHQ-9','responses':[0]*8+[item9]})
    assert r.status_code==201
    assert r.json()['score']==item9 and r.json()['escalation_id']
    assert db.scalar(select(Escalation)).status=='open'
    a=db.scalar(select(Assessment))
    assert decrypt(a.responses_encrypted)['answers'][-1]==item9
    assert 'answers' not in a.responses_encrypted

def test_zero_does_not_escalate(client,db):
    r=client.post('/api/assessments',headers=headers(),json={'instrument':'PHQ-9','responses':[3]*8+[0]})
    assert r.json()['escalation_id'] is None
@pytest.mark.parametrize('text',['I want to KILL MYSELF','suicide','أفكر في الانتحار','إيذاء نفسي'])
def test_keywords(text): assert triggers(text=text)
def test_urgent_button(client):
    assert client.post('/api/crisis',headers=headers(),json={'urgent':True}).json()['escalation_id']
def test_auth_required(client): assert client.post('/api/crisis',json={'urgent':True}).status_code==401
