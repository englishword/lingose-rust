//! Simple queries over the validated, shared lexicon.

use crate::{Result, data, validation};
use data::{Field, Lexicon};

pub(crate) fn list(word: &str, field: Field) -> Result<Vec<String>> {
    optional(word, field).map(|value| value.into_iter().collect())
}

pub(crate) fn optional(word: &str, field: Field) -> Result<Option<String>> {
    value_from(word, field, None, data::lexicon)
}

pub(crate) fn meaning(word: &str, lang: &str) -> Result<Option<String>> {
    let field = if lang == "zh" {
        Field::MeaningZh
    } else {
        Field::MeaningEn
    };
    value_from(word, field, Some(lang), data::lexicon)
}

// A loader argument lets isolated tests exercise the same validation/query path
// without replacing the process-wide resource cache or the bundled data.
pub(crate) fn value_from<'a>(
    word: &str,
    field: Field,
    lang: Option<&str>,
    load: impl FnOnce() -> Result<&'a Lexicon>,
) -> Result<Option<String>> {
    validation::word(word)?;
    if let Some(lang) = lang {
        validation::language(lang)?;
    }
    let lexicon = load()?;
    Ok(lexicon
        .find(word)
        .and_then(|index| lexicon.image.field(index, field))
        .map(str::to_owned))
}
