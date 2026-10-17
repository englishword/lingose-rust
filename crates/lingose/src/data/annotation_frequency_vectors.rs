//! Generated from the pinned installed Python oracle; do not edit by hand.
//! P0 fixture SHA-256: 6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1
//! Reference baseline SHA-256: 9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01
//! Installed annotation.py SHA-256: 76355b9a0d71882f8407640740865529744e8eb9c6400081a0f764188bd4cbfc
//! Oracle: CPython 3.12.4 / Unicode 15.0.0; source bytes 14266.
//! Canonical vector payload SHA-256: b810a6687b1f98cde9fc70fa4fee4dc69e6ec40d0d19118bf30c56ba8998f345

use super::{Record, encode, frequency_fixture, lexicon_fixture};
use crate::annotation::annotate_from;
use crate::data::AnnotationResources;

type WireCase<'a> = (&'a str, &'a str, i64, &'a str, bool);

#[test]
fn pinned_python_p0_complete_frequency_fixture() {
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
    let frequency = frequency_fixture(encode(
        &[],
        &[],
        &[
            ("a lot", 6),
            ("abandon", 2),
            ("abandoned", 2),
            ("messrs.", 4),
            ("p.m.", 5),
            ("tail", 5062),
            ("the", 1),
            ("unlisted", 3),
        ],
    ));
    let cases: &[WireCase<'_>] = &[
        (
            "fixture-0283",
            "Apple APPLE aPpLe May may",
            0,
            "[Apple] APPLE aPpLe M\u{101}y m\u{e3}y",
            true,
        ),
        (
            "fixture-0284",
            "the book THE apple The hour the university the",
            0,
            "\u{1e6b}he\u{30a} book \u{1e6a}H\u{112} apple \u{1e6a}he\u{30a} [hour] \u{1e6b}h\u{113} [university] \u{1e6b}he\u{30a}",
            true,
        ),
        (
            "fixture-0285",
            "the \"apple\" the (apple) the\napple the, apple the\n\napple",
            0,
            "\u{1e6b}h\u{113} \"apple\" \u{1e6b}h\u{113} (apple) \u{1e6b}h\u{113}\napple \u{1e6b}he\u{30a}, apple \u{1e6b}he\u{30a}\n\napple",
            true,
        ),
        (
            "fixture-0286",
            "WHALE WHIM YUM bad BAD",
            0,
            "W\u{305}\u{210d}\u{100}LE W\u{30a}\u{210d}I\u{30a}M Y\u{30a}U\u{307}M [bad] [BAD]",
            true,
        ),
        (
            "fixture-0287",
            "walks boxes baked baking studies studied stopped stopping plays tying",
            0,
            "[walks] b\u{f2}xes [baked] b\u{101}king st\u{fb}dies st\u{fb}died st\u{f2}pped st\u{f2}pping [plays] tying",
            true,
        ),
        (
            "fixture-0288",
            "ageing singeing queueing busing singing axes is",
            0,
            "\u{101}geing si\u{30a}ngeing q\u{16b}eueing b\u{fb}sing s\u{129}nging [axes] [is]",
            true,
        ),
        (
            "fixture-0289",
            "first-rate second-rate second-puldsm pending-compound empty",
            0,
            "fi\u{30a}rst-r\u{101}te seco\u{30a}nd-r\u{101}te seco\u{30a}nd-[puldsm] [pending-compound] [empty]",
            true,
        ),
        (
            "fixture-0290",
            "don't doesn't aren't I'm you're o'clock don\u{2019}t doesn\u{2019}t aren\u{2019}t I\u{2019}m you\u{2019}re o\u{2019}clock",
            0,
            "[don't] d\u{f4}\u{1d556}\u{1e61}n't \u{e0}r\u{1d556}n't I'm yo\u{16b}'re o\u{30a}'clock [don\u{2019}t] d\u{f4}\u{1d556}\u{1e61}n\u{2019}t \u{e0}r\u{1d556}n\u{2019}t I\u{2019}m yo\u{16b}\u{2019}re o\u{30a}\u{2019}clock",
            true,
        ),
        (
            "fixture-0291",
            "caf\u{e9} apple123 \u{4e2d}\u{6587}apple e\u{301} \u{4e2d}\u{6587} \u{1f600}",
            0,
            "caf\u{e9} apple123 \u{4e2d}\u{6587}apple e\u{301} \u{4e2d}\u{6587} \u{1f600}",
            false,
        ),
        ("fixture-0292", "unknownwordzz", 0, "[unknownwordzz]", true),
        (
            "fixture-0293",
            "Messrs. p.m. a lot a lottery unlisted tail abandoned",
            0,
            "[Messrs]. [p].[m]. [a] [lot] [a] [lottery] [unlisted] t\u{e3}il \u{e5}bando\u{30a}ned",
            true,
        ),
        (
            "fixture-0294",
            "walks plays baked don't is",
            0,
            "[walks] [plays] [baked] [don't] [is]",
            true,
        ),
        (
            "fixture-0295",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            0,
            "\u{1e6b}h\u{113} \u{e5}bando\u{30a}n \u{e5}bando\u{30a}ned [unlisted] [Messrs]. [p].[m]. [a] [lot] t\u{e3}il",
            true,
        ),
        (
            "fixture-0296",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            1,
            "the \u{e5}bando\u{30a}n \u{e5}bando\u{30a}ned [unlisted] [Messrs]. [p].[m]. [a] [lot] t\u{e3}il",
            true,
        ),
        (
            "fixture-0297",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            2,
            "the abandon abandoned [unlisted] [Messrs]. [p].[m]. [a] [lot] t\u{e3}il",
            true,
        ),
        (
            "fixture-0298",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            3,
            "the abandon abandoned unlisted [Messrs]. [p].[m]. [a] [lot] t\u{e3}il",
            true,
        ),
        (
            "fixture-0299",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            4,
            "the abandon abandoned unlisted Messrs. [p].[m]. [a] [lot] t\u{e3}il",
            true,
        ),
        (
            "fixture-0300",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            5,
            "the abandon abandoned unlisted Messrs. p.m. [a] [lot] t\u{e3}il",
            true,
        ),
        (
            "fixture-0301",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            6,
            "the abandon abandoned unlisted Messrs. p.m. a lot t\u{e3}il",
            true,
        ),
        (
            "fixture-0302",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            5061,
            "the abandon abandoned unlisted Messrs. p.m. a lot t\u{e3}il",
            true,
        ),
        (
            "fixture-0303",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            5062,
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            true,
        ),
        (
            "fixture-0304",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            5063,
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            true,
        ),
        (
            "fixture-0305",
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            9223372036854775807,
            "the abandon abandoned unlisted Messrs. p.m. a lot tail",
            true,
        ),
    ];
    for &(identifier, text, threshold, expected, expected_tokens) in cases {
        let mut loaded = false;
        let actual = annotate_from(text, threshold, |has_tokens, capped| {
            loaded = true;
            assert!(has_tokens);
            assert_eq!(capped, threshold.min(5062) as u32);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: if capped == 0 { None } else { Some(&frequency) },
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
        assert_eq!(loaded, expected_tokens, "{identifier}/resource-access");
    }
}

#[test]
fn pinned_python_frequency_precedes_saved_states_and_all_fallbacks() {
    let entries = [
        ("Apple", None, 0),
        ("apple", Some("\u{e5}pple"), 2),
        ("apple's", None, 0),
        ("aren't", Some("wrong"), 2),
        ("book", Some("b\u{f2}ok"), 2),
        ("ca", None, 0),
        ("can", Some("c\u{e3}n"), 2),
        ("doesn't", None, 1),
        ("don't", None, 0),
        ("first", Some("fi\u{30a}rst"), 2),
        ("first-rate", None, 0),
        ("i'm", None, 0),
        ("o'clock", None, 0),
        ("rate", Some("r\u{101}te"), 2),
        ("the", None, 0),
        ("walk", Some("w\u{e0}lk"), 2),
        ("walking", None, 1),
        ("walks", None, 0),
        ("wrong", Some("bad"), 2),
        ("you're", None, 0),
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
    let frequency = frequency_fixture(encode(
        &[],
        &[],
        &[
            ("apple", 2),
            ("apple's", 13),
            ("aren't", 6),
            ("ca", 14),
            ("doesn't", 5),
            ("don't", 4),
            ("first-rate", 10),
            ("i'm", 7),
            ("o'clock", 9),
            ("the", 1),
            ("walking", 12),
            ("walks", 11),
            ("wrong", 3),
            ("you're", 8),
        ],
    ));
    let cases: &[WireCase<'_>] = &[
        (
            "frequency_precedes_saved_states_and_all_fallbacks-001",
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            0,
            "[the] \u{e5}pple [THE] \u{c5}PPLE [The] \u{e5}pple [tHe] \u{e5}pple [Apple] \u{c5}PPLE [wrong] [WRONG]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-002",
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            1,
            "the \u{e5}pple THE \u{c5}PPLE The \u{e5}pple tHe \u{e5}pple [Apple] \u{c5}PPLE [wrong] [WRONG]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-003",
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            2,
            "the apple THE APPLE The apple tHe apple Apple APPLE [wrong] [WRONG]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-004",
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            4,
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-005",
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            7,
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-006",
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            10,
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-007",
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            14,
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-008",
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            5062,
            "the apple THE APPLE The apple tHe apple Apple APPLE wrong WRONG",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-009",
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            0,
            "[don't] [don\u{2019}t] [DON\u{2019}T] d\u{f4}\u{1d556}\u{1e61}n't d\u{f4}\u{1d556}\u{1e61}n\u{2019}t [aren't] [aren\u{2019}t] [I'm] [I\u{2019}m] [you're] [you\u{2019}re] [o'clock] [o\u{2019}clock]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-010",
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            1,
            "[don't] [don\u{2019}t] [DON\u{2019}T] d\u{f4}\u{1d556}\u{1e61}n't d\u{f4}\u{1d556}\u{1e61}n\u{2019}t [aren't] [aren\u{2019}t] [I'm] [I\u{2019}m] [you're] [you\u{2019}re] [o'clock] [o\u{2019}clock]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-011",
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            2,
            "[don't] [don\u{2019}t] [DON\u{2019}T] d\u{f4}\u{1d556}\u{1e61}n't d\u{f4}\u{1d556}\u{1e61}n\u{2019}t [aren't] [aren\u{2019}t] [I'm] [I\u{2019}m] [you're] [you\u{2019}re] [o'clock] [o\u{2019}clock]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-012",
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            4,
            "don't don\u{2019}t DON\u{2019}T d\u{f4}\u{1d556}\u{1e61}n't d\u{f4}\u{1d556}\u{1e61}n\u{2019}t [aren't] [aren\u{2019}t] [I'm] [I\u{2019}m] [you're] [you\u{2019}re] [o'clock] [o\u{2019}clock]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-013",
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            7,
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m [you're] [you\u{2019}re] [o'clock] [o\u{2019}clock]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-014",
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            10,
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-015",
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            14,
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-016",
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            5062,
            "don't don\u{2019}t DON\u{2019}T doesn't doesn\u{2019}t aren't aren\u{2019}t I'm I\u{2019}m you're you\u{2019}re o'clock o\u{2019}clock",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-017",
            "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
            0,
            "[first-rate] [FIRST-RATE] fi\u{30a}rst-b\u{f2}ok fi\u{30a}rst-r\u{101}te-\u{e5}pple [walks] W\u{c0}LKING w\u{e0}lking w\u{e0}lked",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-018",
            "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
            1,
            "[first-rate] [FIRST-RATE] fi\u{30a}rst-b\u{f2}ok fi\u{30a}rst-r\u{101}te-\u{e5}pple [walks] W\u{c0}LKING w\u{e0}lking w\u{e0}lked",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-019",
            "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
            2,
            "[first-rate] [FIRST-RATE] fi\u{30a}rst-b\u{f2}ok fi\u{30a}rst-r\u{101}te-apple [walks] W\u{c0}LKING w\u{e0}lking w\u{e0}lked",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-020",
            "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
            4,
            "[first-rate] [FIRST-RATE] fi\u{30a}rst-b\u{f2}ok fi\u{30a}rst-r\u{101}te-apple [walks] W\u{c0}LKING w\u{e0}lking w\u{e0}lked",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-021",
            "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
            7,
            "[first-rate] [FIRST-RATE] fi\u{30a}rst-b\u{f2}ok fi\u{30a}rst-r\u{101}te-apple [walks] W\u{c0}LKING w\u{e0}lking w\u{e0}lked",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-022",
            "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
            10,
            "first-rate FIRST-RATE fi\u{30a}rst-b\u{f2}ok fi\u{30a}rst-r\u{101}te-apple [walks] W\u{c0}LKING w\u{e0}lking w\u{e0}lked",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-023",
            "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
            14,
            "first-rate FIRST-RATE fi\u{30a}rst-b\u{f2}ok fi\u{30a}rst-r\u{101}te-apple walks WALKING walking w\u{e0}lked",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-024",
            "first-rate FIRST-RATE first-book first-rate-apple walks WALKING walking walked",
            5062,
            "first-rate FIRST-RATE fi\u{30a}rst-b\u{f2}ok fi\u{30a}rst-r\u{101}te-apple walks WALKING walking w\u{e0}lked",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-025",
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t a\u{2019}can\u{2019}t",
            0,
            "[apple's] [apple\u{2019}s] [APPLE\u{2019}S] c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T [ca\u{2019}can\u{2019}t] [a\u{2019}can\u{2019}t]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-026",
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t a\u{2019}can\u{2019}t",
            1,
            "[apple's] [apple\u{2019}s] [APPLE\u{2019}S] c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T [ca\u{2019}can\u{2019}t] [a\u{2019}can\u{2019}t]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-027",
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t a\u{2019}can\u{2019}t",
            2,
            "[apple's] [apple\u{2019}s] [APPLE\u{2019}S] c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T [ca\u{2019}can\u{2019}t] [a\u{2019}can\u{2019}t]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-028",
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t a\u{2019}can\u{2019}t",
            4,
            "[apple's] [apple\u{2019}s] [APPLE\u{2019}S] c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T [ca\u{2019}can\u{2019}t] [a\u{2019}can\u{2019}t]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-029",
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t a\u{2019}can\u{2019}t",
            7,
            "[apple's] [apple\u{2019}s] [APPLE\u{2019}S] c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T [ca\u{2019}can\u{2019}t] [a\u{2019}can\u{2019}t]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-030",
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t a\u{2019}can\u{2019}t",
            10,
            "[apple's] [apple\u{2019}s] [APPLE\u{2019}S] c\u{e3}n't c\u{e3}n\u{2019}t C\u{c3}N\u{2019}T [ca\u{2019}can\u{2019}t] [a\u{2019}can\u{2019}t]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-031",
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t a\u{2019}can\u{2019}t",
            14,
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t [a\u{2019}can\u{2019}t]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-032",
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t a\u{2019}can\u{2019}t",
            5062,
            "apple's apple\u{2019}s APPLE\u{2019}S can't can\u{2019}t CAN\u{2019}T ca\u{2019}can\u{2019}t [a\u{2019}can\u{2019}t]",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-033",
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            0,
            "[the]-\u{e5}pple \u{e5}pple-[the] \u{e5}pple [the\u{2019}s] \u{e5}pple [the\u{2019}s]-\u{e5}pple",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-034",
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            1,
            "the-\u{e5}pple \u{e5}pple-the \u{e5}pple the\u{2019}s \u{e5}pple the\u{2019}s-\u{e5}pple",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-035",
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            2,
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-036",
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            4,
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-037",
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            7,
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-038",
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            10,
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-039",
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            14,
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            true,
        ),
        (
            "frequency_precedes_saved_states_and_all_fallbacks-040",
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            5062,
            "the-apple apple-the apple the\u{2019}s apple the\u{2019}s-apple",
            true,
        ),
    ];
    for &(identifier, text, threshold, expected, expected_tokens) in cases {
        let mut loaded = false;
        let actual = annotate_from(text, threshold, |has_tokens, capped| {
            loaded = true;
            assert!(has_tokens);
            assert_eq!(capped, threshold.min(5062) as u32);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: if capped == 0 { None } else { Some(&frequency) },
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
        assert_eq!(loaded, expected_tokens, "{identifier}/resource-access");
    }
}

#[test]
fn pinned_python_frequency_uses_saved_inflection_keys_without_stem_expansion() {
    let entries = [
        ("apple", Some("\u{e5}pple"), 2),
        ("bake", Some("b\u{101}ke"), 2),
        ("box", Some("b\u{f2}x"), 2),
        ("bus", Some("b\u{fb}s"), 2),
        ("stop", Some("st\u{f2}p"), 2),
        ("study", Some("st\u{fb}d\u{1e8f}"), 2),
        ("the", Some("wrong"), 2),
        ("tie", Some("t\u{12b}e"), 2),
        ("walk", Some("w\u{e0}lk"), 2),
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
    let frequency = frequency_fixture(encode(
        &[],
        &[],
        &[
            ("baking", 6),
            ("boxes", 5),
            ("buses", 9),
            ("stopped", 7),
            ("studies", 4),
            ("study", 3),
            ("ties", 8),
            ("unknowned", 10),
            ("walk", 1),
            ("walked", 2),
        ],
    ));
    let cases: &[WireCase<'_>] = &[
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-001",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            0,
            "w\u{e0}lk w\u{e0}lks w\u{e0}lked w\u{e0}lking st\u{fb}d\u{1e8f} st\u{fb}dies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x b\u{f2}xes b\u{101}ke b\u{101}kes b\u{101}ked b\u{101}king st\u{f2}p st\u{f2}ps st\u{f2}pped st\u{f2}pping t\u{12b}e t\u{12b}es t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] W\u{c0}LK W\u{c0}LKS W\u{c0}LKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-002",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            1,
            "walk w\u{e0}lks w\u{e0}lked w\u{e0}lking st\u{fb}d\u{1e8f} st\u{fb}dies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x b\u{f2}xes b\u{101}ke b\u{101}kes b\u{101}ked b\u{101}king st\u{f2}p st\u{f2}ps st\u{f2}pped st\u{f2}pping t\u{12b}e t\u{12b}es t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS W\u{c0}LKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-003",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            2,
            "walk w\u{e0}lks walked w\u{e0}lking st\u{fb}d\u{1e8f} st\u{fb}dies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x b\u{f2}xes b\u{101}ke b\u{101}kes b\u{101}ked b\u{101}king st\u{f2}p st\u{f2}ps st\u{f2}pped st\u{f2}pping t\u{12b}e t\u{12b}es t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-004",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            3,
            "walk w\u{e0}lks walked w\u{e0}lking study st\u{fb}dies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x b\u{f2}xes b\u{101}ke b\u{101}kes b\u{101}ked b\u{101}king st\u{f2}p st\u{f2}ps st\u{f2}pped st\u{f2}pping t\u{12b}e t\u{12b}es t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-005",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            4,
            "walk w\u{e0}lks walked w\u{e0}lking study studies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x b\u{f2}xes b\u{101}ke b\u{101}kes b\u{101}ked b\u{101}king st\u{f2}p st\u{f2}ps st\u{f2}pped st\u{f2}pping t\u{12b}e t\u{12b}es t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-006",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            5,
            "walk w\u{e0}lks walked w\u{e0}lking study studies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x boxes b\u{101}ke b\u{101}kes b\u{101}ked b\u{101}king st\u{f2}p st\u{f2}ps st\u{f2}pped st\u{f2}pping t\u{12b}e t\u{12b}es t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-007",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            6,
            "walk w\u{e0}lks walked w\u{e0}lking study studies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x boxes b\u{101}ke b\u{101}kes b\u{101}ked baking st\u{f2}p st\u{f2}ps st\u{f2}pped st\u{f2}pping t\u{12b}e t\u{12b}es t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-008",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            7,
            "walk w\u{e0}lks walked w\u{e0}lking study studies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x boxes b\u{101}ke b\u{101}kes b\u{101}ked baking st\u{f2}p st\u{f2}ps stopped st\u{f2}pping t\u{12b}e t\u{12b}es t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-009",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            8,
            "walk w\u{e0}lks walked w\u{e0}lking study studies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x boxes b\u{101}ke b\u{101}kes b\u{101}ked baking st\u{f2}p st\u{f2}ps stopped st\u{f2}pping t\u{12b}e ties t\u{12b}ed tying b\u{fb}s b\u{fb}ses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-010",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            9,
            "walk w\u{e0}lks walked w\u{e0}lking study studies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x boxes b\u{101}ke b\u{101}kes b\u{101}ked baking st\u{f2}p st\u{f2}ps stopped st\u{f2}pping t\u{12b}e ties t\u{12b}ed tying b\u{fb}s buses b\u{fb}sing b\u{fb}ssing [unknowns] [unknowned] [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-011",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            10,
            "walk w\u{e0}lks walked w\u{e0}lking study studies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x boxes b\u{101}ke b\u{101}kes b\u{101}ked baking st\u{f2}p st\u{f2}ps stopped st\u{f2}pping t\u{12b}e ties t\u{12b}ed tying b\u{fb}s buses b\u{fb}sing b\u{fb}ssing [unknowns] unknowned [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
        (
            "frequency_uses_saved_inflection_keys_without_stem_expansion-012",
            "walk walks walked walking study studies studied studying box boxes bake bakes baked baking stop stops stopped stopping tie ties tied tying bus buses busing bussing unknowns unknowned unknowning WALK WALKS WALKED WALKING",
            5062,
            "walk w\u{e0}lks walked w\u{e0}lking study studies st\u{fb}died st\u{fb}d\u{1e8f}ing b\u{f2}x boxes b\u{101}ke b\u{101}kes b\u{101}ked baking st\u{f2}p st\u{f2}ps stopped st\u{f2}pping t\u{12b}e ties t\u{12b}ed tying b\u{fb}s buses b\u{fb}sing b\u{fb}ssing [unknowns] unknowned [unknowning] WALK W\u{c0}LKS WALKED W\u{c0}LKING",
            true,
        ),
    ];
    for &(identifier, text, threshold, expected, expected_tokens) in cases {
        let mut loaded = false;
        let actual = annotate_from(text, threshold, |has_tokens, capped| {
            loaded = true;
            assert!(has_tokens);
            assert_eq!(capped, threshold.min(5062) as u32);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: if capped == 0 { None } else { Some(&frequency) },
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
        assert_eq!(loaded, expected_tokens, "{identifier}/resource-access");
    }
}

#[test]
fn pinned_python_special_longest_consumption_membership_and_context() {
    let entries = [
        ("a", Some("\u{101}"), 2),
        ("apple", Some("\u{e5}pple"), 2),
        ("eight", Some("\u{113}ight"), 2),
        ("fifty", Some("fi\u{30a}ft\u{1e8f}"), 2),
        ("hundred", Some("h\u{fb}ndred"), 2),
        ("i", Some("\u{12b}"), 2),
        ("k", Some("k"), 2),
        ("lot", Some("l\u{f2}t"), 2),
        ("lottery", Some("l\u{f2}tter\u{1e8f}"), 2),
        ("one", Some("\u{f2}ne"), 2),
        ("s", Some("s"), 2),
        ("the", Some("wrong"), 2),
        ("wind", Some("wi\u{30a}nd"), 2),
        ("winded", Some("wi\u{30a}nded"), 2),
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
    let frequency = frequency_fixture(encode(
        &[],
        &[],
        &[
            (".i.", 1),
            ("9-1-1", 1),
            ("911", 1),
            ("a lot", 1),
            ("a lottery", 2),
            ("a.m.", 1),
            ("eight hundred", 1),
            ("hundred fifty", 1),
            ("i.i.", 1),
            ("k/k", 1),
            ("lottery apple", 1),
            ("one hundred", 1),
            ("one hundred fifty", 2),
            ("s.s.", 1),
            ("winded ; wind", 1),
        ],
    ));
    let cases: &[WireCase<'_>] = &[
        (
            "special_longest_consumption_membership_and_context-001",
            "a lot a lottery a lottery apple a lotterya lot one hundred fifty apple",
            0,
            "\u{101} l\u{f2}t \u{101} l\u{f2}tter\u{1e8f} \u{101} l\u{f2}tter\u{1e8f} \u{e5}pple \u{101} [lotterya] l\u{f2}t \u{f2}ne h\u{fb}ndred fi\u{30a}ft\u{1e8f} \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-002",
            "a lot a lottery a lottery apple a lotterya lot one hundred fifty apple",
            1,
            "a lot \u{101} l\u{f2}tter\u{1e8f} \u{101} l\u{f2}tter\u{1e8f} \u{e5}pple \u{101} [lotterya] l\u{f2}t one hundred fi\u{30a}ft\u{1e8f} \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-003",
            "a lot a lottery a lottery apple a lotterya lot one hundred fifty apple",
            2,
            "a lot a lottery a lottery \u{e5}pple \u{101} [lotterya] l\u{f2}t one hundred fifty \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-004",
            "a lot a lottery a lottery apple a lotterya lot one hundred fifty apple",
            5062,
            "a lot a lottery a lottery \u{e5}pple \u{101} [lotterya] l\u{f2}t one hundred fifty \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-005",
            "xa lot apple a lottery apple xa lottery apple one hundred fiftyeight",
            0,
            "[xa] l\u{f2}t \u{e5}pple \u{101} l\u{f2}tter\u{1e8f} \u{e5}pple [xa] l\u{f2}tter\u{1e8f} \u{e5}pple \u{f2}ne h\u{fb}ndred [fiftyeight]",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-006",
            "xa lot apple a lottery apple xa lottery apple one hundred fiftyeight",
            1,
            "[xa] l\u{f2}t \u{e5}pple \u{101} l\u{f2}tter\u{1e8f} \u{e5}pple [xa] l\u{f2}tter\u{1e8f} \u{e5}pple one hundred [fiftyeight]",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-007",
            "xa lot apple a lottery apple xa lottery apple one hundred fiftyeight",
            2,
            "[xa] l\u{f2}t \u{e5}pple a lottery \u{e5}pple [xa] l\u{f2}tter\u{1e8f} \u{e5}pple \u{f2}ne h\u{fb}ndred [fiftyeight]",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-008",
            "xa lot apple a lottery apple xa lottery apple one hundred fiftyeight",
            5062,
            "[xa] l\u{f2}t \u{e5}pple a lottery \u{e5}pple [xa] l\u{f2}tter\u{1e8f} \u{e5}pple \u{f2}ne h\u{fb}ndred [fiftyeight]",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-009",
            "i.i.i. \u{130}.i.i. \u{131}.i.i. i.\u{130}.i. i.\u{131}.i. S.S. \u{17f}.s. s.\u{17f}. K/K \u{212a}/k k/\u{212a} apple",
            0,
            "\u{12b}.\u{12b}.\u{12b}. \u{130}.\u{12b}.\u{12b}. \u{131}.\u{12b}.\u{12b}. \u{12b}.\u{130}.\u{12b}. \u{12b}.\u{131}.\u{12b}. S.S. \u{17f}.s. s.\u{17f}. K/K \u{212a}/k k/\u{212a} \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-010",
            "i.i.i. \u{130}.i.i. \u{131}.i.i. i.\u{130}.i. i.\u{131}.i. S.S. \u{17f}.s. s.\u{17f}. K/K \u{212a}/k k/\u{212a} apple",
            1,
            "\u{12b}.\u{12b}.\u{12b}. \u{130}.\u{12b}.\u{12b}. \u{131}.\u{12b}.\u{12b}. \u{12b}.\u{130}.\u{12b}. \u{12b}.\u{131}.\u{12b}. S.S. \u{17f}.s. s.\u{17f}. K/K \u{212a}/k k/\u{212a} \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-011",
            "i.i.i. \u{130}.i.i. \u{131}.i.i. i.\u{130}.i. i.\u{131}.i. S.S. \u{17f}.s. s.\u{17f}. K/K \u{212a}/k k/\u{212a} apple",
            2,
            "\u{12b}.\u{12b}.\u{12b}. \u{130}.\u{12b}.\u{12b}. \u{131}.\u{12b}.\u{12b}. \u{12b}.\u{130}.\u{12b}. \u{12b}.\u{131}.\u{12b}. S.S. \u{17f}.s. s.\u{17f}. K/K \u{212a}/k k/\u{212a} \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-012",
            "i.i.i. \u{130}.i.i. \u{131}.i.i. i.\u{130}.i. i.\u{131}.i. S.S. \u{17f}.s. s.\u{17f}. K/K \u{212a}/k k/\u{212a} apple",
            5062,
            "\u{12b}.\u{12b}.\u{12b}. \u{130}.\u{12b}.\u{12b}. \u{131}.\u{12b}.\u{12b}. \u{12b}.\u{130}.\u{12b}. \u{12b}.\u{131}.\u{12b}. S.S. \u{17f}.s. s.\u{17f}. K/K \u{212a}/k k/\u{212a} \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-013",
            "the eight hundred apple the a lot apple the a.m. apple the one hundred fifty apple",
            0,
            "\u{1e6b}h\u{113} \u{113}ight h\u{fb}ndred \u{e5}pple \u{1e6b}h\u{113} \u{101} l\u{f2}t \u{e5}pple \u{1e6b}h\u{113} \u{101}.[m]. \u{e5}pple \u{1e6b}h\u{113} \u{f2}ne h\u{fb}ndred fi\u{30a}ft\u{1e8f} \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-014",
            "the eight hundred apple the a lot apple the a.m. apple the one hundred fifty apple",
            1,
            "\u{1e6b}he\u{30a} eight hundred \u{e5}pple \u{1e6b}he\u{30a} a lot \u{e5}pple \u{1e6b}he\u{30a} a.m. \u{e5}pple \u{1e6b}he\u{30a} one hundred fi\u{30a}ft\u{1e8f} \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-015",
            "the eight hundred apple the a lot apple the a.m. apple the one hundred fifty apple",
            2,
            "\u{1e6b}he\u{30a} eight hundred \u{e5}pple \u{1e6b}he\u{30a} a lot \u{e5}pple \u{1e6b}he\u{30a} a.m. \u{e5}pple \u{1e6b}he\u{30a} one hundred fifty \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-016",
            "the eight hundred apple the a lot apple the a.m. apple the one hundred fifty apple",
            5062,
            "\u{1e6b}he\u{30a} eight hundred \u{e5}pple \u{1e6b}he\u{30a} a lot \u{e5}pple \u{1e6b}he\u{30a} a.m. \u{e5}pple \u{1e6b}he\u{30a} one hundred fifty \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-017",
            "the\neight hundred apple the\n\neight hundred apple the (eight hundred) apple",
            0,
            "\u{1e6b}h\u{113}\n\u{113}ight h\u{fb}ndred \u{e5}pple \u{1e6b}he\u{30a}\n\n\u{113}ight h\u{fb}ndred \u{e5}pple \u{1e6b}h\u{113} (\u{113}ight h\u{fb}ndred) \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-018",
            "the\neight hundred apple the\n\neight hundred apple the (eight hundred) apple",
            1,
            "\u{1e6b}he\u{30a}\neight hundred \u{e5}pple \u{1e6b}he\u{30a}\n\neight hundred \u{e5}pple \u{1e6b}he\u{30a} (eight hundred) \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-019",
            "the\neight hundred apple the\n\neight hundred apple the (eight hundred) apple",
            2,
            "\u{1e6b}he\u{30a}\neight hundred \u{e5}pple \u{1e6b}he\u{30a}\n\neight hundred \u{e5}pple \u{1e6b}he\u{30a} (eight hundred) \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-020",
            "the\neight hundred apple the\n\neight hundred apple the (eight hundred) apple",
            5062,
            "\u{1e6b}he\u{30a}\neight hundred \u{e5}pple \u{1e6b}he\u{30a}\n\neight hundred \u{e5}pple \u{1e6b}he\u{30a} (eight hundred) \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-021",
            "a lot\u{2019}a lot a lot-a lot a lot\u{301} a lot\u{4e2d}\u{6587} a lot1 a lot_apple",
            0,
            "\u{101} l\u{f2}t\u{2019}a l\u{f2}t \u{101} l\u{f2}t-\u{101} l\u{f2}t \u{101} lot\u{301} \u{101} lot\u{4e2d}\u{6587} \u{101} lot1 \u{101} l\u{f2}t_\u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-022",
            "a lot\u{2019}a lot a lot-a lot a lot\u{301} a lot\u{4e2d}\u{6587} a lot1 a lot_apple",
            1,
            "\u{101} l\u{f2}t\u{2019}a l\u{f2}t \u{101} l\u{f2}t-\u{101} l\u{f2}t \u{101} lot\u{301} \u{101} lot\u{4e2d}\u{6587} \u{101} lot1 a lot_\u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-023",
            "a lot\u{2019}a lot a lot-a lot a lot\u{301} a lot\u{4e2d}\u{6587} a lot1 a lot_apple",
            2,
            "\u{101} l\u{f2}t\u{2019}a l\u{f2}t \u{101} l\u{f2}t-\u{101} l\u{f2}t \u{101} lot\u{301} \u{101} lot\u{4e2d}\u{6587} \u{101} lot1 a lot_\u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-024",
            "a lot\u{2019}a lot a lot-a lot a lot\u{301} a lot\u{4e2d}\u{6587} a lot1 a lot_apple",
            5062,
            "\u{101} l\u{f2}t\u{2019}a l\u{f2}t \u{101} l\u{f2}t-\u{101} l\u{f2}t \u{101} lot\u{301} \u{101} lot\u{4e2d}\u{6587} \u{101} lot1 a lot_\u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-025",
            "winded ; wind winded; wind winded ; winded winded ; wind wind apple",
            0,
            "wi\u{30a}nded ; wi\u{30a}nd wi\u{30a}nded; wi\u{30a}nd wi\u{30a}nded ; wi\u{30a}nded wi\u{30a}nded ; wi\u{30a}nd wi\u{30a}nd \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-026",
            "winded ; wind winded; wind winded ; winded winded ; wind wind apple",
            1,
            "winded ; wind wi\u{30a}nded; wi\u{30a}nd wi\u{30a}nded ; wi\u{30a}nded winded ; wind wi\u{30a}nd \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-027",
            "winded ; wind winded; wind winded ; winded winded ; wind wind apple",
            2,
            "winded ; wind wi\u{30a}nded; wi\u{30a}nd wi\u{30a}nded ; wi\u{30a}nded winded ; wind wi\u{30a}nd \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-028",
            "winded ; wind winded; wind winded ; winded winded ; wind wind apple",
            5062,
            "winded ; wind wi\u{30a}nded; wi\u{30a}nd wi\u{30a}nded ; wi\u{30a}nded winded ; wind wi\u{30a}nd \u{e5}pple",
            true,
        ),
        (
            "special_longest_consumption_membership_and_context-029",
            "911 9-1-1 \u{4e2d}\u{6587} \u{1f600} e\u{301}",
            0,
            "911 9-1-1 \u{4e2d}\u{6587} \u{1f600} e\u{301}",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-030",
            "911 9-1-1 \u{4e2d}\u{6587} \u{1f600} e\u{301}",
            1,
            "911 9-1-1 \u{4e2d}\u{6587} \u{1f600} e\u{301}",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-031",
            "911 9-1-1 \u{4e2d}\u{6587} \u{1f600} e\u{301}",
            2,
            "911 9-1-1 \u{4e2d}\u{6587} \u{1f600} e\u{301}",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-032",
            "911 9-1-1 \u{4e2d}\u{6587} \u{1f600} e\u{301}",
            5062,
            "911 9-1-1 \u{4e2d}\u{6587} \u{1f600} e\u{301}",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-033",
            "",
            0,
            "",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-034",
            "",
            1,
            "",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-035",
            "",
            2,
            "",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-036",
            "",
            5062,
            "",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-037",
            "\t 911 9-1-1\n",
            0,
            "\t 911 9-1-1\n",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-038",
            "\t 911 9-1-1\n",
            1,
            "\t 911 9-1-1\n",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-039",
            "\t 911 9-1-1\n",
            2,
            "\t 911 9-1-1\n",
            false,
        ),
        (
            "special_longest_consumption_membership_and_context-040",
            "\t 911 9-1-1\n",
            5062,
            "\t 911 9-1-1\n",
            false,
        ),
    ];
    for &(identifier, text, threshold, expected, expected_tokens) in cases {
        let mut loaded = false;
        let actual = annotate_from(text, threshold, |has_tokens, capped| {
            loaded = true;
            assert!(has_tokens);
            assert_eq!(capped, threshold.min(5062) as u32);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: if capped == 0 { None } else { Some(&frequency) },
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
        assert_eq!(loaded, expected_tokens, "{identifier}/resource-access");
    }
}

#[test]
fn pinned_python_special_python_unicode_neighbor_boundaries() {
    let entries = [
        ("a", Some("\u{101}"), 2),
        ("apple", Some("\u{e5}pple"), 2),
        ("eight", Some("\u{113}ight"), 2),
        ("fifty", Some("fi\u{30a}ft\u{1e8f}"), 2),
        ("hundred", Some("h\u{fb}ndred"), 2),
        ("i", Some("\u{12b}"), 2),
        ("k", Some("k"), 2),
        ("lot", Some("l\u{f2}t"), 2),
        ("lottery", Some("l\u{f2}tter\u{1e8f}"), 2),
        ("one", Some("\u{f2}ne"), 2),
        ("s", Some("s"), 2),
        ("the", Some("wrong"), 2),
        ("wind", Some("wi\u{30a}nd"), 2),
        ("winded", Some("wi\u{30a}nded"), 2),
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
    let frequency = frequency_fixture(encode(&[], &[], &[("a lot", 1)]));
    let cases: &[WireCase<'_>] = &[
        (
            "special_python_unicode_neighbor_boundaries-001",
            "apple |  a lot | a lot  | the apple",
            0,
            "\u{e5}pple |  \u{101} l\u{f2}t | \u{101} l\u{f2}t  | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-002",
            "apple |  a lot | a lot  | the apple",
            1,
            "\u{e5}pple |  a lot | a lot  | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-003",
            "apple | !a lot | a lot! | the apple",
            0,
            "\u{e5}pple | !\u{101} l\u{f2}t | \u{101} l\u{f2}t! | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-004",
            "apple | !a lot | a lot! | the apple",
            1,
            "\u{e5}pple | !a lot | a lot! | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-005",
            "apple | $a lot | a lot$ | the apple",
            0,
            "\u{e5}pple | $\u{101} l\u{f2}t | \u{101} l\u{f2}t$ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-006",
            "apple | $a lot | a lot$ | the apple",
            1,
            "\u{e5}pple | $a lot | a lot$ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-007",
            "apple | (a lot | a lot( | the apple",
            0,
            "\u{e5}pple | (\u{101} l\u{f2}t | \u{101} l\u{f2}t( | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-008",
            "apple | (a lot | a lot( | the apple",
            1,
            "\u{e5}pple | (a lot | a lot( | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-009",
            "apple | )a lot | a lot) | the apple",
            0,
            "\u{e5}pple | )\u{101} l\u{f2}t | \u{101} l\u{f2}t) | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-010",
            "apple | )a lot | a lot) | the apple",
            1,
            "\u{e5}pple | )a lot | a lot) | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-011",
            "apple | +a lot | a lot+ | the apple",
            0,
            "\u{e5}pple | +\u{101} l\u{f2}t | \u{101} l\u{f2}t+ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-012",
            "apple | +a lot | a lot+ | the apple",
            1,
            "\u{e5}pple | +a lot | a lot+ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-013",
            "apple | -a lot | a lot- | the apple",
            0,
            "\u{e5}pple | -\u{101} l\u{f2}t | \u{101} l\u{f2}t- | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-014",
            "apple | -a lot | a lot- | the apple",
            1,
            "\u{e5}pple | -\u{101} l\u{f2}t | \u{101} l\u{f2}t- | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-015",
            "apple | 0a lot | a lot0 | the apple",
            0,
            "\u{e5}pple | 0a l\u{f2}t | \u{101} lot0 | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-016",
            "apple | 0a lot | a lot0 | the apple",
            1,
            "\u{e5}pple | 0a l\u{f2}t | \u{101} lot0 | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-017",
            "apple | Aa lot | a lotA | the apple",
            0,
            "\u{e5}pple | [Aa] l\u{f2}t | \u{101} [lotA] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-018",
            "apple | Aa lot | a lotA | the apple",
            1,
            "\u{e5}pple | [Aa] l\u{f2}t | \u{101} [lotA] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-019",
            "apple | ^a lot | a lot^ | the apple",
            0,
            "\u{e5}pple | ^\u{101} l\u{f2}t | \u{101} l\u{f2}t^ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-020",
            "apple | ^a lot | a lot^ | the apple",
            1,
            "\u{e5}pple | ^a lot | a lot^ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-021",
            "apple | _a lot | a lot_ | the apple",
            0,
            "\u{e5}pple | _\u{101} l\u{f2}t | \u{101} l\u{f2}t_ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-022",
            "apple | _a lot | a lot_ | the apple",
            1,
            "\u{e5}pple | _a lot | a lot_ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-023",
            "apple | aa lot | a lota | the apple",
            0,
            "\u{e5}pple | [aa] l\u{f2}t | \u{101} [lota] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-024",
            "apple | aa lot | a lota | the apple",
            1,
            "\u{e5}pple | [aa] l\u{f2}t | \u{101} [lota] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-025",
            "apple | \u{a6}a lot | a lot\u{a6} | the apple",
            0,
            "\u{e5}pple | \u{a6}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{a6} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-026",
            "apple | \u{a6}a lot | a lot\u{a6} | the apple",
            1,
            "\u{e5}pple | \u{a6}a lot | a lot\u{a6} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-027",
            "apple | \u{aa}a lot | a lot\u{aa} | the apple",
            0,
            "\u{e5}pple | \u{aa}a l\u{f2}t | \u{101} lot\u{aa} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-028",
            "apple | \u{aa}a lot | a lot\u{aa} | the apple",
            1,
            "\u{e5}pple | \u{aa}a l\u{f2}t | \u{101} lot\u{aa} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-029",
            "apple | \u{ab}a lot | a lot\u{ab} | the apple",
            0,
            "\u{e5}pple | \u{ab}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{ab} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-030",
            "apple | \u{ab}a lot | a lot\u{ab} | the apple",
            1,
            "\u{e5}pple | \u{ab}a lot | a lot\u{ab} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-031",
            "apple | \u{ad}a lot | a lot\u{ad} | the apple",
            0,
            "\u{e5}pple | \u{ad}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{ad} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-032",
            "apple | \u{ad}a lot | a lot\u{ad} | the apple",
            1,
            "\u{e5}pple | \u{ad}a lot | a lot\u{ad} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-033",
            "apple | \u{b2}a lot | a lot\u{b2} | the apple",
            0,
            "\u{e5}pple | \u{b2}a l\u{f2}t | \u{101} lot\u{b2} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-034",
            "apple | \u{b2}a lot | a lot\u{b2} | the apple",
            1,
            "\u{e5}pple | \u{b2}a l\u{f2}t | \u{101} lot\u{b2} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-035",
            "apple | \u{bb}a lot | a lot\u{bb} | the apple",
            0,
            "\u{e5}pple | \u{bb}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{bb} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-036",
            "apple | \u{bb}a lot | a lot\u{bb} | the apple",
            1,
            "\u{e5}pple | \u{bb}a lot | a lot\u{bb} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-037",
            "apple | \u{1c5}a lot | a lot\u{1c5} | the apple",
            0,
            "\u{e5}pple | \u{1c5}a l\u{f2}t | \u{101} lot\u{1c5} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-038",
            "apple | \u{1c5}a lot | a lot\u{1c5} | the apple",
            1,
            "\u{e5}pple | \u{1c5}a l\u{f2}t | \u{101} lot\u{1c5} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-039",
            "apple | \u{2b0}a lot | a lot\u{2b0} | the apple",
            0,
            "\u{e5}pple | \u{2b0}a l\u{f2}t | \u{101} lot\u{2b0} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-040",
            "apple | \u{2b0}a lot | a lot\u{2b0} | the apple",
            1,
            "\u{e5}pple | \u{2b0}a l\u{f2}t | \u{101} lot\u{2b0} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-041",
            "apple | \u{300}a lot | a lot\u{300} | the apple",
            0,
            "\u{e5}pple | \u{300}a l\u{f2}t | \u{101} lot\u{300} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-042",
            "apple | \u{300}a lot | a lot\u{300} | the apple",
            1,
            "\u{e5}pple | \u{300}a l\u{f2}t | \u{101} lot\u{300} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-043",
            "apple | \u{378}a lot | a lot\u{378} | the apple",
            0,
            "\u{e5}pple | \u{378}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{378} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-044",
            "apple | \u{378}a lot | a lot\u{378} | the apple",
            1,
            "\u{e5}pple | \u{378}a lot | a lot\u{378} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-045",
            "apple | \u{488}a lot | a lot\u{488} | the apple",
            0,
            "\u{e5}pple | \u{488}a l\u{f2}t | \u{101} lot\u{488} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-046",
            "apple | \u{488}a lot | a lot\u{488} | the apple",
            1,
            "\u{e5}pple | \u{488}a l\u{f2}t | \u{101} lot\u{488} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-047",
            "apple | \u{903}a lot | a lot\u{903} | the apple",
            0,
            "\u{e5}pple | \u{903}a l\u{f2}t | \u{101} lot\u{903} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-048",
            "apple | \u{903}a lot | a lot\u{903} | the apple",
            1,
            "\u{e5}pple | \u{903}a l\u{f2}t | \u{101} lot\u{903} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-049",
            "apple | \u{16ee}a lot | a lot\u{16ee} | the apple",
            0,
            "\u{e5}pple | \u{16ee}a l\u{f2}t | \u{101} lot\u{16ee} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-050",
            "apple | \u{16ee}a lot | a lot\u{16ee} | the apple",
            1,
            "\u{e5}pple | \u{16ee}a l\u{f2}t | \u{101} lot\u{16ee} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-051",
            "apple | \u{2028}a lot | a lot\u{2028} | the apple",
            0,
            "\u{e5}pple | \u{2028}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{2028} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-052",
            "apple | \u{2028}a lot | a lot\u{2028} | the apple",
            1,
            "\u{e5}pple | \u{2028}a lot | a lot\u{2028} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-053",
            "apple | \u{2029}a lot | a lot\u{2029} | the apple",
            0,
            "\u{e5}pple | \u{2029}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{2029} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-054",
            "apple | \u{2029}a lot | a lot\u{2029} | the apple",
            1,
            "\u{e5}pple | \u{2029}a lot | a lot\u{2029} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-055",
            "apple | \u{e000}a lot | a lot\u{e000} | the apple",
            0,
            "\u{e5}pple | \u{e000}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{e000} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-056",
            "apple | \u{e000}a lot | a lot\u{e000} | the apple",
            1,
            "\u{e5}pple | \u{e000}a lot | a lot\u{e000} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-057",
            "apple | za lot | a lotz | the apple",
            0,
            "\u{e5}pple | [za] l\u{f2}t | \u{101} [lotz] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-058",
            "apple | za lot | a lotz | the apple",
            1,
            "\u{e5}pple | [za] l\u{f2}t | \u{101} [lotz] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-059",
            "apple | Za lot | a lotZ | the apple",
            0,
            "\u{e5}pple | [Za] l\u{f2}t | \u{101} [lotZ] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-060",
            "apple | Za lot | a lotZ | the apple",
            1,
            "\u{e5}pple | [Za] l\u{f2}t | \u{101} [lotZ] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-061",
            "apple | 9a lot | a lot9 | the apple",
            0,
            "\u{e5}pple | 9a l\u{f2}t | \u{101} lot9 | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-062",
            "apple | 9a lot | a lot9 | the apple",
            1,
            "\u{e5}pple | 9a l\u{f2}t | \u{101} lot9 | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-063",
            "apple | 'a lot | a lot' | the apple",
            0,
            "\u{e5}pple | '\u{101} l\u{f2}t | \u{101} l\u{f2}t' | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-064",
            "apple | 'a lot | a lot' | the apple",
            1,
            "\u{e5}pple | '\u{101} l\u{f2}t | \u{101} l\u{f2}t' | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-065",
            "apple | \u{2019}a lot | a lot\u{2019} | the apple",
            0,
            "\u{e5}pple | \u{2019}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{2019} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-066",
            "apple | \u{2019}a lot | a lot\u{2019} | the apple",
            1,
            "\u{e5}pple | \u{2019}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{2019} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-067",
            "apple | .a lot | a lot. | the apple",
            0,
            "\u{e5}pple | .\u{101} l\u{f2}t | \u{101} l\u{f2}t. | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-068",
            "apple | .a lot | a lot. | the apple",
            1,
            "\u{e5}pple | .a lot | a lot. | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-069",
            "apple | ,a lot | a lot, | the apple",
            0,
            "\u{e5}pple | ,\u{101} l\u{f2}t | \u{101} l\u{f2}t, | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-070",
            "apple | ,a lot | a lot, | the apple",
            1,
            "\u{e5}pple | ,a lot | a lot, | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-071",
            "apple | ;a lot | a lot; | the apple",
            0,
            "\u{e5}pple | ;\u{101} l\u{f2}t | \u{101} l\u{f2}t; | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-072",
            "apple | ;a lot | a lot; | the apple",
            1,
            "\u{e5}pple | ;a lot | a lot; | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-073",
            "apple | :a lot | a lot: | the apple",
            0,
            "\u{e5}pple | :\u{101} l\u{f2}t | \u{101} l\u{f2}t: | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-074",
            "apple | :a lot | a lot: | the apple",
            1,
            "\u{e5}pple | :a lot | a lot: | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-075",
            "apple | ?a lot | a lot? | the apple",
            0,
            "\u{e5}pple | ?\u{101} l\u{f2}t | \u{101} l\u{f2}t? | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-076",
            "apple | ?a lot | a lot? | the apple",
            1,
            "\u{e5}pple | ?a lot | a lot? | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-077",
            "apple | [a lot | a lot[ | the apple",
            0,
            "\u{e5}pple | [\u{101} l\u{f2}t | \u{101} l\u{f2}t[ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-078",
            "apple | [a lot | a lot[ | the apple",
            1,
            "\u{e5}pple | [a lot | a lot[ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-079",
            "apple | ]a lot | a lot] | the apple",
            0,
            "\u{e5}pple | ]\u{101} l\u{f2}t | \u{101} l\u{f2}t] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-080",
            "apple | ]a lot | a lot] | the apple",
            1,
            "\u{e5}pple | ]a lot | a lot] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-081",
            "apple | {a lot | a lot{ | the apple",
            0,
            "\u{e5}pple | {\u{101} l\u{f2}t | \u{101} l\u{f2}t{ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-082",
            "apple | {a lot | a lot{ | the apple",
            1,
            "\u{e5}pple | {a lot | a lot{ | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-083",
            "apple | }a lot | a lot} | the apple",
            0,
            "\u{e5}pple | }\u{101} l\u{f2}t | \u{101} l\u{f2}t} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-084",
            "apple | }a lot | a lot} | the apple",
            1,
            "\u{e5}pple | }a lot | a lot} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-085",
            "apple | \u{e9}a lot | a lot\u{e9} | the apple",
            0,
            "\u{e5}pple | \u{e9}a l\u{f2}t | \u{101} lot\u{e9} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-086",
            "apple | \u{e9}a lot | a lot\u{e9} | the apple",
            1,
            "\u{e5}pple | \u{e9}a l\u{f2}t | \u{101} lot\u{e9} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-087",
            "apple | \u{4e2d}a lot | a lot\u{4e2d} | the apple",
            0,
            "\u{e5}pple | \u{4e2d}a l\u{f2}t | \u{101} lot\u{4e2d} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-088",
            "apple | \u{4e2d}a lot | a lot\u{4e2d} | the apple",
            1,
            "\u{e5}pple | \u{4e2d}a l\u{f2}t | \u{101} lot\u{4e2d} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-089",
            "apple | \u{bd}a lot | a lot\u{bd} | the apple",
            0,
            "\u{e5}pple | \u{bd}a l\u{f2}t | \u{101} lot\u{bd} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-090",
            "apple | \u{bd}a lot | a lot\u{bd} | the apple",
            1,
            "\u{e5}pple | \u{bd}a l\u{f2}t | \u{101} lot\u{bd} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-091",
            "apple | \u{2163}a lot | a lot\u{2163} | the apple",
            0,
            "\u{e5}pple | \u{2163}a l\u{f2}t | \u{101} lot\u{2163} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-092",
            "apple | \u{2163}a lot | a lot\u{2163} | the apple",
            1,
            "\u{e5}pple | \u{2163}a l\u{f2}t | \u{101} lot\u{2163} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-093",
            "apple | \u{1d552}a lot | a lot\u{1d552} | the apple",
            0,
            "\u{e5}pple | \u{1d552}a l\u{f2}t | \u{101} lot\u{1d552} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-094",
            "apple | \u{1d552}a lot | a lot\u{1d552} | the apple",
            1,
            "\u{e5}pple | \u{1d552}a l\u{f2}t | \u{101} lot\u{1d552} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-095",
            "apple | \u{17f}a lot | a lot\u{17f} | the apple",
            0,
            "\u{e5}pple | \u{17f}a l\u{f2}t | \u{101} lot\u{17f} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-096",
            "apple | \u{17f}a lot | a lot\u{17f} | the apple",
            1,
            "\u{e5}pple | \u{17f}a l\u{f2}t | \u{101} lot\u{17f} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-097",
            "apple | \u{130}a lot | a lot\u{130} | the apple",
            0,
            "\u{e5}pple | \u{130}a l\u{f2}t | \u{101} lot\u{130} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-098",
            "apple | \u{130}a lot | a lot\u{130} | the apple",
            1,
            "\u{e5}pple | \u{130}a l\u{f2}t | \u{101} lot\u{130} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-099",
            "apple | \u{131}a lot | a lot\u{131} | the apple",
            0,
            "\u{e5}pple | \u{131}a l\u{f2}t | \u{101} lot\u{131} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-100",
            "apple | \u{131}a lot | a lot\u{131} | the apple",
            1,
            "\u{e5}pple | \u{131}a l\u{f2}t | \u{101} lot\u{131} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-101",
            "apple | \u{212a}a lot | a lot\u{212a} | the apple",
            0,
            "\u{e5}pple | \u{212a}a l\u{f2}t | \u{101} lot\u{212a} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-102",
            "apple | \u{212a}a lot | a lot\u{212a} | the apple",
            1,
            "\u{e5}pple | \u{212a}a l\u{f2}t | \u{101} lot\u{212a} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-103",
            "apple | \u{301}a lot | a lot\u{301} | the apple",
            0,
            "\u{e5}pple | \u{301}a l\u{f2}t | \u{101} lot\u{301} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-104",
            "apple | \u{301}a lot | a lot\u{301} | the apple",
            1,
            "\u{e5}pple | \u{301}a l\u{f2}t | \u{101} lot\u{301} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-105",
            "apple | \u{20dd}a lot | a lot\u{20dd} | the apple",
            0,
            "\u{e5}pple | \u{20dd}a l\u{f2}t | \u{101} lot\u{20dd} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-106",
            "apple | \u{20dd}a lot | a lot\u{20dd} | the apple",
            1,
            "\u{e5}pple | \u{20dd}a l\u{f2}t | \u{101} lot\u{20dd} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-107",
            "apple | \u{1f600}a lot | a lot\u{1f600} | the apple",
            0,
            "\u{e5}pple | \u{1f600}\u{101} l\u{f2}t | \u{101} l\u{f2}t\u{1f600} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_python_unicode_neighbor_boundaries-108",
            "apple | \u{1f600}a lot | a lot\u{1f600} | the apple",
            1,
            "\u{e5}pple | \u{1f600}a lot | a lot\u{1f600} | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
    ];
    for &(identifier, text, threshold, expected, expected_tokens) in cases {
        let mut loaded = false;
        let actual = annotate_from(text, threshold, |has_tokens, capped| {
            loaded = true;
            assert!(has_tokens);
            assert_eq!(capped, threshold.min(5062) as u32);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: if capped == 0 { None } else { Some(&frequency) },
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
        assert_eq!(loaded, expected_tokens, "{identifier}/resource-access");
    }
}

#[test]
fn pinned_python_special_patterns_are_literal_escaped_ascii() {
    let entries = [
        ("a", Some("\u{101}"), 2),
        ("apple", Some("\u{e5}pple"), 2),
        ("eight", Some("\u{113}ight"), 2),
        ("fifty", Some("fi\u{30a}ft\u{1e8f}"), 2),
        ("hundred", Some("h\u{fb}ndred"), 2),
        ("i", Some("\u{12b}"), 2),
        ("k", Some("k"), 2),
        ("lot", Some("l\u{f2}t"), 2),
        ("lottery", Some("l\u{f2}tter\u{1e8f}"), 2),
        ("one", Some("\u{f2}ne"), 2),
        ("s", Some("s"), 2),
        ("the", Some("wrong"), 2),
        ("wind", Some("wi\u{30a}nd"), 2),
        ("winded", Some("wi\u{30a}nded"), 2),
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
    let frequency = frequency_fixture(encode(
        &[],
        &[],
        &[
            ("a\tb", 1),
            ("a\nb", 1),
            ("a b", 1),
            ("a$b", 1),
            ("a(b", 1),
            ("a)b", 1),
            ("a*b", 1),
            ("a+b", 1),
            ("a.b", 1),
            ("a/b", 1),
            ("a?b", 1),
            ("a[b", 1),
            ("a\\b", 1),
            ("a]b", 1),
            ("a^b", 1),
            ("a{b", 1),
            ("a|b", 1),
            ("a}b", 1),
        ],
    ));
    let cases: &[WireCase<'_>] = &[
        (
            "special_patterns_are_literal_escaped_ascii-001",
            "apple | a.b | a*b | a+b | a?b | a[b | a]b | a(b | a)b | a{b | a}b | a^b | a$b | a|b | a\\b | a/b | a b | a\tb | a\nb | axb | the apple",
            0,
            "\u{e5}pple | \u{101}.[b] | \u{101}*[b] | \u{101}+[b] | \u{101}?[b] | \u{101}[[b] | \u{101}][b] | \u{101}([b] | \u{101})[b] | \u{101}{[b] | \u{101}}[b] | \u{101}^[b] | \u{101}$[b] | \u{101}|[b] | \u{101}\\[b] | \u{101}/[b] | \u{101} [b] | \u{101}\t[b] | \u{101}\n[b] | [axb] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_patterns_are_literal_escaped_ascii-002",
            "apple | a.b | a*b | a+b | a?b | a[b | a]b | a(b | a)b | a{b | a}b | a^b | a$b | a|b | a\\b | a/b | a b | a\tb | a\nb | axb | the apple",
            1,
            "\u{e5}pple | a.b | a*b | a+b | a?b | a[b | a]b | a(b | a)b | a{b | a}b | a^b | a$b | a|b | a\\b | a/b | a b | a\tb | a\nb | [axb] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
        (
            "special_patterns_are_literal_escaped_ascii-003",
            "apple | a.b | a*b | a+b | a?b | a[b | a]b | a(b | a)b | a{b | a}b | a^b | a$b | a|b | a\\b | a/b | a b | a\tb | a\nb | axb | the apple",
            5062,
            "\u{e5}pple | a.b | a*b | a+b | a?b | a[b | a]b | a(b | a)b | a{b | a}b | a^b | a$b | a|b | a\\b | a/b | a b | a\tb | a\nb | [axb] | \u{1e6b}h\u{113} \u{e5}pple",
            true,
        ),
    ];
    for &(identifier, text, threshold, expected, expected_tokens) in cases {
        let mut loaded = false;
        let actual = annotate_from(text, threshold, |has_tokens, capped| {
            loaded = true;
            assert!(has_tokens);
            assert_eq!(capped, threshold.min(5062) as u32);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: if capped == 0 { None } else { Some(&frequency) },
            }))
        })
        .unwrap();
        assert_eq!(actual, expected, "{identifier}");
        assert_eq!(loaded, expected_tokens, "{identifier}/resource-access");
    }
}

#[test]
fn pinned_python_resource_fixture_outcomes_match() {
    // P0 resource-fixture-0307: a missing frequency resource is a named data error.
    let missing = annotate_from("apple", 1, |has_tokens, threshold| {
        assert!(has_tokens);
        assert_eq!(threshold, 1);
        Err(crate::Error::Data {
            resource: "frequency.bin.z",
            message: "missing fixture".into(),
        })
    });
    assert!(matches!(missing, Err(crate::Error::Data { .. })));
    // P0 resource-fixture-0308: zero threshold does not require frequency.
    let records = [Record {
        word: "apple",
        fields: [None, Some("apple"), None, None, None, None, None],
        state: 2,
    }];
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    assert_eq!(
        annotate_from("apple", 0, |_, threshold| {
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap(),
        "apple"
    );
    // P0 resource-fixture-0309: no English token returns before either resource.
    assert_eq!(
        annotate_from("\u{4e2d}\u{6587} 123 \u{1f600} e\u{301}", 1, |_, _| panic!(
            "no-token resource access"
        ))
        .unwrap(),
        "\u{4e2d}\u{6587} 123 \u{1f600} e\u{301}"
    );
}
