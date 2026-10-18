# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)。CLI0–CLI6 已完成；用户于 2026-10-18 安排 CLI7，顺序 winget → scoop → choco → homebrew。
- 当前正在准备并验收四渠道材料，尚未宣称社区上架。[渠道说明](../docs/cli-package-channels.md)。
- 本次匿名 API 确认仓库 **public**，Release 416347193 和六资产匿名下载均成功、与 CLI6 正式 SHA/字节数相同。此前 private 是历史状态，旧收据原样保留。

## 当前材料与验证

- WinGet：`packaging/winget/manifests/l/Lingose/Lingose/0.2.0/` 三文件 portable ZIP，实际 nested exe/user alias、VC++ runtime 依赖；官方 1.12 schema 通过。
- Scoop：根 `bucket/lingose.json` 自有 bucket；官方 schema 通过，含 x64、extract_dir、shim、checkver/autoupdate 与 runtime 建议。
- Chocolatey：`packaging/chocolatey/` 下载型包，真实 `choco pack` 生成 `.local/cli7/lingose.0.2.0.nupkg`；PowerShell 语法通过。未上传社区。
- Homebrew：根 `Formula/lingose.rb` 自有 tap 二进制 formula，只提供 macOS Intel/ARM；Ruby 语法通过。
- `tools/check_package_channels.py`：匿名资产/官方 schema 校验、安装后 command/shim smoke。`.local/cli7-preflight-1/report.json` 首版通过；工具随后加强到逐项核对冻结收据并增加 Chocolatey/Homebrew URL/SHA，需新目录复跑。
- `.github/workflows/package-channels.yml` 是手动、只读权限验证流程：Windows 按三渠道顺序安装/运行/卸载，再在两个原生 macOS runner 验 tap；尚待执行，不把准备写成通过。
- 本机无 WinGet/Scoop/Homebrew。尝试 WinGetCreate 1.12.13 发现本机 .NET host 太旧，没有更改系统 runtime；不把它计为客户端验证。

## 重要边界

- 自有 bucket/tap 要推送默认分支后才可公开使用。Main/Extras、homebrew/core 不因 public 而合格；详情与官方链接见渠道说明。
- 社区 PR/issue、Chocolatey API key 上传与审核仍是独立后续动作；当前不自动向社区发消息/提交包。
- 所有 crate 与 Release 身份固定；不重传 0.1.0/0.2.0，不移 tag，不修改任何旧发布收据、源词库、Rust 源码或 Cargo.lock。
- tag `9507ff12eac425612a7f9125ecdd65ffb7cb4095` → `cf11a604c8f998a1b4ac67737b3e826cadd40530`；Release ID `416347193`。
- 正式资产与库/CLI 注册表结果见 [CLI6 最终验收](../docs/cli-final-acceptance.md)、[收据](../docs/cli-final-acceptance-verification.json)。库与 CLI 的注册表安装验收限 Windows，其他平台沿用对应 CI 原生证据。
- Windows VC++/UCRT、系统动态库、macOS 未签名/公证、旧 OS 未验、Frequency List/分类来源许可缺口及 CLI4.1 首启超预算事实继续保留。
- 凭据仅供工具使用，不写入仓库、日志或交接。

## 精确下一步

完成本地最小复核（强化后的 preflight、原生 Windows exe smoke、actionlint、打包/语法、空白检查），提交候选并推送；手动运行 `Package channel acceptance`，按失败阶段修正并保留旧尝试。最终收集运行/资产/日志证据，更新 README、CLI7 各项真实状态与此交接。
