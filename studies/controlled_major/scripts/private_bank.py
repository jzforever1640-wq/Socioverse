"""Repository-authorized instrument loader; hash-checked, never provides fallback content."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3]
def read_bank():
    path=Path(os.environ.get('SV2_EJQ_BANK', ROOT/'studies/controlled_major/inputs/EJQ_forms_PRIVATE_DRAFT.jsonl'))
    expected=next(x['sha256'] for x in json.loads((ROOT/'shared/EXTERNAL_ARTIFACTS.json').read_text()) if x['artifact_id']=='private/EJQ_bank')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError('PRIVATE_BANK_HASH_MISMATCH_REQUIRES_RESEARCH_REVIEW')
    return raw.decode('utf-8')
