"""Capture/check the installed reference, including all packed table digests."""

from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
from pathlib import Path
import sqlite3
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (BASELINE, MODULES, ROOT, ReferenceError, canonical, connect, fingerprints,
                       freeze, installed, json_text, main_error, reference_repositories, require)


def schema(db) -> list[dict]:
    return [dict(row) for row in db.execute(
        "SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name")]


def database_checks(db) -> dict:
    integrity = [row[0] for row in db.execute("PRAGMA integrity_check")]
    violations = [list(row) for row in db.execute("PRAGMA foreign_key_check")]
    require(integrity == ["ok"] and not violations, "SQLite integrity/foreign-key check failed")
    return {"integrity_check": integrity, "foreign_key_violations": violations,
            "query_only": db.execute("PRAGMA query_only").fetchone()[0]}


def capture() -> dict:
    import lingose
    from lingose import _packed

    _, package, database, frequency = installed()
    print("Fingerprinting installed code and resources...", flush=True)
    before = fingerprints()
    references = reference_repositories()
    python_ref = references["lingose-python"]
    for name in MODULES:
        if name != "__init__.py":
            require(before["modules"][name] == python_ref["files"][f"src/lingose/{name}"],
                    f"Installed/source behavior differs: {name}")
    for name in ("lexicon.lpk", "frequency.sqlite"):
        require({key: before["resources"][name][key] for key in ("bytes", "sha256")}
                == python_ref["files"][f"src/lingose/{name}"], f"Installed/source data differs: {name}")

    archive = package / "lexicon.lpk"
    with archive.open("rb") as stream:
        manifest, offset = _packed._read_header(stream)
        payload = hashlib.sha256()
        size = 0
        while block := stream.read(1024 * 1024):
            payload.update(block)
            size += len(block)
    require(size == manifest["payload_bytes"] and payload.hexdigest() == manifest["payload_sha256"],
            "Packed payload checksum/length mismatch")
    table_results = {}
    with closing(connect(database)) as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        info = dict(db.execute("SELECT * FROM build_info WHERE singleton=1").fetchone())
        require(version == info["schema_version"] == manifest["schema_version"], "Lexicon schema mismatch")
        require(info["data_version"] == manifest["data_version"], "Lexicon data version mismatch")
        table_names = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        require(table_names == {table["name"] for table in manifest["tables"]}, "Packed/cache tables differ")
        for table in manifest["tables"]:
            actual_sql = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table["name"],)).fetchone()[0]
            require(actual_sql == table["sql"], f"Table schema differs: {table['name']}")
            count, digest = _packed._table_digest(db, table)
            require((count, digest) == (table["rows"], table["sha256"]), f"Packed/cache content differs: {table['name']}")
            table_results[table["name"]] = {"rows": count, "sha256": digest}
            print(f"  {table['name']}: {count:,} rows, digest matches", flush=True)
        indexes = [row[0] for row in db.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL ORDER BY name")]
        require(sorted(indexes) == sorted(manifest["indexes"]), "Packed/cache indexes differ")
        words = hashlib.sha256()
        word_count = 0
        for row in db.execute("SELECT word FROM entry ORDER BY word COLLATE BINARY"):
            words.update(canonical(row[0]) + b"\n")
            word_count += 1
        require(db.execute("SELECT COUNT(DISTINCT word COLLATE BINARY) FROM entry").fetchone()[0] == word_count,
                "Duplicate exact lexicon keys")
        lexicon = {"schema_version": version, "build_info": info, "tables": table_results,
                   "schema": schema(db), "checks": database_checks(db), "word_count": word_count,
                   "binary_ordered_words_sha256": words.hexdigest(),
                   "field_definitions": [dict(row) for row in db.execute("SELECT * FROM field_definition ORDER BY ordinal,field_key")],
                   "pronunciation_states": [list(row) for row in db.execute("SELECT status,COUNT(*) FROM pronunciation_set GROUP BY status ORDER BY status")],
                   "field_states": [list(row) for row in db.execute("SELECT field_key,status,COUNT(*) FROM field_value GROUP BY field_key,status ORDER BY field_key,status")]}
    with closing(connect(frequency)) as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        metadata = dict(db.execute("SELECT * FROM frequency_metadata WHERE singleton=1").fetchone())
        require(version == metadata["schema_version"] == 1 and metadata["max_rank"] == 5062,
                "Unsupported frequency metadata")
        counts = {row[0]: db.execute('SELECT COUNT(*) FROM "' + row[0].replace('"','""') + '"').fetchone()[0]
                  for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")}
        frequency_info = {"schema_version": version, "metadata": metadata, "table_counts": counts,
                          "schema": schema(db), "checks": database_checks(db),
                          "rank_range": list(db.execute("SELECT MIN(rank),MAX(rank) FROM frequency_word").fetchone()),
                          "record_rank_gaps": sorted(set(range(1,metadata["max_rank"]+1)) - {row[0] for row in db.execute("SELECT rank FROM frequency_record")})}
    after = fingerprints()
    require(before == after, "Installed code/resources changed during audit")
    require(references == reference_repositories(), "Reference checkout changed during audit")
    return {"format_version": 1, "environment": {"python": sys.version, "executable": sys.executable,
            "platform": sys.platform, "unicode_version": unicodedata.unidata_version, "sqlite_version": sqlite3.sqlite_version},
            "installed": {"version": lingose.__version__, "package": str(package),
                          "public_names": lingose.__all__,
                          "lowercase_aliases_available": {name: hasattr(lingose,name) for name in ("ipa","ips","ism","ipsm")}},
            "fingerprints": before, "references": references, "archive_manifest": manifest,
            "archive_payload": {"offset": offset, "bytes": size, "sha256": payload.hexdigest()},
            "lexicon": lexicon, "frequency": frequency_info,
            "verification": {"source_files_unchanged": True, "packed_tables_match_cache": True}}


def markdown(data: dict) -> str:
    resources = data["fingerprints"]["resources"]
    rows = "\n".join(f"| {name} | {record['bytes']:,} | `{record['sha256']}` |" for name, record in resources.items())
    tables = "\n".join(f"| {name} | {record['rows']:,} |" for name, record in data["lexicon"]["tables"].items())
    references = "\n".join(f"- `{name}`：`{record['head']}`；工作区状态：`{'; '.join(record['status']) or 'clean'}`。" for name,record in data["references"].items())
    return f"""# Python 参考基线（P0.1）

本记录固定已安装 Lingose **{data['installed']['version']}**，不使用相邻源码库作为查询数据。机器可读完整记录见 [reference-baseline.json](reference-baseline.json)。

## 环境与实际路径

- Python：`{data['environment']['executable']}`，{data['environment']['python'].split(' (')[0]}；Unicode {data['environment']['unicode_version']}；SQLite {data['environment']['sqlite_version']}。
- 安装目录：`{data['installed']['package']}`。
- 实际只读查询库：`{resources['lexicon.sqlite']['path']}`。
- lexicon schema：{data['lexicon']['schema_version']}；data_version：`{data['lexicon']['build_info']['data_version']}`。
- 词条：{data['lexicon']['word_count']:,}；布尔分类：{sum(field['domain']=='category' for field in data['lexicon']['field_definitions'])}。
- 频率 schema：{data['frequency']['schema_version']}；原始行 {data['frequency']['table_counts']['frequency_record']:,}；词键 {data['frequency']['table_counts']['frequency_word']:,}；最大 NUMBER {data['frequency']['metadata']['max_rank']}，缺口 {data['frequency']['record_rank_gaps']}。
- frequency data_version：`{data['frequency']['metadata']['data_version']}`。

| 资源 | 字节 | SHA-256 |
| --- | ---: | --- |
{rows}

## 验证范围

- 7 个已安装模块及 3 个资源在审计前后摘要相同；读取路径须存在，拒绝 SQLite journal/WAL/SHM，使用 mode=ro 与 query_only。
- 两个数据库均通过 integrity_check 与 foreign_key_check；精确词键按 `word COLLATE BINARY` 枚举并记录摘要。
- 压缩包 payload 长度/摘要、{len(data['lexicon']['tables'])} 张表的 schema、行数和带类型逻辑摘要、显式索引均与实际缓存一致。逻辑行编码采用已固定 Python `_packed._encode_row`，排序采用 manifest 的 order。
- 缓存物理大小可与 manifest 的 database_bytes 不同；表内容一致性由逐表摘要证明，不依赖物理字节相等。
- 没有执行恢复、源库构建、维护事务或网络请求；本记录不是 Rust API、性能或发布验收。
- 相邻 0.2.1 的六个行为模块及两个分发数据资源与安装包一致；`__init__.py` 的版本/小写别名不同。Rust 按 README 实现四组别名。

| 缓存表 | 行数 |
| --- | ---: |
{tables}

## 只读参考身份

{references}

工作区已有差异仅记录，不修改或提交。完整相关文件摘要与状态保留在 JSON；后续参考变化须重新审计，不能静默覆盖本记录。

## 重现

```powershell
python -I -B -X utf8 tools/audit_reference.py --check
python -I -B -X utf8 -m unittest discover -s tests -p test_reference.py -v
```

初次缺少记录时使用 `--write`；已有记录不一致时拒绝覆盖。`--check` 不写产物。实际缓存缺失时先显式恢复到本项目隔离目录，并以 `LINGOSE_CACHE_DIR` 指定，再建立基线；本工具不会自动恢复。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Create absent records; never replace drift")
    mode.add_argument("--check", action="store_true", help="Check only (default)")
    arguments = parser.parse_args()
    data = capture()
    print(f"JSON: {freeze(BASELINE, json_text(data), arguments.write)}")
    print(f"Markdown: {freeze(ROOT / 'docs/reference-baseline.md', markdown(data), arguments.write)}")


if __name__ == "__main__":
    try:
        main()
    except (ReferenceError, OSError, ValueError, sqlite3.Error) as error:
        main_error(error)
