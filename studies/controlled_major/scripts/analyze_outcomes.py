"""Prespecified paired contrasts, descriptive only; reject mock unless explicit fixture mode."""
from pathlib import Path
import json,math,sys
from collections import defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parent))
from measurement_sidecar import validate_measurement
IDS=['CS','AUTO','EE','STAT']
CONTRASTS={'PRIMARY_E3_E1':{'E3':1,'E1':-1},'SECONDARY_E4_E2':{'E4':1,'E2':-1},'FEEDBACK_E2_E1':{'E2':1,'E1':-1},'INTERACTION':{'E4':1,'E2':-1,'E3':-1,'E1':1}}

def analyze(bundle,fixture=False,expected_roster=None):
 if bundle.get('data_kind')=='MOCK_ONLY' and not fixture:raise ValueError('MOCK_DATA_REJECTED: --fixture only writes SOFTWARE_TEST_ONLY output')
 rows=bundle['records'];expected=bundle['expected_agent_ids'];seeds=bundle['seeds'];lookup={}
 roster=expected_roster if expected_roster is not None else bundle.get('expected_roster')
 if not isinstance(roster,list) or not roster:raise ValueError('EXPECTED_ROSTER_REQUIRED: never infer denominators from observed outcomes')
 if any(not isinstance(x,dict) or not {'agent_id','ses_group'}<=set(x) for x in roster):raise ValueError('INVALID_EXPECTED_ROSTER')
 ses={x['agent_id']:x['ses_group'] for x in roster}
 if len(ses)!=len(roster) or set(ses)!=set(expected) or any(v not in ['lower','middle','higher'] for v in ses.values()):raise ValueError('ROSTER_ID_OR_SES_MISMATCH')
 if not expected or len(set(expected))!=len(expected) or not seeds or len(set(seeds))!=len(seeds):raise ValueError('EMPTY_OR_DUPLICATE_POPULATION')
 for x in rows:
  validate_measurement(x)
  if x['agent_id'] not in expected or x['seed'] not in seeds:raise ValueError('UNEXPECTED_PANEL_ID')
  if x['data_kind']!=bundle['data_kind']:raise ValueError('MIXED_DATA_KIND')
  if x['step']!={'T0':0,'T1':1,'T2':2,'T3':5}[x['stage_id']] or (x['arm']=='COMMON')!=(x['stage_id'] in ['T0','T1']):raise ValueError('STAGE_ARM_MISMATCH')
  key=(x['seed'],x['agent_id'],x['arm'],x['stage_id'])
  if key in lookup:raise ValueError('DUPLICATE_MEASUREMENT')
  lookup[key]=x
  if x['agent_id'] in ses and ses[x['agent_id']]!=x['ses_group']:raise ValueError('SES_ID_DRIFT')
 if rows and len({(x['scenario_id'],x['measurement_version'],x['intention_prompt_sha256'],x['model_version'],x['materials_sha256']) for x in rows})!=1:raise ValueError('NOT_COMPARABLE_INSTRUMENT')
 def score(seed,aid,arm,stage,major):
  x=lookup.get((seed,aid,arm,stage))
  if x is None or x['measurement_status'] not in ['VALID','PARTIAL']:return None
  value=x['scores'][major]
  if x.get('score_missing_reasons',{}).get(major) is not None:return None
  return value
 contrasts=[]
 for seed in seeds:
  for label,coef in CONTRASTS.items():
   for stage in ['T2','T3']:
    for group in ['ALL','lower','middle','higher']:
     members=[aid for aid in expected if group=='ALL' or ses.get(aid)==group]
     if not members:continue
     values=[];lo=hi=0;missing=0
     for aid in members:
      terms=[(c,score(seed,aid,arm,stage,'CS')) for arm,c in coef.items()]
      if all(v is not None for c,v in terms):values.append(sum(c*v for c,v in terms))
      else:missing+=1
      lo+=sum(c*v if v is not None else min(0,c*100) for c,v in terms)
      hi+=sum(c*v if v is not None else max(0,c*100) for c,v in terms)
     contrasts.append({'seed':seed,'contrast':label,'stage':stage,'ses':group,'outcome_role':('PRIMARY' if label=='PRIMARY_E3_E1' and stage=='T3' and group=='ALL' else ('KEY_SECONDARY' if label=='SECONDARY_E4_E2' and stage=='T3' and group=='ALL' else 'EXPLORATORY')),'expected_n':len(members),'complete_pair_n':len(values),'missing_pair_n':missing,'complete_pair_mean':sum(values)/len(values) if values else None,'prespecified_denominator_bound':[lo/len(members),hi/len(members)],'interpretation':'SOFTWARE_TEST_ONLY' if fixture else 'DESCRIPTIVE_PAIRED_SIMULATION_CONTRAST'})
 changes=[]
 for seed in seeds:
  for aid in expected:
   for arm in ['COMMON','E1','E2','E3','E4']:
    times=[('T0','T1')] if arm=='COMMON' else [('T1','T2'),('T1','T3'),('T2','T3')]
    for start,end in times:
     sourcearm='COMMON' if start in ['T0','T1'] else arm
     a=lookup.get((seed,aid,sourcearm,start));b=lookup.get((seed,aid,arm,end))
     changes.append({'seed':seed,'agent_id':aid,'arm':arm,'from':start,'to':end,'vector':{i:(score(seed,aid,arm,end,i)-score(seed,aid,sourcearm,start,i)) if score(seed,aid,arm,end,i) is not None and score(seed,aid,sourcearm,start,i) is not None else None for i in IDS},'first_choice_changed':set(a['first_choices'])!=set(b['first_choices']) if a and b and a['measurement_status'] in ['VALID','PARTIAL'] and b['measurement_status'] in ['VALID','PARTIAL'] and a['first_choices'] and b['first_choices'] else None,'cs_relative_gap_change':gap(b)-gap(a) if a and b and gap(a) is not None and gap(b) is not None else None,'risk_change':metric_delta(a,b,'risk'),'ejq_change':metric_delta(a,b,'ejq'),'risk_change_status':delta_status(a,b,'risk'),'ejq_change_status':delta_status(a,b,'ejq'),'cs_rank_change':rank(b)-rank(a) if a and b and rank(a) is not None and rank(b) is not None else None})
 metric_levels=[]
 for seed in seeds:
  for arm in ['COMMON','E1','E2','E3','E4']:
   for stage in (['T0','T1'] if arm=='COMMON' else ['T2','T3']):
    for metric in ['risk','ejq']:
     vals=[metric_value(lookup.get((seed,aid,arm,stage)),metric) for aid in expected]
     good=[v for v in vals if v is not None]
     metric_levels.append({'seed':seed,'arm':arm,'stage':stage,'metric':metric,'expected_n':len(expected),'valid_n':len(good),'missing_n':len(expected)-len(good),'mean':sum(good)/len(good) if good else None})
 aggregates=[]
 for label in CONTRASTS:
  vals=[x['complete_pair_mean'] for x in contrasts if x['contrast']==label and x['stage']=='T3' and x['ses']=='ALL' and x['complete_pair_mean'] is not None]
  aggregates.append({'contrast':label,'independent_repeat_unit':'whole fixed-population network/run trajectory','available_seeds':len(vals),'mean':sum(vals)/len(vals) if vals else None,'range':[min(vals),max(vals)] if vals else None,'no_significance_tests':True})
 return {'status':'SOFTWARE_TEST_ONLY' if fixture else 'DESCRIPTIVE_ANALYSIS_NOT_VALIDITY_CLAIM','primary':'E3-E1 CS at T3(t5), additional P1 support vs no additional support under identical static social information; shared T1 baseline cancels','estimand_components_not_separable':['reading_quantity','text_length','source_authority','cognitive_activity'],'interaction_not_causal_mediation':True,'contrasts':contrasts,'metric_levels':metric_levels,'changes':changes,'across_seed_descriptive':aggregates,'denominator_source':'EXPLICIT_PRESPECIFIED_ROSTER','metric_gate':'overall VALID/PARTIAL plus metric-specific VALID required; legacy absent status excluded','warnings':['Missing shared baseline prevents a within-arm change but not an observed paired endpoint contrast; common baseline cancels exactly.','NOT_SCHEDULED t3/t4 outcomes are not manufactured.','No agent-level independent tests, no SES causal inference, no preference direction success criterion.']}

