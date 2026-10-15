"""Run isolated release layout probes; preserve measured evidence without claiming annotation acceptance."""

from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import winreg

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import ROOT, fingerprints, json_text, main_error, no_restore, require, require_baseline

CANDIDATES = ("static", "static-hash", "gzip", "hash")
DATA = ROOT/".local/layout"


class Counters(ctypes.Structure):
    _fields_ = [("cb",ctypes.c_uint32),("PageFaultCount",ctypes.c_uint32)] + [
        (name,ctypes.c_size_t) for name in ("PeakWorkingSetSize","WorkingSetSize",
        "QuotaPeakPagedPoolUsage","QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage",
        "QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage","PrivateUsage")]


class MemoryStatus(ctypes.Structure):
    _fields_ = [("length",ctypes.c_uint32),("load",ctypes.c_uint32)] + [
        (name,ctypes.c_uint64) for name in ("total_physical","available_physical",
        "total_pagefile","available_pagefile","total_virtual","available_virtual","extended")]


def memory(pid):
    kernel = ctypes.WinDLL("kernel32",use_last_error=True)
    psapi = ctypes.WinDLL("psapi",use_last_error=True)
    kernel.OpenProcess.argtypes = (ctypes.c_uint32,ctypes.c_bool,ctypes.c_uint32)
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = (ctypes.c_void_p,)
    psapi.GetProcessMemoryInfo.argtypes = (ctypes.c_void_p,ctypes.POINTER(Counters),ctypes.c_uint32)
    handle = kernel.OpenProcess(0x1000,False,pid)
    require(bool(handle), f"OpenProcess failed: {ctypes.get_last_error()}")
    try:
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        require(bool(psapi.GetProcessMemoryInfo(handle,ctypes.byref(counters),counters.cb)),
                f"GetProcessMemoryInfo failed: {ctypes.get_last_error()}")
        return {key:int(getattr(counters,key)) for key in
                ("WorkingSetSize","PeakWorkingSetSize","PrivateUsage","PeakPagefileUsage")}
    finally:
        kernel.CloseHandle(handle)


def machine():
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
        cpu = winreg.QueryValueEx(key,"ProcessorNameString")[0].strip()
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    require(bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))), "Cannot read system RAM")
    return {"cpu":cpu,"logical_cpus":os.cpu_count(),"physical_memory_bytes":status.total_physical,
            "platform":platform.platform(),"architecture":platform.machine(),
            "python":sys.version,"rustc":subprocess.check_output(["rustc","--version","--verbose"],text=True).strip(),
            "cargo":subprocess.check_output(["cargo","--version"],text=True).strip(),
            "timer":"Rust std::time::Instant; external Python perf_counter",
            "conditions":"desktop session, no CPU affinity or OS-cache flush, other system activity uncontrolled"}


def summarize(values):
    ordered = sorted(values)
    return {"samples":values,"min":min(values),"median":statistics.median(values),
            "p95_nearest_rank":ordered[math.ceil(.95*len(ordered))-1],"max":max(values)}


def command(executable, *options):
    return [str(executable),str(DATA/"corpus-10000.txt"),str(DATA/"corpus-100000.txt"),*options]


def build(candidate, env):
    subprocess.run(["cargo","build","--manifest-path",str(ROOT/"tools/layout-probe/Cargo.toml"),
                    "--offline","--locked","--release","--no-default-features","--features",candidate],
                   cwd=ROOT,env=env,check=True)
    source = Path(env["CARGO_TARGET_DIR"])/"release/lingose-layout-probe.exe"
    destination = DATA/"bin"/(candidate+".exe")
    destination.parent.mkdir(exist_ok=True)
    destination.write_bytes(source.read_bytes())
    return destination


def invoke(executable, load_only=False):
    start = time.perf_counter()
    result = subprocess.run(command(executable,*( ["--load-only"] if load_only else [])),
                            capture_output=True,text=True,encoding="utf-8",check=True)
    wall = (time.perf_counter()-start)*1000
    report = json.loads(result.stdout)
    return report,wall


