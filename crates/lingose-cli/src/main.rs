//! Command-line entry point for offline Lingose queries and IPS annotation.

use std::ffi::OsString;
use std::fmt::Display;
use std::fs;
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use clap::{Arg, ArgAction, ArgGroup, ArgMatches, Command, value_parser};
use serde_json::{Value, json};

const WORD_FIELDS: [&str; 6] = ["word", "ipa", "ips", "ism", "ipsm", "root_lemma"];

fn command() -> Command {
    Command::new("lingose")
        .version(env!("CARGO_PKG_VERSION"))
        .about("Offline Lingose word queries and IPS annotation")
        .subcommand_required(true)
        .arg_required_else_help(true)
        .propagate_version(true)
        .subcommand(
            Command::new("word")
                .about("Query a word's IPA, IPS, ISM, IPSM and root lemma")
                .arg(Arg::new("word").value_name("WORD").required(true))
                .arg(
                    Arg::new("json")
                        .long("json")
                        .help("Output JSON")
                        .action(ArgAction::SetTrue),
                ),
        )
        .subcommand(
            Command::new("annotate")
                .about("Annotate UTF-8 text with IPS; read stdin when no input is given")
                .arg(
                    Arg::new("source")
                        .value_name("TEXT_OR_PATH")
                        .help("Read an existing regular file, otherwise annotate this text")
                        .value_parser(value_parser!(OsString)),
                )
                .arg(
                    Arg::new("input")
                        .long("input")
                        .value_name("PATH")
                        .help("Read a UTF-8 text file")
                        .value_parser(value_parser!(PathBuf)),
                )
                .arg(
                    Arg::new("text")
                        .long("text")
                        .value_name("TEXT")
                        .help("Always interpret the value as text"),
                )
                .group(ArgGroup::new("input-source").args(["source", "input", "text"]))
                .arg(
                    Arg::new("skip-top")
                        .long("skip-top")
                        .value_name("N")
                        .help("Leave words up to this inclusive frequency number unchanged")
                        .default_value("0")
                        .allow_negative_numbers(true)
                        .value_parser(value_parser!(i64)),
                )
                .arg(
                    Arg::new("json")
                        .long("json")
                        .help("Output JSON with the original text and annotation")
                        .action(ArgAction::SetTrue),
                )
                .arg(
                    Arg::new("output")
                        .short('o')
                        .value_name("PATH")
                        .help("Write the selected output format to a file")
                        .value_parser(value_parser!(PathBuf)),
                ),
        )
}

#[derive(Debug)]
enum CliError {
    Library(lingose::Error),
    Io(io::Error),
    NonUnicodeText,
}

impl Display for CliError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Library(error) => error.fmt(formatter),
            Self::Io(error) => error.fmt(formatter),
            Self::NonUnicodeText => formatter.write_str("text argument is not valid Unicode"),
        }
    }
}

impl From<lingose::Error> for CliError {
    fn from(error: lingose::Error) -> Self {
        Self::Library(error)
    }
}

impl From<io::Error> for CliError {
    fn from(error: io::Error) -> Self {
        Self::Io(error)
    }
}

impl CliError {
    fn exit_code(&self) -> u8 {
        match self {
            Self::Library(error) => library_exit_code(error),
            Self::Io(_) => 1,
            Self::NonUnicodeText => 2,
        }
    }
}

fn read_text_file(path: &Path) -> io::Result<String> {
    if !fs::metadata(path)?.is_file() {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            format!("input path is not a regular file: {}", path.display()),
        ));
    }
    fs::read_to_string(path)
}

fn is_text_path_error(error: &io::Error) -> bool {
    if matches!(
        error.kind(),
        io::ErrorKind::NotFound | io::ErrorKind::NotADirectory | io::ErrorKind::InvalidInput
    ) {
        return true;
    }
    // Rust 1.85 predates ErrorKind::InvalidFilename. These narrow OS codes
    // describe invalid/overlong path names, rather than access or read errors.
    let code = error.raw_os_error();
    (cfg!(windows) && matches!(code, Some(123 | 161 | 206)))
        || (cfg!(target_os = "linux") && code == Some(36))
        // macOS also rejects non-UTF-8 filenames with EILSEQ. The caller's
        // Unicode conversion then reports invalid automatic text as usage 2.
        || (cfg!(target_os = "macos") && matches!(code, Some(63 | 92)))
}

fn read_annotation_input(args: &ArgMatches, stdin: &mut impl Read) -> Result<String, CliError> {
    if let Some(text) = args.get_one::<String>("text") {
        return Ok(text.clone());
    }
    if let Some(path) = args.get_one::<PathBuf>("input") {
        return Ok(read_text_file(path)?);
    }
    if let Some(source) = args.get_one::<OsString>("source") {
        // Detect an existing entity first, including dangling symlinks. Once
        // found, target/regular-file/read failures must never become text.
        return match fs::symlink_metadata(source) {
            Ok(_) => Ok(read_text_file(Path::new(source))?),
            Err(error) if is_text_path_error(&error) => source
                .clone()
                .into_string()
                .map_err(|_| CliError::NonUnicodeText),
            Err(error) => Err(error.into()),
        };
    }
    let mut text = String::new();
    stdin.read_to_string(&mut text)?;
    Ok(text)
}

fn query_word(word: &str) -> lingose::Result<Value> {
    Ok(json!({
        "word": word,
        "ipa": lingose::ipa(word)?,
        "ips": lingose::ips(word)?,
        "ism": lingose::ism(word)?,
        "ipsm": lingose::ipsm(word)?,
        "root_lemma": lingose::root_lemma(word)?,
    }))
}

