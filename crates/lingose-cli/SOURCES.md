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

In addition to the `lingose` library, the CLI uses
[Clap](https://github.com/clap-rs/clap) for argument parsing and
[serde_json](https://github.com/serde-rs/json) for JSON. Both use the
`MIT OR Apache-2.0` license; their licenses remain separate from Lingose's
CC BY 4.0 license. Exact direct and transitive versions are in the workspace
`Cargo.lock`. The complete distribution license review is part of CLI4.2.
