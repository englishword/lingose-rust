"""Guarded production projection, including states absent from the real snapshot."""

from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import export_data
from capture_api_vectors import build_fixture, fixture_paths, fixture_spec
from export_data import available, encode, guarded_artifacts, persist_all, project
from reference import BASELINE, ReferenceError, canonical, connect, file_record


class ExportProjectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.lexicon, self.frequency = self.root / "lex.sqlite", self.root / "freq.sqlite"
        self.baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        spec = fixture_spec()
        spec["entries"]["emptytext"] = {"fields": {"ism": "", "root_lemma": "0", "meaning_en": "a\nb", "meaning_zh": "e\u0301 é 中文"}}
        spec["entries"]["\ue000"] = {"fields": {"kind:CET4": False}}
        spec["entries"]["😀"] = {"fields": {"kind:CET4": True, "rank": "0"}}
        spec["entries"]["dependencies"] = {"selected": 1,
            "pronunciations": [{"ips": "first"}, {"ips": "second", "ipsm": "dep-endencies"}],
            "fields": {"ism": "dep-endencies"}}
        build_fixture(self.lexicon, self.frequency, self.baseline, spec)
        # A valid derivation may name another pronunciation's exact dependency.
        with closing(sqlite3.connect(self.lexicon)) as db:
            db.execute("UPDATE ipsm_derivation SET ips_value_id=?,ips_sha256=? WHERE result_value_id=?",
                       ("dependencies:p0:ips", hashlib.sha256(b"first").hexdigest(), "dependencies:p1:ipsm"))
            db.commit()

    def projection(self):
        with closing(connect(self.lexicon)) as db, closing(connect(self.frequency)) as frequency:
            return project(db, frequency)

    def mutate(self, statement, parameters=()):
        with closing(sqlite3.connect(self.lexicon)) as db:
            db.execute(statement, parameters)
            db.commit()

    def test_all_fixture_fields_and_annotation_states_match_installed_python(self):
        from lingose import query, annotation
        before = [file_record(path) for path in (self.lexicon, self.frequency)]
        projection = self.projection()
        with fixture_paths(self.lexicon, self.frequency), closing(connect(self.lexicon)) as db:
            annotator = annotation._Annotator(db, set())
            for row in projection.entries:
                result = query._lookup(db, "fixture-v1", row[0])
                selected = next((pair for pair in result["pronunciations"] if pair["selected"]), None)
                for name, column in (("ipa", 1), ("ips", 2), ("ipsm", 4)):
                    field = selected[name] if selected is not None and result["pronunciation_status"] == "available" else None
                    value = field["value"] if field is not None and field["status"] == "available" else None
                    self.assertEqual(row[column], value, (row[0], name))
                for name, column in (("ism", 3), ("root_lemma", 5)):
                    self.assertEqual(row[column], result[name]["value"] if result[name]["status"] == "available" else None)
                for language, column in (("en", 6), ("zh", 7)):
                    field = result["meanings"][language]
                    self.assertEqual(row[column], field["value"] if field["status"] == "available" else None)
                match = annotator.exact(row[0])
                self.assertEqual(row[9], 2 if match.notation is not None else int(match.fallback))
            self.assertEqual(projection.labels, query.labels())
            for label, members in zip(projection.labels, projection.lists):
                self.assertEqual([projection.entries[index][0] for index in members], query.kind_list(label))
        self.assertEqual([file_record(path) for path in (self.lexicon, self.frequency)], before)
        self.assertEqual({row[9] for row in projection.entries}, {0, 1, 2})
        words = {row[0]: row for row in projection.entries}
        self.assertEqual(words["emptytext"][3:8], ["", None, "0", "a\nb", "e\u0301 é 中文"])
        self.assertEqual(words["dependencies"][4], "dep-endencies")
        self.assertIsNone(words["stale"][4])
        self.assertIsNone(words["noderivation"][4])
        self.assertEqual(projection.invalid_selected_ipsm, 2)
        self.assertLess(list(words).index("\ue000"), list(words).index("😀"))
        self.assertEqual(words["\ue000"][8], 0)
        self.assertIn(["tail", 5062], projection.frequency)

    def test_empty_available_ips_is_a_data_error(self):
        self.mutate("UPDATE field_value SET value_json='\"\"' WHERE value_id='apple:p0:ips'")
        with self.assertRaisesRegex(ReferenceError, "nonempty"):
            self.projection()

    def test_missing_selected_ips_is_a_data_error(self):
        self.mutate("DELETE FROM field_value WHERE value_id='apple:p0:ips'")
        with self.assertRaisesRegex(ReferenceError, "lacks IPS"):
            self.projection()

    def test_cross_entry_selection_is_rejected(self):
        self.mutate("UPDATE pronunciation_set SET selected_id='may:p0' WHERE entry_id='apple'")
        with self.assertRaisesRegex(ReferenceError, "owned selected"):
            self.projection()

    def test_dependency_algorithm_and_unavailable_input_invalidate_ipsm(self):
        self.mutate("UPDATE ipsm_derivation SET algorithm_version='2' WHERE result_value_id='apple:p0:ipsm'")
        self.assertIsNone({row[0]: row for row in self.projection().entries}["apple"][4])
        self.mutate("UPDATE field_value SET status='invalid',value_json=NULL,basis=NULL WHERE value_id='dependencies:p0:ips'")
        self.assertIsNone({row[0]: row for row in self.projection().entries}["dependencies"][4])

    def test_binary_roundtrip_preserves_empty_null_unicode_and_all_states(self):
        from verify_data import decode
        value = self.projection()
        versions = ("11" * 32, "22" * 32)
        image, _ = encode(value.entries, value.labels, value.lists, [], versions)
        entries, categories, _ = decode(image, kind="lexicon", versions=versions)
        self.assertEqual(entries, value.entries)
        self.assertEqual(categories, [(label, [entries[index][0] for index in members])
                                      for label, members in zip(value.labels, value.lists)])
        image, _ = encode([], [], [], value.frequency, versions)
        self.assertEqual(decode(image, kind="frequency", versions=versions)[2], [tuple(row) for row in value.frequency])

    def test_input_change_after_projection_prevents_artifact_return(self):
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        with closing(connect(self.lexicon)) as db, closing(connect(self.frequency)) as frequency:
            baseline["lexicon"]["build_info"] = dict(db.execute("SELECT * FROM build_info").fetchone())
            baseline["frequency"]["metadata"] = dict(frequency.execute("SELECT * FROM frequency_metadata").fetchone())
            baseline["frequency"]["table_counts"]["frequency_word"] = frequency.execute("SELECT COUNT(*) FROM frequency_word").fetchone()[0]
            words = [row[0] for row in db.execute("SELECT word FROM entry ORDER BY word COLLATE BINARY")]
        baseline["lexicon"]["word_count"] = len(words)
        baseline["lexicon"]["binary_ordered_words_sha256"] = hashlib.sha256(b"".join(canonical(word) + b"\n" for word in words)).hexdigest()
        before = {"lexicon": file_record(self.lexicon), "frequency": file_record(self.frequency)}
        baseline["fingerprints"] = before

        def mutate_after_build(*args):
            # A real disposable input changes after projection, before publish.
            self.mutate("UPDATE field_value SET value_json='\"changed\"' WHERE value_id='apple:p0:ips'")
            return {"data/example": b"must not escape the guard"}

        with patch.object(export_data, "require_baseline", return_value=baseline), \
             patch.object(export_data, "installed", return_value=(None, None, self.lexicon, self.frequency)), \
             patch.object(export_data, "build_artifacts", side_effect=mutate_after_build), \
             patch.object(export_data, "fingerprints", side_effect=lambda: {"lexicon": file_record(self.lexicon), "frequency": file_record(self.frequency)}):
            with self.assertRaisesRegex(ReferenceError, "Input changed during export"):
                guarded_artifacts()


