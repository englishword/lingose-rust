"""Ensure P4 comparison fails closed on result drift and broken wire output."""

from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_full_differential as diff
from reference import ReferenceError


class FullDifferentialTests(unittest.TestCase):
    def check_streams(self, wanted, actual, suffix=b"", truncate=False):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            requests, expected, found = (directory / name for name in ("requests", "expected", "actual"))
            header = diff.MAGIC + struct.pack("<I", 1)
            with requests.open("wb") as stream:
                stream.write(header)
                diff.request(stream, 0, "apple")
            for path, value in ((expected, wanted), (found, actual)):
                with path.open("wb") as stream:
                    stream.write(header)
                    diff.write_value(stream, value)
            found.write_bytes(found.read_bytes()[:-1] if truncate else found.read_bytes() + suffix)
            return diff.compare(requests, expected, found)

    def test_complete_lists_reject_interior_reordering(self):
        self.assertEqual(self.check_streams(["a", "b", "c", "d"], ["a", "b", "c", "d"]), {"ipa": 1})
        with self.assertRaisesRegex(ReferenceError, "Difference #0"):
            self.check_streams(["a", "b", "c", "d"], ["a", "c", "b", "d"])

    def test_unicode_and_full_text_are_compared_without_normalization(self):
        with self.assertRaisesRegex(ReferenceError, "Difference #0"):
            self.check_streams("start e\u0301\nend", "start é\nend")
        with self.assertRaisesRegex(ReferenceError, "Difference #0"):
            self.check_streams("x" * 100000 + "tail", "x" * 100000 + "fail")

    def test_empty_unknown_results_are_not_resource_errors(self):
        for empty in (None, [], False, ""):
            with self.subTest(empty=empty), self.assertRaisesRegex(ReferenceError, "Difference #0"):
                self.check_streams(empty, {"error": "Data"})

    def test_truncation_and_trailing_records_are_rejected(self):
        with self.assertRaisesRegex(ReferenceError, "Truncated"):
            self.check_streams(["complete"], ["complete"], truncate=True)
        with self.assertRaisesRegex(ReferenceError, "Trailing"):
            self.check_streams(["complete"], ["complete"], suffix=b"\0")

    def test_unbounded_thresholds_are_adapted_after_comparison(self):
        import io
        for value, expected in ((10 ** 100, 5062), (-10 ** 100, -1), (0, 0), (1000, 1000), (5062, 5062)):
            with self.subTest(value=value):
                stream = io.BytesIO()
                diff.request(stream, 17, "apple", threshold=value)
                stream.seek(0)
                self.assertEqual(diff.read_request(stream), (17, "apple", "", expected))


if __name__ == "__main__":
    unittest.main()
