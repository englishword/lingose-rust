//! Basic pure-text annotation. Context/morphology and frequency follow in P3.2/3.

use crate::annotation_unicode::{self as unicode, base};
use crate::data::{AnnotationResources, AnnotationState, Field, Lexicon};
use crate::{Error, Result, data, validation};

pub(crate) fn annotate(text: &str, skip_top: i64) -> Result<String> {
    annotate_from(text, skip_top, data::for_annotation)
}

pub(crate) fn annotate_from<'a>(
    text: &str,
    skip_top: i64,
    load: impl FnOnce(bool, u32) -> Result<Option<AnnotationResources<'a>>>,
) -> Result<String> {
    validation::annotation(text, skip_top)?;
    let spans = word_spans(text);
    if !spans
        .iter()
        .any(|&(start, end)| is_english(&text[start..end]))
    {
        return Ok(text.to_owned());
    }
    // Do not silently ignore a requested frequency filter during phased work.
    if skip_top != 0 {
        return Err(Error::NotImplemented {
            operation: "annotate_ips_with_skip_top",
        });
    }
    let resources = load(true, 0)?.expect("tokens require annotation resources");
    let mut output = String::with_capacity(text.len());
    let mut previous = 0;
    for (start, end) in spans {
        output.push_str(&text[previous..start]);
        let word = &text[start..end];
        if is_english(word) {
            output.push_str(&convert(word, resources.lexicon));
        } else {
            output.push_str(word);
        }
        previous = end;
    }
    output.push_str(&text[previous..]);
    Ok(output)
}

// UTF-8 byte offsets are always scalar boundaries; business scanning is Python's
// isalnum()/M* and isalpha(), independent of the Rust compiler's Unicode version.
fn word_spans(text: &str) -> Vec<(usize, usize)> {
    let mut spans = Vec::new();
    let mut start = None;
    let mut chars = text.char_indices().peekable();
    while let Some((position, character)) = chars.next() {
        let mut inside = unicode::flags(character) & 5 != 0;
        if matches!(character, '-' | '\'' | '’') && start.is_some() {
            inside = chars
                .peek()
                .is_some_and(|&(_, next)| unicode::flags(next) & 2 != 0);
        }
        if inside {
            start.get_or_insert(position);
        } else if let Some(left) = start.take() {
            spans.push((left, position));
        }
    }
    if let Some(left) = start {
        spans.push((left, text.len()));
    }
    spans
}

fn is_english(word: &str) -> bool {
    let mut needs_letter = true;
    for character in word.chars() {
        if character.is_ascii_alphabetic() {
            needs_letter = false;
        } else if !needs_letter && matches!(character, '-' | '\'' | '’') {
            needs_letter = true;
        } else {
            return false;
        }
    }
    !needs_letter
}

fn clusters(value: &str) -> Vec<&str> {
    let mut result = Vec::new();
    let mut start = 0;
    for (position, character) in value.char_indices() {
        if position != 0 && !unicode::is_mark(character) {
            result.push(&value[start..position]);
            start = position;
        }
    }
    if !value.is_empty() {
        result.push(&value[start..]);
    }
    result
}

fn case_notation(word: &str, notation: &str) -> Option<String> {
    let clusters = clusters(notation);
    if clusters.len() != word.chars().count() {
        return None;
    }
    let mut output = String::with_capacity(notation.len());
    for (character, cluster) in word.chars().zip(clusters) {
        let expected = if character == '’' {
            '\''
        } else {
            character.to_ascii_lowercase()
        };
        if base(cluster) != Some(expected) {
            return None;
        }
        if matches!(character, '-' | '\'' | '’') {
            output.push(character);
        } else {
            unicode::push_case(&mut output, cluster, character.is_ascii_uppercase());
        }
    }
    Some(output)
}

#[derive(Debug, PartialEq)]
enum Match {
    Available(&'static str),
    Blocked,
    Fallback,
    Absent,
}

fn exact(word: &str, lexicon: &Lexicon) -> Option<Match> {
    lexicon
        .find_exact(word)
        .map(|index| match lexicon.image.annotation_state(index) {
            AnnotationState::Available => Match::Available(
                lexicon
                    .image
                    .field(index, Field::Ips)
                    .expect("validated available IPS"),
            ),
            AnnotationState::Blocked => Match::Blocked,
            AnnotationState::Fallback => Match::Fallback,
        })
}

fn matched(word: &str, lexicon: &Lexicon) -> Match {
    if let Some(found) = exact(word, lexicon) {
        return found;
    }
    let straight = word.replace('’', "'");
    if straight != word {
        if let Some(found) = exact(&straight, lexicon) {
            return found;
        }
    }
    // Convertible input is ASCII letters plus delimiters, so ASCII lowercase
    // equals Python str.lower() here. Never call simple-query lower_variant.
    let lower = word.to_ascii_lowercase();
    if lower != word {
        if let Some(found) = exact(&lower, lexicon) {
            return found;
        }
        let straight_lower = lower.replace('’', "'");
        if straight_lower != lower && straight_lower != straight {
            if let Some(found) = exact(&straight_lower, lexicon) {
                return found;
            }
        }
    }
    Match::Absent
}

fn convert(word: &str, lexicon: &Lexicon) -> String {
    if let Match::Available(notation) = matched(word, lexicon) {
        if let Some(output) = case_notation(word, notation) {
            return output;
        }
    }
    format!("[{word}]")
}

#[cfg(test)]
#[path = "annotation_vectors.rs"]
mod vectors;
