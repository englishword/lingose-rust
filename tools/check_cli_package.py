"""CLI4.3: audit a real library archive and install a local CLI candidate.

Each run writes a new .local/cli43-* receipt and preserves its external temp
consumer. No CLI .crate or registry install is claimed. --dry-run requires the
library publication guard to have been removed separately after candidate
validation; this tool never changes source manifests or performs real uploads.
The 0.1.0 tools and receipts remain historical and are not invoked here.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import platform
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_workspace_package as audit

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "crates/lingose"
CLI = ROOT / "crates/lingose-cli"
MSRV_HOME = ROOT / ".local/p52-rustup-home"
require = audit.require


def identity(path):
    return audit.identity(Path(path).read_bytes())


def copy_checked(source, destination, expected=None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    require(identity(source) == identity(destination) == (expected or identity(source)), f"Copy drift: {source}")


def tree_identity(directory):
    records = {}
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), f"Symlink in isolated sources: {path}")
        if path.is_file():
            records[path.relative_to(directory).as_posix()] = identity(path)
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"files": len(records), "total_bytes": sum(row["bytes"] for row in records.values()),
            "inventory_sha256": audit.identity(encoded)["sha256"]}


def cli_inputs():
    manifest = tomllib.loads((CLI / "Cargo.toml").read_text(encoding="utf-8"))
    require(manifest["package"]["name"] == "lingose-cli" and
            manifest["package"]["version"] == "0.2.0" and
            manifest["package"].get("publish") is False, "Wrong/unguarded CLI candidate")
    require(manifest["dependencies"]["lingose"] == {"version": "0.2.0", "path": "../lingose"},
            "CLI library dependency changed")
    names = {"Cargo.toml"}
    for pattern in manifest["package"]["include"]:
        value = audit.safe_name(pattern.removeprefix("/"))
        matches = ((CLI / value[:-3]).rglob("*") if value.endswith("/**") else CLI.glob(value))
        files = [path for path in matches if path.is_file()]
        require(bool(files), f"Empty CLI include: {pattern}")
        for path in files:
            require(not path.is_symlink() and path.resolve().is_relative_to(CLI), "CLI source escaped")
            names.add(path.relative_to(CLI).as_posix())
    return {name: identity(CLI / name) for name in sorted(names)}


def check_includes(files):
    targets = []
    for name, data in files.items():
        if not name.endswith(".rs"):
            continue
        for target in re.findall(rb'include_(?:bytes|str)!\(\s*"([^"\n]+)"\s*\)', data):
            target = target.decode("utf-8")
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
            audit.safe_name(resolved)
            require(resolved in files, f"Rust include escapes package: {name}: {target}")
            targets.append({"source": name, "target": resolved})
    require({row["target"] for row in targets} ==
            {"README.md", "data/lexicon.bin", "data/frequency.bin"}, "Unexpected Rust includes")
    return targets


def check_portable_notices(files):
    """Map historical artifact names explicitly; do not regenerate old records."""
    notice = json.loads(files["docs/distribution-provenance.json"])
    require(files["docs/distribution-provenance.json"] ==
            (ROOT / "docs/distribution-provenance.json").read_bytes(), "Portable notice identity changed")
    for table in notice["unicode_tables"]:
        require(audit.identity(files[table["artifact"]]) == table["identity"], "Unicode table drift")
        source = table["historical_source_record"]
        require(identity(ROOT / source["name"]) == {key: source[key] for key in ("bytes", "sha256")},
                "Historical Unicode record drift")
    license_record = notice["unicode_license"]
    require(audit.identity(files[license_record["file"]]) ==
            {key: license_record[key] for key in ("bytes", "sha256")}, "Unicode license drift")
    historical = notice["dependency_notices"]["historical_source_record"]
    require(identity(ROOT / historical["name"]) ==
            {key: historical[key] for key in ("bytes", "sha256")}, "Historical loader receipt drift")
    locked = tomllib.loads(files["Cargo.lock"].decode("utf-8"))["package"]
    require({(row["name"], row["version"]) for row in locked if row["name"] != "lingose"} ==
            {(row["name"], row["version"]) for row in notice["dependency_notices"]["dependencies"]},
            "Library lock no longer matches historical library dependency notices")
    require(files["LICENSE"] == files["data/LICENSE"], "Data license identity changed")
    return {"unicode_tables_checked": len(notice["unicode_tables"]),
            "historical_library_dependency_names_versions_checked": True,
            "historical_lock_hash_is_not_the_new_workspace_lock": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Also run library publish --dry-run; never upload")
    args = parser.parse_args()
    source, inputs = audit.source_inventory()
    require(source["package"]["version"] == "0.2.0", "This consumer is specific to 0.2.0")
    if args.dry_run:
        require(source["package"].get("publish") is not False, "Validate guarded candidate first")
    cli_source = cli_inputs()
    execution_inputs = {name: identity(ROOT / name) for name in (
        "Cargo.toml", "Cargo.lock", "tools/check_cli_package.py", "tools/check_workspace_package.py",
        "tools/package_consumer_020.rs", "docs/performance-budget.json", "tests/fixtures/python-api-v1.json")}
    require(execution_inputs["tests/fixtures/python-api-v1.json"]["sha256"] ==
            "6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1", "Pinned P0 vectors changed")
    directory = Path(tempfile.mkdtemp(prefix="cli43-", dir=ROOT / ".local")).resolve()
    isolated = Path(tempfile.mkdtemp(prefix="lingose-cli43-")).resolve()
    require(not isolated.is_relative_to(ROOT) and not ROOT.is_relative_to(isolated), "Consumer is in checkout")
    logs = directory / "logs"
    logs.mkdir()
    snapshot = directory / "source"
    report = {"phase": "CLI4.3", "status": "running", "host": platform.platform(),
              "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
              "library_publish_guard": source["package"].get("publish") is False,
              "cli_publish_guard": True, "library_inputs": inputs, "cli_inputs": cli_source,
              "execution_inputs": execution_inputs, "commands": [], "isolation_directory": str(isolated),
              "source_strategy": "Byte-checked workspace snapshot without .git; no VCS metadata fabricated",
              "boundaries": ["Windows x86_64 MSVC only", "CLI is a local path candidate, no CLI .crate",
                             "no registry consumer/install", "no upload or GitHub Release",
                             "Frequency List and external category provenance gaps remain"]}
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    protected = {name: identity(ROOT / name) for name in tracked if name and (ROOT / name).is_file()}
    report["tracked_inputs_before"] = protected

    def persist():
        (directory / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    base = os.environ.copy()
    # Exclude inherited compiler/source overrides and credentials from validation.
    for name in list(base):
        if name.startswith(("CARGO_", "RUSTFLAGS", "RUSTDOCFLAGS", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER")):
            base.pop(name)
    base.update(CARGO_HOME=str(ROOT / ".local/cargo-home"), CARGO_TARGET_DIR=str(directory / "package-target"),
                CARGO_NET_OFFLINE="true", CARGO_TERM_COLOR="never")

    def run(label, command, cwd=snapshot, environment=base, stdin=None, expected=0):
        command = [str(part) for part in command]
        require("publish" not in command or ("--dry-run" in command and "-p" in command and
                command[command.index("-p") + 1] == "lingose"), "Only library dry-run is allowed")
        print(f"Running {label}", flush=True)
        start = time.perf_counter()
        result = subprocess.run(command, cwd=cwd, env=environment, input=stdin, capture_output=True, timeout=600)
        record = {"label": label, "argv": command, "cwd": str(cwd), "exit_code": result.returncode,
                  "expected_exit_code": expected, "elapsed_seconds": round(time.perf_counter() - start, 6)}
        for kind, data in (("stdout", result.stdout), ("stderr", result.stderr)):
            path = logs / f"{label}.{kind}.log"
            path.write_bytes(data)
            record[kind] = {"path": path.relative_to(ROOT).as_posix(), **identity(path)}
        report["commands"].append(record)
        persist()
        if result.returncode != expected:
            print(result.stderr.decode("utf-8", errors="replace"), flush=True)
        require(result.returncode == expected, f"Unexpected exit: {label}")
        return result

    try:
        persist()
        copy_checked(ROOT / "Cargo.toml", snapshot / "Cargo.toml", execution_inputs["Cargo.toml"])
        copy_checked(ROOT / "Cargo.lock", snapshot / "Cargo.lock", execution_inputs["Cargo.lock"])
        for name in inputs:
            if name != "Cargo.lock":
                copy_checked(LIB / name, snapshot / "crates/lingose" / name, inputs[name])
        for name in cli_source:
            copy_checked(CLI / name, snapshot / "crates/lingose-cli" / name, cli_source[name])
        listing = run("package-list", ["cargo", "package", "-p", "lingose", "--list", "--offline", "--locked"])
        audit.check_listing(listing.stdout.decode("utf-8").splitlines(), inputs)
        run("library-package", ["cargo", "package", "-p", "lingose", "--offline", "--locked", "--all-features"])
        artifact = directory / "package-target/package/lingose-0.2.0.crate"
        saved = directory / "lingose-0.2.0.crate"
        copy_checked(artifact, saved)
        require(inputs == audit.source_inventory()[1], "Library inputs changed before archive audit")
        files, links = audit.audit_archive(saved)
        budget = json.loads((ROOT / "docs/performance-budget.json").read_bytes())["limits"]
        require(saved.stat().st_size <= budget["packaged_crate_bytes"] <= 10_000_000, "Compressed budget exceeded")
        raw = sum(len(files[name]) for name in ("data/lexicon.bin", "data/frequency.bin"))
        require(raw <= budget["raw_runtime_resources_bytes"], "Raw runtime budget exceeded")
        report["archive"] = {"path": saved.relative_to(ROOT).as_posix(), **identity(saved),
                             "files": {name: audit.identity(data) for name, data in sorted(files.items())},
                             "local_inline_markdown_file_links": links, "rust_includes": check_includes(files),
                             "portable_notices": check_portable_notices(files),
                             "fixed_budget_bytes": budget["packaged_crate_bytes"], "raw_resources_bytes": raw}
        report["registry_rule"] = {"url": "https://doc.rust-lang.org/cargo/reference/publishing.html",
                                   "checked_on": "2026-10-18", "documented_limit": "10MB",
                                   "conservative_bytes_check": 10_000_000,
                                   "package_semantics_url": "https://doc.rust-lang.org/cargo/commands/cargo-package.html"}

        # Extract only the regular, audited payloads, never arbitrary tar paths.
        package = isolated / "unpacked/lingose-0.2.0"
        for name, data in files.items():
            path = package / PurePosixPath(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        run("vendor-preparation", ["cargo", "vendor", "--offline", "--locked", "--versioned-dirs", isolated / "vendor"])
        config = isolated / ".cargo/config.toml"
        config.parent.mkdir()
        config.write_text('[source.crates-io]\nreplace-with="vendored-sources"\n'
                          '[source.vendored-sources]\ndirectory=' + json.dumps(str(isolated / "vendor")) +
                          '\n[net]\noffline=true\n', encoding="utf-8")
        consumer, candidate = isolated / "consumer", isolated / "cli"
        copy_checked(ROOT / "tools/package_consumer_020.rs", consumer / "src/main.rs",
                     execution_inputs["tools/package_consumer_020.rs"])
        (consumer / "Cargo.toml").write_text('[package]\nname="lingose-package-consumer-020"\nversion="0.0.0"\n'
                    'edition="2024"\npublish=false\n[dependencies]\n'
                    'lingose={version="=0.2.0",path="../unpacked/lingose-0.2.0"}\n[workspace]\n', encoding="utf-8")
        for name in cli_source:
            copy_checked(CLI / name, candidate / name, cli_source[name])
        candidate_manifest = (candidate / "Cargo.toml").read_text(encoding="utf-8").replace(
            'path = "../lingose"', 'path = "../unpacked/lingose-0.2.0"') + '\n[workspace]\n'
        (candidate / "Cargo.toml").write_text(candidate_manifest, encoding="utf-8")
        parsed = tomllib.loads(candidate_manifest)
        require(parsed.pop("workspace") == {}, "Candidate is not standalone")
        parsed["dependencies"]["lingose"]["path"] = "../lingose"
        require(parsed == tomllib.loads((CLI / "Cargo.toml").read_text(encoding="utf-8")),
                "Candidate manifest differs beyond the isolated library path")
        copy_checked(ROOT / "Cargo.lock", candidate / "Cargo.lock")
        clean = base.copy()
        clean["CARGO_HOME"] = str(isolated / "empty-cargo-home")
        clean["CARGO_TARGET_DIR"] = str(isolated / "current-target")
        Path(clean["CARGO_HOME"]).mkdir()
        graphs = {}
        for label, project in (("consumer", consumer), ("cli", candidate)):
            run(f"{label}-lock", ["cargo", "generate-lockfile", "--offline"], project, clean)
            if label == "cli":
                audit.check_lock((project / "Cargo.lock").read_bytes(), (ROOT / "Cargo.lock").read_bytes(),
                                 {"name": "lingose-cli", "version": "0.2.0"})
            else:
                rows = tomllib.loads((project / "Cargo.lock").read_text(encoding="utf-8"))["package"]
                expected_rows = tomllib.loads(files["Cargo.lock"].decode("utf-8"))["package"]
                require({audit.lock_key(row) for row in rows if row["name"] != "lingose-package-consumer-020"} ==
                        {audit.lock_key(row) for row in expected_rows}, "Consumer dependency versions drifted")
            metadata = json.loads(run(f"{label}-metadata", ["cargo", "metadata", "--offline", "--locked",
                                     "--format-version", "1", "--filter-platform", "x86_64-pc-windows-msvc"], project, clean).stdout)
            require(all(Path(row["manifest_path"]).resolve().is_relative_to(isolated) for row in metadata["packages"]),
                    "Source escaped consumer isolation")
            library = [row for row in metadata["packages"] if row["name"] == "lingose"]
            require(len(library) == 1 and Path(library[0]["manifest_path"]).resolve() == package / "Cargo.toml",
                    "Consumer did not use the real unpacked library")
            graphs[label] = [{"name": row["name"], "version": row["version"],
                              "manifest": Path(row["manifest_path"]).relative_to(isolated).as_posix()}
                             for row in metadata["packages"]]
        report["isolated_dependency_graphs"] = graphs
        report["candidate_manifest"] = {"sha256": identity(candidate / "Cargo.toml")["sha256"],
                 "only_changes": ["library path points to real unpacked archive", "standalone empty workspace table"],
                 "source_files": cli_source, "not_a_registry_package": True}
        isolated_inputs = {name: tree_identity(isolated / name) for name in ("vendor", "consumer", "cli", ".cargo")}
        report["isolated_inputs_before"] = isolated_inputs
        runtime = isolated / "runtime"
        runtime.mkdir()
        binaries = []
        for label in ("current", "minimum"):
            environment = clean.copy()
            environment["CARGO_TARGET_DIR"] = str(isolated / f"{label}-target")
            prefix = []
            if label == "minimum":
                require((MSRV_HOME / "toolchains/1.85.0-x86_64-pc-windows-msvc").is_dir(), "Prepare MSRV toolchain first")
                environment["RUSTUP_HOME"] = str(MSRV_HOME)
                prefix = ["rustup", "run", "1.85.0-x86_64-pc-windows-msvc"]
            run(f"{label}-rustc", prefix + ["rustc", "-Vv"], consumer, environment)
            run(f"{label}-consumer-build", prefix + ["cargo", "build", "--release", "--offline", "--locked"], consumer, environment)
            run(f"{label}-cli-install", prefix + ["cargo", "install", "--path", candidate,
                            "--root", isolated / f"{label}-install", "--offline", "--locked"], candidate, environment)
            for kind, original in (("consumer", Path(environment["CARGO_TARGET_DIR"]) / "release/lingose-package-consumer-020.exe"),
                                   ("cli", isolated / f"{label}-install/bin/lingose.exe")):
                destination = runtime / f"{label}-{kind}.exe"
                copy_checked(original, destination)
            binaries.append((label, runtime / f"{label}-cli.exe"))
        run("packaged-library-tests", ["cargo", "test", "--offline", "--locked", "--all-features"], package, clean)
        run("packaged-library-doc", ["cargo", "doc", "--offline", "--locked", "--no-deps", "--all-features"], package, clean)
        # Runtime has only executables, PATH has no Python/Node/Cargo, and all
        # consumer build inputs are temporarily unavailable at their build paths.
        hidden = []
        for name in ("unpacked", "vendor", "consumer", "cli"):
            original, renamed = isolated / name, isolated / f"unavailable-{name}"
            require(original.resolve().parent == isolated and renamed.parent == isolated, "Unsafe isolation rename")
            original.rename(renamed)
            hidden.append((original, renamed))
        runtime_env = {key: value for key, value in clean.items() if not key.startswith(("CARGO_", "PYTHON", "RUST"))}
        runtime_env["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
        try:
            for label, binary in binaries:
                run(f"{label}-consumer-runtime", [runtime / f"{label}-consumer.exe"], runtime, runtime_env)
                cli_smoke(label, binary, runtime, runtime_env, run)
        finally:
            for original, renamed in reversed(hidden):
                renamed.rename(original)
        require(not (Path(clean["CARGO_HOME"]) / "registry").exists(), "Isolated build used registry cache")
        require(all((package / name).read_bytes() == data for name, data in files.items()), "Unpacked library changed")
        require(all(identity(candidate / name) == record for name, record in cli_source.items() if name != "Cargo.toml"),
                "CLI source changed during installation")
        require(isolated_inputs == {name: tree_identity(isolated / name) for name in isolated_inputs},
                "Isolated manifests, locks, sources, vendor or configuration changed")
        report["isolation"] = {"empty_cargo_home_registry_absent": True, "all_sources_inside_isolation": True,
                "runtime_sources_hidden": True, "runtime_path_system32_only": True,
                "runtime_files": {path.name: identity(path) for path in runtime.iterdir()},
                "consumer_source": identity(ROOT / "tools/package_consumer_020.rs"), "public_functions": 18,
                "cli_smoke_cases_per_toolchain": 25, "unpacked_sources_unchanged": True}
        if args.dry_run:
            online = base.copy()
            online.pop("CARGO_NET_OFFLINE")
            run("library-publish-dry-run", ["cargo", "publish", "-p", "lingose", "--dry-run", "--locked", "--all-features"], environment=online)
            dry = directory / "package-target/package/tmp-crate/lingose-0.2.0.crate"
            require(identity(dry) == identity(saved), "Dry-run archive differs from validated candidate")
            report["dry_run_archive"] = {"path": dry.relative_to(ROOT).as_posix(), **identity(dry), "identical": True}
        require(protected == {name: identity(ROOT / name) for name in protected}, "Tracked input changed")
        require(inputs == audit.source_inventory()[1] and cli_source == cli_inputs() and
                execution_inputs == {name: identity(ROOT / name) for name in execution_inputs},
                "Explicit execution inputs changed")
        report["explicit_and_isolated_inputs_unchanged"] = True
        report["tracked_inputs_unchanged"] = True
        report["status"] = "library_dry_run_and_local_cli_passed" if args.dry_run else "guarded_candidate_passed"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = str(error)
        raise
    finally:
        persist()
        print(f"Receipt: {directory.relative_to(ROOT) / 'report.json'}", flush=True)


def cli_smoke(label, binary, runtime, environment, run):
    """Pinned-value acceptance of the installed executable, independent of checkout data."""
    count = 0

    def invoke(name, arguments, stdin=None, expected=0):
        nonlocal count
        count += 1
        result = run(f"{label}-smoke-{name}", [binary, *arguments], runtime, environment, stdin, expected)
        require((not result.stderr) if expected == 0 else (bool(result.stderr) and not result.stdout),
                f"Output/diagnostic contract: {name}")
        return result.stdout

    expected_word = {"word": "apple", "ipa": ["æpəl"], "ips": ["apple"],
                     "ism": "app-le", "ipsm": ["app-le"], "root_lemma": "ap"}
    require(json.loads(invoke("word-json", ["word", "apple", "--json"])) == expected_word, "Word JSON differs")
    unknown = {"word": "unknownwordzz", "ipa": [], "ips": [], "ism": None, "ipsm": [], "root_lemma": None}
    require(json.loads(invoke("unknown", ["word", "unknownwordzz", "--json"])) == unknown, "Unknown result differs")
    plain = invoke("word-plain", ["word", "apple"]).decode("utf-8")
    expected_plain = "".join(f'{key}: {json.dumps(value, ensure_ascii=False, separators=(",", ":"))}\n'
                             for key, value in expected_word.items())
    require(plain == expected_plain, "Plain fields/values differ")
    require(b"annotate" in invoke("help", ["--help"]), "Help missing command")
    require(invoke("version", ["--version"]).strip() == b"lingose 0.2.0", "Version differs")
    original = "Abandon the book."
    marked = "\u00c5bando\u030an \u1e6bhe\u030a book."
    for threshold, expected in ((0, marked), (1000, "\u00c5bando\u030an the book."), (5062, original), (5063, original)):
        require(invoke(f"threshold-{threshold}", ["annotate", "--text", original, "--skip-top", str(threshold)]) ==
                expected.encode("utf-8"), "Threshold/plain bytes differ")
    require(invoke("stdin", ["annotate"], original.encode()) == marked.encode(), "stdin differs")
    require(invoke("empty", ["annotate"], b"") == b"", "Empty input differs")
    unicode = "café apple123 中文apple 中文\t123 é é\r\n😀"
    require(invoke("unicode", ["annotate"], unicode.encode()) == unicode.encode(), "Unicode/CRLF differs")
    require(json.loads(invoke("annotation-json", ["annotate", original, "--json"])) ==
            {"text": original, "annotate": marked}, "Annotation JSON differs")
    input_path, output = runtime / "apple", runtime / "output.txt"
    input_path.write_bytes(original.encode())
    try:
        require(invoke("auto-file", ["annotate", "apple"]) == marked.encode(), "Automatic file differs")
        require(invoke("explicit-file", ["annotate", "--input", "apple"]) == marked.encode(), "Explicit file differs")
        require(invoke("forced-text", ["annotate", "--text", "apple"]) == b"apple", "Forced text differs")
        require(invoke("output-file", ["annotate", "--input", "apple", "-o", "output.txt"]) == b"" and
                output.read_bytes() == marked.encode(), "Plain output differs")
        require(invoke("json-file", ["annotate", "--input", "apple", "-o", "output.txt", "--json"]) == b"" and
                json.loads(output.read_bytes()) == {"text": original, "annotate": marked}, "JSON file differs")
        before = output.read_bytes()
        invoke("missing-file", ["annotate", "--input", "missing.txt", "-o", "output.txt"], expected=1)
        require(output.read_bytes() == before, "Input error truncated output")
        input_path.write_bytes(b"\xff\xfe")
        invoke("invalid-file-utf8", ["annotate", "--input", "apple"], expected=1)
        invoke("invalid-stdin-utf8", ["annotate"], b"\xff", expected=1)
        invoke("directory", ["annotate", "."], expected=1)
        invoke("negative-threshold", ["annotate", "--text", original, "--skip-top=-1"], expected=2)
        invoke("conflicting-inputs", ["annotate", original, "--text", original], expected=2)
        invoke("missing-word", ["word"], expected=2)
    finally:
        input_path.unlink(missing_ok=True)
        output.unlink(missing_ok=True)
    require(count == 25, "Smoke receipt count differs")


if __name__ == "__main__":
    main()
