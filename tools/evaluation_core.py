# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
INDEX_PATH=ROOT/'evaluations/index.json'
METRIC_ORDER=('provenance_retention','unknown_preservation','conflict_preservation','register_satire_preservation','mrs_interpretation','mode_boundary_discipline','invented_history_penalty')
POSITIVE_METRICS=METRIC_ORDER[:-1]; PENALTY_METRIC=METRIC_ORDER[-1]
CASE_PATHS=tuple(f'evaluations/cases/{i:02d}-{name}.json' for i,name in enumerate(METRIC_ORDER,1))
EXECUTION_KINDS={'synthetic_conformance','model_execution','agent_execution','deterministic_replay'}
OPS={'preserves','equals','absent','subset_of_input'}; MISSING=object()
FAILURES={'INT_EVALUATION_INDEX_INVALID','INT_EVALUATION_CASE_INVALID','INT_EVALUATION_ASSERTION_FAILED','INT_CONSUMER_RUN_INVALID','INT_CONSUMER_RESPONSE_MISSING','INT_EVALUATION_IDENTITY_MISMATCH','INT_EVALUATION_REPORT_INVALID','INT_EVALUATION_COMPARISON_INVALID'}

class EvaluationFailure(ValueError):
 def __init__(self,code:str,message:str): super().__init__(f'{code}: {message}'); self.code=code; self.message=message

def require(ok:bool,code:str,message:str)->None:
 if not ok: raise EvaluationFailure(code,message)
def load_json(path:str|Path,code='INT_EVALUATION_INDEX_INVALID')->Any:
 p=Path(path); p=p if p.is_absolute() else ROOT/p
 try:return json.loads(p.read_text(encoding='utf-8'))
 except (OSError,UnicodeDecodeError,json.JSONDecodeError) as e: raise EvaluationFailure(code,f'cannot read JSON {p}: {e}') from e
def canonical_bytes(v:Any)->bytes:return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def canonical_text(v:Any)->str:return canonical_bytes(v).decode()+'\n'
def canonical_sha256(v:Any)->str:return hashlib.sha256(canonical_bytes(v)).hexdigest()
def _path(v:Any,dotted:str,default=MISSING)->Any:
 for part in dotted.split('.'):
  if not isinstance(v,dict) or part not in v:return default
  v=v[part]
 return v
def _hex(v:Any,n:int)->bool:return isinstance(v,str) and len(v)==n and all(c in '0123456789abcdef' for c in v)

def parent_identity(parents:dict)->dict:
 require(isinstance(parents,dict),'INT_EVALUATION_INDEX_INVALID','parent contract invalid'); registry=parents.get('parents')
 require(isinstance(registry,dict) and set(registry)=={'substrate','ark'},'INT_EVALUATION_INDEX_INVALID','parent registry invalid'); out={}
 for name in ('substrate','ark'):
  p=registry[name]; arts=[p.get('manifest'),*p.get('contracts',[])]
  require(isinstance(p,dict) and all(isinstance(a,dict) for a in arts),'INT_EVALUATION_INDEX_INVALID',f'invalid parent {name}')
  normalized=[]
  for a in sorted(arts,key=lambda x:x.get('path','')):
   require(isinstance(a.get('path'),str) and _hex(a.get('git_blob_sha1'),40),'INT_EVALUATION_INDEX_INVALID',f'invalid parent artifact {name}')
   normalized.append({'path':a['path'],'git_blob_sha1':a['git_blob_sha1']})
  require(isinstance(p.get('protocol'),str) and isinstance(p.get('repository'),str) and _hex(p.get('pinned_commit'),40),'INT_EVALUATION_INDEX_INVALID',f'invalid parent identity {name}')
  out[name]={'protocol':p['protocol'],'repository':p['repository'],'pinned_commit':p['pinned_commit'],'artifacts':normalized}
 return out

