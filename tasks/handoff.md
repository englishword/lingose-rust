# Lingose Rust 交接记录

## 当前任务与状态

- 当前计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，约束：[AGENTS.md](../AGENTS.md)。
- 本轮从干净的 `main` / `fbb447f` 恢复，**CLI3.2 已完成并通过验收**；具体提交见 Git 历史。下一项为 **CLI3.3：输出文件、标注 JSON 与完整 shell 错误契约**；本轮到此交接。
- CLI 现有 `word WORD [--json]`、`annotate [TEXT_OR_PATH | --input PATH | --text TEXT] [--skip-top N]`、标准 help/version；无显式标注输入时读取 stdin。
- 尚未实现 `annotate --json` 或 `-o`。两包仍为 0.2.0 / `publish=false`；库算法、数据、API、依赖和根锁文件未改。

## 当前文件和决定

- [标注输入说明](../docs/cli-annotation-input.md)和[完整证据](../docs/cli-annotation-input-verification.json)记录命令、摘要、源文件身份和边界；原始日志/P0 对照/shell 输入捕获/辅助脚本在 `.local/cli32-input/`。
- `crates/lingose-cli/src/main.rs` 新增 annotate 参数、共享命令分派和错误封装。继续使用原 Clap builder/serde_json，无新增依赖或模块路径假设。
- 三种显式输入由 ArgGroup 互斥。位置参数保留 OsString，先 symlink_metadata；现存实体仅普通文件/指向普通文件的链接可读。目录、失效/循环链接、权限及读取失败不回退。
- 不存在、无效/超长路径名及中间组件非目录按文字解释，OS 错误分类保持窄范围并兼容 Rust 1.85；文字分支不做有损 Unicode 转换。--input 始终文件，--text 始终文字。
- 文件/stdin 完整 UTF-8 读取至 EOF，不去 BOM、不按行拆分；一次调用 annotate_ips_skip，i64 阈值默认 0，验证和上限处理交给库。
- 成功结果按库原字节 write_all/flush，不追加换行。输入或参数失败不输出部分标注；错误只到 stderr，参数/库参数错误 2、I/O/资源错误 1。word 六字段/JSON 行为保持原样。
- 新进程测试为 `crates/lingose-cli/tests/annotate.rs`；根/CLI README 更新了当前能力、输入示例和 shell 编码/换行边界。完整分发文档仍留 CLI4.2。

## 验证状态

- Windows x86_64 MSVC / Rust 1.93.1：20 项 CLI（4 单元、8 word、8 annotate）通过；workspace 122 项 Rust、6 项文档测试通过，1 项既有手动 loader 探针仍忽略。fmt、Clippy -D warnings、doc、15 项 workspace 工具 Python 回归通过。
- 已有 `.local/p52-rustup-home` 的 Rust 1.85.0 在独立 `.local/cli32-msrv-target` 实际编译并通过同样 20 项 CLI 测试；Cargo 构建/测试均 offline/locked。
- 五种输入模式对照库完整结果，覆盖跨行 the 上下文、空输入、Unicode/组合符/BOM、LF/CRLF/CR、标点、词形/未知词、同名路径/文字、长文字、非法路径字符、互斥、阈值、无效编码/NUL、目录/缺失文件、Windows 独占文件锁与关闭 stdout。部分 stdin 读取后失败使用明确的合成 Read fixture。
- 固定 P0 中 52 项成功且阈值可由 i64 表示的标注 snapshot，经空目录的 CLI stdin 逐字匹配，零差异。snapshot-0260 的 Python 任意精度大整数超出现有 Rust i64 契约，单列排除；未修改期望或截断参数，CLI 溢出拒绝另有进程测试。
- PowerShell 5.1.26100.9444 与 Git for Windows Bash 5.2.37 的 6 个管道示例通过。PowerShell 实际输入含 UTF-8 BOM/CRLF，以捕获的实际 stdin 对照，CLI 保留原文；Bash 按字节比较。Git Bash 运行 Windows 二进制，不是 Linux 目标机验收。
- 独立只读复核通过；156 个范围外原文件摘要不变，含整个库、数据/向量、Unicode 表、锁文件、许可证、探针和历史证据。
- cfg(unix) 的原生非 UTF-8 路径/普通及失效/循环 symlink 测试已写但本机未运行。完整新版差分/性能/workspace MSRV 留 CLI4.1。没有新 Python oracle、归档/注册表消费、打包/dry-run、上传、远端或跨平台发布操作。

## 下一项的精确恢复动作

1. 核对 Git、本记录与 CLI3.3，读取 main.rs 的 run/read_annotation_input/write_word、现有 CLI 进程测试与输出契约，沿用当前依赖和错误分流。
2. annotate 新增 --json 和 -o PATH；JSON 严格只有 text（原始输入）和 annotate（库完整结果）两个字符串字段，纯文本不追加换行。
3. 默认结果写 stdout；-o 写所选格式且成功时 stdout 为空。先完成参数解析、完整输入读取和标注，再创建/写输出文件，保证这些前置失败不截断既有文件；覆盖输入输出同路径。
4. 验证 JSON 类型/Unicode/原始换行、文件输出/覆盖、参数/输入/标注失败保留原输出、无效编码、冲突输入、I/O 和 stdout 失败及退出码。回归 word 和所有输入模式，保持 stdout/stderr 可组合且无进度信息。
5. 完成 CLI3.3 后更新计划/交接并聚焦提交；后续 CLI4.1 才执行完整新版差分/性能等验收，不提前进入打包或发布。
