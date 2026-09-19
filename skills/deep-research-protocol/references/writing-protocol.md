# Writing and verification protocol

The Writer is an evidence-constrained synthesizer, not a Researcher.

## Build the writer packet

The Lead Agent creates:

- `writing_brief.md`: audience, purpose, language, tone, length, and required output;
- `outline.md`: section purpose and allowed claim IDs;
- `approved_claims.jsonl`: claims that passed admission;
- `evidence_map.jsonl`: claim-to-evidence relationships;
- `source_index.jsonl`: source metadata used by the renderer;
- `contradictions.md`: required treatment of material conflicts;
- `limitations.md`: gaps and boundaries that must remain visible.

The packet is a capability boundary. Do not place unreviewed candidate claims in it.

## Drafting

The Writer writes only to `article/`, preserves required qualifiers, distinguishes actuals/estimates/forecasts/opinions/unknowns, attaches `[[Cxxx]]` after every factual proposition, and does not introduce substantive material absent from approved claims.

The Writer decides whether insufficient or conflicting material requires additional research, can be responsibly qualified or presented as uncertainty, should be omitted, or should remain an explicit limitation. Do not impose a fixed decision tree for this judgment.

When more research is needed, the Writer explains the problem and useful research direction in free-form `article/writer_requests.md`, stops the affected section, and returns control to the Lead Agent. The request may use paragraphs, lists, tables, or another clear structure; it has no schema. The Writer does not search or dispatch subagents.

The Lead decides whether research is warranted, clusters related requests, dispatches bounded workstreams within budget, admits the resulting evidence, rebuilds the Writer Packet, and returns control to the Writer. Record the resolution in `decisions.md` and clear `article/writer_requests.md` only after the request is resolved or deliberately converted into a disclosed limitation.

The Writer may inspect a local raw capture only to understand admitted evidence; it may not fetch the source again or follow links.

## Verification

The Verifier checks unknown or missing claim markers, unsupported propositions, numbers, dates, quotations and causal language, dropped qualifiers, claims outside their allowed section, omitted contradictions, inconsistent measurements, missing required claims, and limitations hidden from the reader.

The Verifier reports findings without editing the draft. Each finding identifies an owner: `writer`, `researcher`, or `lead`. A material evidence defect may initiate the same Lead-controlled synthesis-return loop as a Writer request; it does not grant the Verifier search or dispatch authority.

## Rendering

`render_report.py` converts claim markers into source footnotes through `Claim -> Evidence -> Source`. It rejects unknown claims and claims without resolvable sources, writes `article/report.md`, and leaves the draft unchanged.
