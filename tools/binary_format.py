"""Inspect release executable headers without executing them or external tools.

Supports the 64-bit PE, ELF and Mach-O formats used by the five release targets.
Malformed, truncated and unsupported inputs raise ValueError. Reported loader and
symbol-version requirements are metadata, not proof of compatibility with an OS.
"""

from __future__ import annotations

import struct


class _Reader:
    def __init__(self, data: bytes, label: str):
        self.data = data
        self.label = label

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            raise ValueError(f"{self.label}: {message}")

    def span(self, offset: int, size: int) -> tuple[int, int]:
        self.require(0 <= offset <= len(self.data) and 0 <= size <= len(self.data) - offset,
                     "truncated or invalid file range")
        return offset, offset + size

    def unpack(self, layout: str, offset: int) -> tuple:
        self.span(offset, struct.calcsize(layout))
        return struct.unpack_from(layout, self.data, offset)

    def string(self, offset: int, end: int) -> str:
        self.span(offset, end - offset)
        terminator = self.data.find(b"\0", offset, end)
        self.require(terminator >= offset, "unterminated metadata string")
        try:
            return self.data[offset:terminator].decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"{self.label}: invalid metadata string encoding") from error


def _architecture(reader: _Reader, machine: int, supported: dict[int, str]) -> str:
    reader.require(machine in supported, f"unsupported machine {machine:#x}")
    return supported[machine]


