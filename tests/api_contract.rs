//! Public signatures, argument order, ownership, and remaining phase boundaries.

use lingose::{Error, Result};

type PronunciationQuery = fn(&str) -> Result<Vec<String>>;
type OptionalFieldQuery = fn(&str) -> Result<Option<String>>;

fn assert_not_implemented<T>(result: Result<T>) {
    assert!(matches!(result, Err(Error::NotImplemented { .. })));
}

#[test]
fn public_signatures_own_results_and_preserve_remaining_phase_boundaries() {
    let lists: [PronunciationQuery; 6] = [
        lingose::ipa,
        lingose::IPA,
        lingose::ips,
        lingose::IPS,
        lingose::ipsm,
        lingose::IPSM,
    ];
    let optional: [OptionalFieldQuery; 4] = [
        lingose::ism,
        lingose::ISM,
        lingose::root_lemma,
        lingose::meaning,
    ];
    let meaning: fn(&str, &str) -> Result<Option<String>> = lingose::meaning_with_lang;
    let kind: fn(&str) -> Result<bool> = lingose::kind;
    let kind_with_label: fn(&str, &str) -> Result<bool> = lingose::kind_with_label;
    let word_lists: [fn() -> Result<Vec<String>>; 2] = [lingose::kind_list, lingose::labels];
    let kind_list: fn(&str) -> Result<Vec<String>> = lingose::kind_list_with_label;
    let annotate: fn(&str) -> Result<String> = lingose::annotate_ips;
    let annotate_with_skip_top: fn(&str, i64) -> Result<String> =
        lingose::annotate_ips_with_skip_top;

    for word in ["apple", "zzzzunknownword"] {
        for query in lists {
            assert!(query(word).is_ok());
        }
        for query in optional {
            assert!(query(word).is_ok());
        }
        assert!(meaning(word, "en").is_ok());
        assert!(meaning(word, "zh").is_ok());
        assert!(kind(word).is_ok());
        assert!(kind_with_label(word, "CET4").is_ok());
    }
    for query in word_lists {
        assert!(query().is_ok());
    }
    assert!(kind_list("CET4").is_ok());
    for text in ["", "中文 123 e\u{0301}", "Abandon the book."] {
        assert!(annotate(text).is_ok());
        assert!(annotate_with_skip_top(text, 0).is_ok());
        for threshold in [1000, 5062, 5063, i64::MAX] {
            if text == "Abandon the book." {
                assert_not_implemented(annotate_with_skip_top(text, threshold));
            } else {
                assert_eq!(annotate_with_skip_top(text, threshold).unwrap(), text);
            }
        }
    }
}

fn assert_invalid_word<T>(query: impl Fn(&str) -> Result<T>) {
    for word in [
        "", "\0", "ap\0ple", " apple", "apple ", "\tapple", "apple\n",
    ] {
        assert!(matches!(
            query(word),
            Err(Error::InvalidArgument {
                parameter: "word",
                ..
            })
        ));
    }
}

#[test]
fn every_word_entry_point_rejects_invalid_content() {
    assert_invalid_word(lingose::ipa);
    assert_invalid_word(lingose::IPA);
    assert_invalid_word(lingose::ips);
    assert_invalid_word(lingose::IPS);
    assert_invalid_word(lingose::ism);
    assert_invalid_word(lingose::ISM);
    assert_invalid_word(lingose::ipsm);
    assert_invalid_word(lingose::IPSM);
    assert_invalid_word(lingose::root_lemma);
    assert_invalid_word(lingose::meaning);
    assert_invalid_word(|word| lingose::meaning_with_lang(word, "zh"));
    assert_invalid_word(lingose::kind);
    assert_invalid_word(|word| lingose::kind_with_label(word, "CET4"));
}

#[test]
fn word_boundaries_match_python_whitespace_without_normalizing_text() {
    // All 29 Python 3.12 str.isspace() code points, independent of Rust's UCD.
    let whitespace = [
        0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x85, 0xa0, 0x1680, 0x2000,
        0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008, 0x2009, 0x200a, 0x2028,
        0x2029, 0x202f, 0x205f, 0x3000,
    ];
    for codepoint in whitespace {
        let character = char::from_u32(codepoint).unwrap();
        for word in [format!("{character}apple"), format!("apple{character}")] {
            assert!(matches!(
                lingose::ipa(&word),
                Err(Error::InvalidArgument {
                    parameter: "word",
                    ..
                })
            ));
        }
    }
    for word in [
        "new york",
        "don't",
        "mother-in-law",
        "a\u{001c}b",
        "e\u{0301}",
        "\u{200b}apple",
        "apple\u{feff}",
        "\u{180e}apple",
        "\u{0008}apple",
    ] {
        assert!(lingose::ipa(word).is_ok());
    }
}

