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

def test_adverse_event_log_is_recorded_and_redacted(client):
    id=client.post('/api/crisis',headers=headers(),json={'urgent':True}).json()['escalation_id']
    h=headers('clinician')
    client.post('/api/clinician/escalations/'+id+'/claim',headers=h)
    r=client.post('/api/clinician/adverse-events',headers=h,json={'escalation_id':id,'category':'technical_failure','note':'Synthetic failure record'})
    assert r.status_code==201
    log=client.get('/api/clinician/adverse-events',headers=h).json()
    assert log['simulated'] and log['items'][0]['category']=='technical_failure'
    assert 'note' not in log['items'][0] and 'user_id' not in log['items'][0]
    assert client.get('/api/clinician/adverse-events',headers=headers()).status_code==403

def test_second_reviewer_cannot_take_or_resolve_claimed_task(client,db):
    from backend.app.models import Identity
    from backend.app.auth import token_hash
    db.add(Identity(id='reviewer-two',role='clinician',token_hash=token_hash('reviewer-two')));db.commit()
    id=client.post('/api/crisis',headers=headers(),json={'urgent':True}).json()['escalation_id']
    path='/api/clinician/escalations/'+id
    assert client.post(path+'/claim',headers=headers('clinician')).status_code==200
    assert client.post(path+'/claim',headers=headers('reviewer-two')).status_code==409
    assert client.post(path+'/contact',headers=headers('reviewer-two')).status_code==409
