# New mode

Use this mode when the user supplies a new research question and expects a researched report.

## Phase 1: Research contract

Create `brief.md` with the objective, intended decision or use, audience, scope and non-goals, information cutoff date, required dimensions, deliverable language and format, completion criteria, and declared budget or time constraints.

Infer ordinary details when safe. Ask the user only when a missing choice would materially change the research direction, cost, or deliverable.

## Phase 2: Capability preflight

Inspect the current environment and write `capabilities.json`. The minimum viable research environment has one working source-discovery mechanism and one working mechanism that reads the content behind a result.

Prefer structured search and retrieval over UI automation. Use browser automation or computer use only when structured research tools are unavailable or cannot reach the necessary source.

If the minimum is not met, stop before creating research claims. Explain the limitation in the user's language.

## Phase 3: Question graph and workstreams

Turn the contract into research questions, then cluster them into 3–8 coherent workstreams. A workstream is a bounded research deliverable, not one search query.

Include, when relevant, facts and definitions, mechanisms and causes, comparisons and baselines, historical development, consequences, opposing evidence and falsifiers, and unresolved unknowns.

Write `task_manifest.jsonl`. For each task, create `workstreams/<task-id>/task.md` and `status.json` before spawning its subagent.

## Phase 4: Independent research

Spawn a separate Researcher for every workstream using the contract in `subagent-contracts.md`.

Each Researcher must persist queries and retrieval outcomes, faithful raw source captures, source metadata, atomic evidence, candidate claims bound to evidence, contradictions and limitations, and a concise handoff.

Do not let workers write to `registry/` or `article/`.

## Phase 5: Integration

After a wave completes, the Lead Agent:

1. checks `status.json` and required files;
2. canonicalizes duplicate URLs and source identities;
3. groups dependent or syndicated sources;
4. remaps workstream-local IDs into global IDs;
5. admits or rejects candidate evidence and claims;
6. updates `registry/`;
7. records integration decisions in `decisions.md`.

Do not treat agreement among dependent sources as corroboration.

## Phase 6: Coverage and gaps

For every critical question and required dimension, check the direct answer, primary evidence where reasonably available, independent corroboration for load-bearing claims, coverage of periods/entities/definitions, adverse evidence, temporal or measurement conflicts, and represented uncertainty.

Write gaps to `registry/gaps.jsonl` and contradictions to `registry/contradictions.jsonl`.

## Phase 7: Targeted research loop

Create new, narrowly scoped workstreams for the highest-priority open gaps. Do not tell an existing Researcher merely to "research more."

End the loop when the research-complete gate in `SKILL.md` passes. Stop with a qualified outcome if the declared budget is exhausted, preserving all unresolved gaps.

## Phase 8: Synthesis and verification

The Lead Agent builds `writer_packet/` from admitted claims only. Spawn one Writer for the first version to preserve voice and terminology. The Writer writes chapter by chapter but remains one role with one evidence boundary.

After the draft is complete, spawn an independent Verifier. The Verifier uses only persisted project material and reports findings without silently editing the report.

Route prose, structure, or qualifier errors to the Writer; unsupported or missing evidence to a new Researcher workstream; malformed registries to the Lead Agent; and irreducible uncertainty to explicit disclosure in the report.
