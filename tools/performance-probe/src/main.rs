//! Development-only public API benchmark. No private loader or layout shortcuts.

use std::fs;
use std::hint::black_box;
use std::io::{self, Read, Write};
use std::path::Path;
use std::sync::{Arc, Barrier};
use std::time::Instant;

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

fn metric(name: &str, elapsed: std::time::Duration, operations: usize) {
    println!("METRIC\t{name}\t{}\t{operations}", elapsed.as_nanos());
}

fn hold(stage: &str) -> Result<()> {
    println!("HOLD\t{stage}");
    io::stdout().flush()?;
    let mut line = String::new();
    if io::stdin().read_line(&mut line)? == 0 {
        return Err("memory handshake ended early".into());
    }
    Ok(())
}

fn strings(input: &mut impl Read) -> Result<Vec<String>> {
    fn number(input: &mut impl Read) -> io::Result<u32> {
        let mut bytes = [0; 4];
        input.read_exact(&mut bytes)?;
        Ok(u32::from_le_bytes(bytes))
    }
    (0..number(input)?)
        .map(|_| {
            let mut bytes = vec![0; number(input)? as usize];
            input.read_exact(&mut bytes)?;
            Ok(String::from_utf8(bytes)?)
        })
        .collect()
}

fn inputs(directory: &Path) -> Result<(Vec<String>, Vec<String>, Vec<String>)> {
    let mut input = fs::File::open(directory.join("queries.bin"))?;
    let words = strings(&mut input)?;
    let mixed = strings(&mut input)?;
    let labels = strings(&mut input)?;
    if input.read(&mut [0])? != 0 || words.len() != 50_335 || labels.len() != 24 {
        return Err("query workload shape drift".into());
    }
    Ok((words, mixed, labels))
}

fn query<T>(
    name: &str,
    words: &[String],
    rounds: usize,
    call: impl Fn(&str) -> lingose::Result<T>,
) {
    let started = Instant::now();
    for _ in 0..rounds {
        for word in words {
            // Includes parameter/case checks and destruction of the entire owned result.
            drop(black_box(call(black_box(word)).unwrap()));
        }
    }
    metric(name, started.elapsed(), words.len() * rounds);
}

fn queries(directory: &Path) -> Result<()> {
    let (words, mixed, labels) = inputs(directory)?;
    assert_eq!(lingose::labels()?, labels);
    for (group, values, rounds) in [("exact", &words, 2), ("mixed", &mixed, 2_000)] {
        query(&format!("ipa_{group}"), values, rounds, lingose::ipa);
        query(&format!("ips_{group}"), values, rounds, lingose::ips);
        query(&format!("ism_{group}"), values, rounds, lingose::ism);
        query(&format!("ipsm_{group}"), values, rounds, lingose::ipsm);
        query(
            &format!("root_lemma_{group}"),
            values,
            rounds,
            lingose::root_lemma,
        );
        query(
            &format!("meaning_{group}"),
            values,
            rounds,
            lingose::meaning,
        );
        query(&format!("meaning_en_{group}"), values, rounds, |word| {
            lingose::meaning_with_lang(word, "en")
        });
        query(&format!("meaning_zh_{group}"), values, rounds, |word| {
            lingose::meaning_with_lang(word, "zh")
        });
        query(&format!("kind_{group}"), values, rounds, lingose::kind);
        for label in &labels {
            query(&format!("kind_{label}_{group}"), values, rounds, |word| {
                lingose::kind_with_label(word, label)
            });
        }
    }
    let started = Instant::now();
    for _ in 0..10_000 {
        drop(black_box(lingose::labels()?));
    }
    metric("labels_us", started.elapsed(), 10_000);
    let started = Instant::now();
    for _ in 0..10 {
        let mut members = 0;
        for label in &labels {
            let list = lingose::kind_list_with_label(black_box(label))?;
            members += list.len();
            drop(black_box(list));
        }
        assert_eq!(members, 209_759);
    }
    metric("all_kind_lists_ms", started.elapsed(), 10);
    let started = Instant::now();
    for _ in 0..100 {
        drop(black_box(lingose::kind_list()?));
    }
    metric("default_kind_list_ms", started.elapsed(), 100);
    Ok(())
}

