# Lingose CLI

`lingose-cli` **0.2.0** is the command-line package in the
[Lingose Rust workspace](https://github.com/englishword/lingose-rust).
Its executable is named `lingose` and depends on the offline `lingose` library.
Learn about IPSM at [lingose.com](https://lingose.com/).

Word queries, text/file/stdin annotation, JSON/file output and standard help/version
commands are implemented in this checkout.
Publication remains disabled; these commands describe the local 0.2.0 development version.

The library owns all lexicon data and algorithms. Queries and annotation run offline with
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

## Annotate text

```sh
lingose annotate "This is an English word."
lingose annotate --skip-top 1000 "This is an English word."
lingose annotate input.txt
lingose annotate --input input.txt
lingose annotate --text "input.txt"
lingose annotate input.txt -o output.txt
lingose annotate "hello world" --json
lingose annotate --input input.txt --json -o output.json
```

The optional positional input is read as a file when it names an existing regular
file; otherwise it is text. Directories, non-regular files, broken symlinks and
file access/read errors fail. Text that cannot form a path, such as a long sentence
or characters forbidden in Windows file names, is still accepted as text.
`--input` always requires a regular file; `--text` always uses the exact text.
These three input forms are mutually exclusive. With no input argument, the CLI
reads stdin until EOF:

```powershell
"hello world" | lingose annotate
Get-Content article.txt | lingose annotate
```

```sh
cat article.txt | lingose annotate
printf 'the\napple' | lingose annotate
```

Files and stdin must contain valid UTF-8. The CLI reads the complete input and
calls `lingose::annotate_ips_skip` once, preserving cross-line context, whitespace,
Unicode, BOM and LF/CRLF. It writes the library result to stdout without adding a
newline. Shell pipelines may add a BOM or change encoding/line endings before the
CLI receives bytes; `--input` reads the file bytes directly. On Windows PowerShell 5.1,
set `$OutputEncoding` to UTF-8 when piping non-ASCII text.

`--skip-top` defaults to 0. Numeric values use the library's validation and cap:
negative values fail, and values above 5062 use 5062. Argument and library parameter
errors exit 2; input encoding, file/stdin I/O and output failures exit 1. Input
and parameter errors produce no annotation result. For text starting with a hyphen, use
`lingose annotate -- --hello` or `lingose annotate --text=--hello`.

## Annotation output

Plain annotation output contains exactly the library result, without an added
newline. `--json` returns one UTF-8 JSON object containing only two string fields:
`text` is the original input and `annotate` is its complete annotation. Quotes,
control characters and line endings are JSON-escaped; decoding restores the
original strings. JSON is pretty-printed with a final newline.

By default the selected format goes to stdout. `-o PATH` writes it to a file and
leaves stdout empty on success; existing files are overwritten and parent
directories must already exist. The CLI parses arguments, reads all input and
finishes annotation before opening the output file, so failures in those steps
preserve an existing destination and do not create a new one. Input and output
may name the same file. Once writing starts, an I/O failure can leave a partial
file; output replacement is not atomic.

File/stdout write or flush errors exit 1 and report to stderr. The same error
codes apply with `--json` and `-o`; neither format adds progress messages to the
result. Help/version exit 0 without reading input or creating an output file.

Original Lingose data and notation by **ZHAN Xianjue**.
License: [CC BY 4.0](LICENSE). [Source notices](SOURCES.md).
