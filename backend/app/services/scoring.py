from ..settings import config
DEFINITIONS = config('instruments/definitions.yaml')
def score(instrument, responses):
    if instrument not in DEFINITIONS['instruments']:
        raise ValueError('Unknown instrument')
    definition = DEFINITIONS['instruments'][instrument]
    if len(responses) != definition['items'] or any(type(x) is not int or x < 0 or x > definition['max_response'] for x in responses):
        raise ValueError('Every item must have an integer response in the allowed range')
    total = sum(responses)
    if instrument == 'WHO-5':
        value = total * 4
        band = 'low_wellbeing' if total < 13 else 'higher_wellbeing'
    else:
        value = total
        cutoffs = [(5, 'minimal'), (10, 'mild'), (15, 'moderate')]
        if instrument == 'PHQ-9':
            cutoffs.append((20, 'moderately_severe'))
        band = next((band for upper, band in cutoffs if total < upper), 'severe')
    return {'score': value, 'band': band, 'instrument': instrument,
            'instrument_version': DEFINITIONS['version'], 'placeholder': True,
            'explanation_key': 'result_explanation', 'not_diagnosis': True}
