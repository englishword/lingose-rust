//! Loader-only acceptance, not public API or full annotation acceptance.

use std::hint::black_box;
use std::sync::atomic::Ordering;
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::Instant;

use sha2::{Digest, Sha256};

use super::image::{AnnotationState, Field};
use super::*;
use crate::Error;

fn attempts(resources: &Resources) -> (usize, usize) {
    (
        resources.lexicon_attempts.load(Ordering::SeqCst),
        resources.frequency_attempts.load(Ordering::SeqCst),
    )
}

#[test]
fn annotation_uses_real_scanner_before_resources_and_propagates_errors() {
    let resources = Resources::new(&[], &[]);
    let annotate = |text, threshold| {
        crate::annotation::annotate_from(text, threshold, |tokens, skip| {
            resources.for_annotation(tokens, skip)
        })
    };
    for text in [
        "",
        "中文 123 😀 e\u{301}",
        "中文apple",
        "apple123",
        "\u{903}apple",
        "a\u{20dd}",
        "a-中文",
    ] {
        for threshold in [0, 1, 5062, i64::MAX] {
            assert_eq!(annotate(text, threshold).unwrap(), text);
        }
    }
    assert_eq!(attempts(&resources), (0, 0));
    assert!(matches!(
        annotate("apple\0", -1),
        Err(Error::InvalidArgument {
            parameter: "skip_top",
            ..
        })
    ));
    assert!(matches!(
        annotate("apple\0", 0),
        Err(Error::InvalidArgument {
            parameter: "text",
            ..
        })
    ));
    assert_eq!(attempts(&resources), (0, 0));
    let first = annotate("apple", 0).unwrap_err();
    assert!(matches!(
        first,
        Error::Data {
            resource: "lexicon",
            ..
        }
    ));
    assert_eq!(annotate("unknownwordzz", 0).unwrap_err(), first);
    assert_eq!(attempts(&resources), (1, 0));
    let mut incompatible = LEXICON_BYTES.to_vec();
    incompatible[8..12].copy_from_slice(&999_u32.to_le_bytes());
    let resources = Resources::new(Box::leak(incompatible.into_boxed_slice()), &[]);
    assert!(matches!(
        crate::annotation::annotate_from("apple", 0, |tokens, skip| resources
            .for_annotation(tokens, skip)),
        Err(Error::IncompatibleDataVersion { .. })
    ));
    let resources = Resources::new(LEXICON_BYTES, &[]);
    assert!(
        crate::annotation::annotate_from("apple", 0, |tokens, skip| resources
            .for_annotation(tokens, skip))
        .is_ok()
    );
    assert_eq!(attempts(&resources), (1, 0));
}

#[test]
fn simple_query_validates_before_loading_and_propagates_cached_resource_errors() {
    let mut incompatible = LEXICON_BYTES.to_vec();
    incompatible[8..12].copy_from_slice(&999_u32.to_le_bytes());
    for bytes in [&[][..], Box::leak(incompatible.into_boxed_slice())] {
        let resources = Resources::new(bytes, &[]);
        let query = |word, lang| {
            crate::query::value_from(word, Field::MeaningEn, Some(lang), || resources.lexicon())
        };
        assert!(matches!(
            query(" apple", "ZH"),
            Err(Error::InvalidArgument {
                parameter: "word",
                ..
            })
        ));
        assert!(matches!(
            query("unknown", "ZH"),
            Err(Error::InvalidArgument {
                parameter: "lang",
                ..
            })
        ));
        assert_eq!(attempts(&resources), (0, 0));
        for word in ["unknown", "apple", "Apple"] {
            let error = query(word, "en").unwrap_err();
            if bytes.is_empty() {
                assert!(matches!(error, Error::Data { .. }));
            } else {
                assert!(matches!(error, Error::IncompatibleDataVersion { .. }));
            }
            assert_eq!(query(word, "zh").unwrap_err(), error);
        }
        assert_eq!(attempts(&resources), (1, 0));
    }
}

