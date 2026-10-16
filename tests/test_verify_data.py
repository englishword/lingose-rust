"""Corruption fixtures for the independent production image reader.

Fixtures are assembled directly from the documented wire sections. They do not
use the exporter, its projection, or either development-probe implementation.
"""

import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from reference import ReferenceError
from verify_data import NULL, ROOT, _identity, check_metadata, decode, read_json

VERSIONS = ("11" * 32, "22" * 32)


def wire(strings, rows=(), categories=(), members=(), frequency=()):
    """Frame already-numbered wire records; no business projection/ID mapping."""
    pool = b"".join(strings)
    offsets = [0]
    for text in strings:
        offsets.append(offsets[-1] + len(text))
    header = (1, len(strings), len(rows), len(categories), len(members), len(frequency), len(pool), 2, 1, 1)
    return b"".join((b"LNGIDX01", struct.pack("<10I", *header),
                     bytes.fromhex(VERSIONS[0]), bytes.fromhex(VERSIONS[1]),
                     struct.pack(f"<{len(offsets)}I", *offsets),
                     b"".join(struct.pack("<10I", *row) for row in rows),
                     b"".join(struct.pack("<3I", *row) for row in categories),
                     struct.pack(f"<{len(members)}I", *members),
                     b"".join(struct.pack("<2I", *row) for row in frequency), pool))


def lexicon():
    strings = (b"", b"A", b"CET4", b"a\nb", b"apple", "e\u0301".encode(), b"z", "苹果".encode())
    rows = ((1, NULL, NULL, 0, NULL, NULL, 3, NULL, 1, 0),
            (4, 5, 4, NULL, 0, 4, NULL, 7, 1, 2),
            (6, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 1))
    # A business list can intentionally differ from entry byte ordering.
    return wire(strings, rows, ((2, 0, 2),), (1, 0))


def frequency():
    return wire((b"a lot", b"can't", b"z"), frequency=((0, 29), (1, 1), (2, 5062)))


def changed_u32(raw, position, value):
    result = bytearray(raw)
    struct.pack_into("<I", result, position, value)
    return bytes(result)


def section_positions(raw):
    _, strings, entries, labels, members, frequencies, pool, *_ = struct.unpack_from("<10I", raw, 8)
    entry = 112 + (strings + 1) * 4
    label = entry + entries * 40
    member = label + labels * 12
    freq = member + members * 4
    return entry, label, member, freq, freq + frequencies * 8


