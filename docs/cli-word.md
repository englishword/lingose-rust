# CLI3.1：命令入口和单词查询

从干净的 `main` / `ee435dc` 恢复，完成 `word WORD [--json]` 及标准
help/version。具体命令、日志摘要、源码身份见
[cli-word-verification.json](cli-word-verification.json)，原始日志在
`.local/cli31-word/`。

## 行为

```sh
cargo build -p lingose-cli --offline --locked
lingose --help
lingose --version
lingose word --help
lingose word hello
lingose word hello --json
```

命令示例使用构建所得的 `lingose`（Windows 为 `lingose.exe`）。
普通输出按以下顺序逐行显示六个字段，值采用 JSON 编码：

```text
word: "hello"
ipa: ["hələʊ"]
ips: ["he̊llō"]
ism: "hello"
ipsm: ["he̊llō"]
root_lemma: "hell"
```

JSON 模式返回一个对象，严格只有 `word`、`ipa`、`ips`、`ism`、`ipsm`、
`root_lemma`；键顺序不作保证。三组发音各自为字符串数组，ISM/root lemma
为字符串或 null。CLI 逐项调用库，不配对、补齐或截断发音，不增加释义、
分类或审核字段，不复制业务算法。`word` 保留用户输入的拼写。

合法未知词成功返回空数组和 null。参数解析或库参数校验失败退出 2，
资源及输出 I/O 失败退出 1，成功/help/version 退出 0。
查询全部成功后才写结果，stdout 仅含结果或 help/version，stderr 仅含错误。
输出写入及 flush 错误被传播；关闭 stdout 的进程测试确认退出 1，未 panic。
字面上以连字符开头的词可以写为 `lingose word -- --help`。

## 依赖与验证

- [Clap 4.6.7](https://docs.rs/clap/4.6.7/clap/) 使用 builder API，仅启用
  `std`、`help`、`usage`、`error-context`，关闭默认功能，不使用 derive、颜色或建议。
  [serde_json 1.0.154](https://docs.rs/serde_json/1.0.154/serde_json/) 使用默认 `std`。
  具体直接/传递版本由根 `Cargo.lock` 锁定；库 crate 的依赖和代码未改。
- Windows x86_64 MSVC / Rust 1.93.1：新增 3 项 CLI 单元测试和 8 项进程测试通过；
  workspace 合计 113 项 Rust 测试、6 项文档测试通过，1 项既有手动 loader 探针仍忽略。
  fmt、Clippy `-D warnings`、doc 及 15 项 workspace 工具 Python 回归通过。
- 使用已有隔离 Rust 1.85.0 工具链和独立 target，实际编译并通过全部 11 项 CLI 测试；
  依赖准备后，以上 Cargo 验证均为 `--offline --locked`。
- 进程测试对照库完整六字段，覆盖大小写、Unicode、组合符、引号/反斜线、
  字符串内换行、未知词、字段不可用、参数错误、help/version、前导连字符和关闭 stdout。
  `Marxism` 的真实输出有 IPA/IPS 而没有 IPSM，确认三组列表独立。
- 当前固定库每组最多返回一条采用发音；多发音验证明确使用合成输出 fixture，
  长度分别为 2/1/3，检查两种格式均保留全部值，不冒充真实词库样例。
- 从空运行目录启动当前源码构建的二进制，16 个词的 80 个字段与固定 P0
  snapshot 期望值逐项一致；help/version 正常，目录仍为空。
  此项只使用 P0 中成功的字符串查询；非法输入另由进程测试验证。
  没有重新运行 Python oracle，也没有把空目录运行称作独立归档消费。
- 独立只读复核未发现阻塞问题。150 个范围外原有受控文件逐字节一致，包含
  整个库 crate、词库、P0 期望值、Unicode 表、许可证、探针、历史收据与报告。

本轮仅验证 Windows 本地源码构建。未执行完整新版差分/性能复核、跨平台运行、
真实打包、dry-run 或发布；两包仍为 `publish=false`。
CLI 的 `annotate` 及其文本/文件/stdin 输入留给 CLI3.2；输出文件和标注 JSON
留给 CLI3.3。原性能预算及首启超预算历史保持不变。
