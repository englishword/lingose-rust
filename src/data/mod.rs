//! Independent lazy resources with borrowed, immutable query indices.

use std::collections::HashMap;
use std::sync::OnceLock;

use crate::{Result, data_meta as meta};

use image::{Counts, Expected, Image, Kind, corrupt};

mod image;

pub(crate) use image::{AnnotationState, Field};

static LEXICON_BYTES: &[u8] = include_bytes!("../../data/lexicon.bin");
static FREQUENCY_BYTES: &[u8] = include_bytes!("../../data/frequency.bin");

const LEXICON_EXPECTED: Expected<'static> = Expected {
    resource: "lexicon",
    kind: Kind::Lexicon,
    sha256: meta::LEXICON_SHA256,
    bytes: meta::LEXICON_BYTES,
    counts: Counts {
        strings: meta::LEXICON_STRINGS,
        entries: meta::LEXICON_ENTRIES,
        labels: meta::LEXICON_LABELS,
        members: meta::LEXICON_MEMBERS,
        frequency_words: meta::LEXICON_FREQUENCY_WORDS,
        pool_bytes: meta::LEXICON_POOL_BYTES,
    },
};
const FREQUENCY_EXPECTED: Expected<'static> = Expected {
    resource: "frequency",
    kind: Kind::Frequency,
    sha256: meta::FREQUENCY_SHA256,
    bytes: meta::FREQUENCY_BYTES,
    counts: Counts {
        strings: meta::FREQUENCY_STRINGS,
        entries: meta::FREQUENCY_ENTRIES,
        labels: meta::FREQUENCY_LABELS,
        members: meta::FREQUENCY_MEMBERS,
        frequency_words: meta::FREQUENCY_FREQUENCY_WORDS,
        pool_bytes: meta::FREQUENCY_POOL_BYTES,
    },
};

pub(crate) struct Lexicon {
    pub(crate) image: Image<'static>,
    words: HashMap<&'static str, usize>,
}

impl Lexicon {
    fn load(bytes: &'static [u8]) -> Result<Self> {
        let image = Image::parse(bytes, LEXICON_EXPECTED)?;
        let mut words = HashMap::new();
        words
            .try_reserve(image.counts().entries)
            .map_err(|_| corrupt("lexicon", "cannot allocate exact word index"))?;
        for index in 0..image.counts().entries {
            words.insert(image.word(index), index);
        }
        Ok(Self { image, words })
    }

    pub(crate) fn find_exact(&self, word: &str) -> Option<usize> {
        self.words.get(word).copied()
    }

    // An exact entry stops lookup even when its requested field is unavailable.
    // Annotation uses a different fallback policy and must not call this helper.
    pub(crate) fn find(&self, word: &str) -> Option<usize> {
        self.find_exact(word).or_else(|| {
            crate::query_case::lower_variant(word).and_then(|lower| self.find_exact(&lower))
        })
    }
}

pub(crate) struct Frequency {
    pub(crate) image: Image<'static>,
    pub(crate) special: Vec<(&'static str, u32)>,
}

impl Frequency {
    fn load(bytes: &'static [u8]) -> Result<Self> {
        Self::from_image(Image::parse(bytes, FREQUENCY_EXPECTED)?)
    }

    fn from_image(image: Image<'static>) -> Result<Self> {
        let mut special = Vec::new();
        for index in 0..image.counts().frequency_words {
            let (word, number) = image.frequency(index);
            // Pinned v1 frequency keys are all lowercase ASCII. The literal
            // IGNORECASE matcher relies on this explicit, checked domain.
            if !word.is_ascii() {
                return Err(corrupt(
                    "frequency",
                    "v1 matching requires ASCII frequency keys",
                ));
            }
            if !crate::annotation::is_english(word) {
                special.push((word, number));
            }
        }
        special.sort_unstable_by(|a, b| b.0.len().cmp(&a.0.len()).then(a.0.cmp(b.0)));
        Ok(Self { image, special })
    }

    pub(crate) fn contains(&self, word: &str, skip_top: u32) -> bool {
        self.image
            .find_frequency(word)
            .is_some_and(|number| number <= skip_top.min(meta::MAX_SKIP_TOP))
    }
}

pub(crate) struct AnnotationResources<'a> {
    pub(crate) lexicon: &'a Lexicon,
    pub(crate) frequency: Option<&'a Frequency>,
}

struct Resources {
    lexicon_bytes: &'static [u8],
    frequency_bytes: &'static [u8],
    lexicon: OnceLock<Result<Lexicon>>,
    frequency: OnceLock<Result<Frequency>>,
    #[cfg(test)]
    lexicon_attempts: std::sync::atomic::AtomicUsize,
    #[cfg(test)]
    frequency_attempts: std::sync::atomic::AtomicUsize,
}

impl Resources {
    const fn new(lexicon_bytes: &'static [u8], frequency_bytes: &'static [u8]) -> Self {
        Self {
            lexicon_bytes,
            frequency_bytes,
            lexicon: OnceLock::new(),
            frequency: OnceLock::new(),
            #[cfg(test)]
            lexicon_attempts: std::sync::atomic::AtomicUsize::new(0),
            #[cfg(test)]
            frequency_attempts: std::sync::atomic::AtomicUsize::new(0),
        }
    }

    fn lexicon(&self) -> Result<&Lexicon> {
        cached(&self.lexicon, || {
            #[cfg(test)]
            self.lexicon_attempts
                .fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            Lexicon::load(self.lexicon_bytes)
        })
    }

    fn frequency(&self) -> Result<&Frequency> {
        cached(&self.frequency, || {
            #[cfg(test)]
            self.frequency_attempts
                .fetch_add(1, std::sync::atomic::Ordering::SeqCst);
            Frequency::load(self.frequency_bytes)
        })
    }

    // P3 supplies whether its tokenizer found a convertible English token.
    // Policy is centralized here without approximating tokenization in P2.2.
    fn for_annotation(
        &self,
        has_tokens: bool,
        skip_top: u32,
    ) -> Result<Option<AnnotationResources<'_>>> {
        if !has_tokens {
            return Ok(None);
        }
        let frequency = if skip_top == 0 {
            None
        } else {
            Some(self.frequency()?)
        };
        let lexicon = self.lexicon()?;
        Ok(Some(AnnotationResources { lexicon, frequency }))
    }
}

fn cached<T>(cell: &OnceLock<Result<T>>, initialize: impl FnOnce() -> Result<T>) -> Result<&T> {
    cell.get_or_init(initialize).as_ref().map_err(Clone::clone)
}

static RESOURCES: Resources = Resources::new(LEXICON_BYTES, FREQUENCY_BYTES);

pub(crate) fn lexicon() -> Result<&'static Lexicon> {
    RESOURCES.lexicon()
}

pub(crate) fn for_annotation(
    has_tokens: bool,
    skip_top: u32,
) -> Result<Option<AnnotationResources<'static>>> {
    RESOURCES.for_annotation(has_tokens, skip_top)
}

#[cfg(test)]
mod cache_tests;
#[cfg(test)]
mod tests;
