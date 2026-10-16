//! Independently encoded states exercise the production text pipeline.

use super::{Record, encode, lexicon_fixture};
use crate::annotation::annotate_from;
use crate::data::AnnotationResources;

#[test]
fn direct_annotation_stops_at_first_existing_variant_and_keeps_all_other_bytes() {
    let entries = [
        ("Apple", None, 1), // Missing source still stops lowercase variant search.
        ("Broken", Some("wrong"), 2),
        ("Can't", Some("càn't"), 2),
        ("Can’t", None, 0), // Curly exact blocks the available straight spelling.
        ("May", Some("Māy"), 2),
        ("apple", Some("åpple"), 2),
        ("bad", Some("bādextra"), 2),
        ("blocked", None, 0),
        ("broken", Some("bròken"), 2),
        ("can't", Some("cãn't"), 2),
        ("empty", None, 0),
        ("first-rate", Some("fi̊rst-rāte"), 2),
        ("may", Some("mãy"), 2),
        ("whale", Some("w̄𝕙āle"), 2),
        ("whim", Some("ẘ𝕙i̊m"), 2),
        ("yum", Some("ẙu̇m"), 2),
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
    let annotate = |text| {
        annotate_from(text, 0, |has_tokens, threshold| {
            assert!(has_tokens);
            assert_eq!(threshold, 0);
            Ok(Some(AnnotationResources {
                lexicon: &lexicon,
                frequency: None,
            }))
        })
        .unwrap()
    };
    for (text, expected) in [
        ("Apple APPLE aPpLe May may", "[Apple] ÅPPLE åPpLe Māy mãy"),
        (
            "Broken BROKEN blocked empty bad BAD missing",
            "[Broken] BRÒKEN [blocked] [empty] [bad] [BAD] [missing]",
        ),
        ("Can't Can’t CAN’T can’t", "Càn't [Can’t] CÃN’T cãn’t"),
        ("first-rate FIRST-RATE", "fi̊rst-rāte FI̊RST-RĀTE"),
        ("WHALE WHIM YUM", "W̅ℍĀLE W̊ℍI̊M Y̊U̇M"),
        (
            "\r\n\tapple  😀 中文apple apple123 e\u{301} café\n  may!",
            "\r\n\tåpple  😀 中文apple apple123 e\u{301} café\n  mãy!",
        ),
        ("<apple> [may] &apple;", "<åpple> [mãy] &åpple;"),
    ] {
        assert_eq!(annotate(text), expected, "{text}");
    }
}
