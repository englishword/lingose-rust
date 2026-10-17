"""Freeze P3.3 frequency annotation outputs from the pinned installed Python.

P0/P3.1/P3.2 remain immutable. --write creates missing artifacts only after a
complete preflight; --check rejects input or generated-byte drift. Oracle SQLite
files live only in disposable project-local directories, never installed paths.
"""

from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (BASELINE, ROOT, LIB_ROOT, connect, installed, main_error, no_restore,
                       require, require_baseline, sha256)
from generate_annotation_vectors import (BASELINE_SHA256, SOURCE, SOURCE_SHA256,
                                         header, persist, string, unique)
from generate_annotation_context_vectors import available, blocked, fallback
from capture_api_vectors import build_fixture, fixture_paths, integer_argument

HELPER_TARGET = LIB_ROOT / "src/annotation_frequency_vectors.rs"
PUBLIC_TARGET = LIB_ROOT / "tests/annotation_frequency_vectors.rs"
WIRE_TARGET = LIB_ROOT / "src/data/annotation_frequency_vectors.rs"
I64_MAX = (1 << 63) - 1
I64_MIN = -(1 << 63)


def rust_threshold(value) -> int:
    """Adapt Python's unbounded integer after sign/range comparison, never cast."""
    value = integer_argument(value)
    require(type(value) is int, "Expected a typed integer threshold")
    return min(value, I64_MAX) if value >= 0 else max(value, I64_MIN)


def p0_annotation(fixture: dict, source: str) -> list[dict]:
    return [row for row in fixture["cases"]
            if row["source"] == source and row["call"]["api"] == "annotate_ips"]


def prefix_cases() -> list:
    cases = []
    # Every ASCII scalar is both a literal pattern and a candidate input; the
    # three Unicode-sensitive ASCII letters additionally see every ASCII input.
    for scalar in range(128):
        char = chr(scalar)
        pattern = char.lower()
        cases.append((char + " tail", pattern))
        for pattern in ("s", "i", "k"):
            cases.append((char + "tail", pattern))
    for pattern in ("a.k.a.", "i.i.", "s;s", "k/k", "a lot", "9-1-1",
                    r".*+?[](){}^$|\\", "one thousand one hundred"):
        cases.extend((text, pattern) for text in
                     (pattern, pattern.upper(), pattern.title(), "", pattern[:-1],
                      pattern + "tail", "x" + pattern))
    for text in ("ſ", "S", "İ", "ı", "I", "K", "K", "i\u0307",
                 "ſ;s", "ſ;ſ", "İ.i.", "ı.i.", "i.İ.", "i.ı.", "K/k", "k/K"):
        for pattern in ("s", "i", "k", "s;s", "i.i.", "k/k"):
            cases.append((text, pattern))
    result = []
    for text, pattern in unique(cases):
        match = re.compile(re.escape(pattern), re.IGNORECASE).match(text)
        expected = None if match is None else (len(match.group().encode("utf-8")),
                                                match.group().lower() == pattern)
        result.append((text, pattern, expected))
    return result


