# Lingose CLI

`lingose-cli` **0.2.0** is the command-line package in the
[Lingose Rust workspace](https://github.com/englishword/lingose-rust).
Its executable is named `lingose` and depends on the offline `lingose` library.
Learn about IPSM at [lingose.com](https://lingose.com/).

This package is currently a scaffold. Word queries, annotation, argument parsing
and help/version commands are not implemented yet. Running it reports this
status to stderr and exits with code 1. Publication remains disabled.

The planned commands are `word` and `annotate`, with text/file/stdin input and
JSON output. The library owns all lexicon data and algorithms; the CLI does not
download or duplicate them.

From the workspace root, build the scaffold after preparing Cargo dependencies:

```sh
cargo build --offline --locked -p lingose-cli
```

Original Lingose data and notation by **ZHAN Xianjue**.
License: [CC BY 4.0](LICENSE). [Source notices](SOURCES.md).
