//! Python 3.12 / Unicode 15.0 casing for simple-query fallback only.
//!
//! Tables derive from the audited interpreter, independently of compiler UCD.
//! See docs/query-case.json and third_party/unicode/LICENSE.txt for attribution.

#[path = "query_case_tables.rs"]
mod tables;

fn is_uppercase(character: char) -> bool {
    let codepoint = u32::from(character);
    let past = tables::UPPERCASE_RANGES.partition_point(|&(first, _)| first <= codepoint);
    past != 0 && codepoint <= tables::UPPERCASE_RANGES[past - 1].1
}

fn scalar_lowercase(character: char) -> Option<&'static str> {
    tables::LOWERCASE
        .binary_search_by_key(&u32::from(character), |&(codepoint, _)| codepoint)
        .ok()
        .map(|index| tables::LOWERCASE[index].1)
}

/// Returns Python's one permitted lowercase query variant, when it changes.
pub(crate) fn lower_variant(word: &str) -> Option<String> {
    let mut characters = word.chars();
    if !is_uppercase(characters.next()?) || characters.any(is_uppercase) {
        return None;
    }
    let mut lower = String::with_capacity(word.len());
    for character in word.chars() {
        if let Some(mapped) = scalar_lowercase(character) {
            lower.push_str(mapped);
        } else {
            lower.push(character);
        }
    }
    // Python's only default contextual lowercase rule is Final_Sigma. Its
    // capital Sigma is Uppercase and therefore can occur only at index zero
    // under our predicate. With no preceding cased character, that rule cannot
    // apply. Per-scalar full mappings equal str.lower() on this input domain.
    (lower != word).then_some(lower)
}

#[cfg(test)]
mod tests {
    use sha2::{Digest, Sha256};

    use super::{is_uppercase, lower_variant, scalar_lowercase, tables};

    #[test]
    fn every_scalar_matches_the_pinned_python_uppercase_and_lowercase_digest() {
        let mut digest = Sha256::new();
        let mut count = 0;
        for codepoint in 0..=0x10ffff_u32 {
            let Some(character) = char::from_u32(codepoint) else {
                continue;
            };
            count += 1;
            let mut buffer = [0; 4];
            let lowered =
                scalar_lowercase(character).unwrap_or_else(|| character.encode_utf8(&mut buffer));
            digest.update(codepoint.to_le_bytes());
            digest.update([u8::from(is_uppercase(character))]);
            digest.update(u32::try_from(lowered.len()).unwrap().to_le_bytes());
            digest.update(lowered.as_bytes());
        }
        assert_eq!(count, 0x110000 - 0x800);
        assert_eq!(format!("{:x}", digest.finalize()), tables::SCALAR_SHA256);
    }

    #[test]
    fn fallback_predicate_is_first_uppercase_and_no_later_uppercase() {
        for (word, expected) in [
            ("Apple", Some("apple")),
            ("A", Some("a")),
            ("A1-b'c\u{301}", Some("a1-b'c\u{301}")),
            ("", None),
            ("apple", None),
            ("US", None),
            ("iPhone", None),
            ("McDonald", None),
            ("1Apple", None),
            ("AK", None),
            ("AⒶ", None),
        ] {
            assert_eq!(lower_variant(word).as_deref(), expected, "{word:?}");
        }
    }

    #[test]
    fn full_lowercase_preserves_python_titlecase_expansion_and_uppercase_properties() {
        for (word, expected) in [
            ("ǅfoo", None),
            ("Aǅ", Some("aǆ")),
            ("İ", Some("i\u{307}")),
            ("İs", Some("i\u{307}s")),
            ("Ⅰfoo", Some("ⅰfoo")),
            ("Ⓐfoo", Some("ⓐfoo")),
            ("K", Some("k")),
            ("ℌ", None),
            ("𝐀", None),
            ("𝐀b", None),
            ("A𝐀", None),
        ] {
            assert_eq!(lower_variant(word).as_deref(), expected, "{word:?}");
        }
        assert!(is_uppercase('ℌ'));
        assert!(is_uppercase('𝐀'));
        assert!(!is_uppercase('ǅ'));
    }

    #[test]
    fn accepted_queries_cannot_trigger_contextual_final_sigma() {
        for (word, expected) in [
            ("Σ", Some("σ")),
            ("Σ\u{301}", Some("σ\u{301}")),
            ("Σ'", Some("σ'")),
            ("Σx", Some("σx")),
            ("Aσ", Some("aσ")),
            ("AΣ", None),
            ("A'Σ", None),
            ("ΣΣ", None),
        ] {
            assert_eq!(lower_variant(word).as_deref(), expected, "{word:?}");
        }
    }

    #[test]
    fn post_baseline_unicode_assignments_keep_the_unicode_15_behavior() {
        // U+1C89 and U+A7CB were assigned in Unicode 16; U+A7CE in Unicode 17.
        // Their classification here must not follow the compiler's UCD.
        for character in ['\u{1c89}', '\u{a7cb}', '\u{a7ce}'] {
            assert!(!is_uppercase(character));
            assert_eq!(scalar_lowercase(character), None);
            assert_eq!(lower_variant(&character.to_string()), None);
            assert_eq!(
                lower_variant(&format!("A{character}")),
                Some(format!("a{character}"))
            );
        }
    }
}
