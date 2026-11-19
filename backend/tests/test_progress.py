from .conftest import headers

def test_trend_same_instrument_and_change(client):
    for answers in ([2]*8+[0],[1]*8+[0]):
        assert client.post('/api/assessments',headers=headers(),json={'instrument':'PHQ-9','responses':answers}).status_code==201
    client.post('/api/assessments',headers=headers(),json={'instrument':'WHO-5','responses':[3]*5})
    r=client.get('/api/assessments/trend?instrument=PHQ-9',headers=headers()).json()
    assert len(r['points'])==2
    assert r['points'][1]['delta']==-8 and r['points'][1]['change_flag']
    assert r['threshold_status']=='UNVERIFIED'
    assert client.get('/api/assessments/trend',headers=headers('bob')).json()['points']==[]

def test_followup_handoff_history_consent_and_crisis(client):
    r=client.post('/api/referrals',headers=headers(),json={'provider_id':'primary'}).json()
    body={'referral_id':r['id'],'seen':False,'note':'synthetic follow-up'}
    assert client.post('/api/followups',headers=headers('bob'),json=body).status_code==404
    assert client.post('/api/followups',headers=headers(),json=body).status_code==201
    h=client.get('/api/followups?referral_id='+r['id'],headers=headers()).json()
    assert h['items'][0]['note']=='synthetic follow-up' and h['due_at']
    path='/api/providers/referrals/'+r['id']+'/summary?scopes=followups'
    assert client.get(path,headers=headers('provider')).status_code==403
    client.post('/api/consents',headers=headers(),json={'grantee':'primary','scope':['followups']})
    assert client.get(path,headers=headers('provider')).json()['followups'][0]['note']=='synthetic follow-up'
    body['note']='I might hurt myself'
    assert client.post('/api/followups',headers=headers(),json=body).json()['escalation_id']
