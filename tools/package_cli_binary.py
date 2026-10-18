"""CLI5.2 deterministic archives and native downloaded-archive verification.

Only Python's standard library is required. Packaging reads already prepared
Cargo metadata offline; archive verification needs neither Cargo nor a lexicon.
No command creates a GitHub Release or uploads to a package registry.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import subprocess
import tarfile
import tempfile
import tomllib
import zipfile

from binary_format import inspect_binary
import check_cli_release as native

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.0"
SLUGS = {
    "x86_64-pc-windows-msvc": "windows-x86_64",
    "x86_64-unknown-linux-gnu": "linux-x86_64",
    "aarch64-unknown-linux-gnu": "linux-aarch64",
    "x86_64-apple-darwin": "macos-x86_64",
    "aarch64-apple-darwin": "macos-aarch64",
}
require = native.require


def record(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def stem(target):
    return f"lingose-v{VERSION}-{SLUGS[target]}"


def archive_name(target):
    return stem(target) + (".zip" if "windows" in target else ".tar.gz")


def binary_name(target):
    return "lingose.exe" if "windows" in target else "lingose"


def catalog():
    value = json.loads((ROOT / "release/notices.json").read_bytes())
    require(value["format_version"] == 1 and value["rust_version"] == "1.93.1", "Notice format/toolchain mismatch")
    return value


def dependencies(value, target):
    return [{**value["packages"][row["package"]], "features": row["features"]}
            for row in value["targets"][target]]


def materials(target):
    value = catalog()
    names = list(value["common_files"])
    for package in dependencies(value, target):
        names += package["license_files"]
    result = {}
    for name in names:
        expected = value["files"][name]
        data = (ROOT / expected["snapshot"]).read_bytes()
        require(record(data) == {key: expected[key] for key in ("bytes", "sha256")}, f"Notice drift: {name}")
        result[name] = data
    for name in ("README.md", "SOURCES.md"):
        result[name] = (ROOT / "release" / name).read_bytes()
    return result


def packaging_inputs():
    paths = list((ROOT / "release").rglob("*"))
    paths += [ROOT / name for name in (".gitattributes", "Cargo.lock", ".github/workflows/cli-release.yml",
                                      "tools/package_cli_binary.py", "tools/check_cli_release.py", "tools/binary_format.py")]
    return {path.relative_to(ROOT).as_posix(): record(path.read_bytes()) for path in sorted(paths) if path.is_file()}


def check_dependency_notices(target):
    value = catalog()
    metadata = json.loads(subprocess.check_output(
        ["cargo", "metadata", "--offline", "--locked", "--format-version", "1", "--filter-platform", target], cwd=ROOT))
    nodes = {row["id"]: row for row in metadata["resolve"]["nodes"]}
    locked = {(row["name"], row["version"]): row for row in
              tomllib.loads((ROOT / "Cargo.lock").read_text(encoding="utf-8"))["package"]}
    actual = []
    for package in metadata["packages"]:
        if package["source"] is None:
            continue
        key = package["name"] + "-" + package["version"]
        require(key in value["packages"], f"Missing dependency notice: {key}")
        expected = value["packages"][key]
        require(package["license"] == expected["license"], f"License metadata drift: {key}")
        require(locked[package["name"], package["version"]]["checksum"] == expected["registry_archive_sha256"],
                f"Registry identity drift: {key}")
        for name in expected["license_files"]:
            source = Path(package["manifest_path"]).parent / PurePosixPath(name).name
            require(source.read_bytes() == (ROOT / value["files"][name]["snapshot"]).read_bytes(),
                    f"Cached dependency notice differs: {name}")
        actual.append({"package": key, "features": nodes[package["id"]]["features"]})
    require(sorted(actual, key=lambda row: row["package"]) == value["targets"][target], "Dependency graph/features drift")
    for row in value["files"].values():
        source = row["origin"].get("repository_path")
        if source:
            require(record((ROOT / source).read_bytes()) == {key: row[key] for key in ("bytes", "sha256")},
                    f"Protected source notice changed: {source}")


def write_archive(target, files, epoch):
    output = io.BytesIO()
    if "windows" in target:
        date = datetime.fromtimestamp(epoch, timezone.utc)
        timestamp = (date.year, date.month, date.day, date.hour, date.minute, date.second // 2 * 2)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, (data, mode) in sorted(files.items()):
                item = zipfile.ZipInfo(stem(target) + "/" + name, timestamp)
                item.create_system = 3
                item.external_attr = (stat.S_IFREG | mode) << 16
                item.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(item, data, compresslevel=9)
    else:
        with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=epoch, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
                for name, (data, mode) in sorted(files.items()):
                    item = tarfile.TarInfo(stem(target) + "/" + name)
                    item.size, item.mode, item.mtime = len(data), mode, epoch
                    item.uid = item.gid = 0
                    item.uname = item.gname = ""
                    archive.addfile(item, io.BytesIO(data))
    return output.getvalue()


def safe_member(name, target):
    require("\\" not in name and ":" not in name and "\0" not in name, "Unsafe archive member")
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(part not in ("", ".", "..") for part in name.split("/")), "Unsafe archive path")
    require(len(path.parts) > 1 and path.parts[0] == stem(target), "Wrong archive root")
    return PurePosixPath(*path.parts[1:]).as_posix()


def read_archive(data, target):
    files, total = {}, 0

    def add(name, content, size, mode, regular):
        nonlocal total
        relative = safe_member(name, target)
        require(regular and relative not in files, "Non-regular or duplicate archive member")
        total += size
        require(len(files) < 200 and total <= 32 * 1024 * 1024, "Archive exceeds expected bounds")
        require(mode == (0o755 if relative == binary_name(target) else 0o644), "Incorrect archive permissions")
        value = content()
        require(len(value) == size, "Archive size differs")
        files[relative] = value, mode

    if "windows" in target:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for item in archive.infolist():
                mode = item.external_attr >> 16
                add(item.filename, lambda: archive.read(item), item.file_size, stat.S_IMODE(mode), stat.S_ISREG(mode))
    else:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            for item in archive:
                add(item.name, lambda: archive.extractfile(item).read(), item.size, item.mode, item.isfile())
    return files


def verify_contents(files, target, revision):
    manifest = json.loads(files["manifest.json"][0])
    require(manifest["version"] == VERSION and manifest["target"] == target
            and manifest["revision"] == revision and manifest["root"] == stem(target), "Archive identity differs")
    value = catalog()
    require(manifest["notice_catalog_sha256"] == record((ROOT / "release/notices.json").read_bytes())["sha256"],
            "Notice catalog identity differs")
    require(manifest["rust_version"] == value["rust_version"]
            and manifest["unresolved_provenance"] == value["unresolved_provenance"], "License/toolchain scope differs")
    require(manifest["dependencies"] == dependencies(value, target), "Archive dependency inventory differs")
    expected = materials(target)
    name = binary_name(target)
    require(set(files) == set(expected) | {name, "manifest.json"}, "Archive payload closure differs")
    require(set(manifest["files"]) == set(files) - {"manifest.json"}, "Manifest payload closure differs")
    for path, (content, mode) in files.items():
        if path != "manifest.json":
            require(manifest["files"][path] == {**record(content), "mode": mode}, f"Payload identity differs: {path}")
        if path in expected:
            require(content == expected[path], f"Required notice/instructions differ: {path}")
    metadata = inspect_binary(files[name][0])
    architecture = "aarch64" if target.startswith("aarch64") else "x86_64"
    binary_format = "PE" if "windows" in target else "ELF" if "linux" in target else "Mach-O"
    require(metadata["architecture"] == architecture and metadata["format"] == binary_format, "Binary target header differs")
    require(manifest["binary"] == {"file": name, **record(files[name][0]), **metadata}, "Binary metadata differs")
    return manifest


def checked_archive(path, target, revision):
    require(path.name == archive_name(target), "Archive filename differs")
    data = path.read_bytes()
    expected = f"{record(data)['sha256']}  {path.name}\n".encode("ascii")
    require(path.with_name(path.name + ".sha256").read_bytes() == expected, "Archive checksum differs")
    files = read_archive(data, target)
    return files, verify_contents(files, target, revision)


def package(args):
    report = json.loads(args.build_report.read_bytes())
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    require(report["status"] == "passed" and report["target"] == args.target and report["revision"] == revision,
            "Passed build report for current target/revision required")
    require(len(report["smoke"]) == 12 and all(row["passed"] for row in report["smoke"]), "Build smoke incomplete")
    require(report["runtime"]["mode"] == "native" and all(row["exit_code"] == 0 and not row["timed_out"]
            for row in report["commands"]), "Successful native build commands required")
    require(native.inputs() == report["inputs"], "Build inputs drifted before packaging")
    candidate = (args.build_report.parent / report["binary"]["file"]).resolve()
    require(candidate.is_relative_to(args.build_report.parent.resolve()), "Binary outside build evidence")
    binary = candidate.read_bytes()
    require(record(binary) == {key: report["binary"][key] for key in ("bytes", "sha256")}, "Candidate binary identity differs")
    before = packaging_inputs()
    check_dependency_notices(args.target)
    files = {name: (data, 0o644) for name, data in materials(args.target).items()}
    name = binary_name(args.target)
    files[name] = binary, 0o755
    value = catalog()
    manifest = {"version": VERSION, "target": args.target, "root": stem(args.target), "revision": revision,
                "rust_version": value["rust_version"], "notice_catalog_sha256": record((ROOT / "release/notices.json").read_bytes())["sha256"],
                "dependencies": dependencies(value, args.target), "unresolved_provenance": value["unresolved_provenance"],
                "binary": {"file": name, **record(binary), **inspect_binary(binary)},
                "files": {name: {**record(data), "mode": mode} for name, (data, mode) in sorted(files.items())}}
    files["manifest.json"] = json_bytes(manifest), 0o644
    verify_contents(files, args.target, revision)
    epoch = int(subprocess.check_output(["git", "show", "-s", "--format=%ct", "HEAD"], cwd=ROOT))
    data = write_archive(args.target, files, epoch)
    require(data == write_archive(args.target, files, epoch), "Repeated archive encoding is not deterministic")
    path = args.output / archive_name(args.target)
    path.write_bytes(data)
    path.with_name(path.name + ".sha256").write_bytes(f"{record(data)['sha256']}  {path.name}\n".encode("ascii"))
    checked_archive(path, args.target, revision)
    require(packaging_inputs() == before and native.inputs() == report["inputs"], "Inputs changed while packaging")
    return {"phase": "CLI5.2", "status": "passed", "stage": "package", "target": args.target, "revision": revision,
            "archive": {"file": path.name, **record(data)}, "binary": manifest["binary"], "members": len(files),
            "dependencies": manifest["dependencies"], "packaging_inputs": before, "archive_epoch": epoch,
            "repeated_archive_bytes_identical": True, "unresolved_provenance": value["unresolved_provenance"]}


def verify(args, report, save):
    system, architectures = native.TARGETS[args.target]
    require(platform.system() == system and platform.machine().lower() in architectures, "Native runtime target differs")
    if args.require_source_free_checkout:
        require(not (ROOT / "crates").exists() and not (ROOT / ".local").exists(),
                "Downloaded-archive job must exclude crates and local caches")
    files, manifest = checked_archive(args.archive.resolve(), args.target, args.revision)
    report.update({"phase": "CLI5.2", "stage": "downloaded-archive", "target": args.target,
                   "revision": args.revision, "archive": {"file": args.archive.name, **record(args.archive.read_bytes())},
                   "binary": manifest["binary"], "members": len(files), "smoke": [],
                   "platform": platform.platform(), "machine": platform.machine(),
                   "source_free_checkout_required": args.require_source_free_checkout,
                   "checkout_crates_present": (ROOT / "crates").exists(),
                   "runner": {key: os.environ.get(key) for key in ("RUNNER_OS", "RUNNER_ARCH", "ImageOS", "ImageVersion")}})
    save()
    with tempfile.TemporaryDirectory(prefix="lingose-cli52-extract-") as temporary:
        destination = Path(temporary).resolve()
        require(not destination.is_relative_to(ROOT), "Extraction must be outside checkout")
        for name, (data, mode) in files.items():
            path = destination / stem(args.target) / name
            require(path.resolve().is_relative_to(destination), "Unsafe extraction path")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(mode)
            if os.name != "nt":
                require(stat.S_IMODE(path.stat().st_mode) == mode, "Extracted permissions differ")
        executable = destination / stem(args.target) / binary_name(args.target)
        require(os.access(executable, os.X_OK), "Extracted binary is not executable")
        report["extraction"] = {"outside_checkout": True, "archive_modes_verified": True,
                                "extracted_posix_modes_verified": os.name != "nt",
                                "source_or_dictionary_files_supplied": False,
                                "method": "Extract verified payload, preserve modes, copy that executable to a separate binary-only runtime and run byte-exact smoke"}
        native.smoke(executable, report, save, file_cases=True)
    report["status"] = "passed"


def aggregate(args):
    rows = []
    for target in SLUGS:
        matches = list(args.packages.rglob(archive_name(target)))
        require(len(matches) == 1, f"Expected one archive: {target}")
        _, manifest = checked_archive(matches[0], target, args.revision)
        data = matches[0].read_bytes()
        (args.output / matches[0].name).write_bytes(data)
        rows.append({"file": matches[0].name, **record(data), "binary": manifest["binary"]})
    (args.output / "SHA256SUMS").write_bytes("".join(f"{row['sha256']}  {row['file']}\n"
        for row in sorted(rows, key=lambda row: row["file"])).encode("ascii"))
    return {"phase": "CLI5.2", "stage": "aggregate", "status": "passed", "revision": args.revision, "archives": rows,
            "checksums": record((args.output / "SHA256SUMS").read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("package", "verify", "aggregate"):
        command = sub.add_parser(name)
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--report", type=Path, required=True)
        if name != "aggregate":
            command.add_argument("--target", choices=SLUGS, required=True)
        if name == "package":
            command.add_argument("--build-report", type=Path, required=True)
        else:
            command.add_argument("--revision", required=True)
        if name == "verify":
            command.add_argument("--archive", type=Path, required=True)
            command.add_argument("--require-source-free-checkout", action="store_true")
        if name == "aggregate":
            command.add_argument("--packages", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    require(not args.report.exists(), "Use a fresh report path")
    if args.command != "verify":
        require(not list(args.output.iterdir()), "Use a fresh archive output directory")
    report = {"status": "running", "stage": args.command}

    def save():
        args.report.write_bytes(json_bytes(report))

    save()
    try:
        if args.command == "package":
            report = package(args)
        elif args.command == "verify":
            verify(args, report, save)
        else:
            report = aggregate(args)
    except Exception as error:
        report["status"] = "failed"
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        save()
    print(f"CLI5.2 {args.command}: passed; {args.report}")


if __name__ == "__main__":
    main()
