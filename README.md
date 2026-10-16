# Lingose for Rust

`lingose` is a Rust library in development for the
[IPSM Approach](https://lingose.com/) to English pronunciation, spelling and
meaning. The planned first release is **0.1.0**.

This checkout implements **P2.3 pronunciation, morphology, root and meaning queries**
using the bundled offline lexicon. Category queries and text annotation remain
under development and return `Error::NotImplemented`, including empty text.
Registry publication is disabled in `Cargo.toml` during development.

The reproducible lexicon/frequency resources, expected Rust identities and
source notices are checked in. Their export and independent full-record
verification are described in [the data export guide](docs/data-export.md).
The loader validates and shares the two embedded resources independently,
including cached initialization failures. See [loader validation](docs/data-loader.md).
Simple queries use fixed Python 3.12 / Unicode 15.0 casing tables, with
[query verification](docs/simple-queries.md) covering the P0 samples and isolated
fallback, unavailable-field and resource-error cases.

The completed release will bundle all required data for offline use, without
Python, Node, adjacent source repositories, configuration or lexicon downloads
at build time or first use.

IPA is phonetic transcription; IPS marks pronunciation on the spelling; ISM
divides a word into morphemes; IPSM combines IPS with ISM. Learn more at
[lingose.com](https://lingose.com/). GitHub: [englishword](https://github.com/englishword).

## Query a word

```rust
use lingose::Result;

fn main() -> Result<()> {
    println!("{:?}", lingose::ipa("apple")?);
    println!("{:?}", lingose::ips("running")?);
    println!("{:?}", lingose::ism("running")?);
    println!("{:?}", lingose::ipsm("running")?);
    println!("{:?}", lingose::root_lemma("running")?);
    println!("{:?}", lingose::meaning("apple")?); // English by default
    println!("{:?}", lingose::meaning_with_lang("apple", "zh")?);
    Ok(())
}
```

`IPA`, `IPS`, `ISM` and `IPSM` are re-exports of the corresponding lowercase
functions, with the same signatures and behavior. No public `lookup` or `rank`
API is planned.

Queries first use the exact word. Only when no such entry exists, the first
character is uppercase and every later character is not uppercase, they try
the lowercase form: `Apple` can fall back, while `US`, `iPhone` and `McDonald`
cannot. An existing entry with an unavailable field stops lookup. Saved values
are returned unchanged, without adjusting their case or deriving new forms.

Category functions (`kind`, `kind_with_label`, `kind_list`,
`kind_list_with_label`, `labels`) will be implemented in P2.4; the default
category is `CET4`.

## Annotate plain text

```rust,no_run
fn main() -> lingose::Result<()> {
    let text = "Abandon the book.";
    println!("{}", lingose::annotate_ips(text)?); // skip_top = 0
    println!("{}", lingose::annotate_ips_with_skip_top(text, 1000)?);
    Ok(())
}
```

Rust expresses Python's default arguments through the default entry points and
explicit `*_with_lang`, `*_with_label` and `*_with_skip_top` functions. `skip_top`
is an `i64`; negative values are rejected. The completed annotation will cap
nonnegative thresholds at 5062 and preserve case, whitespace and punctuation.

## Results and errors

All calls are synchronous and return `lingose::Result<T>`. Lists own their
`Vec<String>` values, optional fields own their `Option<String>` values, and
annotation returns a `String`. Callers can retain or modify results independently
of the input and internal lexicon.

Valid unknown or unavailable results are `Ok(Vec::new())` for pronunciations
and `Ok(None)` for optional fields. Present empty strings, original Unicode and
newlines are preserved. IPA, IPS and IPSM lists are independent and must not be
paired by index. `meaning` defaults to English; `meaning_with_lang` accepts only
exact `en` or `zh`. Parameter errors and damaged or incompatible data return `Err`.
Completed category queries will return `Ok(false)` for an unknown word.
`Error` implements `std::error::Error` and `Display` and is non-exhaustive.

```rust
use lingose::{ipa, Error};

assert!(matches!(
    ipa(" apple"),
    Err(Error::InvalidArgument { parameter: "word", .. })
));
```

Rust rejects incorrect argument types at compile time:

```rust,compile_fail
lingose::ipa(123);
```

```rust,compile_fail
lingose::annotate_ips_with_skip_top("apple", true);
```

The full signatures, Python correspondence, validation order and implementation
boundaries are recorded in [the Rust interface contract](docs/rust-api.md).

## Development requirements

Edition **2024**, intended minimum Rust version **1.85**. The minimum version
has not yet been tested; this implementation is checked on Rust/Cargo **1.93.1**,
`x86_64-pc-windows-msvc`. This is not cross-platform or final-release validation.
The resource loader uses `sha2` 0.10.9 for SHA-256 integrity checks. The crate has
no build script, database driver or download step. Declared dependency minimum
versions are recorded in the loader evidence; actual minimum-toolchain testing
remains P5.2 work.

```sh
cargo check --offline --all-targets --all-features
cargo test --offline --all-features
```

Complete compilable examples are in `examples/query.rs` and
`examples/annotate.rs`. The query example runs offline; annotation currently
reports `Error::NotImplemented`.

## License and credits

[CC BY 4.0](./LICENSE). Original Lingose data and notation by **詹先觉 (ZHAN Xianjue)**,
[lingose.com](https://lingose.com/). The existing upstream license and
[source attributions](SOURCES.md) are preserved. Third-party works retain their
own licenses. Derived Unicode casing tables retain the
[Unicode License V3](third_party/unicode/LICENSE.txt); their provenance is in
[query-case.json](docs/query-case.json). Final distribution review remains P5.1.
