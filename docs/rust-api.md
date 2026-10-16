# Rust 接口契约（P1.1）

本文件固定 `lingose` **0.1.0** 的 Rust 表达方式；业务语义继续由
[P0 行为契约](api.md)与[已安装 Python 基线](reference-baseline.md)约束。
当前已完成 P2.4 全部单词和分类查询，使用正式离线资源与共享加载器；
P3.1 已接入基础文本标注，范围见[标注说明](annotation.md)。简单查询验证见[查询说明](simple-queries.md)，分类验证见[分类说明](categories.md)，
全库公共 API 差分和最终性能验收仍属于 P4。

## 工具链和依赖

- `edition = "2024"`，声明的最低版本为 `rust-version = "1.85"`。
  选择该版本以使用当前 edition 的语言和依赖解析约定；
  [官方 Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/index.html)
  记录该 edition 随 1.85.0 发布。
- 最低版本目前**未实测**。本机只有 Rust/Cargo 1.93.1，已验证平台仅为
  `x86_64-pc-windows-msvc`；P5.2 在 1.85 上执行实际验证，不由高版本通过推断。
  不创建锁定开发机版本的 `rust-toolchain.toml`。
- P1.1 仅依赖标准库；P2.2 新增 `sha2` 0.10.9，用于一次性资源完整性校验；`build = false`。
  保留 `Cargo.lock` 用于本项目验证。P1.2 根据完整数据的实测选择加载依赖，
  Unicode 等依赖随具体实现引入；引入时核对 MSRV、许可、体积和离线行为。
  不预先绑定 Python、Node、SQLite、压缩库、网络客户端或异步执行器。
- P1.2 已比较完整数据布局并固定[静态镜像/共享索引方案](data-layout.md)与
  [性能预算](performance-budget.md)。P2.2 的[加载器/索引/并发与错误缓存](data-loader.md)
  已验证；P2.3/P2.4 已接入单词和分类查询，P3.1 接入基本直接标注。
- 正式 crate 的构建和运行不得读取开发机路径、相邻 checkout 或 Python 缓存。
  Python 工具及固定向量仅作开发对照，不在当前 Cargo `include` 分发清单中。
- `publish = false` 标识尚未就绪的工程。P5.3 在完整实现和相应检查通过后移除此保护，
  再执行打包及 dry-run；实际上传仍属于 P6。

## 同步函数与默认参数

所有入口都是 crate 根部的同步函数，无需创建客户端或启动运行时。字符串入参为
`&str`，不取走调用方所有权；返回值独立拥有内存。Rust 不支持 Python 的默认参数，
因此用默认入口和四个显式参数入口表达同一行为，不使用函数重载、宏或动态参数包。

下表的 `Result<T>` 均为 `std::result::Result<T, lingose::Error>`：

| Rust 签名 | Python 对应 |
| --- | --- |
| `ipa(word: &str) -> Result<Vec<String>>` | `ipa(word)` / `IPA(word)` |
| `ips(word: &str) -> Result<Vec<String>>` | `ips(word)` / `IPS(word)` |
| `ism(word: &str) -> Result<Option<String>>` | `ism(word)` / `ISM(word)` |
| `ipsm(word: &str) -> Result<Vec<String>>` | `ipsm(word)` / `IPSM(word)` |
| `root_lemma(word: &str) -> Result<Option<String>>` | `root_lemma(word)` |
| `meaning(word: &str) -> Result<Option<String>>` | `meaning(word, lang="en")` |
| `meaning_with_lang(word: &str, lang: &str) -> Result<Option<String>>` | 显式 `lang`，只接受精确 `en`、`zh` |
| `kind(word: &str) -> Result<bool>` | `kind(word, label="CET4")` |
| `kind_with_label(word: &str, label: &str) -> Result<bool>` | 显式分类，区分大小写 |
| `kind_list() -> Result<Vec<String>>` | `kind_list(label="CET4")` |
| `kind_list_with_label(label: &str) -> Result<Vec<String>>` | 显式分类 |
| `labels() -> Result<Vec<String>>` | `labels()` |
| `annotate_ips(text: &str) -> Result<String>` | `annotate_ips(text, skip_top=0)` |
| `annotate_ips_with_skip_top(text: &str, skip_top: i64) -> Result<String>` | 显式频率阈值 |

