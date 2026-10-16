//! Offline pronunciation, morphology, root and meaning queries.

fn main() -> lingose::Result<()> {
    println!("IPA: {:?}", lingose::ipa("apple")?);
    println!("IPS: {:?}", lingose::ips("running")?);
    println!("ISM: {:?}", lingose::ism("running")?);
    println!("IPSM: {:?}", lingose::ipsm("running")?);
    println!("Root: {:?}", lingose::root_lemma("running")?);
    println!("English: {:?}", lingose::meaning("apple")?);
    println!("Chinese: {:?}", lingose::meaning_with_lang("apple", "zh")?);
    Ok(())
}
