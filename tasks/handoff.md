# Lingose Rust 交接记录

## 当前任务与状态

- 当前计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，约束：[AGENTS.md](../AGENTS.md)。
- 从 `main` / `40848a4` 恢复，**CLI1.2 已完成并通过验收**。下一项为 **CLI2.1：更名阈值标注入口并更新当前调用**；本轮到此交接。
- 正式 workspace 仍为 `crates/lingose` 与 `crates/lingose-cli`，均 0.2.0，共用根锁文件。两个包保持 `publish=false`；三个开发探针独立。
- 库仍公开 `annotate_ips_with_skip_top`；CLI 仍是明确报告未实现、退出 1 的脚手架。业务命令、接口更名与发布均未执行。

## 当前文件和决定

- [工具迁移说明](../docs/workspace-tools.md)与[完整证据](../docs/workspace-tools-verification.json)记录路径映射、命令、摘要和边界；最终原始日志/库回归报告在 `.local/cli12-tools-final/`，基线/生成器及 workspace 日志在 `.local/cli12-tools-verification/`。
- `tools/reference.py` 的 `ROOT` 为仓库根，`LIB_ROOT` 为库根；`artifact_path` 保留冻结记录中的原相对键，`workspace_inputs` 保留原 workspace 和探针锁文件复制布局。
- exporter/verifier/向量生成器、loader/query/differential/performance 及 layout 路径已适配。当前验证器默认新版证据路径，已有报告不可覆盖；性能前置需核验当前完整差分、成功回归和输入摘要。
- Unicode 表/许可逐字节检查，旧报告不改；旧生成器身份通过 `33e72c9` 原始 Git blob 核验。layout 当前开发产物为 `.local/layout-020`；旧 `.local/layout` 不变。
- 新 `tools/check_workspace_package.py` 默认仅做当前库清单检查，可审计显式给出的已有归档。新 `tools/package_consumer_020.rs` 为旧消费者的原字节副本，CLI2.1 只更新新版副本。
- 历史 `check_package.py`、`prepare_package_sources.py`、`check_registry_consumer.py`、`package_consumer.rs` 和 0.1.0 收据保持原身份。旧布局复验在 `33e72c9` 隔离检出执行；新版分发声明、真实归档和注册表验收仍按 CLI4/CLI6 顺序。

## 验证状态

- Windows x86_64 MSVC / Rust 1.93.1 / 固定 Python 3.12.4：90 Python 回归、102 Rust 测试、5 文档测试通过；1 项既有手动 loader 探针仍忽略。
- 固定基线、P0 JSON、全部生成器只读 check 和独立 verifier 通过；50,335 条全字段/标注状态、全部有序分类及频率数据与安装基线一致。
- 隔离 release loader（1 次，仅工具 smoke）、7 个库测试二进制及 differential smoke（881 项，零差异）通过；新版回归报告落盘并通过性能工具前置身份检查。
- workspace fmt / Clippy -D warnings / tests / doc 通过。差分及性能探针 release/offline/locked 构建通过；layout 四种互斥 feature 各自 offline/locked 构建通过，未测 layout 性能。
- 101 个受保护文件与 CLI1.1/迁移前已存摘要逐字节一致。新库 package --list 为 42 项；新归档审计器的合成归档回归通过，未生成真实 .crate 或执行 dry-run。
- 只读独立复核通过。完整新版差分/性能/MSRV 复核留 CLI4.1；没有其他平台、注册表安装、上传或远端操作。原首启超预算历史继续保留。

## 下一项的精确恢复动作

1. 核对 Git、本记录与 CLI2.1，读取 `crates/lingose/src/lib.rs` 的入口和文档，并用 `rg` 定位当前源码、示例、Rust 测试、受控生成器、探针和新版消费者里的旧函数名。
2. 将当前公共入口更名为 `annotate_ips_skip(&str, i64) -> Result<String>`，移除旧名，不留别名；默认 `annotate_ips(text)` 保留。更新当前文档/调用，记录破坏性变更。
3. 固定 Python/P0 期望数据、Unicode、0.1.0 历史消费者/报告不改。当前生成器的调用名与固定期望值分别核验；使用新版消费者，不改 `tools/package_consumer.rs`。
4. 验证新签名、旧名不可用、负数/0/1000/5062/超上限、NUL、资源加载顺序及原输出；用新证据路径，完成 CLI2.1 后更新交接并聚焦提交，不提前实现 CLI3 或发布。