class IndependentDecodeTests(unittest.TestCase):
    def rejected(self, raw, *message, **kwargs):
        with self.assertRaisesRegex(ReferenceError, message[0] if message else "."):
            decode(raw, **kwargs)

    def test_complete_lexicon_preserves_null_empty_combining_unicode_and_three_states(self):
        entries, categories, freq = decode(lexicon(), kind="lexicon", versions=VERSIONS)
        self.assertEqual(entries, [["A", None, None, "", None, None, "a\nb", None, 1, 0],
                                   ["apple", "e\u0301", "apple", None, "", "apple", None, "苹果", 1, 2],
                                   ["z", None, None, None, None, None, None, None, 0, 1]])
        self.assertEqual(categories, [("CET4", ["apple", "A"])])
        self.assertEqual(freq, [])

    def test_frequency_retains_phrases_punctuation_and_original_number_gaps(self):
        self.assertEqual(decode(frequency(), kind="frequency", versions={
            "lexicon_data_version": VERSIONS[0], "frequency_data_version": VERSIONS[1]}),
            ([], [], [("a lot", 29), ("can't", 1), ("z", 5062)]))

    def test_empty_generic_image_has_a_real_zero_offset(self):
        self.assertEqual(decode(wire(())), ([], [], []))

    def test_short_header_trailing_bytes_and_truncated_sections(self):
        raw = lexicon()
        for corrupt in (b"", raw[:111], raw[:-1], raw + b"x"):
            with self.subTest(length=len(corrupt)):
                self.rejected(corrupt)

    def test_magic_all_schema_versions_and_algorithm_are_checked(self):
        self.rejected(b"WRONG001" + lexicon()[8:], "magic")
        for position in (8, 36, 40, 44):
            with self.subTest(position=position):
                self.rejected(changed_u32(lexicon(), position, 999), "version")

    def test_source_versions_are_not_merely_required_to_be_nonzero(self):
        raw = bytearray(lexicon())
        raw[49] ^= 1
        self.rejected(raw, "data version", versions=VERSIONS)
        self.rejected(lexicon(), versions=("11", "22"))
        self.rejected(lexicon(), versions=(None, VERSIONS[1]))

    def test_count_overflow_and_all_count_driven_sections_are_bounded(self):
        for position in (12, 16, 20, 24, 28, 32):
            with self.subTest(position=position):
                self.rejected(changed_u32(lexicon(), position, NULL))

    def test_each_resource_enforces_section_separation(self):
        self.rejected(lexicon(), kind="frequency")
        self.rejected(frequency(), kind="lexicon")
        self.rejected(lexicon(), kind="unknown")

    def test_offsets_begin_zero_end_at_pool_and_never_decrease(self):
        raw = lexicon()
        pool_bytes = struct.unpack_from("<I", raw, 32)[0]
        for position, value in ((112, 1), (112 + 8 * 4, pool_bytes - 1),
                                (112 + 3 * 4, pool_bytes + 1), (112 + 4 * 4, 0)):
            with self.subTest(position=position):
                self.rejected(changed_u32(raw, position, value), "pool")

    def test_string_pool_must_be_valid_utf8_unique_and_byte_sorted(self):
        for strings in ((b"\xff",), (b"a", b"a"), (b"z", b"a"),
                        (b"", b""), (b"\xc0\x80",), (b"\xed\xa0\x80",)):
            with self.subTest(strings=strings):
                self.rejected(wire(strings))

    def test_all_eight_string_ids_are_bounds_checked_and_word_cannot_be_null(self):
        raw = lexicon()
        entry = section_positions(raw)[0]
        self.rejected(changed_u32(raw, entry, NULL), "String ID")
        for column in range(8):
            with self.subTest(column=column):
                self.rejected(changed_u32(raw, entry + column * 4, 8), "String ID")

    def test_entry_words_must_be_nonempty_unique_sorted_without_nul_or_padding(self):
        raw = lexicon()
        entry = section_positions(raw)[0]
        for position, word_id in ((entry, 0), (entry, 6), (entry + 40, 1)):
            self.rejected(changed_u32(raw, position, word_id))
        for word in (b" ", b" a", b"a ", b"a\x00"):
            row = (0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 1)
            self.rejected(wire((word,), (row,)), "word")

    def test_annotation_state_range_and_ips_consistency(self):
        raw = lexicon()
        entry = section_positions(raw)[0]
        for position, value in ((entry + 36, 3), (entry + 36, 2),
                                (entry + 40 + 36, 1), (entry + 8, 0),
                                (entry + 40 + 8, 0), (entry + 40 + 8, NULL)):
            with self.subTest(position=position, value=value):
                self.rejected(changed_u32(raw, position, value), "Annotation|annotation")

    def test_label_id_nonempty_unique_and_no_more_than_32_labels(self):
        raw = lexicon()
        label = section_positions(raw)[1]
        self.rejected(changed_u32(raw, label, NULL), "String ID")
        self.rejected(changed_u32(raw, label, 0), "label")
        self.rejected(wire((b"CET4",), categories=((0, 0, 0), (0, 0, 0))), "label")
        self.rejected(wire((b"x",), categories=((0, 0, 0),) * 33), "32")

    def test_membership_ranges_must_partition_member_section(self):
        raw = lexicon()
        label = section_positions(raw)[1]
        self.rejected(changed_u32(raw, label + 4, 1), "ranges")
        self.rejected(changed_u32(raw, label + 8, 3), "ranges")
        self.rejected(changed_u32(raw, label + 8, 1), "Unreferenced")
        # The second label cannot overlap the first label's already consumed span.
        rows = ((1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 3, 1),)
        self.rejected(wire((b"A", b"word", b"z"), rows, ((0, 0, 1), (2, 0, 1)), (0, 0)), "ranges")

    def test_member_ids_unique_and_bounded_with_exact_bitmap_equivalence(self):
        raw = lexicon()
        entry, _, member, _, _ = section_positions(raw)
        self.rejected(changed_u32(raw, member, 3), "entry ID")
        self.rejected(changed_u32(raw, member, 0), "Duplicate")
        self.rejected(changed_u32(raw, entry + 32, 0), "bitmaps")
        self.rejected(changed_u32(raw, entry + 32, 2), "bitmap bit")

    def test_frequency_string_ids_lowercase_order_uniqueness_and_number_range(self):
        raw = frequency()
        freq = section_positions(raw)[3]
        for position, value in ((freq, NULL), (freq, 3), (freq, 2),
                                (freq + 8, 0), (freq + 4, 0), (freq + 4, 5063)):
            with self.subTest(position=position, value=value):
                self.rejected(changed_u32(raw, position, value))
        for word in (b"", b"Apple", b"a\x00"):
            self.rejected(wire((word,), frequency=((0, 1),)))


