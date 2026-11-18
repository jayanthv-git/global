from backend.app.services.pathways import options

def test_preferences_and_version(db):
    result=options(db,'moderate','ar','free','routine',True,'in_person')
    assert result['rule_version']=='demo-1.0'
    assert [p['id'] for p in result['options'] if p['eligible']]==['primary']
def test_no_match_is_honest(db):
    result=options(db,'severe','ar','free','routine',False,'online')
    assert not any(p['eligible'] for p in result['options'])
