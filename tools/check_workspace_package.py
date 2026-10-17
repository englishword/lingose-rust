"""Inspect the current workspace library inventory, or audit a supplied archive.

The default/--list mode only runs Cargo's package --list: it creates no .crate,
does not run publish/dry-run, and permits the development publish=false guard.
--archive checks an existing archive; neither mode establishes isolated archive
consumption, registry readiness, licensing review, or publication acceptance.
The 0.1.0 tools and receipts are deliberately separate and remain historical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import tarfile
import tomllib
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
LIB_ROOT = REPO_ROOT / "crates/lingose"
REQUIRED = {
    "README.md", "LICENSE", "SOURCES.md", "data/lexicon.bin",
    "data/frequency.bin", "data/manifest.json", "data/SOURCES.json",
    "data/UPSTREAM-SOURCES.md", "data/LICENSE", "third_party/unicode/LICENSE.txt",
    "docs/rust-api.md", "docs/distribution-provenance.json",
}
GENERATED = {"Cargo.toml.orig", ".cargo_vcs_info.json"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def identity(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def safe_name(name):
    require(isinstance(name, str) and bool(name), "Empty package path")
    require("\\" not in name and ":" not in name and not name.startswith("/"),
            f"Unsafe package path: {name}")
    require(all(part not in ("", ".", "..") for part in name.split("/")),
            f"Unsafe package path: {name}")
    return name


def source_inventory(repo_root=REPO_ROOT, library_root=LIB_ROOT):
    """Return package-relative source identities without treating the repo as a crate.

    Cargo generates/normalizes Cargo.toml, Cargo.lock and optional VCS metadata.
    The lock's recorded identity is an input identity, not expected archive bytes.
    """
    repo_root, library_root = Path(repo_root).resolve(), Path(library_root).resolve()
    require(library_root.is_relative_to(repo_root), "Library escaped repository")
    manifest = tomllib.loads((library_root / "Cargo.toml").read_text(encoding="utf-8"))
    package = manifest["package"]
    require(package["name"] == "lingose" and isinstance(package["version"], str),
            "Wrong library package identity")
    require(package.get("build") is False, "Unexpected build script")
    names = {"Cargo.toml"}
    for pattern in package["include"]:
        pattern = pattern.removeprefix("/")
        safe_name(pattern)
        matches = list(library_root.glob(pattern))
        # pathlib's ** matches directories; Cargo's /** includes all files below.
        if pattern.endswith("/**"):
            matches = list((library_root / pattern[:-3]).rglob("*"))
        files = [path for path in matches if path.is_file()]
        require(bool(files), f"Missing included file(s): {pattern}")
        for path in files:
            require(not path.is_symlink() and path.resolve().is_relative_to(library_root),
                    f"Source escapes library: {path}")
            names.add(safe_name(path.relative_to(library_root).as_posix()))
    require(REQUIRED <= names, "Required data, notices or public documentation omitted")
    require(not (names & GENERATED), "Cargo-generated file explicitly included")
    inputs = {name: identity((library_root / name).read_bytes()) for name in sorted(names)}
    inputs["Cargo.lock"] = identity((repo_root / "Cargo.lock").read_bytes())
    return manifest, inputs


def check_listing(names, inputs):
    names = [name.replace("\\", "/") for name in names]
    require(len(names) == len(set(names)), "Duplicate Cargo package listing")
    for name in names:
        safe_name(name)
    expected = set(inputs) | {"Cargo.toml.orig"}
    require(set(names) in (expected, expected | {".cargo_vcs_info.json"}),
            "Cargo listing differs from explicit library inventory")
    return sorted(names)


def lock_key(row):
    return row["name"], row["version"], row.get("source"), row.get("checksum")


def dependency_keys(row, rows):
    result = set()
    for dependency in row.get("dependencies", []):
        fields = dependency.split()
        matches = [candidate for candidate in rows if candidate["name"] == fields[0]
                   and (len(fields) < 2 or candidate["version"] == fields[1])
                   and (len(fields) < 3 or candidate.get("source") == fields[2].strip("()"))]
        require(len(matches) == 1, f"Ambiguous/missing lock dependency: {dependency}")
        result.add(lock_key(matches[0]))
    return result


def check_lock(data, source_data, package):
    """Check the library dependency closure; workspace-only packages may be omitted."""
    actual = tomllib.loads(data.decode("utf-8"))["package"]
    source = tomllib.loads(source_data.decode("utf-8"))["package"]
    source_by_key = {lock_key(row): row for row in source}
    actual_by_key = {lock_key(row): row for row in actual}
    require(len(source_by_key) == len(source) and len(actual_by_key) == len(actual),
            "Duplicate lock package")
    root = (package["name"], package["version"], None, None)
    require(root in source_by_key, "Workspace lock lacks current library")
    required, pending = set(), [root]
    while pending:
        key = pending.pop()
        if key in required:
            continue
        required.add(key)
        pending.extend(dependency_keys(source_by_key[key], source) - required)
    require(set(actual_by_key) == required, "Archive lock differs from library dependency closure")
    for key, row in actual_by_key.items():
        require(dependency_keys(row, actual) == dependency_keys(source_by_key[key], source),
                f"Archive lock dependency graph differs: {key[0]}")


def check_manifest(data, source):
    manifest = tomllib.loads(data.decode("utf-8"))
    require(not ({"workspace", "patch", "replace"} & set(manifest)),
            "Workspace/override in normalized manifest")
    expected = source["package"]
    for name in ("name", "version", "edition", "rust-version", "authors", "license",
                 "readme", "homepage", "repository", "build", "include"):
        require(manifest["package"].get(name) == expected.get(name),
                f"Normalized package field differs: {name}")
    for name in ("dependencies", "build-dependencies", "dev-dependencies"):
        wanted = source.get(name, {})
        found = manifest.get(name, {})
        wanted = {key: {"version": value} if isinstance(value, str) else value
                  for key, value in wanted.items()}
        require(found == wanted, f"Normalized dependency declarations differ: {name}")

    def inspect(table):
        for name, value in table.items():
            if name.endswith("dependencies") and isinstance(value, dict):
                for dependency in value.values():
                    require(isinstance(dependency, dict) and
                            not ({"path", "git", "workspace"} & set(dependency)),
                            "Non-registry dependency in normalized manifest")
            elif isinstance(value, dict):
                inspect(value)
    inspect(manifest)
    return manifest


def check_payload(files):
    absolute = re.compile(rb"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/(?:Users|home|tmp)/")
    for name, data in files.items():
        require(not name.startswith(("tools/", "tasks/", ".local/", "target/")),
                f"Development file shipped: {name}")
        require(PurePosixPath(name).suffix not in (".sqlite", ".db", ".xlsx", ".csv", ".py", ".pyc"),
                f"Maintenance data/tool shipped: {name}")
        if not name.endswith(".bin"):
            require(not absolute.search(data), f"Absolute host path shipped: {name}")
            require(b"site-packages" not in data and b".local/" not in data and b".local\\" not in data,
                    f"Host cache/installation path shipped: {name}")
    links = []
    for name, data in files.items():
        if not name.endswith(".md"):
            continue
        for href in re.findall(r"\[[^\]]*\]\(([^)]+)\)", data.decode("utf-8")):
            href = href.strip().removeprefix("<").removesuffix(">")
            parsed = urlsplit(href)
            if parsed.scheme in ("https", "http", "mailto") or href.startswith(("#", "//")):
                continue
            require(not parsed.scheme and not parsed.netloc, f"Unsupported packaged link: {href}")
            target = unquote(parsed.path)
            require("\\" not in target and not target.startswith("/"), f"Unsafe packaged link: {href}")
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
            safe_name(target)
            require(target in files, f"Broken packaged link: {name} -> {href}")
            links.append({"source": name, "href": href, "target": target})
    return links


def audit_archive(path, repo_root=REPO_ROOT, library_root=LIB_ROOT):
    repo_root, library_root = Path(repo_root).resolve(), Path(library_root).resolve()
    source, inputs = source_inventory(repo_root, library_root)
    package = source["package"]
    prefix = f"{package['name']}-{package['version']}/"
    files = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            require(member.isfile() and member.name.startswith(prefix), "Unexpected archive entry type/root")
            name = safe_name(member.name[len(prefix):])
            require(name not in files, f"Duplicate archive path: {name}")
            stream = archive.extractfile(member)
            require(stream is not None, "Missing archive payload")
            files[name] = stream.read()
    check_listing(list(files), inputs)
    require(files["Cargo.toml.orig"] == (library_root / "Cargo.toml").read_bytes(),
            "Original library manifest differs")
    for name, record in inputs.items():
        if name not in ("Cargo.toml", "Cargo.lock"):
            require(identity(files[name]) == record, f"Archive input differs: {name}")
    check_manifest(files["Cargo.toml"], source)
    check_lock(files["Cargo.lock"], (repo_root / "Cargo.lock").read_bytes(), package)
    if ".cargo_vcs_info.json" in files:
        vcs = json.loads(files[".cargo_vcs_info.json"])
        require(vcs.get("path_in_vcs") == library_root.relative_to(repo_root).as_posix(),
                "VCS metadata library path differs")
        require(re.fullmatch(r"[0-9a-f]{40}", vcs["git"]["sha1"]) is not None,
                "Invalid VCS revision")
    links = check_payload(files)
    return files, links


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true", help="Read source inventory and Cargo package --list (default)")
    mode.add_argument("--archive", type=Path, help="Audit an existing current-library .crate; never create one")
    args = parser.parse_args()
    source, inputs = source_inventory()
    if args.archive:
        files, links = audit_archive(args.archive)
        result = {"mode": "existing-archive", "archive": identity(args.archive.read_bytes()),
                  "files": sorted(files), "local_links": links}
    else:
        command = ["cargo", "package", "--list", "-p", source["package"]["name"],
                   "--offline", "--locked", "--allow-dirty"]
        completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True,
                                   text=True, encoding="utf-8", check=True)
        result = {"mode": "inventory-only", "command": command,
                  "files": check_listing(completed.stdout.splitlines(), inputs)}
    result["package"] = {key: source["package"][key] for key in ("name", "version")}
    result["scope"] = "Inventory/archive structure only; no crate generation, independent consumption, dry-run or publication acceptance"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
