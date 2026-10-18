# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)。**CLI6.5 已完成，CLI0–CLI6 全部完成；当前停在 CLI6.5。**
- [最终验收说明](../docs/cli-final-acceptance.md)、[独立收据](../docs/cli-final-acceptance-verification.json)。
- **下一步等待用户安排；CLI7.1 winget/scoop 仅为延期候选，不因恢复会话自动执行。**
- 本地状态以 Git 历史为准；已发布的 crate、Release 和 tag 不因后续文档修订而重传或移动。

## CLI6.5 已验证结果

- Windows 11 x86_64 MSVC，Rust/Cargo 1.93.1；成功原始证据为 `.local/cli65-dc283d2151ac/`。
- 新增 `tools/check_registry_consumer_020.py`，复用新版消费者 `tools/package_consumer_020.rs`；0.1.0 工具、固定消费者和历史收据保持原字节。
- checkout 外两个初始为空的 Cargo home，分别用于精确依赖 `lingose = "=0.2.0"` 的库消费和 `cargo install lingose-cli --version 0.2.0 --locked`。在线构建/安装后，在全新 target 和安装根离线 locked 复跑；未复制既有 cache、根锁文件、config 或凭据，无 checkout path/patch 借用。
- 注册表 API/index、归档 SHA、全部解包文件、metadata/锁文件与 `.crates2.json` 安装来源通过；91 条命令符合预期退出码，182 份 stdout/stderr 日志大小及摘要独立复核通过。
- 将消费工程、两组 cache、四个 target 和两个安装根移出原路径后，运行目录只提供五个 exe，PATH 仅含 Windows System32，运行用 Cargo home 为空。两份库消费者各验证全部 18 个公开函数且完整输出一致；两份注册表 CLI 和最终 Windows Release CLI 各 25 项，共 75 项通过。
- 运行没有提供外部词库、Python、Node 或相邻项目文件；系统动态库仍可用，未声称有操作系统断网沙箱。本地构建 exe 各有独立摘要，不要求与 CI 二进制逐字节一致。
- 首次 `.local/cli65-e756e643aa13/` 在离线 CLI metadata 阶段缺少 `libc 0.2.190`，失败证据原样保留。验收器补充在线 `cargo fetch --locked`，区分锁文件根包与带 checksum 的依赖后，使用全新 cache 重验；Python isolated-mode 导入问题亦已修正。没有更改已发布包。
- 验收结束时 248 个原有 tracked 文件摘要不变，随后仅更新当前 README/说明/计划与交接；未改 Rust 源码、词库、固定向量、Cargo.lock、旧工具或历史收据。新验收脚本语法、既有 CLI package 两项保护测试及空白检查通过。

## 已发布身份：禁止重复上传或移动标签

- `lingose 0.2.0`：41 文件 / 4,053,096 字节，SHA `91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5`；收据 `docs/cli-library-publication-verification.json`。上传后连接断开但远端成功，仅上传一次。
- `lingose-cli 0.2.0`：7 文件 / 16,498 字节，SHA `3f2e31e77ac7bdcedecb90871597d9821f60119f437be9a2cd7c523faa894490`；收据 `docs/cli-cli-publication-verification.json`。首次 403 后确认未发布，用户更新凭据后第二次成功，仅一次接受。
- CLI6.5 核对两版 API/index 均未 yank，publisher 为 Prefee；两版及 0.1.0 均不得重传。发布载荷/README、旧版消费者和历史收据保持原字节。
- [private v0.2.0 Release](https://github.com/englishword/lingose-rust/releases/tag/v0.2.0)，ID **416347193**，2026-10-18 **09:16:55 UTC** 正式发布，非 draft/非 prerelease；五个固定名称归档及 SHA256SUMS 共六资产。
- 用户已选择以 private 发布；仓库保持 private，查看/下载需要既有认证与仓库权限，不声明匿名公开下载，无需重复询问该选择。
- 注释 tag 对象 `9507ff12eac425612a7f9125ecdd65ffb7cb4095` → **cf11a604c8f998a1b4ac67737b3e826cadd40530**；不得移到后续说明提交。
- 正式 Actions **39114174841** 在 attempt2 发布成功。attempt1 创建草稿失败，未接受 Release/资产；确认远端为空并同步默认分支 workflow 后只重跑发布 job。两个尝试的证据保留，初始精确 HTTP 码未保留，不作断言。
- [正式发布说明](../docs/cli-github-release.md)、[收据](../docs/cli-github-release-publication-verification.json)与原始证据 `.local/cli64-final-39114174841/` 保留。CLI6.5 刷新远端身份后复用并重验 `release-downloads/` 六个正式下载，全部 SHA/载荷身份与最终 CI 候选一致。
- Windows 正式 exe 为 11,286,016 字节，SHA `4dc4476901165818992836459c76ee88f89a97508865e0fb4d60809ca739b3d6`；CLI6.5 脱离构建资料运行的 25 项通过。

## 保留边界

- CLI6.5 的注册表安装及最终 Release 运行限于 Windows x86_64。其余四平台只复核最终归档身份，并列明既有正式 tag CI 的原生候选运行，不外推为本轮最终 Release 运行。
- 既有 tag CI：Windows Server 2022、Linux 两架构 Ubuntu 24/glibc 2.39、macOS 两架构 15.7.9，各有 16 项下载候选 smoke 通过；五包与最终 Release 字节一致，未验证其他旧 OS。
- 此次未重复全量差分、性能或 MSRV 验证，沿用并区分既有阶段证据；CLI4.1 新路径首启超过原 300 ms 预算的事实继续保留。
- Windows VCRUNTIME140/UCRT、Linux/macOS 系统动态库前提，macOS 公证/Gatekeeper/旧 OS 未验，以及 Frequency List/部分分类来源许可缺口继续披露。
- 后续若需 gh 认证，凭据仅在工具内使用，不写入仓库、日志或交接。当前没有阻塞项；精确下一步是等待用户安排，不自动推进 CLI7。
