"""Derive portable notices without changing pinned development evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/distribution-provenance.json"


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def generate():
    names = ["docs/query-case.json", "docs/annotation-unicode.json", "docs/loader-verification.json",
             "Cargo.lock", "src/query_case_tables.rs", "src/annotation_unicode_tables.rs",
             "third_party/unicode/LICENSE.txt"]
    before = {name: identity(ROOT / name) for name in names}
    query, annotation, loader = [json.loads((ROOT / name).read_bytes()) for name in names[:3]]
    assert query["unicode_version"] == annotation["unicode_version"] == "15.0.0"
    assert query["artifacts"]["src/query_case_tables.rs"] == before["src/query_case_tables.rs"]
    assert {key: annotation["tables"][key] for key in ("bytes", "sha256")} == before["src/annotation_unicode_tables.rs"]
    assert query["artifacts"]["third_party/unicode/LICENSE.txt"] == before["third_party/unicode/LICENSE.txt"]
    dependencies = loader["dependencies"]
    locked = tomllib.loads((ROOT / "Cargo.lock").read_text(encoding="utf-8"))
    assert {(row["name"], row["version"]) for row in dependencies} == {
        (row["name"], row["version"]) for row in locked["package"] if row["name"] != "lingose"}
    tables = []
    for source, record, artifact in [(names[0], query, "src/query_case_tables.rs"),
                                     (names[1], annotation, "src/annotation_unicode_tables.rs")]:
        provenance = record["provenance"]
        tables.append({
            "artifact": artifact, "identity": before[artifact], "unicode_version": record["unicode_version"],
            "scalar_sha256": record["scalar_sha256"], "counts": record["counts"],
            "generator": record["generator"],
            "historical_source_record": {"name": source, **before[source]},
            "baseline_identity": {key: provenance["baseline"][key] for key in ("bytes", "sha256")},
            "python": {key: provenance["python"][key] for key in ("implementation", "version", "unicode_version")},
            "installed_module_identities": {
                key: {field: value[field] for field in ("bytes", "sha256")}
                for key, value in provenance.items() if key.startswith("installed_")},
        })
    result = {
        "format_version": 1,
        "scope": "Portable attribution excerpt of fixed development records; omitted host paths are not build or runtime requirements. Original records remain unchanged in the development checkout.",
        "unicode_tables": tables,
        "unicode_license": {"name": "Unicode License V3", "url": "https://www.unicode.org/license.txt",
                            "file": "third_party/unicode/LICENSE.txt", **before["third_party/unicode/LICENSE.txt"]},
        "dependency_notices": {"scope": "Historical declared licenses and Rust versions; locked name/version pairs checked against this distribution, not future resolutions",
                               "cargo_lock": before["Cargo.lock"], "dependencies": dependencies,
                               "historical_source_record": {"name": names[2], **before[names[2]]}},
    }
    assert before == {name: identity(ROOT / name) for name in names}, "Input identity drift"
    return (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = generate()
    if OUTPUT.exists():
        assert OUTPUT.read_bytes() == value, "Existing portable notice differs; do not silently replace it"
    elif args.write:
        OUTPUT.write_bytes(value)
    else:
        raise RuntimeError("Missing portable notice; initial creation requires --write")
    print("Portable source notices match protected records")


if __name__ == "__main__":
    main()
