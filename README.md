# Lingose Rust

Offline English word queries and plain-text IPS annotation for the
[IPSM Approach](https://lingose.com/) to pronunciation, spelling and meaning.
This workspace contains the [lingose library](crates/lingose/README.md) and
[lingose-cli](crates/lingose-cli/README.md); the executable is named `lingose`.
Source repository: [englishword/lingose-rust](https://github.com/englishword/lingose-rust).

**The library `lingose 0.2.0` and `lingose-cli 0.2.0` are published on crates.io.**
GitHub Release assets and fresh registry-install acceptance remain separate steps.

## Command line

Install with Rust/Cargo 1.85 or newer:

```sh
cargo install lingose-cli --version 0.2.0 --locked
```

The usual unpinned command is `cargo install lingose-cli`. For the current
checkout, build from the workspace root after preparing Cargo dependencies:

```sh
cargo build --offline --locked -p lingose-cli
```

Add `target/debug` to PATH or invoke `target/debug/lingose` directly
(`target/debug/lingose.exe` on Windows). Then:

```sh
lingose word hello
lingose word hello --json
lingose annotate "This is an English word."
lingose annotate --skip-top 1000 "This is an English word."
lingose annotate --input input.txt --json -o output.json
lingose --help
lingose annotate --help
```

For a UTF-8 file, `lingose annotate input.txt` automatically reads an existing
regular file. Use `--text "input.txt"` to annotate the same name as text.
Without an input argument, `annotate` reads stdin until EOF:

```powershell
"hello world" | lingose annotate
```

```sh
printf 'the\napple' | lingose annotate
```

Word output contains only `word`, `ipa`, `ips`, `ism`, `ipsm` and `root_lemma`.
Pronunciations are independent arrays; optional fields are strings or null.
Annotation JSON contains only the strings `text` and `annotate`. Plain annotation
adds no newline; `-o` writes the chosen format to a file with no duplicate stdout.
Diagnostics go to stderr. Exit codes are 0 for success, including unknown words
and help/version, 2 for invalid arguments, and 1 for I/O or resource failures.
See the [CLI guide](crates/lingose-cli/README.md) for all options, output overwrite
behavior, UTF-8 shell setup and errors. Pipelines can change input bytes;
`--input`/`-o` avoid shell decoding and re-encoding. Plain annotation output
preserves the input's line endings; JSON escapes them inside strings.

## Rust library

After 0.2.0 is published, add this to your application's `Cargo.toml`:

```toml
[dependencies]
lingose = "0.2.0"
```

In the current checkout, use a path dependency on `crates/lingose` instead.

```rust
fn main() -> lingose::Result<()> {
    println!("{:?}", lingose::ipa("apple")?);
    println!("{:?}", lingose::ipsm("running")?);
    println!("{:?}", lingose::meaning_with_lang("apple", "zh")?);
    println!("{}", lingose::annotate_ips("The apple and the hour.")?);
    println!("{}", lingose::annotate_ips_skip("Abandon the book.", 1000)?);
    Ok(())
}
```

The library also provides IPS, ISM, saved root lemmas, English meanings,
category membership, complete ordered category lists and registered labels.
The [library guide](crates/lingose/README.md) covers every API, default and error;
the [0.2.0 contract](crates/lingose/docs/rust-api.md) gives exact signatures and
the Python correspondence. The CLI's six-field query does not limit library APIs.

**Breaking change from 0.1.0:** replace
`annotate_ips_with_skip_top(text, skip_top)` with
`annotate_ips_skip(text, skip_top)`. The old name has been removed without an
alias; `annotate_ips(text)` still uses zero. Other library behavior is retained.
See [migration details](crates/lingose/docs/rust-api.md#from-010).

## Offline data and validation

The library bundles 50,335 word entries, 24 categories and 10,620 frequency keys.
Builds and first use never download lexicon data. Cargo dependencies must be
available for an offline build; runtime needs no Python, Node, SQLite installation,
configuration or adjacent source checkout. Resources are validated and indexed
once, then shared across calls and threads. Only the CLI binary is needed to run
the built command.

Edition 2024, MSRV 1.85. CLI4.1 verified this 0.2.0 workspace on Windows x86_64
MSVC with Rust/Cargo 1.85.0 and 1.93.1: 131 Rust tests and six doctests per
toolchain, plus a full differential comparison of 1,862,690 public results.
Release performance met the fixed warmed-process budgets; a new executable
path's first run still exceeded the 300 ms startup budget. These measurements
do not guarantee first-run latency. See the
[acceptance record](docs/cli-workspace-acceptance.md).
Native CLI builds and query/annotation/stdin/JSON smoke have passed on Windows
x86_64, Linux x86_64/aarch64 and macOS Intel/Apple Silicon; see the
[CI verification](docs/cli-release-ci.md). Binary archive preparation and
download/extraction verification are tracked in [binary assets](docs/cli-binary-assets.md).
Registry installation and published GitHub Release downloads remain separate acceptance steps.

## License and credits

Original Lingose data and notation by **ZHAN Xianjue**,
[lingose.com](https://lingose.com/). Project license: [CC BY 4.0](LICENSE).
Retain the [source credits](SOURCES.md) and each third party's own license.
Current software dependencies and data provenance boundaries are recorded
separately for the [library](crates/lingose/SOURCES.md) and
[CLI](crates/lingose-cli/SOURCES.md).
