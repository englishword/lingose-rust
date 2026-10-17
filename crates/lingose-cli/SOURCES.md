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

## CLI software dependencies

The CLI calls `lingose` **0.2.0**, which owns all bundled data, Unicode tables,
queries and annotation. Retain the
[library's data and software notices](https://github.com/englishword/lingose-rust/blob/main/crates/lingose/SOURCES.md),
including the Frequency List credit to **Fabien Snauwaert** and the recorded lack
of a separate Frequency List license text. The project CC BY 4.0 declaration
does not resolve that provenance gap or relicense third-party material.
Unicode-derived tables retain
[Unicode License V3](https://github.com/englishword/lingose-rust/blob/main/crates/lingose/third_party/unicode/LICENSE.txt)
and **Copyright © 1991-2026 Unicode, Inc.**

In addition to the library's `sha2` dependency closure, the CLI uses
[Clap](https://github.com/clap-rs/clap) for arguments and
[serde_json](https://github.com/serde-rs/json) for JSON. The current workspace
`Cargo.lock` and local dependency manifests were checked with the enabled
features (`std`, `help`, `usage`, `error-context` for Clap; default serde_json):

| Additional dependency | Locked version | Manifest license |
| --- | --- | --- |
| `clap` (direct), `clap_builder` | 4.6.7 | MIT OR Apache-2.0 |
| `clap_lex` | 1.1.1 | MIT OR Apache-2.0 |
| `anstyle` | 1.0.14 | MIT OR Apache-2.0 |
| `serde_json` (direct) | 1.0.154 | MIT OR Apache-2.0 |
| `serde_core` | 1.0.229 | MIT OR Apache-2.0 |
| `itoa` | 1.0.18 | MIT OR Apache-2.0 |
| `memchr` | 2.8.3 | Unlicense OR MIT |
| `zmij` | 1.0.23 | MIT |

These nine extra crates plus the library closure total 18 external crates on the
three planned x86_64 targets and 19 on aarch64 Linux/macOS (conditional `libc`).
Other lockfile entries can belong to disabled features/target conditions; the
lockfile is not a list of everything compiled into the binary. Offline target
dependency resolution is separate from target build and execution acceptance.

Dependency licenses remain separate from Lingose's CC BY 4.0. Cargo handles
dependency source/license files during source installation; standalone release
assets must include applicable notices and license texts in their own stage.
No new CLI dependencies have been added to the preserved historical loader or
distribution provenance records.
