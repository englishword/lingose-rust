"""CLI6.5: fresh crates.io installs and final private Release runtime acceptance.

Read-only remote operations; never publishes, copies credentials or seeds caches.
Each invocation preserves a new receipt and two independent external Cargo homes.
The 0.1.0 consumer and its evidence are deliberately not used or changed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
import urllib.request
import uuid
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_cli_package import cli_smoke

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "registry+https://github.com/rust-lang/crates.io-index"
REPOSITORY = "englishword/lingose-rust"
EXPECTED = {
    "lingose": "91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5",
    "lingose-cli": "3f2e31e77ac7bdcedecb90871597d9821f60119f437be9a2cd7c523faa894490",
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(path):
    data = Path(path).read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def clean_environment(home, target):
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("CARGO_", "LINGOSE_")) or key in (
            "RUSTFLAGS", "RUSTDOCFLAGS", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER",
            "RUSTC", "RUSTDOC", "RUSTUP_TOOLCHAIN",
        ):
            env.pop(key)
    env.update(CARGO_HOME=str(home), CARGO_TARGET_DIR=str(target), CARGO_TERM_COLOR="never")
    return env


def main():
    require(platform.system() == "Windows" and platform.machine().lower() in ("amd64", "x86_64"),
            "This final runtime acceptance is scoped to native Windows x86_64")
    tag = uuid.uuid4().hex[:12]
    out = ROOT / ".local" / ("cli65-" + tag)
    out.mkdir(parents=True)
    logs = out / "logs"
    logs.mkdir()
    isolated = Path(tempfile.mkdtemp(prefix="lingose-cli65-")).resolve()
    require(not isolated.is_relative_to(ROOT), "Isolation must be outside checkout")
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    protected = {name: identity(ROOT / name) for name in tracked if name}
    inputs = {name: identity(ROOT / name) for name in (
        "tools/check_registry_consumer_020.py", "tools/package_consumer_020.rs",
        "tools/check_cli_package.py", "docs/cli-github-release-publication-verification.json",
    )}
    shutil.copyfile(__file__, out / Path(__file__).name)
    report = {
        "phase": "CLI6.5", "status": "running", "started_at_utc": now(),
        "base_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
        "platform": platform.platform(), "machine": platform.machine(),
        "receipt_directory": out.relative_to(ROOT).as_posix(), "isolation_directory": str(isolated),
        "inputs": inputs, "commands": [], "http": [], "registry": {},
        "protected_inputs_before": protected,
        "cache_policy": "Two initially empty Cargo homes; no config, credentials, lockfile or cache copied",
        "runtime_network_sandbox": False,
        "scope": "Windows final Release runtime; other platforms retain separately identified CI candidate runtime evidence",
    }

    def save():
        (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    def run(label, argv, cwd=isolated, env=None, stdin=None, expected=0):
        argv = [str(value) for value in argv]
        require("publish" not in argv, "Publishing is forbidden")
        print("Running " + label, flush=True)
        started = time.perf_counter()
        row = {"label": label, "argv": argv, "cwd": str(cwd), "expected_exit_code": expected,
               "started_at_utc": now(), "passed": False}
        report["commands"].append(row)
        save()
        try:
            value = subprocess.run(argv, cwd=cwd, env=env, input=stdin, capture_output=True, timeout=900)
        except subprocess.TimeoutExpired as error:
            value = subprocess.CompletedProcess(argv, None, error.stdout or b"", error.stderr or b"")
            row["timed_out"] = True
        row.update(exit_code=value.returncode, elapsed_seconds=round(time.perf_counter() - started, 6))
        for stream in ("stdout", "stderr"):
            path = logs / (label + "." + stream + ".log")
            path.write_bytes(getattr(value, stream))
            row[stream] = {"file": path.relative_to(ROOT).as_posix(), **identity(path)}
        save()
        require(value.returncode == expected, "Command failed: " + label + "; inspect retained logs")
        row["passed"] = True
        save()
        return value

    def fetch(label, url):
        request = urllib.request.Request(url, headers={"User-Agent": "Lingose-CLI6.5-registry-verification/0.2.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            body = response.read()
            require(response.status == 200, "HTTP status: " + label)
        path = out / (label + ".body")
        path.write_bytes(body)
        report["http"].append({"label": label, "url": url, "checked_at_utc": now(),
                               "file": path.relative_to(ROOT).as_posix(), **identity(path)})
        save()
        return body

    def gh(label, endpoint):
        return json.loads(run(label, ["gh", "api", f"repos/{REPOSITORY}/{endpoint}".rstrip("/")]).stdout)

    def audit_registry(home, name):
        archives = list((home / "registry/cache").glob(f"*/{name}-0.2.0.crate"))
        require(len(archives) == 1, "Expected one fresh registry archive: " + name)
        archive = archives[0]
        require(identity(archive)["sha256"] == EXPECTED[name], "Cargo archive identity differs")
        sources = list((home / "registry/src").glob(f"*/{name}-0.2.0"))
        require(len(sources) == 1, "Missing fresh registry source")
        source = sources[0]
        with tarfile.open(archive, "r:gz") as packed:
            members = packed.getmembers()
            for member in members:
                require(member.isfile() and member.name.startswith(name + "-0.2.0/"), "Invalid crate member")
                rel = Path(member.name).relative_to(name + "-0.2.0")
                require(".." not in rel.parts, "Unsafe crate member")
                require((source / rel).read_bytes() == packed.extractfile(member).read(), "Unpacked source differs")
        manifest = tomllib.loads((source / "Cargo.toml").read_text(encoding="utf-8"))
        require(manifest["package"]["homepage"] == "https://lingose.com/" and
                manifest["package"]["repository"] == "https://github.com/" + REPOSITORY, "Distributed links differ")
        report["registry"].setdefault(name, {})[str(home)] = {
            "archive": {"file": str(archive), **identity(archive)}, "members": len(members),
            "source": str(source), "all_unpacked_bytes_match_archive": True,
        }
        save()
        return source

    def audit_metadata(label, project, home, env, local_name):
        data = json.loads(run(label, ["cargo", "metadata", "--offline", "--locked", "--format-version", "1"], project, env).stdout)
        require(Path(data["workspace_root"]).resolve() == project.resolve(), "Foreign workspace")
        for package in data["packages"]:
            path = Path(package["manifest_path"]).resolve()
            if package["name"] == local_name:
                require(path == (project / "Cargo.toml").resolve(), "Wrong metadata root")
            else:
                require(package["source"] == REGISTRY and path.is_relative_to((home / "registry/src").resolve()),
                        "Non-registry or borrowed source: " + package["name"])
            require(not any(dep.get("path") for dep in package["dependencies"]), "Path dependency present")
        lib = next(package for package in data["packages"] if package["name"] == "lingose")
        require(lib["version"] == "0.2.0" and lib["source"] == REGISTRY, "Incorrect library dependency")
        lock = tomllib.loads((project / "Cargo.lock").read_text(encoding="utf-8"))
        for package in lock["package"]:
            if package["name"] != local_name:
                require(package["source"] == REGISTRY, "Non-registry lock entry")
            if package["name"] in EXPECTED and package["name"] != local_name:
                require(package["version"] == "0.2.0" and package["checksum"] == EXPECTED[package["name"]], "Lock checksum differs")
        return {"packages": [{key: p[key] for key in ("name", "version", "source", "manifest_path")} for p in data["packages"]],
                "all_transitive_sources_confined": True, "path_dependencies_absent": True,
                "lock": identity(project / "Cargo.lock")}

    save()
    try:
        for name, checksum in EXPECTED.items():
            version = json.loads(fetch(name + "-api", f"https://crates.io/api/v1/crates/{name}/0.2.0"))["version"]
            index = [json.loads(line) for line in fetch(name + "-index", "https://index.crates.io/li/ng/" + name).splitlines()]
            entry = next(row for row in index if row["vers"] == "0.2.0")
            require(version["checksum"] == entry["cksum"] == checksum and not version["yanked"] and not entry["yanked"], "Published version changed")
            report["registry"][name] = {"version": {key: version[key] for key in ("num", "checksum", "crate_size", "yanked", "published_by")}}
        prior = json.loads((ROOT / "docs/cli-github-release-publication-verification.json").read_bytes())
        repo = gh("repository", "")
        release = gh("release", "releases/tags/v0.2.0")
        ref = gh("tag-ref", "git/ref/tags/v0.2.0")
        tag_object = gh("tag-object", "git/tags/" + ref["object"]["sha"])
        require(repo["private"] is True, "Repository visibility changed")
        require(ref["object"]["type"] == "tag" and ref["object"]["sha"] == prior["tag"]["object_sha"] and
                tag_object["object"]["sha"] == prior["tag"]["commit"], "Tag changed")
        require(release["id"] == prior["release"]["id"] and release["draft"] is False and
                release["prerelease"] is False and release["published_at"] == prior["release"]["published_at"], "Release identity changed")
        require({a["name"] for a in release["assets"]} == set(prior["distribution"]), "Release assets changed")
        downloads = ROOT / ".local/cli64-final-39114174841/release-downloads"
        assets = []
        for asset in release["assets"]:
            name = asset["name"]
            expected = prior["distribution"][name]
            previous_asset = next(a for a in prior["release"]["assets"] if a["name"] == name)
            require(asset["id"] == previous_asset["id"] and asset["state"] == "uploaded" and
                    asset["size"] == expected["bytes"] and asset["digest"] == "sha256:" + expected["sha256"], "Remote asset changed")
            require(identity(downloads / name) == expected, "Previously authenticated Release download changed")
            assets.append({key: asset[key] for key in ("id", "name", "size", "digest")})
        checksums = dict(line.split("  ", 1)[::-1] for line in (downloads / "SHA256SUMS").read_text().splitlines())
        require(checksums == {name: row["sha256"] for name, row in prior["distribution"].items() if name != "SHA256SUMS"}, "Checksum manifest differs")
        report["release"] = {"id": release["id"], "url": release["html_url"], "private": True,
            "tag": prior["tag"], "assets": assets, "checked_at_utc": now(),
            "download_policy": "Refreshed authenticated remote identities; reused and rehashed six authenticated final Release downloads",
            "other_platforms": [{key: row[key] for key in ("target", "platform", "build_smoke", "downloaded_native_smoke")} for row in prior["targets"]],
            "other_platform_scope": "Earlier CI candidate archives, byte-identical to final Release; not final Release runtime on these hosts"}
        report["rustc"] = run("rustc", ["rustc", "-Vv"]).stdout.decode().strip()
        report["cargo"] = run("cargo", ["cargo", "-V"]).stdout.decode().strip()
        require("host: x86_64-pc-windows-msvc" in report["rustc"], "Unexpected Rust host")

        consumer = isolated / "consumer"
        (consumer / "src").mkdir(parents=True)
        manifest = ('[package]\nname="lingose-registry-consumer-020"\nversion="0.0.0"\nedition="2024"\n'
                    'rust-version="1.85"\npublish=false\n[dependencies]\nlingose="=0.2.0"\n[workspace]\nresolver="3"\n')
        (consumer / "Cargo.toml").write_text(manifest, encoding="utf-8", newline="\n")
        shutil.copyfile(ROOT / "tools/package_consumer_020.rs", consumer / "src/main.rs")
        lib_home, cli_home = isolated / "library-cargo-home", isolated / "cli-cargo-home"
        for home in (lib_home, cli_home):
            home.mkdir()
            require(not any(home.iterdir()), "Cache not initially empty")
        lib_env = clean_environment(lib_home, isolated / "library-online-target")
        run("library-fetch", ["cargo", "fetch"], consumer, lib_env)
        audit_registry(lib_home, "lingose")
        lib_resolution = audit_metadata("library-metadata", consumer, lib_home, lib_env, "lingose-registry-consumer-020")
        run("library-online-build", ["cargo", "build", "--release", "--locked"], consumer, lib_env)
        offline_lib_env = clean_environment(lib_home, isolated / "library-offline-target")
        offline_lib_env["CARGO_NET_OFFLINE"] = "true"
        require(not Path(offline_lib_env["CARGO_TARGET_DIR"]).exists(), "Offline target reused")
        run("library-offline-build", ["cargo", "build", "--release", "--offline", "--locked"], consumer, offline_lib_env)
        require(identity(consumer / "Cargo.lock") == lib_resolution["lock"], "Consumer lock changed")
        report["library_consumer"] = {"manifest": identity(consumer / "Cargo.toml"), "resolution": lib_resolution,
                                      "public_functions": 18, "runtime_scope": "Pinned literals, full CET4 membership, Unicode, thresholds, errors; no new full differential"}

        cli_env = clean_environment(cli_home, isolated / "cli-online-target")
        run("cli-registry-install", ["cargo", "install", "lingose-cli", "--version", "0.2.0", "--locked", "--root", isolated / "online-install"], isolated, cli_env)
        cli_source = audit_registry(cli_home, "lingose-cli")
        audit_registry(cli_home, "lingose")
        # Install fetches the host closure; metadata also inspects dependencies
        # for other targets. Prepare that closure online before offline checks.
        run("cli-metadata-fetch", ["cargo", "fetch", "--locked"], cli_source, cli_env)
        cli_resolution = audit_metadata("cli-metadata", cli_source, cli_home, cli_env, "lingose-cli")
        offline_cli_env = clean_environment(cli_home, isolated / "cli-offline-target")
        offline_cli_env["CARGO_NET_OFFLINE"] = "true"
        require(not Path(offline_cli_env["CARGO_TARGET_DIR"]).exists(), "Offline CLI target reused")
        run("cli-offline-registry-install", ["cargo", "install", "lingose-cli", "--version", "0.2.0", "--locked", "--offline", "--root", isolated / "offline-install"], isolated, offline_cli_env)
        for variant in ("online", "offline"):
            installed = json.loads((isolated / (variant + "-install") / ".crates2.json").read_bytes())
            require(list(installed["installs"]) == ["lingose-cli 0.2.0 (" + REGISTRY + ")"], "Install did not come from crates.io")
        require(identity(cli_source / "Cargo.lock") == cli_resolution["lock"], "CLI lock changed")
        report["cli_install"] = {"resolution": cli_resolution, "online_and_offline_registry_names_verified": True,
                                  "cases_per_binary": 25, "fresh_offline_target": True}

        # Hide both complete build environments at their original paths before
        # running. Keep only executable copies, OS libraries and generated test I/O.
        runtime = isolated / "runtime"
        runtime.mkdir()
        binaries = {}
        for variant in ("online", "offline"):
            for kind, source in (("library", isolated / f"library-{variant}-target/release/lingose-registry-consumer-020.exe"),
                                 ("cli", isolated / f"{variant}-install/bin/lingose.exe")):
                destination = runtime / f"{kind}-{variant}.exe"
                shutil.copyfile(source, destination)
                binaries[kind + "-" + variant] = identity(destination)
        windows = next(row for row in prior["targets"] if row["target"] == "x86_64-pc-windows-msvc")
        with zipfile.ZipFile(downloads / windows["archive"]["file"]) as packed:
            members = [name for name in packed.namelist() if name.endswith("/lingose.exe")]
            require(len(members) == 1, "Expected one Windows Release executable")
            (runtime / "release.exe").write_bytes(packed.read(members[0]))
        require(identity(runtime / "release.exe") == {key: windows["binary"][key] for key in ("bytes", "sha256")}, "Release binary differs")
        binaries["release"] = identity(runtime / "release.exe")
        hidden = []
        for path in list(isolated.iterdir()):
            if path != runtime:
                moved = path.with_name(path.name + "-unavailable")
                path.rename(moved)
                hidden.append(str(path))
        empty_home = runtime / "empty-cargo-home"
        empty_home.mkdir()
        runtime_env = {key: os.environ[key] for key in ("SystemRoot", "SystemDrive", "ComSpec", "PATHEXT", "OS") if key in os.environ}
        runtime_env.update(PATH=str(Path(os.environ["SystemRoot"]) / "System32"), TEMP=str(runtime), TMP=str(runtime),
                           HOME=str(runtime), USERPROFILE=str(runtime), CARGO_HOME=str(empty_home))
        outputs = []
        for variant in ("online", "offline"):
            result = run("library-" + variant + "-runtime", [runtime / f"library-{variant}.exe"], runtime, runtime_env)
            require(b"18 public functions" in result.stdout and result.stderr == b"", "Consumer did not pass")
            outputs.append(result.stdout)
        require(outputs[0] == outputs[1], "Consumer results differ")
        for label in ("cli-online", "cli-offline", "release"):
            cli_smoke(label, runtime / (label + ".exe"), runtime, runtime_env, run)
        require(not any(empty_home.iterdir()), "Runtime used Cargo home")
        require({path.name for path in runtime.iterdir()} == {name + ".exe" for name in binaries} | {"empty-cargo-home"}, "Unexpected runtime data remains")
        for home in (lib_home, cli_home):
            moved = home.with_name(home.name + "-unavailable")
            require(not any(moved.glob("config*")) and not any(moved.glob("credentials*")), "Config or credentials entered Cargo home")
        require(all(identity(ROOT / name) == record for name, record in protected.items()), "Pre-existing tracked file changed")
        report["runtime"] = {"binaries": binaries, "cwd": str(runtime), "environment": runtime_env,
            "build_paths_hidden": hidden, "cargo_home_remained_empty": True,
            "library_runs_passed": 2, "cli_scenarios_passed": 75, "release_scenarios_passed": 25,
            "external_lexicon_or_language_runtime_provided": False, "network_disabled": False}
        report.update(status="registry_and_release_accepted", finished_at_utc=now(),
                      protected_tracked_files_unchanged=len(protected), acceptance={"passed": True, "failures": []})
        save()
        print("CLI6.5 accepted: " + str(out.relative_to(ROOT) / "report.json"), flush=True)
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error), failed_at_utc=now())
        save()
        raise


if __name__ == "__main__":
    main()
