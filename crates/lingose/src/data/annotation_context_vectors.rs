//! Generated from the pinned installed Python oracle; do not edit by hand.
//! P0 fixture SHA-256: 6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1
//! Reference baseline SHA-256: 9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01
//! Installed annotation.py SHA-256: 76355b9a0d71882f8407640740865529744e8eb9c6400081a0f764188bd4cbfc
//! Oracle: CPython 3.12.4 / Unicode 15.0.0; source bytes 14266.
//! Canonical vector payload SHA-256: 2440761a76979cdc371bf04c7a049ac11b0a99a3078b3c66828d5077ddd13396

use super::{Record, encode, lexicon_fixture};
use crate::annotation::annotate_from;
use crate::data::AnnotationResources;

#[test]
fn pinned_python_p0_complete_fixture() {
    let entries = [
        ("Apple", None, 0),
        ("I", Some("\u{12b}"), 2),
        ("May", Some("M\u{101}y"), 2),
        ("abandon", Some("\u{e5}bando\u{30a}n"), 2),
        ("age", Some("\u{101}ge"), 2),
        ("apple", Some("apple"), 2),
        ("ax", Some("\u{e3}x"), 2),
        ("axe", Some("\u{101}xe"), 2),
        ("bad", Some("b\u{101}dextra"), 2),
        ("bake", Some("b\u{101}ke"), 2),
        ("baked", None, 0),
        ("book", Some("book"), 2),
        ("box", Some("b\u{f2}x"), 2),
        ("bus", Some("b\u{fb}s"), 2),
        ("don't", None, 0),
        ("empty", None, 0),
        ("first-rate", Some("fi\u{30a}rst-r\u{101}te"), 2),
        ("i", Some("\u{12b}"), 2),
        ("may", Some("m\u{e3}y"), 2),
        ("noderivation", Some("noderivation"), 2),
        ("orphan", None, 1),
        ("pair", None, 1),
        ("pending-compound", None, 0),
        ("play", Some("pl\u{101}y"), 2),
        ("plays", None, 0),
        ("present", Some("pr\u{117}\u{1e61}ent"), 2),
        ("queue", Some("q\u{16b}eue"), 2),
        ("rate", Some("r\u{101}te"), 2),
        ("second", Some("seco\u{30a}nd"), 2),
        ("second-rate", None, 1),
        ("sing", Some("s\u{129}ng"), 2),
        ("singe", Some("si\u{30a}nge"), 2),
        ("stale", Some("stale"), 2),
        ("stop", Some("st\u{f2}p"), 2),
        ("study", Some("st\u{fb}d\u{1e8f}"), 2),
        ("tail", Some("t\u{e3}il"), 2),
        ("the", Some("\u{1e6b}he\u{30a}"), 2),
        ("tie", Some("t\u{12b}e"), 2),
        ("walk", Some("w\u{e0}lk"), 2),
        ("walks", None, 0),
        ("whale", Some("w\u{304}\u{1d559}\u{101}le"), 2),
        ("whim", Some("\u{1e98}\u{1d559}i\u{30a}m"), 2),
        ("yum", Some("\u{1e99}u\u{307}m"), 2),
        ("zeta", None, 1),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[
        (
            "fixture-0283",
            "Apple APPLE aPpLe May may",
            "[Apple] APPLE aPpLe M\u{101}y m\u{e3}y",
        ),
        (
            "fixture-0284",
            "the book THE apple The hour the university the",
            "\u{1e6b}he\u{30a} book \u{1e6a}H\u{112} apple \u{1e6a}he\u{30a} [hour] \u{1e6b}h\u{113} [university] \u{1e6b}he\u{30a}",
        ),
        (
            "fixture-0285",
            "the \"apple\" the (apple) the\napple the, apple the\n\napple",
            "\u{1e6b}h\u{113} \"apple\" \u{1e6b}h\u{113} (apple) \u{1e6b}h\u{113}\napple \u{1e6b}he\u{30a}, apple \u{1e6b}he\u{30a}\n\napple",
        ),
        (
            "fixture-0286",
            "WHALE WHIM YUM bad BAD",
            "W\u{305}\u{210d}\u{100}LE W\u{30a}\u{210d}I\u{30a}M Y\u{30a}U\u{307}M [bad] [BAD]",
        ),
        (
            "fixture-0287",
            "walks boxes baked baking studies studied stopped stopping plays tying",
            "[walks] b\u{f2}xes [baked] b\u{101}king st\u{fb}dies st\u{fb}died st\u{f2}pped st\u{f2}pping [plays] tying",
        ),
        (
            "fixture-0288",
            "ageing singeing queueing busing singing axes is",
            "\u{101}geing si\u{30a}ngeing q\u{16b}eueing b\u{fb}sing s\u{129}nging [axes] [is]",
        ),
        (
            "fixture-0289",
            "first-rate second-rate second-puldsm pending-compound empty",
            "fi\u{30a}rst-r\u{101}te seco\u{30a}nd-r\u{101}te seco\u{30a}nd-[puldsm] [pending-compound] [empty]",
        ),
        (
            "fixture-0290",
            "don't doesn't aren't I'm you're o'clock don\u{2019}t doesn\u{2019}t aren\u{2019}t I\u{2019}m you\u{2019}re o\u{2019}clock",
            "[don't] d\u{f4}\u{1d556}\u{1e61}n't \u{e0}r\u{1d556}n't I'm yo\u{16b}'re o\u{30a}'clock [don\u{2019}t] d\u{f4}\u{1d556}\u{1e61}n\u{2019}t \u{e0}r\u{1d556}n\u{2019}t I\u{2019}m yo\u{16b}\u{2019}re o\u{30a}\u{2019}clock",
        ),
        (
            "fixture-0291",
            "caf\u{e9} apple123 \u{4e2d}\u{6587}apple e\u{301} \u{4e2d}\u{6587} \u{1f600}",
            "caf\u{e9} apple123 \u{4e2d}\u{6587}apple e\u{301} \u{4e2d}\u{6587} \u{1f600}",
        ),
        ("fixture-0292", "unknownwordzz", "[unknownwordzz]"),
        (
            "fixture-0293",
            "Messrs. p.m. a lot a lottery unlisted tail abandoned",
            "[Messrs]. [p].[m]. [a] [lot] [a] [lottery] [unlisted] t\u{e3}il \u{e5}bando\u{30a}ned",
        ),
        (
            "fixture-0294",
            "walks plays baked don't is",
            "[walks] [plays] [baked] [don't] [is]",
        ),
        (
            "fixture-0295",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            "\u{1e6b}h\u{113} \u{e5}bando\u{30a}n \u{e5}bando\u{30a}ned [unlisted] [Messrs]. [p].[m]. [a] [lot] t\u{e3}il",
        ),
    ];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_saved_states_precede_context_and_fallback() {
    let entries = [
        ("THE", None, 1),
        ("The", None, 0),
        ("apple", Some("\u{e5}pple"), 2),
        ("apple's", None, 0),
        ("apple\u{2019}book", None, 0),
        ("aren't", Some("wrong"), 2),
        ("book", Some("b\u{f2}ok"), 2),
        ("book's", None, 1),
        ("doesn't", None, 1),
        ("don't", None, 0),
        ("o'clock", None, 1),
        ("rate", Some("r\u{101}te"), 2),
        ("second", Some("seco\u{30a}nd"), 2),
        ("second-apple", None, 0),
        ("second-book", Some("wrong"), 2),
        ("second-rate", None, 1),
        ("the", Some("wrong"), 2),
        ("walk", Some("w\u{e0}lk"), 2),
        ("walked", None, 1),
        ("walking", Some("wrong"), 2),
        ("walks", None, 0),
        ("you're", Some("y\u{f2}u're"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[
        (
            "saved_states_precede_context_and_fallback-01",
            "the apple The apple THE apple tHe apple the book the",
            "\u{1e6b}h\u{113} \u{e5}pple [The] \u{e5}pple \u{1e6a}H\u{112} \u{e5}pple \u{1e6b}H\u{113} \u{e5}pple \u{1e6b}he\u{30a} b\u{f2}ok \u{1e6b}he\u{30a}",
        ),
        (
            "saved_states_precede_context_and_fallback-02",
            "don't doesn\u{2019}t aren't I\u{2019}m you're o\u{2019}clock DON\u{2019}T DOESN\u{2019}T AREN\u{2019}T I\u{2019}M YOU\u{2019}RE O\u{2019}CLOCK",
            "[don't] d\u{f4}\u{1d556}\u{1e61}n\u{2019}t [aren't] I\u{2019}m y\u{f2}u're o\u{30a}\u{2019}clock [DON\u{2019}T] D\u{d4}\u{1d53c}\u{1e60}N\u{2019}T [AREN\u{2019}T] I\u{2019}M Y\u{d2}U\u{2019}RE O\u{30a}\u{2019}CLOCK",
        ),
        (
            "saved_states_precede_context_and_fallback-03",
            "second-rate second-apple second-book second-rate-apple apple-book second-unknown",
            "seco\u{30a}nd-r\u{101}te [second-apple] [second-book] seco\u{30a}nd-r\u{101}te-\u{e5}pple \u{e5}pple-b\u{f2}ok seco\u{30a}nd-[unknown]",
        ),
        (
            "saved_states_precede_context_and_fallback-04",
            "walks walked walking WALKED WALKING walks-book walked-book walking-book",
            "[walks] w\u{e0}lked [walking] W\u{c0}LKED [WALKING] [walks]-b\u{f2}ok w\u{e0}lked-b\u{f2}ok [walking]-b\u{f2}ok",
        ),
        (
            "saved_states_precede_context_and_fallback-05",
            "apple's apple\u{2019}s book's book\u{2019}s apple\u{2019}book apple'book",
            "[apple's] [apple\u{2019}s] b\u{f2}ok's b\u{f2}ok\u{2019}s [apple\u{2019}book] \u{e5}pple'book",
        ),
        (
            "saved_states_precede_context_and_fallback-06",
            "the's apple the\u{2019}s apple the-apple the-book apple-the apple apple-the, apple",
            "\u{1e6b}he\u{30a}'s \u{e5}pple \u{1e6b}he\u{30a}\u{2019}s \u{e5}pple \u{1e6b}h\u{113}-\u{e5}pple \u{1e6b}he\u{30a}-b\u{f2}ok \u{e5}pple-\u{1e6b}h\u{113} \u{e5}pple \u{e5}pple-\u{1e6b}he\u{30a}, \u{e5}pple",
        ),
        (
            "saved_states_precede_context_and_fallback-07",
            "The-apple THE-APPLE tHe-aPpLe apple-The apple apple-THE apple",
            "[The]-\u{e5}pple \u{1e6a}H\u{112}-\u{c5}PPLE \u{1e6b}H\u{113}-\u{e5}PpLe \u{e5}pple-[The] \u{e5}pple \u{e5}pple-\u{1e6a}H\u{112} \u{e5}pple",
        ),
    ];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_apostrophe_prefers_nt_prefix_and_cuts_unicode_scalars() {
    let entries = [
        ("a", Some("\u{101}"), 2),
        ("apple", Some("\u{e5}pple"), 2),
        ("book", Some("book"), 2),
        ("ca", Some("c\u{101}"), 2),
        ("can", Some("c\u{e3}n"), 2),
        ("the", Some("wrong"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[
        (
            "apostrophe_prefers_nt_prefix_and_cuts_unicode_scalars-01",
            "can't can\u{2019}t CAN\u{2019}T CaN\u{2019}T can't've can\u{2019}t\u{2019}ve can\u{2019}t\u{2019}can\u{2019}t",
            "c\u{101}n't c\u{101}n\u{2019}t C\u{100}N\u{2019}T C\u{101}N\u{2019}T c\u{e3}n't've c\u{e3}n\u{2019}t\u{2019}ve c\u{e3}n\u{2019}t\u{2019}can\u{2019}t",
        ),
        (
            "apostrophe_prefers_nt_prefix_and_cuts_unicode_scalars-02",
            "a\u{2019}can\u{2019}t a'can't ca\u{2019}can\u{2019}t apple\u{2019}can\u{2019}t APPLE\u{2019}CAN\u{2019}T a\u{2019}can\u{2019}t\u{2019}book",
            "\u{101}\u{2019}can\u{2019}t \u{101}'can't c\u{101}\u{2019}can\u{2019}t \u{e5}pple\u{2019}can\u{2019}t \u{c5}PPLE\u{2019}CAN\u{2019}T \u{101}\u{2019}can\u{2019}t\u{2019}book",
        ),
        (
            "apostrophe_prefers_nt_prefix_and_cuts_unicode_scalars-03",
            "apple'book apple\u{2019}book apple's APPLE\u{2019}S aPpLe\u{2019}s apple\u{2019}unknown\u{2019}book",
            "\u{e5}pple'book \u{e5}pple\u{2019}book \u{e5}pple's \u{c5}PPLE\u{2019}S \u{e5}PpLe\u{2019}s \u{e5}pple\u{2019}unknown\u{2019}book",
        ),
        (
            "apostrophe_prefers_nt_prefix_and_cuts_unicode_scalars-04",
            "the's apple the\u{2019}s apple THE\u{2019}S APPLE the-the\u{2019}s apple the-apple\u{2019}s the\u{2019}s-apple",
            "\u{1e6b}he\u{30a}'s \u{e5}pple \u{1e6b}he\u{30a}\u{2019}s \u{e5}pple \u{1e6a}HE\u{30a}\u{2019}S \u{c5}PPLE \u{1e6b}he\u{30a}-\u{1e6b}he\u{30a}\u{2019}s \u{e5}pple \u{1e6b}h\u{113}-\u{e5}pple\u{2019}s \u{1e6b}he\u{30a}\u{2019}s-\u{e5}pple",
        ),
    ];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_apostrophe_first_prefix_blocked() {
    let entries = [
        ("a", Some("\u{101}"), 2),
        ("apple", Some("\u{e5}pple"), 2),
        ("book", Some("book"), 2),
        ("ca", None, 0),
        ("can", Some("c\u{e3}n"), 2),
        ("the", Some("wrong"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "apostrophe_first_prefix_blocked-01",
        "can't can\u{2019}t CAN\u{2019}T CaN\u{2019}T a\u{2019}can\u{2019}t ca\u{2019}can\u{2019}t can't've can\u{2019}t\u{2019}ve",
        "c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T C\u{e3}N\u{2019}T \u{101}\u{2019}can\u{2019}t [ca\u{2019}can\u{2019}t] c\u{e3}n't've c\u{e3}n\u{2019}t\u{2019}ve",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_apostrophe_first_prefix_fallback() {
    let entries = [
        ("a", Some("\u{101}"), 2),
        ("apple", Some("\u{e5}pple"), 2),
        ("book", Some("book"), 2),
        ("ca", None, 1),
        ("can", Some("c\u{e3}n"), 2),
        ("the", Some("wrong"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "apostrophe_first_prefix_fallback-01",
        "can't can\u{2019}t CAN\u{2019}T CaN\u{2019}T a\u{2019}can\u{2019}t ca\u{2019}can\u{2019}t can't've can\u{2019}t\u{2019}ve",
        "c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T C\u{e3}N\u{2019}T \u{101}\u{2019}can\u{2019}t [ca\u{2019}can\u{2019}t] c\u{e3}n't've c\u{e3}n\u{2019}t\u{2019}ve",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_apostrophe_first_prefix_malformed() {
    let entries = [
        ("a", Some("\u{101}"), 2),
        ("apple", Some("\u{e5}pple"), 2),
        ("book", Some("book"), 2),
        ("ca", Some("wrong"), 2),
        ("can", Some("c\u{e3}n"), 2),
        ("the", Some("wrong"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "apostrophe_first_prefix_malformed-01",
        "can't can\u{2019}t CAN\u{2019}T CaN\u{2019}T a\u{2019}can\u{2019}t ca\u{2019}can\u{2019}t can't've can\u{2019}t\u{2019}ve",
        "c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T C\u{e3}N\u{2019}T \u{101}\u{2019}can\u{2019}t [ca\u{2019}can\u{2019}t] c\u{e3}n't've c\u{e3}n\u{2019}t\u{2019}ve",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_same_outputs() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", Some("b\u{fb}s"), 2),
        ("buse", Some("b\u{fb}se"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_same_outputs-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "b\u{fb}ses B\u{db}SES B\u{fb}SeS b\u{fb}ses' b\u{fb}ses\u{2019} b\u{fb}ses-book b\u{fb}ses\u{2019}book",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_different_outputs() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", Some("b\u{fb}s"), 2),
        ("buse", Some("b\u{f9}se"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_different_outputs-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "[buses] [BUSES] [BuSeS] [buses]' [buses]\u{2019} [buses]-book [buses\u{2019}book]",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_blocked_first() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", None, 0),
        ("buse", Some("b\u{fb}se"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_blocked_first-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "[buses] [BUSES] [BuSeS] [buses]' [buses]\u{2019} [buses]-book [buses\u{2019}book]",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_blocked_second() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", Some("b\u{fb}s"), 2),
        ("buse", None, 0),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_blocked_second-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "[buses] [BUSES] [BuSeS] [buses]' [buses]\u{2019} [buses]-book [buses\u{2019}book]",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_fallback_first() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", None, 1),
        ("buse", Some("b\u{fb}se"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_fallback_first-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "b\u{fb}ses B\u{db}SES B\u{fb}SeS b\u{fb}ses' b\u{fb}ses\u{2019} b\u{fb}ses-book b\u{fb}ses\u{2019}book",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_fallback_second() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", Some("b\u{fb}s"), 2),
        ("buse", None, 1),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_fallback_second-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "b\u{fb}ses B\u{db}SES B\u{fb}SeS b\u{fb}ses' b\u{fb}ses\u{2019} b\u{fb}ses-book b\u{fb}ses\u{2019}book",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_malformed_first() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", Some("wrong"), 2),
        ("buse", Some("b\u{fb}se"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_malformed_first-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "b\u{fb}ses B\u{db}SES B\u{fb}SeS b\u{fb}ses' b\u{fb}ses\u{2019} b\u{fb}ses-book b\u{fb}ses\u{2019}book",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_malformed_second() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", Some("b\u{fb}s"), 2),
        ("buse", Some("wrong"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_malformed_second-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "b\u{fb}ses B\u{db}SES B\u{fb}SeS b\u{fb}ses' b\u{fb}ses\u{2019} b\u{fb}ses-book b\u{fb}ses\u{2019}book",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_absent_first() {
    let entries = [("book", Some("book"), 2), ("buse", Some("b\u{fb}se"), 2)];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_absent_first-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "b\u{fb}ses B\u{db}SES B\u{fb}SeS b\u{fb}ses' b\u{fb}ses\u{2019} b\u{fb}ses-book b\u{fb}ses\u{2019}book",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_absent_second() {
    let entries = [("book", Some("book"), 2), ("bus", Some("b\u{fb}s"), 2)];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_absent_second-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "b\u{fb}ses B\u{db}SES B\u{fb}SeS b\u{fb}ses' b\u{fb}ses\u{2019} b\u{fb}ses-book b\u{fb}ses\u{2019}book",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_both_malformed() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", Some("wrong"), 2),
        ("buse", Some("wrong"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_both_malformed-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "[buses] [BUSES] [BuSeS] [buses]' [buses]\u{2019} [buses]-book [buses\u{2019}book]",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_buses_both_fallback() {
    let entries = [
        ("book", Some("book"), 2),
        ("bus", None, 1),
        ("buse", None, 1),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[(
        "inflection_buses_both_fallback-01",
        "buses BUSES BuSeS buses' buses\u{2019} buses-book buses\u{2019}book",
        "[buses] [BUSES] [BuSeS] [buses]' [buses]\u{2019} [buses]-book [buses\u{2019}book]",
    )];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_candidate_first_existing_variant() {
    let entries = [
        ("BUS", None, 1),
        ("Bus", None, 0),
        ("Buse", Some("wrong"), 2),
        ("bus", Some("b\u{fb}s"), 2),
        ("buse", Some("b\u{fb}se"), 2),
        ("buses", None, 1),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[
        (
            "inflection_candidate_first_existing_variant-01",
            "buses BUSES Buses BuSeS bUsEs",
            "b\u{fb}ses B\u{db}SES [Buses] B\u{fb}SeS b\u{db}sEs",
        ),
        (
            "inflection_candidate_first_existing_variant-02",
            "buses buses\u{2019} buses-book",
            "b\u{fb}ses b\u{fb}ses\u{2019} b\u{fb}ses-[book]",
        ),
    ];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}

#[test]
fn pinned_python_inflection_projection_keeps_clusters_and_spelling() {
    let entries = [
        ("age", Some("\u{101}ge"), 2),
        ("bake", Some("b\u{101}ke"), 2),
        ("box", Some("b\u{f2}x"), 2),
        ("cry", Some("cr\u{1e8f}"), 2),
        ("die", Some("d\u{12b}e"), 2),
        ("dye", Some("d\u{1e8f}e"), 2),
        ("fly", Some("fl\u{1e8f}"), 2),
        ("go", Some("g\u{14d}"), 2),
        ("hoe", Some("h\u{14d}e"), 2),
        ("key", Some("k\u{113}y"), 2),
        ("lie", Some("l\u{12b}e"), 2),
        ("play", Some("pl\u{101}y"), 2),
        ("queue", Some("q\u{16b}eue"), 2),
        ("see", Some("s\u{113}e"), 2),
        ("singe", Some("si\u{30a}nge"), 2),
        ("stop", Some("st\u{f2}p"), 2),
        ("study", Some("st\u{fb}d\u{1e8f}"), 2),
        ("tie", Some("t\u{12b}e"), 2),
        ("tinge", Some("ti\u{30a}nge"), 2),
        ("try", Some("tr\u{1e8f}"), 2),
        ("walk", Some("w\u{e0}lk"), 2),
        ("whale", Some("w\u{304}\u{1d559}\u{101}le"), 2),
        ("whim", Some("\u{1e98}\u{1d559}i\u{30a}m"), 2),
        ("yum", Some("\u{1e99}u\u{307}m"), 2),
    ];
    let records: Vec<_> = entries
        .iter()
        .map(|&(word, ips, state)| {
            let mut fields = [None; 7];
            fields[1] = ips;
            Record {
                word,
                fields,
                state,
            }
        })
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    let cases: &[(&str, &str, &str)] = &[
        (
            "inflection_projection_keeps_clusters_and_spelling-01",
            "studies studied studying STUDIES STuDiED StUdYiNg plays played playing PLAYED",
            "st\u{fb}dies st\u{fb}died st\u{fb}d\u{1e8f}ing ST\u{db}DIES ST\u{fb}DiED St\u{db}d\u{1e8e}iNg pl\u{101}ys pl\u{101}yed pl\u{101}ying PL\u{100}YED",
        ),
        (
            "inflection_projection_keeps_clusters_and_spelling-02",
            "stops stopped stopping STOPPED SToPpInG walks walked walking boxes BOXES",
            "st\u{f2}ps st\u{f2}pped st\u{f2}pping ST\u{d2}PPED ST\u{f2}PpInG w\u{e0}lks w\u{e0}lked w\u{e0}lking b\u{f2}xes B\u{d2}XES",
        ),
        (
            "inflection_projection_keeps_clusters_and_spelling-03",
            "ties tied tying dies died dying lies lied lying bakes baked baking BAKING",
            "t\u{12b}es t\u{12b}ed tying d\u{12b}es d\u{12b}ed dying l\u{12b}es l\u{12b}ed lying b\u{101}kes b\u{101}ked b\u{101}king B\u{100}KING",
        ),
        (
            "inflection_projection_keeps_clusters_and_spelling-04",
            "ageing aging singeing singing tingeing tinging queueing queuing",
            "\u{101}geing \u{101}ging si\u{30a}ngeing [singing] ti\u{30a}ngeing [tinging] q\u{16b}eueing q\u{16b}euing",
        ),
        (
            "inflection_projection_keeps_clusters_and_spelling-05",
            "whales WHALES WHiMs yums YUMS keys seeing dyeing hoeing cries cried crying flies tried trying goes",
            "w\u{304}\u{1d559}\u{101}les W\u{305}\u{210d}\u{100}LES W\u{30a}\u{210d}i\u{30a}Ms \u{1e99}u\u{307}ms Y\u{30a}U\u{307}MS k\u{113}ys s\u{113}eing d\u{1e8f}eing h\u{14d}eing cries cried cr\u{1e8f}ing flies tried tr\u{1e8f}ing g\u{14d}es",
        ),
        (
            "inflection_projection_keeps_clusters_and_spelling-06",
            "studys studyed stoped stoping bakeing singeing tinging queuing queueing",
            "[studys] [studyed] [stoped] [stoping] [bakeing] si\u{30a}ngeing [tinging] q\u{16b}euing q\u{16b}eueing",
        ),
    ];
    for &(identifier, text, expected) in cases {
        let actual = annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
    }
}
