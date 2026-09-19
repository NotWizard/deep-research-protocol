#!/usr/bin/env python3
"""Validate a Deep Research Protocol workspace using only the standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CLAIM_MARKER = re.compile(r"\[\[(C[0-9A-Za-z_-]+)\]\]")
DEFAULT_BUDGETS = {
    "max_total_research_workstreams": 20,
    "max_gap_research_rounds": 3,
    "max_synthesis_return_rounds": 2,
}


def load_jsonl(path: Path, errors: list[str]) -> list[dict]:
    if not path.exists():
        errors.append(f"missing file: {path}")
        return []
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON: {path}:{number}: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"expected object: {path}:{number}")
            continue
        rows.append(value)
    return rows


def index(rows: list[dict], label: str, errors: list[str]) -> dict[str, dict]:
    result = {}
    for row in rows:
        item_id = row.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{label} missing id")
        elif item_id in result:
            errors.append(f"duplicate {label} id: {item_id}")
        else:
            result[item_id] = row
    return result


def validate_audit(run: Path, publish: bool) -> list[str]:
    errors: list[str] = []
    report = run / "input" / "report.md"
    if not report.exists():
        errors.append(f"missing file: {report}")
    workstreams = run / "audit" / "workstreams"
    task_dirs = sorted(path for path in workstreams.glob("*") if path.is_dir())
    if not task_dirs:
        errors.append(f"missing audit workstreams: {workstreams}")
    for task_dir in task_dirs:
        for name in ("status.json", "findings.jsonl", "handoff.md"):
            path = task_dir / name
            if not path.exists():
                errors.append(f"missing file: {path}")
        status_path = task_dir / "status.json"
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON: {status_path}: {exc.msg}")
            else:
                if status.get("status") != "complete":
                    errors.append(f"incomplete audit workstream: {task_dir.name}")
        findings_path = task_dir / "findings.jsonl"
        if findings_path.exists():
            load_jsonl(findings_path, errors)
    if publish and not (run / "audit" / "final_audit.md").exists():
        errors.append(f"missing file: {run / 'audit' / 'final_audit.md'}")
    return errors


def validate(run: Path, publish: bool = False) -> list[str]:
    state_path = run / "state.json"
    if not state_path.exists():
        return [f"missing file: {state_path}"]
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {state_path}: {exc.msg}"]
    mode = state.get("mode")
    if mode not in {"new", "audit"}:
        return [f"invalid mode: {mode!r}; expected 'new' or 'audit'"]
    if mode == "audit":
        return validate_audit(run, publish)

    errors: list[str] = []
    raw_budgets = state.get("budgets", {})
    if not isinstance(raw_budgets, dict):
        errors.append("budgets must be an object")
        raw_budgets = {}
    unsupported = sorted(set(raw_budgets) - set(DEFAULT_BUDGETS))
    if unsupported:
        errors.append(f"unsupported budgets: {', '.join(unsupported)}")
    budgets = DEFAULT_BUDGETS.copy()
    for name, default in DEFAULT_BUDGETS.items():
        value = raw_budgets.get(name, default)
        if type(value) is not int or value < 0:
            errors.append(f"invalid budget {name}: {value!r}")
        else:
            budgets[name] = value

    usage = state.get("usage", {})
    if not isinstance(usage, dict):
        errors.append("usage must be an object")
        usage = {}

    tasks = load_jsonl(run / "task_manifest.jsonl", errors)
    workstreams_created = usage.get("research_workstreams_created", len(tasks))
    gap_rounds = usage.get("gap_research_rounds_completed", 0)
    synthesis_rounds = usage.get("synthesis_return_rounds_completed", 0)
    counters = {
        "research_workstreams_created": workstreams_created,
        "gap_research_rounds_completed": gap_rounds,
        "synthesis_return_rounds_completed": synthesis_rounds,
    }
    for name, value in counters.items():
        if type(value) is not int or value < 0:
            errors.append(f"invalid usage counter {name}: {value!r}")

    effective_workstreams = max(len(tasks), workstreams_created) if type(workstreams_created) is int else len(tasks)
    if effective_workstreams > budgets.get("max_total_research_workstreams", 20):
        errors.append("research workstream budget exceeded")
    if type(gap_rounds) is int and gap_rounds > budgets["max_gap_research_rounds"]:
        errors.append("gap-research round budget exceeded")
    if type(synthesis_rounds) is int and synthesis_rounds > budgets["max_synthesis_return_rounds"]:
        errors.append("synthesis-return round budget exceeded")

    registry = run / "registry"
    sources = index(load_jsonl(registry / "sources.jsonl", errors), "source", errors)
    evidence = index(load_jsonl(registry / "evidence.jsonl", errors), "evidence", errors)
    claims = index(load_jsonl(registry / "claims.jsonl", errors), "claim", errors)
    gaps = index(load_jsonl(registry / "gaps.jsonl", errors), "gap", errors)
    contradictions = index(
        load_jsonl(registry / "contradictions.jsonl", errors), "contradiction", errors
    )

    for evidence_id, item in evidence.items():
        if item.get("source_id") not in sources:
            errors.append(f"{evidence_id} references unknown source: {item.get('source_id')}")

    for claim_id, claim in claims.items():
        supporting = claim.get("supporting_evidence", [])
        opposing = claim.get("opposing_evidence", [])
        for evidence_id in [*supporting, *opposing]:
            if evidence_id not in evidence:
                errors.append(f"{claim_id} references unknown evidence: {evidence_id}")

        if claim.get("importance") == "critical" and claim.get("status") == "supported":
            claim_sources = [
                sources[evidence[evidence_id]["source_id"]]
                for evidence_id in supporting
                if evidence_id in evidence and evidence[evidence_id].get("source_id") in sources
            ]
            has_primary = any(item.get("source_type") == "primary" for item in claim_sources)
            groups = {
                item.get("independence_group")
                for item in claim_sources
                if item.get("independence_group")
            }
            if not has_primary and len(groups) < 2:
                errors.append(
                    f"{claim_id} lacks primary evidence or two independent source groups"
                )

    for contradiction_id, item in contradictions.items():
        for claim_id in item.get("claim_ids", []):
            if claim_id not in claims:
                errors.append(f"{contradiction_id} references unknown claim: {claim_id}")

    draft = run / "article" / "report.draft.md"
    if draft.exists():
        approved = index(
            load_jsonl(run / "writer_packet" / "approved_claims.jsonl", errors),
            "approved claim",
            errors,
        )
        for claim_id, claim in approved.items():
            if claim_id not in claims:
                errors.append(f"approved claim is absent from registry: {claim_id}")
            elif claim.get("status") != "supported":
                errors.append(f"approved claim is not supported: {claim_id}")
        for claim_id in CLAIM_MARKER.findall(draft.read_text(encoding="utf-8")):
            if claim_id not in approved:
                errors.append(f"draft references unapproved claim: {claim_id}")
    elif publish:
        errors.append(f"missing file: {draft}")

    if publish:
        for gap_id, gap in gaps.items():
            if gap.get("severity") == "critical" and gap.get("status") == "open":
                errors.append(f"open critical gap: {gap_id}")
        writer_requests = run / "article" / "writer_requests.md"
        if writer_requests.exists() and writer_requests.read_text(encoding="utf-8").strip():
            errors.append("unresolved writer request blocks publication")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    errors = validate(args.run.resolve(), args.publish)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Deep Research workspace validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
