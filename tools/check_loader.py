"""P2.2 loader-only release checks in a minimal offline copy and fresh processes.

This is not public API, annotation, crate-package, or P4 performance acceptance.
The copied test binary runs from a directory containing no data or source files.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import ROOT, workspace_inputs, evidence_output, file_record, json_text, main_error, require

PROBE = "data::cache_tests::cold_process_loader_probe"


def run(arguments, directory, environment):
    result = subprocess.run(arguments, cwd=directory, env=environment, capture_output=True,
                            text=True, encoding="utf-8", errors="strict")
    require(result.returncode == 0,
            f"Command failed ({result.returncode}): {arguments}\n{result.stdout}\n{result.stderr}")
    return result


def summarize(values):
    ordered = sorted(values)
    return {"median": statistics.median(values), "p95": ordered[math.ceil(len(values) * .95) - 1]}


def measure(repeats):
    local = ROOT / ".local"
    local.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="loader-p2_2-", dir=local)).resolve()
    require(directory.is_relative_to(local.resolve()), "Isolated copy escaped the workspace")
    checkout, runtime = directory / "checkout", directory / "runtime"
    checkout.mkdir()
    runtime.mkdir()
    names = workspace_inputs()
    identities = {}
    for name in names:
        original, copied = ROOT / name, checkout / name
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, copied)
        identities[name] = file_record(original)
        require(file_record(copied) == identities[name], f"Copied input differs: {name}")
    environment = os.environ.copy()
    environment["CARGO_HOME"] = str(local / "cargo-home")
    environment["CARGO_TARGET_DIR"] = str(local / "loader-target")
    command = ["cargo", "test", "--offline", "--locked", "--release", "-p", "lingose", "--lib",
               "--no-run", "--message-format=json"]
    built = run(command, checkout, environment)
    artifacts = [json.loads(line) for line in built.stdout.splitlines() if line.startswith("{")]
    binaries = [Path(item["executable"]) for item in artifacts
                if item.get("reason") == "compiler-artifact" and item.get("executable")
                and item.get("profile", {}).get("test") and item.get("target", {}).get("name") == "lingose"]
    require(len(binaries) == 1, "Expected exactly one library test executable")
    executable = runtime / binaries[0].name
    shutil.copyfile(binaries[0], executable)
    # Execute the copied binary directly; Cargo/source/data are not runtime inputs.
    require(list(runtime.iterdir()) == [executable], "Runtime directory must contain only the executable")
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        result = run([str(executable), "--ignored", "--exact", PROBE, "--nocapture", "--test-threads=1"], runtime, environment)
        elapsed_ms = (time.perf_counter() - started) * 1000
        lines = [line.partition("LOADER_PROBE ")[2] for line in result.stdout.splitlines()
                 if "LOADER_PROBE " in line]
        require(len(lines) == 1 and "1 passed; 0 failed" in result.stdout, "Release probe did not complete")
        sample = json.loads(lines[0])
        require(sample["lexicon_initializations"] == sample["frequency_initializations"] == 1,
                "Probe rebuilt a resource")
        sample["cold_process_wall_ms"] = elapsed_ms
        samples.append(sample)
    for name, identity in identities.items():
        require(file_record(ROOT / name) == file_record(checkout / name) == identity,
                f"Input changed during loader checks: {name}")
    metadata = json.loads(run(["cargo", "metadata", "--offline", "--locked", "--format-version=1"],
                              checkout, environment).stdout)
    dependencies = [{"name": item["name"], "version": item["version"], "license": item["license"],
                     "declared_rust_version": item["rust_version"]}
                    for item in metadata["packages"] if item["name"] not in ("lingose", "lingose-cli")]
    metrics = ("lexicon_load_and_index_ms", "frequency_load_ms", "warm_cached_exact_lookup_ns", "cold_process_wall_ms")
    return {
        "stage": "P2.2", "verified_on": datetime.now().astimezone().date().isoformat(),
        "scope": "Private loader and exact-key index only; excludes public query semantics/output allocation, annotation, memory budgets, packaged crate and final P4 acceptance",
        "environment": {"platform": platform.platform(), "machine": platform.machine(),
                        "processor": platform.processor(),
                        "rustc": run(["rustc", "--version"], ROOT, environment).stdout.strip(),
                        "cargo": run(["cargo", "--version"], ROOT, environment).stdout.strip()},
        "build": {"command": command, "profile": "release", "offline": True,
                  "minimal_copy": directory.relative_to(ROOT).as_posix() + "/checkout",
                  "copied_source_and_resources": identities, "inputs_unchanged": True},
        "runtime": {"directory": runtime.relative_to(ROOT).as_posix(),
                    "only_test_executable_present": True, "executable_identity": file_record(executable),
                    "source_or_data_files_opened_by_loader": False},
        "method": {"repeats": repeats, "warm_iterations_per_sample": 100000,
                   "statistics": "median and nearest-rank p95 of independent fresh processes",
                   "cold_note": "Fresh process, not cleared OS file cache. Internal times exclude test harness startup; wall time includes process startup/test harness/exit.",
                   "warm_note": "OnceLock access plus exact HashMap lookup only; no public argument/case checks or owned output. Test-only initialization counters enabled."},
        "samples": samples, "statistics": {key: summarize([sample[key] for sample in samples]) for key in metrics},
        "dependencies": sorted(dependencies, key=lambda item: item["name"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write a new loader evidence file")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/loader-verification-0.2.0.json")
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args()
    require(args.repeats >= 1, "At least one fresh process is required")
    destination = evidence_output(args.output) if args.write else None
    report = measure(args.repeats)
    if args.write:
        destination.write_text(json_text(report), encoding="utf-8", newline="\n")
    print(json_text({key: report[key] for key in ("stage", "statistics", "method")}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