#[test]
fn category_queries_validate_word_then_resource_then_label_without_frequency() {
    let mut incompatible = LEXICON_BYTES.to_vec();
    incompatible[8..12].copy_from_slice(&999_u32.to_le_bytes());
    for bytes in [&[][..], Box::leak(incompatible.into_boxed_slice())] {
        let resources = Resources::new(bytes, &[]);
        assert!(matches!(
            crate::category::kind_from(" apple", "bad label", || resources.lexicon()),
            Err(Error::InvalidArgument {
                parameter: "word",
                ..
            })
        ));
        assert_eq!(attempts(&resources), (0, 0));
        let expected = resources.lexicon().err().unwrap();
        for label in ["CET4", "", "cet4", "\0", "unknown"] {
            for word in ["unknownwordzz", "apple"] {
                assert_eq!(
                    crate::category::kind_from(word, label, || resources.lexicon()).unwrap_err(),
                    expected
                );
            }
            assert_eq!(
                crate::category::list_from(label, || resources.lexicon()).unwrap_err(),
                expected
            );
        }
        assert_eq!(
            crate::category::labels_from(|| resources.lexicon()).unwrap_err(),
            expected
        );
        assert_eq!(attempts(&resources), (1, 0));
    }
    let resources = Resources::new(LEXICON_BYTES, &[]);
    assert!(crate::category::kind_from("apple", "CET4", || resources.lexicon()).unwrap());
    assert!(
        !crate::category::list_from("CET4", || resources.lexicon())
            .unwrap()
            .is_empty()
    );
    assert!(
        !crate::category::labels_from(|| resources.lexicon())
            .unwrap()
            .is_empty()
    );
    assert!(matches!(
        crate::category::kind_from("unknownwordzz", "cet4", || resources.lexicon()),
        Err(Error::InvalidArgument {
            parameter: "label",
            ..
        })
    ));
    assert_eq!(attempts(&resources), (1, 0));
}

#[test]
fn category_public_membership_matches_complete_lists_for_every_exact_word() {
    let lexicon = crate::data::lexicon().unwrap();
    let labels = crate::labels().unwrap();
    let mut total = 0;
    for label in labels {
        let members = crate::kind_list_with_label(&label).unwrap();
        let set: std::collections::HashSet<_> = members.iter().map(String::as_str).collect();
        assert_eq!(set.len(), members.len(), "duplicate members in {label}");
        total += members.len();
        for index in 0..lexicon.image.counts().entries {
            let word = lexicon.image.word(index);
            assert_eq!(
                crate::kind_with_label(word, &label).unwrap(),
                set.contains(word),
                "{word}/{label}"
            );
        }
        assert!(!crate::kind_with_label("unknownwordzz", &label).unwrap());
    }
    assert_eq!(total, crate::data_meta::LEXICON_MEMBERS);
}

#[test]
fn real_resources_are_independent_lazy_and_reused_without_rebuilding() {
    let resources = Resources::new(LEXICON_BYTES, FREQUENCY_BYTES);
    assert_eq!(attempts(&resources), (0, 0));
    let lexicon = resources.lexicon().unwrap();
    assert_eq!(lexicon.image.counts(), LEXICON_EXPECTED.counts);
    assert_eq!(attempts(&resources), (1, 0));
    for _ in 0..100 {
        assert!(std::ptr::eq(lexicon, resources.lexicon().unwrap()));
    }
    let frequency = resources.frequency().unwrap();
    assert_eq!(frequency.image.counts(), FREQUENCY_EXPECTED.counts);
    for _ in 0..100 {
        assert!(std::ptr::eq(frequency, resources.frequency().unwrap()));
    }
    assert_eq!(attempts(&resources), (1, 1));
}

