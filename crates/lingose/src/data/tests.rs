//! Independent v1 wire fixtures: no exporter or layout-probe code is reused.

use std::collections::{BTreeMap, BTreeSet};

use sha2::{Digest, Sha256};

use super::image::{AnnotationState, Counts, Expected, Field, Image, Kind};
use crate::{Error, data_meta};

const RESOURCE: &str = "fixture.bin";
const NULL: u32 = u32::MAX;
const HEADER: usize = 112;

struct Record<'a> {
    word: &'a str,
    fields: [Option<&'a str>; 7],
    state: u32,
}

struct Fixture {
    bytes: Vec<u8>,
    entries: usize,
    labels: usize,
    members: usize,
    frequency: usize,
    pool: usize,
}

fn push_u32(bytes: &mut Vec<u8>, value: usize) {
    bytes.extend_from_slice(&u32::try_from(value).unwrap().to_le_bytes());
}

fn u32_at(bytes: &[u8], at: usize) -> u32 {
    u32::from_le_bytes(bytes[at..at + 4].try_into().unwrap())
}

fn put_u32(bytes: &mut [u8], at: usize, value: u32) {
    bytes[at..at + 4].copy_from_slice(&value.to_le_bytes());
}

fn hex_bytes(value: &str) -> Vec<u8> {
    value
        .as_bytes()
        .chunks_exact(2)
        .map(|pair| u8::from_str_radix(std::str::from_utf8(pair).unwrap(), 16).unwrap())
        .collect()
}

fn encode(
    records: &[Record<'_>],
    categories: &[(&str, &[usize])],
    frequency: &[(&str, u32)],
) -> Fixture {
    let mut strings = BTreeSet::new();
    for record in records {
        strings.insert(record.word);
        strings.extend(record.fields.iter().flatten().copied());
    }
    strings.extend(categories.iter().map(|(label, _)| *label));
    strings.extend(frequency.iter().map(|(word, _)| *word));
    let ids: BTreeMap<_, _> = strings
        .iter()
        .enumerate()
        .map(|(id, value)| (*value, id))
        .collect();
    let member_count = categories.iter().map(|(_, members)| members.len()).sum();
    let pool_bytes = strings.iter().map(|value| value.len()).sum();
    let mut bytes = b"LNGIDX01".to_vec();
    for value in [
        data_meta::FORMAT_VERSION as usize,
        strings.len(),
        records.len(),
        categories.len(),
        member_count,
        frequency.len(),
        pool_bytes,
        data_meta::LEXICON_SCHEMA_VERSION as usize,
        data_meta::FREQUENCY_SCHEMA_VERSION as usize,
        data_meta::IPSM_ALGORITHM_VERSION as usize,
    ] {
        push_u32(&mut bytes, value);
    }
    bytes.extend(hex_bytes(data_meta::LEXICON_DATA_VERSION));
    bytes.extend(hex_bytes(data_meta::FREQUENCY_DATA_VERSION));
    assert_eq!(bytes.len(), HEADER);
    let mut offset = 0;
    push_u32(&mut bytes, offset);
    for value in &strings {
        offset += value.len();
        push_u32(&mut bytes, offset);
    }
    let entries = bytes.len();
    for (index, record) in records.iter().enumerate() {
        push_u32(&mut bytes, ids[record.word]);
        for field in record.fields {
            bytes.extend_from_slice(&field.map_or(NULL, |value| ids[value] as u32).to_le_bytes());
        }
        let mut bits = 0_u32;
        for (label, (_, members)) in categories.iter().enumerate() {
            if members.contains(&index) {
                bits |= 1_u32 << label;
            }
        }
        bytes.extend_from_slice(&bits.to_le_bytes());
        bytes.extend_from_slice(&record.state.to_le_bytes());
    }
    let labels = bytes.len();
    let mut next = 0;
    for (label, members) in categories {
        push_u32(&mut bytes, ids[label]);
        push_u32(&mut bytes, next);
        push_u32(&mut bytes, members.len());
        next += members.len();
    }
    let members = bytes.len();
    for (_, values) in categories {
        for value in *values {
            push_u32(&mut bytes, *value);
        }
    }
    let frequency_start = bytes.len();
    for (word, number) in frequency {
        push_u32(&mut bytes, ids[word]);
        bytes.extend_from_slice(&number.to_le_bytes());
    }
    let pool = bytes.len();
    for value in strings {
        bytes.extend_from_slice(value.as_bytes());
    }
    Fixture {
        bytes,
        entries,
        labels,
        members,
        frequency: frequency_start,
        pool,
    }
}

fn counts(bytes: &[u8]) -> Counts {
    Counts {
        strings: u32_at(bytes, 12) as usize,
        entries: u32_at(bytes, 16) as usize,
        labels: u32_at(bytes, 20) as usize,
        members: u32_at(bytes, 24) as usize,
        frequency_words: u32_at(bytes, 28) as usize,
        pool_bytes: u32_at(bytes, 32) as usize,
    }
}

fn parse(bytes: &[u8], kind: Kind) -> crate::Result<Image<'_>> {
    let digest = format!("{:x}", Sha256::digest(bytes));
    Image::parse(
        bytes,
        Expected {
            resource: RESOURCE,
            kind,
            sha256: &digest,
            bytes: bytes.len(),
            counts: counts(bytes),
        },
    )
}

