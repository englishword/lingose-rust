//! Pure-text IPS annotation with inclusive original-NUMBER frequency filtering.

use crate::annotation_unicode::{self as unicode, base};
use crate::data::{AnnotationResources, AnnotationState, Field, Frequency, Lexicon};
use crate::{Result, data, data_meta, validation};

pub(crate) fn annotate(text: &str, skip_top: i64) -> Result<String> {
    annotate_from(text, skip_top, data::for_annotation)
}

pub(crate) fn annotate_from<'a>(
    text: &str,
    skip_top: i64,
    load: impl FnOnce(bool, u32) -> Result<Option<AnnotationResources<'a>>>,
) -> Result<String> {
    validation::annotation(text, skip_top)?;
    let mut spans = word_spans(text);
    if !spans
        .iter()
        .any(|&(start, end)| is_english(&text[start..end]))
    {
        return Ok(text.to_owned());
    }
    let threshold = skip_top.min(i64::from(data_meta::MAX_SKIP_TOP)) as u32;
    let resources = load(true, threshold)?.expect("tokens require annotation resources");
    let skipped = Skipped {
        frequency: resources.frequency,
        threshold,
    };
    let protected = resources.frequency.map_or_else(Vec::new, |frequency| {
        protected_spans(text, frequency, threshold)
    });
    if !protected.is_empty() {
        spans.clear();
        let mut previous = 0;
        for &(start, end) in &protected {
            spans.extend(
                word_spans(&text[previous..start])
                    .into_iter()
                    .map(|(left, right)| (previous + left, previous + right)),
            );
            spans.push((start, end));
            previous = end;
        }
        spans.extend(
            word_spans(&text[previous..])
                .into_iter()
                .map(|(left, right)| (previous + left, previous + right)),
        );
    }
    let mut output = String::with_capacity(text.len());
    let mut previous = 0;
    for (index, &(start, end)) in spans.iter().enumerate() {
        output.push_str(&text[previous..start]);
        let word = &text[start..end];
        if protected.binary_search(&(start, end)).is_err() && is_english(word) {
            let next_word = spans.get(index + 1).and_then(|&(left, right)| {
                let candidate = &text[left..right];
                (context_separator(&text[end..left]) && is_english(candidate)).then_some(candidate)
            });
            output.push_str(&convert(
                word,
                next_word.unwrap_or(""),
                resources.lexicon,
                &skipped,
            ));
        } else {
            output.push_str(word);
        }
        previous = end;
    }
    output.push_str(&text[previous..]);
    Ok(output)
}

struct Skipped<'a> {
    frequency: Option<&'a Frequency>,
    threshold: u32,
}

impl Skipped<'_> {
    fn contains(&self, word: &str) -> bool {
        self.frequency.is_some_and(|frequency| {
            let lower = word.to_ascii_lowercase();
            frequency.contains(&lower, self.threshold)
                || (lower.contains('’')
                    && frequency.contains(&lower.replace('’', "'"), self.threshold))
        })
    }
}

// Exact CPython 3.12 re.IGNORECASE equivalence for a lowercase ASCII literal.
// Regex matching accepts four extra scalars; str.lower() membership rejects
// dotted/dotless I and long S, but accepts Kelvin K. A rejected match still
// consumes its full interval, just as pattern.finditer does before filtering.
fn special_prefix(text: &str, pattern: &str) -> Option<(usize, bool)> {
    let mut characters = text.chars();
    let mut length = 0;
    let mut lower_matches = true;
    for expected in pattern.bytes() {
        let character = characters.next()?;
        if character.is_ascii() && character.eq_ignore_ascii_case(&char::from(expected)) {
            // Literal ASCII, including regex punctuation, is compared directly.
        } else if (expected == b'i' && matches!(character, 'İ' | 'ı'))
            || (expected == b's' && character == 'ſ')
        {
            lower_matches = false;
        } else if !(expected == b'k' && character == 'K') {
            return None;
        }
        length += character.len_utf8();
    }
    Some((length, lower_matches))
}

fn frequency_neighbor(character: char) -> bool {
    unicode::flags(character) & 5 != 0 || matches!(character, '-' | '\'' | '’')
}

fn protected_spans(text: &str, frequency: &Frequency, threshold: u32) -> Vec<(usize, usize)> {
    let mut result = Vec::new();
    if threshold == 0 || frequency.special.is_empty() {
        return result;
    }
    let mut cursor = 0;
    while cursor < text.len() {
        let found = frequency
            .special
            .iter()
            .filter(|&&(_, rank)| rank <= threshold)
            .find_map(|&(pattern, _)| special_prefix(&text[cursor..], pattern));
        if let Some((length, lower_matches)) = found {
            let end = cursor + length;
            let left_blocked = text[..cursor]
                .chars()
                .next_back()
                .is_some_and(frequency_neighbor);
            let right_blocked = text[end..].chars().next().is_some_and(frequency_neighbor);
            if lower_matches && !left_blocked && !right_blocked {
                result.push((cursor, end));
            }
            cursor = end;
        } else {
            cursor += text[cursor..]
                .chars()
                .next()
                .expect("nonempty remainder")
                .len_utf8();
        }
    }
    result
}

