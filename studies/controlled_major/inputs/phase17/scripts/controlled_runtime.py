"""Offline-only controlled preference adapter. No model SDK or network dependency."""
from pathlib import Path
import copy, hashlib, json, math, re
ROOT=Path(__file__).resolve().parents[1]
IDS=['CS','AUTO','EE','STAT']
SCENARIO=json.loads((ROOT/'config/scenario.json').read_text())
EXPERIMENT=json.loads((ROOT/'config/experiment.json').read_text())
BASE_FIELDS=['cs_interest','programming_interest','initial_cs_knowledge','risk_attitude','risk_tolerance','initial_major_preferences','alternative_interests','initial_risk_perception','knowledge_inventory','unknown_information','career_goal','background']
RESOURCE_FIELDS=['family_resources','parent_education','highest_parent_education','parent_he_familiarity','career_information','financial_constraints']
KINDS={'shock','static','public','neutral_control','peer'}

def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(x): return hashlib.sha256(canon(x).encode()).hexdigest()
def load_roster(): return [json.loads(x) for x in (ROOT/'population/source_roster_DRAFT.jsonl').read_text().splitlines()]
def project(row):
    """Construct fresh agent context by nested allowlist; never merge old memory/state."""
    fixed=row['fixed']; base=fixed['base_profile']; resources=fixed['ses_resources']
    b={k:copy.deepcopy(base[k]) for k in BASE_FIELDS}
    # Nested projections prevent new hidden metadata from hitchhiking.
    r={k:copy.deepcopy(resources[k]) for k in RESOURCE_FIELDS[:4]}
    r['career_information']={k:resources['career_information'][k] for k in ['can_consult_relative','channel_level','family_pathway_familiarity','industry_experience_access']}
    r['financial_constraints']={k:resources['financial_constraints'][k] for k in ['annual_education_budget_cny','extra_annual_education_capacity_cny','income_uncertainty_runway_months','budget_scope','budget_level','tuition_sensitivity','aid_consideration','other_constraints']}
    return {'personal_interests':b,'family_context':r,'regional_background':'安徽背景的合成考生；不代表该省考生总体'}

def display_order(row):
    i=(int(row['fixed']['base_template_id'].split('_')[1])-1)%4
    return IDS[i:]+IDS[:i]

def validate_material(m):
    if set(m)!={'id','kind','body','source_ids','status'}: raise ValueError('material fields')
    if m['kind'] not in KINDS-{'peer'} or not isinstance(m['body'],str) or not m['body'] or len(m['body'])>180: raise ValueError('material payload')
    if m['status']!='MOCK_ONLY': raise ValueError('offline fixture only; formal ingestion requires separate review')
    if not isinstance(m['source_ids'],list) or not all(isinstance(x,str) for x in m['source_ids']): raise ValueError('source ids')

def permitted(m,arm,step):
    kind=m['kind']
    if kind=='shock': return step==1
    if kind=='static': return step in [2,3,4]
    if kind=='public': return step==2 and EXPERIMENT['conditions'][arm]['public_evidence']
    if kind=='neutral_control': return step==2 and not EXPERIMENT['conditions'][arm]['public_evidence']
    return False

def observation(row,step,arm,feed):
    if step in [0,1] and arm!='COMMON': raise ValueError('common history must be computed once')
    if step>=2 and arm not in EXPERIMENT['conditions']: raise ValueError('unknown arm')
    if step not in range(6): raise ValueError('unknown step')
    visible=[]
    for m in feed:
        if m['kind']=='peer':
            if step not in [2,3,4] or not EXPERIMENT['conditions'][arm]['dynamic_feedback'] or m['created_step']!=step-1 or m['arm'] not in [arm,'COMMON']: raise ValueError('peer isolation/delay')
        elif not permitted(m,arm,step): raise ValueError('early/incorrect exposure')
        if not isinstance(m['body'],str) or len(m['body'])>180: raise ValueError('feed budget')
        visible.append({'content_id':m['id'],'body':m['body'],'source_ids':m['source_ids']})
    cards={c['major_id']:{k:v for k,v in c.items()} for c in SCENARIO['cards']}
    # No branch labels, SES group, study outcomes, keys, source pages, raw IDs or old state.
    return {'common_scenario':copy.deepcopy(SCENARIO['common']),'persona':project(row),'major_cards':[cards[i] for i in display_order(row)],'visible_feed':visible}

