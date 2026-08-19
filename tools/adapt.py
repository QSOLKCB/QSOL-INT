#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse,sys
from pathlib import Path
from adapter_core import *
def conformance_report(index=None):
 index,fixtures=validate_index(index);results=[]
 for path,fixture,expected in fixtures:
  for adapter in ADAPTERS:
   output=process(adapter,fixture);errors=[]
   if output.get('decision')!=expected['decision']:errors.append('decision mismatch')
   if output.get('failure_code')!=expected['failure_code']:errors.append('failure-code mismatch')
   if not errors and output.get('decision')=='allow':
    try:validate_output(output,fixture)
    except AdapterFailure as x:errors.append(f'{x.code}: {x.message}')
   results.append({'fixture':path,'fixture_sha256':index['fixture_sha256'][path],'adapter':adapter,'expected':expected,'observed':{'decision':output.get('decision'),'failure_code':output.get('failure_code')},'result':'pass' if not errors else 'fail','errors':errors})
 report={'type':'qsol-int-adapter-conformance-report','protocol':'QSOL-INT/ADAPTER/1','version':'1.0.0','derived_noncanonical':True,'authority':{'transport_conformance_is_not_parent_compatibility':True,'adapter_output_is_source_evidence':False},'identity':{'index':'adapters/index.json','index_sha256':canonical_sha256(index),'contract':index['contract'],'contract_sha256':index['contract_sha256']},'adapters':list(ADAPTERS),'results':results,'summary':{'fixture_count':len(fixtures),'adapter_count':len(ADAPTERS),'total':len(results),'passed':sum(x['result']=='pass' for x in results),'failed':sum(x['result']=='fail' for x in results)}};report['fingerprint_sha256']=canonical_sha256(report);return report
def validate_report(r):
 require(isinstance(r,dict) and r.get('type')=='qsol-int-adapter-conformance-report','INT_ADAPTER_REPORT_INVALID','report identity invalid');fp=r.get('fingerprint_sha256');u=dict(r);u.pop('fingerprint_sha256',None);require(isinstance(fp,str) and len(fp)==64 and all(c in '0123456789abcdef' for c in fp) and fp==canonical_sha256(u) and r==conformance_report(),'INT_ADAPTER_REPORT_INVALID','report regeneration mismatch')
def _write(path,value):p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(canonical_text(value),encoding='utf-8')
def main(argv=None):
 p=argparse.ArgumentParser(prog='int',description='QSOL-INT transport adapters');sub=p.add_subparsers(dest='command',required=True);a=sub.add_parser('adapt');a.add_argument('--adapter',choices=ADAPTERS,required=True);a.add_argument('--input',required=True);a.add_argument('--json',action='store_true');a.add_argument('--output');v=sub.add_parser('validate-adapters');v.add_argument('--json',action='store_true');v.add_argument('--output');v.add_argument('--validate-report');x=p.parse_args(argv)
 try:
  if x.command=='adapt':
   output=process(x.adapter,load_json(x.input,'INT_ADAPTER_ENVELOPE_INVALID'))
   if x.output:_write(x.output,output)
   sys.stdout.write(canonical_text(output) if x.json else f"QSOL-INT adapter={x.adapter} decision={output['decision']} failure_code={output.get('failure_code')}\n");return 0 if output['decision']=='allow' else (2 if output['decision']=='block' else 3)
  report=conformance_report()
  if x.validate_report:validate_report(load_json(x.validate_report,'INT_ADAPTER_REPORT_INVALID'))
  if x.output:_write(x.output,report)
  sys.stdout.write(canonical_text(report) if x.json else f"INT_ADAPTERS_OK passed={report['summary']['passed']} total={report['summary']['total']} fingerprint={report['fingerprint_sha256']}\n");return 0 if report['summary']['failed']==0 else 1
 except AdapterFailure as e:print(f'{e.code}: {e.message}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