fn context_separator(separator: &str) -> bool {
    let mut newline = false;
    for character in separator.chars() {
        if validation::python_whitespace(character) {
            if character == '\n' {
                if newline {
                    return false;
                }
                newline = true;
            }
        } else if matches!(
            character,
            '"' | '\'' | '‘' | '’' | '“' | '”' | '(' | ')' | '[' | ']'
        ) {
            // Python's blank-line regex only spans whitespace, not quotes.
            newline = false;
        } else {
            return false;
        }
    }
    true
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

pub(crate) fn is_english(word: &str) -> bool {
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

fn must_double(stem: &str) -> bool {
    let bytes = stem.as_bytes();
    let vowel = |c| b"aeiou".contains(&c);
    let mut groups = 0;
    let mut in_group = false;
    for &c in bytes {
        let inside = b"aeiouy".contains(&c);
        groups += usize::from(inside && !in_group);
        in_group = inside;
    }
    stem != "bus"
        && bytes.len() >= 3
        && !b"aeiouwxy".contains(&bytes[bytes.len() - 1])
        && vowel(bytes[bytes.len() - 2])
        && !vowel(bytes[bytes.len() - 3])
        && groups == 1
}

fn consonant_y(stem: &str) -> bool {
    stem.len() > 1 && stem.ends_with('y') && !b"aeiou".contains(&stem.as_bytes()[stem.len() - 2])
}

// All callers use lowercase ASCII spelling. Retained counts are letters, so
// byte offsets here equal Python character offsets, unlike notation offsets.
fn morph_candidates(word: &str) -> Vec<(String, usize, String)> {
    let mut candidates = Vec::new();
    let mut add = |stem: String, retained, tail: &str| {
        let candidate = (stem, retained, tail.to_owned());
        if !candidate.0.is_empty() && candidate.0 != word && !candidates.contains(&candidate) {
            candidates.push(candidate);
        }
    };
    if let Some(stem) = word.strip_suffix('s') {
        if stem.len() > 1
            && !["s", "x", "z", "ch", "sh"]
                .iter()
                .any(|suffix| stem.ends_with(suffix))
            && !consonant_y(stem)
        {
            add(stem.to_owned(), stem.len(), "s");
        }
        if let Some(stem) = word.strip_suffix("es") {
            if !stem.is_empty()
                && ["s", "x", "z", "ch", "sh", "o"]
                    .iter()
                    .any(|suffix| stem.ends_with(suffix))
            {
                add(stem.to_owned(), stem.len(), "es");
            }
        }
        if let Some(prefix) = word.strip_suffix("ies") {
            let stem = format!("{prefix}y");
            if consonant_y(&stem) {
                add(stem, prefix.len(), "ies");
            }
        }
    }
    if let Some(stem) = word.strip_suffix("ed") {
        if !stem.is_empty() && !stem.ends_with('e') && !consonant_y(stem) && !must_double(stem) {
            add(stem.to_owned(), stem.len(), "ed");
        }
        add(word[..word.len() - 1].to_owned(), word.len() - 1, "d");
        if let Some(prefix) = word.strip_suffix("ied") {
            let stem = format!("{prefix}y");
            if consonant_y(&stem) {
                add(stem, prefix.len(), "ied");
            }
        }
    }
    if let Some(stem) = word.strip_suffix("ing") {
        let keep_e = ["ee", "ye", "oe"]
            .iter()
            .any(|suffix| stem.ends_with(suffix))
            || matches!(stem, "age" | "singe" | "tinge" | "queue");
        if !stem.is_empty() && (!stem.ends_with('e') || keep_e) && !must_double(stem) {
            add(stem.to_owned(), stem.len(), "ing");
        }
        if !stem.is_empty() && !stem.ends_with(['e', 'y']) && !matches!(stem, "sing" | "ting") {
            add(format!("{stem}e"), stem.len(), "ing");
        }
        if let Some(prefix) = stem.strip_suffix('y') {
            add(format!("{prefix}ie"), prefix.len(), "ying");
        }
    }
    for suffix in ["ed", "ing"] {
        if let Some(stem) = word.strip_suffix(suffix) {
            let bytes = stem.as_bytes();
            if bytes.len() > 2
                && bytes[bytes.len() - 1] == bytes[bytes.len() - 2]
                && !b"aeiouwxy".contains(&bytes[bytes.len() - 1])
            {
                let retained = stem.len() - 1;
                add(
                    stem[..retained].to_owned(),
                    retained,
                    &format!("{}{suffix}", &stem[retained..]),
                );
            }
        }
    }
    candidates
}

fn inflected(word: &str, lexicon: &Lexicon) -> Option<String> {
    let mut output = None;
    let mut ambiguous = false;
    for (stem, retained, tail) in morph_candidates(&word.to_ascii_lowercase()) {
        let cased_stem: String = stem
            .bytes()
            .zip(word.bytes())
            .map(|(letter, original)| {
                char::from(if original.is_ascii_uppercase() {
                    letter.to_ascii_uppercase()
                } else {
                    letter
                })
            })
            .collect();
        let notation = match matched(&cased_stem, lexicon) {
            Match::Blocked => return None,
            Match::Available(value) => value,
            Match::Fallback | Match::Absent => continue,
        };
        let Some(notation) = case_notation(&cased_stem, notation) else {
            continue;
        };
        let mut projected = clusters(&notation)
            .into_iter()
            .take(retained)
            .collect::<String>();
        projected.push_str(&tail);
        if let Some(value) = case_notation(word, &projected) {
            if output.as_ref().is_some_and(|previous| previous != &value) {
                ambiguous = true;
            }
            output = Some(value);
        }
    }
    if ambiguous { None } else { output }
}

fn convert(word: &str, next_word: &str, lexicon: &Lexicon, skipped: &Skipped<'_>) -> String {
    struct Prefix<'a> {
        word: &'a str,
        cut: usize,
        alternative: Option<usize>,
    }
    // Keep Python's ordered depth-first prefix search without input-sized
    // native recursion for a token containing thousands of repeated n't tails.
    let mut pending = Vec::new();
    let mut current = word;
    let mut context = next_word;
    'evaluate: loop {
        let mut value = match convert_step(current, context, lexicon, skipped) {
            Conversion::Complete(value) => value,
            Conversion::Prefixes(cut, alternative) => {
                pending.push(Prefix {
                    word: current,
                    cut,
                    alternative,
                });
                current = &current[..cut];
                context = "";
                continue;
            }
        };
        while let Some(Prefix {
            word,
            cut,
            alternative,
        }) = pending.pop()
        {
            if !value.contains('[') {
                value.push_str(&word[cut..]);
            } else if let Some(cut) = alternative {
                pending.push(Prefix {
                    word,
                    cut,
                    alternative: None,
                });
                current = &word[..cut];
                context = "";
                continue 'evaluate;
            } else {
                value = format!("[{word}]");
            }
        }
        return value;
    }
}

