"""Verify P2.3 in an isolated offline source copy and data-free runtime directory.

Not a packaged-crate check or a P4 full-data/performance acceptance run.
"""

from __future__ import annotations

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
    before = require_baseline()["fingerprints"]
    local = ROOT / ".local"
    local.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="queries-p2_3-", dir=local)).resolve()
    require(directory.is_relative_to(local.resolve()), "Copy escaped workspace")
    checkout, runtime = directory / "checkout", directory / "runtime"
    checkout.mkdir()
    runtime.mkdir()
    names = ["Cargo.toml", "Cargo.lock", "README.md", "LICENSE", "SOURCES.md",
             "data/lexicon.bin", "data/frequency.bin", "third_party/unicode/LICENSE.txt",
             "tests/api_contract.rs", "tests/query_vectors.rs"]
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
    require(set(binaries) == {"lingose", "api_contract", "query_vectors"}, "Unexpected test artifacts")
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
    evidence = {
        "phase": "P2.3", "platform": platform.platform(),
        "scope": "Simple-query P0 samples, isolated unavailable/exact/fallback/error fixtures, Unicode 15.0 scalar parity, ownership/concurrency and remaining phase boundaries. Not P4 exhaustive public-query or performance acceptance, minimum-version testing, packaged-crate checks or publication.",
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
    (ROOT / "docs/query-verification.json").write_text(json_text(evidence), encoding="utf-8", newline="\n")
    print("P2.3 isolated offline release checks passed; reference and copied inputs unchanged")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
