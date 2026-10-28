"""Private read-only measurement plans; deterministic fixture evaluator only in this phase."""
from pathlib import Path
from private_bank import read_bank
import json,hashlib,copy,sys
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'native'))
from studies.controlled_major_phase18 import model as m
TIMES={0:'T0',1:'T1',2:'T2',5:'T3'}

def requests(context,template,stage_index,arm=None):
 if stage_index not in range(4):raise ValueError("PRIVATE_STAGE_INDEX")
 step=list(TIMES)[stage_index]
 if step>=2 and arm not in ("E1","E2","E3","E4"):raise ValueError("PRIVATE_ARM_REQUIRED")
 m.audit_context(context,step,"COMMON" if step<2 else arm)
 scenario=json.loads((BASE/'inputs/phase17/config/scenario.json').read_text())
 intention={'instruction':'请仅返回一个有效JSON对象。','context':copy.deepcopy(context),'intention_prompt':scenario['measurement_prompt'],'risk_prompt':scenario['risk_prompt'],'ranking_prompt':'另独立报告当前四专业排序，以rank_groups从更愿意到较不愿意排列，可并列；尚不能排序则null并说明。'}
 forms=[json.loads(x) for x in read_bank().splitlines()]
 form='ABCD'[(int(template[-2:])-1+stage_index)%4]
 items=[{k:x[k] for k in ['item_id','stem','tier1_options','tier2_question','tier2_options']} for x in forms if x['form_id']==form]
 ejq={'format_instruction':'请仅返回一个有效JSON对象。','context':copy.deepcopy(context),'questions':items,'instruction':'仅根据题境回答各题两层选项，不向他人发送题目。'}
 return intention,ejq,form

def validate_measurement(x):
 if x.get('measurement_status') not in ['VALID','PARTIAL','MISSING','NOT_COMPARABLE','NOT_SCHEDULED']:raise ValueError('MEASUREMENT_STATUS')
 if set(x['scores'])!=set(m.IDS):raise ValueError('FOUR_SCORES_REQUIRED')
 for v in x['scores'].values():
  if v is not None and (type(v) not in [int,float] or not m.math.isfinite(v) or not 0<=v<=100):raise ValueError('INVALID_INTENTION_SCORE')
 if x['rank_groups'] is not None:
  groups=x['rank_groups'];flat=[i for g in groups for i in g]
  if any(not g for g in groups) or len(flat)!=4 or set(flat)!=set(m.IDS):raise ValueError('INVALID_TIED_RANKING')
 if x['risk_cs'] is not None and (type(x['risk_cs']) not in [int,float] or not m.math.isfinite(x['risk_cs']) or not 0<=x['risk_cs']<=100):raise ValueError('INVALID_RISK')
 if x['ejq'] is not None:
  q=x['ejq']
  if set(q)!= {'total','item_scores','form_id'} or len(q['item_scores'])!=8 or any(type(v)!=int or not 0<=v<=2 for v in q['item_scores']) or q['total']!=sum(q['item_scores']):raise ValueError('INVALID_EJQ')
 if not set(x['first_choices'])<=set(m.IDS):raise ValueError('INVALID_FIRST_CHOICE')
 for i in m.IDS:
  if (x['scores'][i] is None)!=(x['score_missing_reasons'][i] is not None):raise ValueError('MISSING_REASON')
 if x['measurement_status']=='VALID' and any(v is None for v in x['scores'].values()):raise ValueError('VALID_WITH_MISSING')


def build_fixture(run_dir,out):
 run_dir=Path(run_dir);data=[];roster,_,_,_=m.load(BASE,20271001);byid={x['fixed']['agent_id']:x for x in roster};ids=None;prompt_hashes=[]
 for arm in ['E1','E2','E3','E4']:
  for line in (run_dir/f'{arm}_panel_MOCK_ONLY.jsonl').read_text().splitlines():
   row=json.loads(line);t=row['step'];aid=row['agent_id']
   if t not in TIMES or (t<2 and arm!='E1'):continue
   context=row['state']['measurement_context'];before=m.digest(context);raw_before=m.digest(row)
   template=byid[aid]['fixed']['base_template_id'];intreq,ejqreq,form=requests(context,template,list(TIMES).index(t),arm if t>=2 else "COMMON")
   # Intentionally stable fixture, no intervention or SES-dependent score changes.
   ranking=byid[aid]['fixed']['base_profile']['initial_major_preferences'];scores={i:70-10*ranking.index(i) for i in m.IDS}
   rec={'run_id':run_dir.name,'scenario_id':'controlled_major_preference_v1','measurement_version':'phase18_DRAFT','model_version':'SCRIPTED_NO_VALIDITY','materials_sha256':m.digest(m.load(BASE,20271001)[2]),'materials_version':m.load(BASE,20271001)[2]['version'],'data_kind':'MOCK_ONLY','seed':json.loads((run_dir/'native_summary.json').read_text())['seed'],'agent_id':aid,'ses_group':byid[aid]['fixed']['ses_group'],'arm':'COMMON' if t<2 else arm,'step':t,'stage_id':TIMES[t],'scores':scores,'score_missing_reasons':dict.fromkeys(m.IDS,None),'measurement_status':'VALID','first_choices':[ranking[0]],'rank_groups':[[i] for i in ranking],'risk_cs':50,'risk_measurement_status':'VALID','risk_missing_reason':None,'ejq_measurement_status':'MISSING','ejq':None,'ejq_missing_reason':'NOT_EXECUTED_SCRIPTED','ejq_form':form,'explanation':'SCRIPTED_INTERFACE_ONLY','context_sha256':before,'exposure_event_id':f"{run_dir.name}/{arm}/{t}/{aid}",'intention_prompt_sha256':m.digest({k:v for k,v in intreq.items() if k!='context'}),'ejq_questions_sha256':m.digest(ejqreq['questions']),'public_received':any(c['item_id'] in {v['item_id'] for v in m.load(BASE,20271001)[2]['P1']} for c in context['visible_feed']+context['visible_history']),'feedback_received':any(c['item_id'].startswith('M-') for c in context['visible_feed']+context['visible_history'])}
   validate_measurement(rec);data.append(rec);prompt_hashes.append(rec['intention_prompt_sha256'])
   assert before==m.digest(context) and raw_before==m.digest(row)
   assert 'answer_key' not in m.canonical(ejqreq) and 'ses_group' not in m.canonical(intreq)
 initial_roster=run_dir/'native_study/population/roster.jsonl'
 if not initial_roster.exists():raise ValueError('PRESPECIFIED_INITIAL_ROSTER_REQUIRED')
 ids=[json.loads(line)['agent_id'] for line in initial_roster.read_text().splitlines()]
 if len(set(ids))!=len(ids) or not ids or not set(ids)<=set(byid):raise ValueError('INVALID_INITIAL_ROSTER')
 if any(x['agent_id'] not in ids for x in data):raise ValueError('UNEXPECTED_MEASUREMENT_AGENT')
 result={'status':'SOFTWARE_TEST_ONLY','data_kind':'MOCK_ONLY','expected_agent_ids':ids,'expected_roster':[{'agent_id':aid,'ses_group':byid[aid]['fixed']['ses_group']} for aid in ids],'seeds':sorted({x['seed'] for x in data}),'measurement_prompt_equal':len(set(prompt_hashes))==1,'records':data}
 Path(out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--run-dir',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
 if a.out.exists():raise FileExistsError('choose a fresh sidecar output')
 x=build_fixture(a.run_dir,a.out);print(json.dumps({'records':len(x['records']),'status':x['status']}))
