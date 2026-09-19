# Workspace and schemas

JSONL artifacts contain one JSON object per non-empty line. IDs are stable within a run.

## New-mode workspace

```text
run/
├── brief.md
├── capabilities.json
├── state.json
├── task_manifest.jsonl
├── decisions.md
├── workstreams/<task-id>/
│   ├── task.md
│   ├── status.json
│   ├── search_log.jsonl
│   ├── sources.jsonl
│   ├── evidence.jsonl
│   ├── candidate_claims.jsonl
│   ├── findings.md
│   ├── handoff.md
│   └── raw/
├── registry/
│   ├── sources.jsonl
│   ├── evidence.jsonl
│   ├── claims.jsonl
│   ├── gaps.jsonl
│   └── contradictions.jsonl
├── writer_packet/
│   ├── writing_brief.md
│   ├── outline.md
│   ├── approved_claims.jsonl
│   ├── evidence_map.jsonl
│   ├── source_index.jsonl
│   ├── contradictions.md
│   └── limitations.md
├── article/
│   ├── report.draft.md
│   ├── writer_requests.md
│   └── report.md
└── audit/
    └── final_audit.md
```

## Audit-mode additions

```text
run/
├── input/
│   ├── report.md
│   └── supplied-sources/
└── audit/workstreams/<audit-id>/
    ├── task.md
    ├── status.json
    ├── claim_inventory.jsonl
    ├── findings.jsonl
    ├── handoff.md
    └── raw/
```

## Capabilities

```json
{"search_available":true,"page_read_available":true,"pdf_read_available":true,"subagents_available":true,"preferred_methods":[{"priority":1,"type":"mcp","name":"provider-name"},{"priority":2,"type":"native_web_search"},{"priority":3,"type":"browser_automation"},{"priority":4,"type":"computer_use"}],"checked_at":"2026-09-19T14:00:00+08:00"}
```

## State

```json
{"run_id":"2026-09-19-example","mode":"new","phase":"targeted_research","iteration":2,"status":"active","open_critical_gaps":1,"budgets":{"max_total_research_workstreams":20,"max_gap_research_rounds":3,"max_synthesis_return_rounds":2},"usage":{"research_workstreams_created":8,"gap_research_rounds_completed":2,"synthesis_return_rounds_completed":0},"stop_reason":null,"next_actions":["Resolve G003 using primary filings"]}
```

These are the only default protocol budgets. Parallelism is host-controlled. Do not add default limits for sources, retries, individual agents, or wall-clock time.

`article/writer_requests.md` is a free-form blocking handoff, not a structured schema. While it contains non-whitespace content, the run is not publishable.

## Task manifest

```json
{"id":"T001","title":"Market size and historical data","priority":"critical","questions":["Q1","Q2"],"status":"pending","depends_on":[],"assigned_agent":null}
```

## Source

```json
{"id":"S001","title":"FY2026 Earnings Call","url":"https://example.com","publisher":"Example Corp","author":null,"published_at":"2026-07-18","accessed_at":"2026-09-19","source_type":"primary","independence_group":"example-corp-management","quality_notes":"Management statement; potentially promotional"}
```

## Evidence

```json
{"id":"E001","source_id":"S001","question_id":"Q1","relation":"supports","excerpt":"Short source-faithful excerpt","locator":"prepared remarks, paragraph 18","extracted_fact":"Management raised full-year capex guidance","limitations":["Forward-looking guidance"],"retrieved_at":"2026-09-19T10:30:00+08:00"}
```

`relation` is `supports`, `contradicts`, or `context`.

## Claim

```json
{"id":"C001","statement":"The company raised FY2026 capex guidance","claim_type":"observation","importance":"critical","status":"supported","supporting_evidence":["E001","E004"],"opposing_evidence":[],"confidence":"high","scope":"Guidance as of 2026-07-18","questions":["Q1"],"allowed_sections":["3.2"],"required_qualifiers":["guidance, not actual spending"]}
```

`claim_type` is `observation`, `inference`, `estimate`, `forecast`, `opinion`, or `unknown`. `status` is `candidate`, `supported`, `contested`, `rejected`, or `superseded`.

## Gap

```json
{"id":"G003","question_id":"Q2","severity":"critical","missing":"Independent primary capacity data","reason":"Current reports share one attribution chain","next_queries":["site:company.com capacity annual report"],"status":"open"}
```

## Contradiction

```json
{"id":"X001","claim_ids":["C014","C015"],"description":"Company guidance conflicts with supplier shipment data","possible_explanations":["Different measurement basis","Different time window"],"resolution_status":"unresolved","report_treatment":"present_both"}
```

## Raw source capture

```markdown
---
source_id: S001
url: https://example.com/report
title: Example Annual Report
publisher: Example Corp
published_at: 2026-08-10
retrieved_at: 2026-09-19T14:30:00+08:00
retrieval_method: web_search
content_type: html
---

# Raw captured content

The text actually returned by the retrieval tool. Mark truncation explicitly.
```

Raw captures are immutable. Add a new capture rather than editing source text after retrieval.
