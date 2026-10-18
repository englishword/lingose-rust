# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)；需求：[TASK_CLI.md](../TASK_CLI.md)；流程：[AGENTS.md](../AGENTS.md)。
- 从干净的 `main` / `1ca5d25` 恢复。CLI4.3 已完成；本轮实现 **CLI5.1 五平台候选构建矩阵**，尚待 GitHub OAuth 权限恢复后的实际 CI 验证。因此没有勾选 CLI5.1，没有进入 CLI5.2/CLI6。
- 工作流/验证器提交为 `399e59e`；后续状态提交以 Git 历史为准，不 amend。

## 已完成的本地工作

- [工作流](../.github/workflows/cli-release.yml)：Windows x64 MSVC、Linux x64/arm64 GNU、macOS Intel/arm64 五目标，全部选择原生标准 runner；固定 Rust 1.93.1 和官方 action commit SHA。
- [验证器](../tools/check_cli_release.py)：locked release 构建和 CLI 测试，校验 native OS/架构/rustc host，在 checkout 外仅复制 binary 的临时目录中运行 12 项逐字节 smoke，保留输入/binary 摘要、命令/超时日志和 JSON 报告。
- 工作流仅具 `contents: read`，只上传保留 14 天的 CI artifact；无 crates.io 或 GitHub Release 发布步骤。标签触发精确为 `v0.2.0`，本轮没有创建标签。
- 说明与收据：[cli-release-ci.md](../docs/cli-release-ci.md)、[cli-release-ci-verification.json](../docs/cli-release-ci-verification.json)。

## 外部阻塞与精确恢复动作

- 已配置 `origin=https://github.com/englishword/lingose-rust.git`。实际核验为 private、空仓库、默认分支 main、未归档/禁用；GitHub CLI 当前账号 `Prefee` 有 admin/push 权限，Actions enabled / allowed_actions=all。
- 初次推送因 HTTPS 连接中断；核验远端仍为空后，以本次命令的 HTTP/1.1 和 50 MiB postBuffer 重试。GitHub 明确拒绝：OAuth App 无 `workflow` scope，不能创建 `.github/workflows/cli-release.yml`。
- 用户已回复“已授权”，但随后系统 keyring 的实际 scopes 仍为 `admin:public_key, gist, read:org, repo`，无 `workflow`。已排除 GH_TOKEN/GITHUB_TOKEN 环境覆盖和查询缓存；用户提供的终端 scopes 与代理一致，确认尚未增加该项。第三次推送连接重置，随后远端 branches/runs 仍为空。
- 代理已启动 `gh auth refresh --hostname github.com --scopes workflow --clipboard`。设备代码在本机剪贴板，用户需打开 `https://github.com/login/device` 完成授权；命令尚在等待。不要将一次性代码或访问令牌写入文件。
- **下一步**：本会话先轮询 exec session `55400` 的授权结果，再通过 API response header 核对实际 `workflow` scope。跨会话该 session 可能失效，此时先查 scope；仍缺时重新启动同一设备流程。已向用户说明并等待网页确认；不要索要、打印或保存令牌。
- 恢复后先核对现有远端分支/运行，避免误覆盖。仍为空时执行：

```powershell
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' -c http.version=HTTP/1.1 -c http.postBuffer=52428800 push --set-upstream origin main
gh run list --repo englishword/lingose-rust --workflow cli-release.yml
```

- 跟踪首次 push 运行（或默认分支已有工作流后使用 workflow_dispatch），保存五个 job 的构建、CLI 测试、原生 smoke 与 artifact 上传结果；下载并核对各 report 的 revision/target/mode、完整日志摘要和 binary SHA-256。仅在实际通过后更新收据、勾选 CLI5.1、提交并交接 CLI5.2。

## 验证状态

- actionlint 1.7.12 通过（下载归档摘要已核对）、Python 语法、`cargo fmt --all -- --check`、`git diff --check` 通过。
- Windows x64 MSVC、Rust 1.93.1：locked release 离线构建、29 项 CLI 测试和 12 项独立 smoke 通过；新验证器没有依赖已安装 Python Lingose 或相邻仓库。
- 最终本地证据：`.local/cli51-windows-final/report.json`；构建/测试日志和 binary 在同目录。初次 versioned rustup alias 不存在/用户 tmp 写权限失败保留在 `.local/cli51-windows-local`，使用已验证为 1.93.1 的 stable alias 复验通过；CI 显式安装版本号。
- Windows 请求 Linux arm64 的负向检查正确拒绝，证据 `.local/cli51-wrong-target/report.json`；另有两项注入超时检查确认保留部分日志且拒绝成功，证据 `.local/cli51-timeout-guards.json`、`.local/cli51-command-timeout/`。
- 各远端平台尚未运行，CI artifacts 尚未上传，不把本地检查记为远端通过。核心源码、数据、Cargo manifests/lock 和固定向量无变更；没有重跑 CLI4 全量差分、性能或包发布验收。

## 后续边界

1. CLI5.2 才生成带使用说明、适用依赖许可/来源声明的正式 zip/tar.gz 与 SHA-256 清单，并完成解包/下载后运行。原始 CI binary artifact 不保留 Unix executable mode，正式分发须先归档；artifact 不是 GitHub Release。
2. 库与 CLI 均 0.2.0；库发布保护已在 CLI4.3 解除，CLI 仍 publish=false。库 0.2.0 尚未发布；CLI 真实归档及注册表 dry-run 留 CLI6.3，先等库注册表依赖可解析，不重复上传 0.1.0。
3. CLI4.3 真实归档及隔离候选证据见 [cli-packaging.md](../docs/cli-packaging.md)。分发输入/VCS 包装改变时重建，不把旧 SHA-256 当新候选；新 GitHub checkout 的真实 crate 仍需单独核定。
4. 来源许可缺口，尤其 Frequency List 缺少独立许可文本的事实继续保留；项目 CC BY 4.0 不替第三方材料授权。
5. 保护数据、P0 期望值、Unicode 表、0.1.0 历史发布证据及相邻参考仓库保持不变；CLI4.1 首启 675.43 ms 超预算历史事实继续保留。