另外以 `pub use` 导出 `IPA`、`IPS`、`ISM`、`IPSM`，直接指向各小写函数，
不另写实现，也不要求调用者开启 feature。由此覆盖 P0 的 14 个名称/10 种行为，
另有四个用于默认参数表达的辅助入口。没有公开 `lookup` 或 `rank`。

## 返回值与内部状态

- 发音返回 `Vec<String>`，三类列表独立；不得按索引假定 IPA、IPS、IPSM 配对。
- 构词、词族和释义返回 `Option<String>`，保留原始 Unicode、换行与文本，
  不为缺失字段生成新值。
- 分类成员为 `bool`，分类词表与标签是 `Vec<String>`，分别保留 P0 的业务排序
  与配置顺序。内部的 false、缺失和错误不得使用通用真值判断合并。
- 标注返回完整 `String`。所有结果可脱离输入生命周期保留，并可由调用者修改；
  公共接口不暴露内部存储结构、锁、缓存或 Python 审核字段。
- 最终实现使用共享只读数据以支持并发调用；加载、初始化、内部索引、内存及结果复制
  成本在 P1.2 用真实完整数据比较。拥有所有权的公共结果不迫使每次重载词库。

完成实现后的合法未知词/不可用结果是 `Ok(Vec::new())`、`Ok(None)` 或 `Ok(false)`；
合法空分类列表也是成功结果。P1.1 不返回这些占位值，也不将资源失败吞掉。

## 参数与错误映射

`Error` 是带 `#[non_exhaustive]` 的结构化枚举，实现 `Debug`、`Display`、
`std::error::Error`，当前也实现 `Clone`、`Eq`、`PartialEq`。
调用方须保留兜底匹配；文案仅供诊断，不要求与 Python 文案逐字一致。

| Python 状况 | Rust 表达 |
| --- | --- |
| 字符串、整数类型错误 | `&str` / `i64` 在编译期约束，不模拟动态 `TypeError` |
| word 内容、语言、分类、text NUL、负阈值错误 | `Error::InvalidArgument { parameter, reason }`，参数名区分错误来源 |
| `LexiconDataError`，含缺失、不可读、损坏资源 | `Error::Data { resource, message }` |
| 其子类 `SchemaVersionError` | `Error::IncompatibleDataVersion { resource, expected, found }` |
| 当前尚未实现的合法调用 | 过渡性的 `Error::NotImplemented { operation }` |

Rust 没有异常继承，按资源失败统一处理时需同时匹配 `Data` 和
`IncompatibleDataVersion`。`resource` 是逻辑资源名，不是开发机必需路径。
版本字符串不预设未来数据布局，P1.2 再固定内部格式；错误不得转成未知词结果。

验证顺序固定为：

1. Rust 类型检查取代 Python 参数类型检查。Rust 调用形式本身排除错误参数数量、
   Python 关键字位置及非字符串、bool/浮点数阈值等输入。
2. 单词查询先检查 word：非空、无 NUL、无首尾 Python `str.strip()` 空白；
   再检查 meaning 的语言值；再加载并验证所需资源；最后验证分类标签并执行查询。
   `kind_list` 无 word 步骤，`labels` 仅需资源检查。
3. 标注先检查负阈值，再检查 text NUL；空文本和首尾空白合法。随后按基线规则
   分词，无可转换英语词段则原样返回且不访问资源；阈值为 0 时不访问频率数据。
   分词和这些无需资源的成功路径留给 P3 实现。

word 的空白集合固定为 Python 3.12 / Unicode 15.0 的 29 个字符：
U+0009–000D、001C–0020、0085、00A0、1680、2000–200A、2028、2029、202F、205F、3000。
这包含 Rust 通常的 `char::is_whitespace()` 之外的 U+001C–001F，因此不直接使用
`trim()`。内部空格、撇号、连字符及 U+200B 等非空白字符不清洗、不规范化。
此处只是输入验证，不预先实现查询大小写或标注 Unicode 算法。