def guard_context(obs):
    text=canon(obs)
    if re.search(r'(?<!\d)600(?!\d)|28,?600|29,?273|predicted_score|academic_performance|eligibility_status|专业组|录取位次|桂林电子科技|成都信息工程|安徽师范|answer_key|ses_group',text):
        raise ValueError('legacy/private contamination in visible context')
    return obs

def measurement_request(obs):
    return {'read_only_context':copy.deepcopy(obs),'prompt':copy.deepcopy(SCENARIO['measurement_prompt']),'risk_prompt_after_intention':copy.deepcopy(SCENARIO['risk_prompt'])}

def number(x,lo=0,hi=100): return type(x) in [int,float] and math.isfinite(x) and lo<=x<=hi

def validate_response(x):
    if set(x)!={'scores','first_choices','explanation','employment_risk_cs','ejq'}: raise ValueError('unexpected response fields')
    if set(x['scores'])!=set(IDS): raise ValueError('all four independent scores required')
    for v in x['scores'].values():
        if v is not None and not number(v): raise ValueError('score outside scale/type')
    if not isinstance(x['first_choices'],list) or len(set(x['first_choices']))!=len(x['first_choices']) or any(i not in IDS for i in x['first_choices']): raise ValueError('first choices')
    if not isinstance(x['explanation'],str): raise ValueError('explanation')
    risk=x['employment_risk_cs']
    if risk is not None and not number(risk): raise ValueError('risk')
    ejq=x['ejq']
    if ejq is not None:
        if set(ejq)!={'form_id','item_scores','total'} or ejq['form_id'] not in ['A','B','C','D'] or len(ejq['item_scores'])!=8: raise ValueError('EJQ form')
        if any(type(v)!=int or v not in [0,1,2] for v in ejq['item_scores']): raise ValueError('EJQ items')
        if ejq['total']!=sum(ejq['item_scores']): raise ValueError('EJQ sum')

def flags(previous,current):
    f=[]
    a=current['scores']
    if previous:
        p=previous['scores']
        if a==p: f.append('UNCHANGED_VECTOR_REVIEW_NOT_INVALID')
        if all(a[i] is not None and p[i] is not None for i in IDS):
            d=[a[i]-p[i] for i in IDS]
            if all(v>=40 for v in d) or all(v<=-40 for v in d): f.append('SYNCHRONOUS_EXTREME_CHANGE_REVIEW')
    if all(v is not None for v in a.values()) and current['first_choices']:
        if any(a[i]<max(a.values()) for i in current['first_choices']): f.append('FIRST_CHOICE_SCORE_DISCORDANCE_REVIEW')
    if current['explanation']: f.append('TEXT_SCORE_ALIGNMENT_REQUIRES_BLIND_REVIEW')
    return f

def delta(a,b):
    if any(a[i] is None or b[i] is None for i in IDS): return {'status':'MISSING_PAIR','vector':None,'cs_change':None}
    v={i:b[i]-a[i] for i in IDS}
    return {'status':'VALID_PAIR_DESCRIPTIVE','vector':v,'cs_change':v['CS'],'cs_gap_change':(b['CS']-sum(b[i] for i in IDS[1:])/3)-(a['CS']-sum(a[i] for i in IDS[1:])/3)}

class MockAgent:
    version='MOCK_ONLY_NO_COGNITIVE_VALIDITY'
    def evaluate(self,request,row,step):
        # Tests include unchanged, up and down changes; no SES/arm success rule.
        i=int(row['fixed']['agent_id'][1:]); rank=row['fixed']['base_profile']['initial_major_preferences']
        scores={m:70-10*rank.index(m) for m in IDS}
        if i%3:
            scores['CS']+=(i%3*2-3)*(step%3)
        return {'scores':scores,'first_choices':[m for m in IDS if scores[m]==max(scores.values())],'explanation':'仅供接口测试的确定性数值；不是认知或干预结果。','employment_risk_cs':50,'ejq':None}

