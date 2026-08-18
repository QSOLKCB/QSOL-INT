#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_INDEX = ROOT / "snapshots" / "parents" / "index.json"

NO_DRIFT = "NO_DRIFT"
CONTENT_DRIFT = "CONTENT_DRIFT"
SCHEMA_DRIFT = "SCHEMA_DRIFT"
SEMANTIC_DRIFT = "SEMANTIC_DRIFT"
CAPABILITY_DRIFT = "CAPABILITY_DRIFT"
AUTHORITY_DRIFT = "AUTHORITY_DRIFT"
BREAKING_DRIFT = "BREAKING_DRIFT"
SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
TAXONOMY = (NO_DRIFT, CONTENT_DRIFT, SCHEMA_DRIFT, SEMANTIC_DRIFT, CAPABILITY_DRIFT, AUTHORITY_DRIFT, BREAKING_DRIFT, SOURCE_UNAVAILABLE)
OUTCOME_EXIT = {"INT_OK":0,"INT_PARENT_DRIFT_DETECTED":2,"INT_PARENT_SOURCE_UNAVAILABLE":3,"INT_PARENT_SNAPSHOT_INVALID":4,"INT_PARENT_RECEIPT_MISMATCH":5,"INT_PARENT_CONTRACT_MISSING":6,"INT_DRIFT_CLASSIFICATION_UNRESOLVED":7,"INT_BREAKING_DRIFT":8,"INT_REVIEW_REQUIRED":9}
CLASS_RANK = {NO_DRIFT:0,CONTENT_DRIFT:1,SCHEMA_DRIFT:2,SEMANTIC_DRIFT:3,CAPABILITY_DRIFT:4,AUTHORITY_DRIFT:5,BREAKING_DRIFT:6,SOURCE_UNAVAILABLE:7}
DOC_METADATA_KEYS = {"description","documentation","docs","human_documentation","snapshot_date","generated_at","generated_date"}

class DriftFailure(Exception):
    def __init__(self, code: str, message: str): super().__init__(message); self.code=code; self.message=message
class SourceUnavailable(DriftFailure):
    def __init__(self, message: str): super().__init__("INT_PARENT_SOURCE_UNAVAILABLE", message)
class ParentContractMissing(DriftFailure):
    def __init__(self, message: str): super().__init__("INT_PARENT_CONTRACT_MISSING", message)
@dataclass(frozen=True)
class LiveArtifact:
    commit: str
    blob_sha1: str
    content: bytes

