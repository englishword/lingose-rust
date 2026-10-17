# Lingose Rust 交接记录

## 当前任务与状态

- 当前计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，约束：[AGENTS.md](../AGENTS.md)。
- 本轮从干净的 `main` / `ee435dc` 恢复，**CLI3.1 已完成并通过验收**；具体提交见 Git 历史。下一项为 **CLI3.2：实现文本、文件、stdin 标注输入**；本轮到此交接。
- CLI 已实现 `word WORD [--json]`、标准 help/version，二进制名为 `lingose`。尚未提供 CLI `annotate`。
- 正式 workspace 为 `crates/lingose` 与 `crates/lingose-cli`，均 0.2.0，共用根锁文件；两包仍 `publish=false`。库的 `annotate_ips_skip(&str, i64)` 与全部查询能力保持不变。

## 当前文件和决定

- [命令查询说明](../docs/cli-word.md)与[完整证据](../docs/cli-word-verification.json)记录行为、验证命令、源码/依赖身份和边界；本轮原始日志、P0 对照、开始前文件摘要及辅助脚本在 `.local/cli31-word/`。
- `crates/lingose-cli/src/main.rs` 使用 Clap builder，仅启用 `std/help/usage/error-context`；JSON 使用 serde_json 的默认 std。根 `Cargo.lock` 锁定 Clap 4.6.7、serde_json 1.0.154 及传递依赖，未使用 derive 或复制业务算法。
- 查询直接调用库的五个字段 API，再加原样的 `word`；普通输出为六行标签和 JSON 编码值，JSON 为六键对象。三组发音独立，ISM/root lemma 保留 null，不输出辅助字段。
- 查询全部成功后才写 stdout；参数/库参数错误退出 2，资源/I/O 错误退出 1，成功/合法未知词/help/version 退出 0。写入和 flush 错误被传播，stderr 仅放诊断。
- `crates/lingose-cli/tests/word.rs` 为进程测试；`main.rs` 内有资源错误分类、输出失败和合成多发音测试。CLI README、SOURCES、根 README 已更新为当前能力；完整分发文档/许可核对仍属 CLI4.2。
- 本轮未改库源码、算法、数据、固定期望、Unicode 表、历史材料或相邻参考仓库。

## 验证状态

- Windows x86_64 MSVC / Rust 1.93.1：新增 11 项 CLI 测试通过；workspace 113 项 Rust 测试、6 项文档测试通过，1 项既有手动 loader 探针仍忽略。fmt、Clippy `-D warnings`、doc 及 15 项 workspace 工具 Python 回归通过。
- 使用 `.local/p52-rustup-home` 中已有 Rust 1.85.0 工具链和独立 `.local/cli31-msrv-target`，实际编译并通过同样 11 项 CLI 测试。依赖准备后的 Cargo 检查均使用 offline/locked。
- 进程对照覆盖六字段/类型、大小写、Unicode、组合符、引号/反斜线、内部换行、未知词、字段不可用、参数错误、help/version、前导连字符和关闭 stdout（退出 1，无 panic）。
- 真实 `Marxism` 的 IPA/IPS 非空而 IPSM 为空；固定库目前每组最多一条采用发音，因此多发音用明确标注的 2/1/3 长度合成输出 fixture 验证，没有声称来自真实词库。
- 当前源码构建的二进制在空目录启动，16 词/80 个成功字符串查询字段与固定 P0 snapshot 零差异，help/version 正常，目录仍为空；没有重新运行 Python oracle 或宣称独立归档消费。
- 独立只读复核通过；150 个范围外原文件摘要不变，涵盖整个库 crate、保护数据/向量、Unicode 表、许可证、历史报告及探针。
- 未执行完整新版差分/性能/MSRV workspace 复核（仍留 CLI4.1）、真实 `.crate`、dry-run、上传、远端或其他平台操作。原首启超预算历史保留。

## 下一项的精确恢复动作

1. 核对 Git、本记录与 CLI3.2，读取当前 `src/main.rs`、CLI 测试及库 `annotate_ips_skip` 契约，沿用已锁定的依赖和错误分类。
2. 新增 `annotate` 子命令，接受可选位置参数、互斥的 `--input PATH` / `--text TEXT`，默认读取 stdin；位置参数仅在现存普通文件时作为文件，目录、权限或读取错误不能回退为文本。
3. 按 UTF-8 读取完整输入，一次调用 `lingose::annotate_ips_skip`，`--skip-top` 默认 0，阈值校验及上限处理交给库。保留大小写、空白、LF/CRLF、标点和跨行上下文，不额外追加换行。
4. 验证文字/同名路径/显式输入/stdin、空输入、Unicode、跨行上下文、阈值、无效编码和 I/O 失败，并与库完整结果对照；保证当前 word/help/version 回归通过。`-o`、标注 JSON 及完整 shell 错误验收留 CLI3.3。
5. 完成 CLI3.2 后更新计划/交接并聚焦提交，不提前进入 CLI4 打包或 CLI6 发布。
