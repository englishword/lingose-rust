//! Query usage; currently exits with the skeleton's explicit unimplemented error.

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
    println!("CET4 list: {:?}", lingose::kind_list()?);
    println!("IELTS list: {:?}", lingose::kind_list_with_label("IELTS")?);
    println!("Labels: {:?}", lingose::labels()?);
    Ok(())
}
