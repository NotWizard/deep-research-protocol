---
name: deep-research-protocol
description: Conduct a new multi-source deep research project through independently delegated research tasks, or audit a completed research report for evidence, citations, consistency, and coverage. Uses persistent source artifacts, claim-evidence traceability, gap-driven iteration, and a non-browsing final writer. Do not use for simple factual lookups or ordinary short web searches.
---

# Deep Research Protocol

Run substantial research as a persistent, evidence-backed project rather than a single prompt-response interaction.

The unit of quality is a supported claim, not a polished paragraph.

## Execution constitution

- The Lead Agent plans, delegates, integrates, and enforces gates; it does not perform substantive domain research.
- Research subagents research independently and persist their materials; they do not write the final report.
- The Writer writes only from the approved local research packet; it must not search, browse, or introduce new facts.
- The Verifier audits the draft independently; it does not silently rewrite it.
- Every handoff occurs through files in the research workspace.
- Every executable research or audit workstream must be assigned to a separate subagent. Run independent workstreams concurrently when capacity permits and in waves otherwise.
- A subagent writes only inside its assigned workstream directory. Only the Lead Agent may merge global registries.

If the host has no subagent/delegation mechanism, state that the current environment cannot execute this protocol and stop. Do not silently fall back to a single-agent workflow.

## Modes

Use exactly one mode:

- `new`: Start from a new research question and produce a fully researched report. Read [references/new-mode.md](references/new-mode.md).
- `audit`: Audit a completed report supplied by the user. Do not rewrite or expand it unless separately requested. Read [references/audit-mode.md](references/audit-mode.md).

Interrupted work remains in its original mode; `resume` and `extend` are not user-facing modes.

## Capability preflight

Before decomposing work, inspect the tools, MCP servers, connectors, apps, installed skills, browser automation, and computer-use capabilities actually available in the current environment. Record the result in `capabilities.json` as described in [references/schemas.md](references/schemas.md).

Use this priority order for external research:

1. Purpose-built search/retrieval MCP servers, connectors, native search tools, or relevant installed search skills.
2. Browser automation or browser-use tooling.
3. Computer-use tooling operating an accessible browser.

A `new` run requires both source discovery and page-reading capability. An `audit` run may operate offline only when the user supplied enough source material to verify the report.

If the required capability is unavailable, stop. Tell the user plainly that the current environment lacks usable search or page-reading capability and therefore cannot complete the Deep Research task. Write that message in the language used by the user; never use a fixed-language literal.

Do not answer from model memory as a substitute for research. Do not install or connect an external service unless the user requested or authorized it.

## Shared rules

Read [references/subagent-contracts.md](references/subagent-contracts.md) before dispatching any subagent. Read [references/source-policy.md](references/source-policy.md) before admitting evidence. Use [references/schemas.md](references/schemas.md) for every persisted artifact.

Core invariants:

1. Bind evidence to claims during extraction, never after writing.
2. Preserve a faithful local source capture for every source used.
3. Search snippets, prior AI reports, and unsourced summaries are leads, not evidence for critical claims.
4. Source quantity alone is never a completion condition.
5. Two URLs are not necessarily two independent sources; record an `independence_group`.
6. Preserve material contradictions instead of averaging them away.
7. Budget exhaustion is a stop reason, not evidence of completion.
8. Missing evidence must remain an explicit gap or unknown.

## Default research budget

Unless the user explicitly approves a larger budget, a `new` run has three limits:

- at most 20 total Research workstreams across initial research, gap follow-ups, synthesis-stage returns, verifier-requested research, and replacement workstreams;
- at most 3 gap-research rounds before synthesis;
- at most 2 synthesis-return rounds initiated by the Writer or Verifier after synthesis begins.

Parallelism is determined by the host environment and is not a protocol budget. A round may contain multiple workstreams, but every workstream counts toward the total of 20.

## Lead Agent workflow

1. Create the run workspace and research contract.
2. Perform capability preflight.
3. Decompose the work into bounded, non-overlapping workstreams with explicit completion criteria.
4. Create each workstream directory before delegation.
5. Spawn one independent subagent per workstream. Never allow concurrent workers to edit a shared registry.
6. Wait for all workstreams, then inspect their structured handoffs and status files.
7. Merge and deduplicate sources, evidence, candidate claims, gaps, and contradictions into `registry/`.
8. Recalculate coverage. Create targeted follow-up workstreams for unresolved critical gaps while budget remains.
9. Enter synthesis only after the research-complete gate passes.
10. Build `writer_packet/`, spawn the non-browsing Writer, then spawn the Verifier.
11. When the Writer or Verifier returns an evidence need, decide whether more research is warranted, cluster related needs into bounded workstreams, dispatch Research subagents within budget, integrate their outputs, rebuild the Writer Packet, and return control to synthesis.
12. Run the deterministic validator and renderer before delivery.

The Lead Agent may inspect raw captures only to resolve malformed artifacts, duplicate sources, disputed handoffs, or integration errors. It must not use that exception to replace a missing Researcher.

## Research-complete gate

Writing may begin only when:

- every critical question is answered or explicitly marked `insufficient_evidence`;
- every critical supported claim has direct primary evidence or at least two genuinely independent high-quality sources;
- no critical gap remains open;
- material contradictions are resolved or assigned explicit report treatment;
- all required dimensions meet their completion criteria; and
- another search round is unlikely to materially change the conclusion, or a declared budget limit has been reached and the limitation will be disclosed.

## Writing boundary

Read [references/writing-protocol.md](references/writing-protocol.md) only after the research-complete gate passes.

The Writer may read only persisted project material. It must not use web search, search MCP, browser automation, computer use, external URLs, or model memory as factual support.

The Writer decides whether insufficient or conflicting material requires more research, can be responsibly qualified or presented as uncertainty, should be omitted, or should remain an explicit limitation. When more research is needed, it explains the need in free-form `article/writer_requests.md`, stops the affected section, and returns control to the Lead Agent. The file has no required schema.

The Lead Agent decides whether to dispatch more research and how many workstreams to create. It must not treat one Writer request as automatically equal to one workstream. After resolving the request, record the decision in `decisions.md`; publishing remains blocked while `article/writer_requests.md` is non-empty.

Every factual proposition in the draft must carry an approved claim marker such as `[[C017]]`. Final source citations are rendered from the claim-evidence graph.

## Final gate

For `new`, run the scripts from this skill directory:

```bash
python3 scripts/validate_run.py <research-directory> --publish
python3 scripts/render_report.py <research-directory>
```

For `audit`, run only:

```bash
python3 scripts/validate_run.py <research-directory> --publish
```

Do not call the work complete unless validation passes. If evidence remains insufficient, deliver an explicitly qualified result rather than weakening the gates.
