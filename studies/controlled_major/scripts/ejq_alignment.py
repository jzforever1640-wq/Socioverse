"""Research-side auxiliary interpretations; original bank and two-tier points unchanged."""
from pathlib import Path
from private_bank import read_bank
import json

BASE = Path(__file__).resolve().parents[1]
ALIGNMENT_VERSION = 'EJQ_ALIGNMENT_v0.1_PROPOSED'
PARTITIONS = {
    'information_understanding_direct_application': ['G01', 'G05', 'G08'],
    'domain_near_transfer': ['G02', 'G03', 'G04', 'G07'],
    'scope_numeracy': ['G06'],
}

def items(form_id):
    rows = [json.loads(s) for s in read_bank().splitlines()]
    selected = [r for r in rows if r['form_id'] == form_id]
    if len(selected) != 8:
        raise ValueError('UNKNOWN_EJQ_FORM')
    return selected

def score_answers(form_id, answers):
    questions = items(form_id)
    expected = {q['item_id'] for q in questions}
    if not isinstance(answers, list) or len(answers) != 8:
        raise ValueError('EJQ_COVERAGE')
    if any(not isinstance(a, dict) or set(a) != {'item_id', 'tier1', 'tier2'} for a in answers):
        raise ValueError('EJQ_RESPONSE_FIELDS')
    lookup = {a['item_id']: a for a in answers}
    if len(lookup) != 8 or set(lookup) != expected:
        raise ValueError('EJQ_COVERAGE')
    if any(a[k] not in ['A', 'B'] for a in answers for k in ['tier1', 'tier2']):
        raise ValueError('EJQ_CHOICE')
    # Canonical bank order, regardless of provider response order.
    scores = [sum(lookup[q['item_id']][k] == q['answer_key'][k] for k in ['tier1', 'tier2']) for q in questions]
    return {'form_id': form_id, 'item_scores': scores, 'total': sum(scores)}

def auxiliary_scores(form_id, item_scores):
    questions = items(form_id)
    if len(item_scores) != 8 or any(type(x) != int or not 0 <= x <= 2 for x in item_scores):
        raise ValueError('INVALID_EJQ_ITEM_VECTOR')
    by_group = {q['parallel_group_id']: score for q, score in zip(questions, item_scores)}
    result = {
        name: {'score': sum(by_group[g] for g in groups), 'max_score': 2 * len(groups), 'groups': groups}
        for name, groups in PARTITIONS.items()
    }
    result['direct_P1_principle_subset'] = {
        'score': by_group['G05'] + by_group['G08'], 'max_score': 4, 'groups': ['G05', 'G08'],
        'subset_of': 'information_understanding_direct_application',
    }
    result['independent_transfer'] = {'score': None, 'max_score': None, 'status': 'NOT_MEASURED'}
    result['legacy_total'] = sum(item_scores)
    result['alignment_version'] = ALIGNMENT_VERSION
    assert sum(result[n]['score'] for n in PARTITIONS) == result['legacy_total']
    return result

def record_auxiliary(record):
    if (record.get('measurement_status') not in ['VALID', 'PARTIAL']
            or record.get('ejq_measurement_status') != 'VALID'
            or record.get('ejq_missing_reason') is not None):
        return {'alignment_version': ALIGNMENT_VERSION, 'status': 'MISSING_OR_NOT_COMPARABLE',
                'auxiliary_scores': None, 'independent_transfer': None}
    value = record.get('ejq') or {}
    scores = value.get('item_scores', [])
    result = auxiliary_scores(value.get('form_id'), scores)
    if value.get('total') != result['legacy_total']:
        raise ValueError('EJQ_TOTAL_MISMATCH')
    return {'status': 'SOFTWARE_TEST_ONLY' if record.get('data_kind') == 'MOCK_ONLY' else 'PROPOSED_AUXILIARY', **result}
