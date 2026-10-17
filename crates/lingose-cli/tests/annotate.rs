//! Process-level input and whole-text annotation checks.

use std::ffi::OsStr;
use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::{Value, json};

struct TestDirectory(PathBuf);

impl TestDirectory {
    fn new() -> Self {
        static NEXT: AtomicU64 = AtomicU64::new(0);
        let parent = std::env::temp_dir().canonicalize().unwrap();
        let path = parent.join(format!(
            "lingose-cli-annotate-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        assert!(path.is_absolute() && path.parent() == Some(parent.as_path()));
        fs::create_dir(&path).unwrap();
        Self(path)
    }
}

impl Drop for TestDirectory {
    fn drop(&mut self) {
        // Only remove the unique directory successfully created by this test.
        let parent = std::env::temp_dir().canonicalize().unwrap();
        assert_eq!(
            self.0.canonicalize().unwrap().parent(),
            Some(parent.as_path())
        );
        fs::remove_dir_all(&self.0).unwrap();
    }
}

fn run(args: &[&OsStr], input: &[u8], directory: &TestDirectory) -> Output {
    let mut child = Command::new(env!("CARGO_BIN_EXE_lingose"))
        .args(args)
        .current_dir(&directory.0)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    // Inputs here are small enough to fit in the pipe. A command with explicit
    // input may exit without reading stdin, so a closed input pipe is harmless.
    if let Err(error) = child.stdin.take().unwrap().write_all(input) {
        assert_eq!(error.kind(), std::io::ErrorKind::BrokenPipe);
    }
    child.wait_with_output().unwrap()
}

fn success(args: &[&OsStr], input: &[u8], directory: &TestDirectory, expected: &str) {
    let output = run(args, input, directory);
    assert_eq!(output.status.code(), Some(0), "{args:?}: {output:?}");
    assert!(output.stderr.is_empty(), "{args:?}: {output:?}");
    assert_eq!(output.stdout, expected.as_bytes(), "{args:?}");
}

fn failure(args: &[&OsStr], input: &[u8], directory: &TestDirectory, code: i32) {
    let output = run(args, input, directory);
    assert_eq!(output.status.code(), Some(code), "{args:?}: {output:?}");
    assert!(output.stdout.is_empty(), "{args:?}: {output:?}");
    assert!(!output.stderr.is_empty(), "{args:?}");
}

#[test]
fn text_file_and_stdin_outputs_match_one_complete_library_call() {
    let directory = TestDirectory::new();
    let file = OsStr::new("文章 with spaces.txt");
    for text in [
        "",
        "This is an English word.",
        "the\napple.\r\nTHE HOUR!\r\n\r\nThe book.\n",
        "the\r\napple",
        "  Abandon\tma’am o’clock don't mother-in-law unknownwordzz.  ",
        "中文 🦀 e\u{0301} café 123\r\n",
        "\u{feff}hello\r\nworld\n",
        "hello\rworld",
    ] {
        let expected = lingose::annotate_ips_skip(text, 0).unwrap();
        fs::write(directory.0.join(file), text.as_bytes()).unwrap();
        success(
            &["annotate".as_ref(), text.as_ref()],
            b"",
            &directory,
            &expected,
        );
        success(
            &["annotate".as_ref(), "--text".as_ref(), text.as_ref()],
            &[0xff],
            &directory,
            &expected,
        );
        success(&["annotate".as_ref(), file], b"", &directory, &expected);
        success(
            &["annotate".as_ref(), "--input".as_ref(), file],
            &[0xff],
            &directory,
            &expected,
        );
        success(
            &["annotate".as_ref()],
            text.as_bytes(),
            &directory,
            &expected,
        );
    }
    let text = "the\napple";
    assert_ne!(
        lingose::annotate_ips(text).unwrap(),
        text.lines()
            .map(|line| lingose::annotate_ips(line).unwrap())
            .collect::<Vec<_>>()
            .join("\n"),
        "the fixture must detect accidental line-by-line annotation"
    );
}

#[test]
fn automatic_paths_and_explicit_text_are_unambiguous() {
    let directory = TestDirectory::new();
    fs::write(directory.0.join("hello"), "the apple").unwrap();
    success(
        &["annotate".as_ref(), "hello".as_ref()],
        b"ignored",
        &directory,
        &lingose::annotate_ips("the apple").unwrap(),
    );
    success(
        &["annotate".as_ref(), "--text".as_ref(), "hello".as_ref()],
        b"ignored",
        &directory,
        &lingose::annotate_ips("hello").unwrap(),
    );
    for text in ["missing.txt", "hello/child", "hello? <world> | \"yes\""] {
        success(
            &["annotate".as_ref(), text.as_ref()],
            b"",
            &directory,
            &lingose::annotate_ips(text).unwrap(),
        );
    }
    let text = "x".repeat(4096);
    success(
        &["annotate".as_ref(), text.as_ref()],
        b"",
        &directory,
        &lingose::annotate_ips(&text).unwrap(),
    );
    success(
        &["annotate".as_ref(), "--".as_ref(), "--hello".as_ref()],
        b"",
        &directory,
        &lingose::annotate_ips("--hello").unwrap(),
    );
}

#[test]
fn frequency_thresholds_are_delegated_to_the_library() {
    let directory = TestDirectory::new();
    let text = "the Abandon abandoned ma’am o’clock Messrs. one hundred unknownwordzz\r\n";
    for threshold in [0, 1000, 5062, 5063, i64::MAX] {
        let number = threshold.to_string();
        success(
            &[
                "annotate".as_ref(),
                "--skip-top".as_ref(),
                number.as_ref(),
                "--text".as_ref(),
                text.as_ref(),
            ],
            b"",
            &directory,
            &lingose::annotate_ips_skip(text, threshold).unwrap(),
        );
        success(
            &["annotate".as_ref(), "--skip-top".as_ref(), number.as_ref()],
            text.as_bytes(),
            &directory,
            &lingose::annotate_ips_skip(text, threshold).unwrap(),
        );
    }
}

#[test]
fn missing_files_directories_and_invalid_utf8_fail_without_output() {
    let directory = TestDirectory::new();
    fs::create_dir(directory.0.join("folder")).unwrap();
    fs::write(directory.0.join("invalid.txt"), [0xff, 0xfe]).unwrap();
    for args in [
        vec!["annotate", "--input", "missing.txt"],
        vec!["annotate", "--input", "folder"],
        vec!["annotate", "folder"],
        vec!["annotate", "--input", "invalid.txt"],
        vec!["annotate", "invalid.txt"],
    ] {
        let args: Vec<_> = args.iter().map(OsStr::new).collect();
        failure(&args, b"", &directory, 1);
    }
    failure(&["annotate".as_ref()], &[0xff, 0xfe], &directory, 1);
}

#[test]
fn conflicting_inputs_bad_thresholds_and_library_invalid_text_exit_two() {
    let directory = TestDirectory::new();
    for args in [
        vec!["annotate", "hello", "--text", "world"],
        vec!["annotate", "hello", "--input", "missing.txt"],
        vec!["annotate", "--input", "missing.txt", "--text", "world"],
        vec!["annotate", "hello", "extra"],
        vec!["annotate", "--input"],
        vec!["annotate", "--text"],
        vec!["annotate", "--skip-top"],
        vec!["annotate", "--skip-top", "abc"],
        vec!["annotate", "--skip-top", "9223372036854775808"],
        vec!["annotate", "--skip-top", "-1", "--text", "hello"],
        vec!["annotate", "--skip-top=-9223372036854775808"],
    ] {
        let args: Vec<_> = args.iter().map(OsStr::new).collect();
        failure(&args, b"", &directory, 2);
    }
    fs::write(directory.0.join("nul.txt"), b"hello\0world").unwrap();
    failure(&["annotate".as_ref()], b"hello\0world", &directory, 2);
    failure(
        &["annotate".as_ref(), "nul.txt".as_ref()],
        b"",
        &directory,
        2,
    );
}

#[test]
fn annotation_help_and_version_do_not_read_stdin() {
    let directory = TestDirectory::new();
    for args in [
        vec!["annotate", "--help"],
        vec!["annotate", "-h"],
        vec!["help", "annotate"],
        vec!["annotate", "--version"],
    ] {
        let args: Vec<_> = args.iter().map(OsStr::new).collect();
        let output = run(&args, &[0xff], &directory);
        assert_eq!(output.status.code(), Some(0), "{output:?}");
        assert!(output.stderr.is_empty());
        assert!(!output.stdout.is_empty());
    }
}

#[test]
fn closed_annotation_stdout_exits_one_without_a_panic() {
    for json in [false, true] {
        let mut command = Command::new(env!("CARGO_BIN_EXE_lingose"));
        command.arg("annotate");
        if json {
            command.arg("--json");
        }
        let mut child = command
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        // The child waits for stdin EOF, so close its output pipe first.
        drop(child.stdout.take());
        let mut stdin = child.stdin.take().unwrap();
        stdin.write_all(&vec![b'x'; 8192]).unwrap();
        drop(stdin);
        let output = child.wait_with_output().unwrap();
        assert_eq!(output.status.code(), Some(1), "{output:?}");
        assert!(output.stdout.is_empty());
        let error = String::from_utf8(output.stderr).unwrap();
        assert!(error.starts_with("error:"), "{error}");
        assert!(!error.contains("panicked"), "{error}");
    }
}

#[test]
fn annotation_json_has_only_original_text_and_complete_annotation_strings() {
    let directory = TestDirectory::new();
    let path = OsStr::new("原文.txt");
    for text in [
        "",
        "中文 🦀 e\u{301} unknownwordzz\r\nthe\napple\r",
        "\u{feff}the\r\napple\n",
        "\"hello\" \\ world\t\u{1}",
    ] {
        fs::write(directory.0.join(path), text.as_bytes()).unwrap();
        for args in [
            vec!["annotate".as_ref(), text.as_ref()],
            vec!["annotate".as_ref(), "--text".as_ref(), text.as_ref()],
            vec!["annotate".as_ref(), path],
            vec!["annotate".as_ref(), "--input".as_ref(), path],
            vec!["annotate".as_ref()],
        ] {
            let mut args = args;
            args.push("--json".as_ref());
            let output = run(&args, text.as_bytes(), &directory);
            assert_eq!(output.status.code(), Some(0), "{args:?}: {output:?}");
            assert!(output.stderr.is_empty());
            let result: Value = serde_json::from_slice(&output.stdout).unwrap();
            assert_eq!(result.as_object().unwrap().len(), 2);
            assert!(result["text"].is_string() && result["annotate"].is_string());
            assert_eq!(
                result,
                json!({"text": text, "annotate": lingose::annotate_ips(text).unwrap()})
            );
        }
    }
}

#[test]
fn new_and_existing_output_files_match_stdout_in_both_formats() {
    let directory = TestDirectory::new();
    let text = "\u{feff}中文 \"the\"\r\napple\\world\n";
    for json in [false, true] {
        let mut args = vec![
            "annotate".as_ref(),
            "--text".as_ref(),
            text.as_ref(),
            "--skip-top".as_ref(),
            "1000".as_ref(),
        ];
        if json {
            args.push("--json".as_ref());
        }
        let reference = run(&args, b"", &directory);
        assert_eq!(reference.status.code(), Some(0));
        assert!(reference.stderr.is_empty());
        if json {
            let result: Value = serde_json::from_slice(&reference.stdout).unwrap();
            assert_eq!(
                result,
                json!({"text": text, "annotate": lingose::annotate_ips_skip(text, 1000).unwrap()})
            );
        } else {
            assert_eq!(
                reference.stdout,
                lingose::annotate_ips_skip(text, 1000).unwrap().as_bytes()
            );
        }
        for existing in [false, true] {
            let path = directory.0.join(format!("输出 {json}-{existing}.txt"));
            if existing {
                fs::write(&path, vec![b'x'; 8192]).unwrap();
            }
            let mut file_args = args.clone();
            file_args.extend(["-o".as_ref(), path.as_os_str()]);
            success(&file_args, b"", &directory, "");
            assert_eq!(fs::read(&path).unwrap(), reference.stdout);
        }
        let path = directory.0.join(format!("empty-{json}.txt"));
        let mut args = vec![
            "annotate".as_ref(),
            "--text".as_ref(),
            "".as_ref(),
            "-o".as_ref(),
            path.as_os_str(),
        ];
        if json {
            args.push("--json".as_ref());
        }
        success(&args, b"", &directory, "");
        let bytes = fs::read(&path).unwrap();
        if json {
            assert_eq!(
                serde_json::from_slice::<Value>(&bytes).unwrap(),
                json!({"text":"", "annotate":""})
            );
        } else {
            assert!(bytes.is_empty());
        }
    }
}

#[test]
fn in_place_output_reads_the_original_file_before_overwriting() {
    let directory = TestDirectory::new();
    let text = "the\r\napple\n中文 \"world\"\n";
    for explicit in [false, true] {
        for json in [false, true] {
            let path = directory.0.join("in-place.txt");
            fs::write(&path, text).unwrap();
            let mut args = vec!["annotate".as_ref()];
            if explicit {
                args.push("--input".as_ref());
            }
            args.extend([
                OsStr::new("in-place.txt"),
                OsStr::new("-o"),
                OsStr::new("./in-place.txt"),
            ]);
            if json {
                args.push("--json".as_ref());
            }
            success(&args, b"", &directory, "");
            let bytes = fs::read(&path).unwrap();
            if json {
                assert_eq!(
                    serde_json::from_slice::<Value>(&bytes).unwrap(),
                    json!({"text":text,"annotate":lingose::annotate_ips(text).unwrap()})
                );
            } else {
                assert_eq!(bytes, lingose::annotate_ips(text).unwrap().as_bytes());
            }
        }
    }
}

#[test]
fn precondition_failures_preserve_existing_output_and_do_not_create_new_output() {
    let directory = TestDirectory::new();
    fs::create_dir(directory.0.join("folder")).unwrap();
    fs::write(directory.0.join("invalid.txt"), [0xff, 0xfe]).unwrap();
    fs::write(directory.0.join("nul.txt"), b"hello\0world").unwrap();
    let sentinel = b"\x00\xfforiginal output\r\n";
    let cases: &[(&[&str], &[u8], i32)] = &[
        (&["annotate", "--input", "missing.txt"], b"", 1),
        (&["annotate", "folder"], b"", 1),
        (&["annotate", "--input", "invalid.txt"], b"", 1),
        (&["annotate"], &[0xff, 0xfe], 1),
        (&["annotate", "nul.txt"], b"", 2),
        (&["annotate"], b"hello\0world", 2),
        (&["annotate", "--text", "hello", "--skip-top", "-1"], b"", 2),
        (&["annotate", "--text", "hello", "world"], b"", 2),
        (&["annotate", "--skip-top", "abc"], b"", 2),
        (&["annotate", "--skip-top", "9223372036854775808"], b"", 2),
    ];
    for (index, (args, input, code)) in cases.iter().enumerate() {
        for json in [false, true] {
            for existing in [false, true] {
                let path = directory.0.join(format!("out-{index}-{json}-{existing}"));
                if existing {
                    fs::write(&path, sentinel).unwrap();
                }
                let mut args: Vec<_> = args.iter().map(OsStr::new).collect();
                args.extend(["-o".as_ref(), path.as_os_str()]);
                if json {
                    args.push("--json".as_ref());
                }
                failure(&args, input, &directory, *code);
                if existing {
                    assert_eq!(fs::read(&path).unwrap(), sentinel);
                } else {
                    assert!(!path.exists());
                }
            }
        }
    }
}

#[test]
fn invalid_in_place_input_is_never_truncated() {
    let directory = TestDirectory::new();
    for (input, code) in [(&[0xff, 0xfe][..], 1), (&b"hello\0world"[..], 2)] {
        for explicit in [false, true] {
            for json in [false, true] {
                let path = directory.0.join("in-place.txt");
                fs::write(&path, input).unwrap();
                let mut args = vec!["annotate".as_ref()];
                if explicit {
                    args.push("--input".as_ref());
                }
                args.extend([
                    OsStr::new("in-place.txt"),
                    OsStr::new("-o"),
                    OsStr::new("in-place.txt"),
                ]);
                if json {
                    args.push("--json".as_ref());
                }
                failure(&args, b"", &directory, code);
                assert_eq!(fs::read(&path).unwrap(), input);
            }
        }
    }
}

#[test]
fn output_path_errors_exit_one_without_stdout() {
    let directory = TestDirectory::new();
    fs::create_dir(directory.0.join("folder")).unwrap();
    fs::write(directory.0.join("parent-file"), "keep").unwrap();
    for path in ["folder", "missing/out.txt", "parent-file/out.txt"] {
        for json in [false, true] {
            let mut args = vec![
                "annotate".as_ref(),
                "--text".as_ref(),
                "hello".as_ref(),
                "-o".as_ref(),
                path.as_ref(),
            ];
            if json {
                args.push("--json".as_ref());
            }
            failure(&args, b"", &directory, 1);
        }
    }
    assert!(!directory.0.join("missing").exists());
    assert_eq!(fs::read(directory.0.join("parent-file")).unwrap(), b"keep");
}

#[test]
fn file_output_succeeds_even_when_stdout_is_closed() {
    let directory = TestDirectory::new();
    let text = "the\napple";
    for json in [false, true] {
        let path = directory.0.join(format!("closed-stdout-{json}.txt"));
        let mut command = Command::new(env!("CARGO_BIN_EXE_lingose"));
        command.args(["annotate", "-o"]).arg(&path);
        if json {
            command.arg("--json");
        }
        let mut child = command
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        drop(child.stdout.take());
        let mut stdin = child.stdin.take().unwrap();
        stdin.write_all(text.as_bytes()).unwrap();
        drop(stdin);
        let output = child.wait_with_output().unwrap();
        assert_eq!(output.status.code(), Some(0), "{output:?}");
        assert!(output.stdout.is_empty() && output.stderr.is_empty());
        let bytes = fs::read(&path).unwrap();
        if json {
            assert_eq!(
                serde_json::from_slice::<Value>(&bytes).unwrap(),
                json!({"text":text,"annotate":lingose::annotate_ips(text).unwrap()})
            );
        } else {
            assert_eq!(bytes, lingose::annotate_ips(text).unwrap().as_bytes());
        }
    }
}

#[test]
fn help_version_and_usage_errors_leave_output_untouched() {
    let directory = TestDirectory::new();
    let path = directory.0.join("out.txt");
    fs::write(&path, "keep").unwrap();
    for flag in ["--help", "--version"] {
        let output = run(
            &[
                "annotate".as_ref(),
                "-o".as_ref(),
                path.as_os_str(),
                "--json".as_ref(),
                flag.as_ref(),
            ],
            &[0xff],
            &directory,
        );
        assert_eq!(output.status.code(), Some(0), "{output:?}");
        assert!(output.stderr.is_empty() && !output.stdout.is_empty());
        assert_eq!(fs::read(&path).unwrap(), b"keep");
    }
    for extra in ["-o", "--json", "--unknown"] {
        let mut args = vec![
            "annotate".as_ref(),
            "--text".as_ref(),
            "hello".as_ref(),
            "-o".as_ref(),
            path.as_os_str(),
            "--json".as_ref(),
        ];
        args.push(extra.as_ref());
        failure(&args, b"", &directory, 2);
        assert_eq!(fs::read(&path).unwrap(), b"keep");
    }
}

#[cfg(windows)]
#[test]
fn locked_output_files_fail_without_stdout_or_truncation() {
    use std::os::windows::fs::OpenOptionsExt;
    let directory = TestDirectory::new();
    let path = directory.0.join("locked-output.txt");
    fs::write(&path, "keep").unwrap();
    for json in [false, true] {
        let locked = fs::OpenOptions::new()
            .read(true)
            .share_mode(0)
            .open(&path)
            .unwrap();
        let mut args = vec![
            "annotate".as_ref(),
            "--text".as_ref(),
            "hello".as_ref(),
            "-o".as_ref(),
            path.as_os_str(),
        ];
        if json {
            args.push("--json".as_ref());
        }
        failure(&args, b"", &directory, 1);
        drop(locked);
        assert_eq!(fs::read(&path).unwrap(), b"keep");
    }
}

#[cfg(windows)]
#[test]
fn locked_files_are_execution_errors_in_both_file_modes() {
    use std::os::windows::fs::OpenOptionsExt;
    let directory = TestDirectory::new();
    let path = directory.0.join("locked.txt");
    fs::write(&path, "hello").unwrap();
    let _locked = fs::OpenOptions::new()
        .read(true)
        .share_mode(0)
        .open(&path)
        .unwrap();
    failure(
        &["annotate".as_ref(), "locked.txt".as_ref()],
        b"",
        &directory,
        1,
    );
    failure(
        &[
            "annotate".as_ref(),
            "--input".as_ref(),
            "locked.txt".as_ref(),
        ],
        b"",
        &directory,
        1,
    );
}

#[cfg(unix)]
#[test]
fn native_paths_and_symlink_errors_keep_their_identity() {
    use std::ffi::OsString;
    use std::os::unix::ffi::OsStringExt;
    use std::os::unix::fs::symlink;
    let directory = TestDirectory::new();
    let name = OsString::from_vec(b"native-\xff.txt".to_vec());
    fs::write(directory.0.join(&name), "hello").unwrap();
    let expected = lingose::annotate_ips("hello").unwrap();
    success(&["annotate".as_ref(), &name], b"", &directory, &expected);
    success(
        &["annotate".as_ref(), "--input".as_ref(), &name],
        b"",
        &directory,
        &expected,
    );
    let invalid_text = OsString::from_vec(b"missing-\xff".to_vec());
    failure(&["annotate".as_ref(), &invalid_text], b"", &directory, 2);
    symlink(&name, directory.0.join("link.txt")).unwrap();
    success(
        &["annotate".as_ref(), "link.txt".as_ref()],
        b"",
        &directory,
        &expected,
    );
    symlink("missing.txt", directory.0.join("dangling.txt")).unwrap();
    failure(
        &["annotate".as_ref(), "dangling.txt".as_ref()],
        b"",
        &directory,
        1,
    );
    symlink("loop.txt", directory.0.join("loop.txt")).unwrap();
    failure(
        &["annotate".as_ref(), "loop.txt".as_ref()],
        b"",
        &directory,
        1,
    );
}
