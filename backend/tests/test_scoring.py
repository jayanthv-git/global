import pytest
from backend.app.services.scoring import score

def responses(total, count, maximum):
    return [min(maximum, max(0, total - i * maximum)) for i in range(count)]
@pytest.mark.parametrize('total,band', [(0,'minimal'),(4,'minimal'),(5,'mild'),(9,'mild'),(10,'moderate'),(14,'moderate'),(15,'moderately_severe'),(19,'moderately_severe'),(20,'severe'),(27,'severe')])
def test_phq_boundaries(total,band):
    result=score('PHQ-9',responses(total,9,3))
    assert (result['score'],result['band']) == (total,band)
@pytest.mark.parametrize('total,band',[(0,'minimal'),(4,'minimal'),(5,'mild'),(9,'mild'),(10,'moderate'),(14,'moderate'),(15,'severe'),(21,'severe')])
def test_gad_boundaries(total,band):
    assert score('GAD-7',responses(total,7,3))['band']==band
@pytest.mark.parametrize('raw,band',[(0,'low_wellbeing'),(12,'low_wellbeing'),(13,'higher_wellbeing'),(25,'higher_wellbeing')])
def test_who_boundaries(raw,band):
    result=score('WHO-5',responses(raw,5,5))
    assert (result['score'],result['band'])==(raw*4,band)
@pytest.mark.parametrize('instrument,answers',[('other',[]),('PHQ-9',[0]*8),('GAD-7',[4]*7),('WHO-5',[-1]*5),('PHQ-9',[True]*9),('GAD-7',[1.0]*7)])
def test_invalid(instrument,answers):
    with pytest.raises(ValueError): score(instrument,answers)
