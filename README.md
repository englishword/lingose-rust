# Lingose Rust workspace

`lingose` is a Rust library for the [IPSM Approach](https://lingose.com/) to
English pronunciation, spelling and meaning. Version **0.1.0** has been released;
this workspace is being prepared for **0.2.0**.

The workspace contains the [offline library](crates/lingose/README.md) and the
[CLI scaffold](crates/lingose-cli/README.md), both version 0.2.0. The CLI commands
and the planned shorter annotation function name are not implemented yet.
Both packages have publication disabled during development.

The [workspace migration record](docs/workspace-migration.md) describes the
verified structure and the remaining development work.

All word queries, category lists and plain-text IPS annotation are implemented.
The checkout embeds **50,335 word entries**, **24 categories** and a frequency
index with **10,620 word keys**. All required lexicon data is bundled, cargo
dependencies must be available before an offline build.

The two resources are validated and indexed once on first use, then shared
across calls and threads.

IPA is phonetic transcription; IPS marks pronunciation on the spelling; ISM
divides a word into morphemes; IPSM combines IPS with ISM. Learn more at
[lingose.com](https://lingose.com/). GitHub: [englishword/lingose-rust](https://github.com/englishword/lingose-rust).

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
    println!("{}", lingose::kind("apple")?); // CET4 by default
    println!("{}", lingose::kind_with_label("apple", "IELTS")?);
    println!("{}", lingose::kind_list()?.len()); // Complete CET4 list
    println!("{}", lingose::kind_list_with_label("IELTS")?.len());
    println!("{:?}", lingose::labels()?);
    Ok(())
}
```

`IPA`, `IPS`, `ISM` and `IPSM` are re-exports of the corresponding lowercase
functions, with the same signatures and behavior. All functions return
`lingose::Result<T>`:

| Function | Successful result | Default or explicit option |
| --- | --- | --- |
| `ipa` / `IPA` | `Vec<String>` of selected, available IPA values | Word |
| `ips` / `IPS` | `Vec<String>` of selected, available IPS values | Word |
| `ism` / `ISM` | `Option<String>` containing the adopted morpheme division | Word |
| `ipsm` / `IPSM` | `Vec<String>` of selected IPSM values with valid dependencies | Word |
| `root_lemma` | `Option<String>` containing the saved word-family value | Word |
| `meaning` / `meaning_with_lang` | `Option<String>` containing the original meaning | `en`; explicit `en` or `zh` |
| `kind` / `kind_with_label` | `bool` category membership | `CET4`; explicit exact label |
| `kind_list` / `kind_list_with_label` | `Vec<String>` containing the complete ordered category list | `CET4`; explicit exact label |
| `labels` | `Vec<String>` of registered boolean category labels | Configuration order |
| `annotate_ips` / `annotate_ips_with_skip_top` | `String` containing the complete annotated text | `0`; explicit inclusive frequency threshold |

`root_lemma` returns saved data rather than running a new lemmatizer. Missing,
conflicting, unreviewed and invalid pronunciation candidates are excluded;
IPSM is returned only when its saved IPS/ISM dependencies remain valid.

Queries first use the exact word. Only when no such entry exists, the first
character is uppercase and every later character is not uppercase, they try
the lowercase form: `Apple` can fall back, while `US`, `iPhone` and `McDonald`
cannot. An existing entry with an unavailable field stops lookup. Saved values
are returned unchanged, without adjusting their case or deriving new forms.

`kind` and `kind_list` default to `CET4`; their `*_with_label` forms accept an
exact registered label such as `IELTS`. Labels are case-sensitive and are listed
by `labels()` in configuration order. `COLLINS` and `Band` are attributes, not
registered categories. `kind_list` returns every member's original word key in
saved root/rank/word business order, without generating case aliases. Invalid
labels return an error even for unknown words; registered empty lists succeed.

## Annotate plain text

```rust
fn main() -> lingose::Result<()> {
    let text = "Abandon the book. The apple and the hour.";
    println!("{}", lingose::annotate_ips(text)?); // skip_top = 0
    println!("{}", lingose::annotate_ips_with_skip_top(text, 1000)?);
    Ok(())
}
```

Rust expresses Python's default arguments through the default entry points and
explicit `*_with_lang`, `*_with_label` and `*_with_skip_top` functions. `skip_top`
is an `i64`; negative values are rejected, and values above 5062 use 5062.
Frequency filtering keeps stored words and inflections with original
`NUMBER <= skip_top` unchanged, including equality and original numbering gaps.
Repeated words use their earliest number. Filtering also protects complete stored
phrases and punctuation forms such as `one hundred` and `Messrs.`. Longer forms
take priority, and Unicode word boundaries keep adjacent unknown text separate.
Filtering precedes unavailable-state checks and fallback; it does not invent
new skipped inflections.

Annotation preserves case, whitespace and punctuation. Only complete English
tokens are annotated; non-English spans, digits and mixed tokens such as `café`
or `apple123` pass through unchanged. Empty text or text without a complete
English token is returned unchanged without accessing either resource, for any
nonnegative threshold. Zero never loads frequency data. Positive thresholds check
the frequency resource followed by the lexicon, even when every token is skipped.
The API accepts plain text; HTML tags are treated as text rather than parsed as
a document.

`the` uses the next English token's first letter across whitespace and selected
quotes/brackets, stopping at punctuation or blank lines. Saved whole-word IPS
values take priority over contraction, hyphen, apostrophe and `s/es/ed/ing`
fallback. Blocked entries stop fallback; unknown parts use `[brackets]`.
Word-form fallback retains aligned stem marks and original suffix spelling;
ambiguous results remain bracketed. These text rules never update word queries.

## Results and errors

All calls are synchronous. Lists own their `Vec<String>` values, optional fields
own their `Option<String>` values, and annotation returns a `String`. Callers can
retain or modify results independently of the input and internal lexicon.

Valid unknown or unavailable results are `Ok(Vec::new())` for pronunciations,
`Ok(None)` for optional fields and `Ok(false)` for category membership. Present
empty strings, original Unicode and newlines are preserved. IPA, IPS and IPSM
lists are independent and must not be paired by index. `meaning` defaults to
English; `meaning_with_lang` accepts only exact `en` or `zh`. An exact entry with
false or unavailable membership blocks lowercase fallback.

Word arguments must be nonempty, contain no NUL and have no surrounding Python
whitespace; internal spaces and punctuation are allowed. Annotation accepts
empty text and surrounding whitespace, rejects NUL, and checks a negative
threshold before checking text. Word validation precedes language validation and
resource loading; category-label validation follows resource loading.

`Error` implements `std::error::Error` and `Display` and is non-exhaustive:

| Error variant | Meaning |
| --- | --- |
| `InvalidArgument { parameter, reason }` | A correctly typed argument has invalid contents. |
| `Data { resource, message }` | A required bundled resource failed validation. |
| `IncompatibleDataVersion { resource, expected, found }` | A bundled data version is unsupported or inconsistent. |

Callers matching errors must include a fallback arm. Error messages are
diagnostic text; the variant and parameter identify the failure. Resource errors
are propagated even for unknown words.

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

The full signatures, Python correspondence and validation order are recorded in
[the current Rust interface contract](crates/lingose/docs/rust-api.md).

## Development and validation

Edition **2024**, minimum Rust version **1.85**. The checked-in dependency
resolution has been tested with Rust/Cargo **1.85.0** and **1.93.1** on
`x86_64-pc-windows-msvc`. The resource loader
uses `sha2` 0.10.9 for integrity checks. The crate has no build script, database
driver or download step.

```sh
cargo check --offline --locked --all-targets --all-features
cargo test --offline --locked --all-features
```

Complete compilable examples are [query.rs](crates/lingose/examples/query.rs) and
[annotate.rs](crates/lingose/examples/annotate.rs). Run them with
`cargo run --offline --locked -p lingose --example query` and
`cargo run --offline --locked -p lingose --example annotate`.

The pre-documentation baseline passed a full Python differential comparison of
1,862,690 public results and release performance checks under fixed warmup
conditions. These are historical Windows results, rather than measurements of
the final package. A newly copied executable's first run exceeded the startup
budget; the measurements do not guarantee that latency. Other-platform and
registry acceptance remain pending.

## License and credits

Project license: [CC BY 4.0](./LICENSE). Original Lingose data and notation by
**ZHAN Xianjue**, [lingose.com](https://lingose.com/). The original license,
author attribution and [source notices](SOURCES.md) are preserved.
