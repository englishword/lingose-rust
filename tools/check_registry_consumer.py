"""P6.3: consume published lingose from a fresh public registry cache.

Creates new receipts and a standalone temporary project. Never publishes,
reads credentials, copies cached packages, or rewrites earlier evidence.
Run in a normal user context if sandbox Schannel cannot access its credentials.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import http.client
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
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "registry+https://github.com/rust-lang/crates.io-index"
FUNCTIONS = ["ipa", "IPA", "ips", "IPS", "ism", "ISM", "ipsm", "IPSM",
             "root_lemma", "meaning", "meaning_with_lang", "kind", "kind_with_label",
             "kind_list", "kind_list_with_label", "labels", "annotate_ips", "annotate_ips_with_skip_top"]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def check_metadata(metadata, isolated):
    """Reject path/patch/source overrides and sources outside the isolation."""
    root_id = metadata["resolve"]["root"]
    packages = metadata["packages"]
    root_package = next(row for row in packages if row["id"] == root_id)
    require(Path(metadata["workspace_root"]).resolve() == (isolated / "consumer").resolve(), "Foreign workspace")
    require(root_package["name"] == "lingose-registry-consumer", "Unexpected consumer")
    require(root_package["source"] is None, "Consumer must be local")
    dependency = next(row for row in root_package["dependencies"] if row["name"] == "lingose")
    require(dependency["req"] == "=0.1.0" and dependency["source"] == REGISTRY, "Not the exact registry dependency")
    require(not dependency.get("path"), "Local path override")
    require(not any((isolated / "consumer").glob(".cargo/config*")), "Consumer Cargo config override")
    for row in packages:
        path = Path(row["manifest_path"]).resolve()
        require(path.is_relative_to(isolated.resolve()), "Borrowed dependency outside isolation")
        if row["id"] != root_id:
            require(row["source"] == REGISTRY, "Non-crates.io dependency")
            require(path.is_relative_to((isolated / "cargo-home/registry/src").resolve()), "Dependency did not come from fresh registry cache")
    lingose = next(row for row in packages if row["name"] == "lingose")
    require(lingose["version"] == "0.1.0", "Wrong resolved version")
    return lingose


def main():
    tag = uuid.uuid4().hex[:12]
    receipt = ROOT / ".local" / ("p63-registry-" + tag)
    receipt.mkdir(parents=True)
    logs = receipt / "logs"
    logs.mkdir()
    shutil.copyfile(Path(__file__), receipt / "check_registry_consumer.py")
    isolated = (Path(tempfile.gettempdir()) / ("lingose-p63-" + tag)).resolve()
    require(not isolated.is_relative_to(ROOT.resolve()), "Consumer must be outside checkout")
    require(not isolated.exists(), "Refuse to reuse a prior consumer")
    isolated.mkdir()
    consumer = isolated / "consumer"
    cargo_home = isolated / "cargo-home"
    runtime = isolated / "runtime"
    for path in (consumer / "src", cargo_home, runtime, isolated / "runtime-empty-home"):
        path.mkdir(parents=True)
    require(not any(cargo_home.iterdir()), "Cargo home was not empty")
    publication = json.loads((ROOT / "docs/publication.json").read_text(encoding="utf-8"))
    preflight = json.loads((ROOT / "docs/publication-preflight.json").read_text(encoding="utf-8"))
    expected = publication["registry"]["checksum"]
    require(publication["status"] == "published_and_index_verified", "No verified publication")
    expected_consumer = preflight["verification"]["package_and_consumers"]["consumer"]["source"]
    require(identity(ROOT / "tools/package_consumer.rs") == expected_consumer, "Consumer changed since preflight")
    manifest = ('[package]\nname="lingose-registry-consumer"\nversion="0.0.0"\n'
                'edition="2024"\nrust-version="1.85"\npublish=false\n'
                '[dependencies]\nlingose="=0.1.0"\n[workspace]\nresolver="3"\n')
    (consumer / "Cargo.toml").write_text(manifest, encoding="utf-8", newline="\n")
    shutil.copyfile(ROOT / "tools/package_consumer.rs", consumer / "src/main.rs")
    protected = {name: identity(ROOT / name) for name in preflight["candidate"]["source_inputs"]}
    histories = {name: identity(ROOT / name) for name in ("docs/publication.json", "docs/publication-preflight.json", "docs/package-verification.json")}
    report = {"phase": "P6.3", "status": "running", "started_at_utc": now(),
              "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "receipt_directory": receipt.relative_to(ROOT).as_posix(), "isolation_directory": str(isolated),
              "expected_archive_sha256": expected, "commands": [], "http": [],
              "consumer_source": expected_consumer, "consumer_manifest": identity(consumer / "Cargo.toml"),
              "cargo_home_initially_empty": True, "root_lockfile_or_caches_copied": False,
              "credentials_read_or_copied": False, "protected_inputs_before": protected,
              "historical_records_before": histories,
              "script": {"path": (receipt / "check_registry_consumer.py").relative_to(ROOT).as_posix(), **identity(Path(__file__))}}

    def persist():
        (receipt / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    environment = os.environ.copy()
    for key in list(environment):
        if key.startswith(("CARGO_", "LINGOSE_")) or key in ("RUSTFLAGS", "RUSTDOCFLAGS", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "RUSTC", "RUSTDOC", "RUSTUP_TOOLCHAIN"):
            environment.pop(key)
    environment["CARGO_HOME"] = str(cargo_home)
    environment["CARGO_TARGET_DIR"] = str(isolated / "online-target")
    environment["CARGO_TERM_COLOR"] = "never"
    # No source replacement, credential/config copying, or seeded registry cache.

    def run(label, command, env=environment, cwd=consumer):
        require(command[:2] != ["cargo", "publish"], "Publication forbidden")
        print("Running " + label, flush=True)
        started = time.perf_counter()
        completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=600)
        row = {"label": label, "argv": command, "cwd": str(cwd), "exit_code": completed.returncode,
               "elapsed_seconds": round(time.perf_counter() - started, 6)}
        for kind, body in (("stdout", completed.stdout), ("stderr", completed.stderr)):
            path = logs / (label + "." + kind + ".log")
            path.write_bytes(body)
            row[kind] = {"path": path.relative_to(ROOT).as_posix(), **identity(path)}
        report["commands"].append(row)
        persist()
        if completed.returncode:
            print(completed.stdout.decode("utf-8", errors="replace"), flush=True)
            print(completed.stderr.decode("utf-8", errors="replace"), flush=True)
        require(completed.returncode == 0, "Command failed: " + label)
        return completed

    def fetch(label, url):
        request = urllib.request.Request(url, headers={"User-Agent": "lingose-registry-acceptance/0.1.0 (P6.3 read-only)"})
        for attempt in range(1, 4):
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    status, body, final = response.status, response.read(), response.url
                break
            except urllib.error.HTTPError as error:
                status, body, final = error.code, error.read(), url
                break
            except (http.client.IncompleteRead, urllib.error.URLError, TimeoutError, ConnectionError) as error:
                row = {"label": label, "url": url, "attempt": attempt,
                       "error_type": type(error).__name__, "checked_at_utc": now()}
                if isinstance(error, http.client.IncompleteRead):
                    partial = receipt / (label + ".attempt-" + str(attempt) + ".partial")
                    partial.write_bytes(error.partial)
                    row["partial"] = {"path": partial.relative_to(ROOT).as_posix(), **identity(partial)}
                report.setdefault("http_transport_errors", []).append(row)
                persist()
                if attempt == 3:
                    raise
        path = receipt / (label + ".body")
        path.write_bytes(body)
        report["http"].append({"label": label, "url": url, "final_url": final, "http_status": status,
                               "checked_at_utc": now(), "path": path.relative_to(ROOT).as_posix(), **identity(path)})
        persist()
        require(status == 200, "HTTP check failed: " + url)
        return body

    persist()
    try:
        version = json.loads(fetch("version", "https://crates.io/api/v1/crates/lingose/0.1.0"))["version"]
        index = [json.loads(line) for line in fetch("index", "https://index.crates.io/li/ng/lingose").splitlines()]
        index_entry = next(row for row in index if row["vers"] == "0.1.0")
        require(version["checksum"] == index_entry["cksum"] == expected and not version["yanked"] and not index_entry["yanked"], "Published identity changed")
        report["published_version"] = {key: version[key] for key in ("num", "checksum", "crate_size", "yanked", "published_by")}
        report["current_toolchain"] = run("current-rustc", ["rustc", "-Vv"]).stdout.decode("utf-8").strip()
        report["current_cargo"] = run("current-cargo", ["cargo", "-V"]).stdout.decode("utf-8").strip()
        run("registry-fetch", ["cargo", "fetch"])
        lock_before = identity(consumer / "Cargo.lock")
        lock = tomllib.loads((consumer / "Cargo.lock").read_text(encoding="utf-8"))
        locked = next(row for row in lock["package"] if row["name"] == "lingose")
        require(locked["version"] == "0.1.0" and locked["source"] == REGISTRY and locked["checksum"] == expected, "Lock does not identify the public crate")
        metadata = json.loads(run("registry-metadata", ["cargo", "metadata", "--offline", "--locked", "--format-version", "1"]).stdout)
        lingose = check_metadata(metadata, isolated)
        require(lingose["homepage"] == "https://lingose.com/" and lingose["repository"] == "https://github.com/englishword", "Wrong distributed links")
        cached = list((cargo_home / "registry/cache").glob("*/lingose-0.1.0.crate"))
        require(len(cached) == 1 and identity(cached[0])["sha256"] == expected, "Fresh Cargo download checksum mismatch")
        require(cached[0].stat().st_size == version["crate_size"], "Fresh Cargo download size mismatch")
        source = Path(lingose["manifest_path"]).parent
        with tarfile.open(cached[0], "r:gz") as archive:
            for member in archive.getmembers():
                require(member.isfile() and member.name.startswith("lingose-0.1.0/"), "Unexpected registry archive entry")
                relative = Path(member.name).relative_to("lingose-0.1.0")
                require(".." not in relative.parts, "Unsafe registry archive path")
                stream = archive.extractfile(member)
                require(stream is not None and (source / relative).read_bytes() == stream.read(), "Registry unpacked source differs: " + str(relative))
        report["registry_resolution"] = {"source": lingose["source"], "manifest_path": lingose["manifest_path"],
                                         "lock_package": locked, "cached_archive": {"path": str(cached[0]), **identity(cached[0])},
                                         "all_source_paths_confined": True, "all_transitive_dependencies_from_crates_io": True,
                                         "unpacked_source_matches_download": True,
                                         "packages": [{"name": row["name"], "version": row["version"], "source": row["source"], "manifest_path": row["manifest_path"]} for row in metadata["packages"]]}
        registry_before = {path.relative_to(cargo_home / "registry").as_posix(): identity(path)
                           for path in (cargo_home / "registry").rglob("*")
                           if path.is_file() and ("/src/" in path.as_posix() or path.suffix == ".crate")}
        run("online-release-build", ["cargo", "build", "--locked", "--release"])
        outputs = []
        variants = [("online", environment, []), ("offline-current", environment.copy(), []), ("offline-minimum", environment.copy(), ["rustup", "run", "1.85.0-x86_64-pc-windows-msvc"])]
        runtime_environment = {key: os.environ[key] for key in ("SystemRoot", "SystemDrive", "ComSpec", "PATHEXT", "OS") if key in os.environ}
        runtime_environment["PATH"] = str(Path(os.environ["SystemRoot"]) / "System32")
        runtime_environment["TEMP"] = runtime_environment["TMP"] = str(runtime)
        runtime_environment["CARGO_HOME"] = str(isolated / "runtime-empty-home")
        for label, env, prefix in variants:
            if label != "online":
                env["CARGO_TARGET_DIR"] = str(isolated / (label + "-target"))
                env["CARGO_NET_OFFLINE"] = "true"
                if label == "offline-minimum":
                    env["RUSTUP_HOME"] = str(ROOT / ".local/p52-rustup-home")
                    report["minimum_toolchain"] = run("minimum-rustc", prefix + ["rustc", "-Vv"], env).stdout.decode("utf-8").strip()
                require(not Path(env["CARGO_TARGET_DIR"]).exists(), "Offline build target was not fresh")
                run(label + "-release-build", prefix + ["cargo", "build", "--offline", "--locked", "--release"], env)
            binary = Path(env["CARGO_TARGET_DIR"]) / "release/lingose-registry-consumer.exe"
            standalone = runtime / (label + ".exe")
            shutil.copyfile(binary, standalone)
            output = run(label + "-standalone-runtime", [str(standalone)], runtime_environment, runtime).stdout
            require(b"18 public functions" in output, "Missing consumer success marker")
            outputs.append(output)
        require(outputs[0] == outputs[1] == outputs[2], "Consumer outputs differ")
        require(identity(consumer / "Cargo.lock") == lock_before, "Consumer lock changed after fetch")
        require(all(identity(cargo_home / "registry" / name) == record for name, record in registry_before.items()), "Registry sources or archives changed")
        require(all(path.suffix == ".exe" for path in runtime.iterdir()) and len(list(runtime.iterdir())) == 3, "Unexpected runtime data")
        require(not any((isolated / "runtime-empty-home").iterdir()), "Runtime used Cargo home")
        require(not any(cargo_home.glob("credentials*")) and not any(cargo_home.glob("config*")), "Credentials/config entered fresh Cargo home")
        require(all(identity(ROOT / name) == record for name, record in protected.items()), "Protected distribution input changed")
        require(all(identity(ROOT / name) == record for name, record in histories.items()), "Historical report changed")
        report["consumer"] = {"public_entries": FUNCTIONS, "all_18_entries_passed": True,
                              "runs": [row[0] for row in variants], "outputs_identical": True,
                              "runtime_files": {path.name: identity(path) for path in runtime.iterdir()},
                              "runtime_environment": runtime_environment, "runtime_cargo_home_empty": True,
                              "registry_cache_credentials_or_config_absent": True,
                              "registry_source_and_archive_files_unchanged": len(registry_before),
                              "consumer_lock": lock_before, "offline_targets_initially_absent": True,
                              "scope": "Fixed Python-baseline literal smoke; full CET4 membership/boundaries, not a new full differential. Resource errors are synthetic public variants, not corruption injection."}
        pages = [("website", "https://lingose.com/"), ("github", "https://github.com/englishword"),
                 ("docs-home", "https://docs.rs/lingose/0.1.0/lingose/"), ("docs-crate", "https://docs.rs/crate/lingose/0.1.0"),
                 ("docs-builds", "https://docs.rs/crate/lingose/0.1.0/builds")]
        bodies = {label: fetch(label, url).decode("utf-8") for label, url in pages}
        require("IPSM" in bodies["website"] and "englishword" in bodies["github"], "Wrong website/profile")
        for name in FUNCTIONS:
            if name.isupper():
                require('id="reexport.' + name + '"' in bodies["docs-home"], "Missing documented uppercase alias: " + name)
            else:
                body = fetch("docs-" + name, "https://docs.rs/lingose/0.1.0/lingose/fn." + name + ".html").decode("utf-8")
                require("pub fn " in re.sub("<[^>]+>", "", body), "Missing function declaration: " + name)
        require("https://lingose.com/" in bodies["docs-home"] and "https://github.com/englishword" in bodies["docs-home"], "Published documentation links missing")
        report["documentation"] = {"all_18_entries_reachable": True, "homepage_and_github_reachable": True,
                                   "scope": "HTTP/content verification; no browser rendering or unrelated dynamic GitHub modules claimed"}
        report.update(status="registry_consumer_accepted", finished_at_utc=now(),
                      protected_inputs_unchanged=True, historical_records_unchanged=True)
        persist()
        print("P6.3 accepted; receipt " + str(receipt.relative_to(ROOT) / "report.json"), flush=True)
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error), failed_at_utc=now())
        persist()
        raise


if __name__ == "__main__":
    main()
