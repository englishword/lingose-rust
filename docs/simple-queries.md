# P2.3 简单查询

已实现 `ipa`/`IPA`、`ips`/`IPS`、`ism`/`ISM`、`ipsm`/`IPSM`、`root_lemma`、
`meaning`/`meaning_with_lang`。公共签名和所有权继续遵循 [Rust 契约](rust-api.md)，
业务采用规则遵循 [P0 契约](api.md)。P2.4 分类查询另见[分类说明](categories.md)；
文本标注、P4 全库公共 API 差分及性能验收仍未完成；打包保护和发布阶段不变。

## 查询与资源

`src/query.rs` 先验证 word，再验证可选语言，然后取得 `data::lexicon()`。各调用
共享 P2.2 的已验证只读数据及索引，不访问频率资源，不重复解析词库。
`Lexicon::find` 先查精确键；存在该词条就停止，不因某个字段缺失再查小写词条。
只有不存在精确词条、首字符为大写且剩余字符都不是大写时，才尝试一次有变化的小写形式。
未知词和不可用字段在成功加载资源后返回空列表/None；Data 和 IncompatibleDataVersion
直接传播，且错误仍由独立 OnceLock 缓存。

发音字段各自从已验证投影读取，不依赖另一发音列表、标注资格或列表索引配对。
IPSM 直接使用 P2.1 已校验依赖的有效采用值，不再计算候选。可选字段保留空字符串、
`"0"`、组合符、非 BMP 字符、原始换行和文本；返回值均拥有所有权，调用方修改不会影响缓存。

## Unicode 15.0

`src/query_case.rs` 和静态 `src/query_case_tables.rs` 固定已审计 CPython 3.12.4 /
Unicode 15.0 的 `isupper()` 与单字符完整小写映射，不调用 Rust 编译器自带 Unicode
分类或大小写转换。共有 651 个大写范围（1,951 个字符）及 1,433 条有变化的小写映射，
表源码 52,751 字节；没有新增 Cargo 依赖或构建脚本。

这不是仅按 ASCII 或 Lu 类判断：罗马数字和带圈大写也可触发回退，标题字符 `ǅ`
不能作为大写首字符，但可在后续位置并转换为 `ǆ`；`İ` 转换为 `i` + U+0307。
数学大写字符可被判为大写而没有小写变化，这时不生成重复变体。
Unicode 15 之后分配的字符保持基线未分配时的行为，不随编译器升级改变。

默认小写的唯一非语言限定上下文规则 Final_Sigma 需要 Σ 前存在 cased 字符。
简单查询回退条件不允许后续位置出现大写 Σ；它只能是首字符，因而永远没有前置字符，
无法触发此规则。该输入域使用单字符完整小写映射与 Python 整串 `lower()` 一致。
本辅助函数仅用于简单查询，不能用于未来文本标注的任意字符串小写。

[query-case.json](query-case.json) 固定生成器、Python/Unicode 版本、输入/输出摘要、
字符数及全字符逻辑摘要；生成器不联网，拒绝覆盖已有不同内容，前后核对输入身份。
Unicode 许可从已审计 TypeScript 参考复制，参考 HEAD/工作区状态和原文件摘要均记录，
没有修改相邻项目。完整 [Unicode License V3](../third_party/unicode/LICENSE.txt) 随表保存。

## 验证与复现

本轮环境仅为 Windows MSVC / Rust 1.93.1，未声明跨平台或最低版本已通过。
[query-verification.json](query-verification.json) 保存最小副本的完整输入摘要、
离线 release 构建命令、工具链和原始测试输出。

- 112 条固定 P0 snapshot 简单查询断言匹配 Python，涵盖大小写、未知词、两种语言和四组别名。
  `tools/generate_query_vectors.py` 只从固定 P0 文件生成断言，不从 Rust 结果生成预期值。
- 独立 wire 夹具覆盖精确不可用词条阻断小写、空字符串、独立发音投影、失效 IPSM 不补值、
  原始文本和 Unicode 回退；缓存夹具覆盖参数/加载顺序及两类资源错误传播。
  P2.1 的 55 项 Python 回归继续验证已采用候选、缺失/待审/冲突及派生依赖过滤。
- Unicode 测试枚举全部 1,112,064 个合法 scalar，对比 Python `isupper`/单字符 `lower`
  的完整逻辑摘要，并单独测试回退条件、标题字符、展开、Sigma 及基线之后的字符。
- 16 线程公共调用结果相同；拥有所有权的输出可脱离输入并修改，不影响后续查询。
- 最小 Cargo/src/资源/测试副本执行离线 locked release 构建；只复制三个测试二进制到
  无资源、无源码的目录运行，通过 30 项库测试、9 项契约测试和含 112 断言的向量测试。
  唯一忽略项是 P2.2 手动加载器性能探针，本轮没有重测历史性能。
- fmt、全目标全 feature Clippy（`-D warnings`）、5 项文档测试、文档构建及 55 项
  Python 回归通过。查询示例可实际离线运行。源库、受保护资源和 P0 固定向量未修改。

```powershell
$env:CARGO_HOME = Join-Path (Get-Location) '.local/cargo-home'
python -I -B -X utf8 tools/generate_query_case.py --check
python -I -B -X utf8 tools/generate_query_vectors.py --check
cargo test --offline --locked --all-features
cargo clippy --offline --locked --all-targets --all-features -- -D warnings
python -I -B -X utf8 tools/check_queries.py
```

此处验证 P2.3 的样例和隔离路径；P4 仍需对所有词条逐字段调用公共 API 差分，
并按原预算测量真实 API 和完整标注。没有执行 Cargo 打包、dry-run 或上传。
