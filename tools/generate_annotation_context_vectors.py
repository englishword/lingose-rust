"""Freeze P3.2 context, compound and inflection expectations from pinned Python.

P0 and P3.1 stay immutable. --write creates missing artifacts only; --check
refuses source or generated-byte drift. Oracle databases are isolated temporary
fixtures under .local; installed files are only read and never restored.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import re
import string as ascii_string
import subprocess
import sys
import tempfile
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (BASELINE, ROOT, LIB_ROOT, installed, main_error, no_restore,
                       require, require_baseline, sha256)
from generate_annotation_vectors import (BASELINE_SHA256, SOURCE, SOURCE_SHA256,
                                         header, persist, string, unique)
from capture_api_vectors import build_fixture, fixture_paths

HELPER_TARGET = LIB_ROOT / "src/annotation_context_vectors.rs"
PUBLIC_TARGET = LIB_ROOT / "tests/annotation_context_vectors.rs"
WIRE_TARGET = LIB_ROOT / "src/data/annotation_context_vectors.rs"


def zero_annotation_rows(fixture: dict, source: str) -> list[dict]:
    return [row for row in fixture["cases"]
            if row["source"] == source and row["call"]["api"] == "annotate_ips"
            and row["call"].get("kwargs", {}).get("skip_top", 0) == 0
            and "value" in row["expected"]]


def separator_cases() -> tuple[list, list[str]]:
    whitespace = [chr(value) for value in range(0x110000)
                  if not 0xd800 <= value <= 0xdfff and chr(value).isspace()]
    require(len(whitespace) == 29, "Pinned Python whitespace domain changed")
    separators = [""]
    # Exhaustive short combinations include quote-separated LF pairs, which
    # the Python blank-line regex does not consider a blank line.
    alphabet = " \t\r\n\"'‘’“”()[]"
    for length in range(1, 4):
        separators.extend("".join(chars) for chars in itertools.product(alphabet, repeat=length))
    for space in whitespace:
        separators.extend((space, "\n" + space + "\n", "\n" + space + "(\n",
                           "\r" + space + "\r", "\r\n" + space + "\r\n"))
    separators.extend(("\n\n", "\n \t\r\n", "\n‘’\n", "\n()\n", "\r\r", "\u2028\u2029",
                       ",", ".", ";", ":", "!", "?", "-", "—", "…", "{", "}", "<", ">",
                       "\0", "\x01", "\u180e", "\u200b", "\ufeff", "\u0300", "😀"))
    return [(value, all(char.isspace() or char in "\"'‘’“”()[]" for char in value)
             and not re.search(r"\n\s*\n", value)) for value in unique(separators)], whitespace


def morphology_cases(annotation) -> tuple[list, list]:
    common = """bus box buzz church dish hero go do ax axe age sing singe ting tinge queue
        stop plan hop run rub tap tip rob fit drop skip prefer refer visit offer open travel
        focus cancel panic begin admit occur permit fix wash watch mix play stay enjoy obey
        study carry cry try fly fry dry key toy day say buy tie die lie vie dye eye hoe toe
        see flee free agree walk bake make take like love move hope create use race change
        be is was has yes news gas class kiss pass miss need read feed seed add end enter
        snow show row wax tax way pay low mow allow echo veto quiz tieing singeing ageing
        queueing busing singing axes studies studied stopped stopping tying lying dying""".split()
    small = ["".join(chars) for length in range(1, 4)
             for chars in itertools.product("abeysx", repeat=length)]
    stems = sorted(set([""] + small + common
                       + [a + b for a in ascii_string.ascii_lowercase for b in ascii_string.ascii_lowercase]))
    predicates = [(stem, annotation._must_double(stem), annotation._consonant_y(stem)) for stem in stems]
    words = {"", "s", "es", "ies", "ed", "ied", "ing", "ying", *common}
    for stem in sorted(set(small + common)):
        for suffix in ("s", "es", "ies", "ed", "ied", "ing"):
            words.add(stem + suffix)
        words.add(stem + stem[-1] + "ed")
        words.add(stem + stem[-1] + "ing")
    candidates = [(word, sorted(annotation._morph_candidates(word))) for word in sorted(words)]
    return predicates, candidates


def public_cases(annotation, fixture: dict, whitespace: list[str]) -> tuple[list, int]:
    rows = zero_annotation_rows(fixture, "snapshot")
    require(len(rows) == 16, "Unexpected P0 zero-threshold snapshot count")
    result = []
    with no_restore():
        for row in rows:
            text = row["call"]["args"][0]
            value = annotation.annotate_ips(text)
            require(value == row["expected"]["value"], f"Pinned P0 result changed: {row['id']}")
            result.append((row["id"], text, value))
        fresh = [
            "the apple The Apple THE APPLE tHe aPpLe the book The hour THE university the unknownwordzz the",
            'the "apple" the (apple) the [apple] the ‘apple’ the “apple” the \'apple\'',
            "the, apple; the. apple! the? apple: the—apple the…apple the{apple} the<apple>",
            "the\napple the\n\napple the\n \t\napple the\r\napple the\r\n\r\napple the\r\rapple",
            "the\n\"\napple the\n(\napple the\n‘’\napple the\n[]\napple the\n \t\r\napple",
            "the 中文 apple the 123 apple the café apple the e\u0301 apple the 𝕒 apple the 😀 apple",
            "the中文 apple the123 apple theé apple the\u0301 apple the—😀apple the\u200bapple",
            "the-apple the-book the-hour the-unknownwordzz apple-the apple-the apple apple-the, apple",
            "THE-APPLE The-Apple tHe-aPpLe the-the-apple the's apple the’s apple THE’S APPLE",
            "the-apple's the-apple’s THE-APPLE’S the-unknownwordzz-book unknownwordzz-the-apple",
            "don't doesn't aren't I'm you're o'clock DON’T DOESN’T AREN’T I’M YOU’RE O’CLOCK",
            "doN't dOeSn’T aReN't i'M YoU’rE o’ClOcK can't can’t won't won’t isn’t shouldn’t",
            "apple's APPLE’S aPpLe’s book’s books’ walk's walks’ does'nt doesn't've doesn’t’ve",
            "a’can’t a'can't ca’can’t apple’can’t APPLE’CAN’T apple'unknown'can't unknown'can't",
            "apple-the’s apple apple-the's apple second-the apple second-the, apple",
            "first-rate second-rate second-puldsm pending-compound SECOND-RATE Second-Rate second-apple-book",
            "walks boxes baked baking studies studied stopped stopping plays tying WALKED BAKING STuDiED",
            "ageing aging singeing singing tingeing tinging queueing queuing busing bussing axes is",
            "dies dying lies lying ties tying cries crying tries trying copied copying studies studying",
            "hoping hopping planned planning visited visiting preferred preferring travelled traveling",
            "buses BUSES BuSeS fixes FIXES glasses heroes potatoes goes does passes washes watches quizzes",
            "  The\t(APPLE),\r\nTHE [book].\n\nThe ‘hour’! [unknownwordzz] 😀 中文 123  ",
        ]
        fresh.extend("the" + space + "apple THE" + space + "book The" + space + "hour"
                     for space in whitespace)
        for index, text in enumerate(unique(fresh), 1):
            result.append((f"context-curated-{index:03d}", text, annotation.annotate_ips(text)))
    return result, len(rows)


def available(value: str) -> dict:
    return {"pronunciations": [{"ips": value}]}


def blocked() -> dict:
    return {"state": "pending_review", "reason": "fixture_pending"}


def fallback() -> dict:
    return {"state": "missing", "reason": "source_record_missing"}


def wire_specs(fixture: dict) -> list[tuple[str, dict, list]]:
    p0 = zero_annotation_rows(fixture, "fixture")
    require(len(p0) == 13, "Unexpected P0 zero-threshold fixture count")
    cases = [(row["id"], row["call"]["args"][0], row["expected"]["value"]) for row in p0]
    specs = [("p0_complete_fixture", fixture["fixture_spec"], cases)]
    states = {
        "apple": available("åpple"), "book": available("bòok"), "rate": available("rāte"),
        "second": available("seco̊nd"), "walk": available("wàlk"), "the": available("wrong"),
        "The": blocked(), "THE": fallback(), "don't": blocked(), "doesn't": fallback(),
        "aren't": available("wrong"), "you're": available("yòu're"), "o'clock": fallback(),
        "second-rate": fallback(), "second-apple": blocked(), "second-book": available("wrong"),
        "walks": blocked(), "walked": fallback(), "walking": available("wrong"),
        "apple's": blocked(), "book's": fallback(), "apple’book": blocked(),
    }
    texts = [
        "the apple The apple THE apple tHe apple the book the",
        "don't doesn’t aren't I’m you're o’clock DON’T DOESN’T AREN’T I’M YOU’RE O’CLOCK",
        "second-rate second-apple second-book second-rate-apple apple-book second-unknown",
        "walks walked walking WALKED WALKING walks-book walked-book walking-book",
        "apple's apple’s book's book’s apple’book apple'book",
        "the's apple the’s apple the-apple the-book apple-the apple apple-the, apple",
        "The-apple THE-APPLE tHe-aPpLe apple-The apple apple-THE apple",
    ]
    specs.append(("saved_states_precede_context_and_fallback", {"entries": states, "frequency": {}}, texts))
    prefixes = {"a": available("ā"), "ca": available("cā"), "can": available("cãn"),
                "apple": available("åpple"), "book": available("book"), "the": available("wrong")}
    prefix_texts = [
        "can't can’t CAN’T CaN’T can't've can’t’ve can’t’can’t",
        "a’can’t a'can't ca’can’t apple’can’t APPLE’CAN’T a’can’t’book",
        "apple'book apple’book apple's APPLE’S aPpLe’s apple’unknown’book",
        "the's apple the’s apple THE’S APPLE the-the’s apple the-apple’s the’s-apple",
    ]
    specs.append(("apostrophe_prefers_nt_prefix_and_cuts_unicode_scalars", {"entries": prefixes, "frequency": {}}, prefix_texts))
    for name, ca in (("blocked", blocked()), ("fallback", fallback()), ("malformed", available("wrong"))):
        entries = {**prefixes, "ca": ca}
        specs.append((f"apostrophe_first_prefix_{name}", {"entries": entries, "frequency": {}},
                      ["can't can’t CAN’T CaN’T a’can’t ca’can’t can't've can’t’ve"]))
    variants = [
        ("same_outputs", available("bûs"), available("bûse")),
        ("different_outputs", available("bûs"), available("bùse")),
        ("blocked_first", blocked(), available("bûse")),
        ("blocked_second", available("bûs"), blocked()),
        ("fallback_first", fallback(), available("bûse")),
        ("fallback_second", available("bûs"), fallback()),
        ("malformed_first", available("wrong"), available("bûse")),
        ("malformed_second", available("bûs"), available("wrong")),
        ("absent_first", None, available("bûse")),
        ("absent_second", available("bûs"), None),
        ("both_malformed", available("wrong"), available("wrong")),
        ("both_fallback", fallback(), fallback()),
    ]
    for name, bus, buse in variants:
        entries = {"book": available("book")}
        for word, value in (("bus", bus), ("buse", buse)):
            if value is not None:
                entries[word] = value
        specs.append((f"inflection_buses_{name}", {"entries": entries, "frequency": {}},
                      ["buses BUSES BuSeS buses' buses’ buses-book buses’book"]))
    entries = {"bus": available("bûs"), "buse": available("bûse"), "Bus": blocked(),
               "BUS": fallback(), "Buse": available("wrong"), "buses": fallback()}
    specs.append(("inflection_candidate_first_existing_variant", {"entries": entries, "frequency": {}},
                  ["buses BUSES Buses BuSeS bUsEs", "buses buses’ buses-book"]))
    entries = {word: available(value) for word, value in {
        "study": "stûdẏ", "play": "plāy", "stop": "stòp", "walk": "wàlk", "tie": "tīe",
        "die": "dīe", "lie": "līe", "bake": "bāke", "box": "bòx", "age": "āge",
        "singe": "si̊nge", "tinge": "ti̊nge", "queue": "qūeue", "whale": "w̄𝕙āle",
        "whim": "ẘ𝕙i̊m", "yum": "ẙu̇m", "key": "kēy", "see": "sēe", "dye": "dẏe",
        "hoe": "hōe", "cry": "crẏ", "fly": "flẏ", "try": "trẏ", "go": "gō",
    }.items()}
    specs.append(("inflection_projection_keeps_clusters_and_spelling", {"entries": entries, "frequency": {}}, [
        "studies studied studying STUDIES STuDiED StUdYiNg plays played playing PLAYED",
        "stops stopped stopping STOPPED SToPpInG walks walked walking boxes BOXES",
        "ties tied tying dies died dying lies lied lying bakes baked baking BAKING",
        "ageing aging singeing singing tingeing tinging queueing queuing",
        "whales WHALES WHiMs yums YUMS keys seeing dyeing hoeing cries cried crying flies tried trying goes",
        "studys studyed stoped stoping bakeing singeing tinging queuing queueing",
    ]))
    return specs


def wire_cases(annotation, baseline: dict, fixture: dict) -> list:
    from lingose import query
    directory = ROOT / ".local"
    directory.mkdir(exist_ok=True)
    result = []
    with tempfile.TemporaryDirectory(prefix="annotation-context-oracle-", dir=directory) as temporary:
        for index, (name, spec, texts) in enumerate(wire_specs(fixture)):
            path = Path(temporary) / f"{index}.sqlite"
            frequency = Path(temporary) / f"{index}-frequency.sqlite"
            build_fixture(path, frequency, baseline, spec)
            records = []
            cases = []
            with fixture_paths(path, frequency):
                with query._open_database() as (database, _):
                    annotator = annotation._Annotator(database, set())
                    for word in sorted(spec["entries"]):
                        match = annotator.exact(word)
                        require(match.exists, "Fixture entry disappeared")
                        state = 2 if match.notation is not None else 1 if match.fallback else 0
                        records.append((word, match.notation, state))
                for number, item in enumerate(texts, 1):
                    if isinstance(item, tuple):
                        identifier, text, expected = item
                    else:
                        identifier, text, expected = f"{name}-{number:02d}", item, None
                    value = annotation.annotate_ips(text)
                    if expected is not None:
                        require(value == expected, f"Pinned P0 fixture result changed: {identifier}")
                    cases.append((identifier, text, value))
            result.append((name, records, cases))
    return result


def render_helpers(baseline: dict, separators: list, predicates: list, candidates: list) -> str:
    lines = header(baseline, {"separators": separators, "predicates": predicates, "candidates": candidates})
    lines += ["use super::{consonant_y, context_separator, morph_candidates, must_double};", "", "#[test]",
              "fn pinned_python_context_separator_includes_all_29_whitespace_characters() {",
              "    let cases: &[(&str, bool)] = &["]
    for value, expected in separators:
        lines.append(f"        ({string(value)}, {str(bool(expected)).lower()}),")
    lines += ["    ];", "    for &(value, expected) in cases {",
              '        assert_eq!(context_separator(value), expected, "{value:?}");', "    }", "}", "", "#[test]",
              "fn pinned_python_stem_predicates_match_spelling_rules() {",
              "    let cases: &[(&str, bool, bool)] = &["]
    for stem, double, consonant in predicates:
        lines.append(f"        ({string(stem)}, {str(double).lower()}, {str(consonant).lower()}),")
    lines += ["    ];", "    for &(stem, double, consonant) in cases {",
              '        assert_eq!(must_double(stem), double, "must_double {stem:?}");',
              '        assert_eq!(consonant_y(stem), consonant, "consonant_y {stem:?}");', "    }", "}", "", "#[test]",
              "fn pinned_python_morph_candidates_match_all_sorted_candidates() {",
              "    type MorphCandidate<'a> = (&'a str, usize, &'a str);",
              "    let cases: &[(&str, &[MorphCandidate<'_>])] = &["]
    for word, expected in candidates:
        values = ", ".join(f"({string(stem)}, {retained}, {string(tail)})" for stem, retained, tail in expected)
        lines.append(f"        ({string(word)}, &[{values}]),")
    lines += ["    ];", "    for &(word, expected) in cases {", "        let mut actual = morph_candidates(word);",
              "        actual.sort();", "        let expected: Vec<_> = expected.iter().map(|&(stem, retained, tail)|",
              "            (stem.to_owned(), retained, tail.to_owned())).collect();",
              '        assert_eq!(actual, expected, "{word:?}");', "    }", "}", ""]
    return "\n".join(lines)


def render_public(baseline: dict, cases: list) -> str:
    lines = header(baseline, cases)
    lines += ["#[test]", "fn pinned_python_complete_zero_threshold_annotation_outputs_match() {",
              "    let cases: &[(&str, &str, &str)] = &["]
    for identifier, text, value in cases:
        lines.append(f"        ({string(identifier)}, {string(text)}, {string(value)}),")
    lines += ["    ];", "    for &(identifier, text, expected) in cases {",
              '        assert_eq!(lingose::annotate_ips(text).unwrap(), expected, "{identifier}");',
              '        assert_eq!(lingose::annotate_ips_with_skip_top(text, 0).unwrap(), expected, "{identifier}/zero");',
              "    }", "}", ""]
    return "\n".join(lines)


def render_wire(baseline: dict, specs: list) -> str:
    lines = header(baseline, specs)
    lines += ["use super::{Record, encode, lexicon_fixture};", "use crate::annotation::annotate_from;",
              "use crate::data::AnnotationResources;", ""]
    for name, records, cases in specs:
        lines += ["#[test]", f"fn pinned_python_{name}() {{", "    let entries = ["]
        for word, ips, state in records:
            value = "None" if ips is None else f"Some({string(ips)})"
            lines.append(f"        ({string(word)}, {value}, {state}),")
        lines += ["    ];", "    let records: Vec<_> = entries.iter().map(|&(word, ips, state)| {",
                  "        let mut fields = [None; 7];", "        fields[1] = ips;",
                  "        Record { word, fields, state }", "    }).collect();",
                  "    let lexicon = lexicon_fixture(encode(&records, &[], &[]));",
                  "    let cases: &[(&str, &str, &str)] = &["]
        for identifier, text, value in cases:
            lines.append(f"        ({string(identifier)}, {string(text)}, {string(value)}),")
        lines += ["    ];", "    for &(identifier, text, expected) in cases {",
                  "        let actual = annotate_from(text, 0, |has_tokens, threshold| {",
                  "            assert!(has_tokens);", "            assert_eq!(threshold, 0);",
                  "            Ok(Some(AnnotationResources { lexicon: &lexicon, frequency: None }))",
                  "        }).unwrap();", '        assert_eq!(actual, expected, "{identifier}");', "    }", "}", ""]
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
    _, package, _, _ = installed()
    from lingose import annotation
    require(Path(annotation.__file__).resolve() == package / "annotation.py", "Unexpected oracle module path")
    fixture = json.loads(SOURCE.read_bytes())
    separators, whitespace = separator_cases()
    predicates, candidates = morphology_cases(annotation)
    public, p0_count = public_cases(annotation, fixture, whitespace)
    wire = wire_cases(annotation, before, fixture)
    raw = {HELPER_TARGET: render_helpers(before, separators, predicates, candidates),
           PUBLIC_TARGET: render_public(before, public), WIRE_TARGET: render_wire(before, wire)}
    outputs = {}
    for target, content in raw.items():
        formatted = subprocess.run(["rustfmt", "--edition", "2024", "--emit", "stdout"],
                                   input=content, text=True, encoding="utf-8", capture_output=True, check=True)
        outputs[target] = formatted.stdout.replace("\r\n", "\n").encode("utf-8")
        require(b"\r" not in outputs[target], "Generated Rust must use LF")
    require(require_baseline() == before, "Installed source or resource identity changed during generation")
    require(sha256(SOURCE) == SOURCE_SHA256 and sha256(BASELINE) == BASELINE_SHA256,
            "Frozen P0 inputs changed during generation")
    return outputs, {"context_separator_inputs": len(separators), "python_whitespace_scalars": len(whitespace),
                     "stem_predicate_inputs": len(predicates), "morph_candidate_inputs": len(candidates),
                     "morph_candidate_tuples": sum(len(value) for _, value in candidates),
                     "public_p0": p0_count, "public_curated": len(public) - p0_count,
                     "public_assertions": 2 * len(public), "wire_specs": len(wire),
                     "wire_p0": len(wire[0][2]), "wire_assertions": sum(len(cases) for _, _, cases in wire)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, counts = generate()
    # Check every target before creating any missing output. A later drift must
    # never leave an earlier artifact newly written after a rejected run.
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
