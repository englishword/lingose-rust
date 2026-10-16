"""P5.3: package a byte-checked snapshot, consume its archive, and dry-run only.

Writes a fresh .local/p53-* receipt; never uploads or rewrites historical reports.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import tomllib
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def package_inputs():
    metadata = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))["package"]
    require(metadata["name"] == "lingose" and metadata["version"] == "0.1.0", "Wrong package identity")
    require(metadata.get("publish") is not False, "Publication guard still present")
    names = {"Cargo.toml", "Cargo.lock"}
    for pattern in metadata["include"]:
        value = pattern.removeprefix("/")
        if value.endswith("/**"):
            names.update(path.relative_to(ROOT).as_posix() for path in (ROOT / value[:-3]).rglob("*") if path.is_file())
        else:
            require((ROOT / value).is_file(), f"Missing included file: {value}")
            names.add(value)
    required = {"README.md", "LICENSE", "SOURCES.md", "data/lexicon.bin", "data/frequency.bin",
                "data/manifest.json", "data/SOURCES.json", "data/UPSTREAM-SOURCES.md", "data/LICENSE",
                "third_party/unicode/LICENSE.txt", "docs/rust-api.md", "docs/distribution-provenance.json"}
    require(required <= names, "Required data, notices or public documentation omitted")
    return sorted(names)


def audit_archive(path, inputs):
    prefix = "lingose-0.1.0/"
    files = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            require(member.isfile() and member.name.startswith(prefix), "Unexpected archive entry type/root")
            name = member.name[len(prefix):]
            require(name not in files and ".." not in Path(name).parts and not name.startswith("/"), "Unsafe/duplicate archive path")
            stream = archive.extractfile(member)
            require(stream is not None, "Missing archive payload")
            files[name] = stream.read()
    require(set(files) == set(inputs) | {"Cargo.toml.orig"}, "Archive does not match explicit source inventory")
    require(files["Cargo.toml.orig"] == (ROOT / "Cargo.toml").read_bytes(), "Original manifest differs")
    for name, record in inputs.items():
        if name == "Cargo.toml":
            continue
        data = files[name]
        require({"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} == record, f"Archive input differs: {name}")
    manifest = tomllib.loads(files["Cargo.toml"].decode("utf-8"))
    require(manifest["package"].get("build") is False, "Unexpected build script")
    require("path" not in manifest["dependencies"]["sha2"], "Path dependency in normalized manifest")
    absolute = re.compile(rb"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/(?:Users|home|tmp)/")
    for name, data in files.items():
        require(not name.startswith(("tools/", "tasks/", ".local/", "target/")), f"Development file shipped: {name}")
        require(Path(name).suffix not in (".sqlite", ".db", ".xlsx", ".csv", ".py", ".pyc"), f"Maintenance data/tool shipped: {name}")
        if name.endswith(".bin"):
            continue
        require(not absolute.search(data), f"Absolute host path shipped: {name}")
        require(b"site-packages" not in data and b".local/" not in data and b".local\\" not in data, f"Host cache/installation path shipped: {name}")
    links = []
    for name, data in files.items():
        if not name.endswith(".md"):
            continue
        for href in re.findall(r"\[[^\]]*\]\(([^)]+)\)", data.decode("utf-8")):
            if re.match(r"(?:https?://|mailto:|#)", href):
                continue
            # Resolve through a synthetic root; never touch checkout paths.
            target = (Path("/package") / Path(name).parent / unquote(href.split("#", 1)[0])).resolve()
            relative = target.relative_to(Path("/package").resolve()).as_posix()
            require(relative in files, f"Broken packaged link: {name} -> {href}")
            links.append({"source": name, "href": href, "target": relative})
    return files, links


def main():
    local = ROOT / ".local"
    local.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="p53-package-", dir=local)).resolve()
    snapshot, logs = directory / "source", directory / "logs"
    snapshot.mkdir()
    logs.mkdir()
    report = {"phase": "P5.3", "status": "running", "commands": [],
              "directory": directory.relative_to(ROOT).as_posix(),
              "source_strategy": "Byte-checked snapshot without .git; no fabricated VCS metadata. Source input hashes bind the archive to the working tree.",
              "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "scope": "Local package/consumer/dry-run only; no upload, permission or registry installation acceptance"}

    def persist():
        (directory / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    base = os.environ.copy()
    for key in list(base):
        if (key.startswith("CARGO_") and "TOKEN" in key) or key.startswith("LINGOSE_"):
            base.pop(key)
    base["CARGO_HOME"] = str(local / "cargo-home")
    base["CARGO_TARGET_DIR"] = str(directory / "package-target")
    base["CARGO_NET_OFFLINE"] = "true"

    def run(label, command, cwd=snapshot, environment=base):
        require(not (command[:2] == ["cargo", "publish"] and "--dry-run" not in command), "Real upload forbidden in P5.3 tool")
        print(f"Running {label}", flush=True)
        start = time.perf_counter()
        result = subprocess.run(command, cwd=cwd, env=environment, capture_output=True, timeout=600)
        stdout, stderr = logs / f"{label}.stdout.log", logs / f"{label}.stderr.log"
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        report["commands"].append({"label": label, "argv": command, "cwd": str(cwd), "exit_code": result.returncode,
                                    "elapsed_seconds": round(time.perf_counter() - start, 6),
                                    "stdout": {"path": stdout.relative_to(ROOT).as_posix(), **identity(stdout)},
                                    "stderr": {"path": stderr.relative_to(ROOT).as_posix(), **identity(stderr)}})
        persist()
        if result.returncode:
            print(result.stdout.decode("utf-8", errors="replace"), flush=True)
            print(result.stderr.decode("utf-8", errors="replace"), flush=True)
        require(result.returncode == 0, f"Command failed: {label}")
        return result

    persist()
    try:
        run("portable-notice-check", ["D:/Python/Python312/python.exe", "-I", "-B", "-X", "utf8", "tools/prepare_package_sources.py", "--check"], ROOT)
        names = package_inputs()
        inputs = {name: identity(ROOT / name) for name in names}
        report["source_inputs"] = inputs
        for name in names:
            destination = snapshot / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
            require(identity(destination) == inputs[name], f"Copy drift: {name}")
        listing = run("package-list", ["cargo", "package", "--list", "--offline", "--locked"])
        listed = [name.replace("\\", "/") for name in listing.stdout.decode("utf-8").splitlines()]
        require(set(listed) == set(names) | {"Cargo.toml.orig"}, "Unexpected package --list inventory")
        run("package", ["cargo", "package", "--offline", "--locked", "--all-features"])
        artifact = directory / "package-target/package/lingose-0.1.0.crate"
        saved = directory / "lingose-0.1.0.crate"
        shutil.copyfile(artifact, saved)
        files, links = audit_archive(saved, inputs)
        budget = json.loads((ROOT / "docs/performance-budget.json").read_bytes())["limits"]["packaged_crate_bytes"]
        require(saved.stat().st_size <= budget, "Fixed compressed .crate budget exceeded")
        require(saved.stat().st_size <= 10_000_000, "Conservative 10 MB registry-doc limit exceeded")
        report["archive"] = {"path": saved.relative_to(ROOT).as_posix(), **identity(saved),
                             "files": {name: {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} for name, data in sorted(files.items())},
                             "local_links": links, "fixed_budget_bytes": budget, "budget_passed": True,
                             "vcs_metadata": "Absent: source snapshot deliberately has no .git; base commit and exact source identities are recorded separately"}
        # A fresh consumer outside the checkout, with an empty Cargo home and vendored dependencies.
        isolated = Path(tempfile.mkdtemp(prefix="lingose-p53-consumer-")).resolve()
        report["consumer_directory"] = str(isolated)
        unpacked, consumer, runtime = isolated / "unpacked", isolated / "consumer", isolated / "runtime"
        for path in (unpacked, consumer, runtime):
            path.mkdir()
        with tarfile.open(saved, "r:gz") as archive:
            archive.extractall(unpacked, filter="data")
        package = unpacked / "lingose-0.1.0"
        run("vendor-preparation", ["cargo", "vendor", "--offline", "--locked", "--versioned-dirs", str(consumer / "vendor")], package)
        (consumer / "src").mkdir()
        (consumer / ".cargo").mkdir()
        shutil.copyfile(ROOT / "tools/package_consumer.rs", consumer / "src/main.rs")
        (consumer / "Cargo.toml").write_text('[package]\nname="lingose-package-consumer"\nversion="0.0.0"\nedition="2024"\npublish=false\n[dependencies]\nlingose={version="=0.1.0",path="../unpacked/lingose-0.1.0"}\n[workspace]\n', encoding="utf-8")
        (consumer / ".cargo/config.toml").write_text('[source.crates-io]\nreplace-with="vendored-sources"\n[source.vendored-sources]\ndirectory="vendor"\n[net]\noffline=true\n', encoding="utf-8")
        clean = base.copy()
        clean["CARGO_HOME"] = str(isolated / "empty-cargo-home")
        clean["CARGO_TARGET_DIR"] = str(isolated / "current-target")
        Path(clean["CARGO_HOME"]).mkdir()
        run("consumer-lock", ["cargo", "generate-lockfile", "--offline"], consumer, clean)
        metadata = run("consumer-metadata", ["cargo", "metadata", "--offline", "--locked", "--format-version", "1"], consumer, clean)
        packages = json.loads(metadata.stdout)["packages"]
        require(all(Path(row["manifest_path"]).resolve().is_relative_to(isolated) for row in packages), "Consumer borrowed an external source")
        report["consumer_dependencies"] = [{"name": row["name"], "version": row["version"], "manifest": str(Path(row["manifest_path"]).relative_to(isolated))} for row in packages]
        outputs = []
        for label in ("current", "minimum"):
            environment = clean.copy()
            environment["CARGO_TARGET_DIR"] = str(isolated / f"{label}-target")
            prefix = []
            if label == "minimum":
                environment["RUSTUP_HOME"] = str(local / "p52-rustup-home")
                prefix = ["rustup", "run", "1.85.0-x86_64-pc-windows-msvc"]
            run(f"consumer-{label}-build", prefix + ["cargo", "build", "--offline", "--locked", "--release"], consumer, environment)
            executable = Path(environment["CARGO_TARGET_DIR"]) / "release/lingose-package-consumer.exe"
            standalone = runtime / f"{label}.exe"
            shutil.copyfile(executable, standalone)
            completed = run(f"consumer-{label}-runtime", [str(standalone)], runtime, environment)
            outputs.append(completed.stdout)
        require(outputs[0] == outputs[1], "Toolchain consumer output differs")
        require(not (Path(clean["CARGO_HOME"]) / "registry").exists(), "Consumer used a registry cache")
        for name, data in files.items():
            require((package / name).read_bytes() == data, f"Consumer altered packaged input: {name}")
        report["consumer"] = {"toolchains": {"current": run("consumer-current-version", ["rustc", "-Vv"], consumer, clean).stdout.decode("utf-8").strip(),
                                                "minimum": run("consumer-minimum-version", ["rustup", "run", "1.85.0-x86_64-pc-windows-msvc", "rustc", "-Vv"], consumer, environment).stdout.decode("utf-8").strip()},
                              "all_18_public_entries": True,
                              "source": identity(ROOT / "tools/package_consumer.rs"), "runtime_files": sorted(path.name for path in runtime.iterdir()),
                              "source_paths_confined_to_isolation": True, "empty_cargo_home_registry_absent": True,
                              "vendored_dependencies_only": True, "outputs_identical": True}
        # Run actual Cargo dry-run; all upload paths remain disabled by --dry-run.
        dry_environment = base.copy()
        dry_environment.pop("CARGO_NET_OFFLINE", None)
        run("publish-dry-run", ["cargo", "publish", "--dry-run", "--locked", "--all-features"], environment=dry_environment)
        dry_artifact = directory / "package-target/package/tmp-crate/lingose-0.1.0.crate"
        require(identity(dry_artifact) == identity(saved), "Dry-run produced a different archive")
        report["dry_run_archive"] = {"path": dry_artifact.relative_to(ROOT).as_posix(), **identity(dry_artifact)}
        require(all(identity(ROOT / name) == identity(snapshot / name) == record for name, record in inputs.items()), "Source inputs changed")
        report["source_inputs_unchanged"] = True
        report["dry_run_archive_identical"] = True
        report["registry_rule"] = {"url": "https://doc.rust-lang.org/cargo/reference/publishing.html", "checked_on": "2026-10-16",
                                    "documented_limit": "10MB", "conservative_bytes_check": 10_000_000,
                                    "local_budget_is_stricter": True}
        report["rustc"] = run("rustc-version", ["rustc", "-Vv"]).stdout.decode("utf-8").strip()
        report["cargo"] = run("cargo-version", ["cargo", "-V"]).stdout.decode("utf-8").strip()
        report["status"] = "local_upload_ready"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = str(error)
        raise
    finally:
        persist()
    print(f"P5.3 passed: {saved.stat().st_size:,} bytes; receipt {directory.relative_to(ROOT) / 'report.json'}", flush=True)


if __name__ == "__main__":
    main()
