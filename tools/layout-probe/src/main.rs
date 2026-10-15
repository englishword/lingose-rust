#![forbid(unsafe_code)]

#[cfg(not(any(
    feature = "static",
    feature = "gzip",
    feature = "hash",
    feature = "static-hash"
)))]
compile_error!("enable exactly one candidate feature: static, gzip, hash, or static-hash");
#[cfg(any(
    all(
        feature = "static",
        any(feature = "gzip", feature = "hash", feature = "static-hash")
    ),
    all(feature = "gzip", any(feature = "hash", feature = "static-hash")),
    all(feature = "hash", feature = "static-hash")
))]
compile_error!("candidate features are mutually exclusive");

mod image;

use image::{Field, Image, Lookup};
use serde::Serialize;
use sha2::{Digest, Sha256};
use std::error::Error;
use std::hint::black_box;
use std::io::{self, Write};
use std::path::Path;
use std::time::{Duration, Instant};

#[cfg(any(feature = "static", feature = "static-hash"))]
const LEXICON_PAYLOAD: &[u8] = include_bytes!("../../../.local/layout/image.bin");
#[cfg(any(feature = "gzip", feature = "hash"))]
const LEXICON_PAYLOAD: &[u8] = include_bytes!("../../../.local/layout/image.bin.gz");
#[cfg(any(feature = "static", feature = "static-hash"))]
const FREQUENCY_PAYLOAD: &[u8] = include_bytes!("../../../.local/layout/frequency.bin");
#[cfg(any(feature = "gzip", feature = "hash"))]
const FREQUENCY_PAYLOAD: &[u8] = include_bytes!("../../../.local/layout/frequency.bin.gz");
const LEXICON_SHA256: &str = include_str!("../../../.local/layout/image.sha256");
const FREQUENCY_SHA256: &str = include_str!("../../../.local/layout/frequency.sha256");

#[derive(Serialize)]
struct Measurement {
    scenario: String,
    operations: u64,
    elapsed_ms: f64,
    ns_per_operation: f64,
    output_bytes: u64,
}

impl Measurement {
    fn new(name: impl Into<String>, elapsed: Duration, operations: u64, bytes: u64) -> Self {
        Self {
            scenario: name.into(),
            operations,
            elapsed_ms: elapsed.as_secs_f64() * 1000.0,
            ns_per_operation: elapsed.as_secs_f64() * 1.0e9 / operations.max(1) as f64,
            output_bytes: bytes,
        }
    }
}

#[derive(Serialize)]
struct Report {
    candidate: &'static str,
    format_version: u32,
    embedded_bytes: usize,
    lexicon_embedded_bytes: usize,
    frequency_embedded_bytes: usize,
    lexicon_raw_bytes: usize,
    frequency_raw_bytes: usize,
    entry_count: usize,
    string_count: usize,
    label_count: usize,
    member_count: usize,
    frequency_count: usize,
    load_ms: f64,
    lexicon_load_ms: f64,
    frequency_load_ms: f64,
    index_ms: f64,
    lexicon_sha256: String,
    frequency_sha256: String,
    logical_content_checksum: String,
    checksum_contract: &'static str,
    workload_contract: &'static str,
    measurements: Vec<Measurement>,
}