def _validate_contract(c:dict)->None:
 require(isinstance(c,dict) and c.get('type')=='qsol-int-consumer-evaluation-contract' and c.get('protocol')=='QSOL-INT/CONSUMER-EVALUATION/1' and c.get('version')=='1.0.0','INT_EVALUATION_INDEX_INVALID','evaluation contract identity invalid')
 require(c.get('status')=='implemented' and c.get('scope')=='exact_fixture_and_pinned_parent_evidence_only' and c.get('derived_noncanonical') is True,'INT_EVALUATION_INDEX_INVALID','evaluation contract boundary invalid')
 policy=c.get('execution_claim_policy',{}); require(policy=={'synthetic_conformance_runs_must_set_claims_execution':False,'model_or_agent_runs_must_declare_execution_kind':True,'self_reported_identity_is_not_authenticated_identity':True},'INT_EVALUATION_INDEX_INVALID','execution policy invalid')
 metrics=c.get('metrics'); require(isinstance(metrics,list) and [m.get('id') for m in metrics if isinstance(m,dict)]==list(METRIC_ORDER),'INT_EVALUATION_INDEX_INVALID','metric registry invalid')
 for m in metrics: require(m.get('kind')==('penalty' if m['id']==PENALTY_METRIC else 'score') and m.get('minimum')==0 and m.get('maximum')==100,'INT_EVALUATION_INDEX_INVALID','metric range invalid')
 rules=c.get('rules'); require(isinstance(rules,list) and len(rules)==len(set(rules)) and {'scores_measure_fixture_conformance_only','comparison_requires_identical_fixture_and_parent_evidence_identity'}.issubset(rules),'INT_EVALUATION_INDEX_INVALID','evaluation rules invalid')
 codes=c.get('failure_codes'); require(isinstance(codes,list) and len(codes)==len(set(codes)) and set(codes)==FAILURES,'INT_EVALUATION_INDEX_INVALID','failure registry invalid')

def _validate_case(c:dict,case_id:str,metric:str)->None:
 require(isinstance(c,dict) and c.get('id')==case_id and c.get('metric')==metric and c.get('synthetic') is True and isinstance(c.get('input'),dict),'INT_EVALUATION_CASE_INVALID',f'invalid case {case_id}')
 assertions=c.get('assertions'); require(isinstance(assertions,list) and assertions,'INT_EVALUATION_CASE_INVALID',f'assertions missing {case_id}')
 for a in assertions:
  require(isinstance(a,dict) and a.get('op') in OPS and isinstance(a.get('output_path'),str) and a['output_path'],'INT_EVALUATION_CASE_INVALID',f'invalid assertion {case_id}')
  if a['op'] in {'preserves','subset_of_input'}: require(isinstance(a.get('input_path'),str) and a['input_path'],'INT_EVALUATION_CASE_INVALID',f'input path missing {case_id}')
  if a['op']=='equals': require('value' in a,'INT_EVALUATION_CASE_INVALID',f'value missing {case_id}')

def validate_index(index:dict|None=None)->tuple[dict,list[dict]]:
 index=load_json(INDEX_PATH) if index is None else index
 require(isinstance(index,dict) and index.get('type')=='qsol-int-consumer-evaluation-index' and index.get('protocol')=='QSOL-INT/CONSUMER-EVALUATION/1' and index.get('version')=='1.0.0','INT_EVALUATION_INDEX_INVALID','index identity invalid')
 require(index.get('scope')=='exact_fixture_and_pinned_parent_evidence_only' and index.get('derived_reports_are_noncanonical') is True,'INT_EVALUATION_INDEX_INVALID','index scope invalid')
 contract=load_json(index.get('contract','')); _validate_contract(contract); require(index.get('contract')=='ai/consumer-evaluation-contract.json' and index.get('contract_sha256')==canonical_sha256(contract),'INT_EVALUATION_INDEX_INVALID','contract receipt invalid')
 parents=load_json(index.get('parent_contract','')); ident=parent_identity(parents)
 require(index.get('parent_contract')=='ai/parent-contracts.json' and index.get('parent_identity')==ident and index.get('parent_identity_sha256')==canonical_sha256(ident),'INT_EVALUATION_INDEX_INVALID','parent identity invalid')
 paths=index.get('cases'); ids=index.get('required_case_ids'); receipts=index.get('case_sha256')
 require(tuple(paths or [])==CASE_PATHS and ids==[f'INT-EVAL-{i:03d}' for i in range(1,8)] and index.get('metrics')==list(METRIC_ORDER),'INT_EVALUATION_INDEX_INVALID','case registry invalid')
 require(isinstance(receipts,dict) and set(receipts)==set(CASE_PATHS),'INT_EVALUATION_INDEX_INVALID','case receipts invalid'); cases=[]
 for path,case_id,metric in zip(CASE_PATHS,ids,METRIC_ORDER):
  case=load_json(path,'INT_EVALUATION_CASE_INVALID'); _validate_case(case,case_id,metric); require(receipts[path]==canonical_sha256(case),'INT_EVALUATION_INDEX_INVALID',f'case receipt invalid {path}'); cases.append(case)
 return index,cases

