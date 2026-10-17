//! Generated from frozen P0 snapshot category outputs; do not edit by hand.
//! Source SHA-256: 6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1

use std::fmt::Write as _;

use sha2::{Digest, Sha256};

// Match Python json.dumps(..., ensure_ascii=false, separators=(",", ":")):
// no BOM, trailing newline, whitespace, slash escaping, or normalization.
fn canonical_list(words: &[String]) -> String {
    let mut json = String::from("[");
    for (index, word) in words.iter().enumerate() {
        if index != 0 {
            json.push(',');
        }
        json.push('"');
        for character in word.chars() {
            match character {
                '"' => json.push_str("\\\""),
                '\\' => json.push_str("\\\\"),
                '\u{8}' => json.push_str("\\b"),
                '\u{c}' => json.push_str("\\f"),
                '\n' => json.push_str("\\n"),
                '\r' => json.push_str("\\r"),
                '\t' => json.push_str("\\t"),
                '\0'..='\u{1f}' => write!(&mut json, "\\u{:04x}", u32::from(character)).unwrap(),
                _ => json.push(character),
            }
        }
        json.push('"');
    }
    json.push(']');
    json
}

fn assert_complete_list(
    label: &str,
    actual: Vec<String>,
    length: usize,
    sha256: &str,
    head: &[&str],
    tail: &[&str],
) {
    assert_eq!(actual.len(), length, "{label} complete list length");
    assert_eq!(
        format!("{:x}", Sha256::digest(canonical_list(&actual).as_bytes())),
        sha256,
        "{label} complete ordered list digest"
    );
    assert_eq!(
        actual
            .iter()
            .take(head.len())
            .map(String::as_str)
            .collect::<Vec<_>>(),
        head,
        "{label} list head"
    );
    assert_eq!(
        actual
            .iter()
            .skip(actual.len() - tail.len())
            .map(String::as_str)
            .collect::<Vec<_>>(),
        tail,
        "{label} list tail"
    );
    for word in &actual {
        assert!(
            lingose::kind_with_label(word, label).unwrap(),
            "{word}/{label} list member"
        );
    }
}

#[test]
fn p0_snapshot_labels_match_python_configuration_order() {
    assert_eq!(
        lingose::labels().unwrap(),
        &[
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
        ]
    );
}

