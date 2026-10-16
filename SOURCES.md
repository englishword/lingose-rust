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

## Rust adaptation and data provenance

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
Its relative project-license link resolves through the identical copy at
[data/LICENSE](data/LICENSE).

The simple-query casing tables in `src/query_case_tables.rs` derive from the
pinned CPython 3.12 / Unicode 15.0 database. Copyright Unicode, Inc.; licensed
under [Unicode License V3](third_party/unicode/LICENSE.txt). The complete notice
is preserved, with generator, interpreter, input and output identities in
[query-case.json](docs/query-case.json). No compiler Unicode data or JavaScript
UTF-16 ordering is used for these tables.

The P3.1 scanner and restricted IPS NFD/casing tables in
`src/annotation_unicode_tables.rs` also derive from pinned CPython 3.12 /
Unicode 15.0, under the same preserved Unicode License V3. Their generator,
interpreter, installed annotation source and output identities are recorded in
[annotation-unicode.json](docs/annotation-unicode.json). Normalization is used
only to generate alignment predicates; output retains original cluster forms.

The Rust port adapts the Lingose behavior to owned Rust results, bundled binary
resources, shared read-only indexes and fixed Unicode tables. Its implementation
changes are recorded in this repository's Git history. The project license does
not relicense third-party works.

### Notice review and retained gaps

The P5.1 review checked the author, original project license, upstream credits,
data provenance and complete local Unicode notice. The original `LICENSE` and
`data/UPSTREAM-SOURCES.md` still match the pinned Python reference byte for byte.
The generated `data/SOURCES.json` is retained as P2.1 provenance, including its
historical note that distribution review was then pending; this section records
the later review without rewriting those protected identities.

The pinned reference attributes the frequency data to Fabien Snauwaert's
[Frequency List](https://frequencylist.com/) and records the source workbook
and database hashes. It supplies no separate license text or license record
establishing distribution terms for this derivative. Those source facts are
retained; Lingose's CC BY 4.0 declaration is not evidence of authorization for
that third-party material. Some external vocabulary lists used for category
reconstruction are mentioned collectively by upstream without per-label source
identities or separate license texts. The review preserves those statements
without inventing missing provenance or claiming that every third-party
permission has been independently verified.

Phonemizer, eSpeak NG and ECDICT credits and license references above are
upstream assertions. Their software is not shipped or required to run this
crate. The fixed reference supplies links rather than separate copies of their
license texts. Unicode's complete local license accompanies the derived tables.

## Rust runtime dependencies

The P2.2 loader uses `sha2` 0.10.9 from the RustCrypto Developers
([upstream](https://github.com/RustCrypto/hashes)), licensed under
`MIT OR Apache-2.0`. Cargo resolves its separately licensed dependencies; the
locked versions, declared licenses and minimum Rust versions are recorded in
[loader-verification.json](docs/loader-verification.json). These software
licenses remain separate from the Lingose data license. The referenced loader
record describes the P2.2 locked dependency snapshot; it is not a new audit of
future dependency resolutions.
