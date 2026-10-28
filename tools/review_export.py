"""Review the candidate release; never prints matched secret values."""
from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[1]
files=subprocess.check_output(['git','ls-files'],cwd=R,text=True).splitlines()
if not files:
 files=[str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.git','__pycache__','.venv','artifacts-local','runs']) and not p.name.endswith('.pyc')]
violations=[]
for name in files:
 p=R/name
 if not p.exists():violations.append([name,'missing']);continue
 if p.name.startswith('.env') or p.suffix in ['.duckdb','.parquet','.pem','.key'] or p.name in ['requests.jsonl','EJQ_forms_PRIVATE_DRAFT.jsonl','ANSWER_KEYS.json']:
  violations.append([name,'forbidden artifact'])
 try:t=p.read_text()
 except UnicodeError:violations.append([name,'unreviewed binary']);continue
 rules=[('personal absolute path',r'/(?:Users|home)/[^\s\"\']+'),('credential-shaped value',r'\bsk-[A-Za-z0-9_-]{16,}'),('AWS access identifier',r'\bAKIA[A-Z0-9]{16}\b'),('private key',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
 for label,pattern in rules:
  if re.search(pattern,t):violations.append([name,label])
 if p.suffix=='.json':
  try:obj=json.loads(t)
  except ValueError:violations.append([name,'invalid JSON']);continue
  def walk(x):
   if isinstance(x,dict):
    if 'answer_key' in x or 'tier1_options' in x or 'tier2_options' in x:violations.append([name,'private instrument structure'])
    for v in x.values():walk(v)
   elif isinstance(x,list):
    for v in x:walk(v)
  walk(obj)
for row in json.loads((R/'shared/MANIFEST.json').read_text()):
 if hashlib.sha256((R/row['path']).read_bytes()).hexdigest()!=row['sha256']:violations.append([row['path'],'changed shared snapshot'])
if violations:
 print(json.dumps({'status':'FAIL','violations':violations},ensure_ascii=False,indent=2));raise SystemExit(1)
print(json.dumps({'status':'PASS','files_reviewed':len(files),'scope':'pattern scan, JSON instrument structure, shared snapshot integrity; researcher review still required'},ensure_ascii=False))
