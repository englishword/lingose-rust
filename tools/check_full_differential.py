"""P4.1 complete public-API comparison against the pinned installed Python.

No production exporter/decoder supplies expectations. Public Python wrappers
share a read-only validated connection and one original _lookup per current
word; the wrappers, validation and result projection remain unchanged. Rust is
built offline in a minimal copy, then run with only requests and its executable.
Full requests/results stay in .local; the report records their identities.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing, contextmanager
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unicodedata
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (BASELINE, ROOT, workspace_inputs, evidence_output,
                       canonical, connect, file_record, fingerprints,
                       installed, json_text, main_error, no_restore, require,
                       require_baseline, sha256)
from generate_annotation_vectors import BASELINE_SHA256, SOURCE, SOURCE_SHA256

MAGIC = b"LNGDIFF1"
APIS = ("ipa", "IPA", "ips", "IPS", "ism", "ISM", "ipsm", "IPSM", "root_lemma",
        "meaning", "meaning_with_lang", "kind", "kind_with_label", "kind_list",
        "kind_list_with_label", "labels", "annotate_ips", "annotate_ips_with_skip_top")
ALIASES = {"ipa": "IPA", "ips": "IPS", "ism": "ISM", "ipsm": "IPSM"}
ENGLISH = re.compile(r"[A-Za-z]+(?:[-'’][A-Za-z]+)*\Z")


def blob(output, value: str):
    encoded = value.encode("utf-8")
    output.write(struct.pack("<I", len(encoded)))
    output.write(encoded)


def exact(stream, length):
    value = stream.read(length)
    require(len(value) == length, "Truncated differential stream")
    return value


def number(stream):
    return struct.unpack("<I", exact(stream, 4))[0]


def text(stream):
    return exact(stream, number(stream)).decode("utf-8")


def write_value(output, value):
    if value is None:
        output.write(b"\0")
    elif type(value) is str:
        output.write(b"\1")
        blob(output, value)
    elif type(value) is list and all(type(item) is str for item in value):
        output.write(b"\2" + struct.pack("<I", len(value)))
        for item in value:
            blob(output, item)
    elif type(value) is bool:
        output.write(bytes((3, int(value))))
    elif type(value) is dict and set(value) == {"error"}:
        output.write(b"\4")
        blob(output, value["error"])
    else:
        raise RuntimeError(f"Unsupported result type: {type(value)}")


def read_value(stream):
    tag = exact(stream, 1)
    if tag == b"\0":
        return None
    if tag == b"\1":
        return text(stream)
    if tag == b"\2":
        return [text(stream) for _ in range(number(stream))]
    if tag == b"\3":
        value = exact(stream, 1)
        require(value in (b"\0", b"\1"), "Invalid boolean tag")
        return value == b"\1"
    if tag == b"\4":
        return {"error": text(stream)}
    raise RuntimeError(f"Invalid result tag: {tag!r}")


def request(output, opcode, word="", option="", threshold=0):
    output.write(bytes((opcode,)))
    blob(output, word)
    blob(output, option)
    # Compare unbounded Python integers before adapting to the Rust i64 domain.
    capped = 5062 if threshold > 5062 else (-1 if threshold < 0 else threshold)
    output.write(struct.pack("<q", capped))


def read_request(stream):
    return (exact(stream, 1)[0], text(stream), text(stream),
            struct.unpack("<q", exact(stream, 8))[0])


def compare(requests: Path, expected: Path, actual: Path):
    counts = Counter()
    with requests.open("rb") as inputs, expected.open("rb") as left, actual.open("rb") as right:
        for stream in (inputs, left, right):
            require(exact(stream, 8) == MAGIC, "Differential protocol version mismatch")
        count = number(inputs)
        require(number(left) == number(right) == count, "Differential record count differs")
        for index in range(count):
            opcode, word, option, threshold = read_request(inputs)
            wanted, found = read_value(left), read_value(right)
            require(type(wanted) is type(found) and wanted == found,
                    f"Difference #{index} {APIS[opcode]}({word[:100]!r}, {option!r}, {threshold}): "
                    f"expected {str(wanted)[:240]!r}, found {str(found)[:240]!r}")
            counts[APIS[opcode]] += 1
        require(all(stream.read(1) == b"" for stream in (inputs, left, right)),
                "Trailing differential records/bytes")
    require(file_record(expected) == file_record(actual), "Equivalent values have noncanonical encoding")
    return dict(sorted(counts.items()))


def corpus(words, count):
    eligible = [word for word in words if ENGLISH.fullmatch(word)]
    seed = ["The", "apple", "is", "running", "unknownwordzz", "don't", "well-known", "the",
            "book", "US", "iPhone", "walks", "baking", "studied", "I'm", "you're"]
    separators = [" ", ", ", ".\n", " ", ";\n\n", "\t", " (", ") "]
    parts = []
    for index in range(count):
        word = seed[(index // 16) % len(seed)] if index % 16 < 4 else eligible[(index * 7919) % len(eligible)]
        parts.extend((word, separators[index % len(separators)]))
    value = "".join(parts)
    require(len(re.findall(r"[A-Za-z]+(?:[-'’][A-Za-z]+)*", value)) == count, "Corpus count drift")
    return value


def python_call(opcode, word, option, threshold):
    import lingose
    api = APIS[opcode]
    if opcode == 10:
        return lingose.meaning(word, option)
    if opcode == 12:
        return lingose.kind(word, option)
    if opcode == 14:
        return lingose.kind_list(option)
    if opcode == 17:
        return lingose.annotate_ips(word, skip_top=threshold)
    function = getattr(lingose, ALIASES.get(api, api))
    return function() if opcode in (13, 15) else function(word)


def p0_request(call):
    api, args, kwargs = call["api"], call.get("args", []), call.get("kwargs", {})
    word, option, threshold = "", "", 0
    if api == "kind_list":
        opcode = 14 if args else 13
        option = args[0] if args else ""
    elif api == "labels":
        opcode = 15
    else:
        word = args[0]
        opcode = APIS.index(api)
        if api == "meaning" and len(args) == 2:
            opcode, option = 10, args[1]
        if api == "kind" and len(args) == 2:
            opcode, option = 12, args[1]
        if api == "annotate_ips" and "skip_top" in kwargs:
            opcode, threshold = 17, kwargs["skip_top"]
            if type(threshold) is dict:
                threshold = int(threshold["$integer"])
    return opcode, word, option, threshold


@contextmanager
def shared_queries():
    """Keep public projection/validation, memoizing only the current raw lookup."""
    from lingose import query
    original = query._lookup
    with query._open_database() as (db, version):  # Original resource validation.
        previous, result = None, None
        @contextmanager
        def opened():
            yield db, version
        def lookup(connection, data_version, word):
            nonlocal previous, result
            require(connection is db and data_version == version, "Unexpected oracle connection")
            if word != previous:
                result = original(connection, data_version, word)
                previous = word
            return result
        with patch.object(query, "_open_database", opened), patch.object(query, "_lookup", lookup):
            yield


def capture(directory, words, labels, fixture, smoke):
    annotations, excluded, p0_ids = [], [], []
    counts = Counter()
    requests, expected = directory / "requests.bin", directory / "python.bin"
    with requests.open("xb") as inputs, expected.open("xb") as outputs, no_restore(), shared_queries():
        inputs.write(MAGIC + bytes(4))
        outputs.write(MAGIC + bytes(4))
        total = 0
        def add(opcode, word="", option="", threshold=0, pinned=None, identifier=None):
            nonlocal total
            try:
                value = python_call(opcode, word, option, threshold)
            except ValueError:
                require(pinned is not None and pinned.get("error") == "ValueError",
                        f"Unexpected Python ValueError: {APIS[opcode]} {word!r}")
                value = {"error": "InvalidArgument"}
            if pinned is not None:
                if "value" in pinned:
                    require(type(value) is type(pinned["value"]) and value == pinned["value"], f"P0 drift: {identifier}")
                elif "ordered_list" in pinned:
                    info = pinned["ordered_list"]
                    require(len(value) == info["length"] and hashlib.sha256(canonical(value)).hexdigest() == info["sha256"],
                            f"P0 full list drift: {identifier}")
                else:
                    require(value == {"error": "InvalidArgument"}, f"P0 error drift: {identifier}")
            request(inputs, opcode, word, option, threshold)
            write_value(outputs, value)
            counts[APIS[opcode]] += 1
            total += 1
            return value
        for index, word in enumerate(words[:16] if smoke else words):
            for opcode in range(10):
                add(opcode, word)
            for lang in ("en", "zh"):
                add(10, word, lang)
            add(11, word)
            for label in labels:
                add(12, word, label)
            if (index + 1) % 10000 == 0:
                print(f"Python public queries: {index + 1:,}/{len(words):,} exact keys", flush=True)
        add(15)
        add(13)
        ordered_members = 0
        for label in labels:
            ordered_members += len(add(14, option=label))
        require(ordered_members == 209759, "Full category member count drift")
        for row in fixture["cases"]:
            if row["source"] != "snapshot":
                continue
            if row["expected"].get("error") == "TypeError":
                excluded.append(row["id"])
                continue
            add(*p0_request(row["call"]), pinned=row["expected"], identifier=row["id"])
            p0_ids.append(row["id"])
        # Full-token and separator combinations supplement the historical P0 corpus.
        rule_texts = [
            "The \"apple\" the (hour) the\nbook the\n \n'apple' the, university.",
            "APPLE aPpLe US us May may iPhone McDonald K ı İ ſ 𝔄 é e\u0301 中文apple 😀",
            "don't doesn’t AREN'T I’m you're o’clock who's unknown'word second-puldsm first-rate",
            "walks boxes baked baking studies studied stopped stopping ageing singeing tingeing queueing axes is",
            "Messrs. P.M. a lot a lottery winded ; wind winded;wind one hundred fifty unknownwordzz",
            "  \t\r\n中文 123 café apple123 — w̄ 𝕙  \n",
        ]
        for index, value in enumerate(rule_texts):
            for threshold in (0, 1000, 5062):
                result = add(17, value, threshold=threshold)
                annotations.append({"case": f"rules-{index}", "skip_top": threshold,
                                    "input": identity(value), "output": identity(result)})
        if not smoke:
            budget = json.loads((ROOT / "docs/performance-budget.json").read_bytes())
            previous = json.loads((ROOT / "docs/layout-probe-results.json").read_bytes())["python_annotation"]
            for count in (10000, 100000):
                value = corpus(words, count)
                require(identity(value) == budget["corpora"][str(count)], "P1.2 corpus identity drift")
                (directory / f"corpus-{count}.txt").write_bytes(value.encode("utf-8"))
                for threshold in (0, 1000, 5062):
                    result = add(17, value, threshold=threshold)
                    original = next(row["output"] for row in previous if row["words"] == count and row["skip_top"] == threshold)
                    require(identity(result) == original, "P1.2 full Python output identity drift")
                    (directory / f"reference-{count}-skip-{threshold}.txt").write_bytes(result.encode("utf-8"))
                    annotations.append({"case": f"corpus-{count}", "words": count, "skip_top": threshold,
                                        "input": identity(value), "output": identity(result)})
                    print(f"Python complete annotation: {count:,} words skip={threshold}", flush=True)
        for stream in (inputs, outputs):
            stream.seek(8)
            stream.write(struct.pack("<I", total))
    return {"operations": dict(sorted(counts.items())), "total": total,
            "ordered_members_across_24_labels": ordered_members, "p0_snapshot_ids": p0_ids,
            "p0_type_domain_exclusions": excluded, "annotations": annotations}


def identity(value):
    encoded = value.encode("utf-8")
    return {"bytes": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest()}


def run(arguments, directory, environment):
    result = subprocess.run(arguments, cwd=directory, env=environment, capture_output=True, text=True, encoding="utf-8")
    require(result.returncode == 0, f"Command failed: {arguments}\n{result.stdout}\n{result.stderr}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="Small bridge validation; never writes formal evidence")
    parser.add_argument("--output", type=Path, help="New report path; never overwrites history")
    args = parser.parse_args()
    report_path = evidence_output(args.output or ROOT / "docs/full-differential-verification-0.2.0.json") if not args.smoke or args.output else None
    require(sha256(BASELINE) == BASELINE_SHA256 and sha256(SOURCE) == SOURCE_SHA256, "Fixed P0 identity drift")
    baseline = require_baseline()
    environment_info = baseline["environment"]
    require(sys.version == environment_info["python"] and sys.platform == environment_info["platform"]
            and Path(sys.executable).resolve() == Path(environment_info["executable"]).resolve()
            and unicodedata.unidata_version == environment_info["unicode_version"] == "15.0.0", "Pinned runtime drift")
    _, _, database, _ = installed()
    with no_restore(), closing(connect(database)) as db:
        words = [row[0] for row in db.execute("SELECT word FROM entry ORDER BY word COLLATE BINARY")]
    import lingose
    with no_restore():
        labels = lingose.labels()
    require(len(words) == 50335 and len(labels) == 24, "Fixed full-data counts drift")
    names = workspace_inputs(probe="tools/differential-probe") + [
             "crates/lingose/data/manifest.json",
             "docs/reference-baseline.json", "tests/fixtures/python-api-v1.json", "docs/performance-budget.json",
             "docs/layout-probe-results.json", "tools/check_full_differential.py", "tools/reference.py",
             "tools/generate_annotation_vectors.py", "tools/generate_error_vectors.py"]
    inputs = {name: file_record(ROOT / name) for name in names}
    local = ROOT / ".local"
    directory = Path(tempfile.mkdtemp(prefix="p41-smoke-" if args.smoke else "p41-differential-", dir=local))
    checkout, runtime, capture_dir = directory / "checkout", directory / "runtime", directory / "capture"
    checkout.mkdir()
    runtime.mkdir()
    capture_dir.mkdir()
    for name in names:
        destination = checkout / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
        require(file_record(destination) == inputs[name], f"Copy drift: {name}")
    environment = os.environ.copy()
    environment["CARGO_HOME"] = str(local / "cargo-home")
    environment["CARGO_TARGET_DIR"] = str(local / "differential-target")
    build = ["cargo", "build", "--manifest-path", "tools/differential-probe/Cargo.toml", "--release", "--offline", "--locked"]
    run(build, checkout, environment)
    executable = "lingose-differential-probe.exe" if os.name == "nt" else "lingose-differential-probe"
    shutil.copyfile(local / "differential-target/release" / executable, runtime / executable)
    coverage = capture(capture_dir, words, labels, json.loads(SOURCE.read_bytes()), args.smoke)
    shutil.copyfile(capture_dir / "requests.bin", runtime / "requests.bin")
    print(f"Comparing {coverage['total']:,} complete public results", flush=True)
    run([str(runtime / executable), "requests.bin", "rust.bin"], runtime, environment)
    require({path.name for path in runtime.iterdir()} == {executable, "requests.bin", "rust.bin"},
            "Rust runtime acquired unapproved inputs")
    require(file_record(runtime / "requests.bin") == file_record(capture_dir / "requests.bin"), "Runtime requests changed")
    shutil.copyfile(runtime / "rust.bin", capture_dir / "rust.bin")
    compared = compare(capture_dir / "requests.bin", capture_dir / "python.bin", capture_dir / "rust.bin")
    require(compared == coverage["operations"], "Comparison coverage differs")
    require(fingerprints() == baseline["fingerprints"], "Installed reference changed")
    for name, record in inputs.items():
        require(file_record(ROOT / name) == file_record(checkout / name) == record, f"Build input drift: {name}")
    report = {
        "phase": "P4.1", "scope": "Complete public result values, lists and texts; no performance, MSRV, package or publication acceptance.",
        "smoke_only": args.smoke, "platform": platform.platform(),
        "rustc": run(["rustc", "-Vv"], ROOT, environment).stdout.strip(),
        "cargo": run(["cargo", "-V"], ROOT, environment).stdout.strip(),
        "python": environment_info, "inputs": inputs, "reference_unchanged": True,
        "oracle_adapter": "Unmodified installed public wrappers, aliases mapped to uppercase; validated read-only connection reused, original _lookup memoized only for current word; no exporter expectations.",
        "full_exact_keys": 16 if args.smoke else len(words), "queries_per_key": 37,
        "labels": labels, "complete_category_lists": 25,
        "ordered_members_across_24_labels": coverage["ordered_members_across_24_labels"],
        "word_keys": identity("\n".join(words)), "coverage": coverage,
        "differences": 0, "comparison": "All typed values compared sequentially, then canonical full-result byte identities verified equal.",
        "build_arguments": build, "capture_directory": directory.relative_to(ROOT).as_posix(),
        "runtime_files": [path.name for path in sorted(runtime.iterdir())],
        "executable": file_record(runtime / executable),
        "artifacts": {path.name: file_record(path) for path in sorted(capture_dir.iterdir())},
    }
    report_path = report_path or directory / "smoke-evidence.json"
    report_path.write_text(json_text(report), encoding="utf-8", newline="\n")
    print(f"P4.1 {'smoke' if args.smoke else 'full'} differential passed: {coverage['total']:,} results, zero differences", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
