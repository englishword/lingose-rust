# Lingose Rust 交接记录

## 当前任务与状态

- 当前计划：[todo_CLI.md](todo_CLI.md)，需求为 [TASK_CLI.md](../TASK_CLI.md)，约束为 [AGENTS.md](../AGENTS.md)。
- 本轮从 `main` / `33e72c9` 恢复，实施用户确认的文档计划；**CLI0.1 已完成，文档核验及独立复核通过**。下一项为 **CLI1.1：建立双 crate workspace 并迁移自足库包**。
- 当前生产工程仍是根目录 `lingose 0.1.0`；workspace、接口更名、CLI、CI 和 0.2.0 发布均未实施。本轮只更新规范、清单和恢复状态，需求原文内容不改。
- 原 [0.1.0 计划](todo.md)的 P0–P6 已完成，保留历史；不得重新上传 `lingose 0.1.0`。

## 已确认决策

- workspace 正式成员为 `crates/lingose` 与 `crates/lingose-cli`，两包均 `0.2.0`，CLI 二进制名 `lingose`，Release 标签 `v0.2.0`；沿用 edition 2024 / MSRV 1.85。
- 新入口 `annotate_ips_skip(&str, i64) -> Result<String>`，移除旧 `annotate_ips_with_skip_top`，不保留别名；默认入口和其余库能力继续保留。
- 位置参数是现有普通文件时读文件，否则按文本；`--input`/`--text` 可显式指定，与位置参数互斥；无显式输入读 stdin。
- CLI 只提供 word/annotate；查询六字段、标注 JSON 的 text/annotate、原始文本保留和 stdout/stderr 契约详见根规范。winget/scoop 延期。

## 迁移注意事项

- 库内 `include_str!`/`include_bytes!`、Cargo include、`.gitattributes` 和包内文档链接须随迁移核对；数据、固定向量期望值、Unicode 表与许可身份受保护。
- Python 工具大量使用仓库根下的 src/data/tests 及根 package/version 假设。CLI1.2 区分仓库根和库 crate 根，不只移动 Rust 文件。
- differential/performance 探针需隔离并调整库依赖；layout 探针已有独立 workspace 和互斥 features，按子目录规范验证。
- `tools/package_consumer.rs`、`tools/check_registry_consumer.py` 和 0.1.0 发布收据保留旧版身份；新版另设消费者/报告。旧布局复验使用历史提交隔离检出。
- 库先发布，注册表 lingose 0.2.0 可解析后才执行 CLI 真实打包/dry-run/发布；此前的 CLI 隔离 path 构建只能记为本地候选验收。
- 当前 `git remote -v` 无输出；用户已指定仓库地址，不代表 remote、GitHub 权限或 Actions 已配置。本轮没有远端操作。

## 保留的 0.1.0 发布依据

- 完成提交 `33e72c9`；[正式消费说明](../docs/registry-consumer.md)、[消费证据](../docs/registry-consumer-verification.json)、[发布说明](../docs/publication.md)及[发布收据](../docs/publication.json)保留详细历史。
- 历史正式包 4,048,633 字节 / 41 文件，SHA-256 `fb1a40407222053fa2acf6b92be99e59648d8e2a7ceac3c7f20182bbb393c6a8`；旧版消费者和收据继续记录原身份。
- 已有验证限于记录中的环境；P4.2 新路径首启超预算、许可资料缺口及用户确认的处置依据继续保留，不改写为新版或全部平台已验证。

## 本轮验证与下一步

- 三个更新/生成文档 UTF-8 无 BOM，18 个本地链接有效；18 项任务编号唯一、依赖顺序正确，仅勾选已完成的 CLI0.1。需求覆盖与独立复核通过，已补齐 CLI5 的远端/Actions 前置条件及 CLI 归档规范化 manifest 表述。
- 新写文档的空白检查通过；TASK_CLI.md 第 211 行原有行尾空格作为原文保留。原需求、旧计划、Cargo.toml/lock、src/lib.rs 的前后 SHA-256 一致，Git 差异范围限任务文档。
- 本轮没有代码变更，未运行 Cargo 测试或构建。聚焦提交范围为 AGENTS.md、TASK_CLI.md、本清单和交接记录；需求内容保持原样，旧计划、生产文件和历史证据不改。
- 下一会话先核对 Git、当前计划和本记录，执行 **CLI1.1**：记录迁移输入身份，读取当前根 manifest/include 路径及三个探针配置，再建立双 crate workspace；按该小任务的验收完成后交接，不自动进入后续发布。
