# Python 参考基线（P0.1）

本记录固定已安装 Lingose **0.2.0**，不使用相邻源码库作为查询数据。机器可读完整记录见 [reference-baseline.json](reference-baseline.json)。

## 环境与实际路径

- Python：`D:\Python\Python312\python.exe`，3.12.4；Unicode 15.0.0；SQLite 3.45.3。
- 安装目录：`D:\Python\Python312\Lib\site-packages\lingose`。
- 实际只读查询库：`C:\Users\Threadman\AppData\Local\lingose\cache\0e18bb818031f60d2d068f45dd4389ae0eafe2968758cb0d5813846b28498833\lexicon.sqlite`。
- lexicon schema：2；data_version：`17a1d0a15cbeec8e323b4a1750eccd88e372a65339e11bee3a7cf55c4f4b0dbd`。
- 词条：50,335；布尔分类：24。
- 频率 schema：1；原始行 5,061；词键 10,620；最大 NUMBER 5062，缺口 [30]。
- frequency data_version：`b6b9e367024c584afd814a8eac80a1f7abfa4b0cdbaa9ff20e810a28c34d0f09`。

| 资源 | 字节 | SHA-256 |
| --- | ---: | --- |
| lexicon.lpk | 89,292,019 | `cf0b3dd5aa7c5f89a88143c0503f089f82ccebd57aec1fc65e1cb3c5b65a3d96` |
| lexicon.sqlite | 1,023,238,144 | `ada92a2b51de23f9f82e403f3593e3b783311f8aaa34071d926f3546f84b52fe` |
| frequency.sqlite | 1,929,216 | `d8da3788e62ec7c2df27a9f7b148ef018e83c8ea5b189b72819a2a8c911ca269` |

## 验证范围

- 7 个已安装模块及 3 个资源在审计前后摘要相同；读取路径须存在，拒绝 SQLite journal/WAL/SHM，使用 mode=ro 与 query_only。
- 两个数据库均通过 integrity_check 与 foreign_key_check；精确词键按 `word COLLATE BINARY` 枚举并记录摘要。
- 压缩包 payload 长度/摘要、15 张表的 schema、行数和带类型逻辑摘要、显式索引均与实际缓存一致。逻辑行编码采用已固定 Python `_packed._encode_row`，排序采用 manifest 的 order。
- 缓存物理大小可与 manifest 的 database_bytes 不同；表内容一致性由逐表摘要证明，不依赖物理字节相等。
- 没有执行恢复、源库构建、维护事务或网络请求；本记录不是 Rust API、性能或发布验收。
- 相邻 0.2.1 的六个行为模块及两个分发数据资源与安装包一致；`__init__.py` 的版本/小写别名不同。Rust 按 README 实现四组别名。

| 缓存表 | 行数 |
| --- | ---: |
| build_info | 1 |
| candidate_origin | 4 |
| entry | 50,335 |
| entry_input | 50,335 |
| field_candidate | 4 |
| field_definition | 36 |
| field_value | 1,811,325 |
| input_manifest | 1 |
| ipsm_derivation | 50,004 |
| pronunciation | 50,090 |
| pronunciation_set | 50,335 |
| review_event | 656 |
| source_record | 195,527 |
| source_snapshot | 5 |
| value_origin | 1,618,527 |

## 只读参考身份

- `lingose-python`：`b36baf6d55fa259ecc38acea9e881ae6d1477d33`；工作区状态：`clean`。
- `lingose-typescript`：`27e6cce8cf968f1ce1bf246670c2c4a428d464dc`；工作区状态：` M tasks/handoff.md;  M tasks/todo.md; ?? docs/release-operation.md`。
- `chrome-extension`：`54fd0ec8d2485ab0dd14cc518e3ac78bad7a6daf`；工作区状态：`clean`。

工作区已有差异仅记录，不修改或提交。完整相关文件摘要与状态保留在 JSON；后续参考变化须重新审计，不能静默覆盖本记录。

## 重现

```powershell
python -I -B -X utf8 tools/audit_reference.py --check
python -I -B -X utf8 -m unittest discover -s tests -p test_reference.py -v
```

初次缺少记录时使用 `--write`；已有记录不一致时拒绝覆盖。`--check` 不写产物。实际缓存缺失时先显式恢复到本项目隔离目录，并以 `LINGOSE_CACHE_DIR` 指定，再建立基线；本工具不会自动恢复。
