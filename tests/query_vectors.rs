//! Generated from frozen P0 snapshot outputs; do not edit by hand.
//! Source SHA-256: 6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1

#[test]
fn p0_snapshot_simple_queries_match_python() {
    assert_eq!(
        lingose::IPA("apple").unwrap(),
        vec![String::from("\u{e6}p\u{259}l")]
    );
    assert_eq!(lingose::IPS("apple").unwrap(), vec![String::from("apple")]);
    assert_eq!(lingose::ISM("apple").unwrap(), Some(String::from("app-le")));
    assert_eq!(
        lingose::IPSM("apple").unwrap(),
        vec![String::from("app-le")]
    );
    assert_eq!(
        lingose::root_lemma("apple").unwrap(),
        Some(String::from("ap"))
    );
    assert_eq!(
        lingose::meaning("apple").unwrap(),
        Some(String::from(
            "n. fruit with red or yellow or green skin and sweet to tart crisp whitish flesh"
        ))
    );
    assert_eq!(
        lingose::IPA("running").unwrap(),
        vec![String::from("r\u{28c}n\u{26a}\u{14b}")]
    );
    assert_eq!(
        lingose::IPS("running").unwrap(),
        vec![String::from("r\u{fb}nning")]
    );
    assert_eq!(
        lingose::ISM("running").unwrap(),
        Some(String::from("runn-ing"))
    );
    assert_eq!(
        lingose::IPSM("running").unwrap(),
        vec![String::from("r\u{fb}nn-ing")]
    );
    assert_eq!(
        lingose::root_lemma("running").unwrap(),
        Some(String::from("run"))
    );
    assert_eq!(
        lingose::meaning("running").unwrap(),
        Some(String::from(
            "n. the act or state of moving fast on foot\na. happening continuously; in operation"
        ))
    );
    assert_eq!(
        lingose::IPA("Apple").unwrap(),
        vec![String::from("\u{e6}p\u{259}l")]
    );
    assert_eq!(lingose::IPS("Apple").unwrap(), vec![String::from("apple")]);
    assert_eq!(lingose::ISM("Apple").unwrap(), Some(String::from("app-le")));
    assert_eq!(
        lingose::IPSM("Apple").unwrap(),
        vec![String::from("app-le")]
    );
    assert_eq!(
        lingose::root_lemma("Apple").unwrap(),
        Some(String::from("ap"))
    );
    assert_eq!(
        lingose::meaning("Apple").unwrap(),
        Some(String::from(
            "n. fruit with red or yellow or green skin and sweet to tart crisp whitish flesh"
        ))
    );
    assert_eq!(lingose::IPA("APPLE").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::IPS("APPLE").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::ISM("APPLE").unwrap(), None);
    assert_eq!(lingose::IPSM("APPLE").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::root_lemma("APPLE").unwrap(), None);
    assert_eq!(lingose::meaning("APPLE").unwrap(), None);
    assert_eq!(
        lingose::IPA("May").unwrap(),
        vec![String::from("me\u{26a}")]
    );
    assert_eq!(
        lingose::IPS("May").unwrap(),
        vec![String::from("M\u{101}y")]
    );
    assert_eq!(lingose::ISM("May").unwrap(), Some(String::from("May")));
    assert_eq!(
        lingose::IPSM("May").unwrap(),
        vec![String::from("M\u{101}y")]
    );
    assert_eq!(
        lingose::root_lemma("May").unwrap(),
        Some(String::from("may"))
    );
    assert_eq!(
        lingose::meaning("May").unwrap(),
        Some(String::from(
            "aux. expressing possibility or permission\nn. the fifth month of the year"
        ))
    );
    assert_eq!(
        lingose::IPA("may").unwrap(),
        vec![String::from("me\u{26a}")]
    );
    assert_eq!(
        lingose::IPS("may").unwrap(),
        vec![String::from("m\u{101}y")]
    );
    assert_eq!(lingose::ISM("may").unwrap(), Some(String::from("may")));
    assert_eq!(
        lingose::IPSM("may").unwrap(),
        vec![String::from("m\u{101}y")]
    );
    assert_eq!(
        lingose::root_lemma("may").unwrap(),
        Some(String::from("may"))
    );
    assert_eq!(
        lingose::meaning("may").unwrap(),
        Some(String::from(
            "aux. expressing possibility or permission\nn. the fifth month of the year"
        ))
    );
    assert_eq!(lingose::IPA("US").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::IPS("US").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::ISM("US").unwrap(), None);
    assert_eq!(lingose::IPSM("US").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::root_lemma("US").unwrap(), None);
    assert_eq!(lingose::meaning("US").unwrap(), None);
    assert_eq!(lingose::IPA("us").unwrap(), vec![String::from("\u{28c}s")]);
    assert_eq!(lingose::IPS("us").unwrap(), vec![String::from("\u{fb}s")]);
    assert_eq!(lingose::ISM("us").unwrap(), Some(String::from("us")));
    assert_eq!(lingose::IPSM("us").unwrap(), vec![String::from("\u{fb}s")]);
    assert_eq!(lingose::root_lemma("us").unwrap(), Some(String::from("us")));
    assert_eq!(
        lingose::meaning("us").unwrap(),
        Some(String::from("pron. objective case of we"))
    );
    assert_eq!(lingose::IPA("iPhone").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::IPS("iPhone").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::ISM("iPhone").unwrap(), None);
    assert_eq!(lingose::IPSM("iPhone").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::root_lemma("iPhone").unwrap(), None);
    assert_eq!(lingose::meaning("iPhone").unwrap(), None);
    assert_eq!(lingose::IPA("McDonald").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::IPS("McDonald").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::ISM("McDonald").unwrap(), None);
    assert_eq!(lingose::IPSM("McDonald").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::root_lemma("McDonald").unwrap(), None);
    assert_eq!(lingose::meaning("McDonald").unwrap(), None);
    assert_eq!(
        lingose::IPA("present").unwrap(),
        vec![String::from("prez\u{259}nt")]
    );
    assert_eq!(
        lingose::IPS("present").unwrap(),
        vec![String::from("pr\u{117}\u{1e61}ent")]
    );
    assert_eq!(
        lingose::ISM("present").unwrap(),
        Some(String::from("pre-sent"))
    );
    assert_eq!(
        lingose::IPSM("present").unwrap(),
        vec![String::from("pr\u{117}-\u{1e61}ent")]
    );
    assert_eq!(
        lingose::root_lemma("present").unwrap(),
        Some(String::from("sent"))
    );
    assert_eq!(
        lingose::meaning("present").unwrap(),
        Some(String::from(
            "a. existing or occurring at this time; current\nn. the period of time now occurring\nvt. to give something to someone; to show or offer something for others to consider"
        ))
    );
    assert_eq!(
        lingose::IPA("largely").unwrap(),
        vec![String::from("l\u{251}\u{2d0}d\u{292}li")]
    );
    assert_eq!(
        lingose::IPS("largely").unwrap(),
        vec![String::from("l\u{e0}rg\u{1d556}l\u{1e8f}")]
    );
    assert_eq!(
        lingose::ISM("largely").unwrap(),
        Some(String::from("large-ly"))
    );
    assert_eq!(
        lingose::IPSM("largely").unwrap(),
        vec![String::from("l\u{e0}rg\u{1d556}-l\u{1e8f}")]
    );
    assert_eq!(
        lingose::root_lemma("largely").unwrap(),
        Some(String::from("large"))
    );
    assert_eq!(
        lingose::meaning("largely").unwrap(),
        Some(String::from("adv. to a great extent; on the whole; mostly"))
    );
    assert_eq!(
        lingose::IPA("Marxism").unwrap(),
        vec![String::from("m\u{251}\u{2d0}ks\u{26a}s\u{26a}m")]
    );
    assert_eq!(
        lingose::IPS("Marxism").unwrap(),
        vec![String::from("M\u{e0}rxi\u{1e61}m")]
    );
    assert_eq!(
        lingose::ISM("Marxism").unwrap(),
        Some(String::from("marx-ism"))
    );
    assert_eq!(lingose::IPSM("Marxism").unwrap(), Vec::<String>::new());
    assert_eq!(
        lingose::root_lemma("Marxism").unwrap(),
        Some(String::from("marx"))
    );
    assert_eq!(
        lingose::meaning("Marxism").unwrap(),
        Some(String::from(
            "n. the political and economic theories of Karl Marx"
        ))
    );
    assert_eq!(lingose::IPA("has").unwrap(), vec![String::from("h\u{e6}z")]);
    assert_eq!(
        lingose::IPS("has").unwrap(),
        vec![String::from("ha\u{1e61}")]
    );
    assert_eq!(lingose::ISM("has").unwrap(), Some(String::from("has")));
    assert_eq!(
        lingose::IPSM("has").unwrap(),
        vec![String::from("ha\u{1e61}")]
    );
    assert_eq!(lingose::root_lemma("has").unwrap(), None);
    assert_eq!(
        lingose::meaning("has").unwrap(),
        Some(String::from("v. third person singular present of \"have\""))
    );
    assert_eq!(lingose::IPA("sh").unwrap(), vec![String::from("\u{283}")]);
    assert_eq!(lingose::IPS("sh").unwrap(), vec![String::from("sh")]);
    assert_eq!(lingose::ISM("sh").unwrap(), Some(String::from("sh")));
    assert_eq!(lingose::IPSM("sh").unwrap(), vec![String::from("sh")]);
    assert_eq!(lingose::root_lemma("sh").unwrap(), None);
    assert_eq!(
        lingose::meaning("sh").unwrap(),
        Some(String::from("int. be quiet!"))
    );
    assert_eq!(lingose::IPA("unknownwordzz").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::IPS("unknownwordzz").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::ISM("unknownwordzz").unwrap(), None);
    assert_eq!(
        lingose::IPSM("unknownwordzz").unwrap(),
        Vec::<String>::new()
    );
    assert_eq!(lingose::root_lemma("unknownwordzz").unwrap(), None);
    assert_eq!(lingose::meaning("unknownwordzz").unwrap(), None);
    assert_eq!(
        lingose::ipa("apple").unwrap(),
        vec![String::from("\u{e6}p\u{259}l")]
    );
    assert_eq!(
        lingose::ipa("running").unwrap(),
        vec![String::from("r\u{28c}n\u{26a}\u{14b}")]
    );
    assert_eq!(lingose::ipa("unknownwordzz").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::ips("apple").unwrap(), vec![String::from("apple")]);
    assert_eq!(
        lingose::ips("running").unwrap(),
        vec![String::from("r\u{fb}nning")]
    );
    assert_eq!(lingose::ips("unknownwordzz").unwrap(), Vec::<String>::new());
    assert_eq!(lingose::ism("apple").unwrap(), Some(String::from("app-le")));
    assert_eq!(
        lingose::ism("running").unwrap(),
        Some(String::from("runn-ing"))
    );
    assert_eq!(lingose::ism("unknownwordzz").unwrap(), None);
    assert_eq!(
        lingose::ipsm("apple").unwrap(),
        vec![String::from("app-le")]
    );
    assert_eq!(
        lingose::ipsm("running").unwrap(),
        vec![String::from("r\u{fb}nn-ing")]
    );
    assert_eq!(
        lingose::ipsm("unknownwordzz").unwrap(),
        Vec::<String>::new()
    );
    assert_eq!(
        lingose::meaning_with_lang("apple", "zh").unwrap(),
        Some(String::from("n. \u{82f9}\u{679c}, \u{5bb6}\u{4f19}"))
    );
    assert_eq!(
        lingose::meaning_with_lang("May", "zh").unwrap(),
        Some(String::from(
            "n. \u{4e94}\u{6708}\naux. \u{613f}\u{80fd}, \u{53ef}\u{4ee5}, \u{613f}\u{610f}"
        ))
    );
    assert_eq!(
        lingose::meaning_with_lang("may", "zh").unwrap(),
        Some(String::from(
            "n. \u{4e94}\u{6708}\naux. \u{613f}\u{80fd}, \u{53ef}\u{4ee5}, \u{613f}\u{610f}"
        ))
    );
    assert_eq!(
        lingose::meaning_with_lang("unknownwordzz", "zh").unwrap(),
        None
    );
}
