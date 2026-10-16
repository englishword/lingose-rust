# Data sources and attribution

Original Lingose data and notation by **詹先觉 (ZHAN Xianjue)**, [lingose.com](https://lingose.com/), licensed under [CC BY 4.0](LICENSE).

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

## Rust port status

The attribution above and the accompanying `LICENSE` are preserved from the
Python reference at commit `b36baf6d55fa259ecc38acea9e881ae6d1477d33`.
Tool versions above describe that reference, not Rust runtime requirements.

The P2.1 resources in `data/lexicon.bin` and `data/frequency.bin` are reproducible
projections of the pinned installed Python Lingose 0.2.0 snapshot. They contain
effective public fields, annotation eligibility, full ordered category lists,
and original frequency thresholds. They omit the maintenance/review database.
Per-resource source identities, snapshot credits and license references are in
[data/SOURCES.json](data/SOURCES.json); the original Python source notice is
preserved verbatim in [data/UPSTREAM-SOURCES.md](data/UPSTREAM-SOURCES.md).

No derived Unicode tables are included yet. Final distribution notices remain
P5.1 work, including the separately documented absence of frequency-list license
text in the pinned reference. The Rust port and its
behavioral specification are adaptations of Lingose, with changes recorded in
this repository's Git history. The project license does not relicense
third-party works.

## Rust runtime dependencies

The P2.2 loader uses `sha2` 0.10.9 from the RustCrypto Developers
([upstream](https://github.com/RustCrypto/hashes)), licensed under
`MIT OR Apache-2.0`. Cargo resolves its separately licensed dependencies; the
locked versions, declared licenses and minimum Rust versions are recorded in
[loader-verification.json](docs/loader-verification.json). These software
licenses remain separate from the Lingose data license. Final distribution
notice review remains P5.1 work.
