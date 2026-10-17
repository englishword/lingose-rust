"""Development-only, read-only access to the installed Python reference."""

from __future__ import annotations

import ast
from contextlib import contextmanager
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
LIB_ROOT = ROOT / "crates/lingose"
BASELINE = ROOT / "docs/reference-baseline.json"
MODULES = ("__init__.py", "query.py", "annotation.py", "_resources.py",
           "_packed.py", "types.py", "ranking.py")


class ReferenceError(RuntimeError):
    """A missing, changed or unsafe reference must be audited explicitly."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReferenceError(message)


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def file_record(path: Path) -> dict:
    require(path.is_file(), f"Missing reference file: {path}")
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def artifact_path(name: str, directory: Path = ROOT) -> Path:
    """Map legacy artifact keys without changing frozen manifests/provenance.

    Alternate output directories retain the original artifact-relative layout.
    Repository documentation and the P0 JSON fixture remain repository-owned.
    """
    relative = Path(name)
    require(bool(relative.parts) and not relative.drive and not relative.is_absolute()
            and ".." not in relative.parts, "Unsafe artifact key")
    library = relative.parts[0] in ("src", "data", "third_party") or (
        relative.parts[0] == "tests" and relative.suffix == ".rs")
    return (LIB_ROOT if directory == ROOT and library else directory) / relative


def workspace_inputs(test_names=(), probe=None) -> list[str]:
    """Minimal byte-preserving workspace snapshot; never rewrite its lockfile."""
    names = ["Cargo.toml", "Cargo.lock", "crates/lingose-cli/Cargo.toml"]
    names += [path.relative_to(ROOT).as_posix()
              for path in sorted((ROOT / "crates/lingose-cli/src").rglob("*.rs"))]
    names += [(LIB_ROOT / name).relative_to(ROOT).as_posix() for name in (
        "Cargo.toml", "README.md", "LICENSE", "SOURCES.md", "data/lexicon.bin",
        "data/frequency.bin", "third_party/unicode/LICENSE.txt")]
    names += [path.relative_to(ROOT).as_posix() for path in sorted((LIB_ROOT / "src").rglob("*.rs"))]
    names += [(LIB_ROOT / f"tests/{name}.rs").relative_to(ROOT).as_posix() for name in test_names]
    if probe:
        names += [f"{probe}/{name}" for name in ("Cargo.toml", "Cargo.lock", "src/main.rs")]
    return names


def evidence_output(path: Path) -> Path:
    """New evidence must stay in the checkout and must not replace old results."""
    path = path.resolve()
    require(path.is_relative_to(ROOT.resolve()), "Evidence output must remain in project")
    require(not path.exists(), "Use a new evidence path; prior results are immutable")
    return path


def check_historical_generator(name: str, generated: bytes, recorded: bytes) -> None:
    """Compare regenerated metadata while independently authenticating its old generator.

    33e72c9 is the completed 0.1.0 checkout, before workspace/path adaptations.
    Only generator identity may differ; tables and all other provenance stay exact.
    """
    current, historical = json.loads(generated), json.loads(recorded)
    identity = historical["generator"]
    require(identity["path"] == current["generator"]["path"], f"Historical generator path drift: {name}")
    source = subprocess.run(["git", "show", f"33e72c9:{identity['path']}"], cwd=ROOT,
                            capture_output=True, check=True).stdout
    require({"bytes": len(source), "sha256": hashlib.sha256(source).hexdigest()} ==
            {key: identity[key] for key in ("bytes", "sha256")},
            f"Historical generator identity drift: {name}")
    current.pop("generator")
    historical.pop("generator")
    require(current == historical, f"Historical provenance drift: {name}")


def no_journals(path: Path) -> None:
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = Path(str(path) + suffix)
        require(not sidecar.exists(), f"Resolve reference SQLite sidecar first: {sidecar}")


def connect(path: Path) -> sqlite3.Connection:
    path = path.resolve()
    require(path.is_file(), f"Missing database; no implicit restoration: {path}")
    no_journals(path)
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA query_only = ON")
    return db


def literal_version(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    stores = [node for node in ast.walk(tree) if isinstance(node, ast.Name)
              and node.id == "__version__" and isinstance(node.ctx, (ast.Store, ast.Del))]
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                   and node.targets[0].id == "__version__"]
    require(len(stores) == len(assignments) == 1, "Expected one literal version assignment")
    value = assignments[0].value
    require(isinstance(value, ast.Constant) and isinstance(value.value, str),
            "Reference version must be a literal string; source is never executed")
    return value.value


def installed() -> tuple[object, Path, Path, Path]:
    import lingose
    from lingose import _resources

    distribution = importlib.metadata.distribution("lingose")
    package = Path(lingose.__file__).resolve().parent
    require(distribution.version == lingose.__version__ == "0.2.0",
            "Only installed Lingose 0.2.0 is the authorized reference")
    require(package == Path(distribution.locate_file("lingose")).resolve(),
            "Imported module does not match the installed distribution")
    database = _resources.database_path().resolve()  # Resolves only; never restores.
    frequency = package / "frequency.sqlite"
    for path in (database, frequency):
        require(path.is_file(), f"Missing reference; restore only to workspace explicitly: {path}")
        no_journals(path)
    require((package / "lexicon.lpk").is_file(), "Missing installed packed snapshot")
    return lingose, package, database, frequency


def fingerprints() -> dict:
    _, package, database, frequency = installed()
    return {
        "modules": {name: file_record(package / name) for name in MODULES},
        "resources": {name: {"path": str(path), **file_record(path)} for name, path in (
            ("lexicon.lpk", package / "lexicon.lpk"), ("lexicon.sqlite", database),
            ("frequency.sqlite", frequency))},
    }


def require_baseline() -> dict:
    require(BASELINE.is_file(), "Run audit_reference.py --write before capturing API vectors")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    require(fingerprints() == baseline["fingerprints"],
            "Installed reference changed; do not overwrite the approved baseline")
    return baseline


@contextmanager
def no_restore():
    """Preserve real query behavior while replacing preparation with an existence guard."""
    from lingose import _packed, _resources
    _, _, expected, _ = installed()

    def present_only(path):
        require(Path(path).resolve() == expected, "Unexpected reference database path")
        require(expected.is_file(), "Reference disappeared; restoration is forbidden")
        no_journals(expected)

    def forbidden(*args, **kwargs):
        raise ReferenceError("Snapshot restoration is forbidden during audit")

    with patch.object(_resources, "ensure_database", present_only), patch.object(_packed, "restore", forbidden):
        yield


def git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-c", f"safe.directory={repository.as_posix()}",
         "-C", str(repository), *arguments], capture_output=True, text=True, encoding="utf-8")
    require(result.returncode == 0, f"Read-only git failed: {result.stderr.strip()}")
    return result.stdout.rstrip("\n")


def reference_repositories() -> dict:
    requested = {
        "lingose-python": ("README.md", "docs/api.md", "pyproject.toml", "LICENSE", "SOURCES.md",
                           *(f"src/lingose/{name}" for name in MODULES),
                           "src/lingose/lexicon.lpk", "src/lingose/frequency.sqlite"),
        "lingose-typescript": ("README.md", "package.json", "tools/reference.py", "tools/audit_reference.py"),
        "chrome-extension": ("README.md", "package.json"),
    }
    result = {}
    for name, names in requested.items():
        repository = (ROOT.parent / name).resolve()
        result[name] = {"path": str(repository), "head": git(repository, "rev-parse", "HEAD"),
                        "branch": git(repository, "branch", "--show-current"),
                        "status": git(repository, "status", "--porcelain=v1", "--untracked-files=all").splitlines(),
                        "files": {name: file_record(repository / name) for name in names}}
    python_init = ROOT.parent / "lingose-python/src/lingose/__init__.py"
    result["lingose-python"]["version"] = literal_version(python_init)
    return result


def freeze(path: Path, text: str, write: bool) -> str:
    """Create a missing baseline explicitly; never replace a different baseline."""
    if path.exists():
        require(path.read_text(encoding="utf-8") == text, f"Recorded artifact drift: {path}")
        return "unchanged"
    require(write, f"Missing artifact: {path}; use --write for initial creation")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return "created"


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def main_error(error: Exception) -> None:
    print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)
