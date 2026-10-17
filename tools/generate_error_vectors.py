"""Freeze P4.1 rare query/category states through an independent wire fixture.

Expected values come from fixed P0 and the pinned installed Python public API.
No production exporter is imported. Rust's independent test encoder supplies the
wire image; temporary SQLite files are disposable and source data stays read-only.
--write creates a missing artifact only; --check rejects generated-byte drift.
"""

from __future__ import annotations

import argparse
from contextlib import closing
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (BASELINE, ROOT, LIB_ROOT, canonical, connect, installed, main_error,
                       require, require_baseline, sha256)
from generate_annotation_vectors import (BASELINE_SHA256, SOURCE, SOURCE_SHA256,
                                         header, persist, string)
from capture_api_vectors import build_fixture, evaluate, fixture_paths

TARGET = LIB_ROOT / "src/data/p41_query_fixture_tests.rs"
WORD_APIS = ("IPA", "IPS", "ISM", "IPSM", "root_lemma", "meaning")


def complete(word: str) -> dict:
    return {"pronunciations": [{"ipa": "fixture ipa", "ips": word, "ipsm": word}],
            "fields": {"ism": word, "root_lemma": "family", "rank": "0",
                       "meaning_en": "first\nsecond", "meaning_zh": "中文 e\u0301",
                       "kind:CET4": True}}


def extended_spec(fixture: dict) -> tuple[dict, list[dict]]:
    spec = copy.deepcopy(fixture["fixture_spec"])
    cases = []
    statuses = [("source", "missing", "source_record_missing"),
                ("empty", "missing", "empty_cell"),
                ("pending", "pending_review", "fixture_pending"),
                ("conflict", "conflict", "fixture_conflict"),
                ("invalid", "invalid", "fixture_invalid")]
    for scope in ("set", "field"):
        for suffix, status, reason in statuses:
            lower = scope + suffix
            upper = lower.capitalize()
            unavailable = {"status": status, "reason": reason}
            spec["entries"][lower] = complete(lower)
            blocked = {"fields": {key: unavailable for key in
                       ("ism", "root_lemma", "meaning_en", "meaning_zh", "kind:CET4")}}
            if scope == "set":
                blocked.update(state=status, reason=reason)
            else:
                # An unavailable selected IPS must leave independent IPA usable.
                blocked["pronunciations"] = [{"ipa": "available ipa", "ips": unavailable}]
            spec["entries"][upper] = blocked
            for word in (upper, lower):
                for api in WORD_APIS:
                    cases.append({"api": api, "args": [word]})
                cases.extend(({"api": "meaning", "args": [word, "zh"]},
                              {"api": "kind", "args": [word, "CET4"]}))
            cases.append({"api": "annotate_ips", "args": [f"{upper} {lower} {upper.upper()}"]})
    # Explicit false remains an ordinary result and blocks lowercase membership.
    spec["entries"]["falsecategory"] = complete("falsecategory")
    spec["entries"]["Falsecategory"] = {"fields": {"kind:CET4": False}}
    cases.extend(({"api": "kind", "args": ["Falsecategory", "CET4"]},
                  {"api": "kind", "args": ["falsecategory", "CET4"]},
                  {"api": "labels"}))
    return spec, cases


