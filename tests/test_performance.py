"""Small synthetic measurements exercise P4.2 gates without running benchmarks."""

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_performance as performance
from reference import ReferenceError


class PerformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.budget = json.loads((ROOT / "docs/performance-budget.json").read_bytes())
        cls.correctness = json.loads((ROOT / "docs/full-differential-verification.json").read_bytes())

    def report(self):
        labels = self.correctness["labels"]
        verified = [
            f"VERIFIED\t{words}\t{skip}\t"
            f"{self.correctness['artifacts'][f'reference-{words}-skip-{skip}.txt']['bytes']}"
            for words in (10000, 100000) for skip in (0, 1000, 5062)
        ]
        counters = {name: 1 for name in (
            "WorkingSetSize", "PeakWorkingSetSize", "PrivateUsage", "PeakPagefileUsage")}
        memory = {
            "before": dict(counters), "after": dict(counters),
            "delta": {name: 0 for name in counters}, "metrics": {},
            "complete_output_verified": False,
        }
        memory_samples = {"loaded": [deepcopy(memory) for _ in range(3)]}
        for skip in (0, 1000, 5062):
            sample = deepcopy(memory)
            sample["complete_output_verified"] = True
            sample["metrics"] = {f"annotation_100000_{skip}_ms": 1}
            memory_samples[f"annotation_{skip}"] = [deepcopy(sample) for _ in range(3)]
        return {
            "labels": labels,
            "corpus_and_query_inputs": {
                name: identity for name, identity in self.correctness["artifacts"].items()
                if name.startswith("reference-")
            },
            "raw_runtime_resources_bytes": self.budget["limits"]["raw_runtime_resources_bytes"],
            "samples": {
                "cold": [{"wall_ms": 1, "metrics": {"lexicon_initialization_ms": 1}}
                         for _ in range(7)],
                "frequency": [{"metrics": {"frequency_initialization_ms": 1}} for _ in range(7)],
                "warm": [{"metrics": {name: 1 for name in performance.expected_metrics(labels)},
                          "verified_annotations": list(verified)} for _ in range(7)],
                "concurrent": [{"metrics": {"concurrent_8_complete_annotations_ms": 1}}
                               for _ in range(7)],
            },
            "memory_samples": memory_samples,
        }

    def assert_rejected(self, report):
        try:
            result = performance.acceptance(report, self.budget)
        except ReferenceError:
            return
        self.assertFalse(result["passed"], "Incomplete evidence must not pass acceptance")
        self.assertTrue(result["failures"])

    def test_nanoseconds_microseconds_milliseconds_and_operation_counts(self):
        output = ("diagnostic\nMETRIC\tips_exact\t9000\t3\n"
                  "METRIC\tlabels_us\t9000\t3\n"
                  "METRIC\tannotation_10000_0_ms\t9000000\t3\n")
        self.assertEqual(performance.metrics(output), {
            "ips_exact": 3000, "labels_us": 3, "annotation_10000_0_ms": 3})

    def test_failed_child_keeps_metrics_error_and_exit_status(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            log = directory / "failed.json"
            code = "import sys; print('METRIC\\tx\\t12\\t1'); print('failed output comparison',file=sys.stderr); sys.exit(3)"
            with self.assertRaises(ReferenceError):
                performance.run([sys.executable, "-I", "-B", "-c", code], directory, os.environ.copy(), log)
            saved = json.loads(log.read_bytes())
            self.assertIn("METRIC\tx\t12\t1", saved["stdout"])
            self.assertIn("failed output comparison", saved["stderr"])
            self.assertEqual(saved["exit_code"], 3)

    def test_memory_child_early_exit_keeps_partial_handshake_and_counters(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            script = directory / "failed.py"
            script.write_text("import sys\nprint('HOLD\\tbefore-load',flush=True)\nsys.stdin.readline()\n"
                              "print('METRIC\\tannotation_100000_0_ms\\t12\\t1',flush=True)\n"
                              "print('incomplete annotation',file=sys.stderr)\nsys.exit(4)\n", encoding="utf-8")
            with patch.object(performance, "memory", return_value={"PrivateUsage": 123}), self.assertRaises(ReferenceError):
                performance.memory_sample(Path(sys.executable), str(script), 0, directory,
                                          os.environ.copy(), directory, 0)
            saved = json.loads(next(directory.glob("*-0-0.json")).read_bytes())
            self.assertIn("METRIC\tannotation_100000_0_ms", saved["stdout"])
            self.assertIn("incomplete annotation", saved["stderr"])
            self.assertEqual(saved["before"], {"PrivateUsage": 123})
            self.assertIsNone(saved["after"])
            self.assertEqual(saved["exit_code"], 4)

    def test_duplicate_negative_or_zero_operation_metrics_are_rejected(self):
        for output in ("METRIC\tx\t1\t1\nMETRIC\tx\t2\t1\n",
                       "METRIC\tx\t-1\t1\n", "METRIC\tx\t1\t0\n",
                       "METRIC\tx\t1\t-1\n"):
            with self.subTest(output=output), self.assertRaises(ReferenceError):
                performance.metrics(output)

    def test_complete_report_and_raw_resource_boundary(self):
        report = self.report()
        result = performance.acceptance(report, self.budget)
        self.assertTrue(result["passed"], result["failures"])
        self.assertEqual(result["statistics"]["ips_exact"]["samples"], [1] * 7)
        report["raw_runtime_resources_bytes"] += 1
        self.assert_rejected(report)

    def test_missing_workloads_or_output_verification_cannot_pass(self):
        for metric in ("ipa_exact", "kind_CET4_mixed", "labels_us", "all_kind_lists_ms",
                       "annotation_10000_0_ms", "annotation_100000_5062_ms"):
            with self.subTest(missing_metric=metric):
                report = self.report()
                del report["samples"]["warm"][0]["metrics"][metric]
                self.assert_rejected(report)
        for mode in ("cold", "frequency", "concurrent"):
            with self.subTest(missing_scenario=mode):
                report = self.report()
                report["samples"][mode][0]["metrics"] = {}
                self.assert_rejected(report)
        verified = self.report()["samples"]["warm"][0]["verified_annotations"]
        wrong_bytes = [verified[0].rsplit("\t", 1)[0] + "\t1"] + verified[1:]
        for verification in ([], [verified[0]] * 6, wrong_bytes):
            with self.subTest(annotation_verification=verification):
                report = self.report()
                report["samples"]["warm"][0]["verified_annotations"] = verification
                self.assert_rejected(report)
        with self.subTest(memory_output_unverified=True):
            report = self.report()
            report["memory_samples"]["annotation_1000"][0]["complete_output_verified"] = False
            self.assert_rejected(report)

    def test_fewer_than_seven_timings_or_three_memory_samples_fail(self):
        for mode in ("cold", "frequency", "warm", "concurrent"):
            with self.subTest(timing=mode):
                report = self.report()
                report["samples"][mode].pop()
                self.assert_rejected(report)
        for group in ("loaded", "annotation_0", "annotation_1000", "annotation_5062"):
            with self.subTest(memory=group):
                report = self.report()
                report["memory_samples"][group].pop()
                self.assert_rejected(report)

    def test_a_single_p95_outlier_is_not_hidden_by_a_small_mean(self):
        scenarios = (
            ("cold", "wall_ms", "cold_process_first_public_query_ms", None),
            ("cold", "lexicon_initialization_ms", "lexicon_initialization_including_index_ms", "metrics"),
            ("frequency", "frequency_initialization_ms", "frequency_initialization_ms", "metrics"),
            ("warm", "ips_exact", "hot_query_batch_ns_per_operation", "metrics"),
            ("warm", "labels_us", "labels_complete_owned_us", "metrics"),
            ("warm", "all_kind_lists_ms", "all_24_kind_lists_complete_owned_ms", "metrics"),
            ("warm", "annotation_10000_1000_ms", "annotate_ips_10000_words_ms_each_skip_0_1000_5062", "metrics"),
            ("warm", "annotation_100000_5062_ms", "annotate_ips_100000_words_ms_each_skip_0_1000_5062", "metrics"),
        )
        for mode, name, budget_name, field in scenarios:
            with self.subTest(metric=name):
                report = self.report()
                limits = self.budget["limits"][budget_name]
                outlier = limits["p95"] + 1
                sample = report["samples"][mode][-1]
                (sample if field is None else sample[field])[name] = outlier
                self.assertLess((6 + outlier) / 7, limits["median"])
                result = performance.acceptance(report, self.budget)
                self.assertFalse(result["passed"])
                statistic = budget_name if field is None else name
                self.assertEqual(result["statistics"][statistic]["p95_nearest_rank"], outlier)

    def test_each_absolute_memory_peak_is_checked_without_averaging(self):
        scenarios = [("loaded", counter, limit) for counter, limit in (
            ("WorkingSetSize", "loaded_process_working_set_bytes"),
            ("PrivateUsage", "loaded_process_private_commit_bytes"),
            ("PeakPagefileUsage", "loaded_process_peak_private_commit_bytes"))]
        scenarios += [(f"annotation_{skip}", counter, limit) for skip in (0, 1000, 5062)
                      for counter, limit in (
                          ("PeakWorkingSetSize", "annotation_100000_peak_working_set_bytes"),
                          ("PeakPagefileUsage", "annotation_100000_peak_private_commit_bytes"))]
        for group, counter, limit in scenarios:
            for index in range(3):
                with self.subTest(group=group, counter=counter, sample=index):
                    report = self.report()
                    sample = report["memory_samples"][group][index]
                    sample["before"][counter] = self.budget["limits"][limit]
                    sample["after"][counter] = self.budget["limits"][limit] + 1
                    sample["delta"][counter] = 1
                    result = performance.acceptance(report, self.budget)
                    self.assertFalse(result["passed"])
                    self.assertTrue(any(f"{group}[{index}] {counter}:" in failure
                                        for failure in result["failures"]))


if __name__ == "__main__":
    unittest.main()
