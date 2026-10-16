"""Verify P2 queries in an isolated offline copy and data-free runtime directory.

Default: P2.3 evidence. --categories: P2.4 evidence, preserving the P2.3 report.
--annotation: P3.1 evidence, preserving both P2 reports.
--annotation-context: P3.2 evidence, preserving P3.1 and both P2 reports.
--annotation-frequency: P3.3 evidence, preserving all earlier reports.
Not a packaged-crate check or final P4 acceptance run.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (ROOT, file_record, fingerprints, json_text, main_error,
                       require, require_baseline)


def run(arguments, directory, environment):
    result = subprocess.run(arguments, cwd=directory, env=environment,
                            capture_output=True, text=True, encoding="utf-8")
    require(result.returncode == 0,
            f"Command failed: {arguments}\n{result.stdout}\n{result.stderr}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--categories", action="store_true", help="Verify P2.4 and write category-verification.json")
    mode.add_argument("--annotation", action="store_true", help="Verify P3.1 and write annotation-verification.json")
    mode.add_argument("--annotation-context", action="store_true", help="Verify P3.2 and write annotation-context-verification.json")
    mode.add_argument("--annotation-frequency", action="store_true", help="Verify P3.3 and write annotation-frequency-verification.json")
    args = parser.parse_args()
    context = args.annotation_context or args.annotation_frequency
    annotation = args.annotation or context
    categories = args.categories or annotation
    phase = "P3.3" if args.annotation_frequency else "P3.2" if args.annotation_context else "P3.1" if args.annotation else "P2.4" if args.categories else "P2.3"
    test_names = ["api_contract", "query_vectors"]
    if categories:
        test_names.append("category_vectors")
    if annotation:
        test_names.append("annotation_vectors")
    if context:
        test_names.append("annotation_context_vectors")
    if args.annotation_frequency:
        test_names.append("annotation_frequency_vectors")
    before = require_baseline()["fingerprints"]
    local = ROOT / ".local"
    local.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix=f"queries-{phase.lower().replace('.', '_')}-", dir=local)).resolve()
    require(directory.is_relative_to(local.resolve()), "Copy escaped workspace")
    checkout, runtime = directory / "checkout", directory / "runtime"
    checkout.mkdir()
    runtime.mkdir()
    names = ["Cargo.toml", "Cargo.lock", "README.md", "LICENSE", "SOURCES.md",
             "data/lexicon.bin", "data/frequency.bin", "third_party/unicode/LICENSE.txt"]
    names += [f"tests/{name}.rs" for name in test_names]
    names += [path.relative_to(ROOT).as_posix() for path in sorted((ROOT / "src").rglob("*.rs"))]
    identities = {}
    for name in names:
        source, destination = ROOT / name, checkout / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        identities[name] = file_record(source)
        require(file_record(destination) == identities[name], f"Copy differs: {name}")
    environment = os.environ.copy()
    environment["CARGO_HOME"] = str(local / "cargo-home")
    environment["CARGO_TARGET_DIR"] = str(local / "query-target")
    arguments = ["cargo", "test", "--offline", "--locked", "--release", "--all-features",
                 "--lib", "--tests", "--no-run", "--message-format=json"]
    built = run(arguments, checkout, environment)
    artifacts = [json.loads(line) for line in built.stdout.splitlines() if line.startswith("{")]
    binaries = {item["target"]["name"]: Path(item["executable"]) for item in artifacts
                if item.get("reason") == "compiler-artifact" and item.get("executable")
                and item.get("profile", {}).get("test")}
    require(set(binaries) == {"lingose", *test_names}, "Unexpected test artifacts")
    # Copy all binaries before running, so the runtime directory has no resources.
    for binary in binaries.values():
        shutil.copyfile(binary, runtime / binary.name)
    outputs = {}
    for name, binary in sorted(binaries.items()):
        result = run([str(runtime / binary.name)], runtime, environment)
        require("test result: ok." in result.stdout, f"Tests did not run: {name}")
        outputs[name] = result.stdout.strip()
    require(set(runtime.iterdir()) == {runtime / binary.name for binary in binaries.values()},
            "Runtime acquired inputs other than the copied test binaries")
    for name, identity in identities.items():
        require(file_record(ROOT / name) == file_record(checkout / name) == identity,
                f"Input changed: {name}")
    require(fingerprints() == before, "Installed reference changed")
    scope = ("Inclusive original-NUMBER frequency filtering with threshold clamping, stored inflections, shared special-literal index, pinned Python IGNORECASE/lower membership and nonoverlap consumption, Unicode boundaries, protected-span rescanning/context, resource failures and concurrency; includes P3.1/P3.2 and P2 regressions. " if args.annotation_frequency else
             "Zero-threshold IPS annotation including the context, explicit contractions, hyphen/apostrophe fallback and s/es/ed/ing candidate projection/ambiguity/blocking, against pinned Python full outputs and independent wire fixtures; includes P3.1 Unicode/scanner/casing and P2 regressions. Positive frequency filtering (P3.3) remains incomplete. " if args.annotation_context else
             "Basic direct IPS annotation: pinned Python scanner/cluster/casing vectors, full Unicode scalar scanner/NFD-predicate/casing digest, 15 full direct/no-token public outputs, independent state/error/ownership/concurrency fixtures and P2 regressions. Context/morphology (P3.2) and positive frequency filtering (P3.3) remain incomplete. " if args.annotation else
             "All 24 complete ordered category lists against P0 Python digests, all 50,335 exact keys across 24 public membership labels, category validation/resource/empty/order/ownership/concurrency fixtures, plus P2.3 regressions. " if args.categories else
             "Simple-query P0 samples, isolated unavailable/exact/fallback/error fixtures, Unicode 15.0 scalar parity, ownership/concurrency and remaining phase boundaries. ")
    evidence = {
        "phase": phase, "platform": platform.platform(),
        "scope": scope + "Not final P4 full-query/annotation/performance acceptance, minimum-version testing, packaged-crate checks or publication.",
        "rustc": run(["rustc", "-Vv"], ROOT, environment).stdout.strip(),
        "cargo": run(["cargo", "-V"], ROOT, environment).stdout.strip(),
        "build_arguments": arguments, "copy_directory": str(directory),
        "inputs": identities, "installed_reference_unchanged": True,
        "runtime_inputs": [binary.name for binary in binaries.values()],
        "outputs": outputs,
        "p0_fixture": file_record(ROOT / "tests/fixtures/python-api-v1.json"),
        "p0_simple_query_assertions": 112,
        "unicode": json.loads((ROOT / "docs/query-case.json").read_text(encoding="utf-8")),
    }
    if categories:
        evidence["category_coverage"] = {
            "labels": 24, "distinct_ordered_members": 209759,
            "complete_list_checks": 25, "default_label": "CET4",
            "exact_membership_checks": 50335 * 24,
        }
    if annotation:
        from generate_annotation_vectors import generate
        generated, coverage = generate()
        for path, expected in generated.items():
            require(path.read_bytes() == expected, f"Generated annotation vectors drifted: {path}")
        evidence["annotation_coverage"] = coverage
        evidence["annotation_unicode"] = json.loads((ROOT / "docs/annotation-unicode.json").read_text(encoding="utf-8"))
        evidence["annotation_generators"] = {name: file_record(ROOT / "tools" / name) for name in (
            "generate_annotation_unicode.py", "generate_annotation_vectors.py")}
    if context:
        from generate_annotation_context_vectors import generate
        generated, coverage = generate()
        for path, expected in generated.items():
            require(path.read_bytes() == expected, f"Generated context vectors drifted: {path}")
        evidence["annotation_context_coverage"] = coverage
        evidence["annotation_generators"]["generate_annotation_context_vectors.py"] = file_record(ROOT / "tools/generate_annotation_context_vectors.py")
    if args.annotation_frequency:
        from generate_annotation_frequency_vectors import generate
        generated, coverage = generate()
        for path, expected in generated.items():
            require(path.read_bytes() == expected, f"Generated frequency vectors drifted: {path}")
        evidence["annotation_frequency_coverage"] = coverage
        evidence["annotation_generators"]["generate_annotation_frequency_vectors.py"] = file_record(ROOT / "tools/generate_annotation_frequency_vectors.py")
    report = "annotation-frequency-verification.json" if args.annotation_frequency else "annotation-context-verification.json" if args.annotation_context else "annotation-verification.json" if args.annotation else "category-verification.json" if args.categories else "query-verification.json"
    (ROOT / "docs" / report).write_text(json_text(evidence), encoding="utf-8", newline="\n")
    print(f"{phase} isolated offline release checks passed; reference and copied inputs unchanged")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
