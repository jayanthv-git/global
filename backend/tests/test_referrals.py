from .conftest import headers

def test_handoff_and_live_revoke(client):
    r=client.post('/api/referrals',headers=headers(),json={'provider_id':'primary','physical_context':'demo context'}).json()
    path='/api/providers/referrals/'+r['id']+'/summary'
    assert client.get(path,headers=headers('provider')).status_code==403
    c=client.post('/api/consents',headers=headers(),json={'grantee':'primary','scope':['scores','physical_context','followups']}).json()
    result=client.get(path,headers=headers('provider'))
    assert result.status_code==200 and result.json()['physical_context']=='demo context'
    client.delete('/api/consents/'+c['id'],headers=headers())
    assert client.get(path,headers=headers('provider')).status_code==403
    assert client.get(path,headers=headers('bob')).status_code==404

def test_status_state_machine_and_isolation(client):
    r=client.post('/api/referrals',headers=headers(),json={'provider_id':'primary'}).json()
    path='/api/referrals/'+r['id']
    assert client.patch(path,headers=headers(),json={'status':'attended'}).status_code==409
    assert client.patch(path,headers=headers('bob'),json={'status':'accepted'}).status_code==404
    for state in ['accepted','booked','attended']:
        result=client.patch(path,headers=headers(),json={'status':state})
        assert result.status_code==200 and result.json()[state+'_at']

def test_different_provider_cannot_use_another_grant(client):
    r=client.post('/api/referrals',headers=headers(),json={'provider_id':'primary'}).json()
    client.post('/api/consents',headers=headers(),json={'grantee':'primary','scope':['scores']})
    tele=client.post('/api/demo/session',json={'persona':'provider','provider_id':'tele'}).json()
    path='/api/providers/referrals/'+r['id']+'/summary?scopes=scores'
    assert client.get(path,headers={'Authorization':'Bearer '+tele['token']}).status_code==404
