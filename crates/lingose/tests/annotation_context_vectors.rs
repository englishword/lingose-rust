//! Generated from the pinned installed Python oracle; do not edit by hand.
//! P0 fixture SHA-256: 6b0eebaef3c8f414e1c65a56dd82949a155981cd41d24fb69c9564f54af3f0b1
//! Reference baseline SHA-256: 9891742574b4c3c5ef5e420cb17d380094601803cddfc73e55062b7fccd54f01
//! Installed annotation.py SHA-256: 76355b9a0d71882f8407640740865529744e8eb9c6400081a0f764188bd4cbfc
//! Oracle: CPython 3.12.4 / Unicode 15.0.0; source bytes 14266.
//! Canonical vector payload SHA-256: b105f933aa3e88b75f1302fd200b89d38cbb77d76bcd7c3431f1f576c9372a9e

#[test]
fn pinned_python_complete_zero_threshold_annotation_outputs_match() {
    let cases: &[(&str, &str, &str)] = &[
        (
            "snapshot-0208",
            "Abandon the book.",
            "\u{c5}bando\u{30a}n \u{1e6b}he\u{30a} book.",
        ),
        (
            "snapshot-0211",
            "the apple THE book The hour the university the",
            "\u{1e6b}h\u{113} apple \u{1e6a}HE\u{30a} book \u{1e6a}he\u{30a} \u{1d559}\u{f2}ur \u{1e6b}h\u{113} \u{16b}nive\u{30a}rsit\u{1e8f} \u{1e6b}he\u{30a}",
        ),
        (
            "snapshot-0214",
            "the, apple; the\napple; the\n\napple",
            "\u{1e6b}he\u{30a}, apple; \u{1e6b}h\u{113}\napple; \u{1e6b}he\u{30a}\n\napple",
        ),
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
            "snapshot-0223",
            "don't doesn't aren't I'm you're o'clock don\u{2019}t doesn\u{2019}t aren\u{2019}t I\u{2019}m you\u{2019}re o\u{2019}clock",
            "don't d\u{f4}\u{1d556}\u{1e61}n't \u{e0}r\u{1d556}n't I'm yo\u{16b}'re o\u{30a}'clock don\u{2019}t d\u{f4}\u{1d556}\u{1e61}n\u{2019}t \u{e0}r\u{1d556}n\u{2019}t I\u{2019}m yo\u{16b}\u{2019}re o\u{30a}\u{2019}clock",
        ),
        (
            "snapshot-0226",
            "walks boxes baked baking studies studied stopped stopping plays tying",
            "w\u{e3}lks box\u{117}\u{1e61} b\u{101}k\u{1d556}\u{1e0b} b\u{101}king st\u{fb}d\u{129}\u{1d556}\u{1e61} st\u{fb}d\u{129}\u{1d556}d stopp\u{1d556}\u{1e0b} stopping pl\u{101}y\u{1e61} t\u{233}ing",
        ),
        (
            "snapshot-0229",
            "ageing singeing tingeing queueing busing singing axes is",
            "\u{101}g\u{117}ing singeing tingeing q\u{1d566}e\u{16b}eing b\u{fb}sing singing axes i\u{1e61}",
        ),
        (
            "snapshot-0232",
            "first-rate second-rate second-puldsm pending-compound",
            "fi\u{30a}rst-r\u{101}te seco\u{30a}nd-r\u{101}te seco\u{30a}nd-[puldsm] pending-co\u{30a}mp\u{f2}und",
        ),
        (
            "snapshot-0235",
            "WHALE WHIM YUM w\u{304} \u{1d559} e\u{30a}",
            "WH\u{100}LE W\u{210d}IM Y\u{db}M w\u{304} \u{1d559} e\u{30a}",
        ),
        (
            "snapshot-0238",
            "unknownwordzz unknown-wordzz who'unknown",
            "[unknownwordzz] \u{fb}n\u{1d55c}n\u{14d}wn-[wordzz] \u{1d568}h\u{f5}'unknown",
        ),
        (
            "snapshot-0241",
            "caf\u{e9} apple123 \u{4e2d}\u{6587}apple \u{4e2d}\u{6587}\t123 \u{e9} e\u{301}\n\u{1f600}",
            "caf\u{e9} apple123 \u{4e2d}\u{6587}apple \u{4e2d}\u{6587}\t123 \u{e9} e\u{301}\n\u{1f600}",
        ),
        (
            "snapshot-0244",
            "Messrs. p.m. a lot a lottery puldsm",
            "[Messrs]. [p].m. \u{e5} lot \u{e5} lotte\u{30a}r\u{1e8f} [puldsm]",
        ),
        (
            "snapshot-0247",
            "  Abandon\t  the (apple).\n\nThe book.  ",
            "  \u{c5}bando\u{30a}n\t  \u{1e6b}h\u{113} (apple).\n\n\u{1e6a}he\u{30a} book.  ",
        ),
        ("snapshot-0250", "", ""),
        (
            "snapshot-0253",
            "Abandon the book.",
            "\u{c5}bando\u{30a}n \u{1e6b}he\u{30a} book.",
        ),
        (
            "context-curated-001",
            "the apple The Apple THE APPLE tHe aPpLe the book The hour THE university the unknownwordzz the",
            "\u{1e6b}h\u{113} apple \u{1e6a}h\u{113} Apple \u{1e6a}H\u{112} APPLE \u{1e6b}H\u{113} aPpLe \u{1e6b}he\u{30a} book \u{1e6a}he\u{30a} \u{1d559}\u{f2}ur \u{1e6a}H\u{112} \u{16b}nive\u{30a}rsit\u{1e8f} \u{1e6b}h\u{113} [unknownwordzz] \u{1e6b}he\u{30a}",
        ),
        (
            "context-curated-002",
            "the \"apple\" the (apple) the [apple] the \u{2018}apple\u{2019} the \u{201c}apple\u{201d} the 'apple'",
            "\u{1e6b}h\u{113} \"apple\" \u{1e6b}h\u{113} (apple) \u{1e6b}h\u{113} [apple] \u{1e6b}h\u{113} \u{2018}apple\u{2019} \u{1e6b}h\u{113} \u{201c}apple\u{201d} \u{1e6b}h\u{113} 'apple'",
        ),
        (
            "context-curated-003",
            "the, apple; the. apple! the? apple: the\u{2014}apple the\u{2026}apple the{apple} the<apple>",
            "\u{1e6b}he\u{30a}, apple; \u{1e6b}he\u{30a}. apple! \u{1e6b}he\u{30a}? apple: \u{1e6b}he\u{30a}\u{2014}apple \u{1e6b}he\u{30a}\u{2026}apple \u{1e6b}he\u{30a}{apple} \u{1e6b}he\u{30a}<apple>",
        ),
        (
            "context-curated-004",
            "the\napple the\n\napple the\n \t\napple the\r\napple the\r\n\r\napple the\r\rapple",
            "\u{1e6b}h\u{113}\napple \u{1e6b}he\u{30a}\n\napple \u{1e6b}he\u{30a}\n \t\napple \u{1e6b}h\u{113}\r\napple \u{1e6b}he\u{30a}\r\n\r\napple \u{1e6b}h\u{113}\r\rapple",
        ),
        (
            "context-curated-005",
            "the\n\"\napple the\n(\napple the\n\u{2018}\u{2019}\napple the\n[]\napple the\n \t\r\napple",
            "\u{1e6b}h\u{113}\n\"\napple \u{1e6b}h\u{113}\n(\napple \u{1e6b}h\u{113}\n\u{2018}\u{2019}\napple \u{1e6b}h\u{113}\n[]\napple \u{1e6b}he\u{30a}\n \t\r\napple",
        ),
        (
            "context-curated-006",
            "the \u{4e2d}\u{6587} apple the 123 apple the caf\u{e9} apple the e\u{301} apple the \u{1d552} apple the \u{1f600} apple",
            "\u{1e6b}he\u{30a} \u{4e2d}\u{6587} apple \u{1e6b}he\u{30a} 123 apple \u{1e6b}he\u{30a} caf\u{e9} apple \u{1e6b}he\u{30a} e\u{301} apple \u{1e6b}he\u{30a} \u{1d552} apple \u{1e6b}he\u{30a} \u{1f600} apple",
        ),
        (
            "context-curated-007",
            "the\u{4e2d}\u{6587} apple the123 apple the\u{e9} apple the\u{301} apple the\u{2014}\u{1f600}apple the\u{200b}apple",
            "the\u{4e2d}\u{6587} apple the123 apple the\u{e9} apple the\u{301} apple \u{1e6b}he\u{30a}\u{2014}\u{1f600}apple \u{1e6b}he\u{30a}\u{200b}apple",
        ),
        (
            "context-curated-008",
            "the-apple the-book the-hour the-unknownwordzz apple-the apple-the apple apple-the, apple",
            "\u{1e6b}h\u{113}-apple \u{1e6b}he\u{30a}-book \u{1e6b}he\u{30a}-\u{1d559}\u{f2}ur \u{1e6b}h\u{113}-[unknownwordzz] apple-\u{1e6b}h\u{113} apple-\u{1e6b}h\u{113} apple apple-\u{1e6b}he\u{30a}, apple",
        ),
        (
            "context-curated-009",
            "THE-APPLE The-Apple tHe-aPpLe the-the-apple the's apple the\u{2019}s apple THE\u{2019}S APPLE",
            "\u{1e6a}H\u{112}-APPLE \u{1e6a}h\u{113}-Apple \u{1e6b}H\u{113}-aPpLe \u{1e6b}he\u{30a}-\u{1e6b}h\u{113}-apple \u{1e6b}he\u{30a}'s apple \u{1e6b}he\u{30a}\u{2019}s apple \u{1e6a}HE\u{30a}\u{2019}S APPLE",
        ),
        (
            "context-curated-010",
            "the-apple's the-apple\u{2019}s THE-APPLE\u{2019}S the-unknownwordzz-book unknownwordzz-the-apple",
            "\u{1e6b}h\u{113}-apple's \u{1e6b}h\u{113}-apple\u{2019}s \u{1e6a}H\u{112}-APPLE\u{2019}S \u{1e6b}h\u{113}-[unknownwordzz]-book [unknownwordzz]-\u{1e6b}h\u{113}-apple",
        ),
        (
            "context-curated-011",
            "don't doesn't aren't I'm you're o'clock DON\u{2019}T DOESN\u{2019}T AREN\u{2019}T I\u{2019}M YOU\u{2019}RE O\u{2019}CLOCK",
            "don't d\u{f4}\u{1d556}\u{1e61}n't \u{e0}r\u{1d556}n't I'm yo\u{16b}'re o\u{30a}'clock DON\u{2019}T D\u{d4}\u{1d53c}\u{1e60}N\u{2019}T \u{c0}R\u{1d53c}N\u{2019}T I\u{2019}M YO\u{16a}\u{2019}RE O\u{30a}\u{2019}CLOCK",
        ),
        (
            "context-curated-012",
            "doN't dOeSn\u{2019}T aReN't i'M YoU\u{2019}rE o\u{2019}ClOcK can't can\u{2019}t won't won\u{2019}t isn\u{2019}t shouldn\u{2019}t",
            "doN't d\u{d4}\u{1d556}\u{1e60}n\u{2019}T \u{e0}R\u{1d556}N't i'M Yo\u{16a}\u{2019}rE o\u{30a}\u{2019}ClOcK can't can\u{2019}t w\u{f4}n't w\u{f4}n\u{2019}t i\u{1e61}n\u{2019}t sho\u{16b}\u{1d55d}dn\u{2019}t",
        ),
        (
            "context-curated-013",
            "apple's APPLE\u{2019}S aPpLe\u{2019}s book\u{2019}s books\u{2019} walk's walks\u{2019} does'nt doesn't've doesn\u{2019}t\u{2019}ve",
            "apple's APPLE\u{2019}S aPpLe\u{2019}s book\u{2019}s books\u{2019} w\u{e3}lk's w\u{e3}lks\u{2019} d\u{f4}\u{1d556}\u{1e61}'nt [doesn't've] [doesn\u{2019}t\u{2019}ve]",
        ),
        (
            "context-curated-014",
            "a\u{2019}can\u{2019}t a'can't ca\u{2019}can\u{2019}t apple\u{2019}can\u{2019}t APPLE\u{2019}CAN\u{2019}T apple'unknown'can't unknown'can't",
            "\u{e5}\u{2019}can\u{2019}t \u{e5}'can't [ca\u{2019}can\u{2019}t] apple\u{2019}can\u{2019}t APPLE\u{2019}CAN\u{2019}T apple'unknown'can't \u{fb}n\u{1d55c}n\u{14d}wn'can't",
        ),
        (
            "context-curated-015",
            "apple-the\u{2019}s apple apple-the's apple second-the apple second-the, apple",
            "apple-\u{1e6b}he\u{30a}\u{2019}s apple apple-\u{1e6b}he\u{30a}'s apple seco\u{30a}nd-\u{1e6b}h\u{113} apple seco\u{30a}nd-\u{1e6b}he\u{30a}, apple",
        ),
        (
            "context-curated-016",
            "first-rate second-rate second-puldsm pending-compound SECOND-RATE Second-Rate second-apple-book",
            "fi\u{30a}rst-r\u{101}te seco\u{30a}nd-r\u{101}te seco\u{30a}nd-[puldsm] pending-co\u{30a}mp\u{f2}und SECO\u{30a}ND-R\u{100}TE Seco\u{30a}nd-R\u{101}te seco\u{30a}nd-apple-book",
        ),
        (
            "context-curated-017",
            "walks boxes baked baking studies studied stopped stopping plays tying WALKED BAKING STuDiED",
            "w\u{e3}lks box\u{117}\u{1e61} b\u{101}k\u{1d556}\u{1e0b} b\u{101}king st\u{fb}d\u{129}\u{1d556}\u{1e61} st\u{fb}d\u{129}\u{1d556}d stopp\u{1d556}\u{1e0b} stopping pl\u{101}y\u{1e61} t\u{233}ing W\u{c3}LK\u{1d53c}\u{1e0a} B\u{100}KING ST\u{fb}D\u{129}\u{1d53c}D",
        ),
        (
            "context-curated-018",
            "ageing aging singeing singing tingeing tinging queueing queuing busing bussing axes is",
            "\u{101}g\u{117}ing \u{101}ging singeing singing tingeing tinging q\u{1d566}e\u{16b}eing q\u{1d566}e\u{16b}ing b\u{fb}sing b\u{fb}ssing axes i\u{1e61}",
        ),
        (
            "context-curated-019",
            "dies dying lies lying ties tying cries crying tries trying copied copying studies studying",
            "d\u{12b}\u{1d556}\u{1e61} d\u{233}ing l\u{12b}\u{1d556}\u{1e61} l\u{233}ing t\u{12b}\u{1d556}\u{1e61} t\u{233}ing cr\u{12b}\u{1d556}\u{1e61} cr\u{233}ing tr\u{12b}\u{1d556}\u{1e61} tr\u{233}ing cop\u{129}\u{1d556}d cop\u{1e8f}ing st\u{fb}d\u{129}\u{1d556}\u{1e61} st\u{fb}d\u{1e8f}ing",
        ),
        (
            "context-curated-020",
            "hoping hopping planned planning visited visiting preferred preferring travelled traveling",
            "h\u{14d}ping hopping plann\u{1d556}d planning vi\u{1e61}it\u{117}d vi\u{1e61}iting pre\u{30a}fe\u{30a}rr\u{1d556}d pr\u{117}fe\u{30a}rring trave\u{30a}lled trave\u{30a}ling",
        ),
        (
            "context-curated-021",
            "buses BUSES BuSeS fixes FIXES glasses heroes potatoes goes does passes washes watches quizzes",
            "b\u{fb}s\u{117}\u{1e61} B\u{db}S\u{116}\u{1e60} B\u{fb}S\u{117}\u{1e60} fix\u{117}\u{1e61} FIX\u{116}\u{1e60} glass\u{1d556}\u{1e61} h\u{113}r\u{14d}\u{1d556}\u{1e61} po\u{30a}t\u{101}t\u{14d}\u{1d556}\u{1e61} g\u{14d}\u{1d556}\u{1e61} d\u{f4}\u{1d556}\u{1e61} pass\u{117}\u{1e61} w\u{e3}sh\u{117}\u{1e61} w\u{e3}tch\u{117}\u{1e61} [quizzes]",
        ),
        (
            "context-curated-022",
            "  The\t(APPLE),\r\nTHE [book].\n\nThe \u{2018}hour\u{2019}! [unknownwordzz] \u{1f600} \u{4e2d}\u{6587} 123  ",
            "  \u{1e6a}h\u{113}\t(APPLE),\r\n\u{1e6a}HE\u{30a} [book].\n\n\u{1e6a}he\u{30a} \u{2018}\u{1d559}\u{f2}ur\u{2019}! [[unknownwordzz]] \u{1f600} \u{4e2d}\u{6587} 123  ",
        ),
        (
            "context-curated-023",
            "the\tapple THE\tbook The\thour",
            "\u{1e6b}h\u{113}\tapple \u{1e6a}HE\u{30a}\tbook \u{1e6a}he\u{30a}\t\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-024",
            "the\napple THE\nbook The\nhour",
            "\u{1e6b}h\u{113}\napple \u{1e6a}HE\u{30a}\nbook \u{1e6a}he\u{30a}\n\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-025",
            "the\u{b}apple THE\u{b}book The\u{b}hour",
            "\u{1e6b}h\u{113}\u{b}apple \u{1e6a}HE\u{30a}\u{b}book \u{1e6a}he\u{30a}\u{b}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-026",
            "the\u{c}apple THE\u{c}book The\u{c}hour",
            "\u{1e6b}h\u{113}\u{c}apple \u{1e6a}HE\u{30a}\u{c}book \u{1e6a}he\u{30a}\u{c}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-027",
            "the\rapple THE\rbook The\rhour",
            "\u{1e6b}h\u{113}\rapple \u{1e6a}HE\u{30a}\rbook \u{1e6a}he\u{30a}\r\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-028",
            "the\u{1c}apple THE\u{1c}book The\u{1c}hour",
            "\u{1e6b}h\u{113}\u{1c}apple \u{1e6a}HE\u{30a}\u{1c}book \u{1e6a}he\u{30a}\u{1c}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-029",
            "the\u{1d}apple THE\u{1d}book The\u{1d}hour",
            "\u{1e6b}h\u{113}\u{1d}apple \u{1e6a}HE\u{30a}\u{1d}book \u{1e6a}he\u{30a}\u{1d}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-030",
            "the\u{1e}apple THE\u{1e}book The\u{1e}hour",
            "\u{1e6b}h\u{113}\u{1e}apple \u{1e6a}HE\u{30a}\u{1e}book \u{1e6a}he\u{30a}\u{1e}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-031",
            "the\u{1f}apple THE\u{1f}book The\u{1f}hour",
            "\u{1e6b}h\u{113}\u{1f}apple \u{1e6a}HE\u{30a}\u{1f}book \u{1e6a}he\u{30a}\u{1f}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-032",
            "the apple THE book The hour",
            "\u{1e6b}h\u{113} apple \u{1e6a}HE\u{30a} book \u{1e6a}he\u{30a} \u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-033",
            "the\u{85}apple THE\u{85}book The\u{85}hour",
            "\u{1e6b}h\u{113}\u{85}apple \u{1e6a}HE\u{30a}\u{85}book \u{1e6a}he\u{30a}\u{85}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-034",
            "the\u{a0}apple THE\u{a0}book The\u{a0}hour",
            "\u{1e6b}h\u{113}\u{a0}apple \u{1e6a}HE\u{30a}\u{a0}book \u{1e6a}he\u{30a}\u{a0}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-035",
            "the\u{1680}apple THE\u{1680}book The\u{1680}hour",
            "\u{1e6b}h\u{113}\u{1680}apple \u{1e6a}HE\u{30a}\u{1680}book \u{1e6a}he\u{30a}\u{1680}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-036",
            "the\u{2000}apple THE\u{2000}book The\u{2000}hour",
            "\u{1e6b}h\u{113}\u{2000}apple \u{1e6a}HE\u{30a}\u{2000}book \u{1e6a}he\u{30a}\u{2000}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-037",
            "the\u{2001}apple THE\u{2001}book The\u{2001}hour",
            "\u{1e6b}h\u{113}\u{2001}apple \u{1e6a}HE\u{30a}\u{2001}book \u{1e6a}he\u{30a}\u{2001}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-038",
            "the\u{2002}apple THE\u{2002}book The\u{2002}hour",
            "\u{1e6b}h\u{113}\u{2002}apple \u{1e6a}HE\u{30a}\u{2002}book \u{1e6a}he\u{30a}\u{2002}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-039",
            "the\u{2003}apple THE\u{2003}book The\u{2003}hour",
            "\u{1e6b}h\u{113}\u{2003}apple \u{1e6a}HE\u{30a}\u{2003}book \u{1e6a}he\u{30a}\u{2003}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-040",
            "the\u{2004}apple THE\u{2004}book The\u{2004}hour",
            "\u{1e6b}h\u{113}\u{2004}apple \u{1e6a}HE\u{30a}\u{2004}book \u{1e6a}he\u{30a}\u{2004}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-041",
            "the\u{2005}apple THE\u{2005}book The\u{2005}hour",
            "\u{1e6b}h\u{113}\u{2005}apple \u{1e6a}HE\u{30a}\u{2005}book \u{1e6a}he\u{30a}\u{2005}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-042",
            "the\u{2006}apple THE\u{2006}book The\u{2006}hour",
            "\u{1e6b}h\u{113}\u{2006}apple \u{1e6a}HE\u{30a}\u{2006}book \u{1e6a}he\u{30a}\u{2006}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-043",
            "the\u{2007}apple THE\u{2007}book The\u{2007}hour",
            "\u{1e6b}h\u{113}\u{2007}apple \u{1e6a}HE\u{30a}\u{2007}book \u{1e6a}he\u{30a}\u{2007}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-044",
            "the\u{2008}apple THE\u{2008}book The\u{2008}hour",
            "\u{1e6b}h\u{113}\u{2008}apple \u{1e6a}HE\u{30a}\u{2008}book \u{1e6a}he\u{30a}\u{2008}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-045",
            "the\u{2009}apple THE\u{2009}book The\u{2009}hour",
            "\u{1e6b}h\u{113}\u{2009}apple \u{1e6a}HE\u{30a}\u{2009}book \u{1e6a}he\u{30a}\u{2009}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-046",
            "the\u{200a}apple THE\u{200a}book The\u{200a}hour",
            "\u{1e6b}h\u{113}\u{200a}apple \u{1e6a}HE\u{30a}\u{200a}book \u{1e6a}he\u{30a}\u{200a}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-047",
            "the\u{2028}apple THE\u{2028}book The\u{2028}hour",
            "\u{1e6b}h\u{113}\u{2028}apple \u{1e6a}HE\u{30a}\u{2028}book \u{1e6a}he\u{30a}\u{2028}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-048",
            "the\u{2029}apple THE\u{2029}book The\u{2029}hour",
            "\u{1e6b}h\u{113}\u{2029}apple \u{1e6a}HE\u{30a}\u{2029}book \u{1e6a}he\u{30a}\u{2029}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-049",
            "the\u{202f}apple THE\u{202f}book The\u{202f}hour",
            "\u{1e6b}h\u{113}\u{202f}apple \u{1e6a}HE\u{30a}\u{202f}book \u{1e6a}he\u{30a}\u{202f}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-050",
            "the\u{205f}apple THE\u{205f}book The\u{205f}hour",
            "\u{1e6b}h\u{113}\u{205f}apple \u{1e6a}HE\u{30a}\u{205f}book \u{1e6a}he\u{30a}\u{205f}\u{1d559}\u{f2}ur",
        ),
        (
            "context-curated-051",
            "the\u{3000}apple THE\u{3000}book The\u{3000}hour",
            "\u{1e6b}h\u{113}\u{3000}apple \u{1e6a}HE\u{30a}\u{3000}book \u{1e6a}he\u{30a}\u{3000}\u{1d559}\u{f2}ur",
        ),
    ];
    for &(identifier, text, expected) in cases {
        assert_eq!(
            lingose::annotate_ips(text).unwrap(),
            expected,
            "{identifier}"
        );
        assert_eq!(
            lingose::annotate_ips_with_skip_top(text, 0).unwrap(),
            expected,
            "{identifier}/zero"
        );
    }
}
