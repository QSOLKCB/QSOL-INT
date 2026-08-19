#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse,sys
from pathlib import Path
from evaluation_core import *

def _write(path,value):
 p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(canonical_text(value),encoding='utf-8')
def _human(r):
 lines=[f"QSOL-INT consumer evaluation: {r['run']['run_id']}",f"execution_kind: {r['run']['execution_kind']}",f"overall_score: {r['summary']['overall_score']}"]
 for m in METRIC_ORDER:
  x=r['metrics'][m]; field='penalty' if m==PENALTY_METRIC else 'score'; lines.append(f'{m}: {field}={x[field]}')
 return '\n'.join(lines)+"\nauthority: derived fixture-conformance report; not parent or source evidence\n"
def main(argv=None):
 p=argparse.ArgumentParser(prog='int',description='QSOL-INT deterministic consumer evaluation'); sub=p.add_subparsers(dest='command',required=True); sub.add_parser('validate-evaluations')
 e=sub.add_parser('evaluate'); e.add_argument('--run',required=True); e.add_argument('--json',action='store_true'); e.add_argument('--output'); e.add_argument('--validate-report')
 c=sub.add_parser('compare-evaluations'); c.add_argument('--left',required=True); c.add_argument('--right',required=True); c.add_argument('--json',action='store_true'); c.add_argument('--output'); c.add_argument('--validate-comparison')
 a=p.parse_args(argv)
 try:
  if a.command=='validate-evaluations':
   index,cases=validate_index(); print(f"INT_EVALUATIONS_OK cases={len(cases)} index_sha256={canonical_sha256(index)} parent_identity_sha256={index['parent_identity_sha256']}"); return 0
  if a.command=='evaluate':
   run=load_json(a.run,'INT_CONSUMER_RUN_INVALID'); report=evaluate_run(run)
   if a.validate_report:validate_report(load_json(a.validate_report,'INT_EVALUATION_REPORT_INVALID'),run)
   if a.output:_write(a.output,report)
   sys.stdout.write(canonical_text(report) if a.json else _human(report)); return 0
  left=load_json(a.left,'INT_EVALUATION_REPORT_INVALID'); right=load_json(a.right,'INT_EVALUATION_REPORT_INVALID'); out=compare_reports(left,right)
  if a.validate_comparison:validate_comparison(load_json(a.validate_comparison,'INT_EVALUATION_COMPARISON_INVALID'),left,right)
  if a.output:_write(a.output,out)
  sys.stdout.write(canonical_text(out) if a.json else f"QSOL-INT evaluation comparison: winner={out['winner_by_overall_fixture_score']} left={out['left']['overall_score']} right={out['right']['overall_score']}\n"); return 0
 except EvaluationFailure as x: print(f'{x.code}: {x.message}',file=sys.stderr); return 1
if __name__=='__main__':raise SystemExit(main())
