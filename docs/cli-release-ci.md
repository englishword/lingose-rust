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

远端运行尚待提交/推送候选后核验；本地 YAML 检查不算五平台 CI 通过。

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