def validate_run(run:dict,index:dict,cases:list[dict])->dict[str,dict]:
 require(isinstance(run,dict) and run.get('type')=='qsol-int-consumer-run' and run.get('protocol')=='QSOL-INT/CONSUMER-RUN/1' and run.get('version')=='1.0.0','INT_CONSUMER_RUN_INVALID','run identity invalid')
 kind=run.get('execution_kind'); claim=run.get('claims_execution'); require(kind in EXECUTION_KINDS and isinstance(claim,bool),'INT_CONSUMER_RUN_INVALID','execution declaration invalid')
 require(claim is (kind!='synthetic_conformance'),'INT_CONSUMER_RUN_INVALID','execution claim contradicts run kind')
 require(isinstance(run.get('run_id'),str) and run['run_id'],'INT_CONSUMER_RUN_INVALID','run id missing'); subject=run.get('subject')
 require(isinstance(subject,dict) and all(isinstance(subject.get(k),str) and subject[k] for k in ('kind','id','version','identity_authentication')),'INT_CONSUMER_RUN_INVALID','subject invalid')
 fixture=run.get('fixture_identity',{}); require(fixture.get('evaluation_index_sha256')==canonical_sha256(index) and fixture.get('parent_identity_sha256')==index['parent_identity_sha256'],'INT_EVALUATION_IDENTITY_MISMATCH','run identity mismatch')
 allowed={c['id'] for c in cases}; responses=run.get('responses'); require(isinstance(responses,list),'INT_CONSUMER_RUN_INVALID','responses invalid'); out={}
 for item in responses:
  cid=item.get('case_id') if isinstance(item,dict) else None; require(cid in allowed and cid not in out and isinstance(item.get('output'),dict),'INT_CONSUMER_RUN_INVALID',f'invalid response {cid}'); out[cid]=item['output']
 return out

def _assert(case_input:dict,output:dict,a:dict)->tuple[bool,str]:
 actual=_path(output,a['output_path']); op=a['op']
 if op=='absent':return actual is MISSING,f"expected {a['output_path']} absent"
 if actual is MISSING:return False,f"missing {a['output_path']}"
 if op=='equals':return actual==a['value'],f"expected {a['output_path']}={a['value']!r}"
 expected=_path(case_input,a['input_path']);
 if expected is MISSING:return False,f"missing fixture {a['input_path']}"
 if op=='preserves':return actual==expected,f"failed to preserve {a['input_path']}"
 ok=isinstance(expected,list) and isinstance(actual,list) and all(isinstance(x,str) for x in expected+actual) and set(actual).issubset(expected)
 return ok,f"unsupported item in {a['output_path']}"

def evaluate_run(run:dict,index:dict|None=None,cases:list[dict]|None=None)->dict:
 if index is None or cases is None:index,cases=validate_index(index)
 responses=validate_run(run,index,cases); case_results=[]; metrics={}
 for case in cases:
  output=responses.get(case['id']); failures=[]
  if output is None: failures=[{'code':'INT_CONSUMER_RESPONSE_MISSING','message':'consumer response is missing'}]
  else:
   for a in case['assertions']:
    ok,msg=_assert(case['input'],output,a)
    if not ok: failures.append({'code':'INT_EVALUATION_ASSERTION_FAILED','message':msg,'assertion':a})
  passed=not failures; metric=case['metric']
  if metric==PENALTY_METRIC:value=0 if passed else 100; metrics[metric]={'kind':'penalty','penalty':value,'passed_cases':int(passed),'total_cases':1}; score={'penalty':value}
  else:value=100 if passed else 0; metrics[metric]={'kind':'score','score':value,'passed_cases':int(passed),'total_cases':1}; score={'score':value}
  case_results.append({'id':case['id'],'metric':metric,'result':'pass' if passed else 'fail',**score,'failure_count':len(failures),'failures':failures})
 positive=sum(metrics[m]['score'] for m in POSITIVE_METRICS); average=positive//len(POSITIVE_METRICS); penalty=metrics[PENALTY_METRIC]['penalty']
 report={'type':'qsol-int-consumer-evaluation-report','protocol':'QSOL-INT/CONSUMER-EVALUATION/1','version':'1.0.0','derived_noncanonical':True,'authority':{'score_is_fixture_conformance_only':True,'report_is_parent_or_source_evidence':False,'report_establishes_general_model_quality':False},'evaluation_identity':{'index':'evaluations/index.json','evaluation_index_sha256':canonical_sha256(index),'contract':index['contract'],'contract_sha256':index['contract_sha256'],'parent_identity':index['parent_identity'],'parent_identity_sha256':index['parent_identity_sha256']},'run':{'run_id':run['run_id'],'execution_kind':run['execution_kind'],'claims_execution':run['claims_execution'],'subject':run['subject'],'manifest_sha256':canonical_sha256(run)},'metrics':metrics,'case_results':case_results,'summary':{'positive_score_sum':positive,'positive_metric_count':len(POSITIVE_METRICS),'positive_score_average':average,'invented_history_penalty':penalty,'overall_score':max(0,average-penalty),'passed_cases':sum(x['result']=='pass' for x in case_results),'failed_cases':sum(x['result']=='fail' for x in case_results)}}
 report['fingerprint_sha256']=canonical_sha256(report); return report

