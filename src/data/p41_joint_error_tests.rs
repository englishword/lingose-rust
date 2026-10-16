//! Independent combinations extend the existing resource-error precedence tests.

use std::sync::atomic::Ordering;

use super::{FREQUENCY_BYTES, Field, LEXICON_BYTES, Resources};
use crate::Error;

fn broken(bytes: &'static [u8], version: bool) -> &'static [u8] {
    if version {
        let mut changed = bytes.to_vec();
        changed[8..12].copy_from_slice(&999_u32.to_le_bytes());
        Box::leak(changed.into_boxed_slice())
    } else {
        b"independent corrupt resource"
    }
}

fn assert_failure(error: &Error, resource: &'static str, version: bool) {
    if version {
        assert!(
            matches!(error, Error::IncompatibleDataVersion { resource: actual, .. } if *actual == resource)
        );
    } else {
        assert!(matches!(error, Error::Data { resource: actual, .. } if *actual == resource));
    }
}

#[test]
fn p41_all_joint_resource_failures_preserve_precedence_after_both_caches_fail() {
    for lexicon_version in [false, true] {
        for frequency_version in [false, true] {
            let resources = Resources::new(
                broken(LEXICON_BYTES, lexicon_version),
                broken(FREQUENCY_BYTES, frequency_version),
            );
            let annotate = |text, skip| {
                crate::annotation::annotate_from(text, skip, |has_tokens, threshold| {
                    resources.for_annotation(has_tokens, threshold)
                })
            };
            // Resource errors cannot turn irrelevant input into a failure.
            assert_eq!(
                annotate("中文 123 😀 e\u{301}", i64::MAX).unwrap(),
                "中文 123 😀 e\u{301}"
            );
            assert_eq!(resources.lexicon_attempts.load(Ordering::SeqCst), 0);
            assert_eq!(resources.frequency_attempts.load(Ordering::SeqCst), 0);

            let frequency_error = annotate("the", i64::MAX).unwrap_err();
            assert_failure(&frequency_error, "frequency", frequency_version);
            assert_eq!(resources.lexicon_attempts.load(Ordering::SeqCst), 0);

            // A simple unknown still checks the main resource. Having cached a
            // frequency failure does not affect simple queries or categories.
            let lexicon_error =
                crate::query::value_from("unknownwordzz", Field::Ips, None, || resources.lexicon())
                    .unwrap_err();
            assert_failure(&lexicon_error, "lexicon", lexicon_version);
            for text in ["the", "unknownwordzz"] {
                assert_eq!(annotate(text, 0).unwrap_err(), lexicon_error);
                assert_eq!(annotate(text, 1).unwrap_err(), frequency_error);
                assert_eq!(annotate(text, 5062).unwrap_err(), frequency_error);
            }
            assert_eq!(
                crate::category::kind_from("unknownwordzz", "invalid label", || resources
                    .lexicon())
                .unwrap_err(),
                lexicon_error
            );
            assert_eq!(
                crate::category::list_from("invalid label", || resources.lexicon()).unwrap_err(),
                lexicon_error
            );
            assert_eq!(
                crate::category::labels_from(|| resources.lexicon()).unwrap_err(),
                lexicon_error
            );
            // Input validation still precedes previously cached failures.
            assert!(matches!(
                annotate("the\0", -1),
                Err(Error::InvalidArgument {
                    parameter: "skip_top",
                    ..
                })
            ));
            assert!(matches!(
                annotate("the\0", 0),
                Err(Error::InvalidArgument {
                    parameter: "text",
                    ..
                })
            ));
            assert!(matches!(
                crate::query::value_from("unknownwordzz", Field::MeaningEn, Some("ZH"), || {
                    resources.lexicon()
                }),
                Err(Error::InvalidArgument {
                    parameter: "lang",
                    ..
                })
            ));
            assert_eq!(resources.lexicon_attempts.load(Ordering::SeqCst), 1);
            assert_eq!(resources.frequency_attempts.load(Ordering::SeqCst), 1);
        }
    }
}

#[test]
fn p41_fully_skipped_english_still_reports_main_data_or_version_error() {
    for version in [false, true] {
        let resources = Resources::new(broken(LEXICON_BYTES, version), FREQUENCY_BYTES);
        for skip in [1, 1000, 5062, i64::MAX] {
            let error = crate::annotation::annotate_from("the", skip, |has_tokens, threshold| {
                resources.for_annotation(has_tokens, threshold)
            })
            .unwrap_err();
            assert_failure(&error, "lexicon", version);
        }
        assert_eq!(resources.lexicon_attempts.load(Ordering::SeqCst), 1);
        assert_eq!(resources.frequency_attempts.load(Ordering::SeqCst), 1);
    }
}
