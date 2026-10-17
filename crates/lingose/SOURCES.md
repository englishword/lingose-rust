# Data sources and attribution

Original Lingose data and notation by **ZHAN Xianjue**, [lingose.com](https://lingose.com/), licensed under [CC BY 4.0](LICENSE).

## Sources

| Data | Source |
| --- | --- |
| `IPA` | Generated using [Phonemizer](https://github.com/bootphon/phonemizer) and [eSpeak NG](https://github.com/espeak-ng/espeak-ng). |
| `IPS`, `ISM`, `rank`, `root_lemma` | Original Lingose data. |
| `IPSM` | Derived from IPS and ISM using Lingose notation. |
| `kind` | Primarily original Lingose data; some labels were rebuilt with reference to external vocabulary lists. |
| `meaning_en` | Adapted from [ECDICT](https://github.com/skywind3000/ECDICT) with extensive rewriting. |
| `meaning_zh` | Translated from the English meanings. |
| Frequency data | [Frequency List](https://frequencylist.com/) by Fabien Snauwaert. |

Verified local tool versions: **Phonemizer 3.3.0**, **eSpeak NG 1.52.0**.

## Upstream credits

- **Phonemizer:** Mathieu Bernard and Hadrien Titeux, [JOSS 6(68), 3958 (2021)](https://doi.org/10.21105/joss.03958). [Software license](https://github.com/bootphon/phonemizer#licence).
- **eSpeak NG:** the eSpeak NG contributors, based on Jonathan Duddington's eSpeak. [Software license](https://github.com/espeak-ng/espeak-ng/blob/master/COPYING).
- **ECDICT:** Copyright (c) 2025 Linwei. [MIT license](https://github.com/skywind3000/ECDICT/blob/master/LICENSE).

Third-party works retain their own licenses.

## Bundled data and Unicode notices

The offline resources retain the fixed [data source record](data/SOURCES.json),
[upstream notices](data/UPSTREAM-SOURCES.md) and [data license](data/LICENSE).
Phonemizer and eSpeak NG produced source IPA; their executables and source
databases are not required at runtime. No Python review/source database is shipped.

The fixed source record names Frequency List by **Fabien Snauwaert** but does not
provide a separate Frequency List license text. This provenance gap remains
recorded; some external category lists also lack per-label source/license
records. Lingose's CC BY 4.0 declaration does not relicense third-party material
or resolve these gaps.

The query and annotation Unicode tables derive from the pinned CPython 3.12 /
Unicode 15.0 behavior. Preserve the bundled [Unicode License V3](third_party/unicode/LICENSE.txt),
including **Copyright © 1991-2026 Unicode, Inc.** The
[distribution provenance record](docs/distribution-provenance.json) retains its
historical identity and loader dependency snapshot; it is not an inventory of
the new CLI's dependencies.

## Library software dependencies (0.2.0)

The current workspace `Cargo.lock` and local dependency manifests were checked
with the default features used by the library. These are software licenses,
separate from the project/data license:

| Dependency | Locked version | Manifest license |
| --- | --- | --- |
| `sha2` (direct) | 0.10.9 | MIT OR Apache-2.0 |
| `cfg-if` | 1.0.5 | MIT OR Apache-2.0 |
| `cpufeatures` | 0.2.17 | MIT OR Apache-2.0 |
| `digest` | 0.10.7 | MIT OR Apache-2.0 |
| `block-buffer` | 0.10.4 | MIT OR Apache-2.0 |
| `crypto-common` | 0.1.7 | MIT OR Apache-2.0 |
| `generic-array` | 0.14.7 | MIT |
| `typenum` | 1.20.1 | MIT OR Apache-2.0 |
| `version_check` (build dependency) | 0.9.5 | MIT/Apache-2.0 |
| `libc` (conditional) | 0.2.190 | MIT OR Apache-2.0 |

`version_check`'s license field above preserves its manifest spelling.
Of the five planned release targets, `libc` is enabled by `cpufeatures` on
aarch64 Linux/macOS; the x86_64 targets use the other nine external dependencies.
Target dependency resolution was inspected offline; this is not target build or
execution evidence. Cargo handles the dependency sources and their own license
files; a standalone binary distribution must also retain its required notices.
The CLI's argument/JSON dependencies are declared separately in its source notices.
