"""Freeze simple-query casing from the audited Python 3.12 / Unicode 15.0.

Development only: no imports of Lingose, database access, downloads, or writes to
the reference checkout. --write creates missing artifacts; neither mode replaces
existing different bytes. Runtime Rust consumes the generated static tables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import unicodedata


sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import ROOT, artifact_path, check_historical_generator
BASELINE = ROOT / "docs/reference-baseline.json"
BASELINE_SHA256 = "9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01"
LICENSE_SHA256 = "e7a93b009565cfce55919a381437ac4db883e9da2126fa28b91d12732bc53d96"
SOURCES_SHA256 = "3f2e6724d3a56a7b6440475eee8ebb4334fc399d04dfee8067f29bf320db9571"
UNICODE_VERSION = "15.0.0"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(data: bytes) -> dict:
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def git(reference: Path, *args: str) -> str:
    # Per-command trust permits read-only inspection without changing Git config.
    result = subprocess.run(
        ["git", "-c", f"safe.directory={reference.as_posix()}", "-C", str(reference), *args],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return result.stdout.rstrip("\n")


def inputs() -> tuple[dict, dict, dict, bytes]:
    baseline_bytes = BASELINE.read_bytes()
    require(identity(baseline_bytes)["sha256"] == BASELINE_SHA256,
            "Approved P0 baseline changed; audit it explicitly before generation")
    baseline = json.loads(baseline_bytes)
    environment = baseline["environment"]
    require(sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 12),
            "Generation requires the pinned CPython 3.12 runtime")
    require(sys.version == environment["python"] and sys.platform == environment["platform"],
            "Python runtime differs from the audited P0 baseline")
    require(Path(sys.executable).resolve() == Path(environment["executable"]).resolve(),
            "Use the audited baseline Python executable")
    require(unicodedata.unidata_version == environment["unicode_version"] == UNICODE_VERSION,
            "Generation requires Unicode 15.0.0")
    query = Path(baseline["installed"]["package"]) / "query.py"
    query_bytes = query.read_bytes()
    require(identity(query_bytes) == baseline["fingerprints"]["modules"]["query.py"],
            "Installed query.py identity changed")

    reference = ROOT.parent / "lingose-typescript"
    sources_path = reference / "tools/unicode/sources.json"
    license_path = reference / "tools/unicode/LICENSE.txt"
    sources_bytes, license_bytes = sources_path.read_bytes(), license_path.read_bytes()
    require(identity(sources_bytes)["sha256"] == SOURCES_SHA256,
            "Read-only Unicode source manifest changed")
    sources = json.loads(sources_bytes)
    license_source = next(row for row in sources["sources"] if row["path"] == "LICENSE.txt")
    require(sources["unicode_version"] == UNICODE_VERSION
            and sources["license"] == "Unicode License V3", "Unicode provenance changed")
    require(identity(license_bytes) == {"bytes": license_source["bytes"],
                                     "sha256": license_source["sha256"]}
            and license_source["sha256"] == LICENSE_SHA256,
            "Unicode license differs from its audited source manifest")
    require(b"\r" not in license_bytes, "Unicode license must retain its original LF bytes")
    reference_state = {"head": git(reference, "rev-parse", "HEAD"),
                       "status": git(reference, "status", "--short", "--untracked-files=all").splitlines()}
    pinned_reference = baseline["references"]["lingose-typescript"]
    require(reference_state == {key: pinned_reference[key] for key in ("head", "status")},
            "Unicode reference checkout changed from its audited head/status")
    fingerprints = {"baseline": identity(baseline_bytes), "query": identity(query_bytes),
                    "unicode_sources": identity(sources_bytes), "unicode_license": identity(license_bytes),
                    "generator": identity(Path(__file__).read_bytes()), "reference": reference_state}
    provenance = {
        "baseline": {"path": "docs/reference-baseline.json", **identity(baseline_bytes)},
        "python": {"executable": environment["executable"], "version": sys.version,
                   "implementation": sys.implementation.name, "unicode_version": UNICODE_VERSION},
        "installed_query": {"path": str(query), **identity(query_bytes)},
        "unicode_license": {
            "name": sources["license"], "url": license_source["url"],
            "reference_path": "../lingose-typescript/tools/unicode/LICENSE.txt",
            **identity(license_bytes),
            "source_manifest": {"path": "../lingose-typescript/tools/unicode/sources.json",
                                **identity(sources_bytes)},
            "reference_checkout": {"path": "../lingose-typescript", **reference_state},
            "copied_to": "third_party/unicode/LICENSE.txt",
        },
    }
    return baseline, fingerprints, provenance, license_bytes


def generate() -> dict[str, bytes]:
    _, before, provenance, license_bytes = inputs()
    uppercase, lower = [], []
    digest = hashlib.sha256()
    scalar_count = 0
    for codepoint in range(0x110000):
        if 0xD800 <= codepoint <= 0xDFFF:
            continue
        scalar_count += 1
        character = chr(codepoint)
        upper, mapped = character.isupper(), character.lower()
        if upper:
            uppercase.append(codepoint)
        if mapped != character:
            lower.append((codepoint, mapped))
        encoded = mapped.encode("utf-8")
        digest.update(struct.pack("<IBI", codepoint, int(upper), len(encoded)))
        digest.update(encoded)
    ranges = []
    for codepoint in uppercase:
        if ranges and ranges[-1][1] + 1 == codepoint:
            ranges[-1][1] = codepoint
        else:
            ranges.append([codepoint, codepoint])
    scalar_digest = digest.hexdigest()
    lines = [
        "//! Generated by tools/generate_query_case.py; do not edit by hand.",
        "//! CPython 3.12 / Unicode 15.0.0; see docs/query-case.json for provenance.",
        "//! Unicode data copyright Unicode, Inc.; Unicode License V3 at",
        "//! third_party/unicode/LICENSE.txt. The project license does not replace it.",
        "",
        "#[rustfmt::skip]",
        "pub(super) const UPPERCASE_RANGES: &[(u32, u32)] = &[",
    ]
    lines.extend(f"    (0x{first:04X}, 0x{last:04X})," for first, last in ranges)
    lines.extend(["];", "", "#[rustfmt::skip]",
                  "pub(super) const LOWERCASE: &[(u32, &str)] = &["])
    for codepoint, mapped in lower:
        escaped = "".join("\\u{" + f"{ord(character):04X}" + "}" for character in mapped)
        lines.append(f'    (0x{codepoint:04X}, "{escaped}"),')
    lines.extend([
        "];", "", "#[cfg(test)]",
        'pub(super) const SCALAR_SHA256: &str =', f'    "{scalar_digest}";', "",
    ])
    tables = "\n".join(lines).encode("utf-8")
    artifacts = {"src/query_case_tables.rs": tables,
                 "third_party/unicode/LICENSE.txt": license_bytes}
    report = {
        "format_version": 1, "unicode_version": UNICODE_VERSION,
        "generator": {"path": "tools/generate_query_case.py", **before["generator"]},
        "provenance": provenance,
        "counts": {"scalars": scalar_count, "uppercase_scalars": len(uppercase),
                   "uppercase_ranges": len(ranges), "nonidentity_lowercase_mappings": len(lower)},
        "scalar_sha256": scalar_digest,
        "scalar_digest_format": "For every Unicode scalar in ascending numeric order: u32 little-endian scalar, u8 Python isupper (0/1), u32 little-endian byte length of Python scalar.lower(), then its UTF-8 bytes; surrogates excluded",
        "scope": "Simple-query fallback only; no normalization, case folding, locale tailoring, or annotation casing",
        "selection": "Only first scalar Uppercase and no later scalar Uppercase; return a variant only when the lowered string changes",
        "lowercase_equivalence": "Python default lower has one language-independent contextual mapping, Final_Sigma. Capital Sigma U+03A3 is Uppercase, so accepted fallback input can contain it only at index zero. Final_Sigma requires a preceding cased character, which is impossible there. Thus per-scalar full lower mappings equal whole-string lower on this accepted input domain. Later titlecase scalars are permitted and must also be lowered.",
        "compiler_unicode": "Rust compiler Unicode properties and casing are never consulted",
        "artifacts": {path: identity(value) for path, value in artifacts.items()},
        "reproduce": "D:\\Python\\Python312\\python.exe -I -B -X utf8 tools/generate_query_case.py --check",
    }
    artifacts["docs/query-case.json"] = (json.dumps(report, ensure_ascii=False, sort_keys=True,
                                                   indent=2, allow_nan=False) + "\n").encode("utf-8")
    _, after, _, _ = inputs()
    require(before == after, "Generation inputs changed; no artifacts written")
    return artifacts


def persist(directory: Path, artifacts: dict[str, bytes], write: bool) -> None:
    pending = []
    for name, value in artifacts.items():
        path = artifact_path(name, directory)
        require(path.resolve().is_relative_to(directory), "Artifact escapes output directory")
        if path.exists():
            if directory == ROOT and name in ("docs/query-case.json", "docs/annotation-unicode.json"):
                check_historical_generator(name, value, path.read_bytes())
            else:
                require(path.read_bytes() == value,
                        f"Artifact drift: {path}; existing bytes preserved")
        else:
            require(write, f"Missing artifact: {path}; initial creation requires --write")
            pending.append((path, value))
    for path, value in pending:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT)
    args = parser.parse_args()
    directory = args.output.resolve()
    require(directory == ROOT or directory.is_relative_to(ROOT / ".local"),
            "Output must be this checkout or its .local directory")
    artifacts = generate()
    persist(directory, artifacts, args.write)
    print(json.dumps({"mode": "write" if args.write else "check", "files": len(artifacts),
                      "input_fingerprints_unchanged": True,
                      "historical_metadata_preserved": directory == ROOT,
                      "artifacts": {name: identity(artifact_path(name, directory).read_bytes())
                                    for name in artifacts}},
                     sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1) from None
