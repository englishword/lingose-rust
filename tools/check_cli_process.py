"""CLI4.1: complete release CLI processes and I/O, separate from library budgets.

Requires current full differential and isolated regression receipts. Every output is
compared in full, outside the measured process interval. No CLI latency budget is
invented; first execution, warmups and all seven samples remain in a new directory.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (ROOT, evidence_output, file_record, fingerprints, installed,
                       json_text, main_error, no_restore, require, require_baseline,
                       workspace_inputs)
from check_performance import validated_regressions
from run_layout_probe import machine, summarize


def bytes_record(value):
    import hashlib
    return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}


def check_output(value, expected, json_output):
    if json_output:
        actual = json.loads(value)
        require(type(actual) is dict and actual.keys() == expected.keys(), "JSON keys differ")
        require(all(type(actual[key]) is type(expected[key]) for key in expected), "JSON types differ")
        require(actual == expected, "Complete JSON value differs")
    else:
        require(value == expected, "Complete plain output differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--correctness", type=Path, default=ROOT / "docs/full-differential-verification-0.2.0.json")
    parser.add_argument("--regressions", type=Path, default=ROOT / "docs/correctness-regression-verification-0.2.0.json")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/cli-process-verification-0.2.0.json")
    args = parser.parse_args()
    require(os.name == "nt", "Machine evidence currently supports Windows only")
    destination = evidence_output(args.output)
    baseline = require_baseline()
    validated_regressions(args.regressions.resolve())
    correctness = json.loads(args.correctness.read_bytes())
    require(correctness["smoke_only"] is False and correctness["differences"] == 0
            and correctness["full_exact_keys"] == 50335, "Full current differential required")
    for name, identity in correctness["inputs"].items():
        require(file_record(ROOT / name) == identity, f"Differential identity drift: {name}")
    directory = Path(tempfile.mkdtemp(prefix="cli41-process-", dir=ROOT / ".local")).resolve()
    checkout, runtime, logs = [directory / name for name in ("checkout", "runtime", "logs")]
    for path in (checkout, runtime, logs):
        path.mkdir()
    inputs = {}
    copied_names = workspace_inputs()
    for name in copied_names:
        original, copied = ROOT / name, checkout / name
        inputs[name] = file_record(original)
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, copied)
        require(file_record(copied) == inputs[name], f"Copy differs: {name}")
    for name in ("tools/check_cli_process.py", "crates/lingose-cli/tests/word.rs", "crates/lingose-cli/tests/annotate.rs",
                 "docs/performance-budget.json", "tools/check_performance.py", "tools/run_layout_probe.py", "tools/reference.py"):
        inputs[name] = file_record(ROOT / name)
    for path in (args.correctness.resolve(), args.regressions.resolve()):
        inputs[path.relative_to(ROOT).as_posix()] = file_record(path)
    capture = ROOT / correctness["capture_directory"] / "capture"
    budget = json.loads((ROOT / "docs/performance-budget.json").read_bytes())
    texts, references = {}, {}
    for words in (10000, 100000):
        name = f"corpus-{words}.txt"
        require(file_record(capture / name) == budget["corpora"][str(words)] == correctness["artifacts"][name], "Corpus drift")
        texts[words] = (capture / name).read_bytes()
        shutil.copyfile(capture / name, runtime / name)
        for skip in (0, 1000, 5062):
            name = f"reference-{words}-skip-{skip}.txt"
            require(file_record(capture / name) == correctness["artifacts"][name], "Reference drift")
            references[words, skip] = (capture / name).read_bytes()
    installed()
    import lingose
    with no_restore():
        word = {"word": "hello", "ipa": lingose.IPA("hello"), "ips": lingose.IPS("hello"),
                "ism": lingose.ISM("hello"), "ipsm": lingose.IPSM("hello"), "root_lemma": lingose.root_lemma("hello")}
    plain_word = "".join(f"{key}: {json.dumps(value, ensure_ascii=False, separators=(',', ':'))}\n" for key, value in word.items()).encode("utf-8")
    environment = dict(os.environ, CARGO_HOME=str(ROOT / ".local/cargo-home"),
                       CARGO_TARGET_DIR=str(ROOT / ".local/cli41-cli-target"))
    command = ["cargo", "build", "--release", "-p", "lingose-cli", "--offline", "--locked"]
    build_timed_out = False
    try:
        build = subprocess.run(command, cwd=checkout, env=environment, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired as error:
        build_timed_out = True
        build = subprocess.CompletedProcess(command, None, error.stdout or b"", error.stderr or b"")
    (logs / "build.stdout.bin").write_bytes(build.stdout)
    (logs / "build.stderr.bin").write_bytes(build.stderr)
    build_record = {"argv": command, "exit_code": build.returncode, "timed_out": build_timed_out,
                    "stdout": build.stdout.decode("utf-8", errors="replace"),
                    "stderr": build.stderr.decode("utf-8", errors="replace")}
    (logs / "build.json").write_text(json_text(build_record), encoding="utf-8", newline="\n")
    if build_timed_out or build.returncode != 0:
        (directory / "report.json").write_text(json_text({"phase": "CLI4.1", "status": "failed",
            "stage": "build", "build": build_record}), encoding="utf-8", newline="\n")
        require(False, "CLI release build failed or timed out; see retained build logs and report")
    executable = runtime / "lingose.exe"
    shutil.copyfile(Path(environment["CARGO_TARGET_DIR"]) / "release/lingose.exe", executable)
    child_environment = {key: value for key, value in os.environ.items()
                         if key not in {"CARGO_HOME", "CARGO_TARGET_DIR", "RUSTUP_HOME", "PYTHONPATH", "PYTHONHOME"}}
    environment_info = machine()
    environment_info["timer"] = "Python time.perf_counter for complete CLI processes; no Rust internal timer"
    report = {"phase": "CLI4.1", "measured_on": datetime.now().astimezone().isoformat(),
              "directory": directory.relative_to(ROOT).as_posix(), "environment": environment_info,
              "build_arguments": command, "profile": "Cargo release; workspace has no profile overrides",
              "build_environment": {key: environment.get(key) for key in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS",
                  "CARGO_PROFILE_RELEASE_OPT_LEVEL", "CARGO_PROFILE_RELEASE_LTO", "CARGO_PROFILE_RELEASE_CODEGEN_UNITS", "CARGO_PROFILE_RELEASE_STRIP")},
              "executable": file_record(executable), "inputs": inputs, "scenarios": {},
              "method": {"repeats": 7, "warmup": "One complete invocation per scenario, excluded from statistics",
                         "clock": "perf_counter: before Popen through communicate/exit; includes process startup, parsing, library work and pipe/file I/O; excludes parent validation",
                         "statistics": "median and nearest-rank p95 of seven independent processes; p95 equals maximum; no samples discarded",
                         "latency_budget": None, "budget_note": "Library budgets are checked separately; no numeric CLI budget was specified.",
                         "file_mode": "Each scenario warmup creates its destination; measured repetitions overwrite it. No fsync or OS cache clearing.",
                         "runtime": "Copied binary plus explicit corpus and output files; no source or external lexicon. Cargo/Python-specific environment variables removed."},
              "corpora": {str(words): bytes_record(value) for words, value in texts.items()},
              "references": {f"{words}-{skip}": bytes_record(value) for (words, skip), value in references.items()},
              "status": "running"}

    def save():
        (directory / "report.json").write_text(json_text(report), encoding="utf-8", newline="\n")

    def invoke(label, index, argv, data, expected, json_output, output=None):
        started = time.perf_counter()
        with subprocess.Popen([str(executable), *argv], cwd=runtime, env=child_environment,
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            created = time.perf_counter()
            timed_out = False
            try:
                stdout, stderr = process.communicate(data, timeout=180)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.kill()
                stdout, stderr = process.communicate()
            ended = time.perf_counter()
        value = (runtime / output).read_bytes() if output and (runtime / output).is_file() else stdout
        record = {"argv": [str(executable), *argv], "exit_code": process.returncode, "timed_out": timed_out,
                  "wall_ms": (ended - started) * 1000, "process_creation_ms": (created - started) * 1000,
                  "stdin": bytes_record(data), "stdout": bytes_record(stdout), "stderr": bytes_record(stderr),
                  "result": bytes_record(value), "complete_output_verified": False}
        try:
            require(not timed_out and process.returncode == 0 and not stderr, "CLI process failed")
            if output:
                require(not stdout and (runtime / output).is_file(), "File output contract failed")
            check_output(value, expected, json_output)
            record["complete_output_verified"] = True
        except Exception:
            (logs / f"{label}-{index}.stdout.bin").write_bytes(stdout)
            (logs / f"{label}-{index}.stderr.bin").write_bytes(stderr)
            raise
        finally:
            (logs / f"{label}-{index}.json").write_text(json_text(record), encoding="utf-8", newline="\n")
        return record

    def scenario(label, argv, data, expected, json_output=False, output=None):
        entry = {"warmup": invoke(label, "warmup", argv, data, expected, json_output, output), "samples": []}
        report["scenarios"][label] = entry
        for index in range(7):
            entry["samples"].append(invoke(label, index, argv, data, expected, json_output, output))
            save()
        entry["wall_ms"] = summarize([row["wall_ms"] for row in entry["samples"]])
        entry["process_creation_ms"] = summarize([row["process_creation_ms"] for row in entry["samples"]])
        print(f"{label}: complete", flush=True)

    try:
        report["artifact_first_execution"] = invoke("artifact-first", 0, ["word", "hello", "--json"], b"", word, True)
        scenario("word-plain", ["word", "hello"], b"", plain_word)
        scenario("word-json", ["word", "hello", "--json"], b"", word, True)
        for words in (10000, 100000):
            for skip in (0, 1000, 5062):
                for json_output in (False, True):
                    expected = {"text": texts[words].decode("utf-8"), "annotate": references[words, skip].decode("utf-8")} if json_output else references[words, skip]
                    args_base = ["annotate", "--skip-top", str(skip)] + (["--json"] if json_output else [])
                    suffix = "json" if json_output else "plain"
                    scenario(f"stdin-stdout-{words}-{skip}-{suffix}", args_base, texts[words], expected, json_output)
                    output = f"out-{words}-{skip}-{suffix}.txt"
                    scenario(f"file-file-{words}-{skip}-{suffix}", args_base + ["--input", f"corpus-{words}.txt", "-o", output], b"", expected, json_output, output)
        for name, identity in inputs.items():
            require(file_record(ROOT / name) == identity, f"Input drift: {name}")
        for name in copied_names:
            require(file_record(checkout / name) == inputs[name], f"Copied input drift: {name}")
        for words in texts:
            require(file_record(runtime / f"corpus-{words}.txt") == bytes_record(texts[words]), "Runtime corpus changed")
        require(file_record(executable) == report["executable"], "CLI binary changed")
        require(fingerprints() == baseline["fingerprints"], "Installed oracle changed")
        require(len(report["scenarios"]) == 26, "Incomplete CLI scene coverage")
        require(all(len(scene["samples"]) == 7 and all(row["complete_output_verified"] for row in scene["samples"])
                    for scene in report["scenarios"].values()), "Incomplete CLI measurements")
        report["runtime_files"] = {path.name: file_record(path) for path in sorted(runtime.iterdir())}
        require(set(report["runtime_files"]) == {"lingose.exe", "corpus-10000.txt", "corpus-100000.txt"}
                | {f"out-{words}-{skip}-{suffix}.txt" for words in (10000, 100000) for skip in (0, 1000, 5062) for suffix in ("plain", "json")}, "Unexpected runtime files")
        report["inputs_and_reference_unchanged"] = True
        report["status"] = "passed_complete_outputs_and_sample_coverage"
        save()
        destination.write_text(json_text(report), encoding="utf-8", newline="\n")
        print(f"CLI process/I/O: 26 scenarios, 182 measured processes, all complete outputs matched; {directory.relative_to(ROOT)}", flush=True)
    except Exception as error:
        report["status"], report["error"] = "failed", str(error)
        raise
    finally:
        save()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
