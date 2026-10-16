//! Checked, borrowed views of the frozen v1 resources. No source data is rebuilt.

use std::collections::HashSet;

use sha2::{Digest, Sha256};

use crate::{Error, Result, data_meta as meta, validation};

const HEADER: usize = 112;
const NULL: u32 = u32::MAX;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct Counts {
    pub strings: usize,
    pub entries: usize,
    pub labels: usize,
    pub members: usize,
    pub frequency_words: usize,
    pub pool_bytes: usize,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(super) enum Kind {
    Lexicon,
    Frequency,
}

#[derive(Clone, Copy)]
pub(super) struct Expected<'a> {
    pub resource: &'static str,
    pub kind: Kind,
    pub sha256: &'a str,
    pub bytes: usize,
    pub counts: Counts,
}

#[derive(Clone, Copy, Debug)]
pub(crate) enum Field {
    Ipa = 1,
    Ips = 2,
    Ism = 3,
    Ipsm = 4,
    RootLemma = 5,
    MeaningEn = 6,
    MeaningZh = 7,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) enum AnnotationState {
    Blocked,
    Fallback,
    Available,
}

pub(crate) struct Image<'a> {
    bytes: &'a [u8],
    pool: &'a str,
    counts: Counts,
    entry_start: usize,
    label_start: usize,
    member_start: usize,
    frequency_start: usize,
    resource: &'static str,
}

impl<'a> Image<'a> {
    pub(super) fn parse(bytes: &'a [u8], expected: Expected<'_>) -> Result<Self> {
        let bad = |message| corrupt(expected.resource, message);
        if bytes.len() < HEADER || &bytes[..8] != b"LNGIDX01" {
            return Err(bad("missing or invalid v1 header"));
        }
        // Classify incompatible versions separately, even when their changed
        // header would also fail the expected digest. Diagnostic text is not API.
        let required = [
            meta::FORMAT_VERSION,
            meta::LEXICON_SCHEMA_VERSION,
            meta::FREQUENCY_SCHEMA_VERSION,
            meta::IPSM_ALGORITHM_VERSION,
        ];
        let found = [
            u32_at(bytes, 8),
            u32_at(bytes, 36),
            u32_at(bytes, 40),
            u32_at(bytes, 44),
        ];
        if found != required {
            return Err(Error::IncompatibleDataVersion {
                resource: expected.resource,
                expected: format!("format/schema/algorithm {required:?}"),
                found: format!("format/schema/algorithm {found:?}"),
            });
        }
        for (name, range, version) in [
            ("lexicon", 48..80, meta::LEXICON_DATA_VERSION),
            ("frequency", 80..112, meta::FREQUENCY_DATA_VERSION),
        ] {
            if !matches_hex(&bytes[range.clone()], version) {
                return Err(Error::IncompatibleDataVersion {
                    resource: expected.resource,
                    expected: format!("{name} {version}"),
                    found: format!("{name} {}", hex(&bytes[range])),
                });
            }
        }
        if bytes.len() != expected.bytes {
            return Err(bad("resource byte count differs from the frozen manifest"));
        }
        if !matches_hex(&Sha256::digest(bytes), expected.sha256) {
            return Err(bad("resource SHA-256 differs from the frozen manifest"));
        }
        let count = |offset| {
            usize::try_from(u32_at(bytes, offset)).map_err(|_| bad("count exceeds address space"))
        };
        let counts = Counts {
            strings: count(12)?,
            entries: count(16)?,
            labels: count(20)?,
            members: count(24)?,
            frequency_words: count(28)?,
            pool_bytes: count(32)?,
        };
        if counts != expected.counts {
            return Err(bad("resource counts differ from the frozen manifest"));
        }
        if counts.strings == 0 || counts.labels > 32 {
            return Err(bad("invalid string or label count"));
        }
        match expected.kind {
            Kind::Lexicon if counts.entries == 0 || counts.frequency_words != 0 => {
                return Err(bad("invalid lexicon sections"));
            }
            Kind::Frequency
                if counts.frequency_words == 0
                    || counts.entries != 0
                    || counts.labels != 0
                    || counts.members != 0 =>
            {
                return Err(bad("invalid frequency sections"));
            }
            _ => {}
        }
        let advance = |start: usize, count: usize, width: usize| {
            count
                .checked_mul(width)
                .and_then(|size| start.checked_add(size))
                .ok_or_else(|| bad("section size exceeds address space"))
        };
        let offsets = counts
            .strings
            .checked_add(1)
            .ok_or_else(|| bad("offset count overflow"))?;
        let entry_start = advance(HEADER, offsets, 4)?;
        let label_start = advance(entry_start, counts.entries, 40)?;
        let member_start = advance(label_start, counts.labels, 12)?;
        let frequency_start = advance(member_start, counts.members, 4)?;
        let pool_start = advance(frequency_start, counts.frequency_words, 8)?;
        if advance(pool_start, counts.pool_bytes, 1)? != bytes.len() {
            return Err(bad("section bounds, truncation or trailing bytes invalid"));
        }
        let pool = std::str::from_utf8(&bytes[pool_start..])
            .map_err(|_| bad("string pool is not valid UTF-8"))?;
        let image = Self {
            bytes,
            pool,
            counts,
            entry_start,
            label_start,
            member_start,
            frequency_start,
            resource: expected.resource,
        };
        image.validate()?;
        Ok(image)
    }

