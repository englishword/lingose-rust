# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，流程：[AGENTS.md](../AGENTS.md)。
- **CLI5.2 已完成并验证**。下一项为 **CLI6.1：核对已有发布授权、0.2.0 注册表状态/账号、许可缺口处置、候选身份及具体 GitHub Release 条件**。本轮止于 CLI5.2，没有进入 CLI6。
- 从干净的 `main / d042a4c` 恢复；本轮实现提交为 `d16c537`，收据/交接提交以 Git 历史为准，不 amend。
- origin 为 `https://github.com/englishword/lingose-rust.git`，仓库仍 **private**。已有 workflow scope 授权，不重复询问；本轮未创建 tag、GitHub Release 或上传 crates.io。

## 最终候选和证据

- 成功运行：[39101457134](https://github.com/englishword/lingose-rust/actions/runs/39101457134)，构建提交 `d16c53773c0fb7e6f21dd2d1544ddcdc549734f3`。
- 11 个 job 全通过：五原生 build/package、五新 runner 下载/解包/运行、最后汇总。固定 Rust 1.93.1；Windows 2022 x64、Ubuntu 24.04 x64/arm64、macOS 15.7.9 Intel/arm64。
- 共 147 次 CLI 测试、35 次 archive guard、60 次构建 smoke、**80 次实际下载后原生 smoke**。下载 job 仅 sparse-checkout tools/release，明确断言无 crates/.local，不安装 Rust/准备 Cargo 或词库缓存；每目标 16 项 smoke 覆盖查询、文本/stdin/文件、JSON/输出文件和错误。
- 五安装包和 SHA256SUMS 的就绪目录：`.local/cli52-dist-d16c537/`，严格六文件，约 4.36–4.48 MB/包。精确 SHA-256 见该清单、[安装包说明](../docs/cli-binary-assets.md)及[完整收据](../docs/cli-binary-assets-verification.json)。
- 原始 17 个 CI artifact zip、API run/jobs/artifacts 响应、build/package/download 报告、binary/日志：`.local/cli52-ci-final/`；总核验为 `verified.json`。所有 service zip digest、五 archive、闭合载荷/架构/模式/许可、57 构建和 53 打包输入已独立核验一致。
- 下载到本机的 Windows archive 再复制到 checkout 外无 crates/cache 工程，另有 16 项 smoke，通过记录 `.local/cli52-local-downloaded/report.json`。
- 最后 docs/plan/handoff 提交只更新验证状态，使用 `[skip ci]`；`d16c537` 是具体候选构建身份，不能把后续提交默认为同一 archive SHA。

## 实现与本地验证

- [工作流](../.github/workflows/cli-release.yml)、[打包器](../tools/package_cli_binary.py)、[二进制头读取器](../tools/binary_format.py)、[guard 测试](../tests/test_cli_binary_package.py)。
- [release/README.md](../release/README.md)、[release/SOURCES.md](../release/SOURCES.md) 为包内用户说明；[notice 清单](../release/notices.json)固定 44 项可用原文及源/摘要。x86 目标 18 外部依赖、arm64 19（条件 libc），每包 46/48 文件。
- 新增 Rust 1.93.1 官方 stdlib copyright/license aggregate 和 commit-pinned ECDICT MIT 许可；原有项目/data/Unicode/UPSTREAM 来源声明原样复制。许可原文保留 CRLF/空白，只有快照目录设 `-text -whitespace`，所有原文 SHA 均核对。
- 每包单一顶层目录；编码固定排序、提交时间、owner/group/gzip header，每目标两次编码逐字节一致。校验和/清单拒绝多余文件、路径穿越、重复、链接、错误模式/架构。Unix 解包后模式明确核对，Windows 只记录 archive mode 和实际执行。
- 本地 99 项 Python 回归、fmt、actionlint 1.7.12、Python 语法及空白检查通过。Windows 本地 release 29 项 CLI 测试、12 项构建 smoke、真实 ZIP 和独立工程 16 项 smoke 通过；初始本地证据 `.local/cli52-build-final-local/`、`.local/cli52-package-final-local/`、`.local/cli52-local-sourcefree/`。
- 部分原始 artifact API 下载瞬时失败，重试后 17 个全部核对；没有忽略失败目标。受保护的库树、CLI Rust 源码/测试、Cargo manifests/lock、P0 向量、历史收据、相邻参考仓库均未改。ROOT/CLI README 仅更新过时的平台状态。
- 没有重跑 CLI4 全量差分/性能或 Rust workspace/MSRV 检查；其既有作用范围保留，CLI4.1 首启 675.43 ms 超预算历史不变。

## CLI6.1 精确下一步与边界

1. 先核对 Git、当前计划、上述候选/收据及本地六文件 SHA。实时查询两包 0.2.0 注册表状态、账号/owner、Git remote/Release 条件，核对已有用户授权；已有授权不重复询问，不索要或记录令牌。
2. **许可缺口仍需处置核对**：Frequency List 无独立许可文本，部分分类无逐标签来源/许可记录；提供 44 项可用许可全文不等于所有第三方再分发权限已解决，不把 CC BY 4.0 当重新授权。
3. Windows 候选实际导入 VCRUNTIME140.dll，需要兼容的 Microsoft Visual C++ v14 x64 Runtime 和系统 UCRT，未重建静态 CRT、未捆绑微软 DLL。Linux 依赖 glibc/libgcc_s/loader；macOS 依赖 libSystem，未提供 Developer ID/公证或 browser quarantine/Gatekeeper 验收。支持声明限实际 runner，元数据最低 OS/符号版本不是旧 OS 运行证据。
4. 当前 GitHub 为 private，CI artifact 需认证且保留 14 天，不能声称公开 Release 下载已通过；本地原始证据和六文件副本已保存。正式公开/上传条件在 CLI6 单独核对。
5. 库/CLI 均 0.2.0，CLI 仍 publish=false；注册表状态在 CLI6.1 刷新，不重复上传 0.1.0。新 Git/VCS 包装、CLI README、后续 Cargo/notice/源码/提交变化均须重新核定候选，不沿用旧 CLI4.3 或本轮 archive SHA。
6. 后续顺序：CLI6.1 条件核对 → CLI6.2 库真实发布/可解析 → CLI6.3 CLI 真实归档/dry-run/发布 → CLI6.4 v0.2.0 GitHub Release → CLI6.5 正式注册表/Release 下载验收。本轮安装包和 CI 下载只满足 CLI5.2，不能代替这些步骤。