#[test]
fn word_validation_precedes_language_and_label_processing() {
    assert!(matches!(
        lingose::meaning_with_lang(" apple", "ZH"),
        Err(Error::InvalidArgument {
            parameter: "word",
            ..
        })
    ));
    for lang in ["", "EN", "ZH", " en", "zh ", "fr", "en\0"] {
        assert!(matches!(
            lingose::meaning_with_lang("zzzzunknownword", lang),
            Err(Error::InvalidArgument {
                parameter: "lang",
                ..
            })
        ));
    }
    assert!(matches!(
        lingose::kind_with_label(" apple", "not-a-label"),
        Err(Error::InvalidArgument {
            parameter: "word",
            ..
        })
    ));
    for label in [
        "",
        "not-a-label",
        "cet4",
        "CET4 ",
        " CET4",
        "CET4\0",
        "COLLINS",
        "Band",
    ] {
        for word in ["apple", "unknownwordzz"] {
            assert!(matches!(
                lingose::kind_with_label(word, label),
                Err(Error::InvalidArgument {
                    parameter: "label",
                    ..
                })
            ));
        }
        assert!(matches!(
            lingose::kind_list_with_label(label),
            Err(Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ));
    }
}

#[test]
fn annotation_checks_threshold_before_text_nul() {
    for threshold in [-1, i64::MIN] {
        for text in ["", "apple", "apple\0"] {
            assert!(matches!(
                lingose::annotate_ips_with_skip_top(text, threshold),
                Err(Error::InvalidArgument {
                    parameter: "skip_top",
                    ..
                })
            ));
        }
    }
    assert!(matches!(
        lingose::annotate_ips("apple\0"),
        Err(Error::InvalidArgument {
            parameter: "text",
            ..
        })
    ));
    assert!(matches!(
        lingose::annotate_ips_with_skip_top("apple\0", i64::MAX),
        Err(Error::InvalidArgument {
            parameter: "text",
            ..
        })
    ));
}

#[test]
fn default_functions_and_case_aliases_share_their_entry_points() {
    assert_eq!(lingose::ipa("apple"), lingose::IPA("apple"));
    assert_eq!(lingose::ips("apple"), lingose::IPS("apple"));
    assert_eq!(lingose::ism("apple"), lingose::ISM("apple"));
    assert_eq!(lingose::ipsm("apple"), lingose::IPSM("apple"));
    assert_eq!(
        lingose::meaning("apple"),
        lingose::meaning_with_lang("apple", "en")
    );
    assert_eq!(
        lingose::kind("apple"),
        lingose::kind_with_label("apple", "CET4")
    );
    assert_eq!(lingose::kind_list(), lingose::kind_list_with_label("CET4"));
    assert_eq!(
        lingose::annotate_ips("apple"),
        lingose::annotate_ips_with_skip_top("apple", 0)
    );
}

#[test]
fn errors_support_standard_thread_safe_error_handling() {
    fn require_error<T: std::error::Error + Send + Sync + 'static>() {}
    require_error::<Error>();
}

#[test]
fn simple_queries_return_empty_unknowns_and_independent_owned_values() {
    for query in [lingose::ipa, lingose::IPS, lingose::ipsm] {
        assert_eq!(query("unknownwordzz").unwrap(), Vec::<String>::new());
    }
    for query in [lingose::ism, lingose::root_lemma, lingose::meaning] {
        assert_eq!(query("unknownwordzz").unwrap(), None);
    }
    assert_eq!(
        lingose::meaning_with_lang("unknownwordzz", "zh").unwrap(),
        None
    );
    let input = String::from("apple");
    let mut result = lingose::IPA(&input).unwrap();
    let saved = result.clone();
    drop(input);
    result[0].clear();
    result.push("caller owned".into());
    assert_eq!(lingose::IPA("apple").unwrap(), saved);
    let mut meaning = lingose::meaning("apple").unwrap().unwrap();
    let saved = meaning.clone();
    meaning.clear();
    assert_eq!(lingose::meaning("apple").unwrap(), Some(saved));
}

#[test]
fn concurrent_public_queries_return_identical_results() {
    let threads: Vec<_> = (0..16)
        .map(|_| {
            std::thread::spawn(|| {
                (
                    lingose::ipa("Apple"),
                    lingose::IPS("Apple"),
                    lingose::ism("running"),
                    lingose::IPSM("running"),
                    lingose::root_lemma("running"),
                    lingose::meaning("apple"),
                    lingose::meaning_with_lang("apple", "zh"),
                )
            })
        })
        .collect();
    let results: Vec<_> = threads
        .into_iter()
        .map(|task| task.join().unwrap())
        .collect();
    assert!(results.iter().all(|result| result == &results[0]));
}

#[test]
fn category_results_are_owned_and_safe_for_concurrent_callers() {
    let label = String::from("CET4");
    let mut members = lingose::kind_list_with_label(&label).unwrap();
    let expected_members = members.clone();
    drop(label);
    members[0].clear();
    members.reverse();
    assert_eq!(lingose::kind_list().unwrap(), expected_members);
    let mut labels = lingose::labels().unwrap();
    let expected_labels = labels.clone();
    labels[0].clear();
    labels.pop();
    assert_eq!(lingose::labels().unwrap(), expected_labels);
    let threads: Vec<_> = (0..16)
        .map(|_| {
            std::thread::spawn(|| {
                (
                    lingose::kind("apple").unwrap(),
                    lingose::labels().unwrap(),
                    lingose::kind_list().unwrap(),
                )
            })
        })
        .collect();
    for task in threads {
        assert_eq!(
            task.join().unwrap(),
            (true, expected_labels.clone(), expected_members.clone())
        );
    }
}

#[test]
fn annotations_are_owned_and_concurrent_and_have_a_separate_case_policy() {
    assert!(lingose::ips("APPLE").unwrap().is_empty());
    assert_eq!(lingose::annotate_ips("APPLE").unwrap(), "APPLE");
    let input = String::from("  Abandon\tAPPLE.\r\n中文 😀 unknownwordzz");
    let mut output = lingose::annotate_ips(&input).unwrap();
    let expected = output.clone();
    drop(input);
    output.clear();
    let threads: Vec<_> = (0..16)
        .map(|_| {
            std::thread::spawn(|| {
                lingose::annotate_ips("  Abandon\tAPPLE.\r\n中文 😀 unknownwordzz").unwrap()
            })
        })
        .collect();
    for thread in threads {
        assert_eq!(thread.join().unwrap(), expected);
    }
}
