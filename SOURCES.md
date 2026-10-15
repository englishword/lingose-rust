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

The Rust P1.1 skeleton contains no production lexicon or derived Unicode data
tables. Data projection and per-resource provenance are scheduled for P2.1;
final distribution notices will be checked in P5.1. The Rust port and its
behavioral specification are adaptations of Lingose, with changes recorded in
this repository's Git history. The project license does not relicense
third-party works.
