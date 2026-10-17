//! Generated from the pinned installed Python oracle; do not edit by hand.
//! P0 fixture SHA-256: 6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1
//! Reference baseline SHA-256: 9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01
//! Installed annotation.py SHA-256: 76355b9a0d71882f8407640740865529744e8eb9c6400081a0f764188bd4cbfc
//! Oracle: CPython 3.12.4 / Unicode 15.0.0; source bytes 14266.
//! Canonical vector payload SHA-256: 9cf9d3f0befdc5757ad9514c50e71c3740a02af57f9b125842a7128ca7465935

use super::{Record, encode, lexicon_fixture};
use crate::data::{AnnotationResources, Field};

#[test]
fn p41_fixed_p0_query_category_fixtures() {
    let records = [
        Record {
            word: "Apple",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "I",
            fields: [None, Some("\u{12b}"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "May",
            fields: [None, Some("M\u{101}y"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "abandon",
            fields: [
                None,
                Some("\u{e5}bando\u{30a}n"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "age",
            fields: [None, Some("\u{101}ge"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "apple",
            fields: [
                Some("\u{e6}p\u{259}l"),
                Some("apple"),
                Some("app-le"),
                Some("app-le"),
                Some("apple"),
                Some("n. fixture apple"),
                None,
            ],
            state: 2,
        },
        Record {
            word: "ax",
            fields: [None, Some("\u{e3}x"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "axe",
            fields: [None, Some("\u{101}xe"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "bad",
            fields: [None, Some("b\u{101}dextra"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "bake",
            fields: [None, Some("b\u{101}ke"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "baked",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "book",
            fields: [None, Some("book"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "box",
            fields: [None, Some("b\u{f2}x"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "bus",
            fields: [None, Some("b\u{fb}s"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "don't",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "empty",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "first-rate",
            fields: [
                None,
                Some("fi\u{30a}rst-r\u{101}te"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "i",
            fields: [None, Some("\u{12b}"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "may",
            fields: [
                None,
                Some("m\u{e3}y"),
                None,
                None,
                None,
                Some("modal. fixture may"),
                None,
            ],
            state: 2,
        },
        Record {
            word: "noderivation",
            fields: [
                None,
                Some("noderivation"),
                Some("no-derivation"),
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "orphan",
            fields: [None, None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "pair",
            fields: [Some("known-ipa"), None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "pending-compound",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "play",
            fields: [None, Some("pl\u{101}y"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "plays",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "present",
            fields: [
                Some("selected"),
                Some("pr\u{117}\u{1e61}ent"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "queue",
            fields: [None, Some("q\u{16b}eue"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "rate",
            fields: [None, Some("r\u{101}te"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "second",
            fields: [None, Some("seco\u{30a}nd"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "second-rate",
            fields: [None, None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "sing",
            fields: [None, Some("s\u{129}ng"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "singe",
            fields: [None, Some("si\u{30a}nge"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "stale",
            fields: [None, Some("stale"), Some("sta-le"), None, None, None, None],
            state: 2,
        },
        Record {
            word: "stop",
            fields: [None, Some("st\u{f2}p"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "study",
            fields: [
                None,
                Some("st\u{fb}d\u{1e8f}"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "tail",
            fields: [None, Some("t\u{e3}il"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "the",
            fields: [
                None,
                Some("\u{1e6b}he\u{30a}"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "tie",
            fields: [None, Some("t\u{12b}e"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "walk",
            fields: [None, Some("w\u{e0}lk"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "walks",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "whale",
            fields: [
                None,
                Some("w\u{304}\u{1d559}\u{101}le"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "whim",
            fields: [
                None,
                Some("\u{1e98}\u{1d559}i\u{30a}m"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "yum",
            fields: [
                None,
                Some("\u{1e99}u\u{307}m"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "zeta",
            fields: [None, None, None, None, Some("apple"), None, None],
            state: 1,
        },
    ];
    let categories: &[(&str, &[usize])] = &[
        ("OXFORD_3000", &[]),
        ("OXFORD_5000", &[]),
        ("CET4", &[43, 5, 20]),
        ("CET6", &[]),
        ("CET4_CET6", &[]),
        ("IELTS", &[]),
        ("TEM-4", &[]),
        ("TEM-8", &[]),
        ("TOEFL", &[]),
        ("SAT", &[]),
        ("GMAT", &[]),
        ("GRE", &[]),
        ("BEC", &[]),
        ("Primary", &[]),
        ("Junior", &[]),
        ("Senior", &[]),
        ("College", &[]),
        ("COCA_20000", &[]),
        ("White", &[]),
        ("Yellow", &[]),
        ("Green", &[]),
        ("Blue", &[]),
        ("Red", &[]),
        ("Black", &[]),
    ];
    let lexicon = lexicon_fixture(encode(&records, categories, &[]));
    assert_eq!(
        crate::query::value_from("Apple", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "fixture-0269"
    );
    assert_eq!(
        crate::query::value_from("APPLE", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "fixture-0270"
    );
    assert_eq!(
        crate::query::value_from("May", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("M\u{101}y")),
        "fixture-0271"
    );
    assert_eq!(
        crate::query::value_from("May", Field::MeaningEn, Some("en"), || Ok(&lexicon)).unwrap(),
        None,
        "fixture-0272"
    );
    assert_eq!(
        crate::query::value_from("may", Field::MeaningEn, Some("en"), || Ok(&lexicon)).unwrap(),
        Some(String::from("modal. fixture may")),
        "fixture-0273"
    );
    assert_eq!(
        crate::query::value_from("pair", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("known-ipa")),
        "fixture-0274"
    );
    assert_eq!(
        crate::query::value_from("pair", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "fixture-0275"
    );
    assert_eq!(
        crate::query::value_from("present", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("selected")),
        "fixture-0276"
    );
    assert_eq!(
        crate::query::value_from("present", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("pr\u{117}\u{1e61}ent")),
        "fixture-0277"
    );
    assert_eq!(
        crate::query::value_from("apple", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("app-le")),
        "fixture-0278"
    );
    assert_eq!(
        crate::query::value_from("stale", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "fixture-0279"
    );
    assert_eq!(
        crate::query::value_from("noderivation", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "fixture-0280"
    );
    assert_eq!(
        crate::category::list_from("CET4", || Ok(&lexicon)).unwrap(),
        ["zeta", "apple", "orphan"],
        "fixture-0281"
    );
    assert!(
        !crate::category::kind_from("apple", "CET6", || Ok(&lexicon)).unwrap(),
        "fixture-0282"
    );
}

#[test]
fn p41_independent_unavailable_state_fixtures() {
    let records = [
        Record {
            word: "Apple",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Falsecategory",
            fields: [None, None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "Fieldconflict",
            fields: [Some("available ipa"), None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Fieldempty",
            fields: [Some("available ipa"), None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Fieldinvalid",
            fields: [Some("available ipa"), None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Fieldpending",
            fields: [Some("available ipa"), None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Fieldsource",
            fields: [Some("available ipa"), None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "I",
            fields: [None, Some("\u{12b}"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "May",
            fields: [None, Some("M\u{101}y"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "Setconflict",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Setempty",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Setinvalid",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Setpending",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "Setsource",
            fields: [None, None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "abandon",
            fields: [
                None,
                Some("\u{e5}bando\u{30a}n"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "age",
            fields: [None, Some("\u{101}ge"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "apple",
            fields: [
                Some("\u{e6}p\u{259}l"),
                Some("apple"),
                Some("app-le"),
                Some("app-le"),
                Some("apple"),
                Some("n. fixture apple"),
                None,
            ],
            state: 2,
        },
        Record {
            word: "ax",
            fields: [None, Some("\u{e3}x"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "axe",
            fields: [None, Some("\u{101}xe"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "bad",
            fields: [None, Some("b\u{101}dextra"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "bake",
            fields: [None, Some("b\u{101}ke"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "baked",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "book",
            fields: [None, Some("book"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "box",
            fields: [None, Some("b\u{f2}x"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "bus",
            fields: [None, Some("b\u{fb}s"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "don't",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "empty",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "falsecategory",
            fields: [
                Some("fixture ipa"),
                Some("falsecategory"),
                Some("falsecategory"),
                Some("falsecategory"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "fieldconflict",
            fields: [
                Some("fixture ipa"),
                Some("fieldconflict"),
                Some("fieldconflict"),
                Some("fieldconflict"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "fieldempty",
            fields: [
                Some("fixture ipa"),
                Some("fieldempty"),
                Some("fieldempty"),
                Some("fieldempty"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "fieldinvalid",
            fields: [
                Some("fixture ipa"),
                Some("fieldinvalid"),
                Some("fieldinvalid"),
                Some("fieldinvalid"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "fieldpending",
            fields: [
                Some("fixture ipa"),
                Some("fieldpending"),
                Some("fieldpending"),
                Some("fieldpending"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "fieldsource",
            fields: [
                Some("fixture ipa"),
                Some("fieldsource"),
                Some("fieldsource"),
                Some("fieldsource"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "first-rate",
            fields: [
                None,
                Some("fi\u{30a}rst-r\u{101}te"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "i",
            fields: [None, Some("\u{12b}"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "may",
            fields: [
                None,
                Some("m\u{e3}y"),
                None,
                None,
                None,
                Some("modal. fixture may"),
                None,
            ],
            state: 2,
        },
        Record {
            word: "noderivation",
            fields: [
                None,
                Some("noderivation"),
                Some("no-derivation"),
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "orphan",
            fields: [None, None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "pair",
            fields: [Some("known-ipa"), None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "pending-compound",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "play",
            fields: [None, Some("pl\u{101}y"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "plays",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "present",
            fields: [
                Some("selected"),
                Some("pr\u{117}\u{1e61}ent"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "queue",
            fields: [None, Some("q\u{16b}eue"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "rate",
            fields: [None, Some("r\u{101}te"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "second",
            fields: [None, Some("seco\u{30a}nd"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "second-rate",
            fields: [None, None, None, None, None, None, None],
            state: 1,
        },
        Record {
            word: "setconflict",
            fields: [
                Some("fixture ipa"),
                Some("setconflict"),
                Some("setconflict"),
                Some("setconflict"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "setempty",
            fields: [
                Some("fixture ipa"),
                Some("setempty"),
                Some("setempty"),
                Some("setempty"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "setinvalid",
            fields: [
                Some("fixture ipa"),
                Some("setinvalid"),
                Some("setinvalid"),
                Some("setinvalid"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "setpending",
            fields: [
                Some("fixture ipa"),
                Some("setpending"),
                Some("setpending"),
                Some("setpending"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "setsource",
            fields: [
                Some("fixture ipa"),
                Some("setsource"),
                Some("setsource"),
                Some("setsource"),
                Some("family"),
                Some("first\nsecond"),
                Some("\u{4e2d}\u{6587} e\u{301}"),
            ],
            state: 2,
        },
        Record {
            word: "sing",
            fields: [None, Some("s\u{129}ng"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "singe",
            fields: [None, Some("si\u{30a}nge"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "stale",
            fields: [None, Some("stale"), Some("sta-le"), None, None, None, None],
            state: 2,
        },
        Record {
            word: "stop",
            fields: [None, Some("st\u{f2}p"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "study",
            fields: [
                None,
                Some("st\u{fb}d\u{1e8f}"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "tail",
            fields: [None, Some("t\u{e3}il"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "the",
            fields: [
                None,
                Some("\u{1e6b}he\u{30a}"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "tie",
            fields: [None, Some("t\u{12b}e"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "walk",
            fields: [None, Some("w\u{e0}lk"), None, None, None, None, None],
            state: 2,
        },
        Record {
            word: "walks",
            fields: [None, None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "whale",
            fields: [
                None,
                Some("w\u{304}\u{1d559}\u{101}le"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "whim",
            fields: [
                None,
                Some("\u{1e98}\u{1d559}i\u{30a}m"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "yum",
            fields: [
                None,
                Some("\u{1e99}u\u{307}m"),
                None,
                None,
                None,
                None,
                None,
            ],
            state: 2,
        },
        Record {
            word: "zeta",
            fields: [None, None, None, None, Some("apple"), None, None],
            state: 1,
        },
    ];
    let categories: &[(&str, &[usize])] = &[
        ("OXFORD_3000", &[]),
        ("OXFORD_5000", &[]),
        (
            "CET4",
            &[65, 16, 27, 28, 29, 30, 31, 32, 47, 48, 49, 50, 51, 37],
        ),
        ("CET6", &[]),
        ("CET4_CET6", &[]),
        ("IELTS", &[]),
        ("TEM-4", &[]),
        ("TEM-8", &[]),
        ("TOEFL", &[]),
        ("SAT", &[]),
        ("GMAT", &[]),
        ("GRE", &[]),
        ("BEC", &[]),
        ("Primary", &[]),
        ("Junior", &[]),
        ("Senior", &[]),
        ("College", &[]),
        ("COCA_20000", &[]),
        ("White", &[]),
        ("Yellow", &[]),
        ("Green", &[]),
        ("Blue", &[]),
        ("Red", &[]),
        ("Black", &[]),
    ];
    let lexicon = lexicon_fixture(encode(&records, categories, &[]));
    assert_eq!(
        crate::query::value_from("Setsource", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-001"
    );
    assert_eq!(
        crate::query::value_from("Setsource", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-002"
    );
    assert_eq!(
        crate::query::value_from("Setsource", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-003"
    );
    assert_eq!(
        crate::query::value_from("Setsource", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-004"
    );
    assert_eq!(
        crate::query::value_from("Setsource", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-005"
    );
    assert_eq!(
        crate::query::value_from("Setsource", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-006"
    );
    assert_eq!(
        crate::query::value_from("Setsource", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-007"
    );
    assert!(
        !crate::category::kind_from("Setsource", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-008"
    );
    assert_eq!(
        crate::query::value_from("setsource", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-009"
    );
    assert_eq!(
        crate::query::value_from("setsource", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setsource")),
        "rare-010"
    );
    assert_eq!(
        crate::query::value_from("setsource", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setsource")),
        "rare-011"
    );
    assert_eq!(
        crate::query::value_from("setsource", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setsource")),
        "rare-012"
    );
    assert_eq!(
        crate::query::value_from("setsource", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-013"
    );
    assert_eq!(
        crate::query::value_from("setsource", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-014"
    );
    assert_eq!(
        crate::query::value_from("setsource", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-015"
    );
    assert!(
        crate::category::kind_from("setsource", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-016"
    );
    assert_eq!(
        crate::annotation::annotate_from("Setsource setsource SETSOURCE", 0, |_, _| Ok(Some(
            AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            }
        )))
        .unwrap(),
        "[Setsource] setsource SETSOURCE",
        "rare-017"
    );
    assert_eq!(
        crate::query::value_from("Setempty", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-018"
    );
    assert_eq!(
        crate::query::value_from("Setempty", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-019"
    );
    assert_eq!(
        crate::query::value_from("Setempty", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-020"
    );
    assert_eq!(
        crate::query::value_from("Setempty", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-021"
    );
    assert_eq!(
        crate::query::value_from("Setempty", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-022"
    );
    assert_eq!(
        crate::query::value_from("Setempty", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-023"
    );
    assert_eq!(
        crate::query::value_from("Setempty", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-024"
    );
    assert!(
        !crate::category::kind_from("Setempty", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-025"
    );
    assert_eq!(
        crate::query::value_from("setempty", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-026"
    );
    assert_eq!(
        crate::query::value_from("setempty", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setempty")),
        "rare-027"
    );
    assert_eq!(
        crate::query::value_from("setempty", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setempty")),
        "rare-028"
    );
    assert_eq!(
        crate::query::value_from("setempty", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setempty")),
        "rare-029"
    );
    assert_eq!(
        crate::query::value_from("setempty", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-030"
    );
    assert_eq!(
        crate::query::value_from("setempty", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-031"
    );
    assert_eq!(
        crate::query::value_from("setempty", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-032"
    );
    assert!(
        crate::category::kind_from("setempty", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-033"
    );
    assert_eq!(
        crate::annotation::annotate_from("Setempty setempty SETEMPTY", 0, |_, _| Ok(Some(
            AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            }
        )))
        .unwrap(),
        "[Setempty] setempty SETEMPTY",
        "rare-034"
    );
    assert_eq!(
        crate::query::value_from("Setpending", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-035"
    );
    assert_eq!(
        crate::query::value_from("Setpending", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-036"
    );
    assert_eq!(
        crate::query::value_from("Setpending", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-037"
    );
    assert_eq!(
        crate::query::value_from("Setpending", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-038"
    );
    assert_eq!(
        crate::query::value_from("Setpending", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-039"
    );
    assert_eq!(
        crate::query::value_from("Setpending", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-040"
    );
    assert_eq!(
        crate::query::value_from("Setpending", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-041"
    );
    assert!(
        !crate::category::kind_from("Setpending", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-042"
    );
    assert_eq!(
        crate::query::value_from("setpending", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-043"
    );
    assert_eq!(
        crate::query::value_from("setpending", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setpending")),
        "rare-044"
    );
    assert_eq!(
        crate::query::value_from("setpending", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setpending")),
        "rare-045"
    );
    assert_eq!(
        crate::query::value_from("setpending", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setpending")),
        "rare-046"
    );
    assert_eq!(
        crate::query::value_from("setpending", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-047"
    );
    assert_eq!(
        crate::query::value_from("setpending", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-048"
    );
    assert_eq!(
        crate::query::value_from("setpending", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-049"
    );
    assert!(
        crate::category::kind_from("setpending", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-050"
    );
    assert_eq!(
        crate::annotation::annotate_from("Setpending setpending SETPENDING", 0, |_, _| Ok(Some(
            AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            }
        )))
        .unwrap(),
        "[Setpending] setpending SETPENDING",
        "rare-051"
    );
    assert_eq!(
        crate::query::value_from("Setconflict", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-052"
    );
    assert_eq!(
        crate::query::value_from("Setconflict", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-053"
    );
    assert_eq!(
        crate::query::value_from("Setconflict", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-054"
    );
    assert_eq!(
        crate::query::value_from("Setconflict", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-055"
    );
    assert_eq!(
        crate::query::value_from("Setconflict", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-056"
    );
    assert_eq!(
        crate::query::value_from("Setconflict", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-057"
    );
    assert_eq!(
        crate::query::value_from("Setconflict", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-058"
    );
    assert!(
        !crate::category::kind_from("Setconflict", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-059"
    );
    assert_eq!(
        crate::query::value_from("setconflict", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-060"
    );
    assert_eq!(
        crate::query::value_from("setconflict", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setconflict")),
        "rare-061"
    );
    assert_eq!(
        crate::query::value_from("setconflict", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setconflict")),
        "rare-062"
    );
    assert_eq!(
        crate::query::value_from("setconflict", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setconflict")),
        "rare-063"
    );
    assert_eq!(
        crate::query::value_from("setconflict", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-064"
    );
    assert_eq!(
        crate::query::value_from("setconflict", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-065"
    );
    assert_eq!(
        crate::query::value_from("setconflict", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-066"
    );
    assert!(
        crate::category::kind_from("setconflict", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-067"
    );
    assert_eq!(
        crate::annotation::annotate_from("Setconflict setconflict SETCONFLICT", 0, |_, _| Ok(
            Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            })
        ))
        .unwrap(),
        "[Setconflict] setconflict SETCONFLICT",
        "rare-068"
    );
    assert_eq!(
        crate::query::value_from("Setinvalid", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-069"
    );
    assert_eq!(
        crate::query::value_from("Setinvalid", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-070"
    );
    assert_eq!(
        crate::query::value_from("Setinvalid", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-071"
    );
    assert_eq!(
        crate::query::value_from("Setinvalid", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-072"
    );
    assert_eq!(
        crate::query::value_from("Setinvalid", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-073"
    );
    assert_eq!(
        crate::query::value_from("Setinvalid", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-074"
    );
    assert_eq!(
        crate::query::value_from("Setinvalid", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-075"
    );
    assert!(
        !crate::category::kind_from("Setinvalid", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-076"
    );
    assert_eq!(
        crate::query::value_from("setinvalid", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-077"
    );
    assert_eq!(
        crate::query::value_from("setinvalid", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setinvalid")),
        "rare-078"
    );
    assert_eq!(
        crate::query::value_from("setinvalid", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setinvalid")),
        "rare-079"
    );
    assert_eq!(
        crate::query::value_from("setinvalid", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("setinvalid")),
        "rare-080"
    );
    assert_eq!(
        crate::query::value_from("setinvalid", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-081"
    );
    assert_eq!(
        crate::query::value_from("setinvalid", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-082"
    );
    assert_eq!(
        crate::query::value_from("setinvalid", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-083"
    );
    assert!(
        crate::category::kind_from("setinvalid", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-084"
    );
    assert_eq!(
        crate::annotation::annotate_from("Setinvalid setinvalid SETINVALID", 0, |_, _| Ok(Some(
            AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            }
        )))
        .unwrap(),
        "[Setinvalid] setinvalid SETINVALID",
        "rare-085"
    );
    assert_eq!(
        crate::query::value_from("Fieldsource", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("available ipa")),
        "rare-086"
    );
    assert_eq!(
        crate::query::value_from("Fieldsource", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-087"
    );
    assert_eq!(
        crate::query::value_from("Fieldsource", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-088"
    );
    assert_eq!(
        crate::query::value_from("Fieldsource", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-089"
    );
    assert_eq!(
        crate::query::value_from("Fieldsource", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-090"
    );
    assert_eq!(
        crate::query::value_from("Fieldsource", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-091"
    );
    assert_eq!(
        crate::query::value_from("Fieldsource", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-092"
    );
    assert!(
        !crate::category::kind_from("Fieldsource", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-093"
    );
    assert_eq!(
        crate::query::value_from("fieldsource", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-094"
    );
    assert_eq!(
        crate::query::value_from("fieldsource", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldsource")),
        "rare-095"
    );
    assert_eq!(
        crate::query::value_from("fieldsource", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldsource")),
        "rare-096"
    );
    assert_eq!(
        crate::query::value_from("fieldsource", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldsource")),
        "rare-097"
    );
    assert_eq!(
        crate::query::value_from("fieldsource", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-098"
    );
    assert_eq!(
        crate::query::value_from("fieldsource", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-099"
    );
    assert_eq!(
        crate::query::value_from("fieldsource", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-100"
    );
    assert!(
        crate::category::kind_from("fieldsource", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-101"
    );
    assert_eq!(
        crate::annotation::annotate_from("Fieldsource fieldsource FIELDSOURCE", 0, |_, _| Ok(
            Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            })
        ))
        .unwrap(),
        "[Fieldsource] fieldsource FIELDSOURCE",
        "rare-102"
    );
    assert_eq!(
        crate::query::value_from("Fieldempty", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("available ipa")),
        "rare-103"
    );
    assert_eq!(
        crate::query::value_from("Fieldempty", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-104"
    );
    assert_eq!(
        crate::query::value_from("Fieldempty", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-105"
    );
    assert_eq!(
        crate::query::value_from("Fieldempty", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-106"
    );
    assert_eq!(
        crate::query::value_from("Fieldempty", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-107"
    );
    assert_eq!(
        crate::query::value_from("Fieldempty", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-108"
    );
    assert_eq!(
        crate::query::value_from("Fieldempty", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        None,
        "rare-109"
    );
    assert!(
        !crate::category::kind_from("Fieldempty", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-110"
    );
    assert_eq!(
        crate::query::value_from("fieldempty", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-111"
    );
    assert_eq!(
        crate::query::value_from("fieldempty", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldempty")),
        "rare-112"
    );
    assert_eq!(
        crate::query::value_from("fieldempty", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldempty")),
        "rare-113"
    );
    assert_eq!(
        crate::query::value_from("fieldempty", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldempty")),
        "rare-114"
    );
    assert_eq!(
        crate::query::value_from("fieldempty", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-115"
    );
    assert_eq!(
        crate::query::value_from("fieldempty", Field::MeaningEn, Some("en"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-116"
    );
    assert_eq!(
        crate::query::value_from("fieldempty", Field::MeaningZh, Some("zh"), || Ok(&lexicon))
            .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-117"
    );
    assert!(
        crate::category::kind_from("fieldempty", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-118"
    );
    assert_eq!(
        crate::annotation::annotate_from("Fieldempty fieldempty FIELDEMPTY", 0, |_, _| Ok(Some(
            AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            }
        )))
        .unwrap(),
        "[Fieldempty] fieldempty FIELDEMPTY",
        "rare-119"
    );
    assert_eq!(
        crate::query::value_from("Fieldpending", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("available ipa")),
        "rare-120"
    );
    assert_eq!(
        crate::query::value_from("Fieldpending", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-121"
    );
    assert_eq!(
        crate::query::value_from("Fieldpending", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-122"
    );
    assert_eq!(
        crate::query::value_from("Fieldpending", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-123"
    );
    assert_eq!(
        crate::query::value_from("Fieldpending", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-124"
    );
    assert_eq!(
        crate::query::value_from("Fieldpending", Field::MeaningEn, Some("en"), || Ok(
            &lexicon
        ))
        .unwrap(),
        None,
        "rare-125"
    );
    assert_eq!(
        crate::query::value_from("Fieldpending", Field::MeaningZh, Some("zh"), || Ok(
            &lexicon
        ))
        .unwrap(),
        None,
        "rare-126"
    );
    assert!(
        !crate::category::kind_from("Fieldpending", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-127"
    );
    assert_eq!(
        crate::query::value_from("fieldpending", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-128"
    );
    assert_eq!(
        crate::query::value_from("fieldpending", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldpending")),
        "rare-129"
    );
    assert_eq!(
        crate::query::value_from("fieldpending", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldpending")),
        "rare-130"
    );
    assert_eq!(
        crate::query::value_from("fieldpending", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldpending")),
        "rare-131"
    );
    assert_eq!(
        crate::query::value_from("fieldpending", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-132"
    );
    assert_eq!(
        crate::query::value_from("fieldpending", Field::MeaningEn, Some("en"), || Ok(
            &lexicon
        ))
        .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-133"
    );
    assert_eq!(
        crate::query::value_from("fieldpending", Field::MeaningZh, Some("zh"), || Ok(
            &lexicon
        ))
        .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-134"
    );
    assert!(
        crate::category::kind_from("fieldpending", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-135"
    );
    assert_eq!(
        crate::annotation::annotate_from("Fieldpending fieldpending FIELDPENDING", 0, |_, _| Ok(
            Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            })
        ))
        .unwrap(),
        "[Fieldpending] fieldpending FIELDPENDING",
        "rare-136"
    );
    assert_eq!(
        crate::query::value_from("Fieldconflict", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("available ipa")),
        "rare-137"
    );
    assert_eq!(
        crate::query::value_from("Fieldconflict", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-138"
    );
    assert_eq!(
        crate::query::value_from("Fieldconflict", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-139"
    );
    assert_eq!(
        crate::query::value_from("Fieldconflict", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-140"
    );
    assert_eq!(
        crate::query::value_from("Fieldconflict", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-141"
    );
    assert_eq!(
        crate::query::value_from("Fieldconflict", Field::MeaningEn, Some("en"), || Ok(
            &lexicon
        ))
        .unwrap(),
        None,
        "rare-142"
    );
    assert_eq!(
        crate::query::value_from("Fieldconflict", Field::MeaningZh, Some("zh"), || Ok(
            &lexicon
        ))
        .unwrap(),
        None,
        "rare-143"
    );
    assert!(
        !crate::category::kind_from("Fieldconflict", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-144"
    );
    assert_eq!(
        crate::query::value_from("fieldconflict", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-145"
    );
    assert_eq!(
        crate::query::value_from("fieldconflict", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldconflict")),
        "rare-146"
    );
    assert_eq!(
        crate::query::value_from("fieldconflict", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldconflict")),
        "rare-147"
    );
    assert_eq!(
        crate::query::value_from("fieldconflict", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldconflict")),
        "rare-148"
    );
    assert_eq!(
        crate::query::value_from("fieldconflict", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-149"
    );
    assert_eq!(
        crate::query::value_from("fieldconflict", Field::MeaningEn, Some("en"), || Ok(
            &lexicon
        ))
        .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-150"
    );
    assert_eq!(
        crate::query::value_from("fieldconflict", Field::MeaningZh, Some("zh"), || Ok(
            &lexicon
        ))
        .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-151"
    );
    assert!(
        crate::category::kind_from("fieldconflict", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-152"
    );
    assert_eq!(
        crate::annotation::annotate_from(
            "Fieldconflict fieldconflict FIELDCONFLICT",
            0,
            |_, _| Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            }))
        )
        .unwrap(),
        "[Fieldconflict] fieldconflict FIELDCONFLICT",
        "rare-153"
    );
    assert_eq!(
        crate::query::value_from("Fieldinvalid", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("available ipa")),
        "rare-154"
    );
    assert_eq!(
        crate::query::value_from("Fieldinvalid", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-155"
    );
    assert_eq!(
        crate::query::value_from("Fieldinvalid", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-156"
    );
    assert_eq!(
        crate::query::value_from("Fieldinvalid", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-157"
    );
    assert_eq!(
        crate::query::value_from("Fieldinvalid", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        None,
        "rare-158"
    );
    assert_eq!(
        crate::query::value_from("Fieldinvalid", Field::MeaningEn, Some("en"), || Ok(
            &lexicon
        ))
        .unwrap(),
        None,
        "rare-159"
    );
    assert_eq!(
        crate::query::value_from("Fieldinvalid", Field::MeaningZh, Some("zh"), || Ok(
            &lexicon
        ))
        .unwrap(),
        None,
        "rare-160"
    );
    assert!(
        !crate::category::kind_from("Fieldinvalid", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-161"
    );
    assert_eq!(
        crate::query::value_from("fieldinvalid", Field::Ipa, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fixture ipa")),
        "rare-162"
    );
    assert_eq!(
        crate::query::value_from("fieldinvalid", Field::Ips, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldinvalid")),
        "rare-163"
    );
    assert_eq!(
        crate::query::value_from("fieldinvalid", Field::Ism, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldinvalid")),
        "rare-164"
    );
    assert_eq!(
        crate::query::value_from("fieldinvalid", Field::Ipsm, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("fieldinvalid")),
        "rare-165"
    );
    assert_eq!(
        crate::query::value_from("fieldinvalid", Field::RootLemma, None, || Ok(&lexicon)).unwrap(),
        Some(String::from("family")),
        "rare-166"
    );
    assert_eq!(
        crate::query::value_from("fieldinvalid", Field::MeaningEn, Some("en"), || Ok(
            &lexicon
        ))
        .unwrap(),
        Some(String::from("first\nsecond")),
        "rare-167"
    );
    assert_eq!(
        crate::query::value_from("fieldinvalid", Field::MeaningZh, Some("zh"), || Ok(
            &lexicon
        ))
        .unwrap(),
        Some(String::from("\u{4e2d}\u{6587} e\u{301}")),
        "rare-168"
    );
    assert!(
        crate::category::kind_from("fieldinvalid", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-169"
    );
    assert_eq!(
        crate::annotation::annotate_from("Fieldinvalid fieldinvalid FIELDINVALID", 0, |_, _| Ok(
            Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None
            })
        ))
        .unwrap(),
        "[Fieldinvalid] fieldinvalid FIELDINVALID",
        "rare-170"
    );
    assert!(
        !crate::category::kind_from("Falsecategory", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-171"
    );
    assert!(
        crate::category::kind_from("falsecategory", "CET4", || Ok(&lexicon)).unwrap(),
        "rare-172"
    );
    assert_eq!(
        crate::category::labels_from(|| Ok(&lexicon)).unwrap(),
        [
            "OXFORD_3000",
            "OXFORD_5000",
            "CET4",
            "CET6",
            "CET4_CET6",
            "IELTS",
            "TEM-4",
            "TEM-8",
            "TOEFL",
            "SAT",
            "GMAT",
            "GRE",
            "BEC",
            "Primary",
            "Junior",
            "Senior",
            "College",
            "COCA_20000",
            "White",
            "Yellow",
            "Green",
            "Blue",
            "Red",
            "Black"
        ],
        "rare-173"
    );
    assert_eq!(
        crate::category::list_from("OXFORD_3000", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-00"
    );
    assert_eq!(
        crate::category::list_from("OXFORD_5000", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-01"
    );
    assert_eq!(
        crate::category::list_from("CET4", || Ok(&lexicon)).unwrap(),
        [
            "zeta",
            "apple",
            "falsecategory",
            "fieldconflict",
            "fieldempty",
            "fieldinvalid",
            "fieldpending",
            "fieldsource",
            "setconflict",
            "setempty",
            "setinvalid",
            "setpending",
            "setsource",
            "orphan"
        ],
        "complete-category-02"
    );
    assert_eq!(
        crate::category::list_from("CET6", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-03"
    );
    assert_eq!(
        crate::category::list_from("CET4_CET6", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-04"
    );
    assert_eq!(
        crate::category::list_from("IELTS", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-05"
    );
    assert_eq!(
        crate::category::list_from("TEM-4", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-06"
    );
    assert_eq!(
        crate::category::list_from("TEM-8", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-07"
    );
    assert_eq!(
        crate::category::list_from("TOEFL", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-08"
    );
    assert_eq!(
        crate::category::list_from("SAT", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-09"
    );
    assert_eq!(
        crate::category::list_from("GMAT", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-10"
    );
    assert_eq!(
        crate::category::list_from("GRE", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-11"
    );
    assert_eq!(
        crate::category::list_from("BEC", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-12"
    );
    assert_eq!(
        crate::category::list_from("Primary", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-13"
    );
    assert_eq!(
        crate::category::list_from("Junior", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-14"
    );
    assert_eq!(
        crate::category::list_from("Senior", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-15"
    );
    assert_eq!(
        crate::category::list_from("College", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-16"
    );
    assert_eq!(
        crate::category::list_from("COCA_20000", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-17"
    );
    assert_eq!(
        crate::category::list_from("White", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-18"
    );
    assert_eq!(
        crate::category::list_from("Yellow", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-19"
    );
    assert_eq!(
        crate::category::list_from("Green", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-20"
    );
    assert_eq!(
        crate::category::list_from("Blue", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-21"
    );
    assert_eq!(
        crate::category::list_from("Red", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-22"
    );
    assert_eq!(
        crate::category::list_from("Black", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new(),
        "complete-category-23"
    );
}