def _pe(data: bytes) -> dict:
    reader = _Reader(data, "PE")
    pe_offset, = reader.unpack("<I", 0x3C)
    reader.span(pe_offset, 24)
    reader.require(data[pe_offset:pe_offset + 4] == b"PE\0\0", "invalid PE signature")
    machine, count, _, _, _, optional_size, _ = reader.unpack("<HHIIIHH", pe_offset + 4)
    architecture = _architecture(reader, machine, {0x8664: "x86_64", 0xAA64: "aarch64"})
    optional = pe_offset + 24
    reader.span(optional, optional_size)
    reader.require(optional_size >= 112, "truncated optional header")
    reader.require(reader.unpack("<H", optional)[0] == 0x20B, "expected PE32+ format")
    image_base, = reader.unpack("<Q", optional + 24)
    headers_size, = reader.unpack("<I", optional + 60)
    directories, = reader.unpack("<I", optional + 108)
    reader.require(directories <= (optional_size - 112) // 8, "truncated data directories")
    sections_start = optional + optional_size
    reader.span(sections_start, count * 40)
    reader.span(0, headers_size)
    sections = []
    for index in range(count):
        fields = reader.unpack("<8sIIIIIIHHI", sections_start + index * 40)
        _, virtual_size, address, raw_size, raw_offset, *_ = fields
        if raw_size:
            reader.span(raw_offset, raw_size)
        sections.append((address, virtual_size, raw_offset, raw_size))

    def rva(value: int, size: int = 1) -> tuple[int, int]:
        if 0 <= value < headers_size and size <= headers_size - value:
            return value, headers_size
        for address, _, raw_offset, raw_size in sections:
            relative = value - address
            if 0 <= relative < raw_size and size <= raw_size - relative:
                return raw_offset + relative, raw_offset + raw_size
        raise ValueError("PE: metadata RVA is not file-backed")

    libraries = []
    for directory, descriptor_size, name_index in ((1, 20, 3), (13, 32, 1)):
        if directory >= directories:
            continue
        address, size = reader.unpack("<II", optional + 112 + directory * 8)
        if address == size == 0:
            continue
        reader.require(bool(address) and size >= descriptor_size, "invalid import directory")
        offset, _ = rva(address, size)
        terminated = False
        for position in range(offset, offset + size - descriptor_size + 1, descriptor_size):
            fields = reader.unpack("<" + "I" * (descriptor_size // 4), position)
            if not any(fields):
                terminated = True
                break
            name_rva = fields[name_index]
            if directory == 13 and not fields[0] & 1:
                name_rva -= image_base
            start, end = rva(name_rva)
            name = reader.string(start, end)
            reader.require(bool(name), "empty imported library name")
            if name not in libraries:
                libraries.append(name)
        reader.require(terminated, "unterminated import descriptor table")
    return {"format": "PE", "architecture": architecture,
            "imported_libraries": libraries, "interpreter": None}


def _elf(data: bytes) -> dict:
    reader = _Reader(data, "ELF")
    reader.span(0, 64)
    reader.require(data[4:7] == b"\x02\x01\x01", "expected little-endian ELF64 version 1")
    fields = reader.unpack("<16sHHIQQQIHHHHHH", 0)
    _, kind, machine, version, _, program_offset, _, _, header_size, entry_size, count, *_ = fields
    architecture = _architecture(reader, machine, {62: "x86_64", 183: "aarch64"})
    reader.require(kind in (2, 3) and version == 1 and header_size == 64,
                   "invalid executable header")
    reader.require(entry_size == 56 and 0 < count < 0xFFFF, "unsupported program header table")
    reader.span(program_offset, count * entry_size)
    programs = [reader.unpack("<IIQQQQQQ", program_offset + index * entry_size)
                for index in range(count)]
    for program in programs:
        _, _, offset, _, _, size, _, _ = program
        if size:
            reader.span(offset, size)

    def address(value: int, size: int) -> int:
        for program in programs:
            kind, _, offset, virtual, _, file_size, _, _ = program
            relative = value - virtual
            if kind == 1 and 0 <= relative <= file_size and size <= file_size - relative:
                return reader.span(offset + relative, size)[0]
        raise ValueError("ELF: metadata address is not file-backed")

    interpreters = [program for program in programs if program[0] == 3]
    reader.require(len(interpreters) <= 1, "multiple interpreters")
    interpreter = None
    if interpreters:
        program = interpreters[0]
        interpreter = reader.string(program[2], program[2] + program[5])
        reader.require(bool(interpreter), "empty interpreter")
    dynamic = [program for program in programs if program[0] == 2]
    reader.require(len(dynamic) <= 1, "multiple dynamic tables")
    result = {"format": "ELF", "architecture": architecture,
              "imported_libraries": [], "interpreter": interpreter,
              "required_symbol_versions": {}}
    if not dynamic:
        return result
    program = dynamic[0]
    reader.require(program[5] % 16 == 0, "misaligned dynamic table")
    entries = []
    for offset in range(program[2], program[2] + program[5], 16):
        tag, value = reader.unpack("<QQ", offset)
        if tag == 0:
            break
        entries.append((tag, value))
    else:
        raise ValueError("ELF: unterminated dynamic table")
    values = dict(entries)
    if not any(tag in (1, 0x6FFFFFFE) for tag, _ in entries):
        return result
    reader.require(5 in values and 10 in values, "missing dynamic string table")
    strings_size = values[10]
    strings = address(values[5], strings_size)

    def text(index: int) -> str:
        reader.require(0 <= index < strings_size, "invalid dynamic string offset")
        return reader.string(strings + index, strings + strings_size)

    result["imported_libraries"] = [text(value) for tag, value in entries if tag == 1]
    if 0x6FFFFFFE not in values:
        return result
    reader.require(0 < values.get(0x6FFFFFFF, 0) <= len(data) // 16,
                   "invalid version requirement count")
    current = values[0x6FFFFFFE]
    seen = set()
    for index in range(values[0x6FFFFFFF]):
        reader.require(current not in seen, "cyclic version requirement table")
        seen.add(current)
        version, count, file_name, auxiliary, next_record = reader.unpack("<HHIII", address(current, 16))
        reader.require(version == 1 and 0 < count <= len(data) // 16,
                       "invalid version requirement record")
        library = text(file_name)
        versions = []
        auxiliary_address = current + auxiliary
        auxiliary_seen = set()
        for auxiliary_index in range(count):
            reader.require(auxiliary_address not in auxiliary_seen, "cyclic version auxiliary table")
            auxiliary_seen.add(auxiliary_address)
            _, _, _, name, next_auxiliary = reader.unpack("<IHHII", address(auxiliary_address, 16))
            versions.append(text(name))
            reader.require(bool(next_auxiliary) == (auxiliary_index + 1 < count),
                           "invalid version auxiliary chain length")
            auxiliary_address += next_auxiliary
        result["required_symbol_versions"].setdefault(library, []).extend(versions)
        reader.require(bool(next_record) == (index + 1 < values[0x6FFFFFFF]),
                       "invalid version requirement chain length")
        current += next_record
    return result


def _version(value: int) -> str:
    return f"{value >> 16}.{(value >> 8) & 255}.{value & 255}"


def _mach_o(data: bytes) -> dict:
    reader = _Reader(data, "Mach-O")
    _, cpu, _, _, count, commands_size, _, _ = reader.unpack("<8I", 0)
    architecture = _architecture(reader, cpu, {0x01000007: "x86_64", 0x0100000C: "aarch64"})
    _, end = reader.span(32, commands_size)
    reader.require(count <= commands_size // 8, "invalid load command count")
    result = {"format": "Mach-O", "architecture": architecture,
              "imported_libraries": [], "interpreter": None}
    position = 32
    for _ in range(count):
        reader.require(position + 8 <= end, "truncated load command")
        command, size = reader.unpack("<II", position)
        reader.require(size >= 8 and size % 8 == 0 and size <= end - position,
                       "invalid load command size")
        if command in (0xC, 0x80000018, 0x8000001F, 0x20, 0x80000023):
            reader.require(size >= 24, "truncated dylib command")
            name, = reader.unpack("<I", position + 8)
            reader.require(24 <= name < size, "invalid dylib name offset")
            result["imported_libraries"].append(reader.string(position + name, position + size))
        elif command == 0xE:
            reader.require(size >= 12, "truncated dynamic linker command")
            name, = reader.unpack("<I", position + 8)
            reader.require(12 <= name < size and result["interpreter"] is None,
                           "invalid dynamic linker name")
            result["interpreter"] = reader.string(position + name, position + size)
        elif command in (0x24, 0x32):
            minimum = 16 if command == 0x24 else 24
            reader.require(size >= minimum, "truncated OS version command")
            if command == 0x24:
                version, sdk = reader.unpack("<II", position + 8)
            else:
                _, version, sdk, tools = reader.unpack("<IIII", position + 8)
                reader.require(tools <= (size - 24) // 8, "truncated build tool records")
            result["minimum_os"] = _version(version)
            result["sdk"] = _version(sdk)
        elif command == 0x19:
            reader.require(size >= 72, "truncated segment command")
            file_offset, file_size = reader.unpack("<QQ", position + 40)
            sections, = reader.unpack("<I", position + 64)
            reader.require(sections <= (size - 72) // 80, "truncated section records")
            if file_size:
                reader.span(file_offset, file_size)
        position += size
    reader.require(position == end, "load command size total differs")
    return result


def inspect_binary(data: bytes) -> dict:
    """Return format, architecture, imported_libraries and interpreter metadata.

    ELF additionally reports required_symbol_versions by library. Mach-O reports
    minimum_os and sdk when their version load command exists. No code is run.
    """
    if not isinstance(data, bytes):
        raise TypeError("inspect_binary expects bytes")
    if data.startswith(b"MZ"):
        return _pe(data)
    if data.startswith(b"\x7fELF"):
        return _elf(data)
    if data.startswith(b"\xcf\xfa\xed\xfe"):
        return _mach_o(data)
    raise ValueError("unsupported executable format")
