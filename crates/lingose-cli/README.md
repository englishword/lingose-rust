# Lingose CLI

`lingose-cli` **0.2.0** provides offline English word queries and plain-text IPS
annotation. Its executable is named `lingose`; the separate `lingose` library
owns the lexicon and algorithms. Learn about the IPSM Approach at
[lingose.com](https://lingose.com/). Source:
[englishword/lingose-rust](https://github.com/englishword/lingose-rust).

**0.2.0 has not been published.** Registry commands in this guide apply after the 0.2.0 release;
current usage is through the source build below.

## Install or build

After publication, install with Rust/Cargo **1.85 or newer**:

```sh
cargo install lingose-cli --version 0.2.0 --locked
```

The usual unpinned command is `cargo install lingose-cli`. Cargo may download
software dependencies during installation; lexicon data is bundled with the
library and is never downloaded by a build script or on first use. Once built,
only the executable is needed at runtime: no Python, Node, Cargo cache, SQLite
installation, configuration or external lexicon directory.

For the current checkout, prepare Cargo dependencies and build from the workspace
root (edition 2024, MSRV 1.85):

```sh
cargo build --offline --locked -p lingose-cli
```

Add `target/debug` to PATH, or replace `lingose` in the examples with
`target/debug/lingose` (`target/debug/lingose.exe` on Windows). Published Cargo
installs put the executable in Cargo's binary directory, which must be on PATH.
Release download assets and other-platform execution have not yet been verified.

## Commands and help

There are two business commands:

```text
lingose word WORD [--json]
lingose annotate [TEXT_OR_PATH | --input PATH | --text TEXT] [--skip-top N] [--json] [-o PATH]
```

```sh
lingose --help
lingose --version
lingose word --help
lingose annotate --help
lingose help annotate
```

Help/version go to stdout and exit 0 without reading stdin or creating output.
There is no interactive prompt or shell plugin; integration uses stdin, stdout,
stderr and exit codes.

## Query a word

```sh
lingose word hello
lingose word hello --json
lingose word -- --help
```

The last command queries the literal word `--help`. Both formats contain only:

| Field | JSON type and meaning |
| --- | --- |
| `word` | String, the original argument |
| `ipa` | Independent array of selected, available IPA strings |
| `ips` | Independent array of selected, available IPS strings |
| `ism` | Adopted morpheme division, string or null |
| `ipsm` | Independent array of IPSM strings with valid saved dependencies |
| `root_lemma` | Saved word-family value, string or null |

Plain output uses one labeled field per line with JSON-encoded values so arrays,
nulls, quotes and control characters are unambiguous. JSON is one pretty-printed
object with a final newline; its key order is not part of the interface. IPA,
IPS and IPSM may have different lengths and must not be paired by index.

Queries try exact spelling first. Only a missing entry with an uppercase first
character and no later uppercase character may fall back to lowercase. Existing
unavailable fields stop fallback. Unknown words succeed with empty arrays and
nulls; invalid arguments and resource failures are errors. Word arguments must
be nonempty, contain no NUL and have no surrounding Python whitespace.

CLI queries omit meanings, categories and other auxiliary fields. All library
APIs remain available through the
[library guide](https://github.com/englishword/lingose-rust/blob/main/crates/lingose/README.md).

## Annotate text or a file

In the file examples, `input.txt` and `article.txt` are existing UTF-8 files.

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

The optional positional input reads an existing regular file, otherwise it is
text. Directories, non-regular files, broken symlinks and file access/read errors
fail. Text that cannot form a path, such as a long sentence or characters
forbidden in Windows file names, is accepted as text. `--input` always requires a
regular file; `--text` always uses the exact text. These three forms are mutually
exclusive. For a leading hyphen use:

```sh
lingose annotate -- --hello
lingose annotate --text=--hello
```

`--skip-top` defaults to 0 and accepts a signed 64-bit integer. Negative values
fail; values above 5062 use 5062. Words, saved inflections and phrases whose
original frequency number is at most the threshold stay unchanged. All other
annotation follows the library, including contextual `the`, apostrophes,
hyphens, word forms and unknown parts in brackets. The CLI reads the complete
text and calls `annotate_ips_skip` once, preserving cross-line context; it does
not parse HTML.

## Read stdin and preserve UTF-8

With no explicit input, `annotate` reads stdin until EOF. PowerShell examples:

```powershell
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
"hello world" | lingose annotate
Get-Content -Raw -Encoding UTF8 article.txt | lingose annotate
```

The encoding setup is especially relevant to Windows PowerShell 5.1 when piping
non-ASCII text. POSIX-style examples:

```sh
cat article.txt | lingose annotate
printf 'the\napple' | lingose annotate
```

Files and stdin must contain valid UTF-8; invalid encoding is an execution error.
The CLI passes the complete text to the library, which annotates English tokens
while preserving Unicode, BOM, whitespace, punctuation and LF/CRLF. Empty input
succeeds with empty plain output. The CLI adds no newline. A shell may prepend a
BOM, decode or re-encode input, and append or change newlines before sending stdin,
even after UTF-8 is selected; PowerShell's
`Get-Content` pipeline is not an exact file-byte transport. Use `--input` and
`-o` for file-byte control, rather than relying on shell redirection encoding.
The documented shell examples were checked on Windows PowerShell 5.1 and Git
for Windows Bash; Linux/macOS execution remains pending.

## JSON and output files

`annotate --json` returns one pretty-printed UTF-8 JSON object with a final
newline and exactly two string fields: `text` is the complete original input;
`annotate` is the complete library result. Quotes, control characters and line
endings are escaped so JSON decoding restores the strings.

By default the selected format goes to stdout. `-o PATH` writes it to a file and
leaves stdout empty on success. Existing files are overwritten; parent
directories must exist. Arguments, full input reading and annotation all finish
before the output file is opened. Failures in those steps preserve an existing
destination and do not create a new one. Input and output may be the same file.
Once writing starts, an I/O failure can leave a partial file; replacement is not
atomic. No progress messages are mixed into output.

## Errors and exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success, legal unknown word, empty annotation, help or version |
| `2` | Usage/argument error, including conflicting inputs, invalid word or threshold |
| `1` | I/O/encoding failure, corrupt/incompatible data or another execution failure |

Results go to stdout or the selected output file; diagnostics go to stderr.
Input/parameter/library failures emit no result. Write and flush failures report
execution errors and may follow partial output. Resource errors are propagated,
even for unknown words; they are never converted to empty successful queries.
Shell exit-code variables differ: PowerShell uses `$LASTEXITCODE`, Bash uses `$?`.

## License and validation

Original Lingose data and notation by **ZHAN Xianjue**.
Project license: [CC BY 4.0](LICENSE). Retain the [source and dependency notices](SOURCES.md),
including third-party credits and the recorded Frequency List license gap.
Clap and serde_json use `MIT OR Apache-2.0`; transitive dependencies retain their
own licenses. These declarations do not relicense third-party data or software.

The locked 0.2.0 workspace passed CLI4.1 on Windows x86_64 MSVC with Rust/Cargo
1.85.0 and 1.93.1, including 29 CLI tests. Full library differential and release
performance evidence is in the
[workspace acceptance record](https://github.com/englishword/lingose-rust/blob/main/docs/cli-workspace-acceptance.md).
New-path first-run latency exceeded the startup budget and is reported separately.
Source examples are separate from real archive, registry-install and Release
asset acceptance. Website/repository links do not establish remote permissions
or publication status.
