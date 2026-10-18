# Lingose 0.2.0

Offline English word queries and IPS text annotation for the
[IPSM Approach](https://lingose.com/), by ZHAN Xianjue.

- New `lingose-cli` package, executable `lingose`: `word WORD [--json]` and
  `annotate` with text, UTF-8 files, stdin, `--skip-top`, JSON and output files.
- The library and CLI include the dictionary. Runtime needs no Python, Node,
  Cargo, configuration or extra data download.
- Library breaking change: `annotate_ips_with_skip_top(text, n)` is replaced by
  `annotate_ips_skip(text, n)` without an alias. `annotate_ips(text)` is retained.
- Both `lingose 0.2.0` and `lingose-cli 0.2.0` are available on crates.io.
  With Rust/Cargo 1.85 or newer: `cargo install lingose-cli --version 0.2.0 --locked`.

Download the archive for Windows x86_64, Linux x86_64/aarch64 GNU, or macOS
Intel/Apple Silicon. Verify its SHA-256 against `SHA256SUMS`, extract it and read
the enclosed README. Run `lingose --help`, `lingose word apple --json`, or
`lingose annotate --text "Abandon the book."`. Keep the included licenses and
source notices when redistributing.

Five targets are built and tested on native GitHub runners, including a separate
download/extraction job. This does not establish compatibility with older OS
versions. Windows requires a compatible Microsoft Visual C++ v14 x64 Runtime
and Windows/UCRT components. Linux requires system glibc/libgcc_s; macOS uses
libSystem. macOS binaries are not Developer ID signed or notarized; Gatekeeper
acceptance is unverified. First invocation can exceed the measured startup
budget; warmed-process results are separate.

Project license: CC BY 4.0. Third-party materials retain their own licenses.
Included notices disclose the existing Frequency List independent-license gap
and incomplete per-category source/license provenance. Project licensing does
not relicense those materials. See the archive's SOURCES and notices for details.
