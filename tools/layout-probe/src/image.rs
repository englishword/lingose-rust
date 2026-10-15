#[cfg(any(feature = "hash", feature = "static-hash"))]
use std::collections::HashMap;
use std::collections::HashSet;
use std::error::Error;

const HEADER_BYTES: usize = 112;
const NULL: u32 = u32::MAX;
const ENTRY_BYTES: usize = 40;
const LABEL_BYTES: usize = 12;
const FREQUENCY_BYTES: usize = 8;

#[derive(Clone, Copy)]
pub enum Field {
    Ipa = 1,
    Ips = 2,
    Ism = 3,
    Ipsm = 4,
    Root = 5,
    MeaningEn = 6,
    MeaningZh = 7,
}

pub struct Image<'a> {
    bytes: &'a [u8],
    strings: usize,
    entries: usize,
    labels: usize,
    member_count: usize,
    frequencies: usize,
    entry_start: usize,
    label_start: usize,
    member_start: usize,
    frequency_start: usize,
    pool_start: usize,
    pool_bytes: usize,
}

impl<'a> Image<'a> {
    pub fn parse(bytes: &'a [u8]) -> Result<Self, Box<dyn Error>> {
        if bytes.len() < HEADER_BYTES || &bytes[..8] != b"LNGIDX01" {
            return Err("invalid image header".into());
        }
        let u32_at = |offset| read_u32(bytes, offset);
        if u32_at(8) != 1 || u32_at(36) != 2 || u32_at(40) != 1 || u32_at(44) != 1 {
            return Err(
                "unsupported format, lexicon schema, frequency schema, or IPSM algorithm".into(),
            );
        }
        if bytes[48..80].iter().all(|&b| b == 0) || bytes[80..112].iter().all(|&b| b == 0) {
            return Err("missing source data version".into());
        }
        let strings = u32_at(12) as usize;
        let entries = u32_at(16) as usize;
        let labels = u32_at(20) as usize;
        let member_count = u32_at(24) as usize;
        let frequencies = u32_at(28) as usize;
        let pool_bytes = u32_at(32) as usize;
        if labels > 32 || strings == 0 || (entries == 0 && frequencies == 0) {
            return Err("invalid image counts".into());
        }
        let advance = |start: usize, count: usize, width: usize| -> Result<usize, Box<dyn Error>> {
            start
                .checked_add(count.checked_mul(width).ok_or("section size overflow")?)
                .ok_or_else(|| "section end overflow".into())
        };
        let entry_start = advance(
            HEADER_BYTES,
            strings.checked_add(1).ok_or("offset count overflow")?,
            4,
        )?;
        let label_start = advance(entry_start, entries, ENTRY_BYTES)?;
        let member_start = advance(label_start, labels, LABEL_BYTES)?;
        let frequency_start = advance(member_start, member_count, 4)?;
        let pool_start = advance(frequency_start, frequencies, FREQUENCY_BYTES)?;
        if advance(pool_start, pool_bytes, 1)? != bytes.len() {
            return Err("section bounds or trailing bytes invalid".into());
        }
        let image = Self {
            bytes,
            strings,
            entries,
            labels,
            member_count,
            frequencies,
            entry_start,
            label_start,
            member_start,
            frequency_start,
            pool_start,
            pool_bytes,
        };
        image.validate()?;
        Ok(image)
    }

