//! Context, compound annotation and inclusive original-NUMBER frequency filtering.

fn main() -> lingose::Result<()> {
    let text = "Abandon the book.\nTHE apple, the hour; doesn't study.\nsecond-unknownwordzz 中文";
    println!("{}", lingose::annotate_ips(text)?);
    println!("{}", lingose::annotate_ips_with_skip_top(text, 1000)?);
    assert_eq!(lingose::annotate_ips("中文 123")?, "中文 123");
    Ok(())
}
