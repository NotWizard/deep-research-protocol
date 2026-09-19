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

The Writer creates `writer_gaps.jsonl` instead of filling missing material. It may inspect a local raw capture only to understand admitted evidence; it may not fetch the source again or follow links.

## Verification

The Verifier checks unknown or missing claim markers, unsupported propositions, numbers, dates, quotations and causal language, dropped qualifiers, claims outside their allowed section, omitted contradictions, inconsistent measurements, missing required claims, and limitations hidden from the reader.

The Verifier reports findings without editing the draft. Each finding identifies an owner: `writer`, `researcher`, or `lead`.

## Rendering

`render_report.py` converts claim markers into source footnotes through `Claim -> Evidence -> Source`. It rejects unknown claims and claims without resolvable sources, writes `article/report.md`, and leaves the draft unchanged.