def public_cases(annotation, fixture: dict, special: list) -> tuple[list, list, list]:
    cases, errors, excluded = [], [], []
    with no_restore():
        for row in p0_annotation(fixture, "snapshot"):
            call = row["call"]
            if row["expected"].get("error") == "TypeError":
                excluded.append((row["id"], call["group"]))
                continue
            text = call["args"][0]
            threshold = rust_threshold(call.get("kwargs", {}).get("skip_top", 0))
            if "error" in row["expected"]:
                require(row["expected"]["error"] == "ValueError", "Unexpected P0 error")
                try:
                    annotation.annotate_ips(text, skip_top=threshold)
                except ValueError:
                    errors.append((row["id"], text, threshold,
                                   "skip_top" if threshold < 0 else "text"))
                else:
                    require(False, f"Pinned P0 error changed: {row['id']}")
                continue
            value = annotation.annotate_ips(text, skip_top=threshold)
            require(value == row["expected"]["value"], f"Pinned P0 output changed: {row['id']}")
            cases.append((row["id"], text, threshold, value))
        require(len(excluded) == 6 and len(errors) == 2, "P0 typed-error domain changed")
        for number, (word, rank) in enumerate(special, 1):
            variants = [word, word.upper(), word.title(), "x" + word, word + "x",
                        "1" + word, word + "1", "中文" + word, word + "中文",
                        "\u0301" + word, word + "\u0301", "-" + word, word + "-",
                        "'" + word, word + "’", "(" + word + ")", "😀" + word + "😀"]
            for old, new in (("s", "ſ"), ("i", "İ"), ("i", "ı"), ("k", "K")):
                if old in word:
                    variants.append(word.replace(old, new))
            text = "apple | " + " | ".join(unique(variants)) + " | the apple"
            for threshold in unique((rank - 1, rank, 5062)):
                cases.append((f"real-special-{number:02d}-{threshold}", text, threshold,
                              annotation.annotate_ips(text, skip_top=threshold)))
        extra = [
            "the eight hundred apple the one hundred apple the a.m. apple the a.k.a. apple",
            "the one thousand one hundred apple one thousand one hundred one thousand",
            "Messrs. messrs. Mr. mr. Mmes. Mrs. p.m. A.M. a/k/a a.k.a.",
            "winded ; wind winded; wind winded ; WIND winded ; winded non- non-stop",
            "walk walks walked walking study studies studied studying abandon abandoned abandoning",
            "the book abandon tail THE BOOK ABANDON TAIL",
            "中文 123 911 9-1-1 😀 e\u0301", "", "\t 911 9-1-1\n",
        ]
        for number, text in enumerate(extra, 1):
            for threshold in (0, 1, 29, 30, 31, 1000, 5061, 5062, 5063, I64_MAX):
                cases.append((f"frequency-curated-{number:02d}-{threshold}", text, threshold,
                              annotation.annotate_ips(text, skip_top=threshold)))
    return cases, errors, excluded


