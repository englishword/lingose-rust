"""Build CLI5.1 candidates and retain native execution evidence (stdlib only).

CI artifacts are verification candidates, not licensed release archives. No
registry upload, GitHub Release creation or external Python oracle is used.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "x86_64-pc-windows-msvc": ("Windows", {"amd64", "x86_64"}),
    "x86_64-unknown-linux-gnu": ("Linux", {"amd64", "x86_64"}),
    "aarch64-unknown-linux-gnu": ("Linux", {"aarch64", "arm64"}),
    "x86_64-apple-darwin": ("Darwin", {"amd64", "x86_64"}),
    "aarch64-apple-darwin": ("Darwin", {"aarch64", "arm64"}),
}
TEXT = "Abandon the book."
ANNOTATED = "\u00c5bando\u030an \u1e6bhe\u030a book."


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def inputs():
    names = subprocess.check_output(
        ["git", "ls-files", "-z", "Cargo.toml", "Cargo.lock", "crates"], cwd=ROOT
    ).decode("utf-8").split("\0")
    names += ["tools/check_cli_release.py", ".github/workflows/cli-release.yml"]
    return {name: identity(ROOT / name) for name in sorted(set(names)) if name}


def smoke(executable, report, save):
    # Tempfile is outside the checkout. Only the binary is copied; no source,
    # vendor directory or external dictionary is available through cwd or PATH.
    with tempfile.TemporaryDirectory(prefix="lingose-cli51-") as temporary:
        runtime = Path(temporary).resolve()
        require(not runtime.is_relative_to(ROOT), "Runtime must be outside checkout")
        binary = runtime / executable.name
        shutil.copy2(executable, binary)
        environment = {"HOME": str(runtime), "TMPDIR": str(runtime),
                       "TMP": str(runtime), "TEMP": str(runtime)}
        if os.name == "nt":
            environment["SystemRoot"] = os.environ["SystemRoot"]
            environment["PATH"] = str(Path(environment["SystemRoot"]) / "System32")
        else:
            environment["PATH"] = "/usr/bin:/bin"
        report["runtime"] = {
            "mode": "native", "isolated_cwd": True, "copied_files": [binary.name],
            "environment_keys": sorted(environment),
            "network_disabled": False,
            "note": "Only the binary is copied; OS runtime libraries remain available. No network sandbox is asserted.",
        }

        def invoke(name, argv, expected=None, data=b"", json_value=None, code=0):
            timed_out = False
            try:
                value = subprocess.run([str(binary), *argv], input=data, cwd=runtime,
                                       env=environment, capture_output=True, timeout=60)
            except subprocess.TimeoutExpired as error:
                timed_out = True
                value = subprocess.CompletedProcess(argv, None, error.stdout or b"", error.stderr or b"")
            row = {"name": name, "argv": argv, "stdin_hex": data.hex(),
                   "exit_code": value.returncode, "stdout_hex": value.stdout.hex(),
                   "stderr_hex": value.stderr.hex(), "timed_out": timed_out, "passed": False}
            report["smoke"].append(row)
            save()
            require(not timed_out, f"{name}: process timed out")
            require(value.returncode == code, f"{name}: exit code differs")
            if code == 0:
                require(value.stderr == b"", f"{name}: unexpected stderr")
            else:
                require(value.stderr != b"", f"{name}: missing diagnostic")
            if json_value is not None:
                actual = json.loads(value.stdout)
                require(type(actual) is dict and actual == json_value,
                        f"{name}: complete JSON value differs")
                require(all(type(actual[key]) is type(expected_value)
                            for key, expected_value in json_value.items()),
                        f"{name}: JSON types differ")
            else:
                require(value.stdout == expected, f"{name}: stdout bytes differ")
            row["passed"] = True
            save()

        apple = {"word": "apple", "ipa": ["\u00e6p\u0259l"], "ips": ["apple"],
                 "ism": "app-le", "ipsm": ["app-le"], "root_lemma": "ap"}
        unknown = {"word": "unknownwordzz", "ipa": [], "ips": [], "ism": None,
                   "ipsm": [], "root_lemma": None}
        invoke("version", ["--version"], b"lingose 0.2.0\n")
        invoke("word-json", ["word", "apple", "--json"], json_value=apple)
        plain = "".join(f"{key}: {json.dumps(value, ensure_ascii=False, separators=(',', ':'))}\n"
                        for key, value in apple.items()).encode("utf-8")
        invoke("word-plain", ["word", "apple"], plain)
        invoke("unknown-json", ["word", "unknownwordzz", "--json"], json_value=unknown)
        invoke("text", ["annotate", "--text", TEXT], ANNOTATED.encode("utf-8"))
        invoke("stdin-crlf", ["annotate"], (ANNOTATED + "\r\n").encode("utf-8"),
               data=(TEXT + "\r\n").encode("utf-8"))
        invoke("annotate-json", ["annotate", "--text", TEXT, "--json"],
               json_value={"text": TEXT, "annotate": ANNOTATED})
        invoke("stdin-json", ["annotate", "--json"], data=(TEXT + "\n").encode("utf-8"),
               json_value={"text": TEXT + "\n", "annotate": ANNOTATED + "\n"})
        invoke("empty-stdin", ["annotate"], b"")
        invoke("skip-top", ["annotate", "--text", TEXT, "--skip-top", "5062"], TEXT.encode("utf-8"))
        invoke("invalid-utf8", ["annotate"], b"", data=b"\xff", code=1)
        invoke("usage-error", ["word"], b"", code=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    require(not (destination / "report.json").exists(), "Use a fresh evidence directory")
    report = {"phase": "CLI5.1", "target": args.target, "status": "running",
              "started_at": datetime.now(timezone.utc).isoformat(),
              "platform": platform.platform(), "machine": platform.machine(),
              "python": platform.python_version(), "commands": [], "smoke": [],
              "runner": {key: os.environ.get(key) for key in
                         ("RUNNER_OS", "RUNNER_ARCH", "ImageOS", "ImageVersion",
                          "GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")}}

    def save():
        (destination / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    def command(label, argv, echo=True):
        print("+ " + " ".join(argv), flush=True)
        row = {"label": label, "argv": argv, "exit_code": None}
        report["commands"].append(row)
        save()
        timed_out = False
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=900)
        except subprocess.TimeoutExpired as error:
            timed_out = True
            result = subprocess.CompletedProcess(argv, None, error.stdout or b"", error.stderr or b"")
        for stream in ("stdout", "stderr"):
            content = getattr(result, stream)
            path = destination / f"{label}.{stream}.txt"
            path.write_bytes(content)
            row[stream] = {"file": path.name, **identity(path)}
            if echo:
                print(content.decode("utf-8", errors="replace"), end="", flush=True)
        row["exit_code"] = result.returncode
        row["timed_out"] = timed_out
        save()
        require(not timed_out, f"{label} timed out; retained partial logs in {destination}")
        require(result.returncode == 0, f"{label} failed; retained logs in {destination}")
        return result.stdout.decode("utf-8").strip()

    save()
    try:
        system, architectures = TARGETS[args.target]
        require(platform.system() == system and platform.machine().lower() in architectures,
                "Native runner OS/architecture does not match requested target")
        report["inputs"] = inputs()
        report["revision"] = command("revision", ["git", "rev-parse", "HEAD"])
        rustc = command("rustc", ["rustc", "-vV"])
        require(f"host: {args.target}" in rustc.splitlines(), "Rust host must match native target")
        require("release: 1.93.1" in rustc.splitlines(), "Expected pinned Rust 1.93.1")
        report["cargo"] = command("cargo", ["cargo", "-V"])
        # -p selects the delivery CLI and its library dependency, never dev probes.
        command("build", ["cargo", "build", "-p", "lingose-cli", "--release", "--locked",
                          "--all-features", "--target", args.target])
        command("tests", ["cargo", "test", "-p", "lingose-cli", "--release", "--locked",
                          "--all-features", "--target", args.target])
        metadata = json.loads(command("metadata", ["cargo", "metadata", "--no-deps",
                                                   "--format-version", "1", "--locked"], echo=False))
        name = "lingose.exe" if system == "Windows" else "lingose"
        executable = Path(metadata["target_directory"]) / args.target / "release" / name
        candidate = destination / "candidate" / name
        candidate.parent.mkdir()
        shutil.copy2(executable, candidate)
        report["binary"] = {"file": f"candidate/{name}", **identity(candidate)}
        smoke(candidate, report, save)
        require(inputs() == report["inputs"], "Build inputs changed during verification")
        report["status"] = "passed"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        save()
    print(f"Native {args.target}: {len(report['smoke'])} smoke cases passed; {destination}")


if __name__ == "__main__":
    main()
