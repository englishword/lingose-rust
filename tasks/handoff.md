# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)；需求：[TASK_CLI.md](../TASK_CLI.md)；流程：[AGENTS.md](../AGENTS.md)。
- **CLI5.1 已完成并验证**。下一项为 **CLI5.2：生成带使用说明/许可的五平台安装包、校验和，并验证下载/解包后运行**。本轮止于 CLI5.1，没有进入 CLI5.2/CLI6。
- 从干净的 `main / 1ca5d25` 恢复；本轮工作流、路径修复和输入身份提交分别为 `399e59e`、`8b9579a`、`4e00367`，状态提交以 Git 历史为准，不 amend。
- 已配置 `origin=https://github.com/englishword/lingose-rust.git` 并成功推送 main。仓库仍为 **private**；没有创建 tag、GitHub Release 或上传 crates.io。

## 最终证据与产物

- [工作流](../.github/workflows/cli-release.yml)、[构建/验证器](../tools/check_cli_release.py)、[说明](../docs/cli-release-ci.md)、[完整收据](../docs/cli-release-ci-verification.json)。
- 最终成功运行：[39097471918](https://github.com/englishword/lingose-rust/actions/runs/39097471918)，构建提交 `4e00367a02ce7c8a317b209ac8de4dcc0620aa16`。
- 固定 Rust 1.93.1；Windows 2022 x64 MSVC、Ubuntu 24.04 x64/arm64 GNU、macOS 15 Intel/arm64，全部为原生构建及运行。每目标 CLI 测试：Windows/macOS 各 29，Linux 各 30；合计 147 次测试执行，另有 60 次独立 binary-only smoke。
- 五份 CI artifact 上传通过，保留 14 天。已独立下载并核对服务端 zip SHA-256、报告 revision/target/native、每条命令/日志、binary 摘要及 57 项完全相同的构建输入。
- 原始 zip、解包 binary/报告/日志及 run/jobs/artifact API 响应：`.local/cli51-ci-identity/`；总核验收据：`.local/cli51-ci-identity/verified.json`。每份 binary 的准确路径和 SHA-256 见正式 docs 收据。
- 最后状态提交仅更新 docs/plan/handoff，使用 `[skip ci]` 避免为无构建输入变更重复运行五平台；上面的具体构建提交是本轮候选身份。

## 本轮修复及验证

- 初次实际 CI 的 Windows NUL 内容 fixture 原名 `nul.txt`，被 runner 当保留设备名；已改为 `contains-nul.txt`，不改原本的库错误/输出文件保护预期。
- macOS runner 拒绝创建原始非 UTF-8 文件名；现有文件的非 UTF-8 路径测试限定 Linux，Unicode symlink/悬空/循环链接仍在全部 Unix 验证。macOS 初始路径探测的 EILSEQ 92 经现有 Unicode 转换返回用法错误 2；显式 `--input` 仍返回 I/O 1，新增 Unix 场景已在四目标实际通过。
- 第二次矩阵五平台全通过，独立下载又发现 Windows 把两个库 example 转为 CRLF；已在 `.gitattributes` 固定 LF 并将该文件纳入输入记录，第三次矩阵和下载核验全部通过。没有重写固定预期来接受差异。
- 首次失败运行 `39097009450` 和第二次 `39097222034` 保留；本地对应 `.local/cli51-first-macos-arm64/`、`.local/cli51-first-windows/`、`.local/cli51-ci-first/`、`.local/cli51-ci-final/`。
- Windows workspace：fmt、Clippy（all targets/features，-D warnings）、131 Rust / 7 文档测试及 doc 通过；日志 `.local/cli51-checks/`。MSRV 1.85 的 29 项 CLI 测试通过。
- 最终本地 release CLI：29 项测试和 12 项独立 smoke 通过，证据 `.local/cli51-windows-identity/`。actionlint 1.7.12、Python 语法、错误 target 拒绝、两项注入超时的部分日志保留检查通过。
- 最初 versioned rustup alias 不存在、HTTPS 中断、缺 workflow scope 和 artifact 下载 EOF 均有记录；用户已完成设备授权，API 确认 workflow scope 生效，无当前权限阻塞。令牌和设备代码未写入仓库。
- 库源码/数据/固定向量/Cargo manifests/lock 未变；CLI 路径处理和相应测试已改。没有重跑 CLI4 全量差分/性能，CLI4.1 首启 675.43 ms 超预算历史事实保留。

## CLI5.2 精确下一步与边界

1. 先核对 Git、活动计划及上述成功构建输入身份。以这些候选或同输入重建，生成计划指定的五个 zip/tar.gz，附 binary、使用说明、项目及适用依赖/Unicode/第三方许可和来源声明，并生成 SHA-256 清单。
2. 原始 CI binary artifact 不保留 Unix executable mode，不能直接当正式安装包；须先打包，再分别验证解包路径、权限、架构和运行。CI artifact、非发布下载验收与正式 GitHub Release 分开留证；当前 private 仓库的 artifact 需要认证，不声称公开下载可用。
3. 本工作流只具 `contents: read`，支持 main push、pull_request、workflow_dispatch、精确 v0.2.0 tag 的候选验证。要发布资产仍须 CLI6 的独立步骤与授权核对，不把只构建的 tag 触发当作已发布。
4. 来源许可缺口，尤其 Frequency List 缺少独立许可文本的事实继续保留；项目 CC BY 4.0 不替第三方材料授权。CLI5.2 必须核对分发所需声明和许可文本。
5. 库/CLI 均 0.2.0，CLI 仍 publish=false。库尚未发布，CLI 真实归档及注册表 dry-run 留 CLI6.3；不重复上传 0.1.0。CLI4.3 证据见 [cli-packaging.md](../docs/cli-packaging.md)，新 CLI 源码或 Git/VCS 包装变化不能沿用旧候选身份。
6. 受保护数据、P0 预期值、Unicode 表、历史发布证据及相邻参考仓库保持不变。CLI5.2 验证完成后更新交接并聚焦提交，正式发布留 CLI6。
