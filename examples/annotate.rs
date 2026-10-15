//! Annotation usage; currently exits with the skeleton's explicit unimplemented error.

fn main() -> lingose::Result<()> {
    let text = "Abandon the book.";
    println!("{}", lingose::annotate_ips(text)?);
    println!("{}", lingose::annotate_ips_with_skip_top(text, 1000)?);
    Ok(())
}
