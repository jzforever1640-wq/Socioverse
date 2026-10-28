"""Use official registry/builder/store/branch helper. No custom simulation engine."""
from pathlib import Path
import argparse,copy,json,hashlib,sys,shutil
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'native'))
from studies.controlled_major_phase18 import model as m
from socioverse.engine import build_simulator,materialize_initial
from socioverse.schemas import EnvironmentBundle,PopulationBundle,SimulationConfig,WarmStartSpec
from socioverse.io.duckdb_store import open_readonly
from skills.sv_workspace import scaffold,save_study_yaml,write_roster,init_manifest,create_branch,check_branch_invariant,resolve_warm_start

def dump(path,x):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def jsonl(path,x):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(''.join(json.dumps(v,ensure_ascii=False)+'\n' for v in x))
def get_panel(path):
 con=open_readonly(path)
 try:raw=con.execute('select agent_id,step,state,action_kind,action_payload,action_source from panel order by step,agent_id').fetchall()
 finally:con.close()
 return [{'agent_id':a,'step':t,'state':json.loads(s),'action_kind':k,'action_payload':json.loads(p),'action_source':src} for a,t,s,k,p,src in raw]

def run(seed,out,selected=None):
 if out.exists():raise FileExistsError('RUN_DIRECTORY_EXISTS: choose fresh --out; never overwrite prior results')
 workspace=scaffold(out,'native_study');study,e,p,s=m.make_bundles(seed,BASE,selected)
 save_study_yaml(workspace/'study.yaml',study)
 dump(workspace/'environment/environment.json',e.model_dump(mode='json'));dump(workspace/'population/population.json',p.model_dump(mode='json'));dump(workspace/'simulation/simulation.json',s.model_dump(mode='json'))
 shutil.copy2(Path(m.__file__),workspace/'model.py');dump(workspace/'resources.json',{'external_services':[],'data_kind':'MOCK_ONLY'})
 dump(workspace/'grounding/grounding.json',{'method_notes':'stylized offline integration only','assumptions':['Phase17 hypothetical common conditions','fixed population and original network','S1 once at t1; F round-specific fallback; no additional materials for E1/E2; P1 t2 E3/E4'],'facts_ref':str(BASE/json.loads((BASE/'config/active_materials.json').read_text())['source_ledger'])})
 _,rows=materialize_initial(e,p,seed);write_roster(workspace/'population/roster.jsonl',rows);init_manifest(workspace)
 panels={};snapshots={};reports=[];call_counts={};real_requests=0
 for arm in ['E1','E2','E3','E4']:
  if arm!='E1':
   version=create_branch(workspace,f'{arm} scripted integration only; no effect inference',fork_step=2,source='v1')
   e=EnvironmentBundle.model_validate_json((workspace/'environment/environment.json').read_text());e.scheduled_events.extend(m.intervention_events(arm));dump(workspace/'environment/environment.json',e.model_dump(mode='json'))
   report=check_branch_invariant(workspace,downgrade=False)
   if not report['ok'] or report.get('error') or report['kind']!='branch':raise RuntimeError('BRANCH_FAIL_CLOSED '+str(report))
   warm=resolve_warm_start(workspace)
   if not warm:raise RuntimeError('MISSING_PARENT_REPLAY')
   p=PopulationBundle.model_validate_json((workspace/'population/population.json').read_text());s=SimulationConfig.model_validate_json((workspace/'simulation/simulation.json').read_text());s.warm_start=WarmStartSpec(**warm);dump(workspace/'simulation/simulation.json',s.model_dump(mode='json'));reports.append({'arm':arm,'version':version,**report})
  sim=build_simulator(env_bundle=e,pop_bundle=p,sim_config=s,store_path=workspace/'trajectory/study.duckdb')
  def record_messages(t,metrics):
   # Core doesn't automatically connect Environment MessageBus to store.messages.
   # Use its public store method; source/parent IDs retained in richer separate JSONL.
   if t in [1,2,3,4]:sim.store.record_messages(sim.env.new_messages)
  sim.on_step=record_messages
  history=sim.run();assert history.covers(study.metrics)==[]
  real_requests+=sim.decision.real_requests
  panels[arm]=get_panel(workspace/'trajectory/study.duckdb');snapshots[arm]=sim.env.snapshot();call_counts[arm]=len(sim.decision.calls)
  dump(workspace/'trajectory/metrics_history.json',history.model_dump(mode='json'))
  shutil.copy2(workspace/'trajectory/study.duckdb',out/f'{arm}_study_MOCK_ONLY.duckdb')
  jsonl(out/f'{arm}_rendered_requests_MOCK_ONLY.jsonl',sim.decision.rendered_requests)
  jsonl(out/f'{arm}_rejected_posts_MOCK_ONLY.jsonl',sim.env.rejections)
  jsonl(out/f'{arm}_panel_MOCK_ONLY.jsonl',panels[arm]);jsonl(out/f'{arm}_messages_MOCK_ONLY.jsonl',[{'seed':seed,'arm':arm,**v} for v in sim.env.messages]);jsonl(out/f'{arm}_exposures_MOCK_ONLY.jsonl',[{'exposure_event_id':f'{out.name}/{arm}/{v["step"]}/{v["agent_id"]}','seed':seed,'arm':arm,'prefix_origin':'COMMON' if v['step']<=1 else arm,'replay_rehydration':arm!='E1' and v['step']<=1,'counted_system_new':sum(z['system_new'] for z in v['entries']) if not (arm!='E1' and v['step']<=1) else 0,**v} for v in sim.env.delivery_log])
  jsonl(out/f'{arm}_memory_MOCK_ONLY.jsonl',[{'agent_id':aid,'history':mem.recent()} for aid,mem in sim.memories.items()])
 # Validate actual inherited realized state/actions. source provenance intentionally differs.
 for arm in ['E2','E3','E4']:
  left=[{k:v for k,v in r.items() if k!='action_source'} for r in panels['E1'] if r['step']<=1]
  right=[{k:v for k,v in r.items() if k!='action_source'} for r in panels[arm] if r['step']<=1]
  if left!=right:raise AssertionError('PREFORK_PANEL_NOT_EQUAL '+arm)
  assert sum(r['action_source']=='replay' for r in panels[arm])==len(rows)
  assert call_counts[arm]==4*len(rows) # t2/3/4 plus rule idle t5; no t1 call
 for arm,snapshot in snapshots.items():
  for d in snapshot['delivered']:
   if d['public_received']:assert arm in ['E3','E4'] and d['step']==2
   if d['peer_received']:assert arm in ['E2','E4'] and d['step'] in [2,3,4]
  for aid in sim.env.ids:
   # state history unchanged by any private evaluation; measurements do not yet exist.
   assert not any(k in m.canonical(snapshot['states'][aid]) for k in ['ejq_total','intention_scores','answer_key'])
 dump(out/'branch_invariants.json',reports)
 dump(out/'native_summary.json',{'status':'PASS_NATIVE_SCRIPTED_ONLY','data_kind':'MOCK_ONLY','seed':seed,'agents':len(rows),'arms':['E1','E2','E3','E4'],'panel_rows_per_arm':len(panels['E1']),'total_panel_rows':sum(map(len,panels.values())),'shared_common_panel_rows':2*len(rows),'new_decision_actions_by_arm':call_counts,'inherited_decision_calls':0,'real_llm_requests':real_requests,'materials_version':sim.env.materials['version'],'support_estimand':'P1 additional support vs no additional support','N1_active':False,'prefix_equal':True,'full_actions_in_payload':True,'native_branch_reports':reports})
 return out

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=20271001);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--pilot-six',action='store_true');ap.add_argument('--mode',choices=['scripted'],default='scripted');args=ap.parse_args()
 selected=json.loads((BASE/'config/pilot_DRAFT.json').read_text())['pilot_agents'] if args.pilot_six else None
 print(run(args.seed,args.out,selected))