def canonical_json_bytes(value: Any) -> bytes: return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")
def sha256_hex(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def git_blob_sha1(data: bytes) -> str: return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()
def _require(condition: bool, code: str, message: str) -> None:
    if not condition: raise DriftFailure(code, message)
def _json_load_bytes(data: bytes) -> Any: return json.loads(data.decode("utf-8"))

def validate_snapshot(index_path: Path = SNAPSHOT_INDEX):
    try: index=json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError,UnicodeDecodeError,json.JSONDecodeError) as exc: raise DriftFailure("INT_PARENT_SNAPSHOT_INVALID",f"cannot parse snapshot index: {exc}") from exc
    _require(isinstance(index,dict),"INT_PARENT_SNAPSHOT_INVALID","snapshot index must be an object")
    _require(index.get("type")=="qsol-int-parent-snapshot","INT_PARENT_SNAPSHOT_INVALID","unexpected snapshot type")
    _require(index.get("protocol")=="QSOL-INT/PARENT-SNAPSHOT/1","INT_PARENT_SNAPSHOT_INVALID","unexpected snapshot protocol")
    semantic=index.get("semantic_identity"); _require(isinstance(semantic,dict),"INT_PARENT_SNAPSHOT_INVALID","semantic_identity missing")
    payload=semantic.get("payload"); _require(isinstance(payload,dict),"INT_PARENT_SNAPSHOT_INVALID","semantic identity payload missing")
    expected="sha256:"+sha256_hex(canonical_json_bytes(payload)); _require(semantic.get("id")==expected,"INT_PARENT_RECEIPT_MISMATCH","snapshot semantic identity receipt mismatch")
    _require(semantic.get("algorithm")=="sha256-canonical-json-v1","INT_PARENT_SNAPSHOT_INVALID","unsupported semantic identity algorithm")
    parents=payload.get("parents"); _require(isinstance(parents,list) and parents,"INT_PARENT_SNAPSHOT_INVALID","snapshot parents missing")
    seen=set(); content_by_key={}; repo_root=index_path.resolve().parents[2]
    for parent in parents:
        _require(isinstance(parent,dict),"INT_PARENT_SNAPSHOT_INVALID","parent snapshot entry must be object")
        name=parent.get("name"); repository=parent.get("repository"); source_commit=parent.get("source_commit")
        _require(isinstance(name,str) and name,"INT_PARENT_SNAPSHOT_INVALID","parent name missing"); _require(name not in seen,"INT_PARENT_SNAPSHOT_INVALID",f"duplicate parent {name}"); seen.add(name)
        _require(isinstance(repository,str) and repository.count("/")==1,"INT_PARENT_SNAPSHOT_INVALID",f"invalid repository for {name}")
        _require(isinstance(source_commit,str) and len(source_commit)==40,"INT_PARENT_SNAPSHOT_INVALID",f"invalid source commit for {name}")
        artifacts=parent.get("artifacts"); _require(isinstance(artifacts,list) and artifacts,"INT_PARENT_SNAPSHOT_INVALID",f"no artifacts for {name}"); paths=set()
        for artifact in artifacts:
            _require(isinstance(artifact,dict),"INT_PARENT_SNAPSHOT_INVALID",f"invalid artifact for {name}")
            path=artifact.get("path"); snapshot_path=artifact.get("snapshot_path")
            _require(isinstance(path,str) and path and path not in paths,"INT_PARENT_SNAPSHOT_INVALID",f"duplicate or invalid path for {name}"); paths.add(path)
            _require(isinstance(snapshot_path,str) and snapshot_path.startswith(f"snapshots/parents/{name}/"),"INT_PARENT_SNAPSHOT_INVALID",f"invalid snapshot path for {name}:{path}")
            local=(repo_root/snapshot_path).resolve(); _require(local.is_relative_to(repo_root),"INT_PARENT_SNAPSHOT_INVALID",f"snapshot path escapes repository for {name}:{path}")
            try: content=local.read_bytes()
            except OSError as exc: raise DriftFailure("INT_PARENT_SNAPSHOT_INVALID",f"snapshot content missing for {name}:{path}: {exc}") from exc
            _require(sha256_hex(content)==artifact.get("content_sha256"),"INT_PARENT_RECEIPT_MISMATCH",f"SHA-256 receipt mismatch for {name}:{path}")
            _require(git_blob_sha1(content)==artifact.get("git_blob_sha1"),"INT_PARENT_RECEIPT_MISMATCH",f"Git blob receipt mismatch for {name}:{path}")
            try: _json_load_bytes(content)
            except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise DriftFailure("INT_PARENT_SNAPSHOT_INVALID",f"snapshot contract is not valid JSON for {name}:{path}: {exc}") from exc
            content_by_key[(name,path)]=content
    authority=index.get("authority",{}); _require(authority.get("live_parent_state_precedence") is True,"INT_PARENT_SNAPSHOT_INVALID","live parent precedence must be explicit"); _require(authority.get("baseline_refresh_is_automatic") is False,"INT_PARENT_SNAPSHOT_INVALID","automatic baseline refresh is forbidden"); _require(authority.get("missing_live_evidence_is_no_drift") is False,"INT_PARENT_SNAPSHOT_INVALID","missing evidence must not mean no drift")
    _require(index.get("generation",{}).get("timestamp_part_of_semantic_identity") is False,"INT_PARENT_SNAPSHOT_INVALID","generation time must be non-semantic")
    return index,content_by_key

