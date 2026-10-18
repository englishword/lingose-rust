# CLI5.1：五平台原生构建与运行

本阶段建立[候选工作流](../.github/workflows/cli-release.yml)和
[构建/验证器](../tools/check_cli_release.py)，实际结果与摘要见
[验证记录](cli-release-ci-verification.json)。
当前最终运行是 [39097471918](https://github.com/englishword/lingose-rust/actions/runs/39097471918)，
构建提交为 `4e00367a02ce7c8a317b209ac8de4dcc0620aa16`。
五个平台的构建、CLI 测试、原生 smoke 和 CI artifact 上传全部通过。
五份原始 artifact 已独立下载，57 项输入逐字节一致；CLI5.1 已完成。

## 实际矩阵

| Rust target | runner | CLI 测试 | 独立 smoke | 执行方式 |
| --- | --- | --- | --- | --- |
| x86_64-pc-windows-msvc | windows-2022 | 29 | 12 | 原生 |
| x86_64-unknown-linux-gnu | ubuntu-24.04 | 30 | 12 | 原生 |
| aarch64-unknown-linux-gnu | ubuntu-24.04-arm | 30 | 12 | 原生 |
| x86_64-apple-darwin | macos-15-intel | 29 | 12 | 原生 |
| aarch64-apple-darwin | macos-15 | 29 | 12 | 原生 |

runner 标签依据当日的
[GitHub 官方公共/私有仓库 runner 表](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
核对；macOS 15 普通标签对应 arm64，Intel 显式使用 `macos-15-intel`。
实际系统版本、ImageVersion、机器架构、rustc host 及二进制摘要分别记录，支持证据限于这些实际运行环境。

## 工作流与证据

- 采用固定 Rust 1.93.1、Python 3.12 和三个 GitHub 官方 action 的完整 commit SHA。
  Python 仅用于开发验证；CLI 运行没有 Python/Node 或外部词库依赖。
- `main` push、指向 `main` 的 pull request、`workflow_dispatch` 和精确的
  `v0.2.0` tag push 都只构建候选。工作流显式使用 `contents: read`，
  checkout 不持久化凭据，没有 crates.io 或 GitHub Release 发布步骤。
- 每目标执行 `cargo build -p lingose-cli --release --locked --all-features --target TARGET`
  和同参数的 `cargo test`；只选择正式 CLI 及其库依赖，开发探针不参与。
- 验证器核对 OS、机器架构及 rustc host，拒绝把交叉编译标成原生执行。
  在 checkout 外仅复制 binary 的临时目录中，用最小子进程环境和原始字节执行 12 项 smoke：
  版本、普通/JSON 查询、未知词、文本标注、CRLF stdin、文本/stdin JSON、空 stdin、
  阈值、无效 UTF-8 和用法错误。固定完整预期沿用 CLI4.3，保留组合符、类型和精确换行。
- 每目标保留输入前后摘要、binary SHA-256、命令/退出码、stdout/stderr、超时状态和逐项结果。
  构建命令或 smoke 超时均保留部分日志，并拒绝记录成功。
  系统运行库仍可用；没有声称禁网或操作系统不含 Python。
- `if: always()` 上传 `cli51-TARGET-COMMIT` CI artifact，保留 14 天。
  独立下载验证器核对服务端 zip digest、每份报告/日志/binary 的字节摘要、提交/target/原生模式、
  全部 smoke 与输入身份；本地副本位于 `.local/cli51-ci-identity/`。
- artifact 中的 `candidate/lingose[.exe]` 是验证候选。原始 binary artifact 不保留 Unix
  executable mode，正式分发须先归档；许可汇编、使用说明、zip/tar.gz、SHA-256 清单、
  下载/解包后运行属于 CLI5.2。CI artifact 不是 GitHub Release。

## 本轮发现与修复

首次运行 [39097009450](https://github.com/englishword/lingose-rust/actions/runs/39097009450)
中两个 Linux 目标完整通过，其余失败已保留：

1. Windows Server 将测试 fixture `nul.txt` 解释成保留设备名；含 NUL 内容的文件改名为
   `contains-nul.txt`，保持原本需要验证的“库拒绝 NUL 文本”和输出文件保护场景。
2. macOS runner 在测试准备时拒绝含原始 `0xff` 字节的文件名，返回 errno 92。
   已把实际非 UTF-8 文件名读取测试限制到 Linux；Unicode symlink、悬空链接、循环链接仍在全部 Unix 上测试。
3. macOS 自动输入的路径探测将 EILSEQ（92）纳入非法路径处理，让现有 Unicode 转换对非法文本返回用法错误 2；
   显式 `--input` 仍保留 I/O 错误 1。新增 Unix 测试同时验证这两个退出码，不改变可读 Linux 非 UTF-8 路径。

修复后的 [39097222034](https://github.com/englishword/lingose-rust/actions/runs/39097222034)
五目标全部通过。独立下载比对又发现 Windows checkout 把两个库 example 转为 CRLF；
已在 `.gitattributes` 固定 LF，并将该文件纳入构建输入记录。最终运行检查完全一致的输入，
没有通过改写预期或忽略数据差异来接受 Windows 报告。库源码、数据、固定向量和 Cargo manifests/lock 未改。

## 本地工程与仓库条件

Windows Rust 1.93.1 的 workspace fmt、Clippy（all targets/features，warnings 为错误）、
131 项 Rust 测试、7 项文档测试和 doc 通过；Rust 1.85.0 的 29 项 CLI 测试通过。
最终本地 release CLI 的 29 项测试和 12 项 smoke 通过；
actionlint 1.7.12、Python 语法、平台不匹配负向检查及两项注入超时检查通过。
原始日志在 `.local/cli51-checks/`、`.local/cli51-windows-identity/` 等收据指向的目录中。
本轮没有重跑全量差分/性能或正式包验收，CLI4.1 的历史首启超预算事实不变。

实际核验并配置 `origin=https://github.com/englishword/lingose-rust.git`。
仓库最初为空且为 private，账号 `Prefee` 有 admin/push 权限，Actions enabled / allowed_actions=all。
初次登录缺 `workflow` scope，GitHub 拒绝工作流写入；用户完成设备授权后，API 已独立确认该 scope 生效。
部分推送曾报告连接重置或重复 ref 更新，但后续逐次核验远端提交/运行，确认接收后没有重复触发。
仓库可见性和 Actions 设置未改，没有创建 tag、Release 或上传 crates.io；令牌和设备代码未写入仓库。

手动复跑和取证：

```powershell
gh workflow run cli-release.yml --repo englishword/lingose-rust --ref main
gh run list --repo englishword/lingose-rust --workflow cli-release.yml
gh run view RUN_ID --repo englishword/lingose-rust --log
gh run download RUN_ID --repo englishword/lingose-rust --dir .local/cli51-download-RUN_ID
```

手动触发的默认分支要求见
[GitHub workflow_dispatch 说明](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)。
