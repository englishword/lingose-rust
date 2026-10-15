"""Independently decode the P1.2 images and check fixed P0 projections, not annotation."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import ROOT, canonical, json_text, main_error, require

NULL = 0xffffffff


def decode(data):
    require(data[:8] == b"LNGIDX01", "Bad probe image magic")
    version,strings,entries,labels,members,frequencies,pool_bytes,lex,frequency,algorithm = struct.unpack_from("<10I",data,8)
    require((version,lex,frequency,algorithm) == (1,2,1,1), "Unsupported image version")
    offset = 112
    offsets = struct.unpack_from(f"<{strings+1}I",data,offset)
    offset += (strings+1)*4
    records = [struct.unpack_from("<10I",data,offset+index*40) for index in range(entries)]
    offset += entries*40
    categories = [struct.unpack_from("<3I",data,offset+index*12) for index in range(labels)]
    offset += labels*12
    positions = struct.unpack_from(f"<{members}I",data,offset)
    offset += members*4
    frequency_rows = [struct.unpack_from("<2I",data,offset+index*8) for index in range(frequencies)]
    offset += frequencies*8
    require(offset+pool_bytes == len(data), "Wrong image section lengths")
    require(offsets[0] == 0 and offsets[-1] == pool_bytes, "Wrong pool boundary")
    texts = [data[offset+offsets[index]:offset+offsets[index+1]].decode("utf-8") for index in range(strings)]
    entries = [[None if reference == NULL else texts[reference] for reference in row[:8]]+list(row[8:]) for row in records]
    categories = [(texts[label],[entries[positions[position]][0] for position in range(start,start+length)])
                  for label,start,length in categories]
    frequency_rows = [(texts[word],number) for word,number in frequency_rows]
    return entries,categories,frequency_rows


def logical_bytes(images):
    def integer(value):
        return struct.pack("<I",value)
    def text(value):
        if value is None:
            return integer(NULL)
        encoded = value.encode("utf-8")
        return integer(len(encoded))+encoded
    for entries,categories,frequency in images:
        yield struct.pack("<4I",len(entries),len(categories),sum(len(words) for _,words in categories),len(frequency))
        for row in entries:
            yield b"".join(text(value) for value in row[:8])+struct.pack("<2I",*row[8:])
        for label,words in categories:
            yield text(label)+integer(len(words))
            yield b"".join(text(word) for word in words)
        for word,number in frequency:
            yield text(word)+integer(number)


def main():
    directory = ROOT/".local/layout"
    manifest = json.loads((directory/"manifest.json").read_text(encoding="utf-8"))
    images = []
    for name in ("image.bin","frequency.bin"):
        raw = (directory/name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == manifest["artifacts"][name]["sha256"], "Raw image digest differs")
        require(gzip.decompress((directory/(name+".gz")).read_bytes()) == raw, "Gzip content differs")
        images.append(decode(raw))
    entries,categories,_ = images[0]
    words = {row[0]:row for row in entries}
    labels = [label for label,_ in categories]
    lists = dict(categories)
    count = 0
    vectors = json.loads((ROOT/"tests/fixtures/python-api-v1.json").read_text(encoding="utf-8"))
    for case in vectors["cases"]:
        if case["source"] != "snapshot" or "error" in case["expected"]:
            continue
        call,expected = case["call"],case["expected"]
        name,args = call["api"],call.get("args",[])
        name = vectors["aliases"].get(name,name)
        if name == "kind_list":
            actual = lists[args[0] if args else "CET4"]
            identity = expected["ordered_list"]
            require(len(actual) == identity["length"] and hashlib.sha256(canonical(actual)).hexdigest() == identity["sha256"], f"P0 full category ordering differs: {case['id']}")
        elif name == "labels":
            require(labels == expected["value"], "P0 registry order differs")
        elif name in ("IPA","IPS","ISM","IPSM","root_lemma","meaning","kind"):
            word = args[0]
            row = words.get(word)
            if row is None and word[0].isupper() and not any(character.isupper() for character in word[1:]):
                row = words.get(word.lower())
            if name in ("IPA","IPS","IPSM"):
                value = row[{"IPA":1,"IPS":2,"IPSM":4}[name]] if row is not None else None
                actual = [] if value is None else [value]
            elif name == "kind":
                actual = row is not None and bool(row[8] & (1 << labels.index(args[1] if len(args)>1 else "CET4")))
            else:
                field = {"ISM":3,"root_lemma":5,"meaning":7 if len(args)>1 and args[1]=="zh" else 6}[name]
                actual = row[field] if row is not None else None
            require(actual == expected["value"], f"P0 query projection differs: {case['id']}")
        else:
            continue
        count += 1
    digest = hashlib.sha256()
    fnv = 0xcbf29ce484222325
    for chunk in logical_bytes(images):
        digest.update(chunk)
        for byte in chunk:
            fnv = ((fnv ^ byte)*0x100000001b3) & 0xffffffffffffffff
    result = {"checked_p0_snapshot_vectors":count,"scope":"query projections, registry and complete ordered category lists; excludes errors, fixtures and annotation",
              "logical_sha256":digest.hexdigest(),"logical_fnv1a64":f"{fnv:016x}"}
    evidence = ROOT/"docs/layout-probe-results.json"
    if evidence.exists():
        report = json.loads(evidence.read_text(encoding="utf-8"))
        require(result["logical_fnv1a64"] == report["shared_identity"][2], "Python and Rust complete logical content differ")
    print(json_text(result))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        main_error(error)