class ExportGuardTests(unittest.TestCase):
    def test_available_values_distinguish_types_without_truthiness(self):
        row = lambda value: {"status": "available", "value_json": json.dumps(value)}
        self.assertIs(available(row(False), bool), False)
        self.assertEqual(available(row(0), int), 0)
        self.assertEqual(available(row(""), str), "")
        self.assertEqual(available(row("0"), str), "0")
        for value in (False, 0, None, [], {}):
            with self.subTest(value=value), self.assertRaises(ReferenceError):
                available(row(value), str)
        with self.assertRaises(ReferenceError):
            available(row(0), bool)
        with self.assertRaises(ReferenceError):
            available({"status": "pending_review", "value_json": '"candidate"'}, str)

    def test_baseline_tamper_is_rejected_before_projection(self):
        with patch.object(export_data, "sha256", return_value="0" * 64), patch.object(export_data, "project") as capture:
            with self.assertRaisesRegex(ReferenceError, "baseline digest"):
                guarded_artifacts()
            capture.assert_not_called()

    def test_installed_input_tamper_is_rejected_before_projection(self):
        import reference
        with patch.object(reference, "fingerprints", return_value={}), patch.object(export_data, "project") as capture:
            with self.assertRaisesRegex(ReferenceError, "Installed reference changed"):
                guarded_artifacts()
            capture.assert_not_called()

    def test_persistence_preflight_detects_drift_without_partial_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            persist_all(root, {"data/a": b"first"}, True)
            with self.assertRaises(ReferenceError):
                persist_all(root, {"data/new": b"new", "data/a": b"changed"}, True)
            self.assertFalse((root / "data/new").exists())
            self.assertEqual((root / "data/a").read_bytes(), b"first")
            persist_all(root, {"data/a": b"first"}, False)
            with self.assertRaises(ReferenceError):
                persist_all(root, {"data/missing": b"x"}, False)
            with self.assertRaises(ReferenceError):
                persist_all(root, {"../escape": b"x"}, True)

    def test_noninteger_frequency_is_not_silently_encoded(self):
        for number in (False, True, "1", None):
            with self.subTest(number=number), self.assertRaises(ReferenceError):
                encode([], [], [], [("the", number)], ("11" * 32, "22" * 32))


if __name__ == "__main__":
    unittest.main()
