"""P1.2 full-data layout experiment; deliberately not the production exporter."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import sys
import tarfile
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (ROOT, LIB_ROOT, canonical, connect, fingerprints, installed, json_text,
                       main_error, no_restore, require, require_baseline)

NULL = 0xffffffff
ENGLISH = re.compile(r"[A-Za-z]+(?:[-'’][A-Za-z]+)*\Z")


def string_value(row):
    if row is None or row["status"] != "available":
        return None
    value = json.loads(row["value_json"])
    require(isinstance(value, str), "Available projected field is not a string")
    return value


def project(baseline):
    from lingose import query
    _, _, path, frequency = installed()
    with closing(connect(path)) as db, closing(connect(frequency)) as freq:
        require(db.execute("PRAGMA user_version").fetchone()[0] == 2, "Lexicon schema drift")
        require(freq.execute("PRAGMA user_version").fetchone()[0] == 1, "Frequency schema drift")
        require(tuple(freq.execute("SELECT schema_version,max_rank FROM frequency_metadata WHERE singleton=1").fetchone()) == (1,5062), "Frequency metadata drift")
        base = list(db.execute("""SELECT e.entry_id,e.word,s.status,s.reason,s.selected_id,
            p.pronunciation_id FROM entry e
            LEFT JOIN pronunciation_set s ON s.entry_id=e.entry_id
            LEFT JOIN pronunciation p ON p.pronunciation_id=s.selected_id AND p.entry_id=e.entry_id
            ORDER BY e.word COLLATE BINARY"""))
        require(len(base) == baseline["lexicon"]["word_count"], "Entry count drift")
        ids = {row["entry_id"]: index for index,row in enumerate(base)}
        entries = [[row["word"], *([None]*7), 0, 0] for row in base]
        word_indices = {entry[0]: index for index,entry in enumerate(entries)}
        require(len(word_indices) == len(entries), "Duplicate precise word key")
        scalar_columns = {"ism":3, "root_lemma":5, "meaning_en":6, "meaning_zh":7}
        for row in db.execute("""SELECT entry_id,field_key,status,value_json FROM field_value
            WHERE scope='entry' AND field_key IN ('ism','root_lemma','meaning_en','meaning_zh')"""):
            entries[ids[row["entry_id"]]][scalar_columns[row["field_key"]]] = string_value(row)
        selected = {}
        for row in db.execute("""SELECT s.entry_id,f.* FROM pronunciation_set s
            JOIN pronunciation p ON p.pronunciation_id=s.selected_id AND p.entry_id=s.entry_id
            JOIN field_value f ON f.pronunciation_id=p.pronunciation_id AND f.scope='pronunciation'
            WHERE f.field_key IN ('ipa','ips','ipsm')"""):
            key = (row["entry_id"], row["field_key"])
            require(key not in selected, "Duplicate selected pronunciation field")
            selected[key] = row
        derivations = {row["result_value_id"]: row for row in db.execute("""SELECT d.*,
            ips.status AS ips_status,ips.value_json AS ips_json,
            ism.status AS ism_status,ism.value_json AS ism_json
            FROM ipsm_derivation d
            LEFT JOIN field_value ips ON ips.value_id=d.ips_value_id
            LEFT JOIN field_value ism ON ism.value_id=d.ism_value_id""")}
        stale = 0
        for index,row in enumerate(base):
            require(row["status"] is not None, "Entry missing pronunciation set")
            key = row["entry_id"]
            if row["status"] == "available":
                require(row["selected_id"] is not None and row["pronunciation_id"] is not None,
                        "Available group lacks an owned selected pronunciation")
                ips = selected.get((key,"ips"))
                require(ips is not None, "Selected pronunciation lacks IPS field")
                for field,column in (("ipa",1),("ips",2),("ipsm",4)):
                    source = selected.get((key,field))
                    value = string_value(source)
                    if value is not None and field == "ipsm":
                        dependency = derivations.get(source["value_id"])
                        valid = dependency is not None and dependency["algorithm_version"] == "1"
                        if valid:
                            valid = dependency["ips_status"] == dependency["ism_status"] == "available"
                        if valid:
                            actual = [json.loads(dependency[name]) for name in ("ips_json","ism_json")]
                            require(all(isinstance(text,str) for text in actual), "Invalid IPSM dependency type")
                            valid = all(hashlib.sha256(text.encode("utf-8")).hexdigest() == dependency[name]
                                        for text,name in zip(actual,("ips_sha256","ism_sha256")))
                        if not valid:
                            stale += 1
                            value = None
                    entries[index][column] = value
                if ips["status"] == "available":
                    require(isinstance(entries[index][2],str) and entries[index][2] != "", "Invalid available annotation IPS")
                    entries[index][9] = 2
                else:
                    entries[index][9] = int(ips["status"] == "missing" and ips["reason"] == "source_record_missing")
            else:
                entries[index][9] = int(row["status"] == "missing" and row["reason"] == "source_record_missing")
        labels = query._labels(db)
        require(len(labels) == len(set(labels)) <= 32, "Unsupported category registry")
        label_positions = {"kind:"+label:index for index,label in enumerate(labels)}
        invalid = db.execute("""SELECT COUNT(*) FROM field_value WHERE scope='entry'
            AND field_key LIKE 'kind:%' AND status='available'
            AND (json_type(value_json) NOT IN ('true','false') OR
                 (json_type(value_json)='true' AND value_json!='true'))""").fetchone()[0]
        require(invalid == 0, "kind boolean and kind_list SQL projections differ")
        for row in db.execute("""SELECT entry_id,field_key FROM field_value
            WHERE scope='entry' AND status='available' AND value_json='true' AND field_key LIKE 'kind:%'"""):
            require(row["field_key"] in label_positions, "Unregistered category")
            entries[ids[row["entry_id"]]][8] |= 1 << label_positions[row["field_key"]]
        lists = []
        for index,label in enumerate(labels):
            members = query.kind_list(label)
            expected = {entry[0] for entry in entries if entry[8] & (1 << index)}
            require(len(members) == len(set(members)) and set(members) == expected, "Category projections disagree")
            lists.append([word_indices[word] for word in members])
        frequencies = [list(row) for row in freq.execute("SELECT word,rank FROM frequency_word ORDER BY word COLLATE BINARY")]
        require(len(frequencies) == baseline["frequency"]["table_counts"]["frequency_word"], "Frequency count drift")
        require(all(type(number) is int and 1 <= number <= 5062 for _,number in frequencies), "Invalid original frequency threshold")
    return entries, labels, lists, frequencies, stale


def encode(entries, labels, lists, frequencies, baseline):
    strings = {text for entry in entries for text in entry[:8] if text is not None}
    strings.update(labels)
    strings.update(word for word,_ in frequencies)
    strings = sorted(strings, key=lambda text:text.encode("utf-8"))
    indices = {text:index for index,text in enumerate(strings)}
    pool = bytearray()
    offsets = [0]
    for text in strings:
        pool.extend(text.encode("utf-8"))
        offsets.append(len(pool))
    members = [member for values in lists for member in values]
    counts = [1,len(strings),len(entries),len(labels),len(members),len(frequencies),len(pool),2,1,1]
    output = bytearray(b"LNGIDX01" + struct.pack("<10I",*counts))
    output.extend(bytes.fromhex(baseline["lexicon"]["build_info"]["data_version"]))
    output.extend(bytes.fromhex(baseline["frequency"]["metadata"]["data_version"]))
    require(len(output) == 112, "Header layout changed")
    output.extend(struct.pack(f"<{len(offsets)}I",*offsets))
    for entry in entries:
        record = [NULL if text is None else indices[text] for text in entry[:8]] + entry[8:]
        output.extend(struct.pack("<10I",*record))
    start = 0
    for label,values in zip(labels,lists):
        output.extend(struct.pack("<3I",indices[label],start,len(values)))
        start += len(values)
    output.extend(struct.pack(f"<{len(members)}I",*members))
    for word,number in frequencies:
        output.extend(struct.pack("<2I",indices[word],number))
    output.extend(pool)
    return bytes(output), {"strings":len(strings),"pool_bytes":len(pool),"entries":len(entries),
                           "labels":len(labels),"members":len(members),"frequency_words":len(frequencies)}


def corpus(entries, count):
    words = [entry[0] for entry in entries if ENGLISH.fullmatch(entry[0])]
    seed = ["The","apple","is","running","unknownwordzz","don't","well-known","the",
            "book","US","iPhone","walks","baking","studied","I'm","you're"]
    separators = [" ", ", ", ".\n", " ", ";\n\n", "\t", " (", ") "]
    parts = []
    for index in range(count):
        word = seed[(index//16)%len(seed)] if index%16 < 4 else words[(index*7919)%len(words)]
        parts.extend((word, separators[index%len(separators)]))
    text = "".join(parts)
    require(len(re.findall(r"[A-Za-z]+(?:[-'’][A-Za-z]+)*",text)) == count, "Corpus word-count mismatch")
    return text.encode("utf-8")


def archive_estimate(resources):
    stream = io.BytesIO()
    version = tomllib.loads((LIB_ROOT / "Cargo.toml").read_text(encoding="utf-8"))["package"]["version"]
    with tarfile.open(fileobj=stream,mode="w",format=tarfile.USTAR_FORMAT) as archive:
        files = {str(path.relative_to(LIB_ROOT)).replace("\\","/"):path.read_bytes()
                 for folder in ("src", "examples") for path in (LIB_ROOT/folder).rglob("*.rs")}
        for name in ("Cargo.toml","Cargo.lock","README.md","LICENSE","SOURCES.md"):
            files[name] = ((ROOT if name == "Cargo.lock" else LIB_ROOT)/name).read_bytes()
        files.update({"data/"+name:value for name,value in resources.items()})
        for name,value in sorted(files.items()):
            item = tarfile.TarInfo(f"lingose-{version}/"+name)
            item.size, item.mtime, item.mode = len(value),0,0o644
            archive.addfile(item,io.BytesIO(value))
    return gzip.compress(stream.getvalue(),compresslevel=6,mtime=0)


def persist(directory, name, value, write):
    path = directory/name
    if path.exists():
        require(path.read_bytes() == value, f"Probe artifact drift: {path}; use a new isolated directory")
    else:
        require(write, f"Missing probe artifact: {path}; initial creation requires --write")
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("xb") as stream:
            stream.write(value)
    return {"bytes":len(value),"sha256":hashlib.sha256(value).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write",action="store_true")
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--output",type=Path,default=ROOT/".local/layout-020")
    args = parser.parse_args()
    require(args.write != args.check, "Choose exactly one of --write or --check")
    directory = args.output.resolve()
    require(directory.is_relative_to(ROOT/".local"), "Probe output must remain under this project's .local")
    baseline = require_baseline()
    with no_restore():
        entries,labels,lists,frequency,stale = project(baseline)
        from lingose import query
        # Actual installed API smoke checks, not self-comparison of the encoder.
        projected = {entry[0]:entry for entry in entries}
        for word in ("apple","running","May","may","present","largely","Marxism","has","sh"):
            entry = projected[word]
            for index,name in ((1,"IPA"),(2,"IPS"),(4,"IPSM")):
                require(getattr(query,name)(word) == ([] if entry[index] is None else [entry[index]]), f"API projection mismatch: {name} {word}")
            for index,name in ((3,"ISM"),(5,"root_lemma")):
                require(getattr(query,name)(word) == entry[index], f"API projection mismatch: {name} {word}")
            for index,lang in ((6,"en"),(7,"zh")):
                require(query.meaning(word,lang) == entry[index], f"Meaning projection mismatch: {word} {lang}")
    image,lex_counts = encode(entries,labels,lists,[],baseline)
    freq_image,freq_counts = encode([],[],[],frequency,baseline)
    resources = {"image.bin":image,"frequency.bin":freq_image}
    resources.update({name+".gz":gzip.compress(value,compresslevel=9,mtime=0) for name,value in list(resources.items())})
    artifacts = {}
    for name,value in resources.items():
        artifacts[name] = persist(directory,name,value,args.write)
        if name.endswith(".bin"):
            persist(directory,name.removesuffix(".bin")+".sha256",(hashlib.sha256(value).hexdigest()+"\n").encode("ascii"),args.write)
    for count in (10000,100000):
        value = corpus(entries,count)
        artifacts[f"corpus-{count}.txt"] = persist(directory,f"corpus-{count}.txt",value,args.write)
    for mode,suffix in (("static",""),("gzip",".gz")):
        payload = {name+suffix:resources[name+suffix] for name in ("image.bin","frequency.bin")}
        value = archive_estimate(payload)
        artifacts[f"archive-estimate-{mode}.tar.gz"] = persist(directory,f"archive-estimate-{mode}.tar.gz",value,args.write)
    manifest = {"experiment":"P1.2-layout-v1","format_version":1,
        "baseline_sha256":hashlib.sha256((ROOT/"docs/reference-baseline.json").read_bytes()).hexdigest(),
        "lexicon_data_version":baseline["lexicon"]["build_info"]["data_version"],
        "frequency_data_version":baseline["frequency"]["metadata"]["data_version"],
        "lexicon":lex_counts,"frequency":freq_counts,"category_lengths":dict(zip(labels,map(len,lists))),
        "annotation_states":dict(Counter(str(entry[9]) for entry in entries)),
        "available_fields":dict(zip(("ipa","ips","ism","ipsm","root_lemma","meaning_en","meaning_zh"),
            (sum(entry[index] is not None for entry in entries) for index in range(1,8)))),
        "invalid_selected_ipsm":stale,"artifacts":artifacts,
        "archive_estimate_note":"Actual gzip-compressed tar with current source and complete projected resources, not cargo package or final .crate acceptance"}
    require(fingerprints() == baseline["fingerprints"], "Input changed during experiment")
    persist(directory,"manifest.json",json_text(manifest).encode("utf-8"),args.write)
    print(json_text(manifest))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