fn main() {
    if let Err(error) = run() {
        eprintln!("layout probe: {error}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), Box<dyn Error>> {
    let mut hold = false;
    let mut hold_before_load = false;
    let mut load_only = false;
    let mut corpus_paths = Vec::new();
    for argument in std::env::args_os().skip(1) {
        if argument == "--hold" {
            hold = true;
        } else if argument == "--hold-before-load" {
            hold_before_load = true;
        } else if argument == "--load-only" {
            load_only = true;
        } else {
            corpus_paths.push(argument);
        }
    }
    if corpus_paths.len() != 2 {
        return Err("expected corpus-10000.txt and corpus-100000.txt, optionally --hold".into());
    }
    if hold_before_load {
        eprintln!("ready-before-load");
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
    }

    let started = Instant::now();
    let lexicon_bytes = decode(LEXICON_PAYLOAD)?;
    let lexicon_sha256 = verify_digest(&lexicon_bytes, LEXICON_SHA256)?;
    let image = Image::parse(&lexicon_bytes)?;
    if image.entry_count() == 0 || image.frequency_count() != 0 {
        return Err("lexicon image must contain entries and no frequency records".into());
    }
    let lexicon_load_time = started.elapsed();
    let started = Instant::now();
    let frequency_bytes = decode(FREQUENCY_PAYLOAD)?;
    let frequency_sha256 = verify_digest(&frequency_bytes, FREQUENCY_SHA256)?;
    let frequency = Image::parse(&frequency_bytes)?;
    if frequency.entry_count() != 0
        || frequency.label_count() != 0
        || frequency.frequency_count() == 0
    {
        return Err("frequency image must contain frequencies and no entries or labels".into());
    }
    let frequency_load_time = started.elapsed();
    let index_started = Instant::now();
    let lookup = Lookup::new(&image);
    let index_time = index_started.elapsed();

    let mut measurements = Vec::new();
    if !load_only {
        measurements = query_measurements(&image, &frequency, &lookup);
        for corpus_path in corpus_paths {
            let path = Path::new(&corpus_path);
            let text = std::fs::read_to_string(path)?;
            let name = path
                .file_name()
                .and_then(|name| name.to_str())
                .ok_or("invalid corpus name")?;
            for threshold in [0, 1000, 5062] {
                measurements.push(corpus_measurement(
                    &image, &frequency, &lookup, name, &text, threshold,
                ));
            }
        }
    }
    let report = Report {
        candidate: candidate(),
        format_version: 1,
        embedded_bytes: LEXICON_PAYLOAD.len() + FREQUENCY_PAYLOAD.len(),
        lexicon_embedded_bytes: LEXICON_PAYLOAD.len(),
        frequency_embedded_bytes: FREQUENCY_PAYLOAD.len(),
        lexicon_raw_bytes: lexicon_bytes.len(),
        frequency_raw_bytes: frequency_bytes.len(),
        entry_count: image.entry_count(),
        string_count: image.string_count(),
        label_count: image.label_count(),
        member_count: image.member_count(),
        frequency_count: frequency.frequency_count(),
        load_ms: (lexicon_load_time + frequency_load_time).as_secs_f64() * 1000.0,
        lexicon_load_ms: lexicon_load_time.as_secs_f64() * 1000.0,
        frequency_load_ms: frequency_load_time.as_secs_f64() * 1000.0,
        index_ms: index_time.as_secs_f64() * 1000.0,
        lexicon_sha256,
        frequency_sha256,
        logical_content_checksum: format!(
            "{:016x}",
            frequency.logical_checksum_from(image.logical_checksum_from(0xcbf29ce484222325))
        ),
        checksum_contract: "fnv1a64-v1: lexicon then frequency image; per image four little-endian u32 counts (entries, labels, members, frequencies); each entry's eight nullable length-prefixed UTF-8 strings, kind bits, annotation state; each label string, member count and ordered member words; every frequency word and original NUMBER; null string length=0xffffffff",
        workload_contract: "exact spelling and owned result projection; ASCII-letter token lookup plus IPS copy at original frequency thresholds; this is a layout workload, not annotate_ips or Python semantic conformance",
        measurements,
    };
    serde_json::to_writer(io::stdout().lock(), &report)?;
    println!();
    io::stdout().flush()?;
    if hold {
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
    }
    Ok(())
}

fn decode(payload: &'static [u8]) -> Result<std::borrow::Cow<'static, [u8]>, Box<dyn Error>> {
    #[cfg(any(feature = "static", feature = "static-hash"))]
    {
        Ok(std::borrow::Cow::Borrowed(payload))
    }
    #[cfg(any(feature = "gzip", feature = "hash"))]
    {
        use std::io::Read;
        let mut bytes = Vec::new();
        let mut decoder = flate2::read::GzDecoder::new(payload);
        decoder.read_to_end(&mut bytes)?;
        Ok(std::borrow::Cow::Owned(bytes))
    }
}

fn verify_digest(bytes: &[u8], expected: &str) -> Result<String, Box<dyn Error>> {
    let expected = expected.trim();
    if expected.len() != 64 || !expected.bytes().all(|b| b.is_ascii_hexdigit()) {
        return Err("invalid SHA256 sidecar".into());
    }
    let actual = format!("{:x}", Sha256::digest(bytes));
    if actual != expected.to_ascii_lowercase() {
        return Err("image SHA256 does not match sidecar".into());
    }
    Ok(actual)
}

fn candidate() -> &'static str {
    if cfg!(feature = "static") {
        "static"
    } else if cfg!(feature = "gzip") {
        "gzip"
    } else if cfg!(feature = "static-hash") {
        "static-hash"
    } else {
        "hash"
    }
}

fn query_measurements(
    image: &Image<'_>,
    frequency: &Image<'_>,
    lookup: &Lookup<'_, '_>,
) -> Vec<Measurement> {
    const QUERY_ROUNDS: usize = 2;
    let mut results = Vec::new();
    for (name, field, list) in [
        ("ipa", Field::Ipa, true),
        ("ips", Field::Ips, true),
        ("ism", Field::Ism, false),
        ("ipsm", Field::Ipsm, true),
        ("root_lemma", Field::Root, false),
        ("meaning_en", Field::MeaningEn, false),
        ("meaning_zh", Field::MeaningZh, false),
    ] {
        let started = Instant::now();
        let mut bytes = 0_u64;
        for _ in 0..QUERY_ROUNDS {
            for position in 0..image.entry_count() {
                let word = black_box(image.word(position));
                let found = lookup.find(word).expect("validated entry must be found");
                let value = image.field(found, field);
                if list {
                    let output: Vec<String> = value.into_iter().map(str::to_owned).collect();
                    bytes += output.iter().map(|s| s.len() as u64).sum::<u64>();
                    black_box(output);
                } else {
                    let output = value.map(str::to_owned);
                    bytes += output.as_ref().map_or(0, |s| s.len() as u64);
                    black_box(output);
                }
            }
        }
        results.push(Measurement::new(
            format!("exact_owned_{name}"),
            started.elapsed(),
            (QUERY_ROUNDS * image.entry_count()) as u64,
            bytes,
        ));
    }

    let started = Instant::now();
    for _ in 0..QUERY_ROUNDS {
        for ordinal in 0..image.label_count() {
            for position in 0..image.entry_count() {
                let word = black_box(image.word(position));
                let found = lookup.find(word).expect("validated entry must be found");
                black_box(image.kind(found, ordinal));
            }
        }
    }
    results.push(Measurement::new(
        "exact_kind_all_labels",
        started.elapsed(),
        (QUERY_ROUNDS * image.entry_count() * image.label_count()) as u64,
        0,
    ));

    let started = Instant::now();
    let mut bytes = 0_u64;
    for _ in 0..10_000 {
        let output: Vec<String> = (0..image.label_count())
            .map(|i| image.label(i).to_owned())
            .collect();
        bytes += output.iter().map(|s| s.len() as u64).sum::<u64>();
        black_box(output);
    }
    results.push(Measurement::new(
        "owned_labels",
        started.elapsed(),
        10_000,
        bytes,
    ));

    let started = Instant::now();
    let mut bytes = 0_u64;
    for _ in 0..10 {
        for ordinal in 0..image.label_count() {
            let output: Vec<String> = image.members(ordinal).map(str::to_owned).collect();
            bytes += output.iter().map(|s| s.len() as u64).sum::<u64>();
            black_box(output);
        }
    }
    results.push(Measurement::new(
        "owned_kind_list_all_labels",
        started.elapsed(),
        (10 * image.label_count()) as u64,
        bytes,
    ));

    let started = Instant::now();
    for _ in 0..10 {
        for position in 0..frequency.frequency_count() {
            let (word, number) = frequency.frequency(position);
            assert_eq!(
                black_box(frequency.find_frequency(black_box(word))),
                Some(number)
            );
        }
    }
    results.push(Measurement::new(
        "exact_frequency_lookup",
        started.elapsed(),
        (10 * frequency.frequency_count()) as u64,
        0,
    ));
    results
}

fn corpus_measurement(
    image: &Image<'_>,
    frequency: &Image<'_>,
    lookup: &Lookup<'_, '_>,
    name: &str,
    text: &str,
    threshold: u32,
) -> Measurement {
    let started = Instant::now();
    let mut tokens = 0;
    let mut bytes = 0;
    for token in text
        .split(|c: char| !c.is_ascii_alphabetic())
        .filter(|s| !s.is_empty())
    {
        tokens += 1;
        let token = black_box(token);
        if threshold != 0
            && frequency
                .find_frequency(token)
                .is_some_and(|number| number <= threshold)
        {
            continue;
        }
        let output: Option<String> = lookup
            .find(token)
            .and_then(|index| image.field(index, Field::Ips))
            .map(str::to_owned);
        bytes += output.as_ref().map_or(0, |value| value.len() as u64);
        black_box(output);
    }
    Measurement::new(
        format!("ascii_exact_ips_layout_{name}_skip_{threshold}"),
        started.elapsed(),
        tokens,
        bytes,
    )
}
