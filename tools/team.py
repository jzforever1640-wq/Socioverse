"""Team offline entrypoint. Imports no paid transport and blocks network connections."""
from pathlib import Path
import argparse, collections, hashlib, html, importlib.util, json, os, socket, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'studies/controlled_major'
sys.path[:0]=[str(ROOT/'vendor/SocioVerse2'),str(STUDY/'scripts'),str(STUDY/'native')]
def deny(*a,**k):raise RuntimeError('OFFLINE_ONLY_NETWORK_BLOCKED')
socket.socket.connect=deny;socket.socket.connect_ex=deny;socket.create_connection=deny
for key in list(os.environ):
 if any(s in key.upper() for s in ['API_KEY','ACCESS_TOKEN','SECRET_KEY']):os.environ.pop(key,None)
def load(name):return json.loads((ROOT/name).read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 for row in load('shared/MANIFEST.json'):
  assert digest(ROOT/row['path'])==row['sha256'],row['path']
def runner():
 spec=importlib.util.spec_from_file_location('team_native_runner',STUDY/'scripts/run_native_scripted.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test():
 verify()
 baseline=load('shared/scripted/panels.json')
 with tempfile.TemporaryDirectory(prefix='sv2-scripted-') as d:
  out=Path(d)/'run';runner().run(20271001,out)
  summary=json.loads((out/'native_summary.json').read_text());assert summary['real_llm_requests']==0;assert summary['total_panel_rows']==576
  for arm in ['E1','E2','E3','E4']:
   actual=[json.loads(x) for x in (out/f'{arm}_panel_MOCK_ONLY.jsonl').read_text().splitlines()]
   expected=[{k:v for k,v in r.items() if k not in ['arm','data_kind','seed']} for r in baseline if r['arm']==arm]
   assert actual==expected, f'{arm}: panel differs from saved source artifact'
  try:runner().run(20271001,out)
  except FileExistsError:pass
  else:raise AssertionError('Must refuse overwrite')
 # Authorized bank is available locally; loading remains offline and hash checked.
 os.environ.pop('SV2_EJQ_BANK',None)
 from ejq_alignment import items,score_answers
 for form in 'ABCD':
  qs=items(form);assert len(qs)==8
  reply=[{'item_id':q['item_id'],**q['answer_key']} for q in qs]
  assert score_answers(form,reply)['total']==16
 with tempfile.TemporaryDirectory() as d:
  bad=Path(d)/'bank.jsonl';bad.write_text('{}')
  os.environ['SV2_EJQ_BANK']=str(bad)
  try:items('A')
  except ValueError as e:assert 'HASH_MISMATCH' in str(e)
  else:raise AssertionError('Changed bank must fail closed')
  finally:os.environ.pop('SV2_EJQ_BANK',None)
 try:socket.create_connection(('example.invalid',443))
 except RuntimeError:pass
 else:raise AssertionError('Network guard absent')
 print('PASS: 576 exact saved panel comparisons; four-arm invariants; 0 API calls; no API key; authorized 32-item bank checked; overwrite rejected; network blocked.')

def analysis():
 verify();panels=load('shared/scripted/panels.json');exposures=load('shared/scripted/exposures.json')
 agents=load('shared/population.json');ses={a['agent_id']:a['ses_group'] for a in agents}
 result={'data_kind':'SCRIPTED_SOFTWARE_REFERENCE_ONLY','real_pilot':'尚未运行','real_formal':'尚未运行','primary_real':None,'intention_real':None,'ses_real':None,'panels':len(panels),'by_arm':{},'ses_counts':dict(collections.Counter(ses.values())),'network_failure_fallback':False,'ejq_scripted':'MISSING_NOT_ZERO'}
 for arm in ['E1','E2','E3','E4']:
  es=[e for e in exposures if e['arm']==arm]
  result['by_arm'][arm]={'panel_rows':sum(p['arm']==arm for p in panels),'agents':len({p['agent_id'] for p in panels if p['arm']==arm}),'public_exposure_agent_steps':sum(e['public_received'] for e in es),'peer_exposure_agent_steps':sum(e['peer_received'] for e in es),'fixed_F_slots':sum(x['fixed_fallback'] for e in es for x in e['entries'])}
 return result

def report(out):
 result=analysis();panels=load('shared/scripted/panels.json');messages=load('shared/scripted/messages.json');exposures=load('shared/scripted/exposures.json')
 esc=lambda x:html.escape(str(x))
 def table(head,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
 body='<h1>SocioVerse2 · Track B 研究记录</h1><p>只读离线报告 · 2026-10-29 · P1 六卡候选待研究者审批</p><p class="notice">真实六人 Pilot：尚未运行。正式 E1–E4：尚未运行。下方四臂轨迹全部来自 SCRIPTED 软件参考；不得用于真实 Primary 或 SES 效应推断。</p>'
 body+='<h2>已有真实组件测试</h2><p>A001 / t1 / seed 20271001；deepseek-flash；3 次真实请求，输入 6045、输出 610 token，估计费用 ¥0.016970（平台账单未核对）。无重试或 fallback。离线 REPLAY 3 条、0新增调用；仅接口可行性。未暴露 P1，无四臂、纵向或同伴效果证据。单人私有意愿与 EJQ 分数不在共享包。</p>'
 body+='<p>另有首次真实连接诊断1次（输入41、输出5 token，估计 ¥0.000122）。历史真实请求合计4次、估计 ¥0.017092。连接测试不属于 Study 结果；旧预检摘要未更新，以实际完成账本为准。</p>'
 body+='<h2>E1–E4 条件比较</h2>'+table(['条件','P1支持','反馈','真实结果','scripted panel行','同伴暴露 agent-step','固定F补位槽'],[(a,'t2六卡' if a in ['E3','E4'] else '无','开' if a in ['E2','E4'] else '关','尚未运行',r['panel_rows'],r['peer_exposure_agent_steps'],r['fixed_F_slots']) for a,r in result['by_arm'].items()])
 body+='<h2>专业意愿与 SES 分层</h2><p>CS、AUTO、EE、STAT 的真实纵向专业意愿：尚未运行。正式 Primary E3−E1：尚未运行。EJQ scripted 未测量，不能填0；未导出人为 fixture 分数作为结果。</p>'+table(['SES','固定人口','真实动态意愿','真实支持差'],[(g,n,'尚未运行','尚未运行') for g,n in result['ses_counts'].items()])
 body+='<h2>Agent 轨迹 · SCRIPTED</h2><p>按条件、Agent 展开；t0 无动作，t5 idle。分支 t1 的 action_source=replay 来自共同历史，不是新 LLM 调用。</p>'
 ses={a['agent_id']:a['ses_group'] for a in load('shared/population.json')}
 for arm in ['E1','E2','E3','E4']:
  body+='<details><summary>'+arm+' · SCRIPTED · 24 agents</summary>'
  for aid in sorted(ses):
   rows=[p for p in panels if p['arm']==arm and p['agent_id']==aid]
   body+='<details><summary>'+aid+' · '+ses[aid]+'</summary>'+table(['t','动作','动作来源','判断'],[(p['step'],p['action_kind'],p['action_source'],p['action_payload'].get('judgment','')) for p in rows])+'</details>'
  body+='</details>'
 body+='<h2>传播来源链 · SCRIPTED</h2><p>保留实际 item / parent / source refs；F 是空槽固定补位，不是失败后改用 scripted。original_claim_ids 为空，未声称命题级事实核验。</p>'
 for arm in ['E1','E2','E3','E4']:
  ms=[m for m in messages if m['arm']==arm]
  body+='<details><summary>'+arm+' · 帖子与父来源链</summary>'+table(['t','Agent','item_id','parent_ids → item','source_ids / refs'],[(m['step'],m['author_id'],m['card']['item_id'],' + '.join(m['parent_ids'])+' → '+m['card']['item_id'],str(m['source_ids'])+' / '+str(m['source_refs'])) for m in ms])+'</details>'
 body+='<h2>审计与访问</h2><p>数据来自已有 JSONL 的只读筛选，导出与代码 hash 见 shared/MANIFEST.json 和 provenance；完整原始 DuckDB/请求日志仅有 hash 外部索引。没有网络资源、写入操作或公开 Dashboard。新实验导出使用 templates/，审批见 DECISION_LOG.md。</p>'
 page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><title>SocioVerse2 Track B 只读研究报告</title><style>body{font:16px/1.65 system-ui,sans-serif;max-width:1100px;margin:36px auto;padding:0 20px;color:#17343e;background:#f7f8f6}h1,h2{color:#174d58}h2{margin-top:36px}.notice{border-left:5px solid #b96724;padding:14px;background:#fff4e4}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;text-align:left;border-bottom:1px solid #c8d3d5;overflow-wrap:anywhere}th{background:#e3eceb}.scroll{overflow-x:auto}details{margin:9px 0}summary{padding:8px;background:#e5eeee;cursor:pointer}</style><body>'+body+'</body></html>'
 out=Path(out)
 if out.exists():raise FileExistsError('Report exists; choose new path')
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(page);print(out)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['test','analyze','report','scripted']);ap.add_argument('--out',type=Path);a=ap.parse_args()
 if a.command=='test':test()
 elif a.command=='analyze':print(json.dumps(analysis(),ensure_ascii=False,indent=2))
 elif a.command=='report':report(a.out or ROOT/'artifacts-local/report.html')
 else:
  if a.out is None:ap.error('scripted requires a fresh --out')
  runner().run(20271001,a.out)
