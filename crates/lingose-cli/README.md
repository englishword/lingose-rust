# Lingose CLI

`lingose-cli` **0.2.0** is the command-line package in the
[Lingose Rust workspace](https://github.com/englishword/lingose-rust).
Its executable is named `lingose` and depends on the offline `lingose` library.
Learn about IPSM at [lingose.com](https://lingose.com/).

Word queries and standard help/version commands are implemented in this checkout.
Annotation and text/file/stdin input are still pending. Publication remains disabled;
these commands describe the local 0.2.0 development version.

The library owns all lexicon data and algorithms. Word queries run offline with
the bundled data, without Python, Node or an external lexicon directory.

From the workspace root, build after preparing Cargo dependencies:

```sh
cargo build --offline --locked -p lingose-cli
```

Run the resulting `target/debug/lingose` (`lingose.exe` on Windows):

```sh
lingose --help
lingose --version
lingose word --help
lingose word hello
lingose word hello --json
```

Both formats contain only `word`, `ipa`, `ips`, `ism`, `ipsm` and `root_lemma`.
Plain output uses one labeled field per line, with JSON-encoded values so that
arrays, nulls, quotes and control characters are unambiguous. JSON output is one
object; its key order is not part of the interface. IPA, IPS and IPSM are
independent string arrays, and ISM/root lemma are strings or null. The input word
is preserved, and matching follows the library's exact-first case rules.

Unknown words succeed with empty arrays and null fields. Results and help/version
go to stdout; errors go to stderr. Exit codes are 0 for success, 2 for invalid
arguments or usage, and 1 for resource or output failures. No result is written
when argument validation or a library query fails. Use `lingose word -- --help`
to query a literal word starting with a hyphen.

Command parsing uses Clap's builder API with only `std`, `help`, `usage` and
`error-context` enabled; JSON uses serde_json's default `std` feature. Both are
locked in the workspace and verified with Rust 1.85.

Original Lingose data and notation by **ZHAN Xianjue**.
License: [CC BY 4.0](LICENSE). [Source notices](SOURCES.md).
