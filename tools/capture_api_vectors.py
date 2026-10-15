"""Capture/check Python API examples from the pinned snapshot and isolated fixtures."""

from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (ROOT, ReferenceError, canonical, fingerprints, freeze, json_text,
                       main_error, no_restore, require, require_baseline)

OUTPUT = ROOT / "tests/fixtures/python-api-v1.json"
ALIASES = {"ipa": "IPA", "ips": "IPS", "ism": "ISM", "ipsm": "IPSM"}
WORD_APIS = ("IPA", "IPS", "ISM", "IPSM", "root_lemma", "meaning", "kind")


def integer_argument(value):
    if isinstance(value, dict) and set(value) == {"$integer"}:
        return int(value["$integer"])
    return value


def evaluate(case: dict, *, compact_lists: bool = False) -> dict:
    import lingose
    name = ALIASES.get(case["api"], case["api"])
    require(name in (*WORD_APIS, "kind_list", "labels", "annotate_ips"), f"Unplanned API: {name}")
    function = getattr(lingose, name)
    args = [integer_argument(value) for value in case.get("args", [])]
    kwargs = {key: integer_argument(value) for key,value in case.get("kwargs", {}).items()}
    try:
        value = function(*args, **kwargs)
    except (TypeError, ValueError, lingose.LexiconDataError) as error:
        require(type(error).__name__ == case.get("error"),
                f"Unexpected error for {case}: {type(error).__name__}: {error}")
        # OS error text and temporary paths are not part of the Rust contract.
        return {"error": type(error).__name__}
    require("error" not in case, f"Expected {case.get('error')} for {case}")
    if "expect" in case:
        require(value == case["expect"], f"Documented expectation differs for {case['api']}: {args}")
    if compact_lists and name == "kind_list":
        return {"ordered_list": {"length": len(value), "sha256": hashlib.sha256(canonical(value)).hexdigest(),
                                 "head": value[:10], "tail": value[-10:]}}
    return {"value": value}


def snapshot_cases(labels: list[str]) -> list[dict]:
    cases = []
    words = ("apple", "running", "Apple", "APPLE", "May", "may", "US", "us", "iPhone",
             "McDonald", "present", "largely", "Marxism", "has", "sh", "unknownwordzz")
    for word in words:
        for api in WORD_APIS:
            cases.append({"group": "word-query", "api": api, "args": [word]})
    for api in ALIASES:
        for word in ("apple", "running", "unknownwordzz"):
            cases.append({"group": "lowercase-alias", "api": api, "args": [word]})
    for word in ("apple", "May", "may", "unknownwordzz"):
        cases.append({"group": "meaning-zh", "api": "meaning", "args": [word,"zh"]})
    cases.append({"group": "labels", "api": "labels"})
    cases.append({"group": "category-list-default", "api": "kind_list"})
    cases.extend({"group": "category-list", "api": "kind_list", "args": [label]} for label in labels)
    for api in WORD_APIS:
        for word, error in (("", "ValueError"), (" apple", "ValueError"), ("apple ", "ValueError"),
                            ("ap\x00ple", "ValueError"), (None,"TypeError"), (42,"TypeError")):
            cases.append({"group": "invalid-word", "api": api, "args": [word], "error": error})
    for lang,error in (("EN","ValueError"), ("fr","ValueError"), (None,"TypeError")):
        cases.append({"group": "invalid-language", "api":"meaning", "args":["unknownwordzz",lang], "error":error})
    for label,error in (("cet4","ValueError"), ("COLLINS","ValueError"), ("Band","ValueError"), (None,"TypeError")):
        cases.append({"group":"invalid-label", "api":"kind", "args":["unknownwordzz",label], "error":error})
        cases.append({"group":"invalid-label", "api":"kind_list", "args":[label], "error":error})
    texts = ("Abandon the book.", "the apple THE book The hour the university the", "the, apple; the\napple; the\n\napple",
             "Apple APPLE aPpLe May may US us iPhone McDonald", "present record address largely",
             "don't doesn't aren't I'm you're o'clock don’t doesn’t aren’t I’m you’re o’clock",
             "walks boxes baked baking studies studied stopped stopping plays tying",
             "ageing singeing tingeing queueing busing singing axes is",
             "first-rate second-rate second-puldsm pending-compound",
             "WHALE WHIM YUM w̄ 𝕙 e\u030a", "unknownwordzz unknown-wordzz who'unknown",
             "café apple123 中文apple 中文\t123 é e\u0301\n😀", "Messrs. p.m. a lot a lottery puldsm",
             "  Abandon\t  the (apple).\n\nThe book.  ", "")
    for text in texts:
        for threshold in (0,1000,5062):
            cases.append({"group":"annotation", "api":"annotate_ips", "args":[text], "kwargs":{"skip_top":threshold}})
    cases.append({"group":"annotation-default", "api":"annotate_ips", "args":["Abandon the book."], "expect":"Åbando̊n ṫhe̊ book."})
    for threshold in (1,29,30,31,5061,5063,{"$integer":"1"+"0"*100}):
        cases.append({"group":"threshold-boundary", "api":"annotate_ips", "args":["the book abandon tail"], "kwargs":{"skip_top":threshold}})
    for text,error in ((None,"TypeError"),(42,"TypeError"),("\x00","ValueError")):
        cases.append({"group":"invalid-text", "api":"annotate_ips", "args":[text], "error":error})
    for threshold,error in ((True,"TypeError"),(1.5,"TypeError"),("1","TypeError"),(-1,"ValueError")):
        cases.append({"group":"invalid-threshold", "api":"annotate_ips", "args":["apple"], "kwargs":{"skip_top":threshold}, "error":error})
    cases.append({"group":"keyword-only", "api":"annotate_ips", "args":["apple",1], "error":"TypeError"})
    return cases


