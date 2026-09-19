import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.render_report import render
from scripts.validate_run import validate


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class ProtocolScriptsTest(unittest.TestCase):
    def make_run(self) -> Path:
        self.temp = tempfile.TemporaryDirectory()
        run = Path(self.temp.name)
        (run / "registry").mkdir()
        (run / "article").mkdir()
        (run / "writer_packet").mkdir()
        (run / "state.json").write_text('{"mode":"new"}', encoding="utf-8")
        write_jsonl(
            run / "registry" / "sources.jsonl",
            [{"id": "S001", "title": "Source", "url": "https://example.com", "source_type": "primary", "independence_group": "origin"}],
        )
        write_jsonl(
            run / "registry" / "evidence.jsonl",
            [{"id": "E001", "source_id": "S001", "relation": "supports"}],
        )
        write_jsonl(
            run / "registry" / "claims.jsonl",
            [{"id": "C001", "importance": "critical", "status": "supported", "supporting_evidence": ["E001"], "opposing_evidence": []}],
        )
        write_jsonl(
            run / "writer_packet" / "approved_claims.jsonl",
            [{"id": "C001", "importance": "critical", "status": "supported", "supporting_evidence": ["E001"], "opposing_evidence": []}],
        )
        write_jsonl(run / "registry" / "gaps.jsonl", [])
        write_jsonl(run / "registry" / "contradictions.jsonl", [])
        (run / "article" / "report.draft.md").write_text(
            "Supported fact.[[C001]]\n", encoding="utf-8"
        )
        return run

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_valid_run_renders(self) -> None:
        run = self.make_run()
        self.assertEqual(validate(run, publish=True), [])
        output = render(run).read_text(encoding="utf-8")
        self.assertIn("Supported fact.[^1]", output)
        self.assertIn("https://example.com", output)

    def test_unknown_claim_fails(self) -> None:
        run = self.make_run()
        (run / "article" / "report.draft.md").write_text(
            "Unsupported.[[C999]]\n", encoding="utf-8"
        )
        self.assertIn("draft references unapproved claim: C999", validate(run, publish=True))

    def test_unapproved_registry_claim_cannot_publish(self) -> None:
        run = self.make_run()
        write_jsonl(run / "writer_packet" / "approved_claims.jsonl", [])
        self.assertIn("draft references unapproved claim: C001", validate(run, publish=True))
        with self.assertRaisesRegex(ValueError, "unapproved claim marker: C001"):
            render(run)

    def test_invalid_mode_fails(self) -> None:
        run = self.make_run()
        (run / "state.json").write_text('{"mode":"resume"}', encoding="utf-8")
        self.assertIn("invalid mode: 'resume'; expected 'new' or 'audit'", validate(run))

    def test_audit_workspace(self) -> None:
        run = self.make_run()
        (run / "state.json").write_text('{"mode":"audit"}', encoding="utf-8")
        (run / "input").mkdir()
        (run / "input" / "report.md").write_text("Report\n", encoding="utf-8")
        workstream = run / "audit" / "workstreams" / "A001"
        workstream.mkdir(parents=True)
        (workstream / "status.json").write_text('{"status":"complete"}', encoding="utf-8")
        write_jsonl(workstream / "findings.jsonl", [])
        (workstream / "handoff.md").write_text("Complete\n", encoding="utf-8")
        (run / "audit" / "final_audit.md").write_text("Audit\n", encoding="utf-8")
        self.assertEqual(validate(run, publish=True), [])


if __name__ == "__main__":
    unittest.main()