fn write_word(output: &mut impl Write, result: &Value, json: bool) -> io::Result<()> {
    if json {
        writeln!(output, "{result:#}")?;
    } else {
        for field in WORD_FIELDS {
            // JSON values keep list boundaries, nulls and control characters clear.
            writeln!(output, "{field}: {}", result[field])?;
        }
    }
    output.flush()
}

fn write_annotation(
    output: &mut impl Write,
    text: &str,
    annotated: &str,
    json: bool,
) -> io::Result<()> {
    if json {
        let result = json!({ "text": text, "annotate": annotated });
        writeln!(output, "{result:#}")?;
    } else {
        output.write_all(annotated.as_bytes())?;
    }
    output.flush()
}

fn library_exit_code(error: &lingose::Error) -> u8 {
    match error {
        lingose::Error::InvalidArgument { .. } => 2,
        _ => 1,
    }
}

fn report_error(error: &impl Display, code: u8) -> ExitCode {
    let _ = writeln!(io::stderr().lock(), "error: {error}");
    ExitCode::from(code)
}

fn run(
    matches: &ArgMatches,
    stdin: &mut impl Read,
    stdout: &mut impl Write,
) -> Result<(), CliError> {
    match matches.subcommand().expect("clap requires a subcommand") {
        ("word", args) => {
            let word = args.get_one::<String>("word").expect("clap requires WORD");
            write_word(stdout, &query_word(word)?, args.get_flag("json"))?;
        }
        ("annotate", args) => {
            let text = read_annotation_input(args, stdin)?;
            let skip_top = *args.get_one::<i64>("skip-top").expect("clap defaults N");
            let annotated = lingose::annotate_ips_skip(&text, skip_top)?;
            let json = args.get_flag("json");
            if let Some(path) = args.get_one::<PathBuf>("output") {
                // Open only after the complete input and library call succeed,
                // including when input and output name the same file.
                write_annotation(&mut fs::File::create(path)?, &text, &annotated, json)?;
            } else {
                write_annotation(stdout, &text, &annotated, json)?;
            }
        }
        _ => unreachable!("clap accepts only word and annotate"),
    }
    Ok(())
}

fn main() -> ExitCode {
    let matches = match command().try_get_matches() {
        Ok(matches) => matches,
        Err(error) => {
            let code = error.exit_code() as u8;
            return match error.print() {
                Ok(()) => ExitCode::from(code),
                Err(error) => report_error(&error, 1),
            };
        }
    };
    match run(&matches, &mut io::stdin().lock(), &mut io::stdout().lock()) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => report_error(&error, error.exit_code()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stdin_read_failure_does_not_emit_partial_annotation() {
        struct FailingReader;
        impl Read for FailingReader {
            fn read(&mut self, _: &mut [u8]) -> io::Result<usize> {
                Err(io::ErrorKind::PermissionDenied.into())
            }
        }
        let matches = command()
            .try_get_matches_from(["lingose", "annotate"])
            .unwrap();
        let mut output = Vec::new();
        let mut input = b"hello".as_slice().chain(FailingReader);
        let error = run(&matches, &mut input, &mut output).unwrap_err();
        assert!(
            matches!(&error, CliError::Io(error) if error.kind() == io::ErrorKind::PermissionDenied)
        );
        assert_eq!(error.exit_code(), 1);
        assert!(output.is_empty());
    }

    #[test]
    fn resource_errors_are_execution_failures() {
        for error in [
            lingose::Error::Data {
                resource: "lexicon",
                message: "corrupt fixture".into(),
            },
            lingose::Error::IncompatibleDataVersion {
                resource: "lexicon",
                expected: "1".into(),
                found: "2".into(),
            },
        ] {
            assert_eq!(library_exit_code(&error), 1);
        }
    }

    #[test]
    fn output_errors_are_propagated_for_both_formats() {
        struct FailingWriter {
            on_flush: bool,
        }
        impl Write for FailingWriter {
            fn write(&mut self, bytes: &[u8]) -> io::Result<usize> {
                if self.on_flush {
                    Ok(bytes.len())
                } else {
                    Err(io::ErrorKind::BrokenPipe.into())
                }
            }

            fn flush(&mut self) -> io::Result<()> {
                Err(io::ErrorKind::BrokenPipe.into())
            }
        }
        let result = query_word("hello").unwrap();
        for json in [false, true] {
            for on_flush in [false, true] {
                let error = write_word(&mut FailingWriter { on_flush }, &result, json).unwrap_err();
                assert_eq!(error.kind(), io::ErrorKind::BrokenPipe);
                let error = write_annotation(
                    &mut FailingWriter { on_flush },
                    "hello",
                    "he\u{30a}ll\u{14d}",
                    json,
                )
                .unwrap_err();
                assert_eq!(error.kind(), io::ErrorKind::BrokenPipe);
            }
        }
    }

    #[test]
    fn multiple_pronunciations_keep_independent_array_lengths() {
        // Synthetic output fixture: the fixed lexicon currently selects at most
        // one pronunciation, but the CLI must preserve the library's list types.
        let result = json!({
            "word": "fixture",
            "ipa": ["a", "b"],
            "ips": ["ā"],
            "ism": null,
            "ipsm": ["x", "y", "z"],
            "root_lemma": null,
        });
        let mut json_output = Vec::new();
        write_word(&mut json_output, &result, true).unwrap();
        assert_eq!(
            serde_json::from_slice::<Value>(&json_output).unwrap(),
            result
        );
        let mut text_output = Vec::new();
        write_word(&mut text_output, &result, false).unwrap();
        assert_eq!(
            String::from_utf8(text_output).unwrap(),
            "word: \"fixture\"\nipa: [\"a\",\"b\"]\nips: [\"ā\"]\nism: null\nipsm: [\"x\",\"y\",\"z\"]\nroot_lemma: null\n"
        );
    }
}