def fixtures():
    def mat(i,k,text): return {'id':i,'kind':k,'body':text,'source_ids':['FIXTURE_'+i],'status':'MOCK_ONLY'}
    return {'shock':[mat('SH'+str(i),'shock','MOCK：共同刺激占位，非正式舆论材料。') for i in range(4)],'static':[mat('ST'+str(i),'static','MOCK：静态信息流占位。') for i in range(4)],'public':[mat('PU'+str(i),'public','MOCK：公共支持占位，非审核证据。') for i in range(3)],'neutral_control':[mat('NC'+str(i),'neutral_control','MOCK：中性对照占位。') for i in range(3)]}

def run_mock(seed=20271001):
    roster=load_roster(); net=json.loads((ROOT/f'population/network_{seed}.json').read_text()); materials=fixtures()
    for group in materials.values():
        for m in group: validate_material(m)
    agent=MockAgent();records=[];obslog=[];messages=[];exposures=[];checkpoints=[]
    oldhash=hashlib.sha256((ROOT/'population/source_roster_DRAFT.jsonl').read_bytes()).hexdigest()
    def eval_step(step,arm,feeds,history):
        observations={r['fixed']['agent_id']:observation(r,step,arm,feeds[r['fixed']['agent_id']]) for r in roster}
        for aid,obs in observations.items():
            obs['visible_history']=copy.deepcopy(history.get('_visible',{}).get(aid,[]))
            guard_context(obs)
        # All observations constructed before any evaluation/action.
        answers={}
        for row in roster:
            aid=row['fixed']['agent_id'];obs=observations[aid];before=digest(obs)
            stage={v:k for k,v in EXPERIMENT['measurement_stages'].items()}.get(step)
            eid=f'{seed}/{arm}/{step}/{aid}'
            ev={'exposure_event_id':eid,'seed':seed,'arm':arm,'step':step,'agent_id':aid,'content_ids':[m['id'] for m in feeds[aid]],'public_received':any(m['kind']=='public' for m in feeds[aid]),'dynamic_received':any(m['kind']=='peer' for m in feeds[aid])}
            history.setdefault('_public',{})[aid]=history.get('_public',{}).get(aid,False) or ev['public_received']
            history.setdefault('_dynamic',{})[aid]=history.get('_dynamic',{}).get(aid,False) or ev['dynamic_received']
            exposures.append(ev);obslog.append({'event_id':eid,'observation':obs,'observation_sha256':before})
            # Behavioral decision here is a fixture post, no feedback from private evaluation.
            body='MOCK：转述此前可见内容，仅供父帖和来源链测试。'
            post={'id':f'MSG/{eid}','kind':'peer','body':body,'source_ids':sorted({s for m in feeds[aid] for s in m['source_ids']}),'parent_ids':[m['id'] for m in feeds[aid]],'original_claim_ids':sorted({s for m in feeds[aid] for s in m['source_ids'] if s.startswith('FIXTURE_SH')}),'created_step':step,'arm':arm,'author':aid,'seed':seed,'added_interpretation':'MOCK_CHAIN_ONLY','factual_audit':'NOT_CODED_MOCK','unsupported_extrapolation':'NOT_CODED_MOCK'}
            if step in [1,2,3,4]: messages.append(post)
            if stage:
                req=measurement_request(obs);result=agent.evaluate(req,row,step);validate_response(result)
                previous=history.get(aid)
                rec={'scenario_id':SCENARIO['scenario_id'],'schema_version':'1.0-DRAFT','run_id':f'MOCK/{seed}','data_kind':'MOCK_ONLY','seed':seed,'population_seed':row['fixed']['population_seed'],'agent_id':aid,'base_template_id':row['fixed']['base_template_id'],'ses_group':row['fixed']['ses_group'],'network_id':net['network_id'],'arm':arm,'stage_id':stage,'step':step,'measurement_status':'VALID','scores':result['scores'],'score_missing_reasons':{i:None for i in IDS},'first_choices':result['first_choices'],'first_choice_status':'TIED' if len(result['first_choices'])>1 else 'SELECTED','explanation':result['explanation'],'employment_risk_cs':result['employment_risk_cs'],'risk_missing_reason':None,'ejq':None,'ejq_missing_reason':'NOT_EXECUTED_MOCK','public_exposure_status':'RECEIVED' if history['_public'][aid] else 'NOT_EXPOSED','feedback_exposure_status':'RECEIVED' if history['_dynamic'][aid] else 'NOT_EXPOSED','endpoint_context':EXPERIMENT['T3_interpretation'].get(arm) if step==5 else None,'exposure_event_id':eid,'received_history_ids':list(history.get('_events',{}).get(aid,[]))+[eid],'display_order':display_order(row),'prompt_sha256':digest(SCENARIO['measurement_prompt']),'risk_prompt_sha256':digest(SCENARIO['risk_prompt']),'scenario_sha256':digest(SCENARIO),'population_sha256':oldhash,'network_sha256':digest(net),'checkpoint_sha256':None,'observation_sha256':before,'model_version':agent.version,'prompt_version':SCENARIO['measurement_prompt']['version'],'audit_flags':flags(previous,result)}
                records.append(rec);answers[aid]=result
            if digest(obs)!=before: raise AssertionError('measurement mutated context')
        history.update(answers)
        history.setdefault('_events',{})
        for aid,obs in observations.items():
            history['_events'].setdefault(aid,[]).append(f'{seed}/{arm}/{step}/{aid}')
            history.setdefault('_visible',{}).setdefault(aid,[]).extend(copy.deepcopy(obs['visible_feed']))
    empty={r['fixed']['agent_id']:[] for r in roster};history={}
    eval_step(0,'COMMON',empty,history)
    eval_step(1,'COMMON',{a:materials['shock'] for a in empty},history)
    checkpoint={'behavioral_history':{k:copy.deepcopy(v) for k,v in history.items() if k.startswith('_')},'observations':copy.deepcopy(obslog),'actions':copy.deepcopy(messages),'pending_queue':copy.deepcopy(messages),'network':net,'static_schedule':materials['static'],'persona_contexts':{r['fixed']['agent_id']:project(r) for r in roster},'scenario':SCENARIO,'rng_policy':'deterministic fixtures','model_version':agent.version}
    cph=digest(checkpoint);checkpoints.append({'seed':seed,'checkpoint_sha256':cph,'payload':checkpoint})
    for rec in records: rec['checkpoint_sha256']=cph
    common_posts=[m for m in messages if m['arm']=='COMMON' and m['created_step']==1]
    for arm,condition in EXPERIMENT['conditions'].items():
        branch_history=copy.deepcopy(history);queue=copy.deepcopy(common_posts)
        for step in [2,3,4]:
            feeds={}
            for aid in empty:
                social=[]
                for slot,neighbor in enumerate(net['ordered_neighbors'][aid]):
                    choices=[m for m in queue if m['author']==neighbor and m['created_step']==step-1]
                    social.append(copy.deepcopy(choices[0]) if condition['dynamic_feedback'] and choices else copy.deepcopy(materials['static'][slot]))
                feeds[aid]=social+(copy.deepcopy(materials['public' if condition['public_evidence'] else 'neutral_control']) if step==2 else [])
            eval_step(step,arm,feeds,branch_history)
            queue=[m for m in messages if m['arm']==arm and m['created_step']==step]
        eval_step(5,arm,empty,branch_history)
        for rec in records:
            if rec['arm']==arm: rec['checkpoint_sha256']=cph
        if digest(checkpoint)!=cph: raise AssertionError('branch changed prefork checkpoint')
    changes=[]
    for row in roster:
        aid=row['fixed']['agent_id'];common={r['stage_id']:r for r in records if r['agent_id']==aid and r['arm']=='COMMON'}
        changes.append({'seed':seed,'agent_id':aid,'arm':'COMMON','from':'T0','to':'T1',**delta(common['T0']['scores'],common['T1']['scores'])})
        for arm in EXPERIMENT['conditions']:
            stages={r['stage_id']:r for r in records if r['agent_id']==aid and r['arm']==arm}
            for a,b in [('T1','T2'),('T1','T3'),('T2','T3')]:
                ra=common[a] if a=='T1' else stages[a]
                changes.append({'seed':seed,'agent_id':aid,'arm':arm,'from':a,'to':b,**delta(ra['scores'],stages[b]['scores'])})
    return {'records':records,'exposures':exposures,'messages':messages,'observations':obslog,'checkpoints':checkpoints,'changes':changes}

