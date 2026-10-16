//! Offline word queries, category membership and complete ordered word lists.

fn main() -> lingose::Result<()> {
    println!("IPA: {:?}", lingose::ipa("apple")?);
    println!("IPS: {:?}", lingose::ips("running")?);
    println!("ISM: {:?}", lingose::ism("running")?);
    println!("IPSM: {:?}", lingose::ipsm("running")?);
    println!("Root: {:?}", lingose::root_lemma("running")?);
    println!("English: {:?}", lingose::meaning("apple")?);
    println!("Chinese: {:?}", lingose::meaning_with_lang("apple", "zh")?);
    println!("CET4: {}", lingose::kind("apple")?);
    println!("IELTS: {}", lingose::kind_with_label("apple", "IELTS")?);
    println!("CET4 words: {}", lingose::kind_list()?.len());
    println!(
        "IELTS words: {}",
        lingose::kind_list_with_label("IELTS")?.len()
    );
    println!("Labels: {:?}", lingose::labels()?);
    Ok(())
}
