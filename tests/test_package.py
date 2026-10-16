"""Reject invalid distribution evidence using tiny disposable archives."""
from contextlib import contextmanager
import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_package as package


class PackageGuards(unittest.TestCase):
    @contextmanager
    def fixture(self, readme=b"Readable offline package.\n"):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = b'[package]\nname="lingose"\nversion="0.1.0"\nbuild=false\n[dependencies.sha2]\nversion="0.10.9"\n'
            (root / "Cargo.toml").write_bytes(manifest)
            (root / "README.md").write_bytes(readme)
            inputs = {name: package.identity(root / name) for name in ("Cargo.toml", "README.md")}
            entries = [("Cargo.toml", manifest), ("Cargo.toml.orig", manifest), ("README.md", readme)]
            with patch.object(package, "ROOT", root):
                yield root, inputs, entries

    def archive(self, root, entries, symlink=False):
        target = root / "sample.crate"
        with tarfile.open(target, "w:gz") as archive:
            for name, data in entries:
                member = tarfile.TarInfo("lingose-0.1.0/" + name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
            if symlink:
                member = tarfile.TarInfo("lingose-0.1.0/escape")
                member.type = tarfile.SYMTYPE
                member.linkname = "../outside"
                archive.addfile(member)
        return target

    def test_complete_inventory_and_payload_identity_succeed(self):
        with self.fixture() as (root, inputs, entries):
            files, links = package.audit_archive(self.archive(root, entries), inputs)
            self.assertEqual(set(files), set(inputs) | {"Cargo.toml.orig"})
            self.assertEqual(links, [])

    def test_traversal_symlink_duplicates_and_extra_payload_are_rejected(self):
        with self.fixture() as (root, inputs, entries):
            for extra in [("../outside", b"x"), ("README.md", b"duplicate"), ("maintenance.sqlite", b"x")]:
                with self.subTest(extra=extra[0]), self.assertRaises(RuntimeError):
                    package.audit_archive(self.archive(root, entries + [extra]), inputs)
            with self.assertRaises(RuntimeError):
                package.audit_archive(self.archive(root, entries, symlink=True), inputs)

    def test_payload_changes_are_not_masked_by_matching_names(self):
        with self.fixture() as (root, inputs, entries):
            entries[-1] = ("README.md", b"changed")
            with self.assertRaisesRegex(RuntimeError, "Archive input differs"):
                package.audit_archive(self.archive(root, entries), inputs)

    def test_host_paths_and_missing_link_targets_are_rejected(self):
        for text in (b"D:\\Python\\secret\n", b"[missing](missing.md)\n"):
            with self.subTest(text=text), self.fixture(text) as (root, inputs, entries):
                with self.assertRaises((RuntimeError, ValueError)):
                    package.audit_archive(self.archive(root, entries), inputs)

    def test_missing_distribution_resources_fail_before_packaging(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Cargo.toml").write_text('[package]\nname="lingose"\nversion="0.1.0"\ninclude=[]\n', encoding="utf-8")
            with patch.object(package, "ROOT", root), self.assertRaisesRegex(RuntimeError, "Required data"):
                package.package_inputs()


if __name__ == "__main__":
    unittest.main()
