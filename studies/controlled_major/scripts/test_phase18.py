from pathlib import Path
import unittest,tempfile,copy,json,hashlib,sys
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'native'));sys.path.insert(0,str(BASE/'scripts'))
from studies.controlled_major_phase18 import model as m
import run_native_scripted as runner
from measurement_sidecar import requests,build_fixture,validate_measurement
from analyze_outcomes import analyze
from skills.sv_workspace import check_branch_invariant
from socioverse.abc import EnvironmentProvider,PopulationProvider,DecisionModel,MetricCollector
from socioverse.io.duckdb_store import open_readonly

class Phase18Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name)/'run';runner.run(20271001,cls.out)
  cls.bundle=build_fixture(cls.out,Path(cls.tmp.name)/'sidecar.json')
  cls.panels={arm:[json.loads(x) for x in (cls.out/f'{arm}_panel_MOCK_ONLY.jsonl').read_text().splitlines()] for arm in ['E1','E2','E3','E4']}
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test01_native_abcs(self):
  for cls,abc in [(m.MajorEnvironment,EnvironmentProvider),(m.MajorPopulation,PopulationProvider),(m.MajorDecision,DecisionModel),(m.MajorMetrics,MetricCollector)]:self.assertTrue(issubclass(cls,abc))
 def test02_persistent_panel(self):
  for rows in self.panels.values():
   self.assertEqual(len(rows),144);self.assertEqual(len({x['agent_id'] for x in rows}),24)
   for aid in {x['agent_id'] for x in rows}:self.assertEqual([x['step'] for x in rows if x['agent_id']==aid],list(range(6)))
 def test03_official_branches_and_replay(self):
  s=json.loads((self.out/'native_summary.json').read_text());self.assertEqual(s['inherited_decision_calls'],0);self.assertEqual(s['real_llm_requests'],0)
  self.assertTrue(all(x['ok'] and x['kind']=='branch' for x in s['native_branch_reports']))
  for arm,rows in self.panels.items():
   if arm=='E1':continue
   expected=[{k:v for k,v in x.items() if k!='action_source'} for x in self.panels['E1'] if x['step']<=1]
   actual=[{k:v for k,v in x.items() if k!='action_source'} for x in rows if x['step']<=1];self.assertEqual(actual,expected)
 def test04_source_tags_not_replayed_as_llm(self):
  for arm in ['E2','E3','E4']:self.assertTrue(all(x['action_source']=='replay' for x in self.panels[arm] if x['step']==1))
 def test05_public_only_t2_support(self):
  for arm in self.panels:
   exp=[json.loads(x) for x in (self.out/f'{arm}_exposures_MOCK_ONLY.jsonl').read_text().splitlines()]
   for x in exp:
    if x['public_received']:self.assertIn(arm,['E3','E4']);self.assertEqual(x['step'],2)
    if x['peer_received']:self.assertIn(arm,['E2','E4']);self.assertIn(x['step'],[2,3,4])
 def test06_no_public_in_control_memory(self):
  for arm in ['E1','E2']:
   self.assertNotIn('EV09',m.canonical(self.panels[arm]));self.assertNotIn('P1_01',m.canonical(self.panels[arm]))
 def test07_public_cascade_delay(self):
  exp=[json.loads(x) for x in (self.out/'E4_exposures_MOCK_ONLY.jsonl').read_text().splitlines()]
  public={s for c in m.load(BASE,20271001)[2]['P1'] for s in c['sources']}
  self.assertTrue(all(set(x['source_ids']) and set(x['source_ids'])<=public for x in exp if x['step']==3))
 def test08_same_round_not_observed(self):
  for arm in ['E2','E4']:
   for x in self.panels[arm]:
    t=x['step']
    for c in x['state']['measurement_context']['visible_feed']:
     if c['item_id'].startswith('M-'):
      msgs=[json.loads(v) for v in (self.out/f'{arm}_messages_MOCK_ONLY.jsonl').read_text().splitlines()]
      msg=next(v for v in msgs if v['card']['item_id']==c['item_id']);self.assertEqual(msg['step'],t-1)
 def test09_endpoint_idle(self):
  for rows in self.panels.values():
   for x in rows:
    if x['step']==5:self.assertEqual(x['action_kind'],'idle');self.assertEqual(x['action_payload'],{});self.assertEqual(x['state']['measurement_context']['visible_feed'],[])
 def test10_action_schema_no_measurement(self):
  for rows in self.panels.values():
   for x in rows:
    if x['step'] in [1,2,3,4]:self.assertEqual(set(x['action_payload']),{'judgment','reason','post'})
 def test11_measurement_not_in_agent_memory(self):
  for arm in self.panels:
   history=(self.out/f'{arm}_memory_MOCK_ONLY.jsonl').read_text()
   for term in ['intention_prompt','rank_groups','score_missing_reasons','answer_key','ejq_total','intention_scores']:self.assertNotIn(term,history)
 def test12_private_requests_exclude_keys_labels(self):
  context=self.panels['E4'][-1]['state']['measurement_context'];a,b,f=requests(context,'BASE_01',3,'E4')
  for word in ['answer_key','expected_reasoning','ses_group','experimental_arm']:self.assertNotIn(word,m.canonical(a)+m.canonical(b))
  self.assertEqual(len(b['questions']),8)
 def test13_deepcopy_request(self):
  x=self.panels['E1'][0]['state']['measurement_context'];before=m.digest(x);a,b,f=requests(x,'BASE_01',0);a['context']['malicious']='fake';self.assertEqual(m.digest(x),before)
 def test14_valid_stages_and_common_once(self):
  self.assertEqual(len(self.bundle['records']),240)
  self.assertEqual(sum(x['arm']=='COMMON' for x in self.bundle['records']),48)
  self.assertFalse(any(x['step'] in [3,4] for x in self.bundle['records']))
 def test15_independent_scores(self):
  self.assertNotEqual(sum(self.bundle['records'][0]['scores'].values()),100)
  for x in self.bundle['records']:validate_measurement(x)
 def test16_mock_rejected_by_default(self):
  with self.assertRaisesRegex(ValueError,'MOCK_DATA_REJECTED'):analyze(self.bundle)
 def tiny(self):
  x=copy.deepcopy(self.bundle);x['records']=[r for r in x['records'] if r['agent_id']=='A001'];x['expected_agent_ids']=['A001'];x['expected_roster']=[r for r in x['expected_roster'] if r['agent_id']=='A001'];return x
 def test17_primary_formula(self):
  x=self.tiny()
  for r in x['records']:
   if r['stage_id']=='T3' and r['arm'] in ['E1','E2','E3','E4']:r['scores']['CS']={'E1':60,'E2':70,'E3':80,'E4':90}[r['arm']]
  a=analyze(x,True);p=next(r for r in a['contrasts'] if r['contrast']=='PRIMARY_E3_E1' and r['stage']=='T3' and r['ses']=='ALL');self.assertEqual(p['complete_pair_mean'],20);self.assertEqual(p['prespecified_denominator_bound'],[20,20])
  inter=next(r for r in a['contrasts'] if r['contrast']=='INTERACTION' and r['stage']=='T3' and r['ses']=='ALL');self.assertEqual(inter['complete_pair_mean'],0)
 def test18_missing_bounds(self):
  x=self.tiny()
  for r in x['records']:
   if r['stage_id']=='T3' and r['arm']=='E1':r['scores']['CS']=60
   if r['stage_id']=='T3' and r['arm']=='E3':r['scores']['CS']=None;r['score_missing_reasons']['CS']='REFUSAL';r['measurement_status']='PARTIAL'
  a=analyze(x,True);p=next(r for r in a['contrasts'] if r['contrast']=='PRIMARY_E3_E1' and r['stage']=='T3' and r['ses']=='ALL');self.assertIsNone(p['complete_pair_mean']);self.assertEqual(p['prespecified_denominator_bound'],[-60,40]);self.assertEqual(p['expected_n'],1)
 def test19_baseline_missing_no_imputation(self):
  x=self.tiny();x['records']=[r for r in x['records'] if r['stage_id']!='T1'];a=analyze(x,True)
  self.assertTrue(all(r['vector']['CS'] is None for r in a['changes'] if r['from']=='T1'))
  self.assertIsNotNone(next(r for r in a['contrasts'] if r['contrast']=='PRIMARY_E3_E1' and r['stage']=='T3' and r['ses']=='ALL')['complete_pair_mean'])
 def test20_duplicate_rejected(self):
  x=self.tiny();x['records'].append(x['records'][0])
  with self.assertRaisesRegex(ValueError,'DUPLICATE_MEASUREMENT'):analyze(x,True)
 def test21_prompt_drift_rejected(self):
  x=self.tiny();x['records'][0]['intention_prompt_sha256']='changed'
  with self.assertRaisesRegex(ValueError,'NOT_COMPARABLE'):analyze(x,True)
 def test22_range_rejects_bool_nan(self):
  for v in [True,float('nan'),101,-1,'50']:
   x=copy.deepcopy(self.bundle['records'][0]);x['scores']['CS']=v
   with self.assertRaises(ValueError):validate_measurement(x)
 def test23_unknown_ranking_rejected(self):
  x=copy.deepcopy(self.bundle['records'][0]);x['rank_groups']=[['CS'],['CS'],['EE'],['STAT']]
  with self.assertRaises(ValueError):validate_measurement(x)
 def test24_actual_duckdb_messages_and_events(self):
  db=self.out/'native_study/trajectory/study.duckdb';con=open_readonly(db)
  try:
   self.assertEqual(con.execute('select count(*) from panel').fetchone()[0],144);self.assertEqual(con.execute('select count(*) from messages').fetchone()[0],96);self.assertEqual(con.execute('select count(*) from events where step=2').fetchone()[0],2)
  finally:con.close()
 def test25_action_purity_replay(self):
  _,env,_,_=m.make_bundles();a=m.MajorEnvironment(env);b=m.MajorEnvironment(env);a.reset(20271001);b.reset(20271001);a.advance_to(1);b.advance_to(1)
  from socioverse.schemas import Action
  actions=[Action(agent_id=x['agent_id'],step=1,kind=x['action_kind'],payload=x['action_payload'],source='replay') for x in self.panels['E1'] if x['step']==1]
  a.apply(actions);b.apply(copy.deepcopy(actions));self.assertEqual(a.snapshot(),b.snapshot())
 def test26_bad_event_time(self):
  _,e,_,_=m.make_bundles();env=m.MajorEnvironment(e);env.reset(20271001)
  with self.assertRaisesRegex(ValueError,'TIME_DISCONTINUITY'):env.advance_to(2)
 def test27_asset_corruption_rejected(self):
  _,e,_,_=m.make_bundles();e.provider_args['asset_hashes']['config/active_materials.json']='fake';env=m.MajorEnvironment(e)
  with self.assertRaisesRegex(ValueError,'ASSET_HASH_MISMATCH'):env.reset(20271001)
 def test28_real_path_blocked_without_authorization(self):
  _,e,_,_=m.make_bundles();env=m.MajorEnvironment(e);env.reset(20271001);env.advance_to(1)
  with self.assertRaisesRegex(RuntimeError,'NOT_AUTHORIZED'):m.MajorDecision(llm_kind='openai').decide_batch(env.observe_batch(env.ids,1),{})
 def test29_source_chain_and_neighbors(self):
  _,net,_,_=m.load(BASE,20271001)
  for arm in ['E2','E4']:
   exp=[json.loads(x) for x in (self.out/f'{arm}_exposures_MOCK_ONLY.jsonl').read_text().splitlines()]
   for e in exp:
    for cid in e['content_ids']:
     if cid.startswith('MSG:'):self.assertIn(cid.split(':')[2],net['ordered_neighbors'][e['agent_id']])
 def test30_active_cards_no_N1_and_220_limit(self):
  x=m.load(BASE,20271001)[2];self.assertNotIn('N1',x);self.assertFalse(x['N1_active'])
  self.assertEqual([len(x['S1']),len(x['P1'])],[4,6]);self.assertEqual([len(g) for g in x['F'].values()],[4,4,4])
  self.assertTrue(all(len(c['full_text'])<=(1024 if c['kind']=='public' else 220) for group in [x['S1'],x['P1']]+list(x['F'].values()) for c in group))
 def test31_prior_artifacts_unchanged(self):
  manifest=json.loads((BASE.parent/'audit/MAIN_BEFORE.json').read_text())
  for path,h in manifest.items():self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),h)
 def test32_official_invariant_rejects_seed_edit(self):
  workspace=self.out/'native_study';p=workspace/'simulation/simulation.json';original=p.read_bytes();x=json.loads(original);x['seed']=1;p.write_text(json.dumps(x))
  try:
   report=check_branch_invariant(workspace,downgrade=False);self.assertFalse(report['ok']);self.assertFalse(report['downgraded'])
  finally:p.write_bytes(original)

 def fake_config(self):
  return {'paid_authorized':True,'human_protocol_approval':True,'human_material_approval':True,'human_measurement_approval':True,'token_counter_verified':True,'model':'FAKE_MODEL','provider':'FAKE_TRANSPORT','exact_model_version':'FAKE_V1','price_input_per_million':2,'price_output_per_million':8,'max_total_budget_usd':5,'max_input_tokens_per_call':4000,'max_output_tokens_per_call':1000,'max_total_calls':126}
 def test33_usage_ledger_fake_transport(self):
  from guarded_channel import GuardedChannel
  with tempfile.TemporaryDirectory() as d:
   ledger=Path(d)/'usage.jsonl'
   channel=GuardedChannel(self.fake_config(),lambda *a:{'text':'{"ok": true}','model':'FAKE_V1','request_id':'fake1','usage':{'input_tokens':10,'output_tokens':5}},lambda p:10,ledger)
   self.assertEqual(channel.invoke({}, {'data_kind':'FAKE_TRANSPORT_TEST'},lambda x:None),{'ok':True})
   self.assertAlmostEqual(channel.spent,.00006);self.assertEqual(json.loads(ledger.read_text())['usage']['output_tokens'],5)
 def test34_budget_stops_before_transport(self):
  from guarded_channel import GuardedChannel
  cfg=self.fake_config();cfg['max_total_budget_usd']=.001
  with tempfile.TemporaryDirectory() as d:
   channel=GuardedChannel(cfg,lambda *a:self.fail('transport must not execute'),lambda p:10,Path(d)/'usage.jsonl')
   with self.assertRaisesRegex(RuntimeError,'BUDGET'):channel.invoke({}, {},lambda x:None)
 def test35_missing_usage_halts(self):
  from guarded_channel import GuardedChannel
  with tempfile.TemporaryDirectory() as d:
   channel=GuardedChannel(self.fake_config(),lambda *a:{'text':'{}','model':'FAKE_V1','request_id':'fake'},lambda p:10,Path(d)/'usage.jsonl')
   with self.assertRaisesRegex(RuntimeError,'USAGE'):channel.invoke({}, {},lambda x:None)
   self.assertTrue(channel.halted)
 def test36_version_drift_halts(self):
  from guarded_channel import GuardedChannel
  with tempfile.TemporaryDirectory() as d:
   channel=GuardedChannel(self.fake_config(),lambda *a:{'text':'{}','model':'NEW_VERSION','request_id':'fake','usage':{'input_tokens':10,'output_tokens':5}},lambda p:10,Path(d)/'usage.jsonl')
   with self.assertRaisesRegex(RuntimeError,'VERSION'):channel.invoke({}, {},lambda x:None)
 def test37_schema_retry_then_stop(self):
  from guarded_channel import GuardedChannel
  with tempfile.TemporaryDirectory() as d:
   channel=GuardedChannel(self.fake_config(),lambda *a:{'text':'brokenJSON','model':'FAKE_V1','request_id':'fake','usage':{'input_tokens':10,'output_tokens':5}},lambda p:10,Path(d)/'usage.jsonl')
   with self.assertRaisesRegex(RuntimeError,'SCHEMA'):channel.invoke({}, {},lambda x:None)
   self.assertEqual(channel.calls,2);self.assertEqual(channel.retries,1);self.assertTrue(channel.halted)
 def test38_no_approval_no_credential_read(self):
  from guarded_channel import open_channel
  with self.assertRaises(PermissionError):open_channel(BASE/'config/pilot_DRAFT.json','unused.jsonl')
 def test39_private_evaluator_fake_channel(self):
  from guarded_channel import GuardedChannel
  from private_llm_measurement import evaluate
  seen=[]
  def transport(prompt,*a):
   seen.append(copy.deepcopy(prompt))
   if 'questions' in prompt:
    reply={'answers':[{'item_id':x['item_id'],'tier1':'A','tier2':'A'} for x in prompt['questions']]}
   else:reply={'scores':dict.fromkeys(m.IDS,50),'first_choices':[],'rank_groups':[['CS','AUTO','EE','STAT']],'risk_cs':50,'explanation':'FAKE_INTERFACE_TEST'}
   return {'text':json.dumps(reply),'model':'FAKE_V1','request_id':'fake','usage':{'input_tokens':10,'output_tokens':5}}
  context=self.panels['E1'][0]['state']['measurement_context'];before=m.digest(context)
  with tempfile.TemporaryDirectory() as d:
   channel=GuardedChannel(self.fake_config(),transport,lambda p:10,Path(d)/'usage.jsonl');out=evaluate(context,'BASE_01',0,channel,{'data_kind':'FAKE_TRANSPORT_TEST'})
   self.assertEqual(channel.calls,2);self.assertEqual(out['ejq']['total'],sum(out['ejq']['item_scores']));self.assertNotIn('answer_key',m.canonical(seen));self.assertEqual(m.digest(context),before)
 def test40_oversized_input_stops(self):
  from guarded_channel import GuardedChannel
  with tempfile.TemporaryDirectory() as d:
   channel=GuardedChannel(self.fake_config(),lambda *a:self.fail('no transport'),lambda p:5000,Path(d)/'usage.jsonl')
   with self.assertRaisesRegex(ValueError,'TOKEN_CAP'):channel.invoke({}, {},lambda x:None)

 def test41_no_N1_any_active_feed_or_history(self):
  _,_,mats,_=m.load(BASE,20271001)
  for arm,rows in self.panels.items():
   for r in rows:
    ctx=r['state']['measurement_context'];text=m.canonical(ctx)
    for word in ['NC01','NC02','NC03','neutral_control','假想校园','图景描述']:self.assertNotIn(word,text)
    if r['step']==2:self.assertEqual(len(ctx['visible_feed']),10 if arm in ['E3','E4'] else 4)
 def test42_round_specific_F_not_S1_rebroadcast(self):
  mats=m.load(BASE,20271001)[2]
  for arm in ['E1','E3']:
   for r in self.panels[arm]:
    t=r['step']
    if t in [2,3,4]:self.assertEqual([c['item_id'] for c in r['state']['measurement_context']['visible_feed'][:4]],[c['item_id'] for c in mats['F'][str(t)]])
 def test43_full_rendered_requests_hide_labels(self):
  for arm in self.panels:
   for line in (self.out/f'{arm}_rendered_requests_MOCK_ONLY.jsonl').read_text().splitlines():
    request=m.canonical(__import__('json').loads(line)['request'])
    for term in ['PUB:','CTL:','EV09','public_intervention','neutral_control','canonical_id','\"kind\"','\"arm\"','treatment','answer_key']:self.assertNotIn(term,request)
 def test44_support_never_early_or_crossarm(self):
  from materials_adapter import audit_context,project
  public=m.load(BASE,20271001)[2]['P1'][0]
  ctx=copy.deepcopy(self.panels['E1'][0]['state']['measurement_context']);ctx['visible_feed']=[project(public)]
  for t,arm in [(0,'COMMON'),(1,'COMMON'),(2,'E1'),(5,'E2')]:
   with self.assertRaises(ValueError):audit_context(ctx,t,arm)
 def test45_roster_denominator_no_returned_rows(self):
  x=copy.deepcopy(self.bundle);x['records']=[r for r in x['records'] if r['agent_id']!='A001'];r=analyze(x,True)
  p=next(c for c in r['contrasts'] if c['contrast']=='PRIMARY_E3_E1' and c['stage']=='T3' and c['ses']=='ALL');self.assertEqual(p['expected_n'],24);self.assertEqual(p['complete_pair_n'],23)
 def test46_invalid_numeric_rows_cannot_enter_risk_or_ejq_means(self):
  x=self.tiny()
  for r in x['records']:
   r.update(risk_cs=80,risk_measurement_status='MISSING',risk_missing_reason='PARSE_ERROR',ejq={'form_id':r['ejq_form'],'item_scores':[2]*8,'total':16},ejq_measurement_status='MISSING',ejq_missing_reason='PARSE_ERROR')
  result=analyze(x,True)
  self.assertTrue(all(z['mean'] is None and z['valid_n']==0 for z in result['metric_levels']))
  self.assertTrue(all(z['risk_change'] is None and z['ejq_change'] is None for z in result['changes']))
 def test47_overall_missing_blocks_metrics_even_with_valid_numeric_substatus(self):
  x=self.tiny()
  for r in x['records']:r.update(measurement_status='MISSING',risk_cs=60,risk_measurement_status='VALID',risk_missing_reason=None)
  result=analyze(x,True);self.assertTrue(all(z['mean'] is None for z in result['metric_levels']))
  self.assertTrue(all(z['complete_pair_mean'] is None for z in result['contrasts']))
 def test48_partial_only_observed_metric_allowed(self):
  from analyze_outcomes import metric_value
  r=copy.deepcopy(self.bundle['records'][0]);r.update(measurement_status='PARTIAL',risk_cs=80,risk_measurement_status='VALID',risk_missing_reason=None)
  self.assertEqual(metric_value(r,'risk'),80);r['risk_measurement_status']='PARTIAL';self.assertIsNone(metric_value(r,'risk'))
 def test49_seed_and_branch_queues_isolated(self):
  _,e,_,_=m.make_bundles();a=m.MajorEnvironment(e);b=m.MajorEnvironment(e);a.reset(20271001);b.reset(20271001)
  a.bus.post({'author_id':'A001','step':1,'card':{},'content':'PRIVATE_TEST'})
  self.assertFalse(b.bus._messages);self.assertIsNot(a.received,b.received)
 def test50_rejected_overlong_post_falls_back_without_truncation(self):
  from socioverse.schemas import Action
  _,e,_,_=m.make_bundles();env=m.MajorEnvironment(e);env.reset(20271001);env.advance_to(1)
  actions=[Action(agent_id=r['agent_id'],step=1,kind=r['action_kind'],payload=copy.deepcopy(r['action_payload']),source='rule') for r in self.panels['E1'] if r['step']==1]
  target=actions[0];target.payload['post']['body']='字'*181;env.apply(actions)
  self.assertEqual(len(target.payload['post']['body']),181);self.assertIsNone(env.current_post[target.agent_id]);self.assertEqual(env.rejections[-1]['reason'],'POST_SCHEMA')
  env.advance_to(2);env.controls['feedback']=True
  for aid in env.ids:
   if target.agent_id in env.net['ordered_neighbors'][aid]:
    slot=env.net['ordered_neighbors'][aid].index(target.agent_id);self.assertEqual(env.raw_feed(aid,2)[slot]['content_id'],env.materials['F']['2'][slot]['content_id'])
 def test51_old_materials_and_banks_preserved(self):
  manifest=json.loads((BASE.parent/'audit/MAIN_BEFORE.json').read_text())
  for name in ['inputs/EJQ_forms_PRIVATE_DRAFT.jsonl','inputs/phase17/population/source_roster_DRAFT.jsonl']:
   expected=next(h for p,h in manifest.items() if p.endswith('/'+name))
   self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(),expected)
 def test52_estimand_updated(self):
  x=analyze(self.bundle,True)
  self.assertIn('additional P1 support vs no additional support',x['primary']);self.assertTrue(x['interaction_not_causal_mediation'])
  self.assertNotIn('替代N1',m.canonical(x));self.assertIn('FEEDBACK_E2_E1',{c['contrast'] for c in x['contrasts']})

if __name__=='__main__':unittest.main()