def wire_specs(fixture: dict) -> list:
    p0 = []
    for row in p0_annotation(fixture, "fixture"):
        require("value" in row["expected"], "Unexpected P0 fixture error")
        p0.append((row["id"], row["call"]["args"][0],
                   rust_threshold(row["call"].get("kwargs", {}).get("skip_top", 0)),
                   row["expected"]["value"]))
    result = [("p0_complete_frequency_fixture", fixture["fixture_spec"], p0)]
    entries = {"apple": available("åpple"), "book": available("bòok"), "the": blocked(),
               "Apple": blocked(), "wrong": available("bad"), "don't": blocked(),
               "doesn't": fallback(), "aren't": available("wrong"), "i'm": blocked(),
               "o'clock": blocked(), "you're": blocked(), "first-rate": blocked(),
               "first": available("fi̊rst"), "rate": available("rāte"),
               "walk": available("wàlk"), "walks": blocked(), "walking": fallback(),
               "apple's": blocked(), "ca": blocked(), "can": available("cãn")}
    texts = ["the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
             "don't don’t DON’T doesn't doesn’t aren't aren’t I'm I’m you're you’re o'clock o’clock",
             "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
             "apple's apple’s APPLE’S can't can’t CAN’T ca’can’t a’can’t",
             "the-apple apple-the apple the’s apple the’s-apple"]
    frequency = {word: number for number, word in enumerate(
        ("the", "apple", "wrong", "don't", "doesn't", "aren't", "i'm", "you're", "o'clock",
         "first-rate", "walks", "walking", "apple's", "ca"), 1)}
    result.append(("frequency_precedes_saved_states_and_all_fallbacks",
                   {"entries": entries, "frequency": frequency},
                   [(text, threshold) for text in texts for threshold in (0, 1, 2, 4, 7, 10, 14, 5062)]))
    inflections = {word: available(value) for word, value in {
        "walk": "wàlk", "study": "stûdẏ", "box": "bòx", "bake": "bāke", "stop": "stòp",
        "tie": "tīe", "bus": "bûs", "apple": "åpple", "the": "wrong"}.items()}
    text = ("walk walks walked walking study studies studied studying box boxes bake bakes baked baking "
            "stop stops stopped stopping tie ties tied tying bus buses busing bussing "
            "unknowns unknowned unknowning WALK WALKS WALKED WALKING")
    result.append(("frequency_uses_saved_inflection_keys_without_stem_expansion",
                   {"entries": inflections, "frequency": {"walk": 1, "walked": 2, "study": 3,
                    "studies": 4, "boxes": 5, "baking": 6, "stopped": 7, "ties": 8,
                    "buses": 9, "unknowned": 10}},
                   [(text, threshold) for threshold in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 5062)]))
    plain = {word: available(value) for word, value in {
        "a": "ā", "lot": "lòt", "lottery": "lòtterẏ", "apple": "åpple", "the": "wrong",
        "one": "òne", "hundred": "hûndred", "fifty": "fi̊ftẏ", "eight": "ēight",
        "i": "ī", "s": "s", "k": "k", "winded": "wi̊nded", "wind": "wi̊nd"}.items()}
    special = {"a lot": 1, "a lottery": 2, "lottery apple": 1, "one hundred": 1,
               "one hundred fifty": 2, "hundred fifty": 1, "i.i.": 1, ".i.": 1,
               "s.s.": 1, "k/k": 1, "eight hundred": 1, "a.m.": 1,
               "winded ; wind": 1, "9-1-1": 1, "911": 1}
    special_texts = [
        "a lot a lottery a lottery apple a lotterya lot one hundred fifty apple",
        "xa lot apple a lottery apple xa lottery apple one hundred fiftyeight",
        "i.i.i. İ.i.i. ı.i.i. i.İ.i. i.ı.i. S.S. ſ.s. s.ſ. K/K K/k k/K apple",
        "the eight hundred apple the a lot apple the a.m. apple the one hundred fifty apple",
        "the\neight hundred apple the\n\neight hundred apple the (eight hundred) apple",
        "a lot’a lot a lot-a lot a lot\u0301 a lot中文 a lot1 a lot_apple",
        "winded ; wind winded; wind winded ; winded winded ; wind wind apple",
        "911 9-1-1 中文 😀 e\u0301", "", "\t 911 9-1-1\n",
    ]
    result.append(("special_longest_consumption_membership_and_context",
                   {"entries": plain, "frequency": special},
                   [(text, threshold) for text in special_texts for threshold in (0, 1, 2, 5062)]))
    # Python's boundary predicate includes alnum and every M* category, not
    # merely ASCII word characters. Include representatives of every category.
    representatives = {}
    for scalar in range(0x110000):
        if not 0xd800 <= scalar <= 0xdfff:
            char = chr(scalar)
            representatives.setdefault(unicodedata.category(char), char)
    neighbors = unique(list(representatives.values()) +
                       list("azAZ09-'’_.,;:!?()[]{} ") +
                       ["é", "中", "²", "½", "Ⅳ", "𝕒", "ſ", "İ", "ı", "K", "\u0301", "\u0903", "\u20dd", "😀"])
    neighbors = [char for char in neighbors if char != "\0"]
    neighbor_texts = ["apple | " + char + "a lot | a lot" + char + " | the apple" for char in neighbors]
    result.append(("special_python_unicode_neighbor_boundaries",
                   {"entries": plain, "frequency": {"a lot": 1}},
                   [(text, threshold) for text in neighbor_texts for threshold in (0, 1)]))
    literals = {pattern: 1 for pattern in
                ("a.b", "a*b", "a+b", "a?b", "a[b", "a]b", "a(b", "a)b", "a{b", "a}b",
                 "a^b", "a$b", "a|b", "a\\b", "a/b", "a b", "a\tb", "a\nb")}
    result.append(("special_patterns_are_literal_escaped_ascii",
                   {"entries": plain, "frequency": literals},
                   [("apple | " + " | ".join(literals) + " | axb | the apple", threshold)
                    for threshold in (0, 1, 5062)]))
    return result


