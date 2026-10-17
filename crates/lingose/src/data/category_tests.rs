//! Independent wire fixtures exercised through the production category helpers.

use super::{Record, encode, lexicon_fixture};
use crate::{Error, category};

#[test]
fn category_queries_preserve_registry_order_empty_classes_and_exact_membership() {
    let words = [
        "Apple", "May", "apple", "may", "orphan", "zeta", "é", "\u{e000}", "😀",
    ];
    let records: Vec<_> = words
        .iter()
        .map(|word| Record {
            word,
            fields: [None; 7],
            state: 1,
        })
        .collect();
    // Lexicographic order, membership and stored business order are distinct.
    let lexicon = lexicon_fixture(encode(
        &records,
        &[
            ("Z", &[8, 7, 6]),
            ("CET4", &[5, 2, 4]),
            ("A", &[]),
            ("Case", &[1, 3]),
        ],
        &[],
    ));
    assert_eq!(
        category::labels_from(|| Ok(&lexicon)).unwrap(),
        ["Z", "CET4", "A", "Case"]
    );
    assert_eq!(
        category::list_from("CET4", || Ok(&lexicon)).unwrap(),
        ["zeta", "apple", "orphan"]
    );
    assert_eq!(
        category::list_from("Z", || Ok(&lexicon)).unwrap(),
        ["😀", "\u{e000}", "é"]
    );
    assert_eq!(
        category::list_from("A", || Ok(&lexicon)).unwrap(),
        Vec::<String>::new()
    );
    for (word, label, expected) in [
        ("apple", "CET4", true),
        ("Apple", "CET4", false),
        ("APPLE", "CET4", false),
        ("aPple", "CET4", false),
        ("May", "Case", true),
        ("May", "CET4", false),
        ("Zeta", "CET4", true),
        ("ZETA", "CET4", false),
        ("unknown", "CET4", false),
        ("apple", "A", false),
        ("😀", "Z", true),
    ] {
        assert_eq!(
            category::kind_from(word, label, || Ok(&lexicon)),
            Ok(expected),
            "{word}/{label}"
        );
    }
    // Both returned vectors and their strings belong to the caller.
    let mut labels = category::labels_from(|| Ok(&lexicon)).unwrap();
    labels[0].clear();
    labels.reverse();
    assert_eq!(
        category::labels_from(|| Ok(&lexicon)).unwrap(),
        ["Z", "CET4", "A", "Case"]
    );
    let mut members = category::list_from("CET4", || Ok(&lexicon)).unwrap();
    members[0].clear();
    members.pop();
    assert_eq!(
        category::list_from("CET4", || Ok(&lexicon)).unwrap(),
        ["zeta", "apple", "orphan"]
    );
    for label in ["", "cet4", "CET4 ", " Z", "Z\0", "COLLINS", "Band"] {
        assert!(matches!(
            category::kind_from("unknown", label, || Ok(&lexicon)),
            Err(Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ));
        assert!(matches!(
            category::list_from(label, || Ok(&lexicon)),
            Err(Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ));
    }
}

#[test]
fn category_queries_support_all_32_bits_and_a_zero_label_registry() {
    let records = [Record {
        word: "a",
        fields: [None; 7],
        state: 0,
    }];
    let labels: Vec<_> = (0..32).map(|index| format!("label{index}")).collect();
    let categories: Vec<_> = labels
        .iter()
        .map(|label| (label.as_str(), &[0][..]))
        .collect();
    let lexicon = lexicon_fixture(encode(&records, &categories, &[]));
    assert_eq!(category::labels_from(|| Ok(&lexicon)).unwrap(), labels);
    for label in &labels {
        assert_eq!(category::kind_from("A", label, || Ok(&lexicon)), Ok(true));
        assert_eq!(category::list_from(label, || Ok(&lexicon)).unwrap(), ["a"]);
    }
    assert!(category::kind_from("a", "label32", || Ok(&lexicon)).is_err());
    let lexicon = lexicon_fixture(encode(&records, &[], &[]));
    assert_eq!(
        category::labels_from(|| Ok(&lexicon)).unwrap(),
        Vec::<String>::new()
    );
    assert!(matches!(
        category::kind_from("a", "CET4", || Ok(&lexicon)),
        Err(Error::InvalidArgument {
            parameter: "label",
            ..
        })
    ));
    assert!(matches!(
        category::list_from("CET4", || Ok(&lexicon)),
        Err(Error::InvalidArgument {
            parameter: "label",
            ..
        })
    ));
}