def run(mode='mock'):
    if mode!='mock': raise RuntimeError('NO-GO: this adapter implements offline mock only')
    results=[run_mock(s) for s in EXPERIMENT['seeds']]
    for key in results[0]:
        out=ROOT/'validation'/f'mock_{key}.jsonl'
        out.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for result in results for r in result[key]))
    return {key:sum(len(x[key]) for x in results) for key in results[0]}


def audit_trace(trace):
    """Replay saved deliveries/checkpoint identities, without agent calls."""
    byobs={x['event_id']:x for x in trace['observations']}
    bymsg={x['id']:x for x in trace['messages']}
    static_ids={m['id'] for group in fixtures().values() for m in group}
    cps={x['seed']:x for x in trace['checkpoints']}
    exposure_map={x['exposure_event_id']:x for x in trace['exposures']}
    for cp in cps.values():
        if digest(cp['payload'])!=cp['checkpoint_sha256']: raise ValueError('checkpoint mismatch')
    for e in trace['exposures']:
        ob=byobs[e['exposure_event_id']]
        if digest(ob['observation'])!=ob['observation_sha256']: raise ValueError('observation mismatch')
        if e['content_ids']!=[x['content_id'] for x in ob['observation']['visible_feed']]: raise ValueError('delivery mismatch')
        net=cps[e['seed']]['payload']['network']
        for mid in e['content_ids']:
            if mid in bymsg:
                m=bymsg[mid]
                if e['arm'] not in ['E2','E4'] or m['arm'] not in [e['arm'],'COMMON'] or m['seed']!=e['seed'] or m['created_step']!=e['step']-1 or m['author'] not in net['ordered_neighbors'][e['agent_id']]: raise ValueError('replay routing/delay violation')
            elif mid not in static_ids: raise ValueError('unknown content')
        pub=any(mid.startswith('PU') for mid in e['content_ids'])
        dyn=any(mid in bymsg for mid in e['content_ids'])
        if pub!=e['public_received'] or dyn!=e['dynamic_received']: raise ValueError('exposure flags')
        if pub and (e['step']!=2 or e['arm'] not in ['E3','E4']): raise ValueError('public leakage')
        for v in ob['observation']['visible_history']:
            if v['content_id'].startswith('PU') and (e['step']<=2 or e['arm'] not in ['E3','E4']): raise ValueError('history public leakage')
        guard_context(ob['observation'])
    for m in bymsg.values():
        if any(p not in bymsg and p not in static_ids for p in m['parent_ids']): raise ValueError('unknown parent')
        parent_sources={s for pid in m['parent_ids'] for s in (bymsg[pid]['source_ids'] if pid in bymsg else next(v['source_ids'] for g in fixtures().values() for v in g if v['id']==pid))}
        if set(m['source_ids'])!=parent_sources: raise ValueError('source chain mismatch')
    seen=set()
    for r in trace['records']:
        key=(r['seed'],r['arm'],r['stage_id'],r['agent_id'])
        if key in seen: raise ValueError('duplicate outcome')
        seen.add(key)
        if r['checkpoint_sha256']!=cps[r['seed']]['checkpoint_sha256']: raise ValueError('outcome checkpoint mismatch')
        if r['observation_sha256']!=byobs[r['exposure_event_id']]['observation_sha256']: raise ValueError('outcome observation mismatch')
        events=[exposure_map[eid] for eid in r['received_history_ids']]
        if any(e['agent_id']!=r['agent_id'] or e['seed']!=r['seed'] or e['arm'] not in [r['arm'],'COMMON'] or e['step']>r['step'] for e in events): raise ValueError('outcome history isolation')
        for status,field in [('public_exposure_status','public_received'),('feedback_exposure_status','dynamic_received')]:
            if (r[status]=='RECEIVED')!=any(e[field] for e in events): raise ValueError('cumulative exposure mismatch')
    return {'status':'PASS_SAVED_FIXTURE_REPLAY','outcomes':len(seen),'agent_calls':0}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--mode',default='mock');args=parser.parse_args()
    print(json.dumps(run(args.mode),ensure_ascii=False))