def sample_memory(executable):
    with subprocess.Popen(command(executable,"--hold-before-load","--hold","--load-only"),
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding="utf-8") as process:
        try:
            require(process.stderr.readline().strip() == "ready-before-load", "Probe pre-load handshake failed")
            before = memory(process.pid)
            process.stdin.write("\n")
            process.stdin.flush()
            report = json.loads(process.stdout.readline())
            after = memory(process.pid)
            process.stdin.write("\n")
            process.stdin.flush()
            process.wait(timeout=20)
            require(process.returncode == 0, "Memory probe failed")
            return {"before":before,"after":after,
                "delta":{key:after[key]-before[key] for key in after},
                "logical_content_checksum":report["logical_content_checksum"]}
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()


def python_reference(baseline, rounds):
    import lingose
    results = []
    with no_restore():
        for count in (10000,100000):
            text = (DATA/f"corpus-{count}.txt").read_text(encoding="utf-8")
            for threshold in (0,1000,5062):
                times,identities = [],[]
                for _ in range(rounds):
                    started = time.perf_counter()
                    output = lingose.annotate_ips(text,skip_top=threshold)
                    times.append((time.perf_counter()-started)*1000)
                    encoded = output.encode("utf-8")
                    identities.append({"bytes":len(encoded),"sha256":hashlib.sha256(encoded).hexdigest()})
                require(all(value == identities[0] for value in identities), "Reference annotation is nondeterministic")
                destination = DATA/f"reference-{count}-skip-{threshold}.txt"
                if destination.exists():
                    require(destination.read_bytes() == encoded, "Reference output drift")
                else:
                    destination.write_bytes(encoded)
                results.append({"words":count,"skip_top":threshold,"elapsed_ms":summarize(times),
                                "output":identities[0]})
                print(f"Python full annotation {count} words skip={threshold}: median {statistics.median(times):.2f} ms",flush=True)
    require(fingerprints() == baseline["fingerprints"], "Reference changed during annotation benchmark")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--repeats",type=int,default=7)
    parser.add_argument("--python-reference",action="store_true")
    parser.add_argument("--python-repeats",type=int,default=3)
    parser.add_argument("--skip-build",action="store_true")
    args = parser.parse_args()
    require(os.name == "nt", "This measurement runner currently supports Windows only")
    require(args.repeats >= 5 and args.python_repeats >= 1, "Insufficient measurement repetitions")
    destination = args.output.resolve()
    require(destination.is_relative_to(ROOT), "Evidence output must remain in project")
    require(not destination.exists(), "Use a new output path to preserve prior measurements")
    manifest = json.loads((DATA/"manifest.json").read_text(encoding="utf-8"))
    for name,identity in manifest["artifacts"].items():
        value = (DATA/name).read_bytes()
        require(len(value) == identity["bytes"] and hashlib.sha256(value).hexdigest() == identity["sha256"], f"Probe input drift: {name}")
    env = os.environ | {"CARGO_HOME":str(ROOT/".local/cargo-home"),"CARGO_TARGET_DIR":str(ROOT/".local/layout-target")}
    executables = {candidate: DATA/"bin"/(candidate+".exe") for candidate in CANDIDATES}
    if not args.skip_build:
        for candidate in CANDIDATES:
            executables[candidate] = build(candidate,env)
    for candidate in CANDIDATES:
        require(executables[candidate].is_file(), f"Missing release binary: {candidate}")
    records = {candidate:{"cold":[],"warm":[],"cold_wall_ms":[],"memory":[]} for candidate in CANDIDATES}
    # One unmeasured complete workload warms each executable's pages/OS file cache.
    for candidate in CANDIDATES:
        invoke(executables[candidate])
    for repeat in range(args.repeats):
        for candidate in CANDIDATES:
            report,wall = invoke(executables[candidate],True)
            records[candidate]["cold"].append(report)
            records[candidate]["cold_wall_ms"].append(wall)
            report,_ = invoke(executables[candidate])
            records[candidate]["warm"].append(report)
        print(f"Rust release round {repeat+1}/{args.repeats} complete",flush=True)
    for _ in range(3):
        for candidate in CANDIDATES:
            records[candidate]["memory"].append(sample_memory(executables[candidate]))
    identities = {(row["lexicon_sha256"],row["frequency_sha256"],row["logical_content_checksum"])
                  for candidate in CANDIDATES for mode in ("cold","warm") for row in records[candidate][mode]}
    require(len(identities) == 1, "Candidate decoded data differs")
    scenario_contracts = {tuple((row["scenario"],row["operations"],row["output_bytes"]) for row in record["measurements"])
                         for candidate in CANDIDATES for record in records[candidate]["warm"]}
    require(len(scenario_contracts) == 1, "Candidate workload coverage or output byte counts differ")
    summary = {}
    for candidate,record in records.items():
        example = record["warm"][0]
        summary[candidate] = {
            "binary_bytes":executables[candidate].stat().st_size,
            "binary_sha256":hashlib.sha256(executables[candidate].read_bytes()).hexdigest(),
            "embedded_bytes":example["embedded_bytes"],
            "cold_process_exit_ms":summarize(record["cold_wall_ms"]),
            "initialization_ms":{key:summarize([row[key] for row in record["cold"]])
                for key in ("lexicon_load_ms","frequency_load_ms","load_ms","index_ms")},
            "measurements":[],"memory_samples":record["memory"]}
        for index,measurement in enumerate(example["measurements"]):
            summary[candidate]["measurements"].append({
                "scenario":measurement["scenario"],"operations":measurement["operations"],
                "output_bytes":measurement["output_bytes"],
                "elapsed_ms":summarize([row["measurements"][index]["elapsed_ms"] for row in record["warm"]]),
                "ns_per_operation":summarize([row["measurements"][index]["ns_per_operation"] for row in record["warm"]])})
    python = []
    if args.python_reference:
        python = python_reference(require_baseline(),args.python_repeats)
    report = {"experiment":"P1.2-layout-v1","measured_at_utc":datetime.now(timezone.utc).isoformat(),
        "machine":machine(),"inputs":manifest,"repeats":args.repeats,
        "protocol":{"build":"release, thin LTO, codegen-units=1, strip=true, offline locked dependencies",
                    "cold":"fresh process; OS cache warm; cold_process_exit includes runtime startup, both loads, full logical checksum, JSON, exit; no public API first-call claim",
                    "warm":"one complete unmeasured process per candidate, then one measured full workload in each fresh process; per-scenario timers exclude initialization",
                    "statistics":"median and nearest-rank p95; with 7 repetitions p95 is maximum",
                    "memory":"3 fresh paused processes, GetProcessMemoryInfo PROCESS_MEMORY_COUNTERS_EX, before init and after both resources/index/checksum; absolute and delta retained/peak; includes runtime, not allocator-only memory",
                    "semantic_scope":"exact-key owned query projection and full ASCII text lookup workload only; Rust annotate_ips not implemented or measured"},
        "shared_identity":list(next(iter(identities))),"candidates":summary,"python_annotation":python,
        "probe_source_sha256":{str(path.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [ROOT/"tools/prepare_layout_probe.py",ROOT/"tools/run_layout_probe.py",ROOT/"tools/layout-probe/Cargo.toml",ROOT/"tools/layout-probe/Cargo.lock",*sorted((ROOT/"tools/layout-probe/src").glob("*.rs"))]}}
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json_text(report),encoding="utf-8",newline="\n")
    (DATA/"raw-measurements.json").write_text(json_text(records),encoding="utf-8",newline="\n")
    print(f"Saved {destination}",flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
