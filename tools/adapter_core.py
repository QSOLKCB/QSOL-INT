# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]; INDEX_PATH=ROOT/'adapters/index.json'; PARENT_PATH=ROOT/'ai/parent-contracts.json'
ADAPTERS=('generic','openai','ollama'); FIXTURES=('valid','unknown','conflict','satire','cross-mode','missing-provenance','drift','invalid'); FIXTURE_PATHS=tuple(f'adapters/fixtures/{x}.json' for x in FIXTURES)
ANNOTATIONS={'epistemic_state','claim_maturity','scenario','register','provenance','mode','drift'}; DRIFT={'NO_DRIFT','CONTENT_DRIFT','SCHEMA_DRIFT','SEMANTIC_DRIFT','CAPABILITY_DRIFT','AUTHORITY_DRIFT','BREAKING_DRIFT','SOURCE_UNAVAILABLE'}
FAILURES={'INT_ADAPTER_CONTRACT_INVALID','INT_ADAPTER_INDEX_INVALID','INT_ADAPTER_FIXTURE_INVALID','INT_ADAPTER_ENVELOPE_INVALID','INT_ADAPTER_PROVENANCE_REQUIRED','INT_ADAPTER_CONFLICT_PROVENANCE_INCOMPLETE','INT_CROSS_MODE_BRIDGE_REQUIRED','INT_ADAPTER_DRIFT_REVIEW_REQUIRED','INT_ADAPTER_SEMANTIC_LOSS','INT_ADAPTER_REPORT_INVALID','INT_ADAPTER_UNKNOWN'}
class AdapterFailure(ValueError):
 def __init__(self,code,message,decision='reject'):super().__init__(f'{code}: {message}');self.code=code;self.message=message;self.decision=decision
def require(ok,code,message,decision='reject'):
 if not ok:raise AdapterFailure(code,message,decision)
def load_json(path,code='INT_ADAPTER_INDEX_INVALID'):
 p=Path(path);p=p if p.is_absolute() else ROOT/p
 try:return json.loads(p.read_text(encoding='utf-8'))
 except (OSError,UnicodeDecodeError,json.JSONDecodeError) as e:raise AdapterFailure(code,f'cannot read JSON {p}: {e}') from e