enum Conversion {
    Complete(String),
    Prefixes(usize, Option<usize>),
}

fn convert_step(
    word: &str,
    next_word: &str,
    lexicon: &Lexicon,
    skipped: &Skipped<'_>,
) -> Conversion {
    use Conversion::{Complete, Prefixes};
    if skipped.contains(word) {
        return Complete(word.to_owned());
    }
    let unknown = || format!("[{word}]");
    let found = matched(word, lexicon);
    if found == Match::Blocked {
        return Complete(unknown());
    }
    let normalized = word.to_ascii_lowercase().replace('’', "'");
    if normalized == "the" {
        let vowel = next_word
            .as_bytes()
            .first()
            .is_some_and(|c| b"aeiou".contains(&c.to_ascii_lowercase()));
        return Complete(
            case_notation(word, if vowel { "ṫhē" } else { "ṫhe̊" }).unwrap_or_else(unknown),
        );
    }
    if let Match::Available(notation) = found {
        return Complete(case_notation(word, notation).unwrap_or_else(unknown));
    }
    let explicit = match normalized.as_str() {
        "don't" => Some("don't"),
        "doesn't" => Some("dô𝕖ṡn't"),
        "aren't" => Some("àr𝕖n't"),
        "i'm" => Some("I'm"),
        "you're" => Some("yoū're"),
        "o'clock" => Some("o̊'clock"),
        _ => None,
    };
    if let Some(notation) = explicit {
        return Complete(case_notation(word, notation).unwrap_or_else(unknown));
    }
    if word.contains('-') {
        let mut parts = word.split('-').peekable();
        let mut output = String::new();
        while let Some(part) = parts.next() {
            output.push_str(&convert(
                part,
                parts.peek().copied().unwrap_or(next_word),
                lexicon,
                skipped,
            ));
            if parts.peek().is_some() {
                output.push('-');
            }
        }
        return Complete(output);
    }
    if let Some(apostrophe) = normalized.find('\'') {
        // normalized offsets count one-byte apostrophes. Input may use U+2019;
        // map character cuts back to UTF-8 boundaries before slicing it.
        let mut cuts = Vec::new();
        if normalized.ends_with("n't") {
            cuts.push(normalized.len() - 3);
        }
        if !cuts.contains(&apostrophe) {
            cuts.push(apostrophe);
        }
        let mut offsets = cuts.into_iter().filter(|&cut| cut != 0).map(|cut| {
            word.char_indices()
                .nth(cut)
                .map_or(word.len(), |(offset, _)| offset)
        });
        if let Some(cut) = offsets.next() {
            return Prefixes(cut, offsets.next());
        }
        return Complete(unknown());
    }
    Complete(inflected(word, lexicon).unwrap_or_else(unknown))
}

#[cfg(test)]
#[path = "annotation_vectors.rs"]
mod vectors;

#[cfg(test)]
#[path = "annotation_context_vectors.rs"]
mod context_vectors;

#[cfg(test)]
#[path = "annotation_frequency_vectors.rs"]
mod frequency_vectors;
