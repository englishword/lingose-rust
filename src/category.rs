//! Category membership and stored business-order word lists.

use crate::{Error, Result, data, validation};
use data::Lexicon;

pub(crate) fn kind(word: &str, label: &str) -> Result<bool> {
    kind_from(word, label, data::lexicon)
}

pub(crate) fn list(label: &str) -> Result<Vec<String>> {
    list_from(label, data::lexicon)
}

pub(crate) fn labels() -> Result<Vec<String>> {
    labels_from(data::lexicon)
}

fn ordinal(lexicon: &Lexicon, label: &str) -> Result<usize> {
    (0..lexicon.image.counts().labels)
        .find(|&index| lexicon.image.label(index) == label)
        .ok_or(Error::InvalidArgument {
            parameter: "label",
            reason: "must be an exact registered category label",
        })
}

// Tests inject a local loader to verify precedence without replacing globals.
pub(crate) fn kind_from<'a>(
    word: &str,
    label: &str,
    load: impl FnOnce() -> Result<&'a Lexicon>,
) -> Result<bool> {
    validation::word(word)?;
    let lexicon = load()?;
    let ordinal = ordinal(lexicon, label)?;
    Ok(lexicon
        .find(word)
        .is_some_and(|index| lexicon.image.kind(index, ordinal)))
}

pub(crate) fn list_from<'a>(
    label: &str,
    load: impl FnOnce() -> Result<&'a Lexicon>,
) -> Result<Vec<String>> {
    let lexicon = load()?;
    let ordinal = ordinal(lexicon, label)?;
    Ok(lexicon.image.members(ordinal).map(str::to_owned).collect())
}

pub(crate) fn labels_from<'a>(load: impl FnOnce() -> Result<&'a Lexicon>) -> Result<Vec<String>> {
    let lexicon = load()?;
    Ok((0..lexicon.image.counts().labels)
        .map(|index| lexicon.image.label(index).to_owned())
        .collect())
}
