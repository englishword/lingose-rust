# Rust 接口契约（0.2.0 开发中）

本文件说明 `lingose` **0.2.0** workspace 迁移后的当前接口，沿用 0.1.0 行为；
显式阈值入口现为 `annotate_ips_skip`。覆盖已安装 Python Lingose 0.2.0
的十种公共行为及四组大小写名称；小写别名同时对应 Python 0.2.1 README。
全部接口均已实现，基础用法见 [README](../README.md)。不提供公开的 `lookup` 或 `rank`。

<a id="from-010"></a>

## 从 0.1.0 迁移

`annotate_ips_with_skip_top(text, skip_top)` 已更名为
`annotate_ips_skip(text, skip_top)`，旧名称移除且不保留别名。
签名仍为 `(&str, i64) -> Result<String>`，校验、阈值上限、资源加载顺序和输出不变；
`annotate_ips(text)` 继续等价于新入口的零阈值调用。

```rust
fn main() -> lingose::Result<()> {
    let annotate: fn(&str, i64) -> lingose::Result<String> = lingose::annotate_ips_skip;
    assert_eq!(annotate("Abandon the book.", 5062)?, "Abandon the book.");
    assert_eq!(lingose::IPA("apple")?, lingose::ipa("apple")?);
    Ok(())
}
```