def fixture_spec() -> dict:
    notations = {"abandon":"åbando̊n", "apple":"apple", "book":"book", "the":"ṫhe̊",
                 "may":"mãy", "walk":"wàlk", "box":"bòx", "bake":"bāke", "study":"stûdẏ",
                 "stop":"stòp", "play":"plāy", "tie":"tīe", "ax":"ãx", "axe":"āxe",
                 "age":"āge", "singe":"si̊nge", "queue":"qūeue", "bus":"bûs", "sing":"sĩng",
                 "whale":"w̄𝕙āle", "whim":"ẘ𝕙i̊m", "yum":"ẙu̇m", "bad":"bādextra",
                 "first-rate":"fi̊rst-rāte", "second":"seco̊nd", "rate":"rāte", "tail":"tãil", "I":"ī", "i":"ī"}
    entries = {word:{"pronunciations":[{"ips":ips}]} for word,ips in notations.items()}
    entries["apple"]["pronunciations"][0].update(ipa="æpəl",ipsm="app-le")
    entries["apple"]["fields"] = {"ism":"app-le", "root_lemma":"apple", "rank":"20", "meaning_en":"n. fixture apple", "kind:CET4":True, "kind:CET6":False}
    entries["May"] = {"pronunciations":[{"ips":"Māy"}], "fields":{"meaning_en":{"status":"missing","reason":"empty_cell"}}}
    entries["may"]["fields"] = {"meaning_en":"modal. fixture may"}
    entries["Apple"] = {"state":"pending_review", "reason":"fixture_pending"}
    entries["second-rate"] = {"state":"missing", "reason":"source_record_missing"}
    entries["pending-compound"] = {"state":"pending_review", "reason":"fixture_pending"}
    entries["empty"] = {"pronunciations":[{"ips":{"status":"missing","reason":"empty_cell"}}]}
    entries["walks"] = {"pronunciations":[{"ips":{"status":"missing","reason":"empty_cell"}}]}
    entries["plays"] = {"state":"conflict", "reason":"fixture_conflict"}
    entries["baked"] = {"pronunciations":[{"ips":{"status":"invalid","reason":"fixture_invalid"}}]}
    entries["don't"] = {"pronunciations":[{"ips":{"status":"invalid","reason":"fixture_invalid"}}]}
    entries["pair"] = {"pronunciations":[{"ipa":"known-ipa"}]}
    entries["present"] = {"pronunciations":[{"ipa":"first","ips":"prīṡent"},{"ipa":"selected","ips":"prėṡent"}], "selected":1}
    entries["stale"] = {"pronunciations":[{"ips":"stale","ipsm":"sta-le"}],"fields":{"ism":"sta-le"},"derivation":"stale"}
    entries["noderivation"] = {"pronunciations":[{"ips":"noderivation","ipsm":"no-derivation"}],"fields":{"ism":"no-derivation"},"derivation":"missing"}
    entries["zeta"] = {"fields":{"root_lemma":"apple","rank":"10","kind:CET4":True}}
    entries["orphan"] = {"fields":{"kind:CET4":True}}
    return {"entries":entries, "frequency":{"the":1,"abandon":2,"abandoned":2,"unlisted":3,"messrs.":4,"p.m.":5,"a lot":6,"tail":5062}}


