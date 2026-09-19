# Audit mode

Use this mode when the user supplies a completed report and asks for an audit. Do not rewrite, expand, or improve the report unless the user separately authorizes that work.

## Inputs

Persist the supplied report under `input/`, together with any source bundle, bibliography, attachments, or citation export provided by the user. Record the expected audit depth, cutoff date, whether external verification is required, and whether the supplied source bundle is complete.

## Capability rule

An offline audit is complete only when the user supplied enough source material to verify the report. If the report contains external citations but the environment cannot retrieve them, do not describe an internal-consistency review as a full evidence audit.

If required verification cannot be performed, explain the limitation in the user's language and stop, or offer a clearly labeled internal-only review when that would still be useful.

## Audit decomposition

Create independent audit workstreams appropriate to the report. Default tracks are:

1. claim inventory and citation coverage;
2. source existence and citation entailment;
3. numbers, dates, units, and comparison bases;
4. internal logic and cross-section consistency;
5. scope coverage, missing perspectives, and material bias.

Do not create an empty track when it does not apply. Every created track must be assigned to a separate audit subagent.

## Audit artifacts

Each Audit subagent writes only inside `audit/workstreams/<audit-id>/`: `task.md`, `claim_inventory.jsonl` when applicable, `findings.jsonl`, `raw/` source captures, `handoff.md`, and `status.json`.

Finding severities are:

- `blocking`: the principal conclusion is not currently supportable;
- `major`: a material claim, number, citation, or omission needs correction;
- `minor`: a localized weakness that does not change the central conclusion;
- `note`: a useful observation without a required correction.

## Consolidation

The Lead Agent deduplicates findings and writes `audit/final_audit.md` with an overall verdict, scope and limitations, blocking/major/minor findings, unsupported claims, citation problems, internal contradictions, missing dimensions, and prioritized remediation.

Every finding identifies the exact report passage, evidence checked, and why the issue matters. Do not score prose merely for disagreeing with the auditor's preferred conclusion.