fn assert_data(bytes: &[u8], kind: Kind) {
    assert!(
        matches!(
            parse(bytes, kind),
            Err(Error::Data {
                resource: RESOURCE,
                ..
            })
        ),
        "fixture must fail as a named data error"
    );
}

fn query_fixture(records: &[Record<'_>]) -> super::Lexicon {
    lexicon_fixture(encode(records, &[], &[]))
}

fn lexicon_fixture(fixture: Fixture) -> super::Lexicon {
    // Only test fixtures are leaked, to exercise the production static view.
    let bytes = Box::leak(fixture.bytes.into_boxed_slice());
    let image = parse(bytes, Kind::Lexicon).unwrap();
    let words = (0..image.counts().entries)
        .map(|index| (image.word(index), index))
        .collect();
    super::Lexicon { image, words }
}

fn frequency_fixture(fixture: Fixture) -> super::Frequency {
    let bytes = Box::leak(fixture.bytes.into_boxed_slice());
    super::Frequency::from_image(parse(bytes, Kind::Frequency).unwrap()).unwrap()
}

#[test]
fn frequency_matching_rejects_non_ascii_keys_without_corrupting_the_wire_parser() {
    let fixture = encode(&[], &[], &[("café", 1)]);
    let image = parse(Box::leak(fixture.bytes.into_boxed_slice()), Kind::Frequency).unwrap();
    assert!(matches!(
        super::Frequency::from_image(image),
        Err(Error::Data {
            resource: "frequency",
            ..
        })
    ));
}

#[path = "category_tests.rs"]
mod category_tests;

#[path = "annotation_tests.rs"]
mod annotation_tests;

#[path = "annotation_context_vectors.rs"]
mod annotation_context_vectors;

#[path = "annotation_frequency_vectors.rs"]
mod annotation_frequency_vectors;

#[path = "p41_query_fixture_tests.rs"]
mod p41_query_fixture_tests;

#[test]
fn simple_query_exact_entries_block_lowercase_even_with_unavailable_fields() {
    let lexicon = query_fixture(&[
        Record {
            word: "Apple",
            fields: [None; 7],
            state: 0,
        },
        Record {
            word: "May",
            fields: [Some("exact IPA"), None, None, None, None, None, None],
            state: 0,
        },
        Record {
            word: "apple",
            fields: [Some("lower"); 7],
            state: 2,
        },
        Record {
            word: "may",
            fields: [Some("lower"); 7],
            state: 2,
        },
    ]);
    for field in [
        Field::Ipa,
        Field::Ips,
        Field::Ism,
        Field::Ipsm,
        Field::RootLemma,
        Field::MeaningEn,
        Field::MeaningZh,
    ] {
        assert_eq!(
            crate::query::value_from("Apple", field, None, || Ok(&lexicon)),
            Ok(None)
        );
        assert_eq!(
            crate::query::value_from("APPLE", field, None, || Ok(&lexicon)),
            Ok(None)
        );
        assert_eq!(
            crate::query::value_from("aPple", field, None, || Ok(&lexicon)),
            Ok(None)
        );
        assert_eq!(
            crate::query::value_from("unknown", field, None, || Ok(&lexicon)),
            Ok(None)
        );
    }
    assert_eq!(
        crate::query::value_from("May", Field::Ipa, None, || Ok(&lexicon)),
        Ok(Some("exact IPA".into()))
    );
    assert_eq!(
        crate::query::value_from("May", Field::MeaningEn, Some("en"), || Ok(&lexicon)),
        Ok(None)
    );
    // A titlecase character later in the word is allowed and must be lowered.
    let lexicon = query_fixture(&[
        Record {
            word: "aǆ",
            fields: [Some("titlecase tail"); 7],
            state: 2,
        },
        Record {
            word: "i\u{307}",
            fields: [Some("expanded"); 7],
            state: 2,
        },
        Record {
            word: "σ",
            fields: [Some("sigma"); 7],
            state: 2,
        },
        Record {
            word: "ⅰ",
            fields: [Some("roman"); 7],
            state: 2,
        },
        Record {
            word: "𐐨",
            fields: [Some("non-BMP"); 7],
            state: 2,
        },
    ]);
    for (word, expected) in [
        ("Aǅ", "titlecase tail"),
        ("İ", "expanded"),
        ("Σ", "sigma"),
        ("Ⅰ", "roman"),
        ("𐐀", "non-BMP"),
    ] {
        assert_eq!(
            crate::query::value_from(word, Field::Ips, None, || Ok(&lexicon)),
            Ok(Some(expected.into()))
        );
    }
}

#[test]
fn simple_query_preserves_independent_projection_empty_text_and_original_bytes() {
    let lexicon = query_fixture(&[
        Record {
            word: "a",
            fields: [
                Some(""),
                None,
                Some(""),
                Some("independent IPSM"),
                Some("0"),
                Some("line one\nline two"),
                Some("e\u{301} é 中文"),
            ],
            state: 0,
        },
        Record {
            word: "stale",
            fields: [None, Some("stale"), Some("sta-le"), None, None, None, None],
            state: 2,
        },
    ]);
    for (field, expected) in [
        (Field::Ipa, Some("")),
        (Field::Ips, None),
        (Field::Ism, Some("")),
        (Field::Ipsm, Some("independent IPSM")),
        (Field::RootLemma, Some("0")),
        (Field::MeaningEn, Some("line one\nline two")),
        (Field::MeaningZh, Some("e\u{301} é 中文")),
    ] {
        assert_eq!(
            crate::query::value_from("A", field, None, || Ok(&lexicon)),
            Ok(expected.map(str::to_owned))
        );
    }
    assert_eq!(
        crate::query::value_from("stale", Field::Ipsm, None, || Ok(&lexicon)),
        Ok(None)
    );
}

fn sample() -> Fixture {
    encode(
        &[
            Record {
                word: "a",
                fields: [
                    Some(""),
                    None,
                    None,
                    Some("independent IPSM"),
                    Some("zero"),
                    Some("line one\nline two"),
                    Some("中文\u{301}"),
                ],
                state: 0,
            },
            Record {
                word: "b",
                fields: [None; 7],
                state: 1,
            },
            Record {
                word: "é",
                fields: [
                    Some("e"),
                    Some("e\u{301}"),
                    Some(""),
                    None,
                    None,
                    Some(""),
                    Some("中文"),
                ],
                state: 2,
            },
        ],
        &[("Z", &[2, 0]), ("A", &[1, 2])],
        &[],
    )
}

#[test]
fn fixture_preserves_null_empty_unicode_states_and_business_order() {
    let fixture = sample();
    let image = parse(&fixture.bytes, Kind::Lexicon).unwrap();
    assert_eq!(image.counts().entries, 3);
    assert_eq!(image.word(0), "a");
    assert_eq!(image.word(2), "é");
    assert_eq!(image.field(0, Field::Ipa), Some(""));
    assert_eq!(image.field(0, Field::Ips), None);
    assert_eq!(image.field(0, Field::Ism), None);
    assert_eq!(image.field(0, Field::Ipsm), Some("independent IPSM"));
    assert_eq!(image.field(0, Field::RootLemma), Some("zero"));
    assert_eq!(image.field(0, Field::MeaningEn), Some("line one\nline two"));
    assert_eq!(image.field(0, Field::MeaningZh), Some("中文\u{301}"));
    assert_eq!(image.field(2, Field::Ips), Some("e\u{301}"));
    assert_eq!(image.field(2, Field::Ism), Some(""));
    assert_eq!(image.field(2, Field::Ipsm), None);
    assert!(matches!(
        image.annotation_state(0),
        AnnotationState::Blocked
    ));
    assert!(matches!(
        image.annotation_state(1),
        AnnotationState::Fallback
    ));
    assert!(matches!(
        image.annotation_state(2),
        AnnotationState::Available
    ));
    assert_eq!(image.label(0), "Z");
    assert_eq!(image.label(1), "A");
    assert_eq!(image.members(0).collect::<Vec<_>>(), ["é", "a"]);
    assert_eq!(image.members(1).collect::<Vec<_>>(), ["b", "é"]);
    for (entry, memberships) in [[true, false], [false, true], [true, true]]
        .iter()
        .enumerate()
    {
        for (label, expected) in memberships.iter().enumerate() {
            assert_eq!(image.kind(entry, label), *expected);
        }
    }
    // Exposed string slices must borrow the fixture's pool, rather than clones.
    let pool = fixture.bytes.as_ptr() as usize + fixture.pool;
    let end = fixture.bytes.as_ptr() as usize + fixture.bytes.len();
    for value in [image.word(2), image.field(0, Field::MeaningZh).unwrap()] {
        let begin = value.as_ptr() as usize;
        assert!(begin >= pool && begin + value.len() <= end);
    }
}

#[test]
fn fixture_supports_all_32_category_bits_and_scalar_order() {
    let names: Vec<_> = (0..32).map(|id| format!("label{id}")).collect();
    let member = [0_usize];
    let categories: Vec<_> = names
        .iter()
        .map(|label| (label.as_str(), member.as_slice()))
        .collect();
    let fixture = encode(
        &[
            Record {
                word: "\u{e000}",
                fields: [None; 7],
                state: 1,
            },
            Record {
                word: "\u{10000}",
                fields: [None; 7],
                state: 0,
            },
        ],
        &categories,
        &[],
    );
    let image = parse(&fixture.bytes, Kind::Lexicon).unwrap();
    assert_eq!(image.word(0), "\u{e000}");
    assert_eq!(image.word(1), "\u{10000}");
    for (label, name) in names.iter().enumerate() {
        assert_eq!(image.label(label), name);
        assert!(image.kind(0, label));
        assert!(!image.kind(1, label));
        assert_eq!(image.members(label).collect::<Vec<_>>(), ["\u{e000}"]);
    }
}

#[test]
fn fixture_frequency_keeps_raw_number_gaps_phrases_and_punctuation() {
    let fixture = encode(
        &[],
        &[],
        &[("a", 1), ("can't", 7), ("two words", 5062), ("é", 17)],
    );
    let image = parse(&fixture.bytes, Kind::Frequency).unwrap();
    assert_eq!(image.counts().frequency_words, 4);
    for (index, expected) in [("a", 1), ("can't", 7), ("two words", 5062), ("é", 17)]
        .iter()
        .enumerate()
    {
        assert_eq!(image.frequency(index), *expected);
        assert_eq!(image.find_frequency(expected.0), Some(expected.1));
    }
    for missing in ["", "A", "can", "two", "zz"] {
        assert_eq!(image.find_frequency(missing), None);
    }
}

#[test]
fn pinned_identity_checks_length_hash_and_each_expected_count() {
    let fixture = sample();
    let digest = format!("{:x}", Sha256::digest(&fixture.bytes));
    let expected = Expected {
        resource: RESOURCE,
        kind: Kind::Lexicon,
        sha256: &digest,
        bytes: fixture.bytes.len(),
        counts: counts(&fixture.bytes),
    };
    assert!(Image::parse(&fixture.bytes, expected).is_ok());
    let mut changed = fixture.bytes.clone();
    changed[fixture.pool] ^= 1;
    assert!(matches!(
        Image::parse(&changed, expected),
        Err(Error::Data {
            resource: RESOURCE,
            ..
        })
    ));
    assert!(matches!(
        Image::parse(
            &fixture.bytes,
            Expected {
                bytes: expected.bytes + 1,
                ..expected
            }
        ),
        Err(Error::Data {
            resource: RESOURCE,
            ..
        })
    ));
    for index in 0..6 {
        let mut wrong = expected.counts;
        match index {
            0 => wrong.strings += 1,
            1 => wrong.entries += 1,
            2 => wrong.labels += 1,
            3 => wrong.members += 1,
            4 => wrong.frequency_words += 1,
            5 => wrong.pool_bytes += 1,
            _ => unreachable!(),
        }
        assert!(matches!(
            Image::parse(
                &fixture.bytes,
                Expected {
                    counts: wrong,
                    ..expected
                }
            ),
            Err(Error::Data {
                resource: RESOURCE,
                ..
            })
        ));
    }
}

#[test]
fn incompatible_versions_take_precedence_over_the_changed_hash() {
    let fixture = sample();
    let digest = format!("{:x}", Sha256::digest(&fixture.bytes));
    for position in [8, 36, 40, 44, 48, 80] {
        let mut bytes = fixture.bytes.clone();
        bytes[position] ^= 1;
        let error = Image::parse(
            &bytes,
            Expected {
                resource: RESOURCE,
                kind: Kind::Lexicon,
                sha256: &digest,
                bytes: bytes.len(),
                counts: counts(&bytes),
            },
        );
        assert!(matches!(
            error,
            Err(Error::IncompatibleDataVersion {
                resource: RESOURCE,
                ..
            })
        ));
    }
}

#[test]
fn rejects_bad_magic_extra_bytes_and_cross_resource_sections() {
    let mut lexicon = sample().bytes;
    lexicon[0] ^= 1;
    assert_data(&lexicon, Kind::Lexicon);
    lexicon[0] ^= 1;
    lexicon.push(0);
    assert_data(&lexicon, Kind::Lexicon);
    let lexicon = sample();
    assert_data(&lexicon.bytes, Kind::Frequency);
    let frequency = encode(&[], &[], &[("a", 1)]);
    assert_data(&frequency.bytes, Kind::Lexicon);
}

#[test]
fn rejects_invalid_pool_boundaries_utf8_and_string_order() {
    let fixture = encode(
        &[Record {
            word: "a",
            fields: [Some("b"), None, None, None, None, None, None],
            state: 1,
        }],
        &[],
        &[],
    );
    for (offset, value) in [(HEADER, 1), (HEADER + 4, 3), (HEADER + 8, 1)] {
        let mut bytes = fixture.bytes.clone();
        put_u32(&mut bytes, offset, value);
        assert_data(&bytes, Kind::Lexicon);
    }
    for pool in [b"aa".as_slice(), b"ba", &[0xff, b'b']] {
        let mut bytes = fixture.bytes.clone();
        bytes[fixture.pool..].copy_from_slice(pool);
        assert_data(&bytes, Kind::Lexicon);
    }
    let fixture = encode(
        &[Record {
            word: "é",
            fields: [Some("éa"), None, None, None, None, None, None],
            state: 1,
        }],
        &[],
        &[],
    );
    let mut bytes = fixture.bytes;
    // A valid whole-pool UTF-8 string still requires valid individual boundaries.
    put_u32(&mut bytes, HEADER + 4, 1);
    assert_data(&bytes, Kind::Lexicon);
}

#[test]
fn rejects_invalid_entry_references_spelling_order_and_annotation_states() {
    let fixture = sample();
    for (relative, value) in [
        (0, NULL),
        (4, u32_at(&fixture.bytes, 12)),
        (32, 4),
        (36, 3),
        (36, 2),
        (80 + 36, 0),
        (80 + 8, NULL),
    ] {
        let mut bytes = fixture.bytes.clone();
        put_u32(&mut bytes, fixture.entries + relative, value);
        assert_data(&bytes, Kind::Lexicon);
    }
    for word in ["", " leading", "trailing\u{a0}", "a\0b"] {
        let fixture = encode(
            &[Record {
                word,
                fields: [None; 7],
                state: 1,
            }],
            &[],
            &[],
        );
        assert_data(&fixture.bytes, Kind::Lexicon);
    }
    let empty_ips = encode(
        &[Record {
            word: "a",
            fields: [None, Some(""), None, None, None, None, None],
            state: 2,
        }],
        &[],
        &[],
    );
    assert_data(&empty_ips.bytes, Kind::Lexicon);
    for words in [["b", "a"], ["a", "a"]] {
        let records = words.map(|word| Record {
            word,
            fields: [None; 7],
            state: 1,
        });
        let fixture = encode(&records, &[], &[]);
        assert_data(&fixture.bytes, Kind::Lexicon);
    }
}

#[test]
fn rejects_label_range_member_and_bitmap_disagreement() {
    let fixture = sample();
    for (offset, value) in [
        (fixture.labels, NULL),
        (fixture.labels + 12, u32_at(&fixture.bytes, fixture.labels)),
        (fixture.labels + 4, 1),
        (fixture.labels + 8, 5),
        (fixture.labels + 12 + 4, 1),
        (fixture.labels + 12 + 8, 1),
        (fixture.members, 3),
        (fixture.members + 4, 2),
        (fixture.entries + 32, 0),
    ] {
        let mut bytes = fixture.bytes.clone();
        put_u32(&mut bytes, offset, value);
        assert_data(&bytes, Kind::Lexicon);
    }
    let fixture = encode(
        &[Record {
            word: "a",
            fields: [None; 7],
            state: 1,
        }],
        &[("", &[])],
        &[],
    );
    assert_data(&fixture.bytes, Kind::Lexicon);
}

#[test]
fn rejects_frequency_bad_keys_numbers_duplicates_and_order() {
    for word in ["", "A", "a\0b"] {
        let fixture = encode(&[], &[], &[(word, 1)]);
        assert_data(&fixture.bytes, Kind::Frequency);
    }
    for values in [
        vec![("a", 0)],
        vec![("a", 5063)],
        vec![("b", 1), ("a", 2)],
        vec![("a", 1), ("a", 2)],
    ] {
        let fixture = encode(&[], &[], &values);
        assert_data(&fixture.bytes, Kind::Frequency);
    }
    let fixture = encode(&[], &[], &[("a", 1)]);
    let mut bytes = fixture.bytes.clone();
    put_u32(&mut bytes, fixture.frequency, NULL);
    assert_data(&bytes, Kind::Frequency);
}

#[test]
fn every_truncation_and_huge_section_count_returns_error_without_panicking() {
    let fixture = sample();
    let digest = format!("{:x}", Sha256::digest(&fixture.bytes));
    let expected = Expected {
        resource: RESOURCE,
        kind: Kind::Lexicon,
        sha256: &digest,
        bytes: fixture.bytes.len(),
        counts: counts(&fixture.bytes),
    };
    for length in 0..fixture.bytes.len() {
        let result = std::panic::catch_unwind(|| Image::parse(&fixture.bytes[..length], expected));
        assert!(result.is_ok(), "panicked at truncated length {length}");
        assert!(matches!(
            result.unwrap(),
            Err(Error::Data {
                resource: RESOURCE,
                ..
            })
        ));
        if length >= HEADER {
            // Re-signing reaches the structural checks, instead of stopping at
            // the frozen byte count or hash as normal damaged resources do.
            let result =
                std::panic::catch_unwind(|| parse(&fixture.bytes[..length], Kind::Lexicon));
            assert!(result.is_ok(), "panicked for re-signed length {length}");
            assert!(matches!(
                result.unwrap(),
                Err(Error::Data {
                    resource: RESOURCE,
                    ..
                })
            ));
        }
    }
    for offset in [12, 16, 20, 24, 28, 32] {
        let mut bytes = fixture.bytes.clone();
        put_u32(&mut bytes, offset, u32::MAX);
        let result = std::panic::catch_unwind(|| parse(&bytes, Kind::Lexicon));
        assert!(result.is_ok(), "panicked for huge count at {offset}");
        assert!(matches!(
            result.unwrap(),
            Err(Error::Data {
                resource: RESOURCE,
                ..
            })
        ));
    }
}

#[test]
fn single_byte_mutations_never_panic_even_with_recomputed_identities() {
    for (fixture, kind) in [
        (sample(), Kind::Lexicon),
        (
            encode(&[], &[], &[("a", 1), ("can't", 5062)]),
            Kind::Frequency,
        ),
    ] {
        for offset in 0..fixture.bytes.len() {
            for replacement in [0, 0xff] {
                let mut bytes = fixture.bytes.clone();
                bytes[offset] = replacement;
                let result = std::panic::catch_unwind(|| parse(&bytes, kind));
                assert!(
                    result.is_ok(),
                    "panicked at byte {offset}, value {replacement}"
                );
            }
        }
    }
}
