# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)。CLI0–CLI6 已完成；用户安排的 **CLI7 四渠道准备与原生验收已完成**，按 WinGet → Scoop → Chocolatey → Homebrew 顺序执行。
- [渠道说明](../docs/cli-package-channels.md)、[验收收据](../docs/cli-package-channels-verification.json)。社区提交/审核与本轮安装验收分开：WinGet 未提交 PR，Chocolatey 未上传；Scoop/Main/Extras 和 Homebrew/core 未提交。
- 仓库现为 **public**。匿名 API/六个 Release 文件下载通过，全部与 CLI6 正式 SHA/字节数相同。历史 private 描述保留在旧收据，不重写历史。

## 当前可用渠道与材料

- **WinGet**：`packaging/winget/manifests/l/Lingose/Lingose/0.2.0/` 三文件 portable ZIP，ID `Lingose.Lingose`；官方 schema/真实客户端 validate、安装、命令、通知、卸载通过。未进入社区索引，不能宣传 `winget install Lingose` 已可用。候选按 `--scope user` 安装；portable 清单不写 Scope，社区索引前的本地注册按 `--name Lingose --exact` 卸载。
- **Scoop**：根 `bucket/lingose.json`。公开自有 bucket 可用：`scoop bucket add lingose https://github.com/englishword/lingose-rust`，再 `scoop install lingose/lingose`。仅 Windows x64；要求先具备 Microsoft VC++ v14 x64 Runtime，缺 DLL 时 pre_install 明确拒绝；extras/vcredist2022 是建议项，可能需管理员安装。安装/shim、当前版本 checkver/autoupdate（真实解析 SHA256SUMS）、卸载/重装通过。Main/Extras 准入与贡献流程见渠道说明。
- **Chocolatey**：`packaging/chocolatey/` 下载型包，固定正式 ZIP/SHA，依赖 vcredist140，拒绝 x86。真实 pack、本地 feed 安装、shim、通知、同版本强制重装和卸载通过。nupkg 不内嵌 exe；上传需用户社区账号/API key 并经过审核，当前 `choco install lingose` 尚不可作为社区安装命令。
- **Homebrew**：根 `Formula/lingose.rb`。公开自有 tap 可用：`brew tap englishword/lingose https://github.com/englishword/lingose-rust`，再 `brew install englishword/lingose/lingose`。macOS Intel/Apple Silicon 两份固定正式归档，保留所有许可/来源到 share/lingose。两原生平台的安装/formula test/命令/重装/卸载通过；Linux Homebrew 未提供，core 准入门槛尚不满足。

## 验收与证据

- 最终 [Actions 39126125352](https://github.com/englishword/lingose-rust/actions/runs/39126125352)，候选 **d237147e5e0bf5b0042e1d11a714bde712d06dc6**，三个 job 全成功。Windows Server 2022 x64 三实例、macOS 15.7.9 Intel/ARM 两实例，各 8 项，共 **40 项命令测试**，另有 formula 内测试与安装/卸载/重装/通知检查。
- 三个服务 artifact ZIP 实际下载大小/SHA256 全部与 API digest 一致；报告/原始日志在 `.local/cli7-final-39126125352/`，服务 artifact 保留 14 天。公开 bucket/tap 拉取提交与候选精确一致。
- 六次先前失败均记录在新收据及原始日志：portable Scope 警告、本地注册 ID 匹配、共享 runner API 限流、手动 Scoop bootstrap/本地 bucket URL 假设。最终改为官方 Scoop 安装器；WinGet bootstrap 用临时只读 token，公开资产检查仍匿名。没有把失败改记为通过。
- 本地官方 schema、直接正式 exe 8 项、真实 choco pack/载荷检查、运行库 guard 正/模拟缺失检查、15 项既有归档/发布保护测试、Python/PowerShell/Ruby 语法、actionlint、空白检查通过。247 个范围外原文件不变；未重复全量 Rust/差分/性能/MSRV，源码/数据/锁/旧收据未改。
- 工具：`tools/check_package_channels.py`；手动流程：`.github/workflows/package-channels.yml`。安装 smoke 在无关临时 cwd 调用实际 command/shim，但不声称断网、文件系统隔离或无预装系统 runtime。

## 保留边界与发布身份

- 当前验证是安装、同版本重装及卸载，不是未来跨版本升级验收。Windows exe Authenticode 状态 NotSigned；macOS Developer ID/公证/Gatekeeper/旧 OS 未验。VC++/UCRT/系统动态库、来源许可缺口、CLI4.1 首启超预算事实继续披露。
- 不重传 `lingose`/`lingose-cli` 的 0.1.0/0.2.0，不移动 tag，不替换 Release 资产或修改历史收据/源词库/相邻参考项目。
- tag `9507ff12eac425612a7f9125ecdd65ffb7cb4095` → `cf11a604c8f998a1b4ac67737b3e826cadd40530`；Release ID **416347193**。CLI7 结束时远端复核身份未变。
- 注册表与 Release 原验收见 [CLI6 最终说明](../docs/cli-final-acceptance.md)、[收据](../docs/cli-final-acceptance-verification.json)。凭据不写入仓库、日志或交接。

## 精确下一步

当前渠道准备/验收无阻塞。等待用户安排社区上架：优先以已验三文件清单提交 WinGet；Scoop 社区须先按贡献流程取得维护者同意；Chocolatey 需在用户本机安全配置 API key 后上传已验下载型包并跟踪审核；Homebrew 继续维护当前自有 tap，暂不向 core 提交。不要把这一指针当作已经获得对外发 issue/PR/上传的指令。
