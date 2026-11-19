from .conftest import headers

def test_complete_non_crisis_loop_with_revocation(client):
    h=headers()
    first=client.post('/api/assessments',headers=h,json={'instrument':'PHQ-9','responses':[2,2,2,1,1,1,1,0,0]}).json()
    assert first['score']==10 and first['band']=='moderate' and first['crisis'] is None
    navigation=client.get('/api/navigation/options?cost=free&language=ar&physical=true&channel=in_person',headers=h).json()
    assert [x['id'] for x in navigation['options'] if x['eligible']]==['primary']
    referral=client.post('/api/referrals',headers=h,json={'provider_id':'primary','physical_context':'Synthetic physical-health context'}).json()
    summary='/api/providers/referrals/'+referral['id']+'/summary'
    assert client.get(summary,headers=headers('provider')).status_code==403
    consent=client.post('/api/consents',headers=h,json={'grantee':'primary','scope':['scores','physical_context','followups']}).json()
    for state in ['accepted','booked','attended']:
        assert client.patch('/api/referrals/'+referral['id'],headers=h,json={'status':state}).status_code==200
    client.post('/api/followups',headers=h,json={'referral_id':referral['id'],'seen':True,'note':'Synthetic appointment attended'})
    shared=client.get(summary,headers=headers('provider')).json()
    assert shared['scores'][0]['score']==10 and shared['followups'][0]['seen']
    assert shared['physical_context']=='Synthetic physical-health context'
    client.delete('/api/consents/'+consent['id'],headers=h)
    assert client.get(summary,headers=headers('provider')).status_code==403
    client.post('/api/assessments',headers=h,json={'instrument':'PHQ-9','responses':[1,1,1,0,0,0,0,0,0]})
    trend=client.get('/api/assessments/trend',headers=h).json()
    assert trend['points'][-1]['delta']==-7 and trend['points'][-1]['change_flag']
    assert trend['threshold_status']=='UNVERIFIED'
    actions={x['action'] for x in client.get('/api/audit',headers=h).json()}
    assert {'consent.granted','consent.revoked','read.allowed','read.denied','followup.created','referral.attended'}.issubset(actions)
