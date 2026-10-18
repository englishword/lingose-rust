"""Fail closed on candidate identity and package-local Rust include targets."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_cli_package as package


class CliCandidateGuards(unittest.TestCase):
    def test_required_rust_includes_resolve_inside_archive(self):
        files = {"src/lib.rs": b'#![doc = include_str!("../README.md")]\n',
                 "src/data/mod.rs": b'include_bytes!("../../data/lexicon.bin");\n'
                                     b'include_bytes!("../../data/frequency.bin");\n',
                 "README.md": b"docs", "data/lexicon.bin": b"lexicon", "data/frequency.bin": b"frequency"}
        self.assertEqual(len(package.check_includes(files)), 3)
        for target in (b"../../outside", b"../../../outside", b"C:/outside"):
            with self.subTest(target=target), self.assertRaises(RuntimeError):
                package.check_includes({**files, "src/extra.rs": b'include_str!("' + target + b'");'})
        del files["data/lexicon.bin"]
        with self.assertRaises(RuntimeError):
            package.check_includes(files)

    def test_cli_guard_and_local_versioned_library_dependency_are_required(self):
        manifest = ('[package]\nname="lingose-cli"\nversion="0.2.0"\npublish=false\n'
                    'include=["/src/**"]\n[dependencies]\n'
                    'lingose={version="0.2.0",path="../lingose"}\n')
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "src").mkdir()
            (directory / "src/main.rs").write_bytes(b"fn main() {}\n")
            with patch.object(package, "CLI", directory):
                (directory / "Cargo.toml").write_text(manifest, encoding="utf-8")
                self.assertEqual(set(package.cli_inputs()), {"Cargo.toml", "src/main.rs"})
                for invalid in (manifest.replace("publish=false", "publish=true"),
                                manifest.replace('path="../lingose"', 'path="../other"'),
                                manifest.replace('version="0.2.0",path', 'version="0.1.0",path')):
                    with self.subTest(invalid=invalid), self.assertRaises(RuntimeError):
                        (directory / "Cargo.toml").write_text(invalid, encoding="utf-8")
                        package.cli_inputs()


if __name__ == "__main__":
    unittest.main()