def wire_cases(annotation, baseline: dict, fixture: dict) -> list:
    from lingose import query
    directory = ROOT / ".local"
    directory.mkdir(exist_ok=True)
    result = []
    with tempfile.TemporaryDirectory(prefix="annotation-frequency-oracle-", dir=directory) as temporary:
        for index, (name, spec, items) in enumerate(wire_specs(fixture)):
            path, frequency = Path(temporary) / f"{index}.sqlite", Path(temporary) / f"{index}-frequency.sqlite"
            build_fixture(path, frequency, baseline, spec)
            fingerprints = (sha256(path), sha256(frequency))
            records, cases = [], []
            with fixture_paths(path, frequency):
                with query._open_database() as (database, _):
                    annotator = annotation._Annotator(database, set())
                    for word in sorted(spec["entries"]):
                        match = annotator.exact(word)
                        require(match.exists, "Fixture entry disappeared")
                        records.append((word, match.notation,
                                        2 if match.notation is not None else 1 if match.fallback else 0))
                for number, item in enumerate(items, 1):
                    if len(item) == 4:
                        identifier, text, threshold, expected = item
                    else:
                        text, threshold = item
                        identifier, expected = f"{name}-{number:03d}", None
                    value = annotation.annotate_ips(text, skip_top=threshold)
                    if expected is not None:
                        require(value == expected, f"Pinned P0 fixture output changed: {identifier}")
                    has_tokens = any(annotation._ENGLISH.fullmatch(text[left:right])
                                     for left, right in annotation._word_spans(text))
                    cases.append((identifier, text, threshold, value, has_tokens))
            require((sha256(path), sha256(frequency)) == fingerprints, "Oracle mutated fixture inputs")
            # Rank values are the original saved NUMBER values, never sorted-row indices.
            result.append((name, records, list(sorted(spec["frequency"].items())), cases))
    return result


def render_helpers(baseline: dict, cases: list) -> str:
    lines = header(baseline, cases)
    lines += ["use super::special_prefix;", "", "type PrefixCase<'a> = (&'a str, &'a str, Option<(usize, bool)>);", "", "#[test]",
              "fn pinned_python_literal_ignorecase_prefix_and_lower_membership_match() {",
              "    let cases: &[PrefixCase<'_>] = &["]
    for text, pattern, value in cases:
        expected = "None" if value is None else f"Some(({value[0]}, {str(value[1]).lower()}))"
        lines.append(f"        ({string(text)}, {string(pattern)}, {expected}),")
    lines += ["    ];", "    for &(text, pattern, expected) in cases {",
              '        assert_eq!(special_prefix(text, pattern), expected, "{text:?}/{pattern:?}");',
              "    }", "}", ""]
    return "\n".join(lines)


def render_public(baseline: dict, cases: list, errors: list, excluded: list) -> str:
    lines = header(baseline, [cases, errors, excluded])
    lines += ["// Python dynamic TypeError calls are outside Rust's typed call domain.",
              "// They are recorded for coverage; their arguments cannot be supplied to these signatures."]
    lines.extend(f"// {identifier}: {group}." for identifier, group in excluded)
    lines += ["// Positive Python integers beyond i64::MAX map to i64::MAX after sign/range comparison;",
              "// both then cap at 5062, so no integer wrapping or truncation is used.", "",
              "type PublicCase<'a> = (&'a str, &'a str, i64, &'a str);", "",
              "#[test]", "fn pinned_python_snapshot_and_real_frequency_outputs_match() {",
              "    let cases: &[PublicCase<'_>] = &["]
    for identifier, text, threshold, value in cases:
        lines.append(f"        ({string(identifier)}, {string(text)}, {threshold}, {string(value)}),")
    lines += ["    ];", "    for &(identifier, text, threshold, expected) in cases {",
              '        assert_eq!(lingose::annotate_ips_with_skip_top(text, threshold).unwrap(), expected, "{identifier}");',
              "        if threshold == 0 {",
              '            assert_eq!(lingose::annotate_ips(text).unwrap(), expected, "{identifier}/default");',
              "        }", "    }", "}", "", "#[test]",
              "fn pinned_python_value_errors_map_to_invalid_arguments() {",
              "    let cases: &[PublicCase<'_>] = &["]
    for identifier, text, threshold, parameter in errors:
        lines.append(f"        ({string(identifier)}, {string(text)}, {threshold}, {string(parameter)}),")
    lines += ["    ];", "    for &(identifier, text, threshold, parameter) in cases {",
              "        assert!(matches!(lingose::annotate_ips_with_skip_top(text, threshold),",
              "            Err(lingose::Error::InvalidArgument { parameter: found, .. }) if found == parameter),",
              '            "{identifier}");', "    }", "}", ""]
    return "\n".join(lines)