def canonical_bytes(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def canonical_text(v):return canonical_bytes(v).decode()+'\n'
def canonical_sha256(v):return hashlib.sha256(canonical_bytes(v)).hexdigest()
def _hex(v,n):return isinstance(v,str) and len(v)==n and all(c in '0123456789abcdef' for c in v)
def _contract(c):
 require(isinstance(c,dict) and c.get('type')=='qsol-int-adapter-contract' and c.get('protocol')=='QSOL-INT/ADAPTER/1' and c.get('version')=='1.0.0' and c.get('status')=='implemented','INT_ADAPTER_CONTRACT_INVALID','contract identity invalid')
 require(c.get('adapters')==list(ADAPTERS) and set(c.get('canonical_envelope',{}).get('required_annotations',[]))==ANNOTATIONS,'INT_ADAPTER_CONTRACT_INVALID','adapter registry invalid')
 a=c.get('authority',{});require(a=={'adapters_are_transport_only':True,'adapter_output_is_source_evidence':False,'adapter_may_redefine_parent_semantics':False,'runtime_model_identity_is_configuration_not_int_fact':True},'INT_ADAPTER_CONTRACT_INVALID','authority boundary invalid')
 rules=c.get('rules');require(isinstance(rules,list) and len(rules)==len(set(rules)) and {'messages_and_annotations_are_preserved_exactly','material_cross_mode_inference_requires_a_declared_bridge','transport_templates_embed_no_api_keys','adapter_receipts_prove_serialization_identity_not_truth_authorship_or_compatibility'}.issubset(rules),'INT_ADAPTER_CONTRACT_INVALID','rules invalid')
 codes=c.get('failure_codes');require(isinstance(codes,list) and len(codes)==len(set(codes)) and set(codes)==FAILURES,'INT_ADAPTER_CONTRACT_INVALID','failure registry invalid')
def validate_index(index=None):
 index=load_json(INDEX_PATH) if index is None else index
 require(isinstance(index,dict) and index.get('type')=='qsol-int-adapter-fixture-index' and index.get('protocol')=='QSOL-INT/ADAPTER/1' and index.get('version')=='1.0.0','INT_ADAPTER_INDEX_INVALID','index identity invalid')
 require(index.get('adapters')==list(ADAPTERS) and index.get('derived_reports_are_noncanonical') is True,'INT_ADAPTER_INDEX_INVALID','index boundary invalid');c=load_json(index.get('contract',''),'INT_ADAPTER_CONTRACT_INVALID');_contract(c)
 require(index.get('contract')=='ai/adapter-contract.json' and index.get('contract_sha256')==canonical_sha256(c),'INT_ADAPTER_INDEX_INVALID','contract receipt invalid')
 paths=index.get('fixtures');receipts=index.get('fixture_sha256');expected=index.get('expected');require(tuple(paths or [])==FIXTURE_PATHS and set(index.get('required_fixture_kinds',[]))==set(FIXTURES),'INT_ADAPTER_INDEX_INVALID','fixture registry invalid')
 require(isinstance(receipts,dict) and set(receipts)==set(paths) and isinstance(expected,dict) and set(expected)==set(paths),'INT_ADAPTER_INDEX_INVALID','fixture metadata invalid');out=[]
 for path in paths:
  f=load_json(path,'INT_ADAPTER_FIXTURE_INVALID');require(receipts[path]==canonical_sha256(f),'INT_ADAPTER_INDEX_INVALID',f'fixture receipt invalid {path}');e=expected[path];require(isinstance(e,dict) and e.get('decision') in {'allow','block','reject'} and 'failure_code' in e,'INT_ADAPTER_INDEX_INVALID',f'fixture outcome invalid {path}');out.append((path,f,e))
 return index,out
def _registries():
 s=load_json(PARENT_PATH,'INT_ADAPTER_CONTRACT_INVALID').get('parents',{}).get('substrate',{});values=tuple(set(s.get(k,[])) for k in ('observed_epistemic_states','observed_claim_maturity_states','observed_scenario_states','observed_register_states'));require(all(values),'INT_ADAPTER_CONTRACT_INVALID','parent registries missing');return values
def validate_envelope(e):
 require(isinstance(e,dict) and e.get('type')=='qsol-int-adapter-envelope' and e.get('protocol')=='QSOL-INT/ADAPTER/1' and e.get('version')=='1.0.0' and isinstance(e.get('id'),str) and e['id'],'INT_ADAPTER_ENVELOPE_INVALID','envelope identity invalid')
 messages=e.get('messages');require(isinstance(messages,list) and messages,'INT_ADAPTER_ENVELOPE_INVALID','messages missing')
 for m in messages:require(isinstance(m,dict) and isinstance(m.get('role'),str) and isinstance(m.get('content'),str),'INT_ADAPTER_ENVELOPE_INVALID','message invalid')
 a=e.get('annotations');require(isinstance(a,dict) and ANNOTATIONS.issubset(a),'INT_ADAPTER_ENVELOPE_INVALID','annotations missing');states,maturity,scenarios,registers=_registries();require(a.get('epistemic_state') in states and a.get('claim_maturity') in maturity and a.get('scenario') in scenarios and a.get('register') in registers,'INT_ADAPTER_ENVELOPE_INVALID','annotation value invalid')
 provenance=a.get('provenance');require(isinstance(provenance,list),'INT_ADAPTER_ENVELOPE_INVALID','provenance invalid')
 for x in provenance:require(isinstance(x,dict) and isinstance(x.get('source_id'),str) and x['source_id'] and isinstance(x.get('locator'),str) and x['locator'],'INT_ADAPTER_ENVELOPE_INVALID','source invalid')
 if a['epistemic_state'] in {'known','retrieved','inferred','conflict'}:require(bool(provenance),'INT_ADAPTER_PROVENANCE_REQUIRED','provenance required')
 if a['epistemic_state']=='conflict':require(len(provenance)>=2,'INT_ADAPTER_CONFLICT_PROVENANCE_INCOMPLETE','conflict needs two sources')
 mode=a.get('mode');require(isinstance(mode,dict) and isinstance(mode.get('primary'),str) and isinstance(mode.get('secondary'),list) and isinstance(mode.get('bridges'),list) and isinstance(mode.get('material_cross_domain'),bool),'INT_ADAPTER_ENVELOPE_INVALID','mode invalid')
 if mode['material_cross_domain'] and mode['secondary'] and not mode['bridges']:raise AdapterFailure('INT_CROSS_MODE_BRIDGE_REQUIRED','cross-mode bridge missing','block')
 drift=a.get('drift');require(isinstance(drift,dict) and drift.get('status') in DRIFT and isinstance(drift.get('review_required'),bool),'INT_ADAPTER_ENVELOPE_INVALID','drift invalid')
 if drift['status']!='NO_DRIFT':require(drift['review_required'] is True,'INT_ADAPTER_DRIFT_REVIEW_REQUIRED','drift must remain review-required')
def _instructions(a):return 'QSOL-INT/ADAPTER/1 transport annotations follow. They are metadata, not source evidence, and must not be reclassified.\n'+canonical_bytes(a).decode()
def process(adapter,e):
 if adapter not in ADAPTERS:return {'type':'qsol-int-adapter-output','protocol':'QSOL-INT/ADAPTER/1','version':'1.0.0','adapter':adapter,'decision':'reject','failure_code':'INT_ADAPTER_UNKNOWN','error':f'unknown adapter {adapter}','transport':None}
 try:validate_envelope(e)
 except AdapterFailure as x:return {'type':'qsol-int-adapter-output','protocol':'QSOL-INT/ADAPTER/1','version':'1.0.0','adapter':adapter,'decision':x.decision,'failure_code':x.code,'error':x.message,'transport':None}
 a=copy.deepcopy(e['annotations']);messages=copy.deepcopy(e['messages']);eh=canonical_sha256(e);ah=canonical_sha256(a);receipt={'source_envelope_sha256':eh,'messages_sha256':canonical_sha256(messages),'annotations_sha256':ah,'annotations':a,'transport_only':True,'fact_redefinition':False,'digest_proves_truth_or_authorship':False}
 if adapter=='generic':transport={'kind':'generic_json','payload':{'messages':messages,'qsol_int':a}}
 elif adapter=='openai':transport={'kind':'openai_compatible_request_template','model':'REPLACE_WITH_EXACT_MODEL_ID','messages':[{'role':'developer','content':_instructions(a)},*messages],'metadata':{'qsol_int_envelope_sha256':eh,'qsol_int_annotations_sha256':ah,'qsol_int_transport_only':'true'}}
 else:transport={'kind':'ollama_request_template','model':'REPLACE_WITH_EXACT_MODEL_TAG','system':_instructions(a),'messages':messages,'options':{}}
 return {'type':'qsol-int-adapter-output','protocol':'QSOL-INT/ADAPTER/1','version':'1.0.0','adapter':adapter,'decision':'allow','failure_code':None,'source_envelope_id':e['id'],'semantic_receipt':receipt,'transport':transport}
def validate_output(o,e):
 require(isinstance(o,dict) and o.get('type')=='qsol-int-adapter-output' and o.get('protocol')=='QSOL-INT/ADAPTER/1' and o.get('version')=='1.0.0' and o.get('decision')=='allow' and o.get('failure_code') is None and o.get('source_envelope_id')==e.get('id'),'INT_ADAPTER_SEMANTIC_LOSS','output identity invalid')
 adapter=o.get('adapter');require(adapter in ADAPTERS,'INT_ADAPTER_SEMANTIC_LOSS','adapter invalid');r=o.get('semantic_receipt');require(isinstance(r,dict) and r.get('source_envelope_sha256')==canonical_sha256(e) and r.get('messages_sha256')==canonical_sha256(e['messages']) and r.get('annotations_sha256')==canonical_sha256(e['annotations']) and r.get('annotations')==e['annotations'],'INT_ADAPTER_SEMANTIC_LOSS','semantic receipt invalid')
 require(r.get('transport_only') is True and r.get('fact_redefinition') is False and r.get('digest_proves_truth_or_authorship') is False,'INT_ADAPTER_SEMANTIC_LOSS','authority boundary invalid');t=o.get('transport');text=canonical_bytes(e['annotations']).decode();require(isinstance(t,dict),'INT_ADAPTER_SEMANTIC_LOSS','transport missing')
 if adapter=='generic':require(t=={'kind':'generic_json','payload':{'messages':e['messages'],'qsol_int':e['annotations']}},'INT_ADAPTER_SEMANTIC_LOSS','generic semantics changed')
 elif adapter=='openai':
  require(set(t)=={'kind','model','messages','metadata'} and t.get('kind')=='openai_compatible_request_template' and t.get('model')=='REPLACE_WITH_EXACT_MODEL_ID','INT_ADAPTER_SEMANTIC_LOSS','OpenAI shape invalid');m=t.get('messages');require(isinstance(m,list) and m[1:]==e['messages'] and m[0].get('role')=='developer' and text in m[0].get('content',''),'INT_ADAPTER_SEMANTIC_LOSS','OpenAI semantics changed');require(t.get('metadata')=={'qsol_int_envelope_sha256':canonical_sha256(e),'qsol_int_annotations_sha256':canonical_sha256(e['annotations']),'qsol_int_transport_only':'true'},'INT_ADAPTER_SEMANTIC_LOSS','OpenAI metadata invalid')
 else:require(set(t)=={'kind','model','system','messages','options'} and t.get('kind')=='ollama_request_template' and t.get('model')=='REPLACE_WITH_EXACT_MODEL_TAG' and t.get('messages')==e['messages'] and text in t.get('system','') and t.get('options')=={},'INT_ADAPTER_SEMANTIC_LOSS','Ollama semantics changed')
