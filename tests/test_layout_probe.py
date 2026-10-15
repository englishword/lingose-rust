"""Meaningful representation and overwrite guards for the development probe."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from check_layout_probe import decode
from prepare_layout_probe import encode, persist
from reference import ReferenceError


class LayoutProbeTests(unittest.TestCase):
    def test_roundtrip_preserves_null_empty_unicode_membership_and_fallback(self):
        baseline = {"lexicon":{"build_info":{"data_version":"11"*32}},
                    "frequency":{"metadata":{"data_version":"22"*32}}}
        entries = [["Apple",None,None,"",None,None,"a\nb",None,0,0],
                   ["apple","æ", "a\u0304pple",None,"", "apple",None,"苹果",1,2],
                   ["z",None,None,None,None,None,None,None,0,1]]
        # Category order is deliberately different from lexical entry order.
        raw,_ = encode(entries,["CET4"],[[1]],[("a lot",29),("z",31)],baseline)
        decoded,labels,frequency = decode(raw)
        self.assertEqual(decoded,entries)
        self.assertEqual(labels,[("CET4",["apple"])])
        self.assertEqual(frequency,[("a lot",29),("z",31)])

    def test_probe_artifacts_refuse_missing_or_changed_existing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with self.assertRaises(ReferenceError):
                persist(target,"data",b"first",False)
            persist(target,"data",b"first",True)
            persist(target,"data",b"first",False)
            with self.assertRaises(ReferenceError):
                persist(target,"data",b"replacement",True)
            self.assertEqual((target/"data").read_bytes(),b"first")


if __name__ == "__main__":
    unittest.main()
