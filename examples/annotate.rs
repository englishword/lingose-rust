//! Basic direct annotation; context and frequency filtering are still in development.

fn main() -> lingose::Result<()> {
    let text = "Abandon apple.\nAPPLE unknownwordzz 中文";
    println!("{}", lingose::annotate_ips(text)?);
    assert_eq!(lingose::annotate_ips("中文 123")?, "中文 123");
    Ok(())
}
