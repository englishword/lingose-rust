"""Guard archive identities, paths, file modes and pinned notice payloads."""
from pathlib import Path
import io
import stat
import struct
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import package_cli_binary as package
from binary_format import inspect_binary

WINDOWS = "x86_64-pc-windows-msvc"
LINUX = "x86_64-unknown-linux-gnu"


class BinaryArchiveGuards(unittest.TestCase):
    def test_archive_names_and_modes_roundtrip_deterministically(self):
        for target in package.SLUGS:
            with self.subTest(target=target):
                files = {package.binary_name(target): (b"program", 0o755), "README.md": ("资料\n".encode(), 0o644)}
                data = package.write_archive(target, files, 1760000000)
                self.assertEqual(package.write_archive(target, files, 1760000000), data)
                self.assertEqual(package.read_archive(data, target), files)

    def test_unsafe_paths_roots_and_duplicate_entries_are_rejected(self):
        root = package.stem(WINDOWS)
        for name in ("../escape", "/absolute", root + "/../escape", root + "/./file",
                     root + "//file", root + "/C:/file", root + "/back\\slash", "wrong/file"):
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                package.safe_member(name, WINDOWS)
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive, warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            for _ in range(2):
                item = zipfile.ZipInfo(root + "/lingose.exe")
                item.create_system = 3
                item.external_attr = (stat.S_IFREG | 0o755) << 16
                archive.writestr(item, b"program")
        with self.assertRaises(RuntimeError):
            package.read_archive(output.getvalue(), WINDOWS)

    def test_links_and_incorrect_permissions_are_rejected(self):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as archive:
            item = tarfile.TarInfo(package.stem(LINUX) + "/lingose")
            item.type, item.linkname, item.mode = tarfile.SYMTYPE, "../../escape", 0o755
            archive.addfile(item)
        with self.assertRaises(RuntimeError):
            package.read_archive(output.getvalue(), LINUX)
        for target in (WINDOWS, LINUX):
            with self.subTest(target=target), self.assertRaises(RuntimeError):
                package.read_archive(package.write_archive(target, {package.binary_name(target): (b"x", 0o644)}, 1760000000), target)

    def test_checksum_tampering_is_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / package.archive_name(WINDOWS)
            path.write_bytes(b"changed archive")
            path.with_name(path.name + ".sha256").write_text("0" * 64 + "  " + path.name + "\n", encoding="ascii")
            with self.assertRaisesRegex(RuntimeError, "checksum differs"):
                package.checked_archive(path, WINDOWS, "a" * 40)

    def test_notice_hash_drift_is_rejected(self):
        value = package.catalog()
        value["files"]["LICENSE"]["sha256"] = "0" * 64
        with patch.object(package, "catalog", return_value=value), self.assertRaisesRegex(RuntimeError, "Notice drift"):
            package.materials(WINDOWS)

    def test_target_specific_license_closure(self):
        for target in package.SLUGS:
            files = package.materials(target)
            libc = [name for name in files if "libc-0.2.190" in name]
            self.assertEqual(bool(libc), target.startswith("aarch64"))
            self.assertIn("licenses/rust-1.93.1/COPYRIGHT-library.html", files)
            self.assertIn("licenses/ECDICT/LICENSE", files)

    def test_binary_header_detects_machine_and_rejects_truncation(self):
        data = bytearray(512)
        data[:2] = b"MZ"
        struct.pack_into("<I", data, 0x3C, 0x80)
        data[0x80:0x84] = b"PE\0\0"
        struct.pack_into("<HHIIIHH", data, 0x84, 0x8664, 0, 0, 0, 0, 112, 0)
        struct.pack_into("<H", data, 0x98, 0x20B)
        struct.pack_into("<I", data, 0x98 + 60, 512)
        self.assertEqual(inspect_binary(bytes(data))["architecture"], "x86_64")
        struct.pack_into("<H", data, 0x84, 0xAA64)
        self.assertEqual(inspect_binary(bytes(data))["architecture"], "aarch64")
        for size in (0, 2, 32, 128, 200, 511):
            with self.subTest(size=size), self.assertRaises(ValueError):
                inspect_binary(bytes(data[:size]))


if __name__ == "__main__":
    unittest.main()