class GitHubProvider:
    def __init__(self):
        self.headers={"Accept":"application/vnd.github+json","User-Agent":"QSOL-INT-drift/1","X-GitHub-Api-Version":"2022-11-28"}; token=os.environ.get("GITHUB_TOKEN")
        if token: self.headers["Authorization"]=f"Bearer {token}"
    def _get_json(self,url,missing_is_contract=False):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=self.headers),timeout=20) as response: return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code==404 and missing_is_contract: raise ParentContractMissing(f"parent contract unavailable at {url}") from exc
            raise SourceUnavailable(f"GitHub HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError,TimeoutError,OSError,json.JSONDecodeError) as exc: raise SourceUnavailable(f"cannot retrieve live parent evidence from {url}: {exc}") from exc
    def resolve_commit(self,repository,ref):
        data=self._get_json(f"https://api.github.com/repos/{repository}/commits/{urllib.parse.quote(ref,safe='')}"); sha=data.get("sha")
        if not isinstance(sha,str) or len(sha)!=40: raise SourceUnavailable(f"invalid live commit identity for {repository}@{ref}")
        return sha
    def fetch_artifact(self,repository,commit,path):
        url=f"https://api.github.com/repos/{repository}/contents/{urllib.parse.quote(path,safe='/')}?{urllib.parse.urlencode({'ref':commit})}"; data=self._get_json(url,True); blob=data.get("sha"); encoded=data.get("content")
        if data.get("encoding")!="base64" or not isinstance(encoded,str): raise SourceUnavailable(f"unsupported GitHub content encoding for {repository}:{path}")
        content=base64.b64decode(encoded,validate=False)
        if not isinstance(blob,str) or len(blob)!=40 or git_blob_sha1(content)!=blob: raise SourceUnavailable(f"GitHub content/blob mismatch for {repository}:{path}")
        return LiveArtifact(commit,blob,content)

class FixtureProvider:
    def __init__(self,commits,artifacts,unavailable=None,missing=None): self.commits=commits; self.artifacts=artifacts; self.unavailable=unavailable or set(); self.missing=missing or set()
    def resolve_commit(self,repository,ref):
        if repository in self.unavailable or repository not in self.commits: raise SourceUnavailable(f"fixture source unavailable: {repository}")
        return self.commits[repository]
    def fetch_artifact(self,repository,commit,path):
        key=(repository,path)
        if key in self.missing: raise ParentContractMissing(f"fixture contract missing: {repository}:{path}")
        if key not in self.artifacts: raise SourceUnavailable(f"fixture artifact unavailable: {repository}:{path}")
        content=self.artifacts[key]; return LiveArtifact(commit,git_blob_sha1(content),content)

def changed_pointers(old,new,prefix=""):
    if type(old) is not type(new): return {prefix or "/"}
    if isinstance(old,dict):
        out=set()
        for key in sorted(set(old)|set(new)):
            child=f"{prefix}/{str(key).replace('~','~0').replace('/','~1')}"
            out.add(child) if key not in old or key not in new else out.update(changed_pointers(old[key],new[key],child))
        return out
    if isinstance(old,list):
        out=set()
        for i in range(max(len(old),len(new))):
            child=f"{prefix}/{i}"; out.add(child) if i>=len(old) or i>=len(new) else out.update(changed_pointers(old[i],new[i],child))
        return out
    return set() if old==new else {prefix or "/"}
def _get(value,path,default=None):
    cur=value
    for part in path:
        try: cur=cur[part]
        except (KeyError,IndexError,TypeError): return default
    return cur

def _unsafe_change(parent,role,old,new):
    reasons=[]
    if not isinstance(old,dict) or not isinstance(new,dict): return reasons
    if parent=="substrate" and role=="epistemic_contract":
        required={"never_promote_inferred_to_known_without_support","never_convert_unknown_to_false_without_support","never_hide_material_conflict"}; rules=set(new.get("rules",[])) if isinstance(new.get("rules"),list) else set(); missing=sorted(required-rules)
        if missing: reasons.append("removed fail-closed epistemic rules: "+",".join(missing))
        if old.get("fallback_state")=="unknown" and new.get("fallback_state")!="unknown": reasons.append("epistemic fallback no longer preserves unknown")
    if parent=="substrate" and role=="mode_contract":
        for path,reason in [(("resolution","no_authority_escalation"),"authority escalation guard weakened"),(("resolution","no_permission_escalation"),"permission escalation guard weakened"),(("cross_mode","bridge_required_for_material_cross_domain_claim"),"cross-mode bridge requirement removed"),(("geometry","not_a_truth_engine"),"geometry may be treated as truth engine")]:
            if _get(old,path) is True and _get(new,path) is not True: reasons.append(reason)
        if _get(old,("cross_mode","undeclared_cross_mode_inference"))=="prohibited" and _get(new,("cross_mode","undeclared_cross_mode_inference"))!="prohibited": reasons.append("undeclared cross-mode inference is no longer prohibited")
    if parent=="ark" and role=="capability_registry" and "capabilities are never inherited implicitly" in str(old.get("ordering_rule","")) and "capabilities are never inherited implicitly" not in str(new.get("ordering_rule","")): reasons.append("ARK capability inheritance guard removed")
    if parent=="ark" and role=="mrs_contract":
        old_text=" ".join(old.get("selection",[])); new_text=" ".join(new.get("selection",[]))
        if "do not infer or inherit undeclared capabilities" in old_text and "do not infer or inherit undeclared capabilities" not in new_text: reasons.append("MRS undeclared-capability guard removed")
        if "explicitly declared capabilities" in str(old.get("definition","")) and "explicitly declared capabilities" not in str(new.get("definition","")): reasons.append("MRS no longer requires explicitly declared capabilities")
    if parent=="ark" and role=="manifest" and isinstance(old.get("authority_order"),list) and old["authority_order"] and old["authority_order"][0]=="live_repository_state":
        if not isinstance(new.get("authority_order"),list) or not new["authority_order"] or new["authority_order"][0]!="live_repository_state": reasons.append("ARK live repository state lost highest parent authority")
    return reasons

def _has_pointer(pointers,fragments): return any(any(fragment in pointer for fragment in fragments) for pointer in pointers)
def classify_artifact(parent,role,path,baseline,live):
    if baseline==live: return {"primary_class":NO_DRIFT,"detected_classes":[NO_DRIFT],"classification_resolved":True,"reasons":["content SHA-256 and bytes match the committed snapshot"],"changed_pointers":[]}
    try: old=_json_load_bytes(baseline); new=_json_load_bytes(live)
    except (UnicodeDecodeError,json.JSONDecodeError): return {"primary_class":CONTENT_DRIFT,"detected_classes":[CONTENT_DRIFT],"classification_resolved":False,"reasons":["changed contract bytes could not be parsed as JSON; semantic impact is unresolved"],"changed_pointers":[]}
    if old==new: return {"primary_class":CONTENT_DRIFT,"detected_classes":[CONTENT_DRIFT],"classification_resolved":True,"reasons":["JSON meaning is byte-equivalent after parsing; formatting or representation changed"],"changed_pointers":[]}
    pointers=changed_pointers(old,new); classes=set(); reasons=[]; unsafe=_unsafe_change(parent,role,old,new)
    if unsafe: classes.add(BREAKING_DRIFT); reasons.extend(unsafe)
    if _has_pointer(pointers,("/$schema","/schema_version")): classes.add(SCHEMA_DRIFT); reasons.append("schema identity or schema version changed")
    if role=="documentation" or path.endswith((".md",".txt",".rst")): classes.add(CONTENT_DRIFT); reasons.append("documentation-only artifact changed")
    if parent=="ark":
        if role=="capability_registry" and _has_pointer(pointers,("/tiers","/implemented_recovery_tiers")): classes.add(CAPABILITY_DRIFT); reasons.append("ARK tier capability or implementation registry changed")
        if role=="manifest" and _has_pointer(pointers,("/implemented_recovery_tiers",)): classes.add(CAPABILITY_DRIFT); reasons.append("ARK implemented tier declaration changed")
        if role=="mrs_contract" and _has_pointer(pointers,("/examples",)): classes.add(CAPABILITY_DRIFT); reasons.append("ARK MRS capability examples changed")
    authority=("/authority","/provenance","/visibility","/canonical","/context_policy","/source_policy","/claim_maturity","/scenario_states","/register_states","/fallback_state","/cross_mode","/no_authority_escalation","/no_permission_escalation","/core_invariant")
    if _has_pointer(pointers,authority): classes.add(AUTHORITY_DRIFT); reasons.append("epistemic entitlement, provenance, boundary, or canonicality surface changed")
    if parent=="substrate" and role=="epistemic_contract" and _has_pointer(pointers,("/states","/rules")): classes.add(AUTHORITY_DRIFT); reasons.append("SUBSTRATE epistemic entitlement semantics changed")
    if role in {"epistemic_contract","mode_contract","mrs_contract"}:
        nonmeta=[p for p in pointers if not any(p.endswith("/"+k) for k in DOC_METADATA_KEYS)]
        if nonmeta: classes.add(SEMANTIC_DRIFT); reasons.append("contract meaning changed outside documentation-only metadata")
    if not classes:
        top={p.split("/")[1] for p in pointers if len(p.split("/"))>1 and p.split("/")[1]}
        classes.add(CONTENT_DRIFT); reasons.append("only documentation or generation metadata changed" if top and top.issubset(DOC_METADATA_KEYS) else "bytes and parsed JSON changed, but impact is not covered by a deterministic rule")
    resolved=True
    if classes=={CONTENT_DRIFT} and role!="documentation" and not path.endswith((".md",".txt",".rst")):
        top={p.split("/")[1] for p in pointers if len(p.split("/"))>1 and p.split("/")[1]}; resolved=bool(top) and top.issubset(DOC_METADATA_KEYS)
    detected=sorted(classes,key=lambda item:(-CLASS_RANK[item],item))
    return {"primary_class":detected[0],"detected_classes":detected,"classification_resolved":resolved,"reasons":sorted(set(reasons)),"changed_pointers":sorted(pointers)}

def build_fixture_from_snapshot(index,content_by_key):
    commits={}; artifacts={}
    for parent in index["semantic_identity"]["payload"]["parents"]:
        repo=parent["repository"]; commits[repo]=parent["source_commit"]
        for artifact in parent["artifacts"]: artifacts[(repo,artifact["path"])]=content_by_key[(parent["name"],artifact["path"])]
    return FixtureProvider(commits,artifacts)
def _failure_report(code,message): return {"type":"qsol-int-drift-report","protocol":"QSOL-INT/DRIFT/1","report_version":"1.0.0","scope":"snapshot_validation","baseline_snapshot_id":None,"authority":{"live_parent_state_over_snapshot":True,"snapshot_refresh_performed":False,"missing_live_evidence_counts_as_no_drift":False},"parents":[],"summary":{"detected_classes":[],"drift_detected":False,"classification_resolved":False,"review_required":True},"outcome":code,"status_codes":[code],"error":message}
def check_drift(provider=None,index_path=SNAPSHOT_INDEX):
    try: index,baseline=validate_snapshot(index_path)
    except DriftFailure as exc: return _failure_report(exc.code,exc.message)
    provider=provider or GitHubProvider(); parents_report=[]; global_classes=set(); unresolved=source_unavailable=contract_missing=breaking=False
    for parent in index["semantic_identity"]["payload"]["parents"]:
        name=parent["name"]; repo=parent["repository"]; ref=parent.get("source_ref","main"); pr={"name":name,"repository":repo,"source_ref":ref,"baseline_commit":parent["source_commit"],"live_commit":None,"artifacts":[]}
        try: live_commit=provider.resolve_commit(repo,ref); pr["live_commit"]=live_commit
        except SourceUnavailable as exc: pr["source_status"]=SOURCE_UNAVAILABLE; pr["error"]=exc.message; global_classes.add(SOURCE_UNAVAILABLE); source_unavailable=True; parents_report.append(pr); continue
        pr["source_status"]="AVAILABLE"
        for artifact in parent["artifacts"]:
            path=artifact["path"]; result={"path":path,"semantic_role":artifact["semantic_role"],"baseline_git_blob_sha1":artifact["git_blob_sha1"],"baseline_content_sha256":artifact["content_sha256"],"live_git_blob_sha1":None,"live_content_sha256":None}
            try: live=provider.fetch_artifact(repo,live_commit,path)
            except ParentContractMissing as exc: result.update({"primary_class":SOURCE_UNAVAILABLE,"detected_classes":[SOURCE_UNAVAILABLE],"classification_resolved":True,"reasons":["required live parent contract is missing"],"error":exc.message,"changed_pointers":[]}); global_classes.add(SOURCE_UNAVAILABLE); contract_missing=True; pr["artifacts"].append(result); continue
            except SourceUnavailable as exc: result.update({"primary_class":SOURCE_UNAVAILABLE,"detected_classes":[SOURCE_UNAVAILABLE],"classification_resolved":True,"reasons":["live parent evidence is unavailable"],"error":exc.message,"changed_pointers":[]}); global_classes.add(SOURCE_UNAVAILABLE); source_unavailable=True; pr["artifacts"].append(result); continue
            result["live_git_blob_sha1"]=live.blob_sha1; result["live_content_sha256"]=sha256_hex(live.content); c=classify_artifact(name,artifact["semantic_role"],path,baseline[(name,path)],live.content); result.update(c); global_classes.update(c["detected_classes"]); unresolved|=not c["classification_resolved"]; breaking|=BREAKING_DRIFT in c["detected_classes"]; pr["artifacts"].append(result)
        parents_report.append(pr)
    if source_unavailable: outcome="INT_PARENT_SOURCE_UNAVAILABLE"
    elif contract_missing: outcome="INT_PARENT_CONTRACT_MISSING"
    elif breaking: outcome="INT_BREAKING_DRIFT"
    elif unresolved: outcome="INT_DRIFT_CLASSIFICATION_UNRESOLVED"
    elif global_classes and global_classes!={NO_DRIFT}: outcome="INT_PARENT_DRIFT_DETECTED"
    else: outcome="INT_OK"
    detected=sorted(global_classes or {NO_DRIFT},key=lambda item:(-CLASS_RANK[item],item)); drift_detected=any(x!=NO_DRIFT for x in detected); codes=[outcome]
    if drift_detected and outcome not in {"INT_PARENT_SOURCE_UNAVAILABLE","INT_PARENT_CONTRACT_MISSING"}: codes.append("INT_REVIEW_REQUIRED")
    return {"type":"qsol-int-drift-report","protocol":"QSOL-INT/DRIFT/1","report_version":"1.0.0","scope":"live_parent_state_vs_committed_parent_snapshot","baseline_snapshot_id":index["semantic_identity"]["id"],"authority":{"live_parent_state_over_snapshot":True,"snapshot_refresh_performed":False,"missing_live_evidence_counts_as_no_drift":False},"parents":parents_report,"summary":{"detected_classes":detected,"drift_detected":drift_detected,"classification_resolved":not unresolved,"review_required":drift_detected},"outcome":outcome,"status_codes":codes}
def canonical_report_text(report): return canonical_json_bytes(report).decode("utf-8")+"\n"
def human_report(report,explain=False):
    lines=[f"QSOL-INT drift outcome: {report['outcome']}"]
    if report.get("baseline_snapshot_id"): lines.append(f"baseline: {report['baseline_snapshot_id']}")
    if report.get("error"): lines.append(f"error: {report['error']}")
    for parent in report.get("parents",[]):
        lines.append(f"{parent['name']}: baseline={parent['baseline_commit']} live={parent.get('live_commit') or 'UNAVAILABLE'}")
        if parent.get("error"): lines.append(f"  {SOURCE_UNAVAILABLE}: {parent['error']}")
        for artifact in parent.get("artifacts",[]):
            lines.append(f"  {artifact['path']}: {','.join(artifact.get('detected_classes',[]))}")
            if explain:
                for reason in artifact.get("reasons",[]): lines.append(f"    - {reason}")
                if artifact.get("changed_pointers"): lines.append("    changed: "+", ".join(artifact["changed_pointers"]))
    summary=report.get("summary",{}); lines.append("detected: "+",".join(summary.get("detected_classes",[]))); lines.append(f"review_required: {str(summary.get('review_required',False)).lower()}")
    if explain: lines += ["rule: live parent state outranks the committed snapshot for parent-owned semantics","rule: changed bytes do not automatically imply breaking semantic drift","rule: unknown impact is review-required, never optimistic compatibility","rule: this command never refreshes the committed baseline"]
    return "\n".join(lines)+"\n"
def _validate_snapshot_report():
    try: index,content=validate_snapshot()
    except DriftFailure as exc: return _failure_report(exc.code,exc.message)
    return {"type":"qsol-int-snapshot-validation-report","protocol":"QSOL-INT/PARENT-SNAPSHOT/1","snapshot_id":index["semantic_identity"]["id"],"artifact_count":len(content),"outcome":"INT_OK","status_codes":["INT_OK"]}
def main(argv=None):
    parser=argparse.ArgumentParser(prog="int",description="QSOL-INT parent drift detection"); sub=parser.add_subparsers(dest="command",required=True); check=sub.add_parser("check-drift"); check.add_argument("--json",action="store_true"); explain=sub.add_parser("explain-drift"); explain.add_argument("--json",action="store_true"); validate=sub.add_parser("validate-snapshot"); validate.add_argument("--json",action="store_true"); args=parser.parse_args(argv)
    if args.command=="validate-snapshot": report=_validate_snapshot_report(); sys.stdout.write(canonical_report_text(report) if args.json else (f"INT_OK snapshot={report['snapshot_id']} artifacts={report['artifact_count']}\n" if report["outcome"]=="INT_OK" else human_report(report,True))); return OUTCOME_EXIT.get(report["outcome"],9)
    report=check_drift(); sys.stdout.write(canonical_report_text(report) if args.json else human_report(report,args.command=="explain-drift")); return OUTCOME_EXIT.get(report["outcome"],9)
if __name__=="__main__": raise SystemExit(main())
