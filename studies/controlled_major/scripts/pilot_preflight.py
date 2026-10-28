"""Budget arithmetic and fail-closed approval gate. Does not call a model."""
from pathlib import Path
import json,math
BASE=Path(__file__).resolve().parents[1]

def counts(n=6,arms=2,ejq=True):
 # Active behavior calls t1..4 parent, t2..4 each child. t0 and t5 no behavior calls.
 behavior=n*(4+3*(arms-1));measurement=n*(2+2*arms)
 return {'agents':n,'arms':arms,'behavior_calls':behavior,'intention_risk_ranking_calls':measurement,'ejq_calls':measurement if ejq else 0,'total_calls':behavior+measurement*(2 if ejq else 1)}

def budget(c,pi,po,retry_fraction=.10):
 calls=c['total_calls'];max_calls=calls+math.ceil(calls*retry_fraction)
 return {'base_calls':calls,'max_calls_with_10pct_retry_reserve':max_calls,'assumed_max_input_tokens':max_calls*4000,'assumed_max_output_tokens':max_calls*1000,'input_usd_per_million_assumption':pi,'output_usd_per_million_assumption':po,'worst_case_usd':max_calls*(4000*pi+1000*po)/1e6,'not_current_model_price':True}

def preflight(config):
 missing=[]
 for key in ['paid_authorized','real_llm_enabled']:
  if config.get(key) is not True:missing.append(key)
 for key in ['model','provider','price_input_per_million','price_output_per_million','human_protocol_approval','human_material_approval','human_measurement_approval','exact_model_version','max_total_budget_usd','usage_ledger_path','token_counter_verified']:
  if config.get(key) is None or config.get(key) is False:missing.append(key)
 return {'status':'NO_GO' if missing else 'REVIEW_GATE_FIELDS_PRESENT_NOT_A_RUN_AUTHORIZATION','missing':missing,'paid_calls':0}

if __name__=='__main__':
 cfg=json.loads((BASE/'config/pilot_DRAFT.json').read_text());a=counts(6,2);b=counts(6,4)
 result={'status':'BUDGET_SCENARIOS_NOT_A_QUOTE','stage_A':a,'stage_A_scenarios':[budget(a,pi,po) for pi,po in [(1,4),(2,8),(5,20)]],'stage_B_incremental_calls':b['total_calls']-a['total_calls'],'complete_4arm':b,'complete_4arm_scenarios':[budget(b,pi,po) for pi,po in [(1,4),(2,8),(5,20)]],'independent_no_shock_incremental_calls':6*(4+2*4),'gate':preflight(cfg),'price_requirement':'select provider/model then verify official price; no model is selected by this file','max_budget_usd_proposal':5,'no_shock_reference':'not included in minimum support pilot; new cold version from t0, cannot fork from shock t1'}
 print(json.dumps(result,ensure_ascii=False,indent=2))
