"""Validate the oracle adapter and rare rules against disposable fixtures."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from capture_api_vectors import build_fixture, evaluate, fixture_paths, fixture_spec
from reference import BASELINE, ReferenceError


class VectorOracleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        self.path, self.frequency = directory / "main.sqlite", directory / "frequency.sqlite"
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        build_fixture(self.path, self.frequency, baseline, fixture_spec())
        self.context = fixture_paths(self.path, self.frequency)
        self.context.__enter__()
        self.addCleanup(self.context.__exit__, None, None, None)

    def value(self, api, *args, **kwargs):
        return evaluate({"api":api,"args":list(args),"kwargs":kwargs})["value"]

    def test_aliases_project_the_selected_pronunciation(self):
        self.assertEqual(self.value("ipa","present"), ["selected"])
        self.assertEqual(self.value("IPS","present"), ["prėṡent"])
        self.assertEqual(self.value("ips","present"), self.value("IPS","present"))

    def test_missing_and_stale_fields_are_not_filled(self):
        self.assertEqual(self.value("IPA","pair"), ["known-ipa"])
        self.assertEqual(self.value("IPS","pair"), [])
        self.assertEqual(self.value("IPSM","apple"), ["app-le"])
        self.assertEqual(self.value("IPSM","stale"), [])
        self.assertEqual(self.value("IPSM","noderivation"), [])

    def test_exact_pending_blocks_but_annotation_has_its_own_case_fallback(self):
        self.assertEqual(self.value("IPS","Apple"), [])
        self.assertEqual(self.value("IPS","APPLE"), [])
        self.assertEqual(self.value("annotate_ips","Apple APPLE aPpLe"), "[Apple] APPLE aPpLe")

    def test_context_and_unicode_clusters(self):
        self.assertEqual(self.value("annotate_ips", 'the "apple" the, apple'), 'ṫhē "apple" ṫhe̊, apple')
        self.assertEqual(self.value("annotate_ips", "WHALE WHIM YUM"), "W̅ℍĀLE W̊ℍI̊M Y̊U̇M")
        self.assertEqual(self.value("annotate_ips", "bad BAD"), "[bad] [BAD]")

    def test_unavailable_exact_entries_block_real_fallback_candidates(self):
        self.assertEqual(self.value("annotate_ips", "walks plays baked don't is"), "[walks] [plays] [baked] [don't] [is]")
        self.assertEqual(self.value("IPS", "walk"), ["wàlk"])
        self.assertEqual(self.value("IPS", "play"), ["plāy"])
        self.assertEqual(self.value("IPS", "bake"), ["bāke"])
        self.assertEqual(self.value("IPS", "i"), ["ī"])

    def test_category_order_and_false_are_preserved(self):
        self.assertEqual(self.value("kind_list"), ["zeta","apple","orphan"])
        self.assertIs(self.value("kind","apple","CET6"), False)

    def test_frequency_inclusive_and_large_integer_clamping(self):
        self.assertEqual(self.value("annotate_ips","the abandon abandoned",skip_top=2), "the abandon abandoned")
        self.assertEqual(self.value("annotate_ips","the abandon",skip_top=1), "the åbando̊n")
        large = {"$integer":"1"+"0"*100}
        self.assertEqual(self.value("annotate_ips","tail",skip_top=large), self.value("annotate_ips","tail",skip_top=5062))

    def test_unexpected_error_cannot_be_saved_as_a_successful_vector(self):
        with fixture_paths(self.path.with_name("absent.sqlite"),self.frequency):
            with self.assertRaises(ReferenceError):
                evaluate({"api":"IPS","args":["apple"]})
            self.assertEqual(evaluate({"api":"IPS","args":["apple"],"error":"LexiconDataError"}), {"error":"LexiconDataError"})

    def test_unused_resources_are_not_opened(self):
        missing = self.path.with_name("absent.sqlite")
        with fixture_paths(missing,missing):
            self.assertEqual(self.value("annotate_ips","中文 123 e\u0301",skip_top=1), "中文 123 e\u0301")
        with fixture_paths(self.path,missing):
            self.assertEqual(self.value("annotate_ips","apple",skip_top=0), "apple")


if __name__=="__main__":
    unittest.main()