    fn validate(&self) -> Result<()> {
        let bad = |message| corrupt(self.resource, message);
        if self.offset(0) != 0 || self.offset(self.counts.strings) != self.pool.len() {
            return Err(bad("invalid string pool boundary"));
        }
        let mut previous: Option<&str> = None;
        for index in 0..self.counts.strings {
            let start = self.offset(index);
            let end = self.offset(index + 1);
            // get() also rejects a boundary inside a UTF-8 sequence, even if
            // concatenating the entire pool produced a valid UTF-8 string.
            let value = self
                .pool
                .get(start..end)
                .ok_or_else(|| bad("invalid string offsets or UTF-8 boundary"))?;
            if previous.is_some_and(|prior| prior.as_bytes() >= value.as_bytes()) {
                return Err(bad("string pool is not unique and UTF-8 byte sorted"));
            }
            previous = Some(value);
        }
        let valid_bits = if self.counts.labels == 32 {
            u32::MAX
        } else {
            (1_u32 << self.counts.labels) - 1
        };
        previous = None;
        for index in 0..self.counts.entries {
            let base = self.entry_start + index * 40;
            for column in 0..8 {
                let id = u32_at(self.bytes, base + column * 4);
                if (id == NULL && column == 0) || (id != NULL && id as usize >= self.counts.strings)
                {
                    return Err(bad("invalid entry string ID"));
                }
            }
            let word = self.word(index);
            if validation::word(word).is_err()
                || previous.is_some_and(|prior| prior.as_bytes() >= word.as_bytes())
            {
                return Err(bad(
                    "entry words are invalid, duplicate or not UTF-8 byte sorted",
                ));
            }
            previous = Some(word);
            if self.bits(index) & !valid_bits != 0 {
                return Err(bad("entry bitmap contains an unregistered label"));
            }
            let state = u32_at(self.bytes, base + 36);
            let ips = self.field(index, Field::Ips);
            if state > 2
                || match state {
                    2 => ips.is_none_or(str::is_empty),
                    _ => ips.is_some(),
                }
            {
                return Err(bad("annotation state and available IPS disagree"));
            }
        }
        let mut reconstructed = Vec::new();
        reconstructed
            .try_reserve_exact(self.counts.entries)
            .map_err(|_| bad("cannot allocate membership validation buffer"))?;
        reconstructed.resize(self.counts.entries, 0_u32);
        let mut labels = HashSet::new();
        let mut next = 0;
        for ordinal in 0..self.counts.labels {
            let base = self.label_start + ordinal * 12;
            let id = u32_at(self.bytes, base);
            let start = u32_at(self.bytes, base + 4) as usize;
            let length = u32_at(self.bytes, base + 8) as usize;
            if id as usize >= self.counts.strings || start != next {
                return Err(bad("invalid label ID or member range order"));
            }
            let label = self.string(id);
            if label.is_empty() || label.contains('\0') || !labels.insert(label) {
                return Err(bad("empty, invalid or duplicate label"));
            }
            let end = start
                .checked_add(length)
                .filter(|&end| end <= self.counts.members)
                .ok_or_else(|| bad("category range outside member section"))?;
            let bit = 1_u32 << ordinal;
            for position in start..end {
                let member = u32_at(self.bytes, self.member_start + position * 4) as usize;
                let value = reconstructed
                    .get_mut(member)
                    .ok_or_else(|| bad("member entry ID out of bounds"))?;
                if *value & bit != 0 {
                    return Err(bad("duplicate category member"));
                }
                *value |= bit;
            }
            next = end;
        }
        if next != self.counts.members {
            return Err(bad("unreferenced category members"));
        }
        for (index, bits) in reconstructed.into_iter().enumerate() {
            if self.bits(index) != bits {
                return Err(bad("category lists and entry bitmaps disagree"));
            }
        }
        previous = None;
        for index in 0..self.counts.frequency_words {
            let base = self.frequency_start + index * 8;
            let id = u32_at(self.bytes, base);
            let number = u32_at(self.bytes, base + 4);
            if id as usize >= self.counts.strings || !(1..=meta::MAX_SKIP_TOP).contains(&number) {
                return Err(bad("invalid frequency ID or original NUMBER"));
            }
            let word = self.string(id);
            // Current frozen keys are all ASCII. Check their lowercase contract
            // without using the compiler's Unicode case tables. Other UTF-8 is
            // preserved; exact source spelling is protected by the fixed hash.
            if word.is_empty()
                || word.contains('\0')
                || word.bytes().any(|byte| byte.is_ascii_uppercase())
                || previous.is_some_and(|prior| prior.as_bytes() >= word.as_bytes())
            {
                return Err(bad(
                    "frequency keys are invalid, duplicate or not UTF-8 byte sorted",
                ));
            }
            previous = Some(word);
        }
        Ok(())
    }

