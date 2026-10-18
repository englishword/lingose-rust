# Sources and notices for Lingose 0.2.0 binaries

Original Lingose data and notation by **ZHAN Xianjue (詹先觉)**,
https://lingose.com/, licensed under [CC BY 4.0](LICENSE).

The original pinned [upstream notice](sources/UPSTREAM-SOURCES.md), its
[license](sources/LICENSE) and [source record](sources/SOURCES.json) are preserved
byte-for-byte. They credit Phonemizer 3.3.0, eSpeak NG 1.52.0, ECDICT, and
**Frequency List by Fabien Snauwaert**, https://frequencylist.com/.
Phonemizer/eSpeak executables and the Python source/review databases are not
distributed with these binaries.

## Data and Unicode

- IPA was generated with Phonemizer/eSpeak NG; IPS, ISM and root-lemma data are
  original Lingose work, and IPSM derives from the selected IPS/ISM.
- English meanings adapt ECDICT with extensive rewriting; Chinese meanings are
  translated from the English meanings. The supplemental full
  [ECDICT MIT license](licenses/ECDICT/LICENSE) preserves Copyright (c) 2025 Linwei.
  Its separately recorded source commit is the license snapshot, not proof of
  the original dictionary snapshot's revision.
- Unicode-derived tables retain [Unicode License V3](licenses/unicode/LICENSE.txt)
  and Copyright © 1991-2026 Unicode, Inc.
- The fixed reference supplies no separate Frequency List license text. Some
  external category lists lack per-label source/license records. These remain
  unresolved provenance gaps; Lingose's CC BY 4.0 does not relicense third-party
  material or resolve them. Formal publication requires the separate release
  preflight to review their disposition.

## Software

The binary calls the Lingose 0.2.0 library. Its enabled Cargo dependency graph
and exact versions, features, registry checksums, license fields and full license
file paths are recorded in manifest.json. Each dependency keeps its own
copyright notice and license text under `licenses/crates/NAME-VERSION/`.
Dual-license notices are preserved together, without replacing distinct authors
with one generic MIT license. Build-only `version_check` is included in the
inventory; that does not assert its code is linked into the runtime.

The Rust 1.93.1 distribution's full
[standard-library copyright/license aggregate](licenses/rust-1.93.1/COPYRIGHT-library.html)
is preserved. This aggregate includes platform-conditional standard-library
components and is broader than an assertion that each component is linked in
each target. Its scope is documented in the
[official Rust copyright record](https://github.com/rust-lang/rust/blob/1.93.1/COPYRIGHT).

Windows/UCRT/Visual C++ Runtime, glibc/libgcc_s/dynamic loaders and macOS system
libraries are runtime prerequisites where applicable; their binaries are not
included in this archive. Read README.md for the tested environments and Windows
runtime prerequisite. Cargo's `libc` crate and the operating system's C runtime
are separate components.