fn annotation(directory: &Path, words: usize, skip: i64, memory: bool) -> Result<()> {
    // No expected output buffer is loaded in the measured memory process.
    let text = fs::read_to_string(directory.join(format!("corpus-{words}.txt")))?;
    let started = Instant::now();
    let output = lingose::annotate_ips_skip(black_box(&text), skip)?;
    let elapsed = started.elapsed();
    metric(&format!("annotation_{words}_{skip}_ms"), elapsed, 1);
    if memory {
        hold("annotation-output-retained")?;
    }
    let expected =
        fs::read_to_string(directory.join(format!("reference-{words}-skip-{skip}.txt")))?;
    assert_eq!(
        output, expected,
        "complete Python annotation output differs"
    );
    black_box((&text, &output));
    println!("VERIFIED\t{words}\t{skip}\t{}", output.len());
    Ok(())
}

fn warm(directory: &Path) -> Result<()> {
    // Each measured sample is a new process; initialize both resources before hot calls.
    black_box(lingose::annotate_ips_skip("the apple", 1)?);
    queries(directory)?;
    for words in [10_000, 100_000] {
        for skip in [0, 1_000, 5_062] {
            annotation(directory, words, skip, false)?;
        }
    }
    Ok(())
}

fn concurrent(directory: &Path) -> Result<()> {
    let text = fs::read_to_string(directory.join("corpus-100000.txt"))?;
    let expected: Vec<_> = [0, 1_000, 5_062]
        .into_iter()
        .map(|skip| fs::read_to_string(directory.join(format!("reference-100000-skip-{skip}.txt"))))
        .collect::<io::Result<_>>()?;
    let barrier = Arc::new(Barrier::new(8));
    let started = Instant::now();
    std::thread::scope(|scope| {
        let handles: Vec<_> = (0..8)
            .map(|index| {
                let barrier = Arc::clone(&barrier);
                let text = &text;
                let expected = &expected;
                scope.spawn(move || {
                    barrier.wait();
                    let output =
                        lingose::annotate_ips_skip(text, [0, 1_000, 5_062][index % 3]).unwrap();
                    assert_eq!(output, expected[index % 3]);
                    assert!(!lingose::ipa("apple").unwrap().is_empty());
                    assert_eq!(lingose::labels().unwrap().len(), 24);
                    black_box(output);
                })
            })
            .collect();
        for handle in handles {
            handle.join().unwrap();
        }
    });
    metric("concurrent_8_complete_annotations_ms", started.elapsed(), 1);
    Ok(())
}

fn main() -> Result<()> {
    let arguments: Vec<_> = std::env::args().collect();
    let mode = arguments.get(1).ok_or("expected mode")?.as_str();
    match mode {
        "control" => println!("CONTROL"),
        "cold" => {
            let started = Instant::now();
            let result = lingose::ips("apple")?;
            metric("lexicon_initialization_ms", started.elapsed(), 1);
            assert!(!result.is_empty());
        }
        "frequency" => {
            black_box(lingose::labels()?);
            let started = Instant::now();
            let result = lingose::annotate_ips_skip("the", 1)?;
            metric("frequency_initialization_ms", started.elapsed(), 1);
            black_box(result);
        }
        "loaded-memory" => {
            hold("before-load")?;
            black_box(lingose::annotate_ips_skip("the apple", 1)?);
            hold("both-resources-loaded")?;
        }
        "warm" => warm(Path::new(
            arguments.get(2).ok_or("expected input directory")?,
        ))?,
        "concurrent" => concurrent(Path::new(
            arguments.get(2).ok_or("expected input directory")?,
        ))?,
        "annotation-memory" => {
            hold("before-load")?;
            let directory = Path::new(arguments.get(2).ok_or("expected input directory")?);
            let skip = arguments.get(3).ok_or("expected threshold")?.parse()?;
            annotation(directory, 100_000, skip, true)?;
        }
        "long-word" => {
            black_box(lingose::ips("apple")?);
            for repeats in [256, 1_024, 4_096] {
                let text = format!("foo{}", "n't".repeat(repeats));
                let started = Instant::now();
                let output = lingose::annotate_ips(&text)?;
                metric(&format!("long_word_{repeats}_ms"), started.elapsed(), 1);
                // The saved foo notation is identical to its spelling; suffixes remain verbatim.
                assert_eq!(output, text);
            }
        }
        _ => return Err("unknown performance mode".into()),
    }
    Ok(())
}
