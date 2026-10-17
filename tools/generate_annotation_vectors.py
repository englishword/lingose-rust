"""Freeze P3.1 scanner, cluster and direct-only public annotation vectors.

All expectations come from the audited installed Python, never Rust output.
P0 remains immutable. --write creates missing artifacts only; --check refuses
any source or generated-byte drift. No reference files are written or restored.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import string as ascii_string
import subprocess
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (BASELINE, ROOT, LIB_ROOT, canonical, installed, main_error,
                       no_restore, require, require_baseline, sha256)

SOURCE = ROOT / "tests/fixtures/python-api-v1.json"
SOURCE_SHA256 = "6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1"
BASELINE_SHA256 = "9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01"
P0_IDS = ("snapshot-0217", "snapshot-0220", "snapshot-0235", "snapshot-0241", "snapshot-0250")
HELPER_TARGET = LIB_ROOT / "src/annotation_vectors.rs"
PUBLIC_TARGET = LIB_ROOT / "tests/annotation_vectors.rs"


def string(value: str) -> str:
    return '"' + "".join(
        {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t", "\0": "\\0"}.get(
            char, char if 0x20 <= ord(char) < 0x7f else f"\\u{{{ord(char):x}}}"
        ) for char in value
    ) + '"'


def character(value: str) -> str:
    require(len(value) == 1, "Expected a scalar character")
    escaped = {"'": "\\'", "\\": "\\\\"}.get(value, value)
    return f"'{escaped}'" if 0x20 <= ord(value) < 0x7f else f"'\\u{{{ord(value):x}}}'"


def unique(values):
    return list(dict.fromkeys(values))


def scanner_cases(annotation) -> list:
    texts = [
        "", "apple", "Apple APPLE aPpLe", "\t apple\r\nbook \u001c\u0085\u2028\u2029",
        "-apple apple- apple--book", "'apple apple' ’apple apple’",
        "apple'book apple’book apple-book", "apple''book apple’’book",
        "12-apple a-中文 a-1 1-apple", "123 apple123 123apple apple1book",
        "café apple123 中文apple 中文\t123 é e\u0301\n😀",
        "\u0301apple apple\u0301", "\u0301\u0302apple", "apple\u0903book apple\u20ddbook",
        "x²apple Ⅳapple ½apple", "a\u1c89b a\ua7cbb a\ua7ceb",
        "a\u0345b a\u200cb a\u200db a\ufe0fb a\U000e0100b",
        "a-\u0301b a-中文 a’中文 a’1", "a\u0301-b 1'book a\u20dd’book",
        "a\0b a\x01b", "(apple)[book]{apple}<book>",
        'apple—book apple–book apple“book”', "😀apple😀book😀", "𝕒apple 𝐀apple Ａapple",
        "a\U00011f00b a\U00011f02b a\U0001e4d0b a\U0001e4ecb",
    ]
    # Every representable Unicode general category supplies a boundary probe;
    # category alone is not a replacement for Python isalnum()/isalpha().
    representatives = {}
    for scalar in range(0x110000):
        if not 0xd800 <= scalar <= 0xdfff:
            value = chr(scalar)
            representatives.setdefault(unicodedata.category(value), value)
    texts.extend("a" + value + "b" for _, value in sorted(representatives.items()))
    texts.extend("a-" + value + "b" for _, value in sorted(representatives.items()))
    result = []
    for text in unique(texts):
        offsets = [0]
        for value in text:
            offsets.append(offsets[-1] + len(value.encode("utf-8")))
        spans = [(offsets[start], offsets[end]) for start, end in annotation._word_spans(text)]
        result.append((text, spans))
    return result


def cluster_cases(annotation) -> tuple[list, list, int]:
    # Enumerate the full scalar domain against Python's NFD-based acceptance,
    # including all 52 special double-struck forms, rather than a data sample.
    accepted = []
    for scalar in range(0x110000):
        if not 0xd800 <= scalar <= 0xdfff:
            value = chr(scalar)
            if annotation._base(value) is not None:
                accepted.append(value)
    require(len(accepted) == 298, "Pinned Unicode scalar-base coverage changed")
    require(all(value in accepted for value in annotation._LOWER_DOUBLE + annotation._UPPER_DOUBLE),
            "Missing a double-struck form")
    clusters = list(accepted)
    marks = sorted(annotation._MARKS)
    clusters.extend(letter + mark for letter in "aAwWyY" for mark in marks)
    clusters.extend(letter + mark for letter in annotation._LOWER_DOUBLE + annotation._UPPER_DOUBLE
                    for mark in ("\u0300", "\u0304"))
    clusters.extend([
        "w\u0304", "W\u0305", "W\u0304", "w\u0305", "a\u0307\u0300", "a\u0300\u0307",
        "A\u0323\u0302", "A\u0302\u0323", "ầ\u0307", "K\u0300", "Å\u0323",
        "\u0300", "\u0300a", "\u0300\u0302", "ab", "a-b", "-\u0300", "’\u0300",
        "á", "ä", "æ", "ø", "ð", "ß", "ſ", "ı", "ﬁ", "α", "Σ", "𝔥", "𝐚", "Ａ",
        "\0", "\u200d", "\u0903", "\u20dd", "\ufe0f", "\U000e0100", "1", "😀",
        "a\u0301", "a\u0306", "a\u0308", "a\u030b", "a\u030c", "a\u0327",
        "a\u0345", "a\u0903", "a\u20dd", "a\ufe0f", "a\U000e0100",
    ])
    bases = [(cluster, annotation._base(cluster)) for cluster in unique(clusters)]
    pairs = []
    for cluster, base in bases:
        if base is not None and base in ascii_string.ascii_lowercase:
            pairs.extend(((base, cluster), (base.upper(), cluster)))
        elif base in ("-", "'"):
            pairs.extend((delimiter, cluster) for delimiter in ("-", "'", "’"))
        else:
            pairs.extend((("a", cluster), ("A", cluster)))
    pairs.extend([
        ("", ""), ("", "a"), ("a", ""), ("a", "\u0300a"), ("ab", "a\u0300b"),
        ("ab", "ab\u0300"), ("ab", "a\u0903b"), ("ab", "a\u20ddb"),
        ("ab", "a\u0300\u0302b"), ("ab", "a\u0300b\u0323"),
        ("ab", "a\u0301b"), ("apple", "apple"), ("ApPlE", "åppl𝕖"),
        ("whale", "w\u0304𝕙āle"), ("WHALE", "w\u0304𝕙āle"),
        ("WhAlE", "w\u0304𝕙āle"), ("WHIM", "ẘ𝕙i\u030am"), ("YUM", "ẙu\u0307m"),
        ("a'b", "ā’b"), ("A’B", "ā'b"), ("A-B", "ā-ḅ"), ("a’b", "a'b"),
        ("bad", "bādextra"), ("bad", "bād😀"), ("bad", "bād\u0301"),
        ("the", "ṫhe\u030a"), ("THE", "ṫhē"), ("word", "wrong"),
    ])
    cases = [(word, notation, annotation._case_notation(word, notation))
             for word, notation in unique(pairs)]
    return bases, cases, len(accepted)


def safe_public(annotation, annotator, text: str) -> None:
    """Require direct saved values/blocked states or a non-inflecting unknown.

    This guards phase selection against Python rules and saved state; it never
    compares against Rust. Existing full compound/apostrophe entries are direct.
    """
    for start, end in annotation._word_spans(text):
        word = text[start:end]
        if not annotation._ENGLISH.fullmatch(word):
            continue
        normalized = word.lower().replace("’", "'")
        require(normalized != "the", "P3.2 the context is outside these vectors")
        match = annotator.match(word)
        if match.notation is not None or not match.fallback:
            continue
        require(normalized not in annotation._EXPLICIT and "-" not in word
                and "'" not in normalized and not annotation._morph_candidates(normalized),
                f"Public vector would depend on a P3.2 fallback: {word!r}")


def public_cases(annotation, fixture: dict) -> tuple[list, int]:
    from lingose import query
    rows = {row["id"]: row for row in fixture["cases"]}
    result = []
    with no_restore(), query._open_database() as (database, _):
        annotator = annotation._Annotator(database, set())
        for identifier in P0_IDS:
            row = rows[identifier]
            call = row["call"]
            require(row["source"] == "snapshot" and call["api"] == "annotate_ips"
                    and call.get("kwargs", {}).get("skip_top", 0) == 0,
                    f"Unexpected P0 vector selection: {identifier}")
            text = call["args"][0]
            safe_public(annotation, annotator, text)
            require(annotation.annotate_ips(text) == row["expected"]["value"],
                    f"Pinned P0 annotation result changed: {identifier}")
            result.append((identifier, text, row["expected"]["value"]))
        fresh = [
            " \tApple,\r\nAPPLE! aPpLe? [book] 😀 中文 123 e\u0301  ",
            "unknownwordzz qzqxzz Zzqxxx", "may MAY mAy US us",
            "Abandon ABANDON aBaNdOn\tWHALE Whim yum",
            "apple’ APPLE' 'book' ‘book’", "-apple apple- apple--book",
            "ma'am MA'AM Ma’Am o’clock O’CLOCK first-rate FIRST-RATE ice-cream",
            "a-1; 12-apple; a-中文; 1-apple; x²apple; a\u0903b; a\u20ddb",
            "中文 123 é e\u0301 𝕙 w\u0304 😀", "\t\r\n\u001c\u0085\u2028\u2029  ",
        ]
        for index, text in enumerate(fresh, 1):
            safe_public(annotation, annotator, text)
            result.append((f"direct-curated-{index:02d}", text, annotation.annotate_ips(text)))
    return result, len(P0_IDS)


def header(baseline: dict, payload: object) -> list[str]:
    fingerprint = baseline["fingerprints"]["modules"]["annotation.py"]
    return [
        "//! Generated from the pinned installed Python oracle; do not edit by hand.",
        f"//! P0 fixture SHA-256: {SOURCE_SHA256}",
        f"//! Reference baseline SHA-256: {BASELINE_SHA256}",
        f"//! Installed annotation.py SHA-256: {fingerprint['sha256']}",
        f"//! Oracle: CPython 3.12.4 / Unicode {unicodedata.unidata_version}; source bytes {fingerprint['bytes']}.",
        f"//! Canonical vector payload SHA-256: {hashlib.sha256(canonical(payload)).hexdigest()}",
        "",
    ]


def render_helpers(baseline: dict, scans: list, bases: list, cases: list) -> str:
    lines = header(baseline, {"scans": scans, "bases": bases, "cases": cases})
    lines += ["use super::{base, case_notation, word_spans};", "", "#[test]",
              "fn pinned_python_scanner_uses_utf8_byte_ranges() {",
              "    let cases: &[(&str, &[(usize, usize)])] = &["]
    for text, spans in scans:
        expected = "&[" + ", ".join(f"({start}, {end})" for start, end in spans) + "]"
        lines.append(f"        ({string(text)}, {expected}),")
    lines += ["    ];", "    for &(text, expected) in cases {",
              '        assert_eq!(word_spans(text), expected, "{text:?}");', "    }", "}", "", "#[test]",
              "fn pinned_python_cluster_bases_cover_all_accepted_scalars_and_invalid_marks() {",
              "    let cases: &[(&str, Option<char>)] = &["]
    for cluster, value in bases:
        expected = "None" if value is None else f"Some({character(value)})"
        lines.append(f"        ({string(cluster)}, {expected}),")
    lines += ["    ];", "    for &(cluster, expected) in cases {",
              '        assert_eq!(base(cluster), expected, "{cluster:?}");', "    }", "}", "", "#[test]",
              "fn pinned_python_case_alignment_preserves_clusters_and_input_punctuation() {",
              "    let cases: &[(&str, &str, Option<&str>)] = &["]
    for word, notation, value in cases:
        expected = "None" if value is None else f"Some({string(value)})"
        lines.append(f"        ({string(word)}, {string(notation)}, {expected}),")
    lines += ["    ];", "    for &(word, notation, expected) in cases {",
              '        assert_eq!(case_notation(word, notation).as_deref(), expected, "{word:?}/{notation:?}");',
              "    }", "}", ""]
    return "\n".join(lines)


def render_public(baseline: dict, cases: list) -> str:
    lines = header(baseline, cases)
    lines += ["#[test]", "fn pinned_python_direct_annotation_outputs_match_public_default_and_zero_threshold() {",
              "    let cases: &[(&str, &str, &str)] = &["]
    for identifier, text, value in cases:
        lines.append(f"        ({string(identifier)}, {string(text)}, {string(value)}),")
    lines += ["    ];", "    for &(identifier, text, expected) in cases {",
              '        assert_eq!(lingose::annotate_ips(text).unwrap(), expected, "{identifier}");',
              '        assert_eq!(lingose::annotate_ips_skip(text, 0).unwrap(), expected, "{identifier}/zero");',
              "    }", "}", ""]
    return "\n".join(lines)


def persist(path: Path, content: bytes, write: bool) -> str:
    if path.exists():
        require(path.read_bytes() == content, f"Recorded artifact drift: {path}; existing bytes preserved")
        return "unchanged"
    require(write, f"Missing artifact: {path}; use --write for initial creation")
    with path.open("xb") as stream:
        stream.write(content)
    return "created"


def generate() -> tuple[dict[Path, bytes], dict]:
    require(sha256(SOURCE) == SOURCE_SHA256, "P0 fixture identity changed; do not overwrite its baseline")
    require(sha256(BASELINE) == BASELINE_SHA256, "Approved P0 baseline identity changed")
    before = require_baseline()
    environment = before["environment"]
    require(sys.version == environment["python"] and sys.platform == environment["platform"]
            and Path(sys.executable).resolve() == Path(environment["executable"]).resolve()
            and unicodedata.unidata_version == environment["unicode_version"] == "15.0.0",
            "Use the pinned Python runtime and Unicode version")
    _, package, _, _ = installed()
    from lingose import annotation
    require(Path(annotation.__file__).resolve() == package / "annotation.py", "Unexpected oracle module path")
    fixture = json.loads(SOURCE.read_bytes())
    scans = scanner_cases(annotation)
    bases, cases, accepted_count = cluster_cases(annotation)
    public, p0_count = public_cases(annotation, fixture)
    raw = {HELPER_TARGET: render_helpers(before, scans, bases, cases),
           PUBLIC_TARGET: render_public(before, public)}
    outputs = {}
    for target, content in raw.items():
        formatted = subprocess.run(["rustfmt", "--edition", "2024", "--emit", "stdout"],
                                   input=content, text=True, encoding="utf-8", capture_output=True, check=True)
        outputs[target] = formatted.stdout.replace("\r\n", "\n").encode("utf-8")
        require(b"\r" not in outputs[target], "Generated Rust must use LF")
    require(require_baseline() == before, "Installed source or resource identity changed during generation")
    require(sha256(SOURCE) == SOURCE_SHA256 and sha256(BASELINE) == BASELINE_SHA256,
            "Frozen P0 inputs changed during generation")
    return outputs, {"scanner_inputs": len(scans), "base_inputs": len(bases),
                     "accepted_scalar_bases": accepted_count, "case_inputs": len(cases),
                     "public_p0": p0_count, "public_curated": len(public) - p0_count,
                     "public_assertions": 2 * len(public)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, counts = generate()
    statuses = {str(path.relative_to(ROOT)): persist(path, content, args.write)
                for path, content in outputs.items()}
    print(json.dumps({"status": statuses, **counts}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