#[test]
fn sixteen_threads_share_one_initialization_and_identical_borrowed_outputs() {
    let resources = Arc::new(Resources::new(LEXICON_BYTES, FREQUENCY_BYTES));
    let barrier = Arc::new(Barrier::new(16));
    let threads: Vec<_> = (0..16)
        .map(|_| {
            let resources = Arc::clone(&resources);
            let barrier = Arc::clone(&barrier);
            thread::spawn(move || {
                barrier.wait();
                let loaded = resources.for_annotation(true, 1000).unwrap().unwrap();
                let row = loaded.lexicon.find_exact("apple").unwrap();
                let ips = loaded.lexicon.image.field(row, Field::Ips).unwrap();
                let frequency = loaded.frequency.unwrap();
                for _ in 0..1000 {
                    assert_eq!(loaded.lexicon.image.field(row, Field::Ips), Some(ips));
                    assert!(frequency.contains("the", 1000));
                    assert!(loaded.lexicon.find_exact("unknownwordzz").is_none());
                }
                (
                    loaded.lexicon as *const Lexicon as usize,
                    frequency as *const Frequency as usize,
                    ips.as_ptr() as usize,
                    ips.to_owned(),
                )
            })
        })
        .collect();
    let results: Vec<_> = threads
        .into_iter()
        .map(|task| task.join().unwrap())
        .collect();
    assert!(results.iter().all(|value| value == &results[0]));
    assert_eq!(attempts(&resources), (1, 1));
}

#[test]
fn concurrent_initialization_failure_is_cached_and_cloned_as_an_error() {
    let resources = Arc::new(Resources::new(b"corrupt lexicon", b"corrupt frequency"));
    let barrier = Arc::new(Barrier::new(16));
    let threads: Vec<_> = (0..16)
        .map(|_| {
            let resources = Arc::clone(&resources);
            let barrier = Arc::clone(&barrier);
            thread::spawn(move || {
                barrier.wait();
                let first = resources.lexicon().err().unwrap();
                for _ in 0..100 {
                    assert_eq!(resources.lexicon().err().unwrap(), first);
                }
                first
            })
        })
        .collect();
    for task in threads {
        assert!(matches!(
            task.join().unwrap(),
            Error::Data {
                resource: "lexicon",
                ..
            }
        ));
    }
    assert_eq!(attempts(&resources), (1, 0));
}

#[test]
fn unused_resources_and_skip_zero_obey_the_annotation_loading_policy() {
    let resources = Resources::new(b"broken", b"broken");
    for skip_top in [0, 1, 1000, 5062, u32::MAX] {
        assert!(resources.for_annotation(false, skip_top).unwrap().is_none());
    }
    assert_eq!(attempts(&resources), (0, 0));
    let resources = Resources::new(LEXICON_BYTES, b"missing frequency");
    let loaded = resources.for_annotation(true, 0).unwrap().unwrap();
    assert!(loaded.frequency.is_none());
    assert!(loaded.lexicon.find_exact("apple").is_some());
    assert_eq!(attempts(&resources), (1, 0));
}

#[test]
fn nonzero_annotation_reports_frequency_before_lexicon_and_caches_each_failure() {
    let resources = Resources::new(b"broken lexicon", b"broken frequency");
    for _ in 0..3 {
        assert!(matches!(
            resources.for_annotation(true, 1),
            Err(Error::Data {
                resource: "frequency",
                ..
            })
        ));
    }
    assert_eq!(attempts(&resources), (0, 1));
    assert!(matches!(
        resources.for_annotation(true, 0),
        Err(Error::Data {
            resource: "lexicon",
            ..
        })
    ));
    assert_eq!(attempts(&resources), (1, 1));
    let resources = Resources::new(b"broken lexicon", FREQUENCY_BYTES);
    assert!(matches!(
        resources.for_annotation(true, 1),
        Err(Error::Data {
            resource: "lexicon",
            ..
        })
    ));
    assert_eq!(attempts(&resources), (1, 1));
    assert!(resources.frequency().is_ok());
}