    fn validate(&self) -> Result<(), Box<dyn Error>> {
        if self.pool_offset(0) != 0 || self.pool_offset(self.strings) != self.pool_bytes {
            return Err("invalid string pool boundaries".into());
        }
        let mut previous: Option<&str> = None;
        for index in 0..self.strings {
            let start = self.pool_offset(index);
            let end = self.pool_offset(index + 1);
            if start > end || end > self.pool_bytes {
                return Err("invalid string offsets".into());
            }
            let value =
                std::str::from_utf8(&self.bytes[self.pool_start + start..self.pool_start + end])?;
            if previous.is_some_and(|prior| prior.as_bytes() >= value.as_bytes()) {
                return Err("strings not distinct and sorted by UTF-8".into());
            }
            previous = Some(value);
        }

        let valid_bits = if self.labels == 32 {
            u32::MAX
        } else {
            (1_u32 << self.labels) - 1
        };
        let mut previous: Option<&str> = None;
        for index in 0..self.entries {
            let base = self.entry_start + index * ENTRY_BYTES;
            for field in 0..8 {
                let reference = self.u32_at(base + field * 4);
                if reference != NULL && reference as usize >= self.strings {
                    return Err("invalid entry string reference".into());
                }
                if field == 0 && reference == NULL {
                    return Err("null word reference".into());
                }
            }
            let word = self.word(index);
            if previous.is_some_and(|prior| prior.as_bytes() >= word.as_bytes()) {
                return Err("entry words not distinct and sorted by UTF-8".into());
            }
            previous = Some(word);
            if self.u32_at(base + 32) & !valid_bits != 0 {
                return Err("invalid membership bitmap".into());
            }
            let state = self.u32_at(base + 36);
            if state > 2
                || (state == 2) != self.field(index, Field::Ips).is_some_and(|s| !s.is_empty())
            {
                return Err("invalid annotation availability state".into());
            }
        }

        let mut label_ids = HashSet::new();
        let mut next_member = 0;
        let mut seen = vec![false; self.entries];
        for ordinal in 0..self.labels {
            let base = self.label_start + ordinal * LABEL_BYTES;
            let label = self.u32_at(base);
            let start = self.u32_at(base + 4) as usize;
            let length = self.u32_at(base + 8) as usize;
            if label as usize >= self.strings || !label_ids.insert(label) || start != next_member {
                return Err("invalid label reference or member range order".into());
            }
            let end = start.checked_add(length).ok_or("member range overflow")?;
            if end > self.member_count {
                return Err("member range outside section".into());
            }
            seen.fill(false);
            for position in start..end {
                let entry = self.u32_at(self.member_start + position * 4) as usize;
                if entry >= self.entries || seen[entry] || !self.kind(entry, ordinal) {
                    return Err("invalid, duplicate, or inconsistent category member".into());
                }
                seen[entry] = true;
            }
            for (entry, listed) in seen.iter().copied().enumerate() {
                if listed != self.kind(entry, ordinal) {
                    return Err("membership bitmap disagrees with complete list".into());
                }
            }
            next_member = end;
        }
        if next_member != self.member_count {
            return Err("unreferenced category members".into());
        }

        let mut previous: Option<&str> = None;
        for index in 0..self.frequencies {
            let base = self.frequency_start + index * FREQUENCY_BYTES;
            let reference = self.u32_at(base);
            let number = self.u32_at(base + 4);
            if reference as usize >= self.strings || !(1..=5062).contains(&number) {
                return Err("invalid frequency record".into());
            }
            let word = self.string(reference);
            if previous.is_some_and(|prior| prior.as_bytes() >= word.as_bytes()) {
                return Err("frequency words not distinct and sorted by UTF-8".into());
            }
            previous = Some(word);
        }
        Ok(())
    }

    fn u32_at(&self, offset: usize) -> u32 {
        read_u32(self.bytes, offset)
    }
    fn pool_offset(&self, index: usize) -> usize {
        self.u32_at(HEADER_BYTES + index * 4) as usize
    }

