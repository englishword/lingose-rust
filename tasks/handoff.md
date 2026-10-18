# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，流程：[AGENTS.md](../AGENTS.md)。
- **CLI6.3 已完成，`lingose-cli 0.2.0` 已正式发布并匿名核验。下一项 CLI6.4：GitHub Release 五平台资产。** 本轮止于 CLI6.3，未创建标签/Release、未改工作流或仓库可见性，未执行 CLI6.5 注册表名称安装验收。
- 从干净的 `main / 91cd10a` 恢复。受保护候选验证后移除 CLI publish=false，更新 CLI/根 README 和本项说明/收据/计划/交接；无 Rust、库包、数据或根锁变化。提交以 Git 历史为准，不 amend。
- [CLI 发布说明](../docs/cli-cli-publication.md)、[完整收据](../docs/cli-cli-publication-verification.json)。原始响应/日志/脚本和两次独立标记在 `.local/cli63-91cd10a/`。

## 禁止重复上传已发布版本

- `lingose-cli 0.2.0` 注册表接受时间 **2026-10-18 08:36:22.922509 UTC**，publisher/owner **Prefee**，未 yank；**7 文件、16,498 字节**，SHA **`3f2e31e77ac7bdcedecb90871597d9821f60119f437be9a2cd7c523faa894490`**。最终候选、两次dry-run、实际上传、API/index/匿名下载全部同字节。
- CLI正式上传命令共 **2 次**：`attempt.json` 记录首次 **403 token permissions / Cargo101**，随后API/index404；用户更新令牌并确认“已创建令牌并完成 cargo login”后，保留原记录，独立 `attempt-2.json` 记录第二次 **Cargo0、Uploaded/Published**。不是盲重试，不删除或覆盖首次标记。`remote-verification-2.json` 为最终远端成功收据。
- 库 `lingose 0.2.0` 已于2026-10-18 07:43:13.810692 UTC发布，41文件/4,053,096字节，SHA **`91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5`**。其CLI6.2上传后连接断开退出101，但远端核验成功，仅上传1次；[库收据](../docs/cli-library-publication-verification.json)，原始证据 `.local/cli62-7578b10/`。
- **CLI0.2.0及库0.1.0/0.2.0均禁止再次上传。** 恢复遇中断先核查远端。已发布库载荷/README及历史证据保持原字节。

## CLI6.4 精确下一步

1. 核对Git、计划及本收据，刷新origin/账号权限/仓库可见性、`v0.2.0` tag/Release是否存在及Actions状态；不能把旧验证当当前远端事实。
2. origin为 `https://github.com/englishword/lingose-rust.git`；CLI6.1曾确认Prefee admin/push/maintain及repo/workflow scope，仓库仍private。匿名公开下载需明确可见性处置或公开分发仓库；未授权公开全部源码/历史。先完成可独立进行的具体准备，不提前创建不符合可见性条件的正式发布。
3. 当前workflow仍 `contents: read`、仅上传CI artifacts。准备仅正式 `v0.2.0` 标签的Release上传路径/最小权限，并以最终manifest/README构建新候选及五目标证据。旧run `39101457134`、构建 `d16c53773c0fb7e6f21dd2d1544ddcdc549734f3` 和 `.local/cli52-dist-d16c537/` 不代表本轮身份；不能直接沿用旧资产SHA/revision。
4. 按计划发布五个固定名称归档、SHA256SUMS及版本说明，核对许可/使用说明及实际下载身份；CI构建、目标运行、上传、Release下载分别留证。已有阶段授权不重复询问；未有的仓库公开授权不推定。
5. CLI6.4完成后交接CLI6.5。正式 `cargo install lingose-cli --version 0.2.0 --locked`、新cache库消费者及Release下载验收留CLI6.5，本轮没有提前执行。

## 可复用验证与候选身份

- `.local/cli63-91cd10a/final/lingose-cli-0.2.0.crate` 与 `final/report.json` 保存真实候选/输入/载荷/命令；`final/source/` 为逐字节核对的workspace快照，无伪造VCS信息。`prepared.json` / `prepared-2.json` 记录两次同字节dry-run。
- `guarded-verified/report.json` 为保护开启时先行验证：16,506字节、SHA `0400ccbbe12d25579e3713a9ef1f28b4d4639c72f0e345b9c19fa634413b9c9e`。通过后才移除CLI正式保护并重验final，两个摘要不混用。
- 源manifest保留 `path + version`，规范manifest无开发库path/patch/git/workspace依赖；根锁仅显式映射本地库为正式registry+SHA，其余全部身份/依赖边不变，未使用CLI6.2探针新锁。
- 全部载荷、3个包内链接、原作者/许可/官网/具体仓库通过；18项Windows启用外部依赖版本/许可与CLI4.2一致。无开发数据库、缓存、工具或绝对主机路径。
- 两候选各在checkout外全新Cargo home在线fetch，再offline/locked metadata和真实解包安装。Rust1.93.1/1.85.0各25场景通过，运行前移开源码/cache、PATH仅System32。最终50、两阶段合计100场景。**不是CLI6.5的注册表名称安装。** 本轮29项CLI测试/fmt通过，未重复全量差分/性能/workspace。
- 独立审查核对候选/许可/锁及首次尝试136项引用证据，成功上传/匿名远端另独立复核。外部临时EXE受读沙箱限制，未由独立代理重新hash；主核验器保存了安装后二进制摘要与运行日志。

## 保留边界

- 沙箱Schannel TLS失败、临时核验脚本清单/分隔符适配、一次审批服务额度中断均已留证；用户恢复后重新审批成功，没有绕过审批。令牌不进聊天/日志/仓库。
- 账号/许可确认沿用既有记录，来源字节未变；Frequency List与部分分类资料缺口仍披露，项目许可不重新授权第三方材料。
- Windows VCRUNTIME140.dll/UCRT及Linux/macOS系统动态库前提不变；未做macOS公证/Gatekeeper/旧OS验收；CLI4.1首启超预算事实保留。