def metric_value(x,metric):
 if x is None or x.get('measurement_status') not in ['VALID','PARTIAL']:return None
 if x.get(metric+'_measurement_status')!='VALID':return None
 if x.get(metric+'_missing_reason') is not None:return None
 value=x.get('risk_cs') if metric=='risk' else (x.get('ejq') or {}).get('total')
 if type(value) not in [int,float] or not math.isfinite(value) or not 0<=value<=(100 if metric=='risk' else 16):return None
 return value

def metric_delta(a,b,metric):
 va=metric_value(a,metric);vb=metric_value(b,metric)
 return vb-va if va is not None and vb is not None else None

def delta_status(a,b,metric):
 return 'VALID' if metric_value(a,metric) is not None and metric_value(b,metric) is not None else 'MISSING_OR_NOT_COMPARABLE'

def gap(x):
 if x['measurement_status'] not in ['VALID','PARTIAL']:return None
 s=x['scores'];return s['CS']-sum(s[i] for i in IDS[1:])/3 if all(v is not None for v in s.values()) else None

def rank(x):
 if x['measurement_status'] not in ['VALID','PARTIAL'] or x['rank_groups'] is None:return None
 start=1
 for group in x['rank_groups']:
  if 'CS' in group:return start+(len(group)-1)/2
  start+=len(group)

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--fixture',action='store_true');ap.add_argument('--roster',type=Path,help='explicit prespecified list of agent_id/ses_group for legacy bundles');a=ap.parse_args()
 if a.out.exists():raise FileExistsError('choose fresh output')
 result=analyze(json.loads(a.input.read_text()),a.fixture,json.loads(a.roster.read_text()) if a.roster else None);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(result['status'])
