"""P4.2 public API release measurements against the unchanged P1.2 budgets.

All timing/memory samples survive failed acceptance in a new .local directory.
No package, publication, MSRV or other-platform acceptance is performed here.
"""

from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (ROOT, connect, file_record, fingerprints, installed, json_text,
                       main_error, no_restore, require, require_baseline)
from run_layout_probe import machine, memory, summarize

BUDGET = ROOT / "docs/performance-budget.json"
CORRECTNESS = ROOT / "docs/full-differential-verification.json"
PROBE = "tools/performance-probe"
MIXED = ("apple", "Apple", "APPLE", "May", "may", "US", "us", "iPhone", "IPHONE",
         "unknownwordzz", "UNKNOWNWORDZZ", "café", "CAFÉ", "Straße", "STRASSE", "İ",
         "ı", "ſ", "K", "Σ", "中文", "e\u0301", "don't", "well-known", "running",
         "NAÏVE", "𝕒𝕡𝕡𝕝𝕖", "𐐀", "the", "The", "THE", "a")
QUERIES = ("ipa", "ips", "ism", "ipsm", "root_lemma", "meaning", "meaning_en", "meaning_zh", "kind")


def run(arguments, directory, environment, log=None):
    started = time.perf_counter()
    with subprocess.Popen(arguments, cwd=directory, env=environment, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, encoding="utf-8") as process:
        created = time.perf_counter()
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=180)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            stdout, stderr = process.communicate()
        ended = time.perf_counter()
        record = {"arguments": arguments, "stdout": stdout, "stderr": stderr,
                  "exit_code": process.returncode, "timed_out": timed_out,
                  "wall_ms": (ended - started) * 1000, "process_creation_ms": (created - started) * 1000}
        if log:
            log.write_text(json_text(record), encoding="utf-8", newline="\n")
        require(not timed_out, f"Command timed out: {arguments}; log={log}")
        result = subprocess.CompletedProcess(arguments, process.returncode, stdout, stderr)
        result.wall_ms, result.process_creation_ms = record["wall_ms"], record["process_creation_ms"]
    require(result.returncode == 0,
            f"Command failed ({result.returncode}): {arguments}\n{result.stdout}\n{result.stderr}")
    return result


def metrics(output):
    result = {}
    for line in output.splitlines():
        if line.startswith("METRIC\t"):
            _, name, elapsed, operations = line.split("\t")
            require(name not in result and int(operations) > 0 and int(elapsed) >= 0,
                    "Duplicate or invalid metric")
            divisor = 1_000 if name.endswith("_us") else 1_000_000 if name.endswith("_ms") else 1
            result[name] = int(elapsed) / int(operations) / divisor
    return result


def invoke(executable, mode, runtime, environment, logs, index):
    arguments = [str(executable), mode, "."]
    result = run(arguments, runtime, environment, logs / f"{mode}-{index}.json")
    return {"metrics": metrics(result.stdout), "wall_ms": result.wall_ms,
            "process_creation_ms": result.process_creation_ms,
            "verified_annotations": [line for line in result.stdout.splitlines() if line.startswith("VERIFIED\t")]}