def validate_report(report:dict,run:dict|None=None)->None:
 require(isinstance(report,dict) and report.get('type')=='qsol-int-consumer-evaluation-report' and report.get('protocol')=='QSOL-INT/CONSUMER-EVALUATION/1' and report.get('version')=='1.0.0' and report.get('derived_noncanonical') is True,'INT_EVALUATION_REPORT_INVALID','report identity invalid')
 fp=report.get('fingerprint_sha256'); unsigned=dict(report); unsigned.pop('fingerprint_sha256',None); require(_hex(fp,64) and fp==canonical_sha256(unsigned),'INT_EVALUATION_REPORT_INVALID','report fingerprint invalid')
 ident=report.get('evaluation_identity',{}); require(isinstance(ident.get('parent_identity'),dict) and ident.get('parent_identity_sha256')==canonical_sha256(ident['parent_identity']),'INT_EVALUATION_REPORT_INVALID','parent identity receipt invalid')
 metrics=report.get('metrics'); require(isinstance(metrics,dict) and set(metrics)==set(METRIC_ORDER),'INT_EVALUATION_REPORT_INVALID','metric registry invalid'); summary=report.get('summary',{})
 require(summary.get('overall_score')==max(0,sum(metrics[m]['score'] for m in POSITIVE_METRICS)//6-metrics[PENALTY_METRIC]['penalty']),'INT_EVALUATION_REPORT_INVALID','score summary invalid')
 if run is not None: require(report==evaluate_run(run),'INT_EVALUATION_REPORT_INVALID','report regeneration mismatch')

def compare_reports(left:dict,right:dict)->dict:
 validate_report(left); validate_report(right); require(left['evaluation_identity']==right['evaluation_identity'],'INT_EVALUATION_IDENTITY_MISMATCH','report identities differ')
 deltas={}
 for m in METRIC_ORDER:
  field='penalty' if m==PENALTY_METRIC else 'score'; a=left['metrics'][m][field]; b=right['metrics'][m][field]; deltas[m]={'left':a,'right':b,'right_minus_left':b-a}
 a=left['summary']['overall_score']; b=right['summary']['overall_score']; winner='tie' if a==b else ('left' if a>b else 'right')
 out={'type':'qsol-int-consumer-evaluation-comparison','protocol':'QSOL-INT/CONSUMER-EVALUATION/1','version':'1.0.0','derived_noncanonical':True,'authority':{'comparison_scope':'exact_fixture_and_parent_evidence_identity_only','comparison_establishes_general_model_quality':False},'evaluation_identity':left['evaluation_identity'],'left':{'run':left['run'],'report_fingerprint_sha256':left['fingerprint_sha256'],'overall_score':a},'right':{'run':right['run'],'report_fingerprint_sha256':right['fingerprint_sha256'],'overall_score':b},'metric_deltas':deltas,'winner_by_overall_fixture_score':winner}; out['fingerprint_sha256']=canonical_sha256(out); return out

def validate_comparison(c:dict,left:dict|None=None,right:dict|None=None)->None:
 require(isinstance(c,dict) and c.get('type')=='qsol-int-consumer-evaluation-comparison' and c.get('protocol')=='QSOL-INT/CONSUMER-EVALUATION/1' and c.get('version')=='1.0.0' and c.get('derived_noncanonical') is True,'INT_EVALUATION_COMPARISON_INVALID','comparison identity invalid')
 fp=c.get('fingerprint_sha256'); unsigned=dict(c); unsigned.pop('fingerprint_sha256',None); require(_hex(fp,64) and fp==canonical_sha256(unsigned),'INT_EVALUATION_COMPARISON_INVALID','comparison fingerprint invalid')
 if left is not None and right is not None: require(c==compare_reports(left,right),'INT_EVALUATION_COMPARISON_INVALID','comparison regeneration mismatch')
