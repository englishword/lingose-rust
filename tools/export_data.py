"""Export the pinned installed Lingose snapshot into reproducible v1 resources.

Development only. No probe artifacts, restoration, downloads, or source writes.
--write creates missing files; both modes refuse to replace different content.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (BASELINE, ROOT, LIB_ROOT, canonical, connect, file_record, fingerprints,
                       installed, json_text, main_error, no_restore, require,
                       require_baseline, sha256)

BASELINE_SHA256 = "9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01"
NULL = 0xffffffff
STATUSES = {"available", "missing", "conflict", "pending_review", "invalid"}
TEXT_FIELDS = {"ipa": 1, "ips": 2, "ism": 3, "ipsm": 4,
               "root_lemma": 5, "meaning_en": 6, "meaning_zh": 7}


@dataclass
class Projection:
    entries: list
    labels: list
    lists: list
    frequency: list
    invalid_selected_ipsm: int


def available(row, expected_type):
    """Do not conflate unavailable, empty, false, zero, or invalid JSON types."""
    if row is None:
        return None
    require(row["status"] in STATUSES, "Unrecognized field status")
    if row["status"] != "available":
        require(row["value_json"] is None, "Unavailable field contains an adopted value")
        return None
    value = json.loads(row["value_json"])
    require(type(value) is expected_type, f"Invalid available {expected_type.__name__} field")
    return value


def valid_ipsm(source, dependency, values):
    """Follow the stored dependency identities; never recalculate a candidate."""
    if dependency is None or dependency["algorithm_version"] != "1":
        return False
    ips_row = values.get(dependency["ips_value_id"])
    ism_row = values.get(dependency["ism_value_id"])
    if ips_row is None or ism_row is None:
        return False
    if (dependency["result_value_id"] != source["value_id"]
            or ips_row["entry_id"] != source["entry_id"] or ism_row["entry_id"] != source["entry_id"]
            or ips_row["field_key"] != "ips" or ips_row["scope"] != "pronunciation"
            or ism_row["field_key"] != "ism" or ism_row["scope"] != "entry"):
        return False
    ips, ism = available(ips_row, str), available(ism_row, str)
    return (ips is not None and ism is not None
            and hashlib.sha256(ips.encode("utf-8")).hexdigest() == dependency["ips_sha256"]
            and hashlib.sha256(ism.encode("utf-8")).hexdigest() == dependency["ism_sha256"])


def project(db, frequency) -> Projection:
    """Read each required field once, retaining every exact entry and its state.

    Connections are supplied so small disposable databases can exercise states
    absent from the pinned snapshot. The CLI separately enforces source identity.
    """
    require(db.execute("PRAGMA query_only").fetchone()[0] == 1, "Lexicon must be read-only")
    require(frequency.execute("PRAGMA query_only").fetchone()[0] == 1, "Frequency must be read-only")
    require(db.execute("PRAGMA user_version").fetchone()[0] == 2, "Lexicon schema drift")
    require(frequency.execute("PRAGMA user_version").fetchone()[0] == 1, "Frequency schema drift")
    base = list(db.execute("""SELECT e.entry_id,e.word,s.status,s.reason,s.selected_id,
        p.pronunciation_id FROM entry e
        LEFT JOIN pronunciation_set s ON s.entry_id=e.entry_id
        LEFT JOIN pronunciation p ON p.pronunciation_id=s.selected_id AND p.entry_id=e.entry_id
        ORDER BY e.word COLLATE BINARY"""))
    ids = {row["entry_id"]: index for index, row in enumerate(base)}
    entries = [[row["word"], *([None] * 7), 0, 0] for row in base]
    words = {entry[0]: index for index, entry in enumerate(entries)}
    require(len(ids) == len(words) == len(base), "Duplicate exact entry")
    labels = [row[0] for row in db.execute("SELECT label FROM field_definition WHERE domain='category' AND scope='entry' ORDER BY ordinal,field_key")]
    require(len(labels) == len(set(labels)) <= 32, "Unsupported category registry")
    positions = {"kind:" + label: index for index, label in enumerate(labels)}
    previous = None
    # Keep only adopted public fields and boolean categories, never candidates.
    for row in db.execute("""SELECT * FROM field_value WHERE scope='entry' AND
        (field_key IN ('ism','root_lemma','meaning_en','meaning_zh') OR field_key LIKE 'kind:%')
        ORDER BY entry_id,field_key"""):
        require(row["entry_id"] in ids, "Orphan entry field")
        key = (row["entry_id"], row["field_key"])
        require(key != previous, "Duplicate entry field")
        previous = key
        if row["field_key"] in TEXT_FIELDS:
            require(row["value_type"] == "text", "Wrong text field definition")
            entries[ids[row["entry_id"]]][TEXT_FIELDS[row["field_key"]]] = available(row, str)
        else:
            field = row["field_key"]
            require(field in positions and row["value_type"] == "boolean", "Invalid category definition")
            value = available(row, bool)
            if value is True:
                require(row["value_json"] == "true", "Python kind/kind_list membership differs")
                entries[ids[row["entry_id"]]][8] |= 1 << positions[field]
    selected = {}
    for row in db.execute("""SELECT f.* FROM pronunciation_set s
        JOIN pronunciation p ON p.pronunciation_id=s.selected_id AND p.entry_id=s.entry_id
        JOIN field_value f ON f.pronunciation_id=p.pronunciation_id AND f.entry_id=s.entry_id
        WHERE f.scope='pronunciation' AND f.field_key IN ('ipa','ips','ipsm')"""):
        key = (row["entry_id"], row["field_key"])
        require(key not in selected and row["value_type"] == "text", "Invalid selected field")
        selected[key] = row
    derivations = {row["result_value_id"]: row for row in db.execute("SELECT * FROM ipsm_derivation")}
    dependencies = {row["value_id"]: row for row in db.execute(
        "SELECT * FROM field_value WHERE (scope='entry' AND field_key='ism') OR (scope='pronunciation' AND field_key='ips')")}
    stale = 0
    for index, row in enumerate(base):
        require(row["status"] in STATUSES, "Entry missing a valid pronunciation set")
        key = row["entry_id"]
        if row["status"] == "available":
            require(row["selected_id"] is not None and row["pronunciation_id"] is not None,
                    "Available set lacks an owned selected pronunciation")
            ips = selected.get((key, "ips"))
            require(ips is not None, "Selected pronunciation lacks IPS field")
            for field in ("ipa", "ips", "ipsm"):
                source = selected.get((key, field))
                value = available(source, str)
                if field == "ipsm" and value is not None:
                    if not valid_ipsm(source, derivations.get(source["value_id"]), dependencies):
                        stale += 1
                        value = None
                entries[index][TEXT_FIELDS[field]] = value
            if ips["status"] == "available":
                require(entries[index][2] != "", "Available annotation IPS must be nonempty")
                entries[index][9] = 2
            else:
                entries[index][9] = int(ips["status"] == "missing" and ips["reason"] == "source_record_missing")
        else:
            require(row["selected_id"] is None, "Unavailable set has a selected pronunciation")
            entries[index][9] = int(row["status"] == "missing" and row["reason"] == "source_record_missing")
    lists = []
    # Preserve the pinned Python sorting SQL on the supplied read-only connection.
    for ordinal, label in enumerate(labels):
        members = [row[0] for row in db.execute("""SELECT e.word FROM field_value k
            JOIN entry e ON e.entry_id=k.entry_id
            LEFT JOIN field_value root ON root.entry_id=e.entry_id AND root.field_key='root_lemma' AND root.scope='entry'
            LEFT JOIN field_value rank ON rank.entry_id=e.entry_id AND rank.field_key='rank' AND rank.scope='entry'
            WHERE k.field_key=? AND k.scope='entry' AND k.status='available' AND k.value_json='true'
            ORDER BY CASE WHEN root.status='available' AND rank.status='available' THEN 0 ELSE 1 END,
                CASE WHEN root.status='available' THEN json_extract(root.value_json,'$') ELSE '' END,
                CASE WHEN rank.status='available' THEN json_extract(rank.value_json,'$') ELSE '' END,
                e.word COLLATE BINARY""", ("kind:" + label,))]
        expected = {entry[0] for entry in entries if entry[8] & (1 << ordinal)}
        require(len(members) == len(set(members)) and set(members) == expected,
                "Category membership and Python list differ")
        lists.append([words[word] for word in members])
    frequencies = [list(row) for row in frequency.execute("SELECT word,rank FROM frequency_word ORDER BY word COLLATE BINARY")]
    for word, number in frequencies:
        require(type(word) is str and word != "" and word == word.lower(), "Invalid frequency key")
        require(type(number) is int and 1 <= number <= 5062, "Invalid original NUMBER threshold")
    return Projection(entries, labels, lists, frequencies, stale)


def encode(entries, labels, lists, frequency, versions):
    """Encode fixed v1; the independent verifier must validate the result."""
    require(len(labels) == len(lists) <= 32, "Label/list count mismatch")
    strings = {value for row in entries for value in row[:8] if value is not None}
    strings.update(labels)
    strings.update(word for word, _ in frequency)
    require(all(type(value) is str for value in strings), "Image strings must be text")
    strings = sorted(strings, key=lambda value: value.encode("utf-8"))
    indices = {value: index for index, value in enumerate(strings)}
    pool = bytearray()
    offsets = [0]
    for value in strings:
        pool.extend(value.encode("utf-8"))
        offsets.append(len(pool))
    members = [member for values in lists for member in values]
    counts = dict(strings=len(strings), entries=len(entries), labels=len(labels),
                  members=len(members), frequency_words=len(frequency), pool_bytes=len(pool))
    require(all(0 <= value < NULL for value in counts.values()), "v1 u32 capacity exceeded")
    header = [1, len(strings), len(entries), len(labels), len(members), len(frequency), len(pool), 2, 1, 1]
    output = bytearray(b"LNGIDX01" + struct.pack("<10I", *header))
    for version in versions:
        require(len(version) == 64 and set(version) <= set("0123456789abcdef"), "Invalid source data version")
        output.extend(bytes.fromhex(version))
    require(len(output) == 112, "v1 header length changed")
    output.extend(struct.pack(f"<{len(offsets)}I", *offsets))
    for row in entries:
        require(len(row) == 10 and type(row[8]) is int and type(row[9]) is int, "Invalid entry record types")
        output.extend(struct.pack("<10I", *[NULL if value is None else indices[value] for value in row[:8]], *row[8:]))
    start = 0
    for label, values in zip(labels, lists):
        output.extend(struct.pack("<3I", indices[label], start, len(values)))
        start += len(values)
    output.extend(struct.pack(f"<{len(members)}I", *members))
    for word, number in frequency:
        require(type(number) is int, "Frequency NUMBER is not an integer")
        output.extend(struct.pack("<2I", indices[word], number))
    output.extend(pool)
    return bytes(output), counts


def identity(value):
    return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}


def sources(baseline):
    """Copy recorded source identity and credit statements, without local paths."""
    upstream = baseline["references"]["lingose-python"]
    original = ROOT.parent / "lingose-python"
    for name in ("SOURCES.md", "LICENSE"):
        require(file_record(original / name) == upstream["files"][name], "Pinned upstream notice changed")
    require(file_record(ROOT / "LICENSE") == upstream["files"]["LICENSE"], "Original license was not preserved")
    lex_sources = json.loads(baseline["lexicon"]["build_info"]["manifest_json"])["sources"]
    return {
        "format_version": 1,
        "author": "詹先觉 (ZHAN Xianjue)",
        "homepage": "https://lingose.com/",
        "repository": "https://github.com/englishword",
        "license": "CC-BY-4.0",
        "license_file": "LICENSE",
        "upstream_notices": {"file": "data/UPSTREAM-SOURCES.md", **upstream["files"]["SOURCES.md"]},
        "reference": {"distribution": "lingose", "version": "0.2.0", "source_commit": upstream["head"],
                      "baseline_sha256": BASELINE_SHA256},
        "resources": {
            "lexicon.bin": {
                "source": "Installed Lingose lexicon.sqlite, verified against its packed snapshot",
                "source_identity": {key: value for key, value in baseline["fingerprints"]["resources"]["lexicon.sqlite"].items() if key != "path"},
                "snapshots": lex_sources,
                "fields": {
                    "ipa": "Phonemizer 3.3.0 and eSpeak NG 1.52.0 generated IPA",
                    "ips/ism/root_lemma": "Original Lingose data",
                    "ipsm": "Stored selected Lingose derivation with valid IPS/ISM dependencies; not recalculated",
                    "meaning_en": "Adapted from ECDICT with extensive rewriting",
                    "meaning_zh": "Translated from the English meanings",
                    "categories": "Primarily original Lingose data; some labels rebuilt with external vocabulary lists",
                },
                "adaptation": "Effective adopted public fields, annotation state and ordered category membership; UTF-8 v1 binary projection",
            },
            "frequency.bin": {
                "source": "Frequency List by Fabien Snauwaert, https://frequencylist.com/",
                "source_identity": {key: value for key, value in baseline["fingerprints"]["resources"]["frequency.sqlite"].items() if key != "path"},
                "metadata": baseline["frequency"]["metadata"],
                "adaptation": "Exact Python-lowercase tokens and minimum original NUMBER, including phrases/punctuation and gaps",
            },
        },
        "third_party": [
            {"name": "Phonemizer", "credit": "Mathieu Bernard and Hadrien Titeux, JOSS 6(68), 3958 (2021)",
             "license_reference": "https://github.com/bootphon/phonemizer#licence"},
            {"name": "eSpeak NG", "credit": "eSpeak NG contributors, based on Jonathan Duddington's eSpeak",
             "license_reference": "https://github.com/espeak-ng/espeak-ng/blob/master/COPYING"},
            {"name": "ECDICT", "credit": "Copyright (c) 2025 Linwei", "license": "MIT",
             "license_reference": "https://github.com/skywind3000/ECDICT/blob/master/LICENSE"},
            {"name": "Frequency List", "credit": "Fabien Snauwaert", "license_reference": "https://frequencylist.com/"},
        ],
        "notice_scope": "Preserves pinned upstream assertions and links, not a new license grant. Third-party works retain their licenses. Full distribution notice review remains P5.1; no separate frequency-list license text is supplied by the pinned reference.",
    }, (original / "SOURCES.md").read_bytes()


def rust_constants(resources, versions):
    lines = ["// @generated by tools/export_data.py; do not edit.",
             "// P2.2 will consume these expected identities in the production loader.",
             "pub(crate) const FORMAT_VERSION: u32 = 1;",
             "pub(crate) const LEXICON_SCHEMA_VERSION: u32 = 2;",
             "pub(crate) const FREQUENCY_SCHEMA_VERSION: u32 = 1;",
             "pub(crate) const IPSM_ALGORITHM_VERSION: u32 = 1;",
             "pub(crate) const MAX_SKIP_TOP: u32 = 5062;"]
    for prefix, version in zip(("LEXICON", "FREQUENCY"), versions):
        lines.append(f'pub(crate) const {prefix}_DATA_VERSION: &str = "{version}";')
        metadata = resources[prefix.lower() + ".bin"]
        lines.append(f'pub(crate) const {prefix}_SHA256: &str = "{metadata["sha256"]}";')
        for key in ("bytes", "strings", "entries", "labels", "members", "frequency_words", "pool_bytes"):
            lines.append(f"pub(crate) const {prefix}_{key.upper()}: usize = {metadata[key]};")
    formatted = []
    for line in lines:
        if len(line) > 100 and " = " in line:
            declaration, value = line.split(" = ", 1)
            formatted.extend((declaration + " =", "    " + value))
        else:
            formatted.append(line)
    return ("\n".join(formatted) + "\n").encode("utf-8")


def build_artifacts(projection, baseline):
    versions = (baseline["lexicon"]["build_info"]["data_version"], baseline["frequency"]["metadata"]["data_version"])
    lexicon, lex_counts = encode(projection.entries, projection.labels, projection.lists, [], versions)
    frequency, freq_counts = encode([], [], [], projection.frequency, versions)
    resources = {"lexicon.bin": {**lex_counts, **identity(lexicon)},
                 "frequency.bin": {**freq_counts, **identity(frequency)}}
    provenance, notices = sources(baseline)
    artifacts = {"data/lexicon.bin": lexicon, "data/frequency.bin": frequency,
                 "data/SOURCES.json": json_text(provenance).encode("utf-8"),
                 "data/UPSTREAM-SOURCES.md": notices,
                 "src/data_meta.rs": rust_constants(resources, versions)}
    manifest = {
        "format_version": 1, "exporter_version": 1, "lexicon_schema": 2, "frequency_schema": 1,
        "ipsm_algorithm": 1, "max_skip_top": 5062,
        "lexicon_data_version": versions[0], "frequency_data_version": versions[1],
        "baseline_sha256": BASELINE_SHA256, "reference_version": "0.2.0",
        "input_identities": {"modules": baseline["fingerprints"]["modules"],
                             "resources": {name: {k: v for k, v in metadata.items() if k != "path"}
                                           for name, metadata in baseline["fingerprints"]["resources"].items()}},
        "resources": resources,
        "category_lengths": dict(zip(projection.labels, map(len, projection.lists))),
        "annotation_states": dict(sorted(Counter(str(row[9]) for row in projection.entries).items())),
        "available_fields": {field: sum(row[column] is not None for row in projection.entries)
                             for field, column in TEXT_FIELDS.items()},
        "invalid_selected_ipsm": projection.invalid_selected_ipsm,
        "generated_files": {name: identity(value) for name, value in artifacts.items() if not name.endswith(".bin")},
        "ordering": "Original UTF-8 bytes; labels in configured order; category lists in pinned Python business order",
        "null_string_id": NULL,
    }
    artifacts["data/manifest.json"] = json_text(manifest).encode("utf-8")
    return artifacts


def persist_all(directory, artifacts, write):
    """Preflight every path before creating anything. Never overwrite drift."""
    root = directory.resolve()
    pending = []
    for name, value in artifacts.items():
        path = root / name
        require(path.resolve().is_relative_to(root), "Artifact escapes output root")
        if path.exists():
            require(path.read_bytes() == value, f"Artifact drift: {path}; existing content preserved")
        else:
            require(write, f"Missing artifact: {path}; initial creation requires --write")
            pending.append((path, value))
    for path, value in pending:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(value)


def guarded_artifacts():
    require(sha256(BASELINE) == BASELINE_SHA256, "Approved P0 baseline digest changed")
    baseline = require_baseline()
    try:
        _, _, path, frequency = installed()
        with no_restore(), closing(connect(path)) as db, closing(connect(frequency)) as freq:
            require(dict(db.execute("SELECT * FROM build_info WHERE singleton=1").fetchone()) == baseline["lexicon"]["build_info"], "Lexicon metadata drift")
            require(dict(freq.execute("SELECT * FROM frequency_metadata WHERE singleton=1").fetchone()) == baseline["frequency"]["metadata"], "Frequency metadata drift")
            projection = project(db, freq)
            require(len(projection.entries) == baseline["lexicon"]["word_count"], "Entry coverage drift")
            require(hashlib.sha256(b"".join(canonical(row[0]) + b"\n" for row in projection.entries)).hexdigest()
                    == baseline["lexicon"]["binary_ordered_words_sha256"], "Exact word keys drift")
            require(len(projection.frequency) == baseline["frequency"]["table_counts"]["frequency_word"], "Frequency coverage drift")
        return build_artifacts(projection, baseline)
    finally:
        require(fingerprints() == baseline["fingerprints"], "Input changed during export; no artifacts written")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=LIB_ROOT, help="Artifact root; alternate roots must be under .local")
    args = parser.parse_args()
    directory = args.output.resolve()
    require(directory == LIB_ROOT or directory.is_relative_to(ROOT / ".local"), "Export root must be the library crate or project .local")
    artifacts = guarded_artifacts()
    # Validate independently before writing, including all structural invariants.
    from verify_data import decode
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    versions = (baseline["lexicon"]["build_info"]["data_version"], baseline["frequency"]["metadata"]["data_version"])
    decode(artifacts["data/lexicon.bin"], kind="lexicon", versions=versions)
    decode(artifacts["data/frequency.bin"], kind="frequency", versions=versions)
    persist_all(directory, artifacts, args.write)
    manifest = json.loads(artifacts["data/manifest.json"])
    print(json_text({"mode": "write" if args.write else "check", "resources": manifest["resources"],
                     "input_fingerprints_unchanged": True, "files": len(artifacts)}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
