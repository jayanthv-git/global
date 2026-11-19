from sqlalchemy import select
from backend.app.models import Escalation
from .conftest import headers

def test_human_lifecycle_and_no_auto_close(client,db):
    id=client.post('/api/crisis',headers=headers(),json={'urgent':True}).json()['escalation_id']
    path='/api/clinician/escalations/'+id
    h=headers('clinician')
    assert client.post(path+'/resolve',headers=h,json={'note':'demo reviewed'}).status_code==409
    assert client.post(path+'/claim',headers=h).status_code==200
    assert client.post(path+'/claim',headers=h).status_code==409
    assert client.post(path+'/resolve',headers=h,json={'note':'demo reviewed'}).status_code==409
    assert client.post(path+'/contact',headers=h).status_code==200
    assert client.post(path+'/resolve',headers=h,json={'note':'demo reviewed'}).status_code==200
    db.expire_all()
    assert db.get(Escalation,id).resolved_at is not None

def test_queue_redacts_participant_content(client):
    client.post('/api/crisis',headers=headers(),json={'urgent':True})
    tasks=client.get('/api/clinician/queue',headers=headers('clinician')).json()['tasks']
    assert len(tasks)==1
    assert not {'user_id','trigger','responses','resolution_encrypted'} & tasks[0].keys()
    assert client.get('/api/clinician/queue',headers=headers()).status_code==403
