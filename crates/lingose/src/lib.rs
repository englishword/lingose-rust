#![doc = include_str!("../README.md")]

mod annotation;
mod annotation_unicode;
mod category;
mod data;
mod data_meta;
mod error;
mod query;
mod query_case;
mod validation;

pub use error::{Error, Result};

/// Returns the selected, available IPA pronunciations for `word`.
///
/// Returns an empty list for an unknown word or unavailable IPA. Exact spelling
/// takes priority; eligible initial-capital words may fall back to lowercase.
/// Invalid arguments and resource failures return an error.
pub fn ipa(word: &str) -> Result<Vec<String>> {
    query::list(word, data::Field::Ipa)
}

/// Returns the selected, available IPS pronunciations for `word`.
///
/// The list is independent of [`ipa`] and [`ipsm`]. Returns an empty list when
/// unknown or unavailable, with the same matching and error rules as [`ipa`].
pub fn ips(word: &str) -> Result<Vec<String>> {
    query::list(word, data::Field::Ips)
}

/// Returns the adopted morpheme division for `word`.
///
/// Returns `None` when unknown or unavailable, with the same matching and error
/// rules as [`ipa`]. Does not derive a new division.
pub fn ism(word: &str) -> Result<Option<String>> {
    query::optional(word, data::Field::Ism)
}

/// Returns the selected IPSM values whose dependencies remain valid.
///
/// The list is independent of [`ipa`] and [`ips`]. Returns an empty list when
/// unknown or unavailable, with the same matching and error rules as [`ipa`].
/// Uses saved, validated values rather than recomputing candidates.
pub fn ipsm(word: &str) -> Result<Vec<String>> {
    query::list(word, data::Field::Ipsm)
}

/// An alias of [`ipa`] with identical behavior.
pub use ipa as IPA;
/// An alias of [`ips`] with identical behavior.
pub use ips as IPS;
/// An alias of [`ipsm`] with identical behavior.
pub use ipsm as IPSM;
/// An alias of [`ism`] with identical behavior.
pub use ism as ISM;

/// Returns the saved root lemma, without running a lemmatization algorithm.
///
/// Returns `None` when unknown or unavailable, with the same matching and error
/// rules as [`ipa`].
pub fn root_lemma(word: &str) -> Result<Option<String>> {
    query::optional(word, data::Field::RootLemma)
}

/// Returns the original English meaning for `word`.
///
/// Equivalent to [`meaning_with_lang`] with `lang = "en"`.
pub fn meaning(word: &str) -> Result<Option<String>> {
    meaning_with_lang(word, "en")
}

/// Returns the original meaning for `word` in exactly `"en"` or `"zh"`.
///
/// Word validation precedes language validation and resource loading. Returns
/// `None` when unknown or unavailable; preserves original Unicode and newlines.
/// Uses the same matching rules as [`ipa`].
pub fn meaning_with_lang(word: &str, lang: &str) -> Result<Option<String>> {
    query::meaning(word, lang)
}

/// Returns whether `word` belongs to `CET4`.
///
/// Equivalent to [`kind_with_label`] with `label = "CET4"`.
pub fn kind(word: &str) -> Result<bool> {
    kind_with_label(word, "CET4")
}

/// Returns whether `word` belongs to the exact, case-sensitive category.
///
/// Validates `word`, loads the lexicon, then validates the exact category label
/// before lookup. Unknown words and unavailable or false membership return
/// `false`. Uses the same word matching rules as [`ipa`].
pub fn kind_with_label(word: &str, label: &str) -> Result<bool> {
    category::kind(word, label)
}

/// Returns the complete ordered `CET4` word list.
///
/// Equivalent to [`kind_list_with_label`] with `label = "CET4"`.
pub fn kind_list() -> Result<Vec<String>> {
    kind_list_with_label("CET4")
}

/// Returns the complete word list for the exact, case-sensitive category.
///
/// Preserves the saved Python root/rank/word business order and original word
/// keys. Loads the lexicon before validating the label; registered empty
/// categories return an empty list. The result owns its strings.
pub fn kind_list_with_label(label: &str) -> Result<Vec<String>> {
    category::list(label)
}

/// Returns the registered category labels in baseline configuration order.
///
/// Returns owned strings from the validated lexicon, in configuration order.
/// Only boolean categories are registered; attributes such as `COLLINS` and
/// `Band` are excluded.
pub fn labels() -> Result<Vec<String>> {
    category::labels()
}

/// Annotates plain text using IPS, with `skip_top = 0`.
///
/// Equivalent to [`annotate_ips_with_skip_top`] with zero threshold.
/// Includes `the` context, contractions, compound and word-form fallback.
/// Preserves whitespace, punctuation and non-English spans.
pub fn annotate_ips(text: &str) -> Result<String> {
    annotate_ips_with_skip_top(text, 0)
}

/// Annotates plain text, leaving words up to an inclusive frequency threshold.
///
/// Validates the nonnegative threshold before text NUL. With no English token,
/// returns the input without loading resources. Uses the original inclusive
/// frequency NUMBER, capped at 5062, including stored inflections and phrases.
/// Zero never loads frequency data; positive values check frequency then lexicon.
pub fn annotate_ips_with_skip_top(text: &str, skip_top: i64) -> Result<String> {
    annotation::annotate(text, skip_top)
}