def oracle(baseline: dict, fixture: dict, spec: dict, extra: list) -> tuple[list, list, list]:
    from lingose import annotation, query
    p0 = [row for row in fixture["cases"] if row["source"] == "fixture"
          and row["call"]["api"] != "annotate_ips"]
    require(len(p0) == 14, "P0 query/category fixture coverage changed")
    directory = ROOT / ".local"
    directory.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="p41-query-oracle-", dir=directory) as temporary:
        path, frequency = Path(temporary) / "main.sqlite", Path(temporary) / "frequency.sqlite"
        build_fixture(path, frequency, baseline, spec)
        before = [sha256(value) for value in (path, frequency)]
        cases, records = [], []
        with fixture_paths(path, frequency):
            # Only the P0 fixture has the frozen P0 ordered category list.
            # Additions change it, so compare P0 below in its own isolated spec.
            for index, call in enumerate(extra, 1):
                cases.append((f"rare-{index:03d}", call, evaluate(call)["value"]))
            with closing(connect(path)) as db:
                annotator = annotation._Annotator(db, set())
                for word in sorted(spec["entries"]):
                    values = [getattr(query, api)(word) for api in WORD_APIS[:4]]
                    require(all(len(value) <= 1 for value in (values[0], values[1], values[3])),
                            "The selected-pronunciation projection must contain at most one value")
                    fields = [values[0][0] if values[0] else None,
                              values[1][0] if values[1] else None, values[2],
                              values[3][0] if values[3] else None,
                              query.root_lemma(word), query.meaning(word, "en"), query.meaning(word, "zh")]
                    match = annotator.exact(word)
                    require(match.exists, "Fixture entry disappeared")
                    records.append((word, fields, 2 if match.notation is not None else int(match.fallback)))
            labels = [(label, query.kind_list(label)) for label in query.labels()]
            cases.extend((f"complete-category-{index:02d}", {"api": "kind_list", "args": [label]}, members)
                         for index, (label, members) in enumerate(labels))
        require(before == [sha256(value) for value in (path, frequency)], "Oracle modified fixture files")
    return records, labels, cases


def p0_oracle(baseline: dict, fixture: dict) -> tuple[list, list, list]:
    spec = fixture["fixture_spec"]
    records, labels, _ = oracle(baseline, fixture, spec, [])
    cases = [(row["id"], row["call"], row["expected"]["value"])
             for row in fixture["cases"] if row["source"] == "fixture"
             and row["call"]["api"] != "annotate_ips"]
    # Re-evaluate fixed P0 results independently before encoding Rust fixtures.
    directory = ROOT / ".local"
    with tempfile.TemporaryDirectory(prefix="p41-p0-check-", dir=directory) as temporary:
        path, frequency = Path(temporary) / "main.sqlite", Path(temporary) / "frequency.sqlite"
        build_fixture(path, frequency, baseline, spec)
        before = [sha256(value) for value in (path, frequency)]
        with fixture_paths(path, frequency):
            for identifier, call, expected in cases:
                require(evaluate(call)["value"] == expected, f"P0 fixture result changed: {identifier}")
        require(before == [sha256(value) for value in (path, frequency)], "P0 oracle modified fixtures")
    return records, labels, cases


def optional(value):
    return "None" if value is None else f"Some({string(value)})"


def expression(call: dict, expected) -> tuple[str, str]:
    api, args = call["api"], call.get("args", [])
    word = string(args[0]) if args else None
    field = {"IPA": "Ipa", "IPS": "Ips", "ISM": "Ism", "IPSM": "Ipsm", "root_lemma": "RootLemma"}
    if api in field or api == "meaning":
        language = optional(args[1] if len(args) > 1 else "en") if api == "meaning" else "None"
        target = "MeaningZh" if api == "meaning" and len(args) > 1 and args[1] == "zh" else "MeaningEn"
        target = field.get(api, target)
        actual = f"crate::query::value_from({word}, Field::{target}, {language}, || Ok(&lexicon)).unwrap()"
        if api in ("IPA", "IPS", "IPSM"):
            require(len(expected) <= 1, "Expected selected list must contain at most one value")
            expected = expected[0] if expected else None
        return actual, optional(expected)
    if api == "kind":
        label = string(args[1] if len(args) > 1 else "CET4")
        return f"crate::category::kind_from({word}, {label}, || Ok(&lexicon)).unwrap()", str(expected).lower()
    if api == "kind_list":
        label = string(args[0] if args else "CET4")
        actual = f"crate::category::list_from({label}, || Ok(&lexicon)).unwrap()"
    elif api == "labels":
        actual = "crate::category::labels_from(|| Ok(&lexicon)).unwrap()"
    else:
        require(api == "annotate_ips", "Unexpected fixture API")
        return (f"crate::annotation::annotate_from({word}, 0, |_, _| Ok(Some(AnnotationResources {{ lexicon: &lexicon, frequency: None }}))).unwrap()",
                string(expected))
    return actual, ("[" + ", ".join(string(value) for value in expected) + "]"
                    if expected else "Vec::<String>::new()")


