"""Render frozen P0 category values and complete-list digests as Rust tests.

The oracle is the immutable Python fixture, never the Rust implementation.
--write creates a missing output only; both modes refuse different existing
bytes. Canonical JSON serialization is test-only and adds no crate dependency.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import ROOT, main_error, require, sha256

SOURCE = ROOT / "tests/fixtures/python-api-v1.json"
SOURCE_SHA256 = "6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1"
TARGET = ROOT / "tests/category_vectors.rs"


def string(value: str) -> str:
    # ASCII Rust literals preserve every scalar, without Unicode normalization.
    return '"' + "".join(
        {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t", "\0": "\\0"}.get(
            char, char if 0x20 <= ord(char) < 0x7f else f"\\u{{{ord(char):x}}}"
        ) for char in value
    ) + '"'


def strings(values: list[str]) -> str:
    require(all(type(value) is str for value in values), "Expected a string list")
    return "&[" + ", ".join(map(string, values)) + "]"


def invalid(expression: str, parameter: str, identifier: str) -> str:
    return (f"    assert!(matches!({expression}, "
            f"Err(lingose::Error::InvalidArgument {{ parameter: {string(parameter)}, .. }})), "
            f"{string(identifier)});")


HELPERS = r'''
use std::fmt::Write as _;

use sha2::{Digest, Sha256};

// Match Python json.dumps(..., ensure_ascii=false, separators=(",", ":")):
// no BOM, trailing newline, whitespace, slash escaping, or normalization.
fn canonical_list(words: &[String]) -> String {
    let mut json = String::from("[");
    for (index, word) in words.iter().enumerate() {
        if index != 0 {
            json.push(',');
        }
        json.push('"');
        for character in word.chars() {
            match character {
                '"' => json.push_str("\\\""),
                '\\' => json.push_str("\\\\"),
                '\u{8}' => json.push_str("\\b"),
                '\u{c}' => json.push_str("\\f"),
                '\n' => json.push_str("\\n"),
                '\r' => json.push_str("\\r"),
                '\t' => json.push_str("\\t"),
                '\0'..='\u{1f}' => write!(&mut json, "\\u{:04x}", u32::from(character)).unwrap(),
                _ => json.push(character),
            }
        }
        json.push('"');
    }
    json.push(']');
    json
}

fn assert_complete_list(
    label: &str,
    actual: Vec<String>,
    length: usize,
    sha256: &str,
    head: &[&str],
    tail: &[&str],
) {
    assert_eq!(actual.len(), length, "{label} complete list length");
    assert_eq!(
        format!("{:x}", Sha256::digest(canonical_list(&actual).as_bytes())),
        sha256,
        "{label} complete ordered list digest"
    );
    assert_eq!(
        actual.iter().take(head.len()).map(String::as_str).collect::<Vec<_>>(),
        head,
        "{label} list head"
    );
    assert_eq!(
        actual.iter().skip(actual.len() - tail.len()).map(String::as_str).collect::<Vec<_>>(),
        tail,
        "{label} list tail"
    );
    for word in &actual {
        assert!(lingose::kind_with_label(word, label).unwrap(), "{word}/{label} list member");
    }
}
'''


def render() -> tuple[str, dict]:
    require(sha256(SOURCE) == SOURCE_SHA256,
            "P0 fixture identity changed; do not overwrite its baseline")
    fixture = json.loads(SOURCE.read_bytes())
    rows = [row for row in fixture["cases"] if row["source"] == "snapshot"]
    lines = ["//! Generated from frozen P0 snapshot category outputs; do not edit by hand.",
             f"//! Source SHA-256: {SOURCE_SHA256}", HELPERS]
    label_rows = [row for row in rows if row["call"]["api"] == "labels"]
    require(len(label_rows) == 1, "Expected one complete labels vector")
    labels = label_rows[0]["expected"]["value"]
    require(len(labels) == len(set(labels)), "Duplicate P0 labels")
    lines += ["#[test]", "fn p0_snapshot_labels_match_python_configuration_order() {",
              f"    assert_eq!(lingose::labels().unwrap(), {strings(labels)});", "}", ""]

    lines += ["#[test]", "fn p0_snapshot_membership_values_and_errors_match_python() {"]
    membership_values = membership_errors = 0
    for row in rows:
        call = row["call"]
        args = call.get("args", [])
        if call["api"] != "kind" or not all(type(arg) is str for arg in args):
            continue
        require(len(args) in (1, 2), "Unexpected kind argument count")
        api = "kind" if len(args) == 1 else "kind_with_label"
        expression = f"lingose::{api}({', '.join(map(string, args))})"
        expected = row["expected"]
        if "value" in expected:
            require(type(expected["value"]) is bool, "Expected boolean membership")
            negate = "" if expected["value"] else "!"
            lines.append(f"    assert!({negate}{expression}.unwrap(), {string(row['id'])});")
            membership_values += 1
        else:
            require(expected == {"error": "ValueError"}, "Unexpected kind error")
            parameter = {"invalid-word": "word", "invalid-label": "label"}.get(call["group"])
            require(parameter is not None, "Unmapped kind error precedence")
            lines.append(invalid(expression, parameter, row["id"]))
            membership_errors += 1
    lines += ["}", "", "#[test]", "fn p0_snapshot_complete_ordered_lists_match_python() {"]
    summaries = {}
    list_errors = []
    list_count = checked_entries = 0
    for row in rows:
        call = row["call"]
        args = call.get("args", [])
        if call["api"] != "kind_list" or not all(type(arg) is str for arg in args):
            continue
        require(len(args) <= 1, "Unexpected kind_list argument count")
        expression = (f"lingose::kind_list_with_label({string(args[0])})" if args
                      else "lingose::kind_list()")
        expected = row["expected"]
        if "error" in expected:
            require(expected == {"error": "ValueError"} and call["group"] == "invalid-label",
                    "Unexpected kind_list error")
            list_errors.append(invalid(expression, "label", row["id"]))
            continue
        summary = expected["ordered_list"]
        label = args[0] if args else "CET4"
        require(label in labels, "Unregistered P0 list label")
        require(set(summary) == {"length", "sha256", "head", "tail"},
                "Incomplete ordered-list oracle")
        require(type(summary["length"]) is int and summary["length"] >= max(len(summary["head"]), len(summary["tail"])),
                "Invalid complete-list length")
        require(len(summary["sha256"]) == 64
                and all(char in "0123456789abcdef" for char in summary["sha256"]),
                "Invalid complete-list SHA-256")
        if label in summaries:
            require(summaries[label] == summary, "Default/explicit category oracle differs")
        summaries[label] = summary
        lines.append(f"    assert_complete_list({string(label)}, {expression}.unwrap(), "
                     f"{summary['length']}, {string(summary['sha256'])}, "
                     f"{strings(summary['head'])}, {strings(summary['tail'])});")
        list_count += 1
        checked_entries += summary["length"]
    require(set(summaries) == set(labels) and list_count == len(labels) + 1,
            "Expected every registered list and the default CET4 list")
    lines += ["}", "", "#[test]", "fn p0_snapshot_invalid_list_labels_match_python() {",
              *list_errors, "}", "", "#[test]",
              "fn canonical_list_serializer_matches_independent_python_json_fixtures() {"]
    # Expected bytes come from Python's serializer, independently of Rust logic.
    samples = [[], [""],
               ['"\\/\b\f\n\r\t\0\x01\x0b\x1f', '\x7f\u0085\u2028\u2029 é e\u0301 😀']]
    for sample in samples:
        rust_values = "&[" + ", ".join(f"String::from({string(value)})" for value in sample) + "]"
        expected = json.dumps(sample, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        lines.append(f"    assert_eq!(canonical_list({rust_values}), {string(expected)});")
    lines += ["}", ""]
    require(sha256(SOURCE) == SOURCE_SHA256, "P0 fixture changed during generation")
    return "\n".join(lines), {
        "labels": len(labels), "membership_values": membership_values,
        "membership_errors": membership_errors, "complete_lists": list_count,
        "list_label_errors": len(list_errors), "unique_member_total": sum(row["length"] for row in summaries.values()),
        "checked_list_entries_including_default": checked_entries, "serializer_samples": len(samples),
    }


def persist(path: Path, content: bytes, write: bool) -> str:
    if path.exists():
        require(path.read_bytes() == content, f"Recorded artifact drift: {path}; existing bytes preserved")
        return "unchanged"
    require(write, f"Missing artifact: {path}; use --write for initial creation")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)
    return "created"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content, counts = render()
    formatted = subprocess.run(["rustfmt", "--edition", "2024", "--emit", "stdout"],
                               input=content, text=True, encoding="utf-8", capture_output=True, check=True)
    output = formatted.stdout.replace("\r\n", "\n").encode("utf-8")
    require(b"\r" not in output, "Generated Rust must use LF")
    print(json.dumps({"status": persist(TARGET, output, args.write), **counts}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
