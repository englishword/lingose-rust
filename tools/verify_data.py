"""Independently validate P2.1 resources against the pinned installed Python API.

This reader deliberately imports neither an encoder nor the layout probe reader.
Bulk comparisons share read-only connections, with source restoration disabled.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (BASELINE, ROOT, LIB_ROOT, ReferenceError, canonical, connect, fingerprints,
                       installed, json_text, main_error, no_restore, require,
                       require_baseline, sha256)

NULL = 0xffffffff
BASELINE_SHA256 = "9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01"
SUPPORTED = (1, 2, 1, 1)
FIELDS = ("ipa", "ips", "ism", "ipsm", "root_lemma", "meaning_en", "meaning_zh")


def decode(data, *, kind=None, versions=None):
    """Decode a complete v1 image, rejecting malformed data before exposing values.

    ``kind`` optionally enforces ``lexicon`` or ``frequency`` section separation.
    ``versions`` is a pair of hexadecimal versions, or a mapping containing
    ``lexicon_data_version`` and ``frequency_data_version``.
    """
    require(isinstance(data, (bytes, bytearray, memoryview)), "Image must be bytes")
    data = bytes(data)
    require(kind in (None, "lexicon", "frequency"), "Unknown resource kind")
    require(len(data) >= 112, "Truncated image header")
    require(data[:8] == b"LNGIDX01", "Invalid image magic")
    (version, string_count, entry_count, label_count, member_count, frequency_count,
     pool_bytes, lexicon_schema, frequency_schema, algorithm) = struct.unpack_from("<10I", data, 8)
    require((version, lexicon_schema, frequency_schema, algorithm) == SUPPORTED,
            "Unsupported image format/schema/algorithm version")
    if versions is not None:
        if isinstance(versions, dict):
            versions = (versions.get("lexicon_data_version"), versions.get("frequency_data_version"))
        require(isinstance(versions, (tuple, list)) and len(versions) == 2,
                "Expected two data versions")
        require(all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                    for value in versions), "Expected hexadecimal data versions")
        require(data[48:80].hex() == versions[0] and data[80:112].hex() == versions[1],
                "Incompatible source data version")
    require(label_count <= 32, "Category bitmap exceeds 32 labels")
    if kind == "lexicon":
        require(frequency_count == 0, "Lexicon resource contains frequency records")
    elif kind == "frequency":
        require(entry_count == label_count == member_count == 0,
                "Frequency resource contains lexicon sections")

    # Perform all count arithmetic before using counts to allocate/unpack arrays.
    entry_start = 112 + (string_count + 1) * 4
    label_start = entry_start + entry_count * 40
    member_start = label_start + label_count * 12
    frequency_start = member_start + member_count * 4
    pool_start = frequency_start + frequency_count * 8
    require(pool_start + pool_bytes == len(data), "Invalid image section lengths")
    offsets = struct.unpack_from(f"<{string_count + 1}I", data, 112)
    require(offsets[0] == 0 and offsets[-1] == pool_bytes, "Invalid string pool boundary")
    require(all(left <= right <= pool_bytes for left, right in zip(offsets, offsets[1:])),
            "String pool offsets are not monotonic or in bounds")
    strings = []
    previous = None
    for begin, end in zip(offsets, offsets[1:]):
        raw = data[pool_start + begin:pool_start + end]
        require(previous is None or previous < raw, "Strings are not unique UTF-8 byte sorted")
        try:
            strings.append(raw.decode("utf-8", errors="strict"))
        except UnicodeDecodeError as error:
            raise ReferenceError("Invalid UTF-8 in string pool") from error
        previous = raw

    def text(identifier, *, nullable=False):
        if nullable and identifier == NULL:
            return None
        require(identifier < string_count, "String ID out of bounds or unexpectedly null")
        return strings[identifier]

    entries = []
    previous = None
    valid_bits = (1 << label_count) - 1
    for index in range(entry_count):
        row = struct.unpack_from("<10I", data, entry_start + index * 40)
        record = [text(row[0])] + [text(value, nullable=True) for value in row[1:8]] + list(row[8:])
        word, ips, bits, state = record[0], record[2], row[8], row[9]
        require(word != "" and "\x00" not in word and word == word.strip(), "Invalid entry word")
        encoded = word.encode("utf-8")
        require(previous is None or previous < encoded, "Entries are not unique word-byte sorted")
        require(bits & ~valid_bits == 0, "Unregistered category bitmap bit")
        require(state in (0, 1, 2), "Unknown annotation state")
        require((state == 2 and isinstance(ips, str) and ips != "")
                or (state in (0, 1) and ips is None), "Annotation state and IPS disagree")
        entries.append(record)
        previous = encoded

    categories = []
    reconstructed_bits = [0] * entry_count
    seen_labels = set()
    next_member = 0
    for ordinal in range(label_count):
        label_id, begin, length = struct.unpack_from("<3I", data, label_start + ordinal * 12)
        label = text(label_id)
        require(label != "" and label not in seen_labels, "Empty or duplicate classification label")
        require(begin == next_member and length <= member_count - begin,
                "Category member ranges overlap, have gaps or exceed section")
        seen_labels.add(label)
        next_member += length
        positions = struct.unpack_from(f"<{length}I", data, member_start + begin * 4)
        require(all(position < entry_count for position in positions), "Category entry ID out of bounds")
        require(len(set(positions)) == length, "Duplicate category member")
        words = []
        for position in positions:
            reconstructed_bits[position] |= 1 << ordinal
            words.append(entries[position][0])
        categories.append((label, words))
    require(next_member == member_count, "Unreferenced category member records")
    require(all(row[8] == bits for row, bits in zip(entries, reconstructed_bits)),
            "Category member lists and entry bitmaps disagree")

    frequency = []
    previous = None
    for index in range(frequency_count):
        word_id, number = struct.unpack_from("<2I", data, frequency_start + index * 8)
        word = text(word_id)
        require(word != "" and "\x00" not in word and word == word.lower(),
                "Frequency key is empty, contains NUL or is not lowercase")
        encoded = word.encode("utf-8")
        require(previous is None or previous < encoded, "Frequency keys are not unique word-byte sorted")
        require(1 <= number <= 5062, "Frequency NUMBER outside 1..5062")
        frequency.append((word, number))
        previous = encoded
    return entries, categories, frequency


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _identity(path, expected):
    require(isinstance(expected, dict) and type(expected.get("bytes")) is int
            and isinstance(expected.get("sha256"), str), f"Invalid file identity: {path}")
    require(path.is_file() and path.stat().st_size == expected["bytes"]
            and sha256(path) == expected["sha256"], f"File length/SHA-256 differs: {path}")


def check_vectors(entries, categories):
    """Recheck all applicable frozen P0 snapshot query/list projections."""
    vectors = read_json(ROOT / "tests/fixtures/python-api-v1.json")
    words = {row[0]: row for row in entries}
    labels = [label for label, _ in categories]
    lists = dict(categories)
    checked = 0
    for case in vectors["cases"]:
        if case["source"] != "snapshot" or "error" in case["expected"]:
            continue
        call, expected = case["call"], case["expected"]
        name, args = call["api"], call.get("args", [])
        name = vectors["aliases"].get(name, name)
        if name == "labels":
            actual = labels
        elif name == "kind_list":
            actual = lists[args[0] if args else "CET4"]
            identity = expected["ordered_list"]
            require(len(actual) == identity["length"]
                    and hashlib.sha256(canonical(actual)).hexdigest() == identity["sha256"],
                    f"P0 ordered category list differs: {case['id']}")
            checked += 1
            continue
        elif name in ("IPA", "IPS", "ISM", "IPSM", "root_lemma", "meaning", "kind"):
            word = args[0]
            row = words.get(word)
            if row is None and word[0].isupper() and not any(char.isupper() for char in word[1:]):
                row = words.get(word.lower())
            if name in ("IPA", "IPS", "IPSM"):
                value = row[{"IPA": 1, "IPS": 2, "IPSM": 4}[name]] if row is not None else None
                actual = [] if value is None else [value]
            elif name == "kind":
                actual = row is not None and bool(row[8] & (1 << labels.index(args[1] if len(args) > 1 else "CET4")))
            else:
                position = {"ISM": 3, "root_lemma": 5,
                            "meaning": 7 if len(args) > 1 and args[1] == "zh" else 6}[name]
                actual = row[position] if row is not None else None
        else:
            continue
        require(actual == expected["value"], f"P0 query projection differs: {case['id']}")
        checked += 1
    return checked


def compare_source(entries, categories, frequency, baseline):
    """Compare every row using the installed implementation, not export SQL."""
    from lingose import annotation, query

    _, _, path, frequency_path = installed()
    started = time.perf_counter()
    with no_restore(), closing(connect(path)) as db, closing(connect(frequency_path)) as freq:
        require(db.execute("PRAGMA user_version").fetchone()[0] == 2, "Source lexicon schema differs")
        version = db.execute("SELECT data_version FROM build_info WHERE singleton=1").fetchone()[0]
        require(version == baseline["lexicon"]["build_info"]["data_version"], "Source lexicon data version differs")
        require([row[0] for row in db.execute("SELECT word FROM entry ORDER BY word COLLATE BINARY")]
                == [row[0] for row in entries], "Full precise word-key stream differs")
        labels = query._labels(db)
        require(labels == [label for label, _ in categories], "Source category registry differs")
        annotator = annotation._Annotator(db, set())
        stale = 0

        def available(field):
            if field["status"] != "available":
                return None
            require(isinstance(field["value"], str), "Source available public field is not a string")
            return field["value"]

        for index, row in enumerate(entries):
            result = query._lookup(db, version, row[0])
            require(result["matched_word"] == row[0] and result["match_type"] == "exact",
                    f"Source exact lookup differs: {row[0]!r}")
            selected = [pair for pair in result["pronunciations"] if pair["selected"]]
            require(len(selected) <= 1, "Source has multiple selected pronunciations")
            pronunciations = [None, None, None]
            if result["pronunciation_status"] == "available":
                require(len(selected) == 1, "Available source pronunciation has no selected pair")
                pair = selected[0]
                pronunciations = [available(pair[key]) for key in ("ipa", "ips", "ipsm")]
                if pair["ipsm"]["reason"] in ("stale_derivation", "missing_derivation"):
                    raw = db.execute("SELECT status FROM field_value WHERE pronunciation_id=? AND field_key='ipsm' AND scope='pronunciation'",
                                     (pair["pronunciation_id"],)).fetchone()
                    stale += int(raw is not None and raw[0] == "available")
            bits = 0
            for ordinal, label in enumerate(labels):
                field = result["kinds"][label]
                if field["status"] == "available":
                    require(type(field["value"]) is bool, "Source kind is not a JSON boolean")
                    if field["value"]:
                        bits |= 1 << ordinal
            match = annotator.exact(row[0])
            require(match.exists, "Source annotation exact lookup lost an entry")
            state = 2 if match.notation is not None else int(match.fallback)
            actual = [row[0], pronunciations[0], pronunciations[1], available(result["ism"]),
                      pronunciations[2], available(result["root_lemma"]),
                      available(result["meanings"]["en"]), available(result["meanings"]["zh"]),
                      bits, state]
            require(actual == row, f"Full source record differs: {row[0]!r}")
            require(match.notation == row[2], f"Source annotation IPS differs: {row[0]!r}")
            if (index + 1) % 10000 == 0:
                print(f"Checked {index + 1:,}/{len(entries):,} full installed-API records", file=sys.stderr, flush=True)
        for label, words in categories:
            require(query.kind_list(label) == words, f"Source full ordered category list differs: {label}")
        require(freq.execute("PRAGMA user_version").fetchone()[0] == 1, "Source frequency schema differs")
        metadata = dict(freq.execute("SELECT * FROM frequency_metadata WHERE singleton=1").fetchone())
        require(metadata == baseline["frequency"]["metadata"], "Source frequency metadata differs")
        expected = [tuple(row) for row in freq.execute("SELECT word,rank FROM frequency_word ORDER BY word COLLATE BINARY")]
        require(expected == frequency, "Full source frequency stream differs")
    return {"checked_records": len(entries), "checked_fields_per_record": 7,
            "checked_annotation_states": len(entries), "checked_categories": len(categories),
            "checked_category_members": sum(len(words) for _, words in categories),
            "checked_frequency_words": len(frequency), "source_invalid_selected_ipsm": stale,
            "source_comparison_seconds": round(time.perf_counter() - started, 3)}


def verify(directory):
    """Verify an artifact root without writing or repairing any artifact."""
    require(sha256(BASELINE) == BASELINE_SHA256, "Pinned P0 baseline file changed")
    baseline = require_baseline()
    directory = Path(directory).resolve()
    manifest = read_json(directory / "data/manifest.json")
    require(manifest.get("baseline_sha256") == BASELINE_SHA256, "Manifest baseline identity differs")
    for key, expected in zip(("format_version", "lexicon_schema", "frequency_schema", "ipsm_algorithm"), SUPPORTED):
        require(type(manifest.get(key)) is int and manifest[key] == expected, f"Manifest version differs: {key}")
    versions = (baseline["lexicon"]["build_info"]["data_version"], baseline["frequency"]["metadata"]["data_version"])
    require(tuple(manifest.get(key) for key in ("lexicon_data_version", "frequency_data_version")) == versions,
            "Manifest source data versions differ")
    require(set(manifest.get("resources", {})) == {"lexicon.bin", "frequency.bin"}, "Unexpected resource inventory")
    images = []
    for name, kind in (("lexicon.bin", "lexicon"), ("frequency.bin", "frequency")):
        path = directory / "data" / name
        identity = manifest["resources"][name]
        _identity(path, identity)
        raw = path.read_bytes()
        result = decode(raw, kind=kind, versions=versions)
        header = struct.unpack_from("<10I", raw, 8)
        actual = dict(zip(("strings", "entries", "labels", "members", "frequency_words", "pool_bytes"), header[1:7]))
        require(all(type(identity.get(key)) is int and identity[key] == value for key, value in actual.items()),
                f"Manifest resource counts differ: {name}")
        images.append(result)
    entries, categories, _ = images[0]
    frequency = images[1][2]
    require(manifest.get("category_lengths") == {label: len(words) for label, words in categories},
            "Manifest category lengths differ")
    require(manifest.get("annotation_states") == dict(Counter(str(row[9]) for row in entries)),
            "Manifest annotation states differ")
    require(manifest.get("available_fields") == {key: sum(row[position] is not None for row in entries)
                                                for position, key in enumerate(FIELDS, 1)},
            "Manifest available-field counts differ")
    generated = manifest.get("generated_files", {})
    require(set(generated) == {"data/SOURCES.json", "data/UPSTREAM-SOURCES.md", "src/data_meta.rs"},
            "Unexpected generated-file inventory")
    for name, identity in generated.items():
        _identity(directory / name, identity)
    check_metadata(directory, manifest, baseline)
    result = compare_source(entries, categories, frequency, baseline)
    require(type(manifest.get("invalid_selected_ipsm")) is int
            and manifest["invalid_selected_ipsm"] == result["source_invalid_selected_ipsm"],
            "Manifest stale selected IPSM count differs")
    result["checked_p0_snapshot_vectors"] = check_vectors(entries, categories)
    require(fingerprints() == baseline["fingerprints"], "Installed source changed during verification")
    result["source_files_unchanged"] = True
    result["resources"] = {name: {key: value[key] for key in ("bytes", "sha256")}
                           for name, value in manifest["resources"].items()}
    return result


def check_metadata(directory, manifest, baseline):
    """Check generated provenance/constants; kept independent of their renderer."""
    def identical(actual, expected, message):
        require(canonical(actual) == canonical(expected), message)

    for key, expected in (("exporter_version", 1), ("max_skip_top", 5062),
                          ("null_string_id", NULL), ("reference_version", "0.2.0")):
        identical(manifest.get(key), expected, f"Manifest metadata differs: {key}")
    input_identities = {"modules": baseline["fingerprints"]["modules"],
                        "resources": {name: {key: value for key, value in identity.items() if key != "path"}
                                      for name, identity in baseline["fingerprints"]["resources"].items()}}
    identical(manifest.get("input_identities"), input_identities, "Manifest input identities differ")
    sources = read_json(directory / "data/SOURCES.json")
    require(isinstance(sources, dict), "Source list must be an object")
    upstream = baseline["references"]["lingose-python"]
    for key, value in (("format_version", 1), ("author", "詹先觉 (ZHAN Xianjue)"),
                       ("homepage", "https://lingose.com/"),
                       ("repository", "https://github.com/englishword"),
                       ("license", "CC-BY-4.0"), ("license_file", "LICENSE")):
        identical(sources.get(key), value, f"Source attribution differs: {key}")
    identical(sources.get("reference"), {"distribution": "lingose", "version": "0.2.0",
              "source_commit": upstream["head"], "baseline_sha256": BASELINE_SHA256},
              "Source reference identity differs")
    identical(sources.get("upstream_notices"), {"file": "data/UPSTREAM-SOURCES.md", **upstream["files"]["SOURCES.md"]},
              "Upstream notice identity differs")
    _identity(directory / "data/UPSTREAM-SOURCES.md", upstream["files"]["SOURCES.md"])
    _identity(ROOT / "LICENSE", upstream["files"]["LICENSE"])
    resource_sources = sources.get("resources", {})
    require(set(resource_sources) == {"lexicon.bin", "frequency.bin"}, "Source resource inventory differs")
    for name in ("lexicon", "frequency"):
        identical(resource_sources[name + ".bin"].get("source_identity"),
                  input_identities["resources"][name + ".sqlite"], f"Source resource identity differs: {name}")
    lexicon = resource_sources["lexicon.bin"]
    identical(lexicon.get("snapshots"), json.loads(baseline["lexicon"]["build_info"]["manifest_json"])["sources"],
              "Source snapshot identities differ")
    require(set(lexicon.get("fields", {})) == {"ipa", "ips/ism/root_lemma", "ipsm", "meaning_en", "meaning_zh", "categories"},
            "Source field attribution inventory differs")
    require(all(isinstance(value, str) and value for value in lexicon["fields"].values()),
            "Missing source field attribution")
    identical(resource_sources["frequency.bin"].get("metadata"), baseline["frequency"]["metadata"],
              "Frequency source identity differs")
    third_party = sources.get("third_party", [])
    require(isinstance(third_party, list)
            and [item.get("name") for item in third_party] == ["Phonemizer", "eSpeak NG", "ECDICT", "Frequency List"]
            and all(isinstance(item.get("credit"), str) and item["credit"]
                    and isinstance(item.get("license_reference"), str) and item["license_reference"].startswith("https://")
                    for item in third_party), "Third-party credits/license references are incomplete")
    require(third_party[2].get("license") == "MIT", "ECDICT license attribution differs")

    def no_absolute_paths(value):
        if isinstance(value, dict):
            for child in value.values():
                no_absolute_paths(child)
        elif isinstance(value, list):
            for child in value:
                no_absolute_paths(child)
        elif isinstance(value, str):
            require(not re.match(r"^(?:[A-Za-z]:[\\/]|/|\\\\)", value),
                    "Local absolute path leaked into distributable metadata")

    no_absolute_paths(sources)
    no_absolute_paths(manifest)

    expected = {"FORMAT_VERSION": ("u32", 1), "LEXICON_SCHEMA_VERSION": ("u32", 2),
                "FREQUENCY_SCHEMA_VERSION": ("u32", 1), "IPSM_ALGORITHM_VERSION": ("u32", 1),
                "MAX_SKIP_TOP": ("u32", 5062)}
    for prefix in ("LEXICON", "FREQUENCY"):
        expected[prefix + "_DATA_VERSION"] = ("&str", manifest[prefix.lower() + "_data_version"])
        identity = manifest["resources"][prefix.lower() + ".bin"]
        expected[prefix + "_SHA256"] = ("&str", identity["sha256"])
        for key in ("bytes", "strings", "entries", "labels", "members", "frequency_words", "pool_bytes"):
            expected[prefix + "_" + key.upper()] = ("usize", identity[key])
    constants = {}
    declarations = "\n".join(line for line in (directory / "src/data_meta.rs").read_text(encoding="utf-8").splitlines()
                             if line.strip() and not line.lstrip().startswith("//")).split(";")
    require(declarations[-1].strip() == "", "Generated Rust metadata lacks final semicolon")
    for declaration in declarations[:-1]:
        match = re.fullmatch(r'\s*pub\(crate\)\s+const\s+([A-Z0-9_]+)\s*:\s*(u32|usize|&str)\s*=\s*([0-9]+|"[0-9a-f]+")\s*', declaration)
        require(match is not None, "Unexpected generated Rust metadata syntax")
        name, kind, value = match.groups()
        require(name not in constants, "Duplicate generated Rust metadata constant")
        constants[name] = (kind, json.loads(value))
    identical(constants, expected, "Generated Rust expected identities differ")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=LIB_ROOT, help="Artifact root containing data/ and src/")
    arguments = parser.parse_args()
    print(json_text(verify(arguments.output)))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
