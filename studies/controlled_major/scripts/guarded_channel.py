"""Budget/usage boundary, tested with fake transports only. Never loads credentials on import."""
from pathlib import Path
import json,math,hashlib,threading,time

class GuardedChannel:
 def __init__(self,config,transport,count_tokens,ledger_path):
  for key in ['paid_authorized','human_protocol_approval','human_material_approval','human_measurement_approval','token_counter_verified']:
   if config.get(key) is not True:raise PermissionError('APPROVAL_REQUIRED '+key)
  for key in ['model','provider','exact_model_version']:
   if not config.get(key):raise PermissionError('MODEL_METADATA_REQUIRED '+key)
  self.config=config;self.transport=transport;self.count_tokens=count_tokens;self.path=Path(ledger_path);self.lock=threading.Lock();self.spent=0;self.calls=0;self.retries=0;self.halted=False
  if self.path.exists():raise FileExistsError('new run requires new usage ledger; recovery must reconcile provider billing first')
 def _log(self,obj):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  with self.path.open('a') as f:f.write(json.dumps(obj,ensure_ascii=False)+'\n')
 def invoke(self,prompt,metadata,validator):
  with self.lock:
   if self.halted:raise RuntimeError('RUN_HALTED')
   cfg=self.config;nin=self.count_tokens(prompt)
   if type(nin)!=int or not 0<nin<=cfg.get('max_input_tokens_per_call',4000):raise ValueError('INPUT_TOKEN_CAP')
   output=cfg.get('max_output_tokens_per_call',1000);pi=cfg['price_input_per_million'];po=cfg['price_output_per_million'];reserve=(nin*pi+output*po)/1e6
   maxcalls=cfg.get('max_total_calls',126)
   for attempt in range(2):
    if self.calls>=maxcalls or self.spent+reserve>cfg['max_total_budget_usd']:self.halted=True;raise RuntimeError('BUDGET_OR_CALL_CAP')
    if attempt and self.retries>=cfg.get('max_retry_calls',12):self.halted=True;raise RuntimeError('RETRY_CAP')
    if attempt:self.retries+=1
    self.calls+=1;self.spent+=reserve
    record={'request_index':self.calls,'metadata':metadata,'attempt':attempt,'model_requested':cfg['model'],'provider':cfg['provider'],'timestamp':time.time(),'prompt_sha256':hashlib.sha256(json.dumps(prompt,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'reserved_cost_usd':reserve}
    try:res=self.transport(prompt,cfg['model'],output)
    except Exception as e:
     record.update(status='PROVIDER_FAILURE_UNRECONCILED',error_type=type(e).__name__,charged_conservative_usd=reserve,cumulative_cost_ceiling_usd=self.spent);self._log(record)
     if attempt==0:continue
     self.halted=True;raise RuntimeError('PROVIDER_FAILURE_STOP') from e
    usage=res.get('usage');model=res.get('model');request_id=res.get('request_id')
    if not usage or any(type(usage.get(k))!=int or usage[k]<0 for k in ['input_tokens','output_tokens']) or not model or not request_id:
     record.update(status='MISSING_USAGE_OR_MODEL_STOP',charged_conservative_usd=reserve);self._log(record);self.halted=True;raise RuntimeError('USAGE_METADATA_REQUIRED')
    cost=(usage['input_tokens']*pi+usage['output_tokens']*po)/1e6;self.spent+=cost-reserve
    record.update(usage=usage,model_returned=model,request_id=request_id,actual_cost_at_approved_rates_usd=cost,cumulative_cost_ceiling_usd=self.spent,raw_response=res['text'])
    if model!=cfg['exact_model_version'] or usage['input_tokens']>cfg.get('max_input_tokens_per_call',4000) or usage['output_tokens']>output or self.spent>cfg['max_total_budget_usd']:
     record['status']='VERSION_OR_USAGE_CAP_STOP';self._log(record);self.halted=True;raise RuntimeError('VERSION_OR_USAGE_CAP_STOP')
    if res.get('finish_reason') is not None and res['finish_reason']!='stop':
     record['status']='OUTPUT_FINISH_REASON_STOP';record['finish_reason']=res['finish_reason'];self._log(record);self.halted=True;raise RuntimeError('OUTPUT_TRUNCATED_OR_NONSTOP')
    try:parsed=json.loads(res['text']);validator(parsed)
    except Exception as e:
     record.update(status='PARSE_OR_SCHEMA_FAILURE',error_type=type(e).__name__);self._log(record)
     if attempt==0:continue
     self.halted=True;raise RuntimeError('SCHEMA_FAILURE_STOP') from e
    record['status']='VALID';self._log(record);return parsed


def open_channel(config_path,ledger_path):
 """Real channel factory. Requires model-specific tokenizer approval; not invoked this phase."""
 cfg=json.loads(Path(config_path).read_text())
 # Validate approval before imports, dotenv or credential access.
 for key in ['paid_authorized','human_protocol_approval','human_material_approval','human_measurement_approval','token_counter_verified']:
  if cfg.get(key) is not True:raise PermissionError('APPROVAL_REQUIRED '+key)
 import tiktoken
 encoding=tiktoken.encoding_for_model(cfg['model'])
 def count(prompt):return len(encoding.encode(json.dumps(prompt,ensure_ascii=False)))+128
 def transport(prompt,model,max_output):
  import os
  from socioverse.external_events import _load_dotenv
  _load_dotenv()
  from openai import OpenAI
  client=OpenAI(api_key=os.environ.get('SV_LLM_API_KEY') or os.environ.get('OPENAI_API_KEY'),base_url=os.environ.get('SV_LLM_BASE_URL') or 'https://api.openai.com/v1')
  res=client.chat.completions.create(model=model,messages=[{'role':'user','content':json.dumps(prompt,ensure_ascii=False)}],temperature=0,max_tokens=max_output,response_format={'type':'json_object'})
  return {'text':res.choices[0].message.content,'finish_reason':res.choices[0].finish_reason,'model':res.model,'request_id':res.id,'usage':{'input_tokens':res.usage.prompt_tokens,'output_tokens':res.usage.completion_tokens} if res.usage else None}
 return GuardedChannel(cfg,transport,count,ledger_path)
