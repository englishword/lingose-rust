# Lingose Rust 交接记录

## 当前任务与状态

- 当前计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，约束：[AGENTS.md](../AGENTS.md)。
- 从 `main` / `5ae873d` 恢复，**CLI1.1 已完成并通过验收**。下一项为 **CLI1.2：适配开发工具和版本相关路径假设**；本轮不继续该项。
- 根现为 virtual workspace，正式成员为 `crates/lingose`、`crates/lingose-cli`，版本均 0.2.0，共用根 Cargo.lock。三个开发探针保持独立 workspace/锁文件/profile。
- 库源码、数据、examples 和六个 Rust 集成测试文件已迁入库目录；Python 测试及 P0 fixture 留在仓库根。两个包保持 `publish = false`。
- CLI 二进制名 `lingose`，目前仅为明确报告未实现并退出 1 的脚手架。业务命令尚未实现；标注仍使用旧 `annotate_ips_with_skip_top`，更名按计划留 CLI2.1。

## 本轮文件与决策

- 根 Cargo.toml、两包 manifest、CLI main/README、两个探针 manifest/锁文件、.gitattributes；根 README/API 导航按新路径调整，库内保留必要文档和声明副本。
- [迁移记录](../docs/workspace-migration.md)及[完整证据](../docs/workspace-migration-verification.json)记录路径映射、摘要、命令和边界；原始快照/日志保留于 `.local/cli11-workspace-b97b1a285c66/`。
- 38 个迁移文件逐字节一致，4 个库内来源/许可副本和两个 CLI 声明副本原样保留。88 个不在变更范围内的原文件摘要不变；历史收据、固定消费者、P0 fixture、词库和 Unicode 表未改。
- 根及两个探针的注册表依赖均不变；探针锁文件只更新本地库版本。原来源摘要中的旧锁文件身份仍为历史证据，分发声明更新留 CLI4.2。
- CLI 与库同名导致首次 cargo doc 输出路径碰撞；已为 CLI bin 设置 `doc = false`，在全新文档 target 重跑通过，保留原警告日志。
- 两包发布保护分别在 CLI4.3（库）和 CLI6.3（CLI）按验收条件解除。真实发布仍需库先进入注册表，再处理 CLI；本轮无归档生成、dry-run、上传或远端操作。

## 验证状态

- Windows x86_64 MSVC / Rust 1.93.1：库离线 check、workspace fmt/Clippy（-D warnings）/测试/文档构建、CLI 构建通过。102 项 Rust 测试和 5 项文档测试通过，1 项既有手动加载器探针仍忽略。
- Rust 1.85.0：workspace/all-targets/all-features 离线 locked 编译通过，未重跑该版本完整测试套件。
- metadata 确认只有两个正式成员，三个探针各自独立；差分/性能探针 offline locked check 通过。layout 探针本轮只核对 workspace 归属，未构建或测性能。
- `cargo package --list` 列出库 42 项、CLI 8 项，必要资源/许可齐全；这不是实际 .crate、独立归档消费或发布验收。
- 库源码复制到仓库外临时目录并离线构建两个示例；只复制两个 exe 到独立运行目录、Cargo/Rustup home 为空，查询/标注运行通过。显式复用已准备依赖及移除无关 CLI 条目的锁文件副本；不等同注册表消费或系统级断网审计。
- 独立只读复核通过；46 个当前文档本地链接、任务状态、Git 差异空白与证据输入身份核对通过。完整检查信息见迁移记录。

## 下一项的精确恢复动作

1. 核对 Git、本记录与 CLI1.2；读取 `tools/reference.py` 的 ROOT、导出/验证器的输出根及当前 Python 测试保护，建立仓库根/库 crate 根的明确映射。
2. 按 CLI1.2 适配生成器、loader/query/differential/performance、打包工具和受影响测试；当前这些工具仍可能引用旧 src/data/tests 路径，不能假定 Python 工具套件已通过。
3. 固定数据、向量期望、Unicode、历史发布证据不改；0.1.0 专用工具和消费者留原身份，旧布局复验使用历史提交隔离检出。
4. 保留用户已确认的输入自动识别、显式 --input/--text、移除旧函数名、两包 0.2.0 选择。原 0.1.0 P0–P6 已完成，不重复发布；GitHub remote/Actions 尚未配置，按 CLI5 处理。