class MetadataGuards(unittest.TestCase):
    def test_identity_rejects_same_size_tampering_missing_files_and_boolean_length(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resource.bin"
            path.write_bytes(b"original")
            expected = {"bytes": 8, "sha256": hashlib.sha256(b"original").hexdigest()}
            _identity(path, expected)
            path.write_bytes(b"tampered")
            with self.assertRaises(ReferenceError):
                _identity(path, expected)
            path.unlink()
            with self.assertRaises(ReferenceError):
                _identity(path, expected)
            path.write_bytes(b"x")
            with self.assertRaises(ReferenceError):
                _identity(path, {"bytes": True, "sha256": hashlib.sha256(b"x").hexdigest()})

    def test_duplicate_json_keys_are_rejected_instead_of_silently_shadowed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text('{"sha256":"first","sha256":"second"}')
            with self.assertRaisesRegex(ReferenceError, "Duplicate JSON key"):
                read_json(path)
            path.write_text(json.dumps({"zero": 0, "false": False, "null": None}))
            self.assertEqual(read_json(path), {"zero": 0, "false": False, "null": None})


class MetadataSemanticGuards(unittest.TestCase):
    """Tamper small disposable copies, never the installed reference or exports."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        for name in ("data/SOURCES.json", "data/UPSTREAM-SOURCES.md", "src/data_meta.rs"):
            target = self.directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.manifest = read_json(ROOT / "data/manifest.json")
        self.baseline = read_json(ROOT / "docs/reference-baseline.json")

    def check(self):
        check_metadata(self.directory, self.manifest, self.baseline)

    def replace_sources(self, value):
        path = self.directory / "data/SOURCES.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        # A file checksum alone is insufficient when the manifest changes too.
        self.manifest["generated_files"]["data/SOURCES.json"] = {
            "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    def test_valid_pinned_metadata_and_wrapped_rust_declarations(self):
        self.check()
        path = self.directory / "src/data_meta.rs"
        path.write_text(path.read_text(encoding="utf-8").replace(' = "', ' =\n    "'), encoding="utf-8")
        self.check()

    def test_changed_or_duplicate_rust_constants_are_rejected(self):
        path = self.directory / "src/data_meta.rs"
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace("LEXICON_ENTRIES: usize = 50335", "LEXICON_ENTRIES: usize = 50336"), encoding="utf-8")
        with self.assertRaisesRegex(ReferenceError, "expected identities"):
            self.check()
        path.write_text(original + "pub(crate) const FORMAT_VERSION: u32 = 1;\n", encoding="utf-8")
        with self.assertRaisesRegex(ReferenceError, "Duplicate"):
            self.check()

    def test_semantic_source_identity_tamper_is_rejected_even_with_rehashed_manifest(self):
        value = read_json(self.directory / "data/SOURCES.json")
        value["resources"]["lexicon.bin"]["source_identity"]["sha256"] = "0" * 64
        self.replace_sources(value)
        with self.assertRaisesRegex(ReferenceError, "resource identity"):
            self.check()

    def test_source_snapshot_and_local_path_tampering_is_rejected(self):
        value = read_json(self.directory / "data/SOURCES.json")
        original = json.loads(json.dumps(value))
        value["resources"]["lexicon.bin"]["snapshots"][0]["sha256"] = "0" * 64
        self.replace_sources(value)
        with self.assertRaisesRegex(ReferenceError, "snapshot identities"):
            self.check()
        original["unexpected_local_path"] = "C:/private/not-distributable"
        self.replace_sources(original)
        with self.assertRaisesRegex(ReferenceError, "absolute path"):
            self.check()

    def test_upstream_notice_and_input_identity_tampering_is_rejected(self):
        notice = self.directory / "data/UPSTREAM-SOURCES.md"
        original = notice.read_bytes()
        notice.write_bytes(original.replace(b"Lingose", b"Changed", 1))
        with self.assertRaisesRegex(ReferenceError, "SHA-256"):
            self.check()
        notice.write_bytes(original)
        self.manifest["input_identities"]["modules"]["query.py"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ReferenceError, "input identities"):
            self.check()

    def test_boolean_version_cannot_impersonate_integer_one(self):
        value = read_json(self.directory / "data/SOURCES.json")
        value["format_version"] = True
        self.replace_sources(value)
        with self.assertRaisesRegex(ReferenceError, "attribution"):
            self.check()


if __name__ == "__main__":
    unittest.main()
