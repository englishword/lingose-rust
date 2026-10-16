"""Render P0 snapshot simple-query vectors as dependency-free Rust assertions.

The oracle stays the frozen Python fixture, never the Rust implementation.
--write creates a missing output only; --check refuses any drift.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import ROOT, freeze, main_error, require, sha256

SOURCE = ROOT / "tests/fixtures/python-api-v1.json"
SOURCE_SHA256 = "6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1"
APIS = {"ipa", "IPA", "ips", "IPS", "ism", "ISM", "ipsm", "IPSM", "root_lemma", "meaning"}


def string(value):
    # ASCII Rust literals retain exact scalar sequences, including newlines.
    return '"' + "".join(
        {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t", "\0": "\\0"}.get(
            char, char if 0x20 <= ord(char) < 0x7f else f"\\u{{{ord(char):x}}}"
        ) for char in value
    ) + '"'


def render():
    require(sha256(SOURCE) == SOURCE_SHA256, "P0 fixture identity changed; do not overwrite its baseline")
    fixture = json.loads(SOURCE.read_text(encoding="utf-8"))
    lines = ["//! Generated from frozen P0 snapshot outputs; do not edit by hand.",
             f"//! Source SHA-256: {sha256(SOURCE)}", "", "#[test]",
             "fn p0_snapshot_simple_queries_match_python() {"]
    count = 0
    for row in fixture["cases"]:
        call = row["call"]
        if row["source"] != "snapshot" or call["api"] not in APIS or "value" not in row["expected"]:
            continue
        api, args, value = call["api"], call.get("args", []), row["expected"]["value"]
        require(all(type(arg) is str for arg in args), "Unexpected non-string value case")
        if api == "meaning" and len(args) == 2:
            api = "meaning_with_lang"
        expression = f"lingose::{api}({', '.join(map(string, args))}).unwrap()"
        if isinstance(value, list):
            expected = "Vec::<String>::new()" if not value else "vec![" + ", ".join(f"String::from({string(v)})" for v in value) + "]"
        else:
            expected = "None" if value is None else f"Some(String::from({string(value)}))"
        lines.append(f"    assert_eq!({expression}, {expected});")
        count += 1
    lines += ["}", ""]
    require(count > 0, "No P2.3 snapshot vectors found")
    return "\n".join(lines), count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content, count = render()
    # rustfmt is part of the established development toolchain, not crate build.
    import subprocess
    formatted = subprocess.run(["rustfmt", "--edition", "2024", "--emit", "stdout"],
                               input=content, text=True, encoding="utf-8", capture_output=True, check=True)
    target = ROOT / "tests/query_vectors.rs"
    print(f"{freeze(target, formatted.stdout.replace(chr(13) + chr(10), chr(10)), args.write)}: {count} P0 queries")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