def build_fixture(path: Path, frequency: Path, baseline: dict, spec: dict) -> None:
    require(not path.exists() and not frequency.exists(), "Fixture targets must be absent")
    definitions = {field["field_key"]:field for field in baseline["lexicon"]["field_definitions"]}
    with closing(sqlite3.connect(path)) as db:
        for table in baseline["archive_manifest"]["tables"]:
            db.execute(table["sql"])
        db.execute("PRAGMA user_version=2")
        db.execute("INSERT INTO build_info VALUES (1,2,'fixture-v1','1','fixture','{}')")
        for field in definitions.values():
            db.execute("INSERT INTO field_definition VALUES (?,?,?,?,?,?)", tuple(field[key] for key in ("field_key","scope","domain","value_type","label","ordinal")))

        def field_value(word,key,value,pron=None):
            status = value["status"] if isinstance(value,dict) else "available"
            reason = value.get("reason") if isinstance(value,dict) else None
            identifier = (pron or word) + ":" + key
            db.execute("INSERT INTO field_value (value_id,entry_id,pronunciation_id,field_key,scope,value_type,status,value_json,basis,matched_word,match_type,reason) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                       (identifier,word,pron,key,definitions[key]["scope"],definitions[key]["value_type"],status,
                        json.dumps(value,ensure_ascii=False) if status=="available" else None,
                        ("derived" if key=="ipsm" else "source") if status=="available" else None,word,"exact",reason))
            return identifier

        for word,entry in spec["entries"].items():
            db.execute("INSERT INTO entry VALUES (?,?)", (word,word))
            pairs = entry.get("pronunciations",[])
            selected = f"{word}:p{entry.get('selected',0)}" if pairs else None
            state = entry.get("state","available" if pairs else "missing")
            db.execute("INSERT INTO pronunciation_set VALUES (?,?,?,?,NULL)",(word,state,selected,entry.get("reason","source_record_missing" if not pairs else None)))
            for key,value in entry.get("fields",{}).items():
                field_value(word,key,value)
            for ordinal,pair in enumerate(pairs):
                pron = f"{word}:p{ordinal}"
                db.execute("INSERT INTO pronunciation VALUES (?,?,?,'unreviewed',NULL)",(pron,word,ordinal))
                for key in ("ipa","ips","ipsm"):
                    field_value(word,key,pair.get(key,{"status":"missing","reason":"source_record_missing"}),pron)
                if isinstance(pair.get("ipsm"),str) and entry.get("derivation") != "missing":
                    digest = lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest()
                    ips_hash = "0"*64 if entry.get("derivation")=="stale" else digest(pair["ips"])
                    db.execute("INSERT INTO ipsm_derivation VALUES (?,?,?,?,?,'1','{}')",(pron+":ipsm",pron+":ips",word+":ism",ips_hash,digest(entry["fields"]["ism"])))
        db.commit()
    with closing(sqlite3.connect(frequency)) as db:
        for table in baseline["frequency"]["schema"]:
            if table["type"]=="table":
                db.execute(table["sql"])
        db.execute("PRAGMA user_version=1")
        db.execute("INSERT INTO frequency_metadata VALUES (1,1,5062,?,'fixture','fixture',8,'fixture-v1')",("f"*64,))
        db.executemany("INSERT INTO frequency_word VALUES (?,?)",spec["frequency"].items())
        db.commit()


@contextmanager
def fixture_paths(path: Path, frequency: Path):
    from lingose import query, annotation, _resources, _packed
    with patch.object(query,"_database_path",return_value=path), patch.object(annotation,"_frequency_path",return_value=frequency), \
         patch.object(_resources,"ensure_database",return_value=None), \
         patch.object(_packed,"restore",side_effect=ReferenceError("Fixture restoration forbidden")):
        yield