def render(baseline: dict, suites: list) -> str:
    lines = header(baseline, suites)
    lines += ["use super::{Record, encode, lexicon_fixture};", "use crate::data::{AnnotationResources, Field};", ""]
    for name, (records, labels, cases) in suites:
        lines += ["#[test]", f"fn {name}() {{", "    let records = ["]
        ids = {word: index for index, (word, _, _) in enumerate(records)}
        for word, fields, state in records:
            values = ", ".join(optional(value) for value in fields)
            lines.append(f"        Record {{ word: {string(word)}, fields: [{values}], state: {state} }},")
        lines += ["    ];", "    let categories: &[(&str, &[usize])] = &["]
        for label, members in labels:
            lines.append(f"        ({string(label)}, &[{', '.join(str(ids[word]) for word in members)}]),")
        lines += ["    ];", "    let lexicon = lexicon_fixture(encode(&records, categories, &[]));"]
        for identifier, call, expected in cases:
            actual, value = expression(call, expected)
            # Optional results own their strings; fixture record strings borrow.
            if value.startswith("Some("):
                value = "Some(String::from(" + value[5:-1] + "))"
            if type(expected) is bool:
                lines.append(f"    assert!({'!' if not expected else ''}{actual}, {string(identifier)});")
            else:
                lines.append(f"    assert_eq!({actual}, {value}, {string(identifier)});")
        lines += ["}", ""]
    return "\n".join(lines)


def generate() -> tuple[bytes, dict]:
    require(sha256(SOURCE) == SOURCE_SHA256 and sha256(BASELINE) == BASELINE_SHA256,
            "Frozen P0 input identity changed")
    baseline = require_baseline()
    environment = baseline["environment"]
    require(sys.version == environment["python"] and sys.platform == environment["platform"]
            and Path(sys.executable).resolve() == Path(environment["executable"]).resolve()
            and unicodedata.unidata_version == environment["unicode_version"] == "15.0.0",
            "Use the pinned Python runtime and Unicode version")
    _, package, _, _ = installed()
    from lingose import query
    require(Path(query.__file__).resolve() == package / "query.py", "Unexpected oracle module path")
    fixture = json.loads(SOURCE.read_bytes())
    spec, extra = extended_spec(fixture)
    suites = [("p41_fixed_p0_query_category_fixtures", p0_oracle(baseline, fixture)),
              ("p41_independent_unavailable_state_fixtures", oracle(baseline, fixture, spec, extra))]
    content = render(baseline, suites)
    formatted = subprocess.run(["rustfmt", "--edition", "2024", "--emit", "stdout"], input=content,
                               text=True, encoding="utf-8", capture_output=True, check=True)
    require(require_baseline() == baseline, "Installed reference changed during generation")
    require(sha256(SOURCE) == SOURCE_SHA256 and sha256(BASELINE) == BASELINE_SHA256,
            "Frozen P0 inputs changed during generation")
    return formatted.stdout.replace("\r\n", "\n").encode("utf-8"), {
        "suites": len(suites), "p0_query_category_cases": len(suites[0][1][2]),
        "rare_cases": len(suites[1][1][2]), "rare_states": 10,
        "records": [len(suite[0]) for _, suite in suites],
        "payload_sha256": hashlib.sha256(canonical(suites)).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content, counts = generate()
    print(json.dumps({"status": persist(TARGET, content, args.write), **counts}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