#[test]
fn p0_snapshot_membership_values_and_errors_match_python() {
    assert!(lingose::kind("apple").unwrap(), "snapshot-0007");
    assert!(!lingose::kind("running").unwrap(), "snapshot-0014");
    assert!(lingose::kind("Apple").unwrap(), "snapshot-0021");
    assert!(!lingose::kind("APPLE").unwrap(), "snapshot-0028");
    assert!(lingose::kind("May").unwrap(), "snapshot-0035");
    assert!(lingose::kind("may").unwrap(), "snapshot-0042");
    assert!(!lingose::kind("US").unwrap(), "snapshot-0049");
    assert!(lingose::kind("us").unwrap(), "snapshot-0056");
    assert!(!lingose::kind("iPhone").unwrap(), "snapshot-0063");
    assert!(!lingose::kind("McDonald").unwrap(), "snapshot-0070");
    assert!(lingose::kind("present").unwrap(), "snapshot-0077");
    assert!(lingose::kind("largely").unwrap(), "snapshot-0084");
    assert!(lingose::kind("Marxism").unwrap(), "snapshot-0091");
    assert!(!lingose::kind("has").unwrap(), "snapshot-0098");
    assert!(!lingose::kind("sh").unwrap(), "snapshot-0105");
    assert!(!lingose::kind("unknownwordzz").unwrap(), "snapshot-0112");
    assert!(
        matches!(
            lingose::kind(""),
            Err(lingose::Error::InvalidArgument {
                parameter: "word",
                ..
            })
        ),
        "snapshot-0191"
    );
    assert!(
        matches!(
            lingose::kind(" apple"),
            Err(lingose::Error::InvalidArgument {
                parameter: "word",
                ..
            })
        ),
        "snapshot-0192"
    );
    assert!(
        matches!(
            lingose::kind("apple "),
            Err(lingose::Error::InvalidArgument {
                parameter: "word",
                ..
            })
        ),
        "snapshot-0193"
    );
    assert!(
        matches!(
            lingose::kind("ap\0ple"),
            Err(lingose::Error::InvalidArgument {
                parameter: "word",
                ..
            })
        ),
        "snapshot-0194"
    );
    assert!(
        matches!(
            lingose::kind_with_label("unknownwordzz", "cet4"),
            Err(lingose::Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ),
        "snapshot-0200"
    );
    assert!(
        matches!(
            lingose::kind_with_label("unknownwordzz", "COLLINS"),
            Err(lingose::Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ),
        "snapshot-0202"
    );
    assert!(
        matches!(
            lingose::kind_with_label("unknownwordzz", "Band"),
            Err(lingose::Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ),
        "snapshot-0204"
    );
}

#[test]
fn p0_snapshot_complete_ordered_lists_match_python() {
    assert_complete_list(
        "CET4",
        lingose::kind_list().unwrap(),
        5225,
        "f8a57f8bb483f3c92fa0bcdde69cc9bb6cdf78555c81a4a5e5edbe209a3f22ac",
        &[
            "a", "able", "ability", "disable", "enable", "unable", "ache", "acid", "acre", "act",
        ],
        &[
            "roman",
            "saturday",
            "september",
            "soviet",
            "sunday",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
            "x-ray",
        ],
    );
    assert_complete_list(
        "OXFORD_3000",
        lingose::kind_list_with_label("OXFORD_3000").unwrap(),
        3447,
        "35d942dd25967ddcd79843a02dbe77634a3fd7c5cad26b5876ed1f213afc2eb1",
        &[
            "a",
            "able",
            "ability",
            "disabled",
            "enable",
            "inability",
            "unable",
            "acid",
            "act",
            "action",
        ],
        &[
            "monday",
            "november",
            "october",
            "saturday",
            "september",
            "sunday",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
        ],
    );
    assert_complete_list(
        "OXFORD_5000",
        lingose::kind_list_with_label("OXFORD_5000").unwrap(),
        5103,
        "c3e96d47b461f13e64d90c7dd76d38d03b04321bc19dc1d32e5e56cee82b4cab",
        &[
            "a",
            "able",
            "ability",
            "disabled",
            "disability",
            "enable",
            "inability",
            "unable",
            "acid",
            "acre",
        ],
        &[
            "monday",
            "november",
            "october",
            "saturday",
            "september",
            "sunday",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
        ],
    );
    assert_complete_list(
        "CET4",
        lingose::kind_list_with_label("CET4").unwrap(),
        5225,
        "f8a57f8bb483f3c92fa0bcdde69cc9bb6cdf78555c81a4a5e5edbe209a3f22ac",
        &[
            "a", "able", "ability", "disable", "enable", "unable", "ache", "acid", "acre", "act",
        ],
        &[
            "roman",
            "saturday",
            "september",
            "soviet",
            "sunday",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
            "x-ray",
        ],
    );
    assert_complete_list(
        "CET6",
        lingose::kind_list_with_label("CET6").unwrap(),
        7232,
        "7e06f3e800ad88f3c7493e32bc63456ac7bcdbe76fea0e69fa7e18dd1e9b4a1e",
        &[
            "a", "able", "ability", "disable", "enable", "unable", "ache", "acid", "acre", "act",
        ],
        &[
            "september",
            "soviet",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "venus",
            "wednesday",
            "x-ray",
        ],
    );
    assert_complete_list(
        "CET4_CET6",
        lingose::kind_list_with_label("CET4_CET6").unwrap(),
        7994,
        "6d0225a82b071fe8dc250dd793195d16c9336b460dd05cbf5beed30afb26ac8b",
        &[
            "a",
            "an",
            "able",
            "ability",
            "disable",
            "disabled",
            "disability",
            "enable",
            "ace",
            "ache",
        ],
        &[
            "october",
            "saturday",
            "september",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
            "x-ray",
        ],
    );
    assert_complete_list(
        "IELTS",
        lingose::kind_list_with_label("IELTS").unwrap(),
        5254,
        "52f08907969ffee2e403354bd515ab03e1acf0c051451983db1948782a47f5da",
        &[
            "ability",
            "disable",
            "enable",
            "exacerbate",
            "acid",
            "activate",
            "actual",
            "enact",
            "exact",
            "interact",
        ],
        &[
            "beyond",
            "zeal",
            "zest",
            "zone",
            "zoology",
            "zoological",
            "enzyme",
            "catholic",
            "christian",
            "mercury",
        ],
    );
    assert_complete_list(
        "TEM-4",
        lingose::kind_list_with_label("TEM-4").unwrap(),
        8795,
        "2961f180e34e723b527e57e2ebe3e8b7159e2c4a2e0147422e676153a4053035",
        &[
            "Jew",
            "an",
            "able",
            "ability",
            "disable",
            "disability",
            "enable",
            "inability",
            "unable",
            "ace",
        ],
        &[
            "september",
            "soviet",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "venus",
            "wednesday",
            "x-ray",
        ],
    );
    assert_complete_list(
        "TEM-8",
        lingose::kind_list_with_label("TEM-8").unwrap(),
        12952,
        "5c70d6ea44a6ee778285fb330e2a42dc5b6e9458e14d79f87ae144dddd417e4d",
        &[
            "Jew",
            "Maori",
            "a",
            "an",
            "abbot",
            "able",
            "ability",
            "ably",
            "disable",
            "disability",
        ],
        &[
            "september",
            "soviet",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "venus",
            "wednesday",
            "x-ray",
        ],
    );
    assert_complete_list(
        "TOEFL",
        lingose::kind_list_with_label("TOEFL").unwrap(),
        11246,
        "112de3d1baf20b9cefa0e0d745d3e91424788f1540912e607751cbd2ed416081",
        &[
            "Holland", "Illinois", "Iraq", "Iroquois", "Jewett", "Jules", "Kenya", "London",
            "Lowa", "Maine",
        ],
        &[
            "miss",
            "november",
            "october",
            "roman",
            "saturday",
            "saturn",
            "september",
            "soviet",
            "venus",
            "x-ray",
        ],
    );
    assert_complete_list(
        "SAT",
        lingose::kind_list_with_label("SAT").unwrap(),
        4437,
        "9d4ae8dd150f4d05a5a6755e0d13571a8e2bbf8819083b7bef37bdd96895af56",
        &[
            "abbess",
            "abyss",
            "acerbity",
            "exacerbate",
            "acid",
            "acidify",
            "acme",
            "acne",
            "acoustics",
            "acreage",
        ],
        &[
            "zeal", "zealot", "zealous", "zenith", "zephyr", "zero", "zest", "enzyme", "august",
            "x-ray",
        ],
    );
    assert_complete_list(
        "GMAT",
        lingose::kind_list_with_label("GMAT").unwrap(),
        3300,
        "39ee4a893dfac8e834c2d9458b369bbd25e955a624b2a69e5b90a9cfa5a56f4a",
        &[
            "Kelvin",
            "disability",
            "inability",
            "exacerbate",
            "acidity",
            "acreage",
            "activate",
            "activism",
            "activist",
            "enact",
        ],
        &[
            "underwrite",
            "underwriter",
            "yard",
            "yeast",
            "yen",
            "yield",
            "nonzero",
            "paleozoologist",
            "enzyme",
            "catholic",
        ],
    );
    assert_complete_list(
        "GRE",
        lingose::kind_list_with_label("GRE").unwrap(),
        10952,
        "fe92be3fcd690724a811f0be7c13449228e6533ae666902dc188764ba72a84a6",
        &[
            "abyss",
            "abysmal",
            "acedia",
            "acerbity",
            "exacerbate",
            "coacervate",
            "acidic",
            "acidulous",
            "acme",
            "acne",
        ],
        &[
            "zone",
            "protozoan",
            "zoom",
            "zoster",
            "zygote",
            "enzyme",
            "august",
            "bible",
            "catholic",
            "n",
        ],
    );
    assert_complete_list(
        "BEC",
        lingose::kind_list_with_label("BEC").unwrap(),
        2814,
        "04db25696ee5534bb98d1315f61829641c2a9cc6644a1206c431220a79c8eb69",
        &[
            "able", "ability", "enable", "act", "acting", "action", "actual", "activity",
            "actually", "actuals",
        ],
        &[
            "wreckage",
            "wrestle",
            "writ",
            "write-off",
            "copywriter",
            "yearly",
            "yen",
            "yield",
            "zero",
            "false",
        ],
    );
    assert_complete_list(
        "Primary",
        lingose::kind_list_with_label("Primary").unwrap(),
        847,
        "0738df41a099c956f5213fbb14a6669adaa1671e95a78c78d4ddb5a9acf4e953",
        &[
            "London",
            "a",
            "an",
            "active",
            "after",
            "afternoon",
            "Alaska",
            "all",
            "also",
            "a.m.",
        ],
        &[
            "november",
            "october",
            "saturday",
            "september",
            "sunday",
            "thanksgiving",
            "thursday",
            "tuesday",
            "wednesday",
            "has",
        ],
    );
    assert_complete_list(
        "Junior",
        lingose::kind_list_with_label("Junior").unwrap(),
        2876,
        "db44dca9349da7d60a24ee524a705d3a777420419bc0a46daeb8a22b751e5bb1",
        &[
            "Jason", "Jerry", "Jessica", "Jew", "Julie", "Katie", "Kevin", "Lausanne", "London",
            "Luke",
        ],
        &[
            "saturday",
            "september",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
            "x-ray",
            "has",
        ],
    );
    assert_complete_list(
        "Senior",
        lingose::kind_list_with_label("Senior").unwrap(),
        4334,
        "eceaf80ad9a762cb6fa94e6c48ab2af04c4a09c4a21359e531802ab72277739d",
        &[
            "Jason", "Jerry", "Jessica", "Jew", "Julie", "Katie", "Kevin", "Lausanne", "London",
            "Luke",
        ],
        &[
            "saturday",
            "september",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
            "x-ray",
            "has",
        ],
    );
    assert_complete_list(
        "College",
        lingose::kind_list_with_label("College").unwrap(),
        7874,
        "924e92a4b0062f9048001a1e0c2736e127c2f994794d9f15ac9276e0a638ac88",
        &[
            "Hippomenes",
            "Hobart",
            "Horace",
            "Houston",
            "Ithaca",
            "Jamie",
            "Janice",
            "Janson",
            "Jason",
            "Jem",
        ],
        &[
            "september",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "venus",
            "wednesday",
            "x-ray",
            "has",
        ],
    );
    assert_complete_list(
        "COCA_20000",
        lingose::kind_list_with_label("COCA_20000").unwrap(),
        16840,
        "6099fb8e3cbac8e3ed8a983fb0fed9dcbbdc6077dae8b59659f6c0ccf84838cc",
        &[
            "Jew",
            "a",
            "able",
            "ability",
            "disable",
            "disabled",
            "disability",
            "enable",
            "inability",
            "unable",
        ],
        &[
            "mercury",
            "miss",
            "mister",
            "negro",
            "roman",
            "soviet",
            "thanksgiving",
            "true",
            "x-ray",
            "sh",
        ],
    );
    assert_complete_list(
        "White",
        lingose::kind_list_with_label("White").unwrap(),
        847,
        "0738df41a099c956f5213fbb14a6669adaa1671e95a78c78d4ddb5a9acf4e953",
        &[
            "London",
            "a",
            "an",
            "active",
            "after",
            "afternoon",
            "Alaska",
            "all",
            "also",
            "a.m.",
        ],
        &[
            "november",
            "october",
            "saturday",
            "september",
            "sunday",
            "thanksgiving",
            "thursday",
            "tuesday",
            "wednesday",
            "has",
        ],
    );
    assert_complete_list(
        "Yellow",
        lingose::kind_list_with_label("Yellow").unwrap(),
        2876,
        "db44dca9349da7d60a24ee524a705d3a777420419bc0a46daeb8a22b751e5bb1",
        &[
            "Jason", "Jerry", "Jessica", "Jew", "Julie", "Katie", "Kevin", "Lausanne", "London",
            "Luke",
        ],
        &[
            "saturday",
            "september",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
            "x-ray",
            "has",
        ],
    );
    assert_complete_list(
        "Green",
        lingose::kind_list_with_label("Green").unwrap(),
        6473,
        "ef2f9d3f16debfaee444ea02b4ce0b6ad30115e4c05153b63d76334cfb5750f3",
        &[
            "Jason", "Jerry", "Jessica", "Jew", "Julie", "Katie", "Kevin", "Lausanne", "London",
            "Luke",
        ],
        &[
            "september",
            "soviet",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "wednesday",
            "x-ray",
            "has",
        ],
    );
    assert_complete_list(
        "Blue",
        lingose::kind_list_with_label("Blue").unwrap(),
        9622,
        "cddd540ab95ebe6a9540d161443885af99d4cf9852ec00a945ecc3353c69f780",
        &[
            "Hippomenes",
            "Hobart",
            "Horace",
            "Houston",
            "Ithaca",
            "Jamie",
            "Janice",
            "Janson",
            "Jason",
            "Jem",
        ],
        &[
            "soviet",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "venus",
            "wednesday",
            "x-ray",
            "has",
        ],
    );
    assert_complete_list(
        "Red",
        lingose::kind_list_with_label("Red").unwrap(),
        22999,
        "e1371927e9d4cd37014d7da579a63f25c7ec00a09377022419d69e6a0172b390",
        &[
            "Hippomenes",
            "Hobart",
            "Holland",
            "Horace",
            "Houston",
            "Illinois",
            "Iraq",
            "Iroquois",
            "Ithaca",
            "Jamie",
        ],
        &[
            "soviet",
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "venus",
            "wednesday",
            "x-ray",
            "has",
        ],
    );
    assert_complete_list(
        "Black",
        lingose::kind_list_with_label("Black").unwrap(),
        45420,
        "a93f5496b2d8b333dc11a71909c024f20ab2e47dac7b4c0f947df9ec6c0ccba3",
        &[
            "Hippomenes",
            "Hobart",
            "Holland",
            "Horace",
            "Houston",
            "Illinois",
            "Iraq",
            "Iroquois",
            "Ithaca",
            "Jamie",
        ],
        &[
            "sunday",
            "thanksgiving",
            "thursday",
            "true",
            "tuesday",
            "venus",
            "wednesday",
            "x-ray",
            "has",
            "sh",
        ],
    );
}

#[test]
fn p0_snapshot_invalid_list_labels_match_python() {
    assert!(
        matches!(
            lingose::kind_list_with_label("cet4"),
            Err(lingose::Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ),
        "snapshot-0201"
    );
    assert!(
        matches!(
            lingose::kind_list_with_label("COLLINS"),
            Err(lingose::Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ),
        "snapshot-0203"
    );
    assert!(
        matches!(
            lingose::kind_list_with_label("Band"),
            Err(lingose::Error::InvalidArgument {
                parameter: "label",
                ..
            })
        ),
        "snapshot-0205"
    );
}

#[test]
fn canonical_list_serializer_matches_independent_python_json_fixtures() {
    assert_eq!(canonical_list(&[]), "[]");
    assert_eq!(canonical_list(&[String::from("")]), "[\"\"]");
    assert_eq!(
        canonical_list(&[
            String::from("\"\\/\u{8}\u{c}\n\r\t\0\u{1}\u{b}\u{1f}"),
            String::from("\u{7f}\u{85}\u{2028}\u{2029} \u{e9} e\u{301} \u{1f600}")
        ]),
        "[\"\\\"\\\\/\\b\\f\\n\\r\\t\\u0000\\u0001\\u000b\\u001f\",\"\u{7f}\u{85}\u{2028}\u{2029} \u{e9} e\u{301} \u{1f600}\"]"
    );
}
