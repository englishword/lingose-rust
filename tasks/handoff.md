# Lingose Rust 交接记录

## 当前任务与状态

- 当前计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，约束：[AGENTS.md](../AGENTS.md)。
- 从 `main` / `24a87fb` 恢复，**CLI2.1 已完成并通过验收**。下一项为 **CLI3.1：建立命令入口并实现单词查询**；本轮到此交接。
- 库现公开 `annotate_ips_skip(&str, i64) -> Result<String>`，旧 `annotate_ips_with_skip_top` 已移除，没有别名；`annotate_ips(text)` 继续使用零阈值。
- 正式 workspace 仍为 `crates/lingose` 与 `crates/lingose-cli`，均 0.2.0，共用根锁文件；两包均 `publish=false`。CLI 仍是明确报告未实现并退出 1 的脚手架，未增加业务命令或依赖。

## 当前文件和决定

- [更名说明](../docs/annotation-api-rename.md)及[完整证据](../docs/annotation-api-rename-verification.json)记录破坏性变更、命令、源码身份与边界；本轮原始日志、原文件副本及临时消费者在 `.local/cli21-api-rename/`。
- 当前源码、示例、API 测试、三组公共标注向量及其生成器、差分/性能探针、`tools/package_consumer_020.rs` 均改用新名称；Python oracle 仍调用其原 `annotate_ips(skip_top=...)`，差分协议 opcode 不变。
- 业务实现只改 `src/lib.rs` 的公开入口、默认委托与文档链接；原算法、校验、数据及资源加载逻辑不改。
- 根/库 README 和库内 0.2.0 API 契约说明旧名称移除；根 README 指向库内当前契约。根 `docs/rust-api.md` 明确属于 0.1.0，连同既有阶段报告、旧消费者和发布/注册表工具保留原身份。
- 新版消费者的说明/成功消息改为 0.2.0 API 消费；本轮用当前源码本地依赖运行，不冒充真实归档或注册表消费。

## 验证状态

- Windows x86_64 MSVC / Rust 1.93.1 / 固定 Python 3.12.4：90 Python 回归、102 Rust 测试、6 文档测试通过；1 项既有手动 loader 探针仍忽略。
- 新函数指针签名和当前源码消费者 18 个公共入口通过；同一消费工程引用旧函数名明确报 E0425。README 的旧名称 compile_fail 及新名称非法类型 compile_fail 均通过。
- 三个受影响生成器只读 check、隔离 release 的 7 个测试二进制及差分 smoke（881 项，零差异）通过。smoke 请求/Python/Rust 输出字节摘要与 CLI1.2 相同，71 项使用显式阈值入口。
- 现有回归覆盖负阈值、0/1000/5062/超上限、NUL、校验顺序、无英语词不加载、零阈值不加载频率、正阈值先频率后词库、完全屏蔽仍校验主词库、错误缓存及并发。
- 9 个 Rust 文件与原文独立比较，只允许名称、局部变量、rustfmt 排版及新版消费者说明/成功消息变化；固定期望/阈值/错误断言未变。4 个 Python 工具仅名称替换，138 个范围外原文件逐字节不变。
- workspace fmt / Clippy -D warnings / tests / doc、两个独立探针 release/offline/locked 构建和库 package --list（42 项）通过。只读独立复核通过。
- 完整新版差分/性能/MSRV 复核仍留 CLI4.1；没有实际 .crate、dry-run、上传、远端或其他平台操作。原首启超预算历史保留。

## 下一项的精确恢复动作

1. 核对 Git、本记录与 CLI3.1，读取 `crates/lingose-cli/Cargo.toml`、`src/main.rs` 和 CLI 接口约束，保持只提供 word/annotate/help/version 的范围。
2. 选择并锁定符合 Rust 1.85 的最小参数/JSON 依赖，先落实标准 help/version 和 `word WORD [--json]`；数据和算法通过库调用，不复制词库或查询实现。
3. 输出严格只含 word、ipa、ips、ism、ipsm、root_lemma；发音为独立数组，ism/root_lemma 为字符串或 null，合法未知词成功，参数错误退出 2，执行错误退出 1，结果/诊断分流。
4. 验证普通/JSON 输出类型、Unicode、多个发音、未知词、参数错误与 help/version 独立运行；完成 CLI3.1 后更新交接并聚焦提交。文本/文件/stdin 标注留 CLI3.2，不能提前进入打包或发布。