def memory_sample(executable, mode, skip, runtime, environment, logs, index):
    arguments = [str(executable), mode, ".", str(skip)]
    with subprocess.Popen(arguments, cwd=runtime, env=environment, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8") as process:
        lines, before, after, stderr, finished = [], None, None, "", False
        timed_out = threading.Event()
        def expire():
            timed_out.set()
            process.kill()
        watchdog = threading.Timer(180, expire)
        watchdog.start()
        try:
            line = process.stdout.readline()
            lines.append(line)
            require(line.strip() == "HOLD\tbefore-load", "Pre-load memory handshake failed")
            before = memory(process.pid)
            process.stdin.write("\n")
            process.stdin.flush()
            stage = "both-resources-loaded" if mode == "loaded-memory" else "annotation-output-retained"
            while True:
                line = process.stdout.readline()
                require(line, "Child ended before final memory handshake")
                lines.append(line)
                if line.strip() == f"HOLD\t{stage}":
                    break
            after = memory(process.pid)
            stdout, stderr = process.communicate("\n", timeout=60)
            finished = True
            lines.append(stdout)
            output = "".join(lines)
            require(process.returncode == 0, f"Memory probe failed: {stderr}")
            if mode == "annotation-memory":
                require(f"VERIFIED\t100000\t{skip}\t" in output, "Memory annotation was not compared completely")
            return {"before": before, "after": after,
                    "delta": {key: after[key] - before[key] for key in after},
                    "metrics": metrics(output), "complete_output_verified": mode == "annotation-memory"}
        finally:
            watchdog.cancel()
            if process.poll() is None:
                process.kill()
            if not finished:
                stdout, stderr = process.communicate()
                lines.append(stdout)
            (logs / f"{mode}-{skip}-{index}.json").write_text(json_text({
                "stdout": "".join(lines), "stderr": stderr, "exit_code": process.returncode,
                "timed_out": timed_out.is_set(), "before": before, "after": after}), encoding="utf-8", newline="\n")


def expected_metrics(labels):
    names = {f"{api}_{group}" for api in QUERIES for group in ("exact", "mixed")}
    names |= {f"kind_{label}_{group}" for label in labels for group in ("exact", "mixed")}
    names |= {"labels_us", "all_kind_lists_ms", "default_kind_list_ms"}
    names |= {f"annotation_{words}_{skip}_ms" for words in (10000, 100000) for skip in (0, 1000, 5062)}
    return names


def acceptance(report, budget):
    """Fail closed for missing samples/metrics; never average memory peaks."""
    limits = budget["limits"]
    samples, labels = report["samples"], report["labels"]
    failures, statistics = [], {}

    def check(name, values, limit):
        if len(values) < 7:
            failures.append(f"{name}: fewer than 7 samples")
            return
        summary = summarize(values)
        statistics[name] = summary
        if summary["median"] > limit["median"] or summary["p95_nearest_rank"] > limit["p95"]:
            failures.append(f"{name}: median/p95 {summary['median']:.4f}/{summary['p95_nearest_rank']:.4f} > {limit}")

    check("cold_process_first_public_query_ms", [x["wall_ms"] for x in samples["cold"]],
          limits["cold_process_first_public_query_ms"])
    for mode, name, limit in (("cold", "lexicon_initialization_ms", "lexicon_initialization_including_index_ms"),
                              ("frequency", "frequency_initialization_ms", "frequency_initialization_ms")):
        require(all(set(x["metrics"]) == {name} for x in samples[mode]), "Missing initialization metric")
        check(name, [x["metrics"][name] for x in samples[mode]], limits[limit])
    expected = expected_metrics(labels)
    verified = {f"VERIFIED\t{words}\t{skip}\t{report['corpus_and_query_inputs'][f'reference-{words}-skip-{skip}.txt']['bytes']}"
                for words in (10000, 100000) for skip in (0, 1000, 5062)}
    require(all(set(x["metrics"]) == expected and len(x["verified_annotations"]) == 6
                and set(x["verified_annotations"]) == verified for x in samples["warm"]),
            "Incomplete warm workload or output verification")
    for name in sorted(expected):
        if name == "default_kind_list_ms":
            # Supplementary metric: budget constrains all 24 lists as one round.
            statistics[name] = summarize([x["metrics"][name] for x in samples["warm"]])
            continue
        if name.startswith("annotation_"):
            limit = f"annotate_ips_{name.split('_')[1]}_words_ms_each_skip_0_1000_5062"
        elif name == "labels_us":
            limit = "labels_complete_owned_us"
        elif name == "all_kind_lists_ms":
            limit = "all_24_kind_lists_complete_owned_ms"
        else:
            limit = "hot_query_batch_ns_per_operation"
        check(name, [x["metrics"][name] for x in samples["warm"]], limits[limit])
    memory_limits = {
        "loaded": {"WorkingSetSize": "loaded_process_working_set_bytes", "PrivateUsage": "loaded_process_private_commit_bytes",
                   "PeakPagefileUsage": "loaded_process_peak_private_commit_bytes"},
        "annotation": {"PeakWorkingSetSize": "annotation_100000_peak_working_set_bytes",
                       "PeakPagefileUsage": "annotation_100000_peak_private_commit_bytes"}}
    for group in ("loaded", "annotation_0", "annotation_1000", "annotation_5062"):
        values = report["memory_samples"][group]
        if len(values) < 3:
            failures.append(f"{group}: fewer than 3 memory samples")
        for index, sample in enumerate(values):
            if group != "loaded":
                require(sample["complete_output_verified"] is True, "Memory annotation output not verified")
                require(set(sample["metrics"]) == {f"annotation_100000_{group.split('_')[1]}_ms"},
                        "Memory annotation metric missing")
            for counter, limit in memory_limits["loaded" if group == "loaded" else "annotation"].items():
                if sample["after"][counter] > limits[limit]:
                    failures.append(f"{group}[{index}] {counter}: {sample['after'][counter]} > {limits[limit]}")
    if report["raw_runtime_resources_bytes"] > limits["raw_runtime_resources_bytes"]:
        failures.append("raw runtime resource size exceeds budget")
    if len(samples["concurrent"]) < 7:
        failures.append("fewer than 7 concurrent correctness samples")
    require(all(set(sample["metrics"]) == {"concurrent_8_complete_annotations_ms"}
                for sample in samples["concurrent"]), "Concurrent public workload missing")
    return {"passed": not failures, "failures": failures, "statistics": statistics,
            "deferred_to_P5_3": ["packaged_crate_bytes"],
            "initialization_note": "Public ips(apple) and first positive annotation include tiny public-call overhead; conservative upper bounds on loader initialization."}


def string_array(output, values):
    output.write(struct.pack("<I", len(values)))
    for value in values:
        encoded = value.encode("utf-8")
        output.write(struct.pack("<I", len(encoded)) + encoded)


def investigate_startup(executable, directory, environment, logs):
    """Separate per-file first execution from library work using identical bytes."""
    diagnostic = directory / "startup-diagnostics"
    diagnostic.mkdir()
    samples = []
    for index, first_mode in enumerate(("control", "cold", "control", "cold")):
        copied = diagnostic / f"copy-{index}.exe"
        shutil.copyfile(executable, copied)
        require(file_record(copied) == file_record(executable), "Startup diagnostic binary differs")
        for repeat, mode in enumerate((first_mode, "control", "cold")):
            sample = invoke(copied, mode, diagnostic, environment, logs, f"diagnostic-{index}-{repeat}")
            samples.append({"copy": copied.name, "mode": mode, "first_execution": repeat == 0, **sample})
    return {"executable": file_record(executable), "samples": samples,
            "measurement_boundary": "Compare identical executable bytes at four new paths, control/query first execution then same-file reuse. process_creation_ms measures parent time until Python Popen returns; it does not trace an individual Windows call or identify an OS component."}


def prepare(directory):
    baseline = require_baseline()
    correctness = json.loads(CORRECTNESS.read_bytes())
    require(not correctness["smoke_only"] and correctness["differences"] == 0
            and correctness["full_exact_keys"] == 50335, "Complete P4.1 prerequisite missing")
    # Every recorded correctness input must still match, not just the exported data.
    for name, identity in correctness["inputs"].items():
        require(file_record(ROOT / name) == identity, f"P4.1 correctness identity drift: {name}")
    budget = json.loads(BUDGET.read_bytes())
    capture = ROOT / correctness["capture_directory"] / "capture"
    checkout, runtime, logs = (directory / name for name in ("checkout", "runtime", "logs"))
    for path in (checkout, runtime, logs):
        path.mkdir()
    names = ["Cargo.toml", "Cargo.lock", "README.md", "LICENSE", "SOURCES.md", "data/lexicon.bin", "data/frequency.bin",
             f"{PROBE}/Cargo.toml", f"{PROBE}/Cargo.lock", f"{PROBE}/src/main.rs"]
    names += [path.relative_to(ROOT).as_posix() for path in sorted((ROOT / "src").rglob("*.rs"))]
    identities = {}
    for name in names:
        original, copied = ROOT / name, checkout / name
        identities[name] = file_record(original)
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, copied)
        require(file_record(copied) == identities[name], f"Build copy differs: {name}")
    identities.update({name: file_record(ROOT / name) for name in (
        "tools/check_performance.py", "tests/test_performance.py", "tools/run_layout_probe.py", "tools/reference.py",
        "docs/performance-budget.json", "docs/full-differential-verification.json",
        "docs/correctness-regression-verification.json")})
    corpus_inputs = {}
    for words in (10000, 100000):
        name = f"corpus-{words}.txt"
        require(file_record(capture / name) == budget["corpora"][str(words)] == correctness["artifacts"][name],
                f"Corpus identity differs: {words}")
        for item in [name] + [f"reference-{words}-skip-{skip}.txt" for skip in (0, 1000, 5062)]:
            identity = file_record(capture / item)
            require(identity == correctness["artifacts"][item], f"P4.1 full output identity differs: {item}")
            shutil.copyfile(capture / item, runtime / item)
            require(file_record(runtime / item) == identity, f"Copied workload differs: {item}")
            corpus_inputs[item] = identity
    _, _, database, _ = installed()
    with no_restore(), closing(connect(database)) as db:
        words = [row[0] for row in db.execute("SELECT word FROM entry ORDER BY word COLLATE BINARY")]
    import lingose
    with no_restore():
        labels = lingose.labels()
    require(len(words) == 50335 and labels == correctness["labels"], "Query workload differs")
    with (runtime / "queries.bin").open("xb") as output:
        for values in (words, MIXED, labels):
            string_array(output, values)
    corpus_inputs["queries.bin"] = file_record(runtime / "queries.bin")
    return baseline, budget, identities, corpus_inputs, labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="One sample; cannot pass acceptance")
    args = parser.parse_args()
    require(os.name == "nt", "This runner records Windows process memory; no other-platform claim")
    local = ROOT / ".local"
    directory = Path(tempfile.mkdtemp(prefix="p42-smoke-" if args.smoke else "p42-performance-", dir=local)).resolve()
    baseline, budget, identities, corpus_inputs, labels = prepare(directory)
    checkout, runtime, logs = (directory / name for name in ("checkout", "runtime", "logs"))
    environment = os.environ.copy()
    environment["CARGO_HOME"] = str(local / "cargo-home")
    environment["CARGO_TARGET_DIR"] = str(local / "performance-target")
    command = ["cargo", "build", "--manifest-path", f"{PROBE}/Cargo.toml", "--release", "--offline", "--locked"]
    print(f"Building isolated public API probe: {directory.relative_to(ROOT)}", flush=True)
    run(command, checkout, environment, logs / "build.json")
    executable = runtime / "lingose-performance-probe.exe"
    shutil.copyfile(local / "performance-target/release" / executable.name, executable)
    report = {"phase": "P4.2", "measured_on": datetime.now().astimezone().isoformat(), "smoke_only": args.smoke,
              "environment": machine(), "budget": file_record(BUDGET), "inputs": identities,
              "corpus_and_query_inputs": corpus_inputs, "labels": labels,
              "build_arguments": command, "release_profile": {"lto": "thin", "codegen_units": 1, "strip": True},
              "directory": directory.relative_to(ROOT).as_posix(), "executable": file_record(executable),
              "raw_runtime_resources_bytes": sum((ROOT / f"data/{name}.bin").stat().st_size for name in ("lexicon", "frequency")),
              "samples": {mode: [] for mode in ("cold", "control", "frequency", "warm", "concurrent", "long-word")},
              "memory_samples": {group: [] for group in ("loaded", "annotation_0", "annotation_1000", "annotation_5062")},
              "scope": "Real public APIs, full annotation equality and Windows runtime budgets; excludes packaged .crate, MSRV, other platforms and publication.",
              "method": {"statistics": "min/median/max and nearest-rank p95, no outlier removal; 7 samples p95=max",
                         "cold": "Single ips(apple), 7 fresh processes after the P1.2-prescribed uncounted full warm-up; no OS cache flush or affinity. Newly copied file's first-ever execution is separately retained before warm-up, including its slower process creation. Control uses identical executable without library calls.",
                         "warm": "One uncounted complete warm-up, then 7 new processes; initialize both resources outside hot timing; full owned outputs allocated and destroyed; exact keys twice, mixed 32 words 2000 times, every registered label.",
                         "annotation": "Both full fixed corpora at all three thresholds; Instant wraps the public call only; complete UTF-8 equality outside timing on every call, no truncation.",
                         "memory": "3 fresh paused processes per loaded/annotation threshold; GetProcessMemoryInfo absolute and delta working set/private commit and peaks. Annotation process loads full input and retains full output; Python expected buffer is loaded only AFTER memory snapshot.",
                         "concurrent": "8 barrier-synchronized first callers in each fresh process; complete 100k output comparison at thresholds 0/1000/5062 plus public queries; 7 samples; no numeric throughput budget."}}
    def save():
        (directory / "report.json").write_text(json_text(report), encoding="utf-8", newline="\n")
    save()
    try:
        repeats = 1 if args.smoke else 7
        # Retain first EXECUTION before any warm-up; hashing has already read the file.
        report["artifact_first_execution"] = invoke(executable, "cold", runtime, environment, logs, "artifact-first")
        save()
        report["startup_investigation"] = investigate_startup(executable, directory, environment, logs)
        report["warmup"] = invoke(executable, "warm", runtime, environment, logs, "warmup")
        for index in range(repeats):
            for mode in ("cold", "control", "frequency"):
                report["samples"][mode].append(invoke(executable, mode, runtime, environment, logs, index))
            save()
        for index in range(repeats):
            report["samples"]["warm"].append(invoke(executable, "warm", runtime, environment, logs, index))
            report["samples"]["concurrent"].append(invoke(executable, "concurrent", runtime, environment, logs, index))
            save()
            print(f"Complete warm/concurrent sample {index + 1}/{repeats}", flush=True)
        report["samples"]["long-word"].append(invoke(executable, "long-word", runtime, environment, logs, 0))
        for index in range(1 if args.smoke else 3):
            report["memory_samples"]["loaded"].append(memory_sample(executable, "loaded-memory", 0, runtime, environment, logs, index))
            for skip in (0, 1000, 5062):
                report["memory_samples"][f"annotation_{skip}"].append(memory_sample(executable, "annotation-memory", skip, runtime, environment, logs, index))
            save()
        for name, identity in identities.items():
            require(file_record(ROOT / name) == identity, f"Measurement input changed: {name}")
            if (checkout / name).exists():
                require(file_record(checkout / name) == identity, f"Build copy changed: {name}")
        for name, identity in corpus_inputs.items():
            require(file_record(runtime / name) == identity, f"Runtime input changed: {name}")
        require(file_record(executable) == report["executable"], "Executable changed")
        require(fingerprints() == baseline["fingerprints"], "Installed source/reference changed")
        require({path.name for path in runtime.iterdir()} == set(corpus_inputs) | {executable.name}, "Unexpected runtime file")
        report["inputs_and_reference_unchanged"] = True
        report["acceptance"] = acceptance(report, budget)
        report["artifact_first_execution"]["exceeds_cold_p95_limit"] = (
            report["artifact_first_execution"]["wall_ms"] > budget["limits"]["cold_process_first_public_query_ms"]["p95"])
        report["status"] = "passed_under_fixed_warmup_conditions" if report["acceptance"]["passed"] else "budget_failed_or_smoke_only"
        print(json_text({"directory": report["directory"], "passed": report["acceptance"]["passed"],
                         "failures": report["acceptance"]["failures"]}))
    except Exception as error:
        report["status"] = "failed"
        report["error"] = str(error)
        raise
    finally:
        save()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
