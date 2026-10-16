# P2.4 分类与完整有序词表

已实现 `kind`、`kind_with_label`、`kind_list`、`kind_list_with_label` 和 `labels`。
接口、所有权及参数表达保持 [Rust 契约](rust-api.md)，采用规则遵循 [P0 契约](api.md)。
标注尚未实现，`NotImplemented` 仍为过渡错误；打包及发布保护不变。

## 实现与行为

`src/category.rs` 复用 `data::lexicon()` 的共享只读资源。标签来自已验证资源注册表，
按精确字符串查找，不清洗、不转大小写，也不在代码中硬编码注册标签。
最多扫描 32 个合法注册项；标签位置在使用分类位图前已验证范围。没有新增数据索引、
Cargo 依赖或资源。分类查询不读取频率资源。

- `kind(word)` 默认 CET4；显式入口先验证 word，再加载资源，再验证 label，最后查词。
  资源错误不能变成 false，也不能被非法标签遮蔽。未知词配非法标签仍报 label 参数错误。
- 查词复用 P2.3 的精确优先及 Unicode 15.0 条件小写回退。精确词条的 false 或不可用分类
  不允许借小写 true 补值；分类不依赖发音、IPSM 或标注资格。
- `kind_list()` 默认 CET4；显式入口先加载资源，再验证标签，复制保存的全部有序成员。
  实际词键、大小写、Unicode 和业务顺序保持原样，不生成别名。空注册分类返回空 Vec。
- `labels()` 只需资源，返回配置顺序的注册布尔分类；COLLINS 和 Band 不是此注册表的分类。
  空注册表可成功返回空列表。所有列表及其字符串均拥有所有权。

P2.1 已按 root/rank 可用性、原始词族、rank 文本及实际词键排序，并独立对照 Python。
P2.2 解析器验证完整成员范围、无重复、位图与词表的等价性；P2.4 直接使用 `Image.members`
的顺序，不在运行时重新猜测排序。内部 rank 未成为公共 API。

## 验证

本轮仅在 Windows MSVC / Rust 1.93.1 上验证。完整原始测试输出、最小副本输入 SHA-256、
工具链及命令记录在 [category-verification.json](category-verification.json)。

- `tests/category_vectors.rs` 由 `tools/generate_category_vectors.py` 从未修改的 P0 Python
  fixture 生成，固定源摘要，拒绝覆盖已有不同字节。24 个标签的顺序完全匹配。
- P0 分类测试覆盖 16 条成员结果、7 条单词/标签参数错误、3 条词表标签错误。
  24 个显式完整词表加默认 CET4 词表，共 25 个调用逐项核对长度、完整有序 UTF-8 JSON
  SHA-256 及首尾；24 类合计 209,759 个成员，含默认重复调用实际核对 214,984 项。
  每个返回成员也通过公共 `kind_with_label` 验证为 true。
- 完整列表摘要覆盖全部内容，未用首尾样本替代完整顺序。测试期 JSON 序列化器另用 Python
  独立生成的空列表、空字符串及含控制符/Unicode/非 BMP 的三组字节样例核对。
- 公共成员查询遍历 50,335 个精确词键与全部 24 类，共 1,208,040 组 true/false 结果，
  与上述完整词表成员集一致；另逐类检查未知词 false。
- 独立 wire 夹具覆盖非字典序注册表/成员顺序、空分类、零标签注册表、最高第 31 位、
  精确 false/缺失阻断小写 true、非默认分类与非 BMP/Unicode 原词，以及拥有所有权的输出。
- 缓存夹具通过公共入口共用的内部路径验证 word→资源→label 的优先级，
  Data/IncompatibleDataVersion 传播与单次缓存、三个分类入口均不访问频率资源。
  公共列表修改和 16 线程调用不影响其他结果。
- 新增 Python 隔离投影测试覆盖 false、missing、pending_review、conflict、invalid 分类字段，
  核对采用位图及 Python kind/kind_list，证明精确不可用字段不会从小写值补洞。
  311 条固定 Python 向量重新只读核对通过，安装包/源码/数据库前后身份不变。
- 34 项 Rust 库测试、10 项公共契约、1 项简单查询向量、5 项分类向量测试和 5 文档测试通过；
  唯一忽略项是需显式执行的 P2.2 加载器性能探针。56 项 Python 回归、fmt、Clippy 全目标
  全 feature -D warnings、文档构建与真实查询示例通过。
- `tools/check_queries.py --categories` 在最小 Cargo/src/资源/测试副本执行离线 locked
  release 构建，四个测试二进制在仅含二进制、无源码及资源文件的目录独立运行通过。
  P2.3 的 query-verification.json 历史证据保留，P2.4 写入独立报告。

```powershell
$env:CARGO_HOME = Join-Path (Get-Location) '.local/cargo-home'
python -I -B -X utf8 tools/generate_category_vectors.py --check
cargo test --offline --locked --test category_vectors
cargo test --offline --locked --all-features
cargo clippy --offline --locked --all-targets --all-features -- -D warnings
python -I -B -X utf8 tools/check_queries.py --categories
```

上述结论验收分类接口及其完整数据；P4 仍需对所有查询字段和完整标注进行联合差分，
并测量真实 release 性能。MSRV、其他平台、.crate 离线消费和发布尚未验收。
