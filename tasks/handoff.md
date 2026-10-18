# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)；需求：[TASK_CLI.md](../TASK_CLI.md)；流程：[AGENTS.md](../AGENTS.md)。
- 从干净的 `main` / `9fe3489` 恢复，**CLI4.3 已完成并验证**，本阶段提交以 Git 历史为准。
- 下一项为 **CLI5.1：核对指定 GitHub 仓库条件，建立五平台 release 构建矩阵**。本轮止于 CLI4.3，没有执行 CLI5/CLI6。
- 库与 CLI 均为 0.2.0。库的 `publish=false` 已在受保护候选验证后移除；CLI 继续保留发布保护。没有真实上传，不重复发布 0.1.0。

## 本轮结果与文件

- [打包说明](../docs/cli-packaging.md)与[完整收据](../docs/cli-package-verification.json)记录实际归档、输入摘要、命令/日志、失败尝试和验证边界。
- 新工具：[check_cli_package.py](../tools/check_cli_package.py)；保护测试：[test_cli_package.py](../tests/test_cli_package.py)。复用新版归档审计和 `package_consumer_020.rs`，不改 0.1.0 专用工具。
- 最终库归档：`.local/cli43-3h9dn32c/lingose-0.2.0.crate`，41 文件、**4,053,096 字节**。
  SHA-256：`91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5`。
- `cargo publish -p lingose --dry-run --locked --all-features` 成功，实际 `tmp-crate` 与候选摘要相同；Cargo 明确中止上传。
- 库/CLI README 只修正了过时的双包禁用描述；仍明确 0.2.0 尚未发布。原交接中文已损坏，本文件依据 Git、计划和验证证据重新写为 UTF-8，并固定 LF。

## 验证状态

- Windows x86_64 MSVC：Rust 1.93.1 与 MSRV 1.85.0 分别使用真实解包库，离线构建全部 **18 入口**消费者并 `cargo install --path` 安装 CLI 本地候选；每套 **25 个 CLI 场景**通过。
- 消费工程位于仓库外，先准备 vendor，再使用空 Cargo home 和独立 target。metadata 所有源码均位于隔离目录；运行前移开源码、解包库及 vendor，运行目录仅有四个可执行文件，PATH 只有 System32。
- 包内 **80 项库测试、7 项文档测试**和 doc 通过；一项既有手动探针忽略。另有 **92 项 Python、workspace 131 项 Rust / 7 项文档测试、fmt、Clippy、doc** 通过。
- 41 项归档清单/载荷、19 个本地文件链接、3 个 Rust include、库锁依赖闭包、Unicode/许可/来源身份通过；原始资源合计 10,460,015 字节。最终验证前后 176 项已跟踪输入不变，隔离清单/锁/源码/vendor 目录摘要也不变。
- 初次脚本预期字符串漏字与沙箱 Schannel TLS 失败已保留；最终在正常用户 TLS 环境完整复验。正常用户和沙箱的私有临时目录权限不同，最终共享收据副本位于 `.local/cli43-final-export.json`；完整汇总已写入仓库 docs。
- CLI4.1 的新路径首次启动 675.43 ms 超出 300 ms 的历史事实继续保留；本轮没有重跑差分/性能或放宽预算。

## 继续执行时的边界

1. 先核对 Git 状态/最新阶段提交及 CLI5.1。只读取配置链接不能证明 remote、Actions 权限或远端条件已验证；实际核对用户指定仓库 `https://github.com/englishword/lingose-rust`。
2. 核对当时可用 runner/工具链，建立五目标矩阵及非发布验证：Windows x86_64 MSVC、Linux x86_64/aarch64 GNU、macOS x86_64/aarch64。区分构建、原生/仿真运行和资产上传证据；外部权限阻塞时记录具体恢复动作。
3. CLI 候选的库 path 仅指向本地真实归档，不是注册表验收。CLI 真实 `.crate`、注册表 dry-run 留 CLI6.3，须等库 0.2.0 注册表依赖可解析；真实发布仍按 CLI6 单独执行。
4. 归档来自无 `.git` 的逐字节快照。若分发输入变化或改由 Git checkout 打包加入 VCS 元数据，须重建并重新验证，不沿用当前 SHA-256。
5. 来源许可缺口，尤其 Frequency List 缺少独立许可文本的事实继续保留；项目 CC BY 4.0 不替第三方材料授权。CLI5.2 独立二进制资产仍需附适用依赖许可文本及来源说明。
6. 受保护数据、P0 预期值、Unicode 表、历史发布记录及相邻参考仓库保持不变；0.1.0 工具若需复验，从历史提交隔离检出。
