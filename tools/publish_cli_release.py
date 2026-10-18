"""Publish only the verified v0.2.0 tag; never replace a release or its assets.

Uses the runner's gh authentication without reading or logging credentials.
Creates a draft, downloads and checks every uploaded byte, then publishes it.
A failed/interrupted mutation requires remote inspection before recovery.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess

import package_cli_binary as package

REPOSITORY = "englishword/lingose-rust"
TAG = "v0.2.0"
require = package.require


def api(endpoint, *, method="GET", body=None, binary=False):
    command = ["gh", "api", endpoint, "--method", method]
    if body is not None:
        command += ["--input", "-"]
    if binary:
        command += ["-H", "Accept: application/octet-stream"]
    result = subprocess.run(command, input=None if body is None else package.json_bytes(body),
                            capture_output=True, check=True, timeout=180)
    return result.stdout if binary else json.loads(result.stdout)


def candidate(directory, revision):
    require(re.fullmatch(r"[0-9a-f]{40}", revision) is not None, "Full commit SHA required")
    names = {package.archive_name(target) for target in package.SLUGS} | {"SHA256SUMS"}
    require({path.name for path in directory.iterdir()} == names, "Expected exactly six distribution files")
    require(all(path.is_file() and not path.is_symlink() for path in directory.iterdir()), "Regular assets required")
    rows = {}
    for target in package.SLUGS:
        path = directory / package.archive_name(target)
        data = path.read_bytes()
        package.verify_contents(package.read_archive(data, target), target, revision)
        rows[path.name] = package.record(data)
    expected = "".join(f"{rows[name]['sha256']}  {name}\n" for name in sorted(rows)).encode("ascii")
    require((directory / "SHA256SUMS").read_bytes() == expected, "SHA256SUMS differs from candidates")
    rows["SHA256SUMS"] = package.record(expected)
    return rows


def release_identity(value, *, draft):
    require(value["tag_name"] == TAG and value["name"] == "Lingose 0.2.0"
            and value["draft"] is draft and value["prerelease"] is False, "Remote release identity differs")


def uploaded_assets(value, rows, destination):
    assets = value["assets"]
    require(len(assets) == len(rows) and {row["name"] for row in assets} == set(rows), "Remote asset set differs")
    result = []
    for asset in assets:
        expected = rows[asset["name"]]
        require(asset["state"] == "uploaded" and asset["size"] == expected["bytes"]
                and asset["digest"] == "sha256:" + expected["sha256"], "Remote asset metadata differs")
        data = api(f"repos/{REPOSITORY}/releases/assets/{asset['id']}", binary=True)
        require(package.record(data) == expected, "Downloaded release asset differs")
        (destination / asset["name"]).write_bytes(data)
        result.append({key: asset[key] for key in ("id", "name", "size", "digest", "browser_download_url")})
    return result


def publish(args, report, save):
    require(os.environ.get("GITHUB_REPOSITORY") == REPOSITORY
            and os.environ.get("GITHUB_EVENT_NAME") == "push"
            and os.environ.get("GITHUB_REF") == "refs/tags/" + TAG
            and os.environ.get("GITHUB_SHA") == args.revision, "Only the exact repository/tag push may publish")
    rows = candidate(args.assets, args.revision)
    notes = args.notes.read_text(encoding="utf-8")
    require("Lingose 0.2.0" in notes, "Versioned release notes required")
    repository = api(f"repos/{REPOSITORY}")
    require(repository["full_name"] == REPOSITORY and repository["visibility"] == "public",
            "Public distribution requires explicitly authorized public repository visibility")
    ref = api(f"repos/{REPOSITORY}/git/ref/tags/{TAG}")["object"]
    if ref["type"] == "tag":
        ref = api(f"repos/{REPOSITORY}/git/tags/{ref['sha']}")["object"]
    require(ref["type"] == "commit" and ref["sha"] == args.revision, "Remote tag commit differs")
    # Paginate, including drafts; no retry may overwrite an existing publication.
    page = 1
    while True:
        releases = api(f"repos/{REPOSITORY}/releases?per_page=100&page={page}")
        require(not any(value["tag_name"] == TAG for value in releases), "Release already exists; inspect remote state before recovery")
        if len(releases) < 100:
            break
        page += 1
    report.update({"candidate": rows, "repository_visibility": repository["visibility"],
                   "notes": package.record(args.notes.read_bytes()), "status": "creating-draft"})
    save()  # Durable intent before the first mutation.
    value = api(f"repos/{REPOSITORY}/releases", method="POST", body={
        "tag_name": TAG, "target_commitish": args.revision, "name": "Lingose 0.2.0",
        "body": notes, "draft": True, "prerelease": False})
    release_identity(value, draft=True)
    report.update({"release_id": value["id"], "status": "uploading"})
    save()
    subprocess.run(["gh", "release", "upload", TAG, "--repo", REPOSITORY,
                    *[str(args.assets / name) for name in sorted(rows)]], check=True, timeout=300)
    value = api(f"repos/{REPOSITORY}/releases/{value['id']}")
    release_identity(value, draft=True)
    report["assets"] = uploaded_assets(value, rows, args.output)
    # Verify the actual downloads, including notices and internal commit identity.
    require(candidate(args.output, args.revision) == rows, "Downloaded candidate payload differs")
    require(value["body"] == notes, "Remote release notes differ")
    report["status"] = "verified-draft"
    save()
    value = api(f"repos/{REPOSITORY}/releases/{value['id']}", method="PATCH", body={"draft": False, "make_latest": "true"})
    release_identity(value, draft=False)
    require(value["published_at"] is not None and value["body"] == notes, "Publication metadata differs")
    report.update({"status": "passed", "url": value["html_url"], "published_at": value["published_at"],
                   "completed_at": datetime.now(timezone.utc).isoformat()})
    save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--notes", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists() and not args.report.exists(), "Fresh download and report paths required")
    args.output.mkdir(parents=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    report = {"phase": "CLI6.4", "status": "preflight", "revision": args.revision,
              "repository": REPOSITORY, "tag": TAG, "run_id": os.environ.get("GITHUB_RUN_ID"),
              "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
              "started_at": datetime.now(timezone.utc).isoformat()}

    def save():
        args.report.write_bytes(package.json_bytes(report))

    save()
    try:
        publish(args, report, save)
    except Exception as error:
        report["status"] = "failed"
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        save()


if __name__ == "__main__":
    main()