def render_wire(baseline: dict, specs: list, fixture: dict) -> str:
    lines = header(baseline, specs)
    lines += ["use super::{Record, encode, frequency_fixture, lexicon_fixture};",
              "use crate::annotation::annotate_from;", "use crate::data::AnnotationResources;", "",
              "type WireCase<'a> = (&'a str, &'a str, i64, &'a str, bool);", ""]
    for name, records, frequency, cases in specs:
        lines += ["#[test]", f"fn pinned_python_{name}() {{", "    let entries = ["]
        for word, ips, state in records:
            value = "None" if ips is None else f"Some({string(ips)})"
            lines.append(f"        ({string(word)}, {value}, {state}),")
        lines += ["    ];", "    let records: Vec<_> = entries.iter().map(|&(word, ips, state)| {",
                  "        let mut fields = [None; 7];", "        fields[1] = ips;",
                  "        Record { word, fields, state }", "    }).collect();",
                  "    let lexicon = lexicon_fixture(encode(&records, &[], &[]));",
                  "    let frequency = frequency_fixture(encode(&[], &[], &["]
        for word, rank in frequency:
            lines.append(f"        ({string(word)}, {rank}),")
        lines += ["    ]));", "    let cases: &[WireCase<'_>] = &["]
        for identifier, text, threshold, value, has_tokens in cases:
            lines.append(f"        ({string(identifier)}, {string(text)}, {threshold}, {string(value)}, {str(has_tokens).lower()}),")
        lines += ["    ];", "    for &(identifier, text, threshold, expected, expected_tokens) in cases {",
                  "        let mut loaded = false;",
                  "        let actual = annotate_from(text, threshold, |has_tokens, capped| {",
                  "            loaded = true;", "            assert!(has_tokens);",
                  "            assert_eq!(capped, threshold.min(5062) as u32);",
                  "            Ok(Some(AnnotationResources { lexicon: &lexicon,",
                  "                frequency: if capped == 0 { None } else { Some(&frequency) } }))",
                  "        }).unwrap();", '        assert_eq!(actual, expected, "{identifier}");',
                  '        assert_eq!(loaded, expected_tokens, "{identifier}/resource-access");', "    }", "}", ""]
    resources = p0_annotation(fixture, "resource-fixture")
    require(len(resources) == 3, "P0 annotation resource fixture domain changed")
    lines += ["#[test]", "fn pinned_python_resource_fixture_outcomes_match() {",
              "    // P0 resource-fixture-0307: a missing frequency resource is a named data error.",
              "    let missing = annotate_from(\"apple\", 1, |has_tokens, threshold| {",
              "        assert!(has_tokens);", "        assert_eq!(threshold, 1);",
              '        Err(crate::Error::Data { resource: "frequency.bin.z", message: "missing fixture".into() })',
              "    });", "    assert!(matches!(missing, Err(crate::Error::Data { .. })));",
              "    // P0 resource-fixture-0308: zero threshold does not require frequency.",
              '    let records = [Record { word: "apple", fields: [None, Some("apple"), None, None, None, None, None], state: 2 }];',
              "    let lexicon = lexicon_fixture(encode(&records, &[], &[]));",
              '    assert_eq!(annotate_from("apple", 0, |_, threshold| {',
              "        assert_eq!(threshold, 0);",
              "        Ok(Some(AnnotationResources { lexicon: &lexicon, frequency: None }))",
              '    }).unwrap(), "apple");',
              "    // P0 resource-fixture-0309: no English token returns before either resource."]
    no_tokens = resources[-1]
    require(no_tokens["call"]["group"] == "no-token-no-resources", "Unexpected P0 resource order")
    text = no_tokens["call"]["args"][0]
    lines += [f"    assert_eq!(annotate_from({string(text)}, 1, |_, _| panic!(\"no-token resource access\")).unwrap(), {string(no_tokens['expected']['value'])});",
              "}", ""]
    return "\n".join(lines)


