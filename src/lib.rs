#![doc = include_str!("../README.md")]

// Internal resource access is connected to public queries in P2.3/P2.4 and
// annotation in P3. Keep this temporary allowance confined to that module.
#[allow(dead_code)]
mod data;
mod data_meta;
mod error;
mod validation;

pub use error::{Error, Result};

/// Returns the selected, available IPA pronunciations for `word`.
///
/// The completed implementation will return an empty list for an unknown word
/// or unavailable IPA. This skeleton validates `word`, then returns
/// [`Error::NotImplemented`].
pub fn ipa(word: &str) -> Result<Vec<String>> {
    validation::word(word)?;
    not_implemented("ipa")
}

/// Returns the selected, available IPS pronunciations for `word`.
///
/// The list is independent of [`ipa`] and [`ipsm`]. This skeleton validates
/// `word`, then returns [`Error::NotImplemented`].
pub fn ips(word: &str) -> Result<Vec<String>> {
    validation::word(word)?;
    not_implemented("ips")
}

/// Returns the adopted morpheme division for `word`.
///
/// The completed implementation will return `None` when unavailable. This
/// skeleton validates `word`, then returns [`Error::NotImplemented`].
pub fn ism(word: &str) -> Result<Option<String>> {
    validation::word(word)?;
    not_implemented("ism")
}

/// Returns the selected IPSM values whose dependencies remain valid.
///
/// The list is independent of [`ipa`] and [`ips`]. This skeleton validates
/// `word`, then returns [`Error::NotImplemented`].
pub fn ipsm(word: &str) -> Result<Vec<String>> {
    validation::word(word)?;
    not_implemented("ipsm")
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
/// The completed implementation will return `None` when unavailable. This
/// skeleton validates `word`, then returns [`Error::NotImplemented`].
pub fn root_lemma(word: &str) -> Result<Option<String>> {
    validation::word(word)?;
    not_implemented("root_lemma")
}

/// Returns the original English meaning for `word`.
///
/// Equivalent to [`meaning_with_lang`] with `lang = "en"`. This skeleton
/// validates its arguments, then returns [`Error::NotImplemented`].
pub fn meaning(word: &str) -> Result<Option<String>> {
    meaning_with_lang(word, "en")
}

/// Returns the original meaning for `word` in exactly `"en"` or `"zh"`.
///
/// Word validation precedes language validation. The completed implementation
/// will return `None` for a valid unavailable meaning. This skeleton returns
/// [`Error::NotImplemented`] after argument validation.
pub fn meaning_with_lang(word: &str, lang: &str) -> Result<Option<String>> {
    validation::word(word)?;
    validation::language(lang)?;
    not_implemented("meaning_with_lang")
}

/// Returns whether `word` belongs to `CET4`.
///
/// Equivalent to [`kind_with_label`] with `label = "CET4"`. This skeleton
/// validates `word`, then returns [`Error::NotImplemented`].
pub fn kind(word: &str) -> Result<bool> {
    kind_with_label(word, "CET4")
}

/// Returns whether `word` belongs to the exact, case-sensitive category.
///
/// In the completed implementation resource validation will precede label
/// validation; a valid unknown word will return `false`. This skeleton validates
/// `word`, then returns [`Error::NotImplemented`] without validating the label.
pub fn kind_with_label(word: &str, label: &str) -> Result<bool> {
    validation::word(word)?;
    // The category registry will come from validated bundled data in P2.4.
    let _ = label;
    not_implemented("kind_with_label")
}

/// Returns the complete ordered `CET4` word list.
///
/// Equivalent to [`kind_list_with_label`] with `label = "CET4"`. This skeleton
/// returns [`Error::NotImplemented`].
pub fn kind_list() -> Result<Vec<String>> {
    kind_list_with_label("CET4")
}

/// Returns the complete word list for the exact, case-sensitive category.
///
/// The completed implementation will preserve Python's root/rank/word order.
/// This skeleton returns [`Error::NotImplemented`] without validating the label.
pub fn kind_list_with_label(label: &str) -> Result<Vec<String>> {
    let _ = label;
    not_implemented("kind_list_with_label")
}

/// Returns the registered category labels in baseline configuration order.
///
/// This skeleton returns [`Error::NotImplemented`].
pub fn labels() -> Result<Vec<String>> {
    not_implemented("labels")
}

/// Annotates plain text using IPS, with `skip_top = 0`.
///
/// Equivalent to [`annotate_ips_with_skip_top`]. This skeleton validates its
/// arguments, then returns [`Error::NotImplemented`], including for empty text.
pub fn annotate_ips(text: &str) -> Result<String> {
    annotate_ips_with_skip_top(text, 0)
}

/// Annotates plain text, leaving words up to an inclusive frequency threshold.
///
/// `skip_top` must be nonnegative. The completed implementation will cap it at
/// 5062 and preserve spelling case, whitespace and punctuation. This skeleton
/// validates the threshold before checking text for NUL, then returns
/// [`Error::NotImplemented`]; it does not yet tokenize or access resources.
pub fn annotate_ips_with_skip_top(text: &str, skip_top: i64) -> Result<String> {
    validation::annotation(text, skip_top)?;
    not_implemented("annotate_ips_with_skip_top")
}

fn not_implemented<T>(operation: &'static str) -> Result<T> {
    Err(Error::NotImplemented { operation })
}