库依赖配置见 [README](../README.md#add-the-library)。0.2.0 尚未发布；文档中的
注册表安装示例是发布后用法，当前使用本地 path 依赖。CLI 是独立的 `lingose-cli`
包，二进制名为 `lingose`；CLI 的六字段 word 输出不缩减下表的库能力。

## 同步函数与默认参数

所有入口都是 crate 根部的同步函数，无需创建客户端或启动运行时。字符串入参为
`&str`，返回值独立拥有内存。Rust 通过默认入口和四个显式参数入口表达 Python 默认参数。

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
| `annotate_ips_skip(text: &str, skip_top: i64) -> Result<String>` | 显式频率阈值 |

另外以 `pub use` 导出 `IPA`、`IPS`、`ISM`、`IPSM`，直接指向各小写函数，
不要求开启 feature。共 18 个公共函数入口；`Error` 和 `Result<T>` 从 crate 根部导出。

## 返回值与匹配规则

- 发音返回 `Vec<String>`，三类列表独立，不得按索引假定 IPA、IPS、IPSM 配对。
  只投影已选择且有效的采用值，不补用待审、冲突或无效候选。
  IPSM 还要求保存的 IPS/ISM 依赖仍有效；运行时不重算。
- 构词、词族和释义返回 `Option<String>`，保留原始 Unicode、换行和空字符串，
  不为缺失字段生成新值。`root_lemma` 返回已保存词族，不运行新的词形还原。
- 查询先精确匹配词键，存在即停止，包括字段不可用或分类 false。
  只有精确词条不存在、首字符为 Python `isupper()` 且后续每个字符均不是大写时，
  才尝试一次有变化的 `word.lower()`。不调整返回值的大小写。
- 分类标签精确匹配已验证资源注册表，默认 `CET4`。`kind_list` 返回完整原始词键，
  保留固定 Python 词族/rank/原词业务顺序；`labels` 保留配置顺序。
  `COLLINS`、`Band` 等非布尔属性不属于注册分类。
- 合法未知词/不可用结果是 `Ok(Vec::new())`、`Ok(None)` 或 `Ok(false)`；
  注册的空分类返回成功的空列表。资源错误始终与这些结果区分。
- 所有结果拥有内存，可脱离输入生命周期保留或修改；并发调用共享只读索引，
  不因返回 owned 值而重复解析全库。

查询大小写固定为 Python 3.12 / Unicode 15.0，不随编译器 Unicode 版本改变。
派生表身份见 [分发来源摘要](distribution-provenance.json)，完整许可见
[Unicode License V3](../third_party/unicode/LICENSE.txt)。标题字符、展开及非 BMP
字符按固定基线处理；不做通用 Unicode 清洗或规范化。

## 纯文本标注

标注扫描固定 Python Unicode 字母/数字/组合符词段，只有整个词段符合
`[A-Za-z]+(?:[-'’][A-Za-z]+)*` 才转换；数字或非英语字符相连的整个词段原样保留。
空白、CR/LF、标点、非英语片段及原始大小写保留；该接口不解析 HTML。

直接查找依次为精确词、直撇号形式、小写、小写直撇号形式。首个存在词条即停止，
规则独立于简单查询。`the` 根据相邻英语词段首字母选择读音；只跨允许的空白和
引号/括号，不跨阻断标点或空行。已存整词优先，状态阻断先于上下文和拆词。
缺源后支持明确缩写、连字符、直/弯撇号及 s/es/ed/ing 回退；词形候选有阻断或
产生不同输出时保留中括号。无法对齐的词或未知部分输出 `[原词]`。
推导只作用于返回文本，不更新词库或单词查询。

`skip_top` 是 `i64`，负数报参数错误，非负数按 `min(skip_top, 5062)` 解释，
`i64::MAX` 合法。以原始 `NUMBER <= skip_top` 屏蔽已存词与词形，包含等于阈值
及原始编号缺口；重复键用最小编号，不生成额外屏蔽词形。频率屏蔽先于状态和推导；
完整短语和带标点形式按最长优先及 Unicode 边界保护。

没有完整英语词段时不访问任何资源。零阈值只访问主词库；正阈值先验证频率，
再验证主词库，即使全部词都被屏蔽也传播主词库错误。分词、对齐和大小写表身份见
[分发来源摘要](distribution-provenance.json)，同样保留 Unicode 许可。

## 参数与错误映射

`Error` 带 `#[non_exhaustive]`，实现 `Debug`、`Display`、`std::error::Error`、
`Clone`、`Eq`、`PartialEq`。调用方匹配时须保留兜底分支；错误文案仅供诊断。

| Python 状况 | Rust 表达 |
| --- | --- |
| 字符串、整数类型错误 | `&str` / `i64` 在编译期约束，不模拟动态 `TypeError` |
| word 内容、语言、分类、text NUL、负阈值错误 | `Error::InvalidArgument { parameter, reason }` |
| `LexiconDataError`，含缺失、不可读、损坏资源 | `Error::Data { resource, message }` |
| 其子类 `SchemaVersionError` | `Error::IncompatibleDataVersion { resource, expected, found }` |

Rust 没有异常继承，统一处理资源错误时需同时匹配 `Data` 和
`IncompatibleDataVersion`。`resource` 是逻辑资源名，不是开发机必需路径。

验证顺序固定为：

1. Rust 类型及函数签名排除错误类型、参数数量和 Python 关键字调用形式。
2. 单词查询先检查 word：非空、无 NUL、无首尾 Python `str.strip()` 空白；
   再检查 meaning 的语言；再加载并验证资源；最后验证分类标签并查询。
   `kind_list` 无 word 步骤，`labels` 仅需资源检查。
3. 标注先检查负阈值，再检查 text NUL；空文本和首尾空白合法。随后分词，
   没有可转换词段时返回原文；否则按上述阈值规则访问资源。

word 的空白集合固定为 Python 3.12 / Unicode 15.0 的 29 个字符：
U+0009–000D、001C–0020、0085、00A0、1680、2000–200A、2028、2029、202F、205F、3000。
包含 Rust 常用空白集合之外的 U+001C–001F，因此不直接使用 `trim()`。
内部空格、撇号、连字符及 U+200B 等非空白字符不清洗、不规范化。

Rust 不直接接受 Python 的任意精度整数。开发期对照适配器先根据十进制文本判断
符号及 5062 上限，负数映射参数错误，超上限映射 5062，再转换为 i64；
Python 的动态类型错误不计为 Rust 运行时接口。

## 离线资源与验证范围

正式构建使用随包二进制资源，无 build script 或下载步骤；安装 Cargo 依赖后可离线
构建和运行。首次访问验证资源格式、版本及摘要，成功索引和初始化错误分别缓存，
支持并发调用。生产运行无需 Python、Node、SQLite、额外配置或相邻 checkout。
资源版本和计数见 [data/manifest.json](../data/manifest.json)，来源声明见
[SOURCES.md](../SOURCES.md)。

Edition 2024，MSRV 为 1.85。CLI4.1 已在 Windows x86_64 MSVC 的 Rust/Cargo
1.85.0 和 1.93.1 对 0.2.0 workspace 验证：各 131 项 Rust 测试、6 项文档测试，
以及 Clippy/doc；全量公共差分 1,862,690 个完整结果零差异。原固定预热后的运行时间、
资源和内存预算通过，新路径首启 675.43 ms 仍超 300 ms，单列保留；CLI 进程/I/O
另测，不混入库预算。详见
[新版验收说明](https://github.com/englishword/lingose-rust/blob/main/docs/cli-workspace-acceptance.md)。
旧版契约和收据保留原文，不能用作新版归档或其他平台验收。

本轮用户文档的示例编译/运行另行留证；尚无 0.2.0 真实归档或注册表消费，
两包仍为 `publish=false`。CLI4.3 才进入本地真实库归档、隔离 CLI 候选及库 dry-run；
CLI5 的多平台 CI、CLI6 的 CLI 注册表 dry-run/上传/注册表验收按各阶段记录。
官网为 [lingose.com](https://lingose.com/)，仓库为
[englishword/lingose-rust](https://github.com/englishword/lingose-rust)；链接配置本身
不代表 Git remote、远端权限或发布已验证。