def generate() -> tuple[dict[Path, bytes], dict]:
    require(sha256(SOURCE) == SOURCE_SHA256, "P0 fixture identity changed; do not overwrite its baseline")
    require(sha256(BASELINE) == BASELINE_SHA256, "Approved P0 baseline identity changed")
    before = require_baseline()
    environment = before["environment"]
    require(sys.version == environment["python"] and sys.platform == environment["platform"]
            and Path(sys.executable).resolve() == Path(environment["executable"]).resolve()
            and unicodedata.unidata_version == environment["unicode_version"] == "15.0.0",
            "Use the pinned Python runtime and Unicode version")
    _, package, _, frequency_path = installed()
    from lingose import annotation
    require(Path(annotation.__file__).resolve() == package / "annotation.py", "Unexpected oracle module path")
    with closing(connect(frequency_path)) as database:
        frequency = list(database.execute("SELECT word, rank FROM frequency_word ORDER BY word COLLATE BINARY"))
    require(len(frequency) == 10620 and all(word.isascii() for word, _ in frequency),
            "Pinned v1 ASCII frequency key domain changed")
    special = [(word, rank) for word, rank in frequency if not annotation._ENGLISH.fullmatch(word)]
    require(len(special) == 26, "Pinned special frequency key domain changed")
    fixture = json.loads(SOURCE.read_bytes())
    prefixes = prefix_cases()
    public, errors, excluded = public_cases(annotation, fixture, special)
    wire = wire_cases(annotation, before, fixture)
    raw = {HELPER_TARGET: render_helpers(before, prefixes),
           PUBLIC_TARGET: render_public(before, public, errors, excluded),
           WIRE_TARGET: render_wire(before, wire, fixture)}
    outputs = {}
    for target, content in raw.items():
        formatted = subprocess.run(["rustfmt", "--edition", "2024", "--emit", "stdout"],
                                   input=content, text=True, encoding="utf-8", capture_output=True, check=True)
        outputs[target] = formatted.stdout.replace("\r\n", "\n").encode("utf-8")
        require(b"\r" not in outputs[target], "Generated Rust must use LF")
    require(require_baseline() == before, "Installed source or resource identity changed during generation")
    require(sha256(SOURCE) == SOURCE_SHA256 and sha256(BASELINE) == BASELINE_SHA256,
            "Frozen P0 inputs changed during generation")
    return outputs, {"prefix_inputs": len(prefixes), "frequency_keys": len(frequency),
                     "special_keys": len(special), "public_p0_successes": 53,
                     "public_p0_value_errors": len(errors), "p0_dynamic_type_errors_outside_rust_domain": excluded,
                     "public_cases": len(public), "public_assertions": len(public) + sum(threshold == 0 for _, _, threshold, _ in public) + len(errors),
                     "wire_specs": len(wire), "wire_p0": len(wire[0][3]),
                     "wire_cases": sum(len(cases) for _, _, _, cases in wire),
                     "wire_resource_p0": len(p0_annotation(fixture, "resource-fixture"))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, counts = generate()
    # Preflight all targets before creating any output. A later drift cannot
    # leave an earlier missing artifact behind after an unsuccessful run.
    for path, content in outputs.items():
        if path.exists():
            require(path.read_bytes() == content, f"Recorded artifact drift: {path}; existing bytes preserved")
        else:
            require(args.write, f"Missing artifact: {path}; use --write for initial creation")
    statuses = {str(path.relative_to(ROOT)): persist(path, content, args.write)
                for path, content in outputs.items()}
    print(json.dumps({"status": statuses, **counts}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
