//! Context and compound annotation; positive frequency filtering follows in P3.3.

fn main() -> lingose::Result<()> {
    let text = "Abandon the book.\nTHE apple, the hour; doesn't study.\nsecond-unknownwordzz 中文";
    println!("{}", lingose::annotate_ips(text)?);
    assert_eq!(lingose::annotate_ips("中文 123")?, "中文 123");
    Ok(())
}
