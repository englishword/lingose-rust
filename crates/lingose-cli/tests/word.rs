//! Process-level checks for the public word command and shell contract.

use std::process::{Command, Output, Stdio};

use serde_json::{Value, json};

const FIELDS: [&str; 6] = ["word", "ipa", "ips", "ism", "ipsm", "root_lemma"];

fn run(args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_lingose"))
        .args(args)
        .stdin(Stdio::null())
        .output()
        .expect("run lingose")
}

fn success(args: &[&str]) -> Vec<u8> {
    let output = run(args);
    assert_eq!(output.status.code(), Some(0), "{args:?}: {output:?}");
    assert!(output.stderr.is_empty(), "{args:?}: {output:?}");
    output.stdout
}

fn library_word(word: &str) -> Value {
    json!({
        "word": word,
        "ipa": lingose::ipa(word).unwrap(),
        "ips": lingose::ips(word).unwrap(),
        "ism": lingose::ism(word).unwrap(),
        "ipsm": lingose::ipsm(word).unwrap(),
        "root_lemma": lingose::root_lemma(word).unwrap(),
    })
}

#[test]
fn json_preserves_library_values_types_and_exact_input_spelling() {
    for word in [
        "hello",
        "apple",
        "Apple",
        "APPLE",
        "May",
        "may",
        "US",
        "us",
        "present",
        "running",
        "Marxism",
        "don't",
        "ma’am",
        "中文",
        "e\u{0301}",
        "🦀",
        "zzzzunknownword",
        "a\"b\\c",
        "a\nb",
    ] {
        let output = success(&["word", word, "--json"]);
        let result: Value = serde_json::from_slice(&output).unwrap();
        assert_eq!(result, library_word(word), "{word:?}");
        assert_eq!(result.as_object().unwrap().len(), FIELDS.len());
        for field in ["ipa", "ips", "ipsm"] {
            assert!(
                result[field]
                    .as_array()
                    .unwrap()
                    .iter()
                    .all(Value::is_string)
            );
        }
        for field in ["ism", "root_lemma"] {
            assert!(result[field].is_null() || result[field].is_string());
        }
    }
    assert_eq!(
        success(&["word", "apple", "--json"]),
        success(&["word", "--json", "apple"])
    );
}

#[test]
fn text_has_exactly_six_fields_and_preserves_values() {
    for word in [
        "apple",
        "Marxism",
        "中文",
        "zzzzunknownword",
        "a\"b\\c",
        "a\nb",
    ] {
        let output = String::from_utf8(success(&["word", word])).unwrap();
        let lines: Vec<_> = output.lines().collect();
        assert_eq!(lines.len(), FIELDS.len(), "{word:?}: {output}");
        let expected = library_word(word);
        for (line, field) in lines.iter().zip(FIELDS) {
            let (label, value) = line.split_once(": ").unwrap();
            assert_eq!(label, field);
            assert_eq!(
                serde_json::from_str::<Value>(value).unwrap(),
                expected[field]
            );
        }
    }
}

#[test]
fn unavailable_fields_do_not_truncate_other_pronunciations() {
    let result: Value = serde_json::from_slice(&success(&["word", "Marxism", "--json"])).unwrap();
    assert_eq!(result["ipa"], json!(["mɑːksɪsɪm"]));
    assert_eq!(result["ips"], json!(["Màrxiṡm"]));
    assert_eq!(result["ipsm"], json!([]));
}

#[test]
fn unknown_words_succeed_with_empty_arrays_and_nulls() {
    let result: Value =
        serde_json::from_slice(&success(&["word", "zzzzunknownword", "--json"])).unwrap();
    assert_eq!(
        result,
        json!({
            "word": "zzzzunknownword",
            "ipa": [], "ips": [], "ism": null, "ipsm": [], "root_lemma": null,
        })
    );
}

#[test]
fn help_and_version_succeed_without_word_arguments() {
    for args in [
        vec!["--help"],
        vec!["-h"],
        vec!["help"],
        vec!["word", "--help"],
        vec!["word", "-h"],
        vec!["help", "word"],
    ] {
        let output = String::from_utf8(success(&args)).unwrap();
        assert!(output.contains("Usage:"), "{args:?}: {output}");
        assert!(output.contains("word"), "{args:?}: {output}");
    }
    for args in [vec!["--version"], vec!["-V"], vec!["word", "--version"]] {
        let output = String::from_utf8(success(&args)).unwrap();
        assert!(output.contains(env!("CARGO_PKG_VERSION")));
        assert!(output.contains("lingose"));
    }
}

#[test]
fn invalid_arguments_exit_two_with_only_stderr() {
    for args in [
        vec![],
        vec!["word"],
        vec!["unknown-command"],
        vec!["--json"],
        vec!["word", "apple", "extra"],
        vec!["word", "apple", "--unknown"],
        vec!["word", "apple", "--json=true"],
        vec!["word", "apple", "--json", "--json"],
        vec!["word", ""],
        vec!["word", " apple"],
        vec!["word", "apple\n", "--json"],
        vec!["word", "\u{001c}apple"],
    ] {
        let output = run(&args);
        assert_eq!(output.status.code(), Some(2), "{args:?}: {output:?}");
        assert!(output.stdout.is_empty(), "{args:?}: {output:?}");
        assert!(!output.stderr.is_empty(), "{args:?}");
    }
}

#[test]
fn end_of_options_allows_a_word_starting_with_a_hyphen() {
    let result: Value =
        serde_json::from_slice(&success(&["word", "--json", "--", "--help"])).unwrap();
    assert_eq!(result, library_word("--help"));
}

#[test]
fn closed_stdout_is_an_execution_error_without_a_panic() {
    let mut child = Command::new(env!("CARGO_BIN_EXE_lingose"))
        .args(["word", &"x".repeat(8192), "--json"])
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    drop(child.stdout.take());
    let output = child.wait_with_output().unwrap();
    assert_eq!(output.status.code(), Some(1), "{output:?}");
    assert!(output.stdout.is_empty());
    let error = String::from_utf8(output.stderr).unwrap();
    assert!(error.starts_with("error:"), "{error}");
    assert!(!error.contains("panicked"), "{error}");
}