def rule_cases() -> list[dict]:
    cases = []
    for api,word in (("IPS","Apple"),("IPS","APPLE"),("IPS","May"),("meaning","May"),("meaning","may"),
                     ("IPA","pair"),("IPS","pair"),("IPA","present"),("IPS","present"),
                     ("IPSM","apple"),("IPSM","stale"),("IPSM","noderivation")):
        cases.append({"group":"query-fixture","api":api,"args":[word]})
    cases.extend([{"group":"category-fixture","api":"kind_list"},{"group":"category-fixture","api":"kind","args":["apple","CET6"]}])
    texts = ("Apple APPLE aPpLe May may", "the book THE apple The hour the university the",
             'the "apple" the (apple) the\napple the, apple the\n\napple',
             "WHALE WHIM YUM bad BAD", "walks boxes baked baking studies studied stopped stopping plays tying",
             "ageing singeing queueing busing singing axes is", "first-rate second-rate second-puldsm pending-compound empty",
             "don't doesn't aren't I'm you're o'clock don’t doesn’t aren’t I’m you’re o’clock",
             "café apple123 中文apple e\u0301 中文 😀", "unknownwordzz", "Messrs. p.m. a lot a lottery unlisted tail abandoned")
    for text in texts:
        cases.append({"group":"annotation-fixture","api":"annotate_ips","args":[text]})
    cases.append({"group":"blocked-fallback-fixture","api":"annotate_ips","args":["walks plays baked don't is"],"expect":"[walks] [plays] [baked] [don't] [is]"})
    for threshold in (0,1,2,3,4,5,6,5061,5062,5063,{"$integer":"1"+"0"*100}):
        cases.append({"group":"frequency-fixture","api":"annotate_ips","args":["the abandon abandoned unlisted Messrs. p.m. a lot tail"],"kwargs":{"skip_top":threshold}})
    return cases


def capture() -> dict:
    import lingose
    baseline = require_baseline()
    before = baseline["fingerprints"]
    records = []

    def append(case,source,compact=False):
        records.append({"id":f"{source}-{len(records)+1:04d}","source":source,
                        "call":case, "expected":evaluate(case,compact_lists=compact)})

    with no_restore():
        labels = lingose.labels()
        for case in snapshot_cases(labels):
            append(case,"snapshot",True)
    spec = fixture_spec()
    with tempfile.TemporaryDirectory(prefix="lingose-p0-") as temporary:
        directory = Path(temporary)
        main_path,frequency = directory/"fixture.sqlite",directory/"frequency.sqlite"
        build_fixture(main_path,frequency,baseline,spec)
        fixture_before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (main_path,frequency)}
        with fixture_paths(main_path,frequency):
            for case in rule_cases():
                append(case,"fixture")
        require(fixture_before == {path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in (main_path,frequency)}, "Fixture APIs modified their input")
        # Mutate only disposable fixture files to exercise data failures.
        with fixture_paths(directory/"absent.sqlite",frequency):
            append({"group":"missing-main","api":"IPS","args":["apple"],"error":"LexiconDataError"},"resource-fixture")
        with fixture_paths(main_path,directory/"absent-frequency.sqlite"):
            append({"group":"missing-frequency","api":"annotate_ips","args":["apple"],"kwargs":{"skip_top":1},"error":"LexiconDataError"},"resource-fixture")
            append({"group":"zero-no-frequency","api":"annotate_ips","args":["apple"],"kwargs":{"skip_top":0},"expect":"apple"},"resource-fixture")
        with fixture_paths(directory/"absent.sqlite",directory/"absent-frequency.sqlite"):
            append({"group":"no-token-no-resources","api":"annotate_ips","args":["中文 123 😀 e\u0301"],"kwargs":{"skip_top":1},"expect":"中文 123 😀 e\u0301"},"resource-fixture")
        with closing(sqlite3.connect(main_path)) as db:
            db.execute("PRAGMA user_version=999")
        with fixture_paths(main_path,frequency):
            append({"group":"schema-version","api":"IPS","args":["apple"],"error":"SchemaVersionError"},"resource-fixture")
        with closing(sqlite3.connect(main_path)) as db:
            db.execute("PRAGMA user_version=2")
            db.execute("DROP TABLE pronunciation_set")
        with fixture_paths(main_path,frequency):
            append({"group":"missing-table","api":"IPS","args":["apple"],"error":"LexiconDataError"},"resource-fixture")
    require(fingerprints()==before,"Installed reference changed during API capture")
    return {"format_version":1,"reference":{"version":"0.2.0","fingerprints":before},
            "aliases":ALIASES,"fixture_spec":spec,"canonical_json":"UTF-8, ensure_ascii=false, sorted object keys, compact separators, no NaN, no normalization",
            "summary":{"total":len(records),"by_source":{source:sum(row['source']==source for row in records) for source in ("snapshot","fixture","resource-fixture")},
                       "public_names":sorted({row['call']['api'] for row in records})},"cases":records}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--write",action="store_true")
    mode.add_argument("--check",action="store_true")
    args=parser.parse_args()
    data=capture()
    print(f"{freeze(OUTPUT,json_text(data),args.write)}: {data['summary']}")


if __name__=="__main__":
    try:
        main()
    except (ReferenceError,OSError,ValueError,sqlite3.Error) as error:
        main_error(error)
