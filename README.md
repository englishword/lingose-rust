# Lingose for Rust

`lingose` is a Rust library in development for the
[IPSM Approach](https://lingose.com/) to English pronunciation, spelling and
meaning. The planned first release is **0.1.0**.

This checkout is the **P1.1 interface skeleton**. Argument validation works;
production lexicon data, queries and text annotation are not implemented yet.
Valid calls return `Error::NotImplemented`, including unknown words and empty
text. The examples compile but cannot yet produce lexicon or annotation output.
Registry publication is disabled in `Cargo.toml` during development.

The completed release will bundle all required data for offline use, without
Python, Node, adjacent source repositories, configuration or lexicon downloads
at build time or first use.

IPA is phonetic transcription; IPS marks pronunciation on the spelling; ISM
divides a word into morphemes; IPSM combines IPS with ISM. Learn more at
[lingose.com](https://lingose.com/). GitHub: [englishword](https://github.com/englishword).

## Query a word

```rust,no_run
use lingose::Result;

fn main() -> Result<()> {
    println!("{:?}", lingose::ipa("apple")?);
    println!("{:?}", lingose::ips("running")?);
    println!("{:?}", lingose::ism("running")?);
    println!("{:?}", lingose::ipsm("running")?);
    println!("{:?}", lingose::root_lemma("running")?);
    println!("{:?}", lingose::meaning("apple")?); // English by default
    println!("{:?}", lingose::meaning_with_lang("apple", "zh")?);
    println!("{}", lingose::kind("apple")?); // CET4 by default
    println!("{:?}", lingose::kind_list_with_label("IELTS")?);
    println!("{:?}", lingose::labels()?);
    Ok(())
}
```

`IPA`, `IPS`, `ISM` and `IPSM` are re-exports of the corresponding lowercase
functions, with the same signatures and behavior. No public `lookup` or `rank`
API is planned.

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

Once implemented, valid unknown or unavailable results will be `Ok(Vec::new())`
for pronunciations, `Ok(None)` for optional fields, and `Ok(false)` for category
membership. Parameter errors and damaged or incompatible data will return `Err`.
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
has not yet been tested; the P1.1 skeleton is checked on Rust/Cargo **1.93.1**,
`x86_64-pc-windows-msvc`. This is not cross-platform or final-release validation.
There are currently no third-party dependencies or build scripts. Later runtime
dependencies must support the declared minimum version and offline data use.

```sh
cargo check --offline --all-targets --all-features
cargo test --offline --all-features
```

Complete compilable examples are in `examples/query.rs` and
`examples/annotate.rs`. Running them currently reports `Error::NotImplemented`.

## License and credits

[CC BY 4.0](./LICENSE). Original Lingose data and notation by **詹先觉 (ZHAN Xianjue)**,
[lingose.com](https://lingose.com/). The existing upstream license and
[source attributions](SOURCES.md) are preserved. Third-party works retain their
own licenses; resource-specific notices will be completed when data is bundled.
