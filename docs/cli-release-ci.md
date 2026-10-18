# CLI5.1：五平台原生构建与运行

本阶段建立 [候选工作流](../.github/workflows/cli-release.yml)和独立的
[构建/验证器](../tools/check_cli_release.py)。机器可读汇总见
[验证记录](cli-release-ci-verification.json)。正式安装包、许可汇编和下载验收留 CLI5.2；
crates.io 与 GitHub Release 发布留 CLI6。

## 仓库与运行条件

2026-10-18 实际查询 `englishword/lingose-rust`：仓库为 private，未归档且未禁用；
当前 GitHub CLI 账号 `Prefee` 有 admin/push 权限。Actions enabled、allowed_actions=all，
本工作流仍显式使用 `contents: read`，checkout 不持久化凭据。
最初没有分支、标签、工作流，且本地没有 remote；已配置
`origin=https://github.com/englishword/lingose-rust.git` 并通过 Git 认证读取空远端。
不改变仓库可见性或组织设置，不创建 Release 或标签。

| Rust target | 固定 runner 标签 | 运行方式 |
| --- | --- | --- |
| x86_64-pc-windows-msvc | windows-2022 | 原生 Windows x64 |
| x86_64-unknown-linux-gnu | ubuntu-24.04 | 原生 Linux x64 |
| aarch64-unknown-linux-gnu | ubuntu-24.04-arm | 原生 Linux arm64 |
| x86_64-apple-darwin | macos-15-intel | 原生 macOS Intel |
| aarch64-apple-darwin | macos-15 | 原生 macOS arm64 |

这些标准 runner 标签在当日的
[GitHub 官方公共/私有仓库 runner 表](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
中可用；特别是 macOS 15 普通标签对应 arm64，Intel 显式使用 `macos-15-intel`。
操作系统镜像仍会更新，各次实际 ImageOS/ImageVersion、runner 架构、工具链和提交均留证。

## 工作流与证据边界

- `main` push、指向 `main` 的 pull request、手动 `workflow_dispatch` 和精确的
  `v0.2.0` tag push 均只运行候选验证。工作流没有 Release 上传或 crates.io 发布步骤。
- Rust 固定 1.93.1；Python 3.12 仅执行开发期验证，不是 CLI 运行依赖。
  三个 GitHub 官方 action 固定完整 commit SHA，版本及身份见工作流注释和汇总。
- 每个 target 分别执行 `cargo build -p lingose-cli --release --locked --all-features --target TARGET`
  及同参数的 `cargo test`。只选交付 CLI 与其库依赖，开发探针不进入构建。
- 验证器先核对 OS、机器架构和 rustc host；不允许把交叉编译记成原生运行。
  CLI 测试包含该平台适用的路径、编码、I/O、JSON 和错误场景。
- 另外将唯一可执行文件复制到 checkout 外的临时目录，设置最小子进程环境，
  用原始字节执行 12 项 smoke：版本、普通/JSON 查询、未知词、文本标注、CRLF stdin、
  文本/stdin JSON、空 stdin、阈值、无效 UTF-8 和用法错误。
  与既有 CLI4.3 的固定完整预期比较，保留 Unicode 组合符和精确换行。
- 构建输入前后摘要、binary SHA-256、每条命令退出码、stdout/stderr 和逐项 smoke
  留在每目标的 `report.json` 与日志。子进程超时保留已捕获的部分日志。
  运行目录没有复制源码或外部词库，系统运行库仍可用；没有声称禁网或操作系统不含 Python。
- `if: always()` 上传 `cli51-TARGET-COMMIT` CI artifact，保留 14 天。
  artifact 中的 `candidate/lingose[.exe]` 是原始验证候选，不是 CLI5.2 安装包；
  artifact 服务本身不保留 Unix executable mode，后续正式资产须先归档再上传。

## 本地与远端验证

本地 actionlint 1.7.12（下载归档 SHA-256 经 GitHub release API digest 核验）通过，
Python 语法检查和 `git diff --check` 通过。Windows 原生 Rust 1.93.1 release 构建、
29 项 CLI 测试和 12 项独立 smoke 通过，依赖使用已准备的本地 cache 离线构建。
初次指定 `RUSTUP_TOOLCHAIN=1.93.1` 时该 alias 未安装，沙箱禁止写用户 rustup tmp，
失败证据保留在 `.local/cli51-windows-local`；后续使用已核对版本为 1.93.1 的 stable alias。
CI 则明确安装版本号 1.93.1。

**远端运行尚未完成。** 候选工作流已提交，但第一次推送因 HTTPS 请求中断失败；
读取远端确认仍为空后，使用命令级 `http.version=HTTP/1.1` 和
`http.postBuffer=52428800` 重试，GitHub 返回：

```text
refusing to allow an OAuth App to create or update workflow `.github/workflows/cli-release.yml` without `workflow` scope
```

随后独立查询 OAuth response header，实际 scopes 为
`admin:public_key, gist, read:org, repo`，确实没有 `workflow`。
第二次推送后远端 branches 和 Actions runs 仍为空。用户随后回复已授权，但当前代理从
系统 keyring 读取的 scopes 仍缺 `workflow`；未设置 GH_TOKEN/GITHUB_TOKEN，也以独立
禁缓存请求复核了同一结果。第三次推送连接重置，之后远端仍为空；用户提供的终端 scopes
与代理一致，确认尚未增加该项。代理随后启动 `gh auth refresh --hostname github.com
--scopes workflow --clipboard` 设备授权流程，目前等待用户完成网页确认。账号有仓库 admin/push 权限，
但当前 OAuth token 无工作流写入 scope；本地 YAML 检查不能替代五平台 CI 通过。
当前认证 scope 尚未恢复；未改变仓库可见性、Actions 设置或创建任何标签/Release。

恢复步骤：由用户在本机终端执行以下命令并完成交互授权（不把令牌粘贴到聊天或文件）：

```powershell
gh auth refresh -h github.com -s workflow
```

授权后先确认远端当前分支/标签，仍为空时推送当前已验证 `main`。
若默认 Git credential helper 使用其他登录，可仅为本次命令使用现有 `gh` helper：

```powershell
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' -c http.version=HTTP/1.1 -c http.postBuffer=52428800 push --set-upstream origin main
```

随后收集五个 job 的构建日志、CLI 测试、原生 smoke 报告和 artifact 身份；
全部实际验证后再勾选 CLI5.1。Windows 本地错误 target 的负向检查已确认验证器在执行
构建前拒绝 `aarch64-unknown-linux-gnu`，不会把不匹配架构记为原生运行。
另有两项注入超时检查通过：构建命令与 smoke 均保留部分 stdout/stderr，并拒绝记录成功；
证据位于 `.local/cli51-timeout-guards.json` 和 `.local/cli51-command-timeout/`。

手动复跑（需要工作流已存在于默认分支，且具有 write 权限）：

```powershell
gh workflow run cli-release.yml --repo englishword/lingose-rust --ref main
gh run list --repo englishword/lingose-rust --workflow cli-release.yml
gh run view RUN_ID --repo englishword/lingose-rust --log
gh run download RUN_ID --repo englishword/lingose-rust --dir .local/cli51-download-RUN_ID
```

GitHub 对手动触发的默认分支要求见
[官方 workflow_dispatch 说明](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)。
下载证据后核对报告 revision、target、原生模式、全部通过的 smoke、日志摘要和 binary 摘要；
CI artifact 不作为已发布 Release 的证明。
