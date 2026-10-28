"""Native Path-B study on unmodified SocioVerse2 Core.
Precedents: opinion_diffusion branch replay, campus_dining messaging.
All costs/rounds/roster are researcher assumptions from Phase17; no behavioral effect rule.
Measurements run as private post-run sidecars, NEVER as action state.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import copy,hashlib,json,sys,os,math
from socioverse.abc import EnvironmentProvider,PopulationProvider,DecisionModel,MetricCollector
from socioverse.engine.registry import register
from socioverse.engine.messaging import InMemoryMessageBus
from socioverse.schemas import (Action,Observation,Persona,EnvironmentBundle,EnvironmentLayer,PopulationBundle,InteractionStructure,SimulationConfig,StudySpec,ScheduledEvent)

BASE=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(BASE/'inputs/phase17/scripts'))
import controlled_runtime as legacy
IDS=legacy.IDS
sys.path.insert(0,str(BASE/'scripts'))
from materials_adapter import load_materials,project,text,behavior_request,rendered_request,audit_context


def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def read_assets(root,expected):
 root=Path(root)
 for name,h in expected.items():
  if hashlib.sha256((root/name).read_bytes()).hexdigest()!=h:raise ValueError('ASSET_HASH_MISMATCH '+name)
 return root

def assets(root):
 root=Path(root)
 names=['scripts/ejq_alignment.py','scripts/guarded_channel.py','scripts/private_llm_measurement.py','scripts/measurement_sidecar.py','inputs/phase17/scripts/controlled_runtime.py','inputs/phase17/config/experiment.json','inputs/phase17/config/scenario.json','inputs/phase17/population/source_roster_DRAFT.jsonl','config/active_materials.json','scripts/materials_adapter.py','native/studies/controlled_major_phase18/model.py']+list(json.loads((root/'config/active_materials.json').read_text())[k] for k in ['payloads','source_ledger'])+[f'inputs/phase17/population/network_{s}.json' for s in [20271001,20271002,20271003]]
 return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names}

def load(root,seed,selected=None):
 root=Path(root);rows=[json.loads(x) for x in (root/'inputs/phase17/population/source_roster_DRAFT.jsonl').read_text().splitlines()]
 if selected is not None:rows=[r for r in rows if r['fixed']['agent_id'] in selected]
 return rows,json.loads((root/f'inputs/phase17/population/network_{seed}.json').read_text()),load_materials(root),json.loads((root/'inputs/phase17/config/scenario.json').read_text())

@register('population','phase18.pop')
class MajorPopulation(PopulationProvider):
 def __init__(self,bundle):self.bundle=bundle
 def build(self,seed):
  a=self.bundle.provider_args;root=read_assets(a['asset_root'],a['asset_hashes']);self.rows,self.net,_,_=load(root,seed,a.get('selected_ids'))
  return [Persona(agent_id=r['fixed']['agent_id'],attributes=legacy.project(r),group_key=r['fixed']['base_template_id'],init_state={'measurement':'PRIVATE_SIDECAR_ONLY'}) for r in self.rows]
 def neighbors(self,aid):
  allowed={r['fixed']['agent_id'] for r in self.rows}
  return [n for n in self.net['ordered_neighbors'][aid] if n in allowed]

@register('environment','phase18.env')
class MajorEnvironment(EnvironmentProvider):
 def __init__(self,bundle):self.bundle=bundle
 def reset(self,seed):
  a=self.bundle.provider_args;root=read_assets(a['asset_root'],a['asset_hashes']);rows,self.net,self.materials,self.scenario=load(root,seed,a.get('selected_ids'))
  self.rows={r['fixed']['agent_id']:r for r in rows};self.ids=list(self.rows);self.step=0;self.controls={'public':False,'feedback':False};self.bus=InMemoryMessageBus(carry_previous_step=True)
  self.judgments={aid:[] for aid in self.ids};self.received={aid:[] for aid in self.ids};self.messages=[];self.delivery_log=[];self.current_packet={};self.current_post={aid:None for aid in self.ids};self.new_messages=[];self.applied_steps=[];self.seed=seed;self.rejections=[];self.request_log=[];self.scope_id=str(root)
 def advance_to(self,t):
  if t!=self.step+1:raise ValueError('TIME_DISCONTINUITY')
  self.step=t;fired=[]
  for e in self.bundle.scheduled_events:
   if e.at_step==t:
    if e.property_name not in self.controls or e.target_layer!='controls' or e.op!='set':raise ValueError('INVALID_INTERVENTION')
    self.controls[e.property_name]=bool(e.value);fired.append(e)
  return fired
 def arm(self):
  if self.step<2:return 'COMMON'
  return ('E4' if self.controls['feedback'] else 'E3') if self.controls['public'] else ('E2' if self.controls['feedback'] else 'E1')
 def _social(self,aid,t):
  if t==1:return copy.deepcopy(self.materials['S1'])
  if t not in [2,3,4]:return []
  visible=self.bus.fetch(aid,t,self.net['ordered_neighbors'][aid]) if self.controls['feedback'] else []
  out=[]
  for slot,neighbor in enumerate(self.net['ordered_neighbors'][aid]):
   matches=[v for v in visible if v['author_id']==neighbor and v['step']==t-1]
   out.append(copy.deepcopy(matches[0]['card']) if len(matches)==1 else copy.deepcopy(self.materials['F'][str(t)][slot]))
  return out
 def raw_feed(self,aid,t):
  feed=self._social(aid,t)
  if t==2 and self.controls['public']:feed+=copy.deepcopy(self.materials['P1'])
  return feed
 def packet(self,aid,t):
  row=self.rows[aid];cards={c['major_id']:c for c in self.scenario['cards']}
  packet={'common_scenario':copy.deepcopy(self.scenario['common']),'persona':legacy.project(row),'major_cards':[copy.deepcopy(cards[i]) for i in legacy.display_order(row)],'visible_feed':[project(c) for c in self.raw_feed(aid,t)],'visible_history':[project(c) for c in self.received[aid]],'own_judgments':copy.deepcopy(self.judgments[aid])}
  legacy.guard_context(packet);audit_context(packet,t,self.arm())
  return packet
 def observe_batch(self,agent_ids,t,round_idx=0):
  if t!=self.step or round_idx!=0:raise ValueError('OBSERVATION_TIME_OR_ROUND')
  return [Observation(agent_id=aid,step=t,macro_physical=copy.deepcopy(self.scenario['common']),local_physical={'personal_resources':legacy.project(self.rows[aid])},macro_information={'major_cards':self.packet(aid,t)['major_cards']},local_information={'packet':self.packet(aid,t)}) for aid in agent_ids]
 def apply(self,actions):
  if len(actions)!=len(self.ids) or {a.agent_id for a in actions}!=set(self.ids) or any(a.step!=self.step for a in actions):raise ValueError('ACTION_COVERAGE_OR_TIME')
  packets={aid:self.packet(aid,self.step) for aid in self.ids}
  feeds={aid:self.raw_feed(aid,self.step) for aid in self.ids}
  self.new_messages=[]
  for a in actions:
   aid=a.agent_id;post=a.payload.get('post');rejected=None
   try:validate_action(a,packets[aid])
   except ValueError as error:
    if str(error) not in ['POST_SCHEMA','UNKNOWN_PARENT','UNKNOWN_SOURCE','UNKNOWN_ORIGINAL_CLAIM','PARENT_SOURCE_MISMATCH']:raise
    rejected=str(error);post=None;self.rejections.append({'step':self.step,'agent_id':aid,'reason':rejected})
   self.current_packet[aid]=packets[aid]
   if self.step==5:continue
   self.received[aid].extend(copy.deepcopy(feeds[aid]))
   self.judgments[aid].append({'step':self.step,'judgment':a.payload['judgment'],'reason':a.payload['reason']})
   self.current_post[aid]=copy.deepcopy(post)
   if post:
    cid=f'MSG:{self.step}:{aid}';mid='M-'+hashlib.sha256(cid.encode()).hexdigest()[:12]
    inverse={r:s for c in self.materials['S1']+self.materials['P1']+sum(self.materials['F'].values(),[]) for r,s in zip(c['source_refs'],c['sources'])}
    card={'content_id':cid,'item_id':mid,'title':'同伴帖子','body':post['body'],'source_ids':[inverse[r] for r in post['source_ids']],'source_refs':post['source_ids'],'kind':'peer','source_note':'同伴转述'}
    msg={'author_id':aid,'step':self.step,'round':0,'channel':'peer','content':post['body'],'audience':'neighbors','card':card,'parent_ids':post['parent_ids'],'source_ids':card['source_ids'],'source_refs':post['source_ids'],'original_claim_ids':post['original_claim_ids'],'added_interpretation':post['added_interpretation'],'unsupported_extrapolation':'NOT_CODED_SCRIPTED'}
    self.bus.post(msg);self.messages.append(copy.deepcopy(msg));self.new_messages.append(copy.deepcopy(msg))
  for aid in self.ids:
   feed=feeds[aid];entries=[]
   for slot,c in enumerate(feed):
    social=self.step in [2,3,4] and slot<4;peer=c['kind']=='peer'
    reason=None
    if social and not peer:
     neighbor=self.net['ordered_neighbors'][aid][slot]
     reason='FEEDBACK_OFF' if not self.controls['feedback'] else ('NEIGHBOR_POST_REJECTED' if any(x['step']==self.step-1 and x['agent_id']==neighbor for x in self.rejections) else 'NO_UNIQUE_LEGAL_PREVIOUS_POST')
    entries.append({'slot':slot,'canonical_id':c['content_id'],'item_id':c['item_id'],'kind':c['kind'],'source_ids':c['source_ids'],'source_refs':c['source_refs'],'visible_chars':len(text(project(c))),'system_new':not peer,'dynamic_replacement':social and peer,'fixed_fallback':social and not peer,'replaced_static_id':self.materials['F'][str(self.step)][slot]['content_id'] if social and peer else None,'fallback_reason':reason,'generated_step':self.step-1 if peer else None})
   self.delivery_log.append({'agent_id':aid,'step':self.step,'content_ids':[c['content_id'] for c in feed],'source_ids':sorted({r for c in feed for r in c['source_ids']}),'public_received':any(c['kind']=='public' for c in feed),'peer_received':any(c['kind']=='peer' for c in feed),'support_assignment':('ADDITIONAL_P1' if self.controls['public'] else 'NO_ADDITIONAL_INTERVENTION_MATERIAL') if self.step==2 else 'NOT_SCHEDULED','materials_version':self.materials['version'],'entries':entries})
  self.applied_steps.append(self.step)
 def agent_state(self,aid):
  context=self.current_packet.get(aid) if self.step else self.packet(aid,0)
  # Post-decision read-only measurement view, not agent state updated by measurement.
  view=copy.deepcopy(context);view['own_judgments']=copy.deepcopy(self.judgments[aid])
  return {'step':self.step,'reason':self.judgments[aid][-1]['reason'] if self.judgments[aid] else '', 'judgment_history':copy.deepcopy(self.judgments[aid]),'visible_history':[project(c) for c in self.received[aid]],'current_post':copy.deepcopy(self.current_post[aid]),'measurement_context':view,'context_sha256':digest(view),'data_kind':self.bundle.provider_args.get('data_kind','MOCK_ONLY'),'materials_version':self.materials['version'],'backend_scope':{'seed':self.seed,'arm':self.arm()}}
 def snapshot(self):return {'controls':copy.deepcopy(self.controls),'messages':copy.deepcopy(self.messages),'delivered':copy.deepcopy(self.delivery_log),'states':{aid:self.agent_state(aid) for aid in self.ids}}

def validate_action(a,packet):
 if a.step==5:
  if a.kind!='idle' or a.payload!={}:raise ValueError('ENDPOINT_NOT_IDLE')
  return
 if a.kind!='judge_and_post' or set(a.payload)!={'judgment','reason','post'}:raise ValueError('ACTION_SCHEMA')
 if not all(isinstance(a.payload[k],str) and 0<len(a.payload[k])<=400 for k in ['judgment','reason']):raise ValueError('JUDGMENT_FORMAT')
 post=a.payload['post']
 if post is not None:
  if set(post)!={'body','source_ids','parent_ids','original_claim_ids','added_interpretation'} or not isinstance(post['body'],str) or not 0<len(post['body'])<=180:raise ValueError('POST_SCHEMA')
  visible={c['item_id']:c for c in packet['visible_feed']+packet['visible_history']}
  if any(not isinstance(post[k],list) or any(not isinstance(x,str) for x in post[k]) for k in ['source_ids','parent_ids','original_claim_ids']):raise ValueError('POST_SCHEMA')
  if any(len(post[k])!=len(set(post[k])) for k in ['source_ids','parent_ids']):raise ValueError('POST_SCHEMA')
  if not isinstance(post['added_interpretation'],str) or len(post['added_interpretation'])>400:raise ValueError('POST_SCHEMA')
  if any(p not in visible for p in post['parent_ids']):raise ValueError('UNKNOWN_PARENT')
  available={s for c in visible.values() for s in c['source_refs']}
  if any(s not in available for s in post['source_ids']):raise ValueError('UNKNOWN_SOURCE')
  if post['original_claim_ids']:raise ValueError('UNKNOWN_ORIGINAL_CLAIM')
  if post['source_ids'] and (not post['parent_ids'] or not set(post['source_ids'])<={s for p in post['parent_ids'] for s in visible[p]['source_refs']}):raise ValueError('PARENT_SOURCE_MISMATCH')

@register('decision','phase18.decision')
class MajorDecision(DecisionModel):
 def __init__(self,llm_kind='scripted',model=None,max_workers=1,authorized=False,approval_config=None,usage_ledger_path=None):
  self.llm_kind=llm_kind;self.model=model;self.max_workers=max_workers;self.authorized=authorized;self.calls=[];self.real_requests=0;self.approval_config=approval_config;self.usage_ledger_path=usage_ledger_path;self.channel=None;self.rendered_requests=[]
 def _one(self,ob):
  packet=ob.local_information['packet']
  if ob.step==5:return Action(agent_id=ob.agent_id,step=5,kind='idle',payload={},source='rule')
  rendered=rendered_request(packet);self.rendered_requests.append({'agent_id':ob.agent_id,'step':ob.step,'request':rendered})
  if self.llm_kind=='scripted':
   card=packet['visible_feed'][4+(int(ob.agent_id[-3:])-1)%6] if len(packet['visible_feed'])==10 else packet['visible_feed'][0]
   # No direction/effect, SES rule, factual invention or copying a private measurement.
   reason='我会结合已有兴趣和刚看到的讨论，再想想自己的专业选择。'
   post={'body':'我看到了一段关于AI编程和职业变化的讨论，还想继续了解。','source_ids':card['source_refs'],'parent_ids':[card['item_id']],'original_claim_ids':[],'added_interpretation':'SCRIPTED_TRACE_FIXTURE'}
   return Action(agent_id=ob.agent_id,step=ob.step,kind='judge_and_post',payload={'judgment':'SCRIPTED_ONLY，不对真实风险或专业意愿作推断。','reason':reason,'post':post},rationale=[reason],source='rule')
  if self.llm_kind!='openai' or not self.authorized:raise RuntimeError('REAL_LLM_NOT_AUTHORIZED')
  # Provider path implemented but unexecuted this phase. No automatic fallback to mock.
  sys.path.insert(0,str(BASE/'scripts'))
  from guarded_channel import open_channel
  if not self.approval_config or not self.usage_ledger_path:raise RuntimeError('APPROVAL_AND_USAGE_LEDGER_REQUIRED')
  if self.channel is None:self.channel=open_channel(self.approval_config,self.usage_ledger_path)
  prompt=behavior_request(packet)
  self.real_requests+=1
  def validate(payload):
   a=Action(agent_id=ob.agent_id,step=ob.step,kind='judge_and_post',payload=payload,rationale=[payload.get('reason','')],source='llm');validate_action(a,packet)
  payload=self.channel.invoke(prompt,{'agent_id':ob.agent_id,'step':ob.step,'purpose':'behavior'},validate)
  return Action(agent_id=ob.agent_id,step=ob.step,kind='judge_and_post',payload=payload,rationale=[payload['reason']],source='llm')

 def decide_batch(self,obs,memories):
  # The study does not read raw AgentMemory; the environment supplies allowed prior judgments.
  before={aid:digest(m.recent()) for aid,m in memories.items()}
  if self.llm_kind=='scripted':out=[self._one(ob) for ob in obs]
  else:
   with ThreadPoolExecutor(max_workers=min(self.max_workers,len(obs))) as pool:out=list(pool.map(self._one,obs))
  if before!={aid:digest(m.recent()) for aid,m in memories.items()}:raise AssertionError('DECISION_MUTATED_MEMORY')
  self.calls.extend((a.agent_id,a.step) for a in out)
  return out

@register('collector','phase18.metrics')
class MajorMetrics(MetricCollector):
 def collect(self,env,actions,t):return {'agents':len(env.ids),'posts':len(env.new_messages) if t in [1,2,3,4] else 0,'measurement_fields_in_actions':sum(any(k in canonical(a.payload) for k in ['"scores"','"ejq"','"rank_groups"','"answer_key"','"intention_prompt"']) for a in actions)}
 def columns(self):return ['agents','posts','measurement_fields_in_actions']

def make_bundles(seed=20271001,root=BASE,selected_ids=None):
 root=Path(root);rows,net,_,_=load(root,seed,selected_ids);ids={x['fixed']['agent_id'] for x in rows}
 args={'asset_root':str(root),'asset_hashes':assets(root),'selected_ids':selected_ids}
 study=StudySpec(study_id='controlled_major_phase18',title='Controlled major preference — isolated P1 six-card scripted validation',research_question='Additional P1 support vs no additional support; CS E3-E1 endpoint; scripted has no effect validity',n_steps=5,seed=seed,time_unit='abstract',step_meaning='One controlled information/decision round, no calendar duration asserted',metrics=['agents','posts','measurement_fields_in_actions'],metric_descriptions={'agents':'Persistent agents count','posts':'Current round generated posts count, including research-only OFF posts','measurement_fields_in_actions':'Action payloads containing private measurement field names (must be zero); full memory audited separately'},domain='college-major-information-response',tags=['SES','controlled','DRAFT'],legacy_simulator='from_scratch',provider_refs=['phase18.env','phase18.pop','phase18.decision','phase18.metrics'],status='draft')
 env=EnvironmentBundle(study_id=study.study_id,provider_ref='phase18.env',provider_args=args,layers=[EnvironmentLayer(name='common',modality='physical',scope='macro'),EnvironmentLayer(name='controls',modality='physical',scope='macro'),EnvironmentLayer(name='major_and_social',modality='information',scope='local')])
 pop=PopulationBundle(study_id=study.study_id,provider_ref='phase18.pop',provider_args=args,materialized_count=len(rows),interaction=InteractionStructure(kind='explicit_network',edges=[tuple(e) for e in net['edges'] if set(e)<=ids]))
 sim=SimulationConfig(study_id=study.study_id,n_steps=5,seed=seed,decision_ref='phase18.decision',decision_args={'llm_kind':'scripted','model':None,'max_workers':1,'authorized':False},collector_ref='phase18.metrics',interaction_rounds=1,engine_args={'memory_window':8})
 return study,env,pop,sim

def intervention_events(arm):
 out=[]
 for prop,on in [('public',arm in ['E3','E4']),('feedback',arm in ['E2','E4'])]:
  if on:out.append(ScheduledEvent(at_step=2,target_layer='controls',op='set',property_name=prop,value=True,note=f'enable {prop} at t2; DRAFT'))
 return out
