# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，流程：[AGENTS.md](../AGENTS.md)。
- 从干净的 `main / d042a4c` 恢复。**当前 CLI5.2 安装包与下载验收**：实现及本地验证已准备，下一步提交/推送后核验实际五平台 build/package/download 和汇总 job；尚未勾选 CLI5.2。
- CLI5.1 已完成，基线证据见 [cli-release-ci.md](../docs/cli-release-ci.md) / 成功运行 `39097471918`。
- origin 为 `https://github.com/englishword/lingose-rust.git`，仓库 private；已有 workflow scope 授权，不重复询问。无 tag/Release/crates.io 发布。

## CLI5.2 文件和实现

- [工作流](../.github/workflows/cli-release.yml)：五原生 build/package job、五独立 download/解包/运行 job、最后汇总五包和 SHA256SUMS。下载 runner 仅 sparse-checkout tools/release，断言无 crates/.local，不安装 Rust 或准备 Cargo 词库缓存。
- [打包器](../tools/package_cli_binary.py)、[架构/导入库读取器](../tools/binary_format.py)；复用 [smoke](../tools/check_cli_release.py)，下载验收扩展至 16 项（构建保持 12 项）。
- [release/README.md](../release/README.md)、[release/SOURCES.md](../release/SOURCES.md) 是包内说明；[notice 清单](../release/notices.json)固定 44 项原文及来源摘要，包含目标闭包所需 crates、Rust stdlib、ECDICT 和原有项目/data/Unicode 声明。
- [当前说明](../docs/cli-binary-assets.md)和[收据](../docs/cli-binary-assets-verification.json)记录阶段边界。ROOT/CLI README 更新过时的“其他平台执行待验”文字，核心库 README/数据不改。
- Windows 候选继续动态依赖 VCRUNTIME140.dll，文档明确官方运行库前提；不隐式改 CRT 静态链接。Frequency List/分类许可缺口保留，未宣称再分发权已解决。

## 本地验证及下一动作

- 99 项 Python 回归（含 7 项 archive/notice/header guard）、actionlint 1.7.12、Python 语法、fmt/空白检查通过。
- Windows release 的 29 项 CLI 测试、12 项构建 smoke 通过；真实 ZIP 确定性编码、闭合载荷/架构/许可/摘要检查通过。
- 验证器、notice 和 ZIP 复制到 checkout 外的独立无 crates/cache 工程，16 项解包后 smoke 通过。
- 证据：`.local/cli52-build-final-local/`、`.local/cli52-package-final-local/`、`.local/cli52-local-sourcefree/`。初次本地调试产物另有非 final 命名目录。
- **精确下一步**：提交当前实现并推送 main（正常用户 gh/Git 认证；不创建标签或 Release），获取 Actions run id。逐一核对五 build/package、五 downloaded-native、assets 汇总结果；失败按报告修复并保留历史，不能把 YAML/本地 ZIP 当全平台通过。
- 全部通过后下载 raw CI artifacts，核验服务端 digest、五 archive/SHA256SUMS、载荷/模式/架构、native 报告和源码输入身份；保存本地副本，更新正式 docs 收据，勾选 CLI5.2，提交并交接 CLI6.1。

## 后续边界

- 五资产名称见活动计划；archive 内单一顶层目录、binary 0755、文档 0644，Windows 和 Unix 权限证据分开。
- 原始 CI artifact 保留 14 天、private 需认证；它不是 GitHub Release，不宣称公开下载、macOS Gatekeeper 或未测试旧 OS 已验收。
- 没有改 Rust 源码、核心词库、P0 预期、Cargo manifests/lock、历史收据或相邻参考仓库；CLI4.1 首启超预算历史保留，不重跑差分/性能以覆盖它。
- 库/CLI 均 0.2.0，库尚未发布，CLI 仍 publish=false。正式发布在 CLI6；不重复上传 0.1.0。新 Git/VCS/CLI README 输入必须独立核定候选，不沿用旧 CLI4.3 身份。