#[test]
fn incompatible_version_failure_is_cached_without_becoming_a_missing_word() {
    // Deliberately only change the version header. Version errors take priority
    // over the resulting digest mismatch and retain the logical resource name.
    let mut bytes = LEXICON_BYTES.to_vec();
    bytes[8..12].copy_from_slice(&999_u32.to_le_bytes());
    let bytes = Box::leak(bytes.into_boxed_slice());
    let resources = Resources::new(bytes, FREQUENCY_BYTES);
    let first = resources.lexicon().err().unwrap();
    assert!(matches!(
        first,
        Error::IncompatibleDataVersion {
            resource: "lexicon",
            ..
        }
    ));
    assert_eq!(resources.lexicon().err().unwrap(), first);
    assert_eq!(attempts(&resources), (1, 0));
}

#[test]
fn exact_index_retains_every_precise_key_and_borrows_resource_strings() {
    let resources = Resources::new(LEXICON_BYTES, FREQUENCY_BYTES);
    let lexicon = resources.lexicon().unwrap();
    let start = LEXICON_BYTES.as_ptr() as usize;
    let end = start + LEXICON_BYTES.len();
    assert_eq!(lexicon.words.len(), meta::LEXICON_ENTRIES);
    for index in 0..lexicon.image.counts().entries {
        let word = lexicon.image.word(index);
        assert_eq!(lexicon.find_exact(word), Some(index));
        assert!((start..end).contains(&(word.as_ptr() as usize)));
        let stored_key = *lexicon.words.get_key_value(word).unwrap().0;
        assert_eq!(word.as_ptr(), stored_key.as_ptr());
        for field in [
            Field::Ipa,
            Field::Ips,
            Field::Ism,
            Field::Ipsm,
            Field::RootLemma,
            Field::MeaningEn,
            Field::MeaningZh,
        ] {
            if let Some(value) = lexicon.image.field(index, field) {
                let address = value.as_ptr() as usize;
                assert!(start <= address && address + value.len() <= end);
            }
        }
    }
    assert_ne!(lexicon.find_exact("May"), lexicon.find_exact("may"));
    assert!(lexicon.find_exact("APPLE").is_none());
    assert!(lexicon.find_exact("unknownwordzz").is_none());
}

#[test]
fn frequency_search_preserves_exact_spelling_and_inclusive_original_thresholds() {
    let resources = Resources::new(LEXICON_BYTES, FREQUENCY_BYTES);
    let frequency = resources.frequency().unwrap();
    for index in 0..frequency.image.counts().frequency_words {
        let (word, number) = frequency.image.frequency(index);
        assert_eq!(frequency.image.find_frequency(word), Some(number));
        assert!(frequency.contains(word, number));
        assert!(!frequency.contains(word, number - 1));
        assert!(frequency.contains(word, 5062));
        assert!(frequency.contains(word, u32::MAX));
        assert!(
            word.is_ascii(),
            "snapshot identity requires an explicit Unicode review if this changes"
        );
    }
    assert!(frequency.image.find_frequency("the").is_some());
    assert_eq!(frequency.image.find_frequency("eight hundred"), Some(2134));
    assert!((0..frequency.image.counts().frequency_words).any(|index| {
        frequency
            .image
            .frequency(index)
            .0
            .bytes()
            .any(|byte| byte.is_ascii_punctuation())
    }));
    assert!(!frequency.contains("The", 5062));
    assert!(!frequency.contains("unknownwordzz", 5062));
    assert!(!frequency.contains("the", 0));
    assert_eq!(attempts(&resources), (0, 1));
}

