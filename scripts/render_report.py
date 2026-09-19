#!/usr/bin/env python3
"""Render claim markers in a draft as source footnotes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CLAIM_MARKER = re.compile(r"\[\[(C[0-9A-Za-z_-]+)\]\]")


def load_jsonl(path: Path) -> dict[str, dict]:
    rows = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        item_id = value.get("id")
        if not item_id or item_id in rows:
            raise ValueError(f"invalid or duplicate id in {path}:{number}")
        rows[item_id] = value
    return rows


def render(run: Path) -> Path:
    registry = run / "registry"
    sources = load_jsonl(registry / "sources.jsonl")
    evidence = load_jsonl(registry / "evidence.jsonl")
    claims = load_jsonl(run / "writer_packet" / "approved_claims.jsonl")
    draft_path = run / "article" / "report.draft.md"
    draft = draft_path.read_text(encoding="utf-8")
    source_numbers: dict[str, int] = {}

    def replace(match: re.Match[str]) -> str:
        claim_id = match.group(1)
        if claim_id not in claims:
            raise ValueError(f"unapproved claim marker: {claim_id}")
        source_ids = []
        for evidence_id in claims[claim_id].get("supporting_evidence", []):
            if evidence_id not in evidence:
                raise ValueError(f"{claim_id} references unknown evidence: {evidence_id}")
            source_id = evidence[evidence_id].get("source_id")
            if source_id not in sources:
                raise ValueError(f"{evidence_id} references unknown source: {source_id}")
            if source_id not in source_ids:
                source_ids.append(source_id)
        if not source_ids:
            raise ValueError(f"claim has no supporting sources: {claim_id}")
        for source_id in source_ids:
            source_numbers.setdefault(source_id, len(source_numbers) + 1)
        return "".join(f"[^{source_numbers[source_id]}]" for source_id in source_ids)

    body = CLAIM_MARKER.sub(replace, draft).rstrip()
    footnotes = []
    for source_id, number in sorted(source_numbers.items(), key=lambda item: item[1]):
        source = sources[source_id]
        details = " — ".join(
            part for part in [source.get("title") or source_id, source.get("publisher")] if part
        )
        if source.get("url"):
            details += f". {source['url']}"
        footnotes.append(f"[^{number}]: {details}")

    output = run / "article" / "report.md"
    output.write_text(
        f"{body}\n\n## Sources\n\n" + "\n".join(footnotes) + "\n", encoding="utf-8"
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    try:
        output = render(args.run.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