    fn string(&self, reference: u32) -> &'a str {
        let reference = reference as usize;
        let start = self.pool_start + self.pool_offset(reference);
        let end = self.pool_start + self.pool_offset(reference + 1);
        std::str::from_utf8(&self.bytes[start..end]).expect("validated UTF-8 string")
    }

    pub fn entry_count(&self) -> usize {
        self.entries
    }
    pub fn string_count(&self) -> usize {
        self.strings
    }
    pub fn label_count(&self) -> usize {
        self.labels
    }
    pub fn member_count(&self) -> usize {
        self.member_count
    }
    pub fn frequency_count(&self) -> usize {
        self.frequencies
    }

    pub fn word(&self, index: usize) -> &'a str {
        self.string(self.u32_at(self.entry_start + index * ENTRY_BYTES))
    }

    pub fn field(&self, index: usize, field: Field) -> Option<&'a str> {
        let reference = self.u32_at(self.entry_start + index * ENTRY_BYTES + field as usize * 4);
        (reference != NULL).then(|| self.string(reference))
    }

    pub fn kind(&self, index: usize, ordinal: usize) -> bool {
        self.u32_at(self.entry_start + index * ENTRY_BYTES + 32) & (1_u32 << ordinal) != 0
    }

    pub fn label(&self, ordinal: usize) -> &'a str {
        self.string(self.u32_at(self.label_start + ordinal * LABEL_BYTES))
    }

    pub fn members(&self, ordinal: usize) -> impl Iterator<Item = &'a str> + '_ {
        let base = self.label_start + ordinal * LABEL_BYTES;
        let start = self.u32_at(base + 4) as usize;
        let length = self.u32_at(base + 8) as usize;
        (start..start + length)
            .map(|position| self.word(self.u32_at(self.member_start + position * 4) as usize))
    }

    pub fn frequency(&self, position: usize) -> (&'a str, u32) {
        let base = self.frequency_start + position * FREQUENCY_BYTES;
        (self.string(self.u32_at(base)), self.u32_at(base + 4))
    }

    pub fn find_frequency(&self, word: &str) -> Option<u32> {
        binary_find(self.frequencies, |index| {
            self.frequency(index).0.as_bytes().cmp(word.as_bytes())
        })
        .map(|index| self.frequency(index).1)
    }

    pub fn logical_checksum_from(&self, seed: u64) -> u64 {
        let mut fnv = Fnv(seed);
        for count in [
            self.entries,
            self.labels,
            self.member_count,
            self.frequencies,
        ] {
            fnv.u32(count as u32);
        }
        for index in 0..self.entries {
            let base = self.entry_start + index * ENTRY_BYTES;
            for field in 0..8 {
                let reference = self.u32_at(base + field * 4);
                if reference == NULL {
                    fnv.u32(NULL);
                } else {
                    fnv.string(self.string(reference));
                }
            }
            fnv.u32(self.u32_at(base + 32));
            fnv.u32(self.u32_at(base + 36));
        }
        for ordinal in 0..self.labels {
            fnv.string(self.label(ordinal));
            let base = self.label_start + ordinal * LABEL_BYTES;
            fnv.u32(self.u32_at(base + 8));
            for word in self.members(ordinal) {
                fnv.string(word);
            }
        }
        for index in 0..self.frequencies {
            let (word, number) = self.frequency(index);
            fnv.string(word);
            fnv.u32(number);
        }
        fnv.0
    }
}

pub struct Lookup<'image, 'data> {
    image: &'image Image<'data>,
    #[cfg(any(feature = "hash", feature = "static-hash"))]
    words: HashMap<&'data str, usize>,
}

impl<'image, 'data> Lookup<'image, 'data> {
    pub fn new(image: &'image Image<'data>) -> Self {
        Self {
            image,
            #[cfg(any(feature = "hash", feature = "static-hash"))]
            words: (0..image.entries)
                .map(|index| (image.word(index), index))
                .collect(),
        }
    }

    pub fn find(&self, word: &str) -> Option<usize> {
        #[cfg(any(feature = "hash", feature = "static-hash"))]
        {
            debug_assert_eq!(self.words.len(), self.image.entries);
            self.words.get(word).copied()
        }
        #[cfg(not(any(feature = "hash", feature = "static-hash")))]
        {
            binary_find(self.image.entries, |index| {
                self.image.word(index).as_bytes().cmp(word.as_bytes())
            })
        }
    }
}

fn read_u32(bytes: &[u8], offset: usize) -> u32 {
    u32::from_le_bytes(
        bytes[offset..offset + 4]
            .try_into()
            .expect("bounded u32 field"),
    )
}

fn binary_find(count: usize, compare: impl Fn(usize) -> std::cmp::Ordering) -> Option<usize> {
    let mut low = 0;
    let mut high = count;
    while low < high {
        let middle = low + (high - low) / 2;
        match compare(middle) {
            std::cmp::Ordering::Less => low = middle + 1,
            std::cmp::Ordering::Greater => high = middle,
            std::cmp::Ordering::Equal => return Some(middle),
        }
    }
    None
}

struct Fnv(u64);

impl Fnv {
    fn u32(&mut self, value: u32) {
        self.bytes(&value.to_le_bytes());
    }
    fn string(&mut self, value: &str) {
        self.u32(value.len() as u32);
        self.bytes(value.as_bytes());
    }
    fn bytes(&mut self, bytes: &[u8]) {
        for &byte in bytes {
            self.0 = (self.0 ^ u64::from(byte)).wrapping_mul(0x100000001b3);
        }
    }
}
