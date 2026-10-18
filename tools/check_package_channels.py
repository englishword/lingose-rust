"""CLI7 public asset/schema checks and installed-command smoke (no publishing).

Schema validation needs PyYAML/jsonschema; installed smoke uses only stdlib.
Use a fresh output directory to retain failed attempts separately.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://github.com/englishword/lingose-rust/releases/download/v0.2.0/"
WINDOWS = "lingose-v0.2.0-windows-x86_64.zip"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def identity(data):
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def fetch(url, destination, report):
    request = urllib.request.Request(url, headers={"User-Agent": "lingose-cli7-verification"})
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read()
        report["downloads"].append({"url": url, "status": response.status, **identity(data)})
    destination.write_bytes(data)
    return data


def preflight(output, report):
    import jsonschema
    import yaml

    report["downloads"] = []
    repo = json.loads(fetch("https://api.github.com/repos/englishword/lingose-rust", output / "repository.json", report))
    require(repo["private"] is False, "Repository is not public")
    release = json.loads(fetch("https://api.github.com/repos/englishword/lingose-rust/releases/tags/v0.2.0", output / "release.json", report))
    require(release["id"] == 416347193 and not release["draft"] and not release["prerelease"], "Release identity changed")
    sums = fetch(BASE + "SHA256SUMS", output / "SHA256SUMS", report).decode("ascii")
    expected = {name: sha for sha, name in (line.split() for line in sums.splitlines())}
    prior = json.loads((ROOT / "docs/cli-github-release-publication-verification.json").read_bytes())
    require(set(asset["name"] for asset in release["assets"]) == set(prior["distribution"]), "Release asset set changed")
    # Compare to the frozen publication and current API/checksum identities.
    report["assets"] = {}
    for asset in release["assets"]:
        name = asset["name"]
        data = fetch(BASE + name, output / name, report)
        value = identity(data)
        require(asset["digest"] == "sha256:" + value["sha256"], f"API digest differs: {name}")
        if name != "SHA256SUMS":
            require(expected[name] == value["sha256"], f"Checksum differs: {name}")
        require(value == prior["distribution"][name], f"Publication asset changed: {name}")
        report["assets"][name] = value
    require(set(expected) == set(report["assets"]) - {"SHA256SUMS"}, "Asset set differs")

    report["schemas"] = []
    manifests = ROOT / "packaging/winget/manifests/l/Lingose/Lingose/0.2.0"
    for path in sorted(manifests.glob("*.yaml")):
        value = yaml.safe_load(path.read_bytes())
        kind = value["ManifestType"]
        url = f"https://raw.githubusercontent.com/microsoft/winget-cli/master/schemas/JSON/manifests/v1.12.0/manifest.{kind}.1.12.0.json"
        schema = json.loads(fetch(url, output / f"winget-{kind}.json", report))
        jsonschema.validate(value, schema)
        report["schemas"].append(str(path.relative_to(ROOT)))
    installer = yaml.safe_load((manifests / "Lingose.Lingose.installer.yaml").read_bytes())
    require(installer["Installers"][0]["InstallerSha256"].lower() == expected[WINDOWS], "WinGet SHA differs")
    with zipfile.ZipFile(output / WINDOWS) as archive:
        require(installer["NestedInstallerFiles"][0]["RelativeFilePath"].replace("\\", "/") in archive.namelist(), "Missing nested executable")
    scoop = json.loads((ROOT / "bucket/lingose.json").read_bytes())
    schema = json.loads(fetch("https://raw.githubusercontent.com/ScoopInstaller/Scoop/master/schema.json", output / "scoop-schema.json", report))
    jsonschema.validate(scoop, schema)
    require(set(scoop["architecture"]) == {"64bit"}, "Unexpected Scoop architecture")
    require(scoop["architecture"]["64bit"]["hash"] == expected[WINDOWS], "Scoop SHA differs")
    auto = scoop["autoupdate"]["architecture"]["64bit"]
    require(auto["url"].replace("$version", scoop["version"]) == BASE + WINDOWS, "Scoop update URL differs")
    require(auto["extract_dir"].replace("$version", scoop["version"]) == scoop["architecture"]["64bit"]["extract_dir"], "Scoop update directory differs")
    require(auto["hash"]["url"].replace("$version", scoop["version"]) == BASE + "SHA256SUMS", "Scoop checksum URL differs")
    report["schemas"].append("bucket/lingose.json")
    choco = (ROOT / "packaging/chocolatey/tools/chocolateyInstall.ps1").read_text(encoding="utf-8")
    require(BASE + WINDOWS in choco and expected[WINDOWS] in choco, "Chocolatey URL/SHA differs")
    formula = (ROOT / "Formula/lingose.rb").read_text(encoding="utf-8")
    for slug in ("macos-aarch64", "macos-x86_64"):
        name = f"lingose-v0.2.0-{slug}.tar.gz"
        require(BASE + name in formula and expected[name] in formula, f"Homebrew URL/SHA differs: {slug}")
    report["repository"] = {key: repo[key] for key in ("id", "private", "visibility", "created_at", "stargazers_count", "forks_count")}
    report["release_id"] = release["id"]


def smoke(executable, report, save):
    executable = executable.absolute()
    require(executable.is_file(), f"Missing installed command: {executable}")
    report["smoke"] = []
    report["executable"] = str(executable)
    with tempfile.TemporaryDirectory(prefix="lingose-cli7-") as temporary:
        def invoke(name, args, *, stdin=b"", value=None, exact=None, code=0):
            result = subprocess.run([str(executable), *args], input=stdin, capture_output=True, cwd=temporary, timeout=60)
            report["smoke"].append({"name": name, "args": args, "exit_code": result.returncode,
                                    "stdout_hex": result.stdout.hex(), "stderr_hex": result.stderr.hex()})
            save()
            require(result.returncode == code, f"{name}: exit code differs")
            require(bool(result.stderr) == (code != 0), f"{name}: diagnostic differs")
            if value is not None:
                require(json.loads(result.stdout) == value, f"{name}: complete JSON differs")
            if exact is not None:
                require(result.stdout == exact, f"{name}: bytes differ")

        apple = {"word": "apple", "ipa": ["æpəl"], "ips": ["apple"], "ism": "app-le", "ipsm": ["app-le"], "root_lemma": "ap"}
        text, annotated = "Abandon the book.\r\n", "Åbando\u030an \u1e6bhe\u030a book.\r\n"
        invoke("version", ["--version"], exact=b"lingose 0.2.0\n")
        invoke("word", ["word", "apple", "--json"], value=apple)
        invoke("text", ["annotate", "--text", text], exact=annotated.encode())
        invoke("stdin-json", ["annotate", "--json"], stdin=text.encode(), value={"text": text, "annotate": annotated})
        invoke("skip-top", ["annotate", "--text", text, "--skip-top", "5062"], exact=text.encode())
        invoke("empty", ["annotate"], exact=b"")
        invoke("invalid-utf8", ["annotate"], stdin=b"\xff", exact=b"", code=1)
        invoke("usage", ["word"], exact=b"", code=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["preflight", "smoke"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--executable", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "report.json"
    require(not path.exists(), "Use a fresh evidence directory")
    report = {"phase": "CLI7", "mode": args.mode, "status": "running", "started_at": datetime.now(timezone.utc).isoformat(), "platform": platform.platform()}

    def save():
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    save()
    try:
        if args.mode == "preflight":
            preflight(args.output, report)
        else:
            require(args.executable is not None, "--executable required for smoke")
            smoke(args.executable, report, save)
        report["status"] = "passed"
    except Exception as error:
        report["status"], report["error"] = "failed", str(error)
        raise
    finally:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        save()
    print(f"CLI7 {args.mode}: passed ({path})")


if __name__ == "__main__":
    main()