P2.3 简单查询先精确匹配词键，存在即停止（包括字段不可用）。只有精确词条不存在、
首字符为 Python `isupper()` 且后续每个字符均不是大写时，才尝试一次有变化的
`word.lower()`。返回已保存原值，不按输入调整输出大小写。固定 Unicode 15.0 表
来自已审计 CPython，保留标题字符、单字符展开和非 BMP 行为；
见[生成身份](query-case.json)及[Unicode 许可](../third_party/unicode/LICENSE.txt)。
标注使用另一套规则，不能复用此简单查询回退函数。

`skip_top` 选择 `i64`，便于 Rust 调用方传入并获得负数的内容错误。
非负值最终按 `min(skip_top, 5062)` 解释；`i64::MAX` 也合法。
Rust 不直接接受任意精度 Python 整数。P4 向量适配器读取 `{"$integer":"..."}` 时，
须先按十进制文本判断符号并与 5062 比较，负数映射参数错误，超上限值映射 5062，
然后才转换为有限宽整数；不能先解析为 i64 而溢出。该适配器尚未实现。

## 当前实现与阶段边界

- 已实现所有签名、别名、默认入口转发、错误表示和 word/lang/text/负阈值验证。
- ipa/IPA、ips/IPS、ism/ISM、ipsm/IPSM、root_lemma 和 meaning/meaning_with_lang
  已实现。资源成功加载后的未知/不可用值返回空 Vec 或 None，空字符串及原文保留；
  三种发音列表独立投影，IPSM 不重算、不补用未采用或过期候选。
- kind/kind_with_label、kind_list/kind_list_with_label、labels 已实现。分类标签精确匹配
  已验证资源注册表（不硬编码）；默认 CET4。kind 在 word 验证及资源加载后验证 label，
  然后按简单查询规则查词；未知词及 unavailable/false 为 false，精确不可用词条阻断小写回退。
  kind_list 直接复制已冻结业务顺序的完整实际词键；labels 保留配置顺序，结果拥有所有权。
- P3.1 标注已支持完整词段扫描、直接 IPS、字符簇对齐/大小写与未知词中括号。
  空文本或没有完整英语词段时原样返回，不访问资源；零阈值不访问频率。
  标注按精确→直撇号→小写→小写直撇号搜索，首个存在词条即停止，独立于简单查询规则。
  `the` 上下文、缺源后的复合/缩写/词形回退留给 P3.2，当前只使用保存的直接值。
  有英语词段且正阈值时仍返回 `NotImplemented`，operation 为 `annotate_ips_with_skip_top`；
  P3.3 实现前不静默忽略频率请求。该分支在调用资源加载器之前返回。
- `Data` / `IncompatibleDataVersion` 的资源校验、缓存已在 P2.2 验证，P2.3 同一路径的
  查询夹具证实 word/lang 验证先于资源加载，未知词仍传播加载错误，且不访问频率。
  P2.4 已验证分类标签错误、完整词表及全部精确词键的成员关系；标注及全部接口的联合差分留给 P3/P4。
- 在 P5.1 发布文档收口前移除 `NotImplemented` 变体及所有占位返回；不在首版分发。

基础示例为 [query.rs](../examples/query.rs) 和 [annotate.rs](../examples/annotate.rs)。
README 的查询、基础标注与参数错误示例用 rustdoc 实际执行。
`tests/api_contract.rs` 验证函数签名、拥有所有权的结果类型、别名/默认入口、参数边界与
标注接口当前阶段边界；112 条固定 P0 查询断言位于 `tests/query_vectors.rs`，分类 P0 向量
位于 `tests/category_vectors.rs`，含全部 24 分类的完整有序词表摘要及默认 CET4 入口。
验证证据见[查询说明](simple-queries.md)，精确恢复动作记录在 [handoff](../tasks/handoff.md)。

Cargo 的 `rust-version` 用法及其验证预期参见
[官方说明](https://doc.rust-lang.org/cargo/reference/rust-version.html)；
元数据及分发清单语义参见
[manifest reference](https://doc.rust-lang.org/cargo/reference/manifest.html)。
