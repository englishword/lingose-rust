"""Exercise workspace/package boundaries using tiny independent archives."""
from contextlib import contextmanager
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_workspace_package as package


class WorkspacePackageGuards(unittest.TestCase):
    @contextmanager
    def fixture(self, readme=b"[Sources](SOURCES.md)\n"):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library = root / "crates/lingose"
            library.mkdir(parents=True)
            (root / "Cargo.toml").write_text('[workspace]\nmembers=["crates/lingose"]\n', encoding="utf-8")
            names = sorted(package.REQUIRED | {"src/lib.rs"})
            manifest = ('[package]\nname="lingose"\nversion="0.2.7"\nedition="2024"\n'
                        'rust-version="1.85"\nauthors=["Original author"]\nlicense="CC-BY-4.0"\n'
                        'readme="README.md"\nhomepage="https://lingose.com/"\n'
                        'repository="https://github.com/englishword/lingose-rust"\n'
                        'build=false\npublish=false\ninclude=' + json.dumps(names) + '\n'
                        '[dependencies]\nsha2="0.10.9"\n').encode()
            (library / "Cargo.toml").write_bytes(manifest)
            for name in names:
                path = library / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(readme if name == "README.md" else b"retained source\n")
            library_lock = ('version=4\n[[package]]\nname="lingose"\nversion="0.2.7"\n'
                            'dependencies=["sha2"]\n[[package]]\nname="sha2"\nversion="0.10.9"\n'
                            'source="registry+https://github.com/rust-lang/crates.io-index"\n'
                            'checksum="' + 'a' * 64 + '"\n').encode()
            root_lock = library_lock + b'[[package]]\nname="lingose-cli"\nversion="0.2.7"\ndependencies=["lingose"]\n'
            (root / "Cargo.lock").write_bytes(root_lock)
            normalized = manifest.replace(b'[dependencies]\nsha2="0.10.9"',
                                          b'[dependencies.sha2]\nversion="0.10.9"')
            entries = {name: (library / name).read_bytes() for name in names}
            entries.update({"Cargo.toml": normalized, "Cargo.toml.orig": manifest,
                            "Cargo.lock": library_lock})
            yield root, library, entries

    def archive(self, root, entries, extra=(), prefix="lingose-0.2.7/", symlink=False):
        target = root / "sample.crate"
        with tarfile.open(target, "w:gz") as archive:
            for name, data in [*entries.items(), *extra]:
                member = tarfile.TarInfo(prefix + name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
            if symlink:
                member = tarfile.TarInfo(prefix + "escape")
                member.type = tarfile.SYMTYPE
                member.linkname = "../outside"
                archive.addfile(member)
        return target

    def audit(self, root, library, entries, **options):
        return package.audit_archive(self.archive(root, entries, **options), root, library)

    def test_virtual_workspace_and_normalized_library_lock_are_accepted(self):
        with self.fixture() as (root, library, entries):
            manifest, inputs = package.source_inventory(root, library)
            self.assertEqual(manifest["package"]["version"], "0.2.7")
            self.assertFalse(manifest["package"]["publish"])
            self.assertEqual(inputs["Cargo.lock"], package.identity((root / "Cargo.lock").read_bytes()))
            self.assertNotEqual(entries["Cargo.lock"], (root / "Cargo.lock").read_bytes())
            files, links = self.audit(root, library, entries)
            self.assertEqual(set(files), set(entries))
            self.assertEqual(links, [{"source": "README.md", "href": "SOURCES.md", "target": "SOURCES.md"}])

    def test_listing_rejects_missing_and_unexpected_files(self):
        with self.fixture() as (root, library, entries):
            _, inputs = package.source_inventory(root, library)
            self.assertEqual(package.check_listing(list(entries), inputs), sorted(entries))
            package.check_listing([*entries, ".cargo_vcs_info.json"], inputs)
            for names in ([name for name in entries if name != "data/LICENSE"],
                          [*entries, "maintenance.sqlite"], [*entries, "README.md"]):
                with self.subTest(names=names), self.assertRaises(RuntimeError):
                    package.check_listing(names, inputs)

    def test_original_manifest_is_the_library_manifest(self):
        with self.fixture() as (root, library, entries):
            entries["Cargo.toml.orig"] = (root / "Cargo.toml").read_bytes()
            with self.assertRaisesRegex(RuntimeError, "Original library manifest"):
                self.audit(root, library, entries)

    def test_normalized_manifest_identity_and_dependencies_are_checked(self):
        mutations = [(b'version="0.2.7"', b'version="0.1.0"'),
                     (b'version="0.10.9"', b'version="0.10.9"\npath="../other"'),
                     (b'license="CC-BY-4.0"', b'license="MIT"')]
        for old, new in mutations:
            with self.subTest(new=new), self.fixture() as (root, library, entries):
                entries["Cargo.toml"] = entries["Cargo.toml"].replace(old, new)
                with self.assertRaises(RuntimeError):
                    self.audit(root, library, entries)

    def test_lock_rejects_foreign_missing_and_changed_dependencies(self):
        for mutation in (lambda data: data.replace(b'"a' + b'a' * 63 + b'"', b'"b' + b'a' * 63 + b'"'),
                         lambda data: data + b'[[package]]\nname="foreign"\nversion="1.0.0"\n',
                         lambda data: data.replace(b'dependencies=["sha2"]', b'dependencies=[]'),
                         lambda data: data.split(b'[[package]]\nname="sha2"')[0]):
            with self.subTest(mutation=mutation), self.fixture() as (root, library, entries):
                entries["Cargo.lock"] = mutation(entries["Cargo.lock"])
                with self.assertRaises(RuntimeError):
                    self.audit(root, library, entries)

    def test_archive_rejects_unsafe_duplicate_extra_and_wrong_version_paths(self):
        extras = [("../outside", b"x"), ("/absolute", b"x"), ("src\\escape", b"x"),
                  ("C:/escape", b"x"), ("README.md", b"duplicate"), ("maintenance.sqlite", b"x")]
        with self.fixture() as (root, library, entries):
            for extra in extras:
                with self.subTest(extra=extra), self.assertRaises(RuntimeError):
                    self.audit(root, library, entries, extra=[extra])
            with self.assertRaises(RuntimeError):
                self.audit(root, library, entries, symlink=True)
            with self.assertRaises(RuntimeError):
                self.audit(root, library, entries, prefix="lingose-0.1.0/")

    def test_resource_payload_and_required_license_cannot_be_omitted_or_changed(self):
        with self.fixture() as (root, library, entries):
            entries["data/lexicon.bin"] = b"different lexicon"
            with self.assertRaisesRegex(RuntimeError, "Archive input differs"):
                self.audit(root, library, entries)
            (library / "data/LICENSE").unlink()
            with self.assertRaisesRegex(RuntimeError, "Missing included"):
                package.source_inventory(root, library)

    def test_packaged_links_and_host_paths_fail_closed(self):
        for readme in (b"[missing](missing.md)\n", b"[escape](../outside)\n",
                       b"[escape](%2e%2e/outside)\n", b"D:\\Python\\secret\n"):
            with self.subTest(readme=readme), self.fixture(readme) as (root, library, entries):
                with self.assertRaises(RuntimeError):
                    self.audit(root, library, entries)

    def test_optional_vcs_metadata_uses_library_relative_path(self):
        with self.fixture() as (root, library, entries):
            vcs = {"git": {"sha1": "a" * 40, "dirty": True}, "path_in_vcs": "crates/lingose"}
            entries[".cargo_vcs_info.json"] = json.dumps(vcs).encode()
            self.audit(root, library, entries)
            vcs["path_in_vcs"] = ""
            entries[".cargo_vcs_info.json"] = json.dumps(vcs).encode()
            with self.assertRaisesRegex(RuntimeError, "VCS metadata library path"):
                self.audit(root, library, entries)

    def test_default_mode_only_invokes_cargo_list(self):
        with self.fixture() as (root, library, entries):
            _, inputs = package.source_inventory(root, library)
            with patch.object(package, "source_inventory", return_value=({"package": {"name": "lingose", "version": "0.2.7"}}, inputs)), \
                    patch.object(sys, "argv", ["check_workspace_package.py"]), \
                    patch.object(package.subprocess, "run") as run, \
                    patch("builtins.print"):
                run.return_value.stdout = "\n".join(entries)
                package.main()
            command = run.call_args.args[0]
            self.assertEqual(command, ["cargo", "package", "--list", "-p", "lingose",
                                       "--offline", "--locked", "--allow-dirty"])


if __name__ == "__main__":
    unittest.main()
