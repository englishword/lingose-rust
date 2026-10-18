# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)。**CLI6.4 已完成；下一项 CLI6.5：注册表安装与 Release 下载运行验收。** 本轮止于 CLI6.4，未提前执行 CLI6.5。
- 用户明确选择“目前以 private 发布 Release”；仓库保持 private。认证且有仓库权限的查看/下载是本项验收范围，不要求也不声明匿名公开下载；后续不再重复询问该选择。
- [正式说明](../docs/cli-github-release.md)、[正式收据](../docs/cli-github-release-publication-verification.json)。前次非发布候选收据 `cli-github-release-verification.json` 原样保留，不与正式身份混用。

## 已发布 Release：不要重建或重传

- [v0.2.0 Release](https://github.com/englishword/lingose-rust/releases/tag/v0.2.0)，ID **416347193**，2026-10-18 **09:16:55 UTC**正式发布，非draft/非prerelease；五个固定名称归档与 SHA256SUMS 共六资产。查看/下载需要既有 gh 认证与仓库权限。
- 注释 tag 对象 `9507ff12eac425612a7f9125ecdd65ffb7cb4095` → 提交 **cf11a604c8f998a1b4ac67737b3e826cadd40530**；不得将其移动到后续说明提交。main包含后续诊断/文档提交，以Git历史为准。
- 正式 Actions **39114174841**：五构建/五独立下载/汇总十一项候选job均成功，147项CLI、35项归档保护、35项发布保护、60项构建/80项下载原生smoke通过。attempt1创建草稿POST失败，无Release/资产接受；先核实远端为空、同步默认分支workflow，再只重跑发布job，attempt2成功。保留两个发布报告，不能抹去首次失败或将其写为成功。
- 原因推断：tag的workflow与当时远端main不同，触发GitHub额外workflow权限规则；同步main后成功。原脚本未保留服务端错误正文，不能断言初始精确HTTP码。main已补足API诊断及测试（8发布+7归档通过）。没有本地伪造CI环境，没有改可见性或tag。
- **正式六下载** `.local/cli64-final-39114174841/release-downloads/` 已认证下载，逐字节等于同提交CI候选；全部载荷/二进制/manifest/架构/权限/许可/安装说明通过。独立代理从原始ZIP内存重验全部19份service资料及六下载通过。发布后尚未运行这些二进制；最终运行留CLI6.5。
- SHA256SUMS：506字节，SHA `97c8dae2ccfb1bbbdf242c40199cfda1fa50ed75519af0b3951b6c1b675e2ac2`；五包SHA/大小/远端资产ID在正式收据。
- 最终原始证据 `.local/cli64-final-39114174841/`；首次失败 `.local/cli64-ci-39114174841/`、`.local/cli64-publish-first/`；核验脚本 `.local/cli64-preparation/collect_final.py`。两份publication artifact的数值ID不按时间排序，按created_at与内部run_attempt判别，原文件完整保留。

## CLI6.5 精确下一步

1. 先核对Git/计划及本收据，刷新注册表两版本、tag、Release及六资产状态；不要重新发布、移动标签或重跑上传。gh配置读取可能需要已有审批流程；凭据只在工具内使用，不输出或保存。
2. 新增0.2.0独立消费工程和收据，使用全新cache与正式注册表 `lingose = "=0.2.0"`，全部库API/新函数基本调用通过。旧0.1.0注册表工具/历史消费者保持原字节，不能改写为新版证据。
3. 在checkout外新cache实际执行 `cargo install lingose-cli --version 0.2.0 --locked`，依赖准备后离线/locked复跑，确认无path/patch借用checkout。运行完整查询/标注/JSON/文件/stdin等场景，来源/归档身份与正式注册表对应。
4. 认证下载本次private Release（或先刷新远端身份再使用已核定的正式下载），按实际平台验证脱离源码运行；其余平台与本轮CI原生结果分别列明，不把本机结果外推。runtime无需外部词库。
5. 更新最终验收说明/独立收据/计划/交接并聚焦提交。CLI7 winget/scoop仅延期候选，不自动推进。

## crates.io 已发布版本：禁止重复上传

- `lingose 0.2.0`：41文件/4,053,096字节，SHA `91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5`；上传后连接断开但远端成功，仅上传1次。收据 `docs/cli-library-publication-verification.json`。
- `lingose-cli 0.2.0`：7文件/16,498字节，SHA `3f2e31e77ac7bdcedecb90871597d9821f60119f437be9a2cd7c523faa894490`。第一次403后核实未发布，用户更新cargo login后第二次成功，仅一次接受。收据 `docs/cli-cli-publication-verification.json`。
- 上述两版及lingose0.1.0均不得重传。发布载荷/README、旧版消费者与历史证据保持原字节。CLI6.3归档隔离安装不替代CLI6.5注册表名称安装。

## 保留边界

- 本轮没有Rust源码/词库/固定向量/根锁/相邻仓库变化；未重复全量差分/性能。已发布crate未变；原作者/许可与用户既有处置沿用，Frequency List和部分分类来源许可缺口继续披露。
- Windows VCRUNTIME140/UCRT、Linux/macOS系统动态库前提，macOS公证/Gatekeeper/旧OS未验及CLI4.1首启超预算事实保留。
- 一次只读artifact EOF保留截断/错误后重取且摘要通过；Git推送重复ref错误后API确认已在准确提交，未盲重推。未绕过审批或输出凭据。
