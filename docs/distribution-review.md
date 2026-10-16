# P5.1 文档、元数据与分发声明核对

本记录核对文档与来源声明，并给出 P5.3 要采用和实际验证的分发清单。
它不代表已完成归档、最低版本或发布验收。`Cargo.toml` 的 `publish = false`
及现有过渡 `include` 在本阶段保留，**现有 include 缺少编译必需数据，不能作为发布清单**。

## 元数据与公共文档

- Cargo 名称 `lingose`，版本 `0.1.0`，作者 `ZHAN Xianjue`，项目许可证 `CC-BY-4.0`。
  原有元数据符合需求，无须更换；edition 2024，声明 MSRV 1.85 仍待 P5.2 实测。
- Cargo 与 [README](../README.md) 均保留官网 https://lingose.com/ 和用户指定的
  https://github.com/englishword；未添加未经核实的具体仓库地址。
- README 的接口表及 [Rust 契约](rust-api.md) 覆盖 18 个入口、四组大小写别名、
  默认值、完整 owned 结果、错误、独立发音列表、精确/小写匹配、分类顺序、纯文本
  标注及频率边界。README 五个 Rust 代码块由 crate rustdoc 编译/执行。
- [query.rs](../examples/query.rs) 与 [annotate.rs](../examples/annotate.rs) 是可运行示例。
  资源随源码嵌入，无 build script 或词库下载；离线 Cargo 构建仍需已获取软件依赖。
- 已移除开发期 `NotImplemented` 错误及差分探针映射；现有公共契约断言已是实际成功
  或具体错误断言，无占位返回需要替换。

## 来源与许可资料边界

作者及所有既有第三方署名、软件版本和许可链接继续由 [SOURCES](../SOURCES.md)
保留。项目 [LICENSE](../LICENSE) 与原始 [UPSTREAM-SOURCES](../data/UPSTREAM-SOURCES.md)
分别与 P0 固定 Python 参考逐字节相同；Unicode 完整 [许可](../third_party/unicode/LICENSE.txt)
保持原样。独立只读审阅也核对了这些身份。
原始 UPSTREAM-SOURCES 的相对 `(LICENSE)` 链接位于 data/ 下；新增逐字节相同的
`data/LICENSE` 使它可直接解析，并以 Git `-text` 规则保护两个许可副本的原始字节。

`data/SOURCES.json`、`data/manifest.json`、生产二进制及派生 Unicode 表是受保护产物，
本轮不修改。`data/SOURCES.json` 内“P5.1 待审查”的文字记录 P2.1 生成时的状态，
本记录和当前 SOURCES 是后续审查说明，不能为更新状态而重写历史摘要。

固定参考缺少 Frequency List 的独立许可文本，以及部分外部分类词表逐标签来源/许可
记录；SOURCES 已明确记录。Phonemizer/eSpeak NG/ECDICT 的署名与许可链接也是
上游保留声明；本轮没有取得其新增授权或补全未提供的许可全文。
项目 CC BY 4.0 不作为第三方材料的授权证明。P6.1 必须核对这些资料缺口的处置状态，
不能将 P5.1 的声明核对描述成所有第三方分发条件已核实。

## P5.3 候选 include 与链接闭包

以下为本轮核对的**候选文件范围**，不是已生成的 `.crate` 文件清单。
P5.3 更新 Cargo include 后，须对真实 `cargo package --list` 和归档解包内容再核对。

| 范围 | 必需文件及用途 |
| --- | --- |
| 源码与示例 | `/src/**`、`/examples/**`；包含生成常量和实际使用的 Unicode 表 |
| 用户文档与项目声明 | `/README.md`、`/LICENSE`、`/SOURCES.md` |
| 生产资源 | `/data/lexicon.bin`、`/data/frequency.bin`；`src/data/mod.rs` 编译时直接嵌入 |
| 数据版本与来源 | `/data/manifest.json`、`/data/SOURCES.json`、`/data/UPSTREAM-SOURCES.md`、`/data/LICENSE`（原始声明的相对许可链接） |
| 派生表许可 | `/third_party/unicode/LICENSE.txt` |
| README 接口链接 | `/docs/rust-api.md` |
| SOURCES 和接口契约的来源链接 | `/docs/query-case.json`、`/docs/annotation-unicode.json`、`/docs/loader-verification.json` |

上述用户 Markdown 的全部本地链接在候选范围内，包括叶文档和原始来源声明。
JSON 中的生成器、源库路径和摘要仅为历史来源记录，不是构建或运行时依赖。
Cargo 元数据及其自动生成/添加的文件由 P5.3 实测记录，不预先伪造归档身份。
维护数据库、Python 缓存、相邻 checkout、`.local`、开发工具和开发任务记录不列入候选范围。

## 当前验证与历史证据

本轮检查及受保护身份核对见 [p5-documentation-verification.json](p5-documentation-verification.json)。
P4.1/P4.2 的固定原始 JSON 保持不变。当前 README、SOURCES、`src/error.rs`、
公共测试说明和差分桥源码与它们记录的输入身份已不同；这些历史报告不能称为当前
输入或最终归档的新验证。未改变查询/标注算法、资源或依赖，不重测性能来覆盖旧报告。

本轮最小验证覆盖文档代码块、已有 Rust 回归、差分桥 smoke、示例、文档构建、格式、
Clippy、元数据、候选范围内链接及声明身份；不将 smoke 计为 1,862,690 项全量重验。
P5.2 执行工程必需检查和 MSRV 实测；P5.3 验证真实归档、独立离线消费及 dry-run；
P6 再核对正式发布条件。阶段和平台范围分别记录。
