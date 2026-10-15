"""Guard behavior tested with small disposable files, never the source database."""

from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from reference import ReferenceError, canonical, connect, file_record, freeze, literal_version, no_restore


class ReferenceGuards(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_missing_database_is_not_created(self):
        path = self.root / "missing.sqlite"
        with self.assertRaises(ReferenceError):
            connect(path)
        self.assertFalse(path.exists())

    def test_readonly_prevents_write_and_preserves_hash(self):
        path = self.root / "fixture.sqlite"
        with closing(sqlite3.connect(path)) as db:
            db.execute("CREATE TABLE example(value)")
            db.commit()
        before = file_record(path)
        with closing(connect(path)) as db:
            self.assertEqual(db.execute("PRAGMA query_only").fetchone()[0], 1)
            with self.assertRaises(sqlite3.OperationalError):
                db.execute("INSERT INTO example VALUES (1)")
        self.assertEqual(file_record(path), before)

    def test_sidecars_are_rejected_even_if_empty(self):
        path = self.root / "fixture.sqlite"
        path.touch()
        for suffix in ("-wal", "-shm", "-journal"):
            with self.subTest(suffix=suffix):
                sidecar = Path(str(path) + suffix)
                sidecar.touch()
                with self.assertRaises(ReferenceError):
                    connect(path)
                sidecar.unlink()

    def test_baseline_creation_requires_write_and_drift_never_overwrites(self):
        path = self.root / "baseline.json"
        with self.assertRaises(ReferenceError):
            freeze(path, "original\n", False)
        self.assertFalse(path.exists())
        self.assertEqual(freeze(path, "original\n", True), "created")
        self.assertEqual(freeze(path, "original\n", False), "unchanged")
        with self.assertRaises(ReferenceError):
            freeze(path, "changed\n", True)
        self.assertEqual(path.read_text(), "original\n")

    def test_version_is_literal_and_source_is_not_executed(self):
        path = self.root / "source.py"
        path.write_text("raise RuntimeError('must not execute')\n__version__ = '0.2.1'\n")
        self.assertEqual(literal_version(path), "0.2.1")
        for content in ("__version__ = str(1)\n", "__version__='1'\n__version__='2'\n",
                        "__version__='1'\n__version__ += '2'\n", "__version__='1'\ndel __version__\n"):
            with self.subTest(content=content):
                path.write_text(content)
                with self.assertRaises(ReferenceError):
                    literal_version(path)

    def test_canonical_encoding_preserves_types_and_unicode(self):
        self.assertNotEqual(canonical(None), canonical(False))
        self.assertNotEqual(canonical(False), canonical(0))
        self.assertNotEqual(canonical('\u00e9'), canonical('e\u0301'))
        with self.assertRaises(ValueError):
            canonical(float('nan'))

    def test_api_guard_never_restores_a_disappearing_database(self):
        from lingose import _resources
        path = (self.root / "disappeared.sqlite").resolve()
        with patch('reference.installed', return_value=(None, None, path, None)):
            with no_restore():
                with self.assertRaises(ReferenceError):
                    _resources.ensure_database(path)
        self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
