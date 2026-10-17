//! Independent packaged-crate consumer: only lingose public APIs and std.
//!
//! Expected literals were sampled from tests/query_vectors.rs,
//! tests/category_vectors.rs, tests/annotation_context_vectors.rs and
//! tests/annotation_frequency_vectors.rs. Their pinned P0 source is
//! tests/fixtures/python-api-v1.json, SHA-256:
//! 6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1.
//! Annotation samples below retain their pinned Python snapshot case IDs.
//! No fixture, checkout, Python installation, or external data is read at runtime.

use lingose::{Error, Result};

fn error_class(error: &Error) -> &'static str {
    match error {
        Error::InvalidArgument { .. } => "invalid-argument",
        Error::Data { .. } => "data",
        Error::IncompatibleDataVersion { .. } => "incompatible-data-version",
        _ => "future-error",
    }
}

fn require_public_error<T: std::error::Error + Send + Sync + 'static>() {}

fn assert_invalid<T>(actual: Result<T>, expected_parameter: &str) {
    match actual {
        Err(Error::InvalidArgument { parameter, .. }) => {
            assert_eq!(parameter, expected_parameter);
        }
        _ => panic!("expected invalid {expected_parameter}"),
    }
}

fn main() -> Result<()> {
    // All four lowercase functions and all four uppercase aliases have
    // independent content expectations, rather than only alias equality.
    for query in [lingose::ipa, lingose::IPA] {
        assert_eq!(query("apple")?, ["\u{e6}p\u{259}l"]);
        assert_eq!(query("Apple")?, ["\u{e6}p\u{259}l"]);
        assert_eq!(query("APPLE")?, Vec::<String>::new());
        assert_eq!(query("unknownwordzz")?, Vec::<String>::new());
    }
    for query in [lingose::ips, lingose::IPS] {
        assert_eq!(query("apple")?, ["apple"]);
        assert_eq!(query("May")?, ["M\u{101}y"]);
        assert_eq!(query("may")?, ["m\u{101}y"]);
        assert_eq!(query("APPLE")?, Vec::<String>::new());
        assert_eq!(query("unknownwordzz")?, Vec::<String>::new());
    }
    for query in [lingose::ism, lingose::ISM] {
        assert_eq!(query("apple")?.as_deref(), Some("app-le"));
        assert_eq!(query("unknownwordzz")?, None);
    }
    for query in [lingose::ipsm, lingose::IPSM] {
        assert_eq!(query("apple")?, ["app-le"]);
        assert_eq!(query("unknownwordzz")?, Vec::<String>::new());
        // A known word can legitimately lack valid IPSM despite having IPA.
        assert_eq!(query("Marxism")?, Vec::<String>::new());
    }
    assert_eq!(lingose::ipa("Marxism")?, ["m\u{251}\u{2d0}ks\u{26a}s\u{26a}m"]);
    assert_eq!(lingose::root_lemma("running")?.as_deref(), Some("run"));
    assert_eq!(lingose::root_lemma("has")?, None);
    assert_eq!(lingose::root_lemma("unknownwordzz")?, None);

    const APPLE_EN: &str =
        "n. fruit with red or yellow or green skin and sweet to tart crisp whitish flesh";
    assert_eq!(lingose::meaning("apple")?.as_deref(), Some(APPLE_EN));
    assert_eq!(
        lingose::meaning_with_lang("apple", "en")?.as_deref(),
        Some(APPLE_EN)
    );
    assert_eq!(
        lingose::meaning_with_lang("apple", "zh")?.as_deref(),
        Some("n. \u{82f9}\u{679c}, \u{5bb6}\u{4f19}")
    );
    assert_eq!(
        lingose::meaning("running")?.as_deref(),
        Some("n. the act or state of moving fast on foot\na. happening continuously; in operation")
    );
    assert_eq!(lingose::meaning("unknownwordzz")?, None);
    assert_eq!(lingose::meaning_with_lang("unknownwordzz", "zh")?, None);

    assert!(lingose::kind("apple")?);
    assert!(!lingose::kind("running")?);
    assert!(!lingose::kind("unknownwordzz")?);
    assert!(lingose::kind_with_label("Apple", "CET4")?);
    assert!(!lingose::kind_with_label("APPLE", "CET4")?);
    assert_eq!(
        lingose::labels()?,
        [
            "OXFORD_3000", "OXFORD_5000", "CET4", "CET6", "CET4_CET6", "IELTS",
            "TEM-4", "TEM-8", "TOEFL", "SAT", "GMAT", "GRE", "BEC", "Primary",
            "Junior", "Senior", "College", "COCA_20000", "White", "Yellow", "Green",
            "Blue", "Red", "Black",
        ]
    );
    // Frozen P0 complete-list count and ordered boundary samples. This is a
    // packaged-consumer smoke check; full canonical SHA-256 comparison remains
    // in the repository's category vectors, not a new dependency here.
    let cet4 = lingose::kind_list()?;
    assert_eq!(cet4.len(), 5225);
    assert_eq!(cet4, lingose::kind_list_with_label("CET4")?);
    assert_eq!(
        &cet4[..10],
        ["a", "able", "ability", "disable", "enable", "unable", "ache", "acid", "acre", "act"]
    );
    assert_eq!(
        &cet4[cet4.len() - 10..],
        ["roman", "saturday", "september", "soviet", "sunday", "thursday", "true", "tuesday", "wednesday", "x-ray"]
    );
    for member in &cet4 {
        assert!(lingose::kind_with_label(member, "CET4")?);
    }

    // snapshot-0208, 0209, 0210: default, zero, 1000, 5062 and capped threshold.
    assert_eq!(
        lingose::annotate_ips("Abandon the book.")?,
        "\u{c5}bando\u{30a}n \u{1e6b}he\u{30a} book."
    );
    for (threshold, expected) in [
        (0, "\u{c5}bando\u{30a}n \u{1e6b}he\u{30a} book."),
        (1000, "\u{c5}bando\u{30a}n the book."),
        (5062, "Abandon the book."),
        (5063, "Abandon the book."),
        (i64::MAX, "Abandon the book."),
    ] {
        assert_eq!(lingose::annotate_ips_with_skip_top("Abandon the book.", threshold)?, expected);
    }
    // snapshot-0217: annotation casing fallback differs from simple queries.
    assert_eq!(
        lingose::annotate_ips("Apple APPLE aPpLe May may US us iPhone McDonald")?,
        "Apple APPLE aPpLe M\u{101}y m\u{101}y \u{db}S \u{fb}s \u{12b}Ph\u{14d}ne [McDonald]"
    );
    // snapshot-0238, 0241, 0247: unknown brackets, Unicode and exact whitespace.
    assert_eq!(
        lingose::annotate_ips("unknownwordzz unknown-wordzz who'unknown")?,
        "[unknownwordzz] \u{fb}n\u{1d55c}n\u{14d}wn-[wordzz] \u{1d568}h\u{f5}'unknown"
    );
    let unicode = "caf\u{e9} apple123 \u{4e2d}\u{6587}apple \u{4e2d}\u{6587}\t123 \u{e9} e\u{301}\n\u{1f600}";
    assert_eq!(lingose::annotate_ips(unicode)?, unicode);
    assert_eq!(
        lingose::annotate_ips("  Abandon\t  the (apple).\n\nThe book.  ")?,
        "  \u{c5}bando\u{30a}n\t  \u{1e6b}h\u{113} (apple).\n\n\u{1e6a}he\u{30a} book.  "
    );
    assert_eq!(lingose::annotate_ips("")?, "");

    assert_invalid(lingose::ipa(" apple"), "word");
    assert_invalid(lingose::meaning_with_lang("apple", "EN"), "lang");
    assert_invalid(lingose::kind_with_label("apple", "cet4"), "label");
    assert_invalid(lingose::kind_list_with_label("COLLINS"), "label");
    assert_invalid(lingose::annotate_ips("apple\0"), "text");
    assert_invalid(lingose::annotate_ips_with_skip_top("apple\0", -1), "skip_top");

    // Compile and exercise public handling for both resource error variants.
    // These synthetic errors demonstrate the consumer's match compatibility;
    // they do not claim to inject corruption into bundled crate resources.
    require_public_error::<Error>();
    let data_error = Error::Data {
        resource: "consumer-example",
        message: String::from("synthetic resource failure"),
    };
    let version_error = Error::IncompatibleDataVersion {
        resource: "consumer-example",
        expected: String::from("1"),
        found: String::from("2"),
    };
    assert_eq!(error_class(&data_error), "data");
    assert_eq!(error_class(&version_error), "incompatible-data-version");
    assert!(!data_error.to_string().is_empty());
    assert!(!version_error.to_string().is_empty());

    println!("P5.3 packaged consumer passed: 18 public functions, pinned values, complete CET4 membership, Unicode, thresholds, argument errors, public resource error handling.");
    Ok(())
}
