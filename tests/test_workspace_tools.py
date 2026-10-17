"""Guard migration boundaries: artifact identity, isolated inputs and old evidence."""

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import reference
import check_performance as performance
from generate_query_case import persist


class WorkspaceToolsTests(unittest.TestCase):
    def test_library_artifacts_and_repository_fixtures_have_distinct_roots(self):
        for name in ("src/data_meta.rs", "data/manifest.json", "tests/query_vectors.rs",
                     "third_party/unicode/LICENSE.txt"):
            self.assertEqual(reference.artifact_path(name), reference.LIB_ROOT / name)
        for name in ("docs/query-case.json", "tests/fixtures/python-api-v1.json"):
            self.assertEqual(reference.artifact_path(name), reference.ROOT / name)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(reference.artifact_path("src/data_meta.rs", root), root / "src/data_meta.rs")
            persist(root, {"src/table.rs": b"original", "docs/provenance.json": b"{}"}, True)
            with self.assertRaises(ValueError):
                persist(root, {"src/new.rs": b"new", "src/table.rs": b"changed"}, True)
            self.assertFalse((root / "src/new.rs").exists())
        for name in ("../data/file", str(reference.ROOT / "data/file")):
            with self.assertRaises(reference.ReferenceError):
                reference.artifact_path(name)

    def test_snapshot_keeps_virtual_workspace_and_independent_probe_locks(self):
        names = reference.workspace_inputs(("query_vectors",), "tools/differential-probe")
        self.assertEqual(len(names), len(set(names)))
        for name in ("Cargo.toml", "Cargo.lock", "crates/lingose/Cargo.toml",
                     "crates/lingose-cli/Cargo.toml", "crates/lingose-cli/src/main.rs",
                     "crates/lingose/tests/query_vectors.rs", "crates/lingose/data/lexicon.bin",
                     "tools/differential-probe/Cargo.lock"):
            self.assertIn(name, names)
        self.assertTrue(all((reference.ROOT / name).is_file() for name in names))
        self.assertFalse(any(name.startswith(("src/", "data/")) for name in names))

    def test_existing_evidence_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(reference, "ROOT", Path(temporary)):
            root = Path(temporary)
            prior = root / "prior.json"
            prior.write_bytes(b"original")
            with self.assertRaises(reference.ReferenceError):
                reference.evidence_output(prior)
            with self.assertRaises(reference.ReferenceError):
                reference.evidence_output(root.parent / "escaped.json")
            self.assertEqual(reference.evidence_output(root / "new.json"), root / "new.json")
            self.assertEqual(prior.read_bytes(), b"original")

    def test_only_generator_identity_can_differ_from_verified_historical_provenance(self):
        for name in ("query-case", "annotation-unicode"):
            recorded = (reference.ROOT / f"docs/{name}.json").read_bytes()
            current = json.loads(recorded)
            current["generator"]["sha256"] = "current generator"
            reference.check_historical_generator(name, json.dumps(current).encode(), recorded)
            current["unicode_version"] = "unapproved"
            with self.assertRaises(reference.ReferenceError):
                reference.check_historical_generator(name, json.dumps(current).encode(), recorded)
            tampered = json.loads(recorded)
            tampered["generator"]["sha256"] = "0" * 64
            with self.assertRaises(reference.ReferenceError):
                reference.check_historical_generator(name, recorded, json.dumps(tampered).encode())

    def test_performance_rejects_old_incomplete_and_changed_regression_prerequisites(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(performance, "ROOT", Path(temporary)):
            root = Path(temporary)
            names = ("api_contract", "query_vectors", "category_vectors", "annotation_vectors",
                     "annotation_context_vectors", "annotation_frequency_vectors")
            inputs = {}
            for name in names:
                path = root / f"crates/lingose/tests/{name}.rs"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"unchanged tests")
                inputs[path.relative_to(root).as_posix()] = reference.file_record(path)
            report = {"phase": "P4.1", "outputs": {name: "test result: ok." for name in (*names, "lingose")},
                      "inputs": inputs}
            path = root / "regressions.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            performance.validated_regressions(path)
            for key, replacement in (("phase", "P3.3"), ("outputs", {"lingose": "failed"}), ("inputs", {})):
                path.write_text(json.dumps(report | {key: replacement}), encoding="utf-8")
                with self.assertRaises(reference.ReferenceError):
                    performance.validated_regressions(path)
            path.write_text(json.dumps(report), encoding="utf-8")
            (root / next(iter(inputs))).write_bytes(b"edited tests")
            with self.assertRaisesRegex(reference.ReferenceError, "identity drift"):
                performance.validated_regressions(path)


if __name__ == "__main__":
    unittest.main()
