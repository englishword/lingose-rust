//! Command-line entry point for offline Lingose queries.

use std::fmt::Display;
use std::io::{self, Write};
use std::process::ExitCode;

use clap::{Arg, ArgAction, Command};
use serde_json::{Value, json};

const WORD_FIELDS: [&str; 6] = ["word", "ipa", "ips", "ism", "ipsm", "root_lemma"];

fn command() -> Command {
    Command::new("lingose")
        .version(env!("CARGO_PKG_VERSION"))
        .about("Offline Lingose word queries")
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
    let (_, args) = matches.subcommand().expect("clap requires a subcommand");
    let word = args.get_one::<String>("word").expect("clap requires WORD");
    let result = match query_word(word) {
        Ok(result) => result,
        Err(error) => return report_error(&error, library_exit_code(&error)),
    };
    match write_word(&mut io::stdout().lock(), &result, args.get_flag("json")) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => report_error(&error, 1),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

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
        struct FailingWriter;
        impl Write for FailingWriter {
            fn write(&mut self, _: &[u8]) -> io::Result<usize> {
                Err(io::ErrorKind::BrokenPipe.into())
            }

            fn flush(&mut self) -> io::Result<()> {
                Ok(())
            }
        }
        let result = query_word("hello").unwrap();
        for json in [false, true] {
            let error = write_word(&mut FailingWriter, &result, json).unwrap_err();
            assert_eq!(error.kind(), io::ErrorKind::BrokenPipe);
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