#[test]
fn complete_decoded_logical_content_matches_the_independent_p2_1_identity() {
    // This stream identity was established by the independent Python decoder,
    // not computed by the Rust parser under test. Include every field/state,
    // every ordered category member and every original frequency NUMBER.
    fn number(digest: &mut Sha256, value: usize) {
        digest.update(u32::try_from(value).unwrap().to_le_bytes());
    }
    fn text(digest: &mut Sha256, value: Option<&str>) {
        if let Some(value) = value {
            number(digest, value.len());
            digest.update(value.as_bytes());
        } else {
            digest.update(u32::MAX.to_le_bytes());
        }
    }
    let resources = Resources::new(LEXICON_BYTES, FREQUENCY_BYTES);
    let images = [
        &resources.lexicon().unwrap().image,
        &resources.frequency().unwrap().image,
    ];
    let mut digest = Sha256::new();
    for image in images {
        let counts = image.counts();
        for value in [
            counts.entries,
            counts.labels,
            counts.members,
            counts.frequency_words,
        ] {
            number(&mut digest, value);
        }
        for index in 0..counts.entries {
            text(&mut digest, Some(image.word(index)));
            for field in [
                Field::Ipa,
                Field::Ips,
                Field::Ism,
                Field::Ipsm,
                Field::RootLemma,
                Field::MeaningEn,
                Field::MeaningZh,
            ] {
                text(&mut digest, image.field(index, field));
            }
            digest.update(image.bits(index).to_le_bytes());
            let state: u32 = match image.annotation_state(index) {
                AnnotationState::Blocked => 0,
                AnnotationState::Fallback => 1,
                AnnotationState::Available => 2,
            };
            digest.update(state.to_le_bytes());
        }
        for ordinal in 0..counts.labels {
            text(&mut digest, Some(image.label(ordinal)));
            number(&mut digest, image.members(ordinal).count());
            for word in image.members(ordinal) {
                text(&mut digest, Some(word));
            }
        }
        for index in 0..counts.frequency_words {
            let (word, rank) = image.frequency(index);
            text(&mut digest, Some(word));
            digest.update(rank.to_le_bytes());
        }
    }
    assert_eq!(
        format!("{:x}", digest.finalize()),
        "30c5cd54d9fcf6cc7bdf0d8d99dd7d87f9763e3f65189596aae3c972702d2bd3"
    );
}

#[test]
fn shared_types_are_send_and_sync() {
    fn assert_shared<T: Send + Sync>() {}
    assert_shared::<Lexicon>();
    assert_shared::<Frequency>();
    assert_shared::<Resources>();
}

#[test]
#[ignore = "loader-only release measurement in fresh processes via tools/check_loader.py"]
fn cold_process_loader_probe() {
    let started = Instant::now();
    let lexicon = lexicon().unwrap();
    let lexicon_ms = started.elapsed().as_secs_f64() * 1000.0;
    let started = Instant::now();
    let frequency = RESOURCES.frequency().unwrap();
    let frequency_ms = started.elapsed().as_secs_f64() * 1000.0;
    let words = ["apple", "May", "may", "running", "unknownwordzz", "the"];
    let iterations = 100_000;
    let started = Instant::now();
    for index in 0..iterations {
        let loaded = black_box(super::lexicon().unwrap());
        black_box(loaded.find_exact(black_box(words[index % words.len()])));
    }
    let warm_ns = started.elapsed().as_secs_f64() * 1e9 / iterations as f64;
    assert!(std::ptr::eq(lexicon, RESOURCES.lexicon().unwrap()));
    assert!(std::ptr::eq(frequency, RESOURCES.frequency().unwrap()));
    assert_eq!(attempts(&RESOURCES), (1, 1));
    println!(
        "LOADER_PROBE {{\"lexicon_load_and_index_ms\":{lexicon_ms},\"frequency_load_ms\":{frequency_ms},\"warm_cached_exact_lookup_ns\":{warm_ns},\"warm_iterations\":{iterations},\"lexicon_initializations\":1,\"frequency_initializations\":1}}"
    );
}
