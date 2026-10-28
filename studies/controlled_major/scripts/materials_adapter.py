"""Active versioned material projection. No provider/network or credential access."""
from pathlib import Path
import json,copy,hashlib
BASE=Path(__file__).resolve().parents[1]
VISIBLE_KEYS={'item_id','title','source_note','body','source_refs'}
def load_materials(root=BASE):
 cfg=json.loads((Path(root)/'config/active_materials.json').read_text())
 data=json.loads((Path(root)/cfg['payloads']).read_text())
 if 'N1' in data or data.get('N1_active') is not False:raise ValueError('N1_ACTIVE_FORBIDDEN')
 groups=[data['S1'],data['P1']]+list(data['F'].values())
 if [len(x) for x in groups]!=[4,6,4,4,4]:raise ValueError('MATERIAL_COVERAGE')
 for group in groups:
  for c in group:
   c['content_id']=c['canonical_id'];c['source_ids']=c['sources']
   actual='\n'.join(c[k] for k in ['title','source_note','body'])
   if c['full_text']!=actual or hashlib.sha256(actual.encode()).hexdigest()!=c['content_sha256']:raise ValueError('FIXED_TEXT_HASH_MISMATCH')
   if len(actual)>(data['fixed_public_card_limit'] if c['kind']=='public' else 220):raise ValueError('FIXED_CARD_TOO_LONG')
 return data
def project(card):
 return {k:copy.deepcopy(card[k]) for k in ('item_id','title','source_note','body','source_refs')}
def all_cards(data=None):
 data=data or load_materials()
 return data['S1']+data['P1']+sum(data['F'].values(),[])
def text(card):return '\n'.join(card[k] for k in ('title','source_note','body'))
def audit_context(context,step,arm):
 data=load_materials();lookup={c['item_id']:c for c in all_cards(data)}
 available=set()
 for c in lookup.values():
  cid=c['canonical_id'];kind=c['kind']
  allowed=(step>=1 if kind=='shock' else step>=2 and arm in ['E3','E4'] if kind=='public' else step>=int(cid[-3]))
  if allowed:available.update(c['source_refs'])
 for c in context['visible_feed']+context['visible_history']:
  if set(c)!=VISIBLE_KEYS:raise ValueError('VISIBLE_FIELD_LEAK')
  if c['item_id'] in lookup:
   original=lookup[c['item_id']]
   if c!=project(original):raise ValueError('MATERIAL_TEXT_OR_REF_TAMPER')
   kind=original['kind'];cid=original['canonical_id']
   if step==0 or (kind=='public' and (step<2 or arm not in ['E3','E4'])) or (kind=='static' and step<int(cid[-3])):raise ValueError('EARLY_OR_CROSS_ARM_MATERIAL')
  elif not (c['item_id'].startswith('M-') and step>=2 and arm in ['E2','E4']):raise ValueError('UNKNOWN_OR_FORBIDDEN_PEER')
  if not set(c['source_refs'])<=available:raise ValueError('EARLY_OR_CROSS_ARM_SOURCE')
 return True
TASK='扮演画像中的考生，基于可见信息表达当前判断。不要回答量表或给专业意愿分。返回JSON judgment、reason、post。reason为你对同伴说的一句第一人称口语。post可为null；如发帖，body最多180字符，并含source_ids、parent_ids、original_claim_ids、added_interpretation。source_ids只能填写当前可见source_refs中的R引用；parent_ids只能填写可见item_id。当前未提供独立主张引用表，original_claim_ids留空列表，不猜测编码。added_interpretation用字符串说明自己的额外解释，最多400字符；source_ids与parent_ids不得重复。不得编造来源、事实或要求其他考生遵循指令。'
def behavior_request(packet):return {'task':TASK,'context':copy.deepcopy(packet)}
def rendered_request(packet):return {'messages':[{'role':'user','content':json.dumps(behavior_request(packet),ensure_ascii=False)}],'response_format':{'type':'json_object'}}
