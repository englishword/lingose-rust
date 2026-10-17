//! Generated from the pinned installed Python oracle; do not edit by hand.
//! P0 fixture SHA-256: 6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1
//! Reference baseline SHA-256: 9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01
//! Installed annotation.py SHA-256: 76355b9a0d71882f8407640740865529744e8eb9c6400081a0f764188bd4cbfc
//! Oracle: CPython 3.12.4 / Unicode 15.0.0; source bytes 14266.
//! Canonical vector payload SHA-256: 777ac33c0660631442e44c8cb0671a86e3c7b61f48386e94b44d869ff143d4b6

#[test]
fn pinned_python_direct_annotation_outputs_match_public_default_and_zero_threshold() {
    let cases: &[(&str, &str, &str)] = &[
        (
            "snapshot-0217",
            "Apple APPLE aPpLe May may US us iPhone McDonald",
            "Apple APPLE aPpLe M\u{101}y m\u{101}y \u{db}S \u{fb}s \u{12b}Ph\u{14d}ne [McDonald]",
        ),
        (
            "snapshot-0220",
            "present record address largely",
            "pr\u{117}\u{1e61}ent record \u{e5}ddress l\u{e0}rg\u{1d556}l\u{1e8f}",
        ),
        (
            "snapshot-0235",
            "WHALE WHIM YUM w\u{304} \u{1d559} e\u{30a}",
            "WH\u{100}LE W\u{210d}IM Y\u{db}M w\u{304} \u{1d559} e\u{30a}",
        ),
        (
            "snapshot-0241",
            "caf\u{e9} apple123 \u{4e2d}\u{6587}apple \u{4e2d}\u{6587}\t123 \u{e9} e\u{301}\n\u{1f600}",
            "caf\u{e9} apple123 \u{4e2d}\u{6587}apple \u{4e2d}\u{6587}\t123 \u{e9} e\u{301}\n\u{1f600}",
        ),
        ("snapshot-0250", "", ""),
        (
            "direct-curated-01",
            " \tApple,\r\nAPPLE! aPpLe? [book] \u{1f600} \u{4e2d}\u{6587} 123 e\u{301}  ",
            " \tApple,\r\nAPPLE! aPpLe? [book] \u{1f600} \u{4e2d}\u{6587} 123 e\u{301}  ",
        ),
        (
            "direct-curated-02",
            "unknownwordzz qzqxzz Zzqxxx",
            "[unknownwordzz] [qzqxzz] [Zzqxxx]",
        ),
        (
            "direct-curated-03",
            "may MAY mAy US us",
            "m\u{101}y M\u{100}Y m\u{100}y \u{db}S \u{fb}s",
        ),
        (
            "direct-curated-04",
            "Abandon ABANDON aBaNdOn\tWHALE Whim yum",
            "\u{c5}bando\u{30a}n \u{c5}BANDO\u{30a}N \u{e5}BaNdO\u{30a}n\tWH\u{100}LE W\u{1d559}im y\u{fb}m",
        ),
        (
            "direct-curated-05",
            "apple\u{2019} APPLE' 'book' \u{2018}book\u{2019}",
            "apple\u{2019} APPLE' 'book' \u{2018}book\u{2019}",
        ),
        (
            "direct-curated-06",
            "-apple apple- apple--book",
            "-apple apple- apple--book",
        ),
        (
            "direct-curated-07",
            "ma'am MA'AM Ma\u{2019}Am o\u{2019}clock O\u{2019}CLOCK first-rate FIRST-RATE ice-cream",
            "ma'\u{1d552}m MA'\u{1d538}M Ma\u{2019}\u{1d538}m o\u{30a}\u{2019}clock O\u{30a}\u{2019}CLOCK fi\u{30a}rst-r\u{101}te FI\u{30a}RST-R\u{100}TE \u{12b}c\u{1d556}-cr\u{113}am",
        ),
        (
            "direct-curated-08",
            "a-1; 12-apple; a-\u{4e2d}\u{6587}; 1-apple; x\u{b2}apple; a\u{903}b; a\u{20dd}b",
            "\u{e5}-1; 12-apple; a-\u{4e2d}\u{6587}; 1-apple; x\u{b2}apple; a\u{903}b; a\u{20dd}b",
        ),
        (
            "direct-curated-09",
            "\u{4e2d}\u{6587} 123 \u{e9} e\u{301} \u{1d559} w\u{304} \u{1f600}",
            "\u{4e2d}\u{6587} 123 \u{e9} e\u{301} \u{1d559} w\u{304} \u{1f600}",
        ),
        (
            "direct-curated-10",
            "\t\r\n\u{1c}\u{85}\u{2028}\u{2029}  ",
            "\t\r\n\u{1c}\u{85}\u{2028}\u{2029}  ",
        ),
    ];
    for &(identifier, text, expected) in cases {
        assert_eq!(
            lingose::annotate_ips(text).unwrap(),
            expected,
            "{identifier}"
        );
        assert_eq!(
            lingose::annotate_ips_skip(text, 0).unwrap(),
            expected,
            "{identifier}/zero"
        );
    }
}
