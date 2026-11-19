from datetime import datetime,timedelta,timezone
from backend.app.models import Assessment
from backend.app.services.crypto import encrypt
from .conftest import headers

def test_database_normalizes_offsets_and_api_returns_utc(client,db):
    timestamp=datetime(2026,11,1,12,0,tzinfo=timezone(timedelta(hours=4)))
    row=Assessment(user_id='alice',instrument='PHQ-9',responses_encrypted=encrypt({'answers':[0]*9}),score=0,band='minimal',created_at=timestamp)
    db.add(row);db.commit();db.expire_all()
    assert db.get(Assessment,row.id).created_at==datetime(2026,11,1,8,tzinfo=timezone.utc)
    value=client.get('/api/assessments/trend',headers=headers()).json()['points'][0]['created_at']
    assert value.endswith('Z') or value.endswith('+00:00')