    fn offset(&self, index: usize) -> usize {
        u32_at(self.bytes, HEADER + index * 4) as usize
    }

    fn string(&self, id: u32) -> &'a str {
        &self.pool[self.offset(id as usize)..self.offset(id as usize + 1)]
    }

    pub(crate) fn counts(&self) -> Counts {
        self.counts
    }

    // Indices below come only from validated records, bounded iteration or the
    // exact-key map. They are not public caller-provided parameters.
    pub(crate) fn word(&self, index: usize) -> &'a str {
        self.string(u32_at(self.bytes, self.entry_start + index * 40))
    }

    pub(crate) fn field(&self, index: usize, field: Field) -> Option<&'a str> {
        let id = u32_at(
            self.bytes,
            self.entry_start + index * 40 + field as usize * 4,
        );
        (id != NULL).then(|| self.string(id))
    }

    pub(crate) fn bits(&self, index: usize) -> u32 {
        u32_at(self.bytes, self.entry_start + index * 40 + 32)
    }

    pub(crate) fn kind(&self, index: usize, ordinal: usize) -> bool {
        self.bits(index) & (1_u32 << ordinal) != 0
    }

    pub(crate) fn annotation_state(&self, index: usize) -> AnnotationState {
        match u32_at(self.bytes, self.entry_start + index * 40 + 36) {
            0 => AnnotationState::Blocked,
            1 => AnnotationState::Fallback,
            2 => AnnotationState::Available,
            _ => unreachable!("validated annotation state"),
        }
    }

    pub(crate) fn label(&self, ordinal: usize) -> &'a str {
        self.string(u32_at(self.bytes, self.label_start + ordinal * 12))
    }

    pub(crate) fn members(&self, ordinal: usize) -> impl Iterator<Item = &'a str> + '_ {
        let base = self.label_start + ordinal * 12;
        let start = u32_at(self.bytes, base + 4) as usize;
        let length = u32_at(self.bytes, base + 8) as usize;
        (start..start + length).map(|position| {
            self.word(u32_at(self.bytes, self.member_start + position * 4) as usize)
        })
    }

    pub(crate) fn frequency(&self, index: usize) -> (&'a str, u32) {
        let base = self.frequency_start + index * 8;
        (
            self.string(u32_at(self.bytes, base)),
            u32_at(self.bytes, base + 4),
        )
    }

    pub(crate) fn find_frequency(&self, word: &str) -> Option<u32> {
        let mut low = 0;
        let mut high = self.counts.frequency_words;
        while low < high {
            let middle = low + (high - low) / 2;
            let (key, number) = self.frequency(middle);
            match key.as_bytes().cmp(word.as_bytes()) {
                std::cmp::Ordering::Less => low = middle + 1,
                std::cmp::Ordering::Greater => high = middle,
                std::cmp::Ordering::Equal => return Some(number),
            }
        }
        None
    }
}

fn u32_at(bytes: &[u8], offset: usize) -> u32 {
    u32::from_le_bytes(
        bytes[offset..offset + 4]
            .try_into()
            .expect("validated u32 section bounds"),
    )
}

fn matches_hex(bytes: &[u8], expected: &str) -> bool {
    const HEX: &[u8] = b"0123456789abcdef";
    expected.len() == bytes.len() * 2
        && bytes
            .iter()
            .zip(expected.as_bytes().chunks_exact(2))
            .all(|(&byte, pair)| pair == [HEX[usize::from(byte >> 4)], HEX[usize::from(byte & 15)]])
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|byte| format!("{byte:02x}")).collect()
}

pub(super) fn corrupt(resource: &'static str, message: &str) -> Error {
    Error::Data {
        resource,
        message: message.to_owned(),
    }
}
