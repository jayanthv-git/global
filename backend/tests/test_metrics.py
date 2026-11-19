from backend.app.models import User
from backend.app.services.metrics import aggregate
from data.generate import cohort,seed_cohort
from .conftest import headers

def test_reproducible_generator():
    assert list(cohort())==list(cohort())
    assert list(cohort(1))!=list(cohort(2))
def test_small_groups_return_nothing(db):
    for i in range(9): db.add(User(id=f'small-{i}',cohort=True,synthetic=True,language='ar'))
    db.commit()
    assert aggregate(db,'language')['groups']==[]
    assert aggregate(db,'all')['groups']==[]
    db.add(User(id='small-9',cohort=True,synthetic=True,language='ar'));db.commit()
    groups=aggregate(db,'language')['groups']
    assert len(groups)==1 and groups[0]['participants']==10
    assert groups[0]['followup_hours'] is None
    assert groups[0]['crisis_completion'] is None

def test_seeded_metrics_all_dimensions(db):
    seed_cohort(db)
    for dimension in ['all','age_band','gender','nationality','language','geography']:
        r=aggregate(db,dimension)
        assert r['synthetic'] and r['groups']
        assert all(g['participants']>=10 for g in r['groups'])
    assert aggregate(db)['groups'][0]['participants']==120
    assert aggregate(db)['groups'][0]['followup_hours']>0
    assert aggregate(db)['groups'][0]['human_contact_minutes']>0
    assert aggregate(db,minimum=121)['groups']==[]

def test_metrics_protected(client):
    assert client.get('/api/metrics/aggregate',headers=headers()).status_code==403
    assert client.get('/api/metrics/aggregate',headers=headers('clinician')).status_code==200
