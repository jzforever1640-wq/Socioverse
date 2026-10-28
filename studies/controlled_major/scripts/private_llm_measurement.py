"""Private evaluator implementation; fake-channel tests only, no live calls this phase."""
import copy,json
from measurement_sidecar import requests,validate_measurement,BASE

def evaluate(context,template,stage_index,channel,metadata):
 original=copy.deepcopy(context);ir,er,form=requests(context,template,stage_index,metadata.get("arm"))
 ir['response_format']={'scores':{'CS':'0..100','AUTO':'0..100','EE':'0..100','STAT':'0..100'},'first_choices':['major IDs or empty if undecided'],'rank_groups':[['ranked major IDs; ties share a group']],'risk_cs':'0..100 or null','explanation':'简短个人说明，最多400字符'}
 def check_intention(x):
  if set(x)!={'scores','first_choices','rank_groups','risk_cs','explanation'}:raise ValueError('measurement response fields')
  if not isinstance(x['explanation'],str) or len(x['explanation'])>400:raise ValueError('explanation format')
  if not isinstance(x['first_choices'],list) or len(x['first_choices'])!=len(set(x['first_choices'])):raise ValueError('first choice format')
  validate_measurement({**x,'score_missing_reasons':{i:'NOT_PROVIDED' if v is None else None for i,v in x['scores'].items()},'measurement_status':'PARTIAL' if any(v is None for v in x['scores'].values()) else 'VALID','ejq':None})
 intention=channel.invoke(ir,{**metadata,'purpose':'private_intention_risk_ranking'},check_intention)
 er['response_format']={'answers':[{'item_id':'question ID','tier1':'A or B','tier2':'A or B'}]}
 expected={x['item_id'] for x in er['questions']}
 def check_ejq(x):
  if set(x)!={'answers'} or len(x['answers'])!=8 or {a['item_id'] for a in x['answers']}!=expected:raise ValueError('EJQ coverage')
  from ejq_alignment import score_answers
  score_answers(form,x['answers'])
 answers=channel.invoke(er,{**metadata,'purpose':'private_EJQ'},check_ejq)
 # Same official keys/points, stable original-bank order; no answer key in request.
 from ejq_alignment import score_answers
 scored=score_answers(form,answers['answers'])
 item_scores=scored['item_scores']
 assert context==original
 return {**intention,'risk_measurement_status':'VALID' if intention['risk_cs'] is not None else 'MISSING','risk_missing_reason':None if intention['risk_cs'] is not None else 'NOT_PROVIDED','ejq_measurement_status':'VALID','ejq_missing_reason':None,'ejq':{'form_id':form,'item_scores':item_scores,'total':sum(item_scores)},'measurement_source':'LLM_PILOT_UNVALIDATED'}
