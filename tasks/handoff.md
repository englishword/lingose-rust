# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，流程：[AGENTS.md](../AGENTS.md)。
- **CLI6.2 已完成，`lingose 0.2.0` 已正式发布并核验。下一项 CLI6.3：CLI 真实归档、隔离消费、dry-run 和正式发布。** 本轮止于 CLI6.2，CLI 仍 `publish=false`；未创建 GitHub 标签/Release、未改工作流或仓库可见性。
- 从干净的 `main / 7578b10` 恢复；本轮提交以 Git 历史为准，不 amend。仅新增库发布记录/收据及更新计划/交接。
- [库发布说明](../docs/cli-library-publication.md)、[完整脱敏收据](../docs/cli-library-publication-verification.json)；原始日志、响应和一次上传标记：`.local/cli62-7578b10/`。

## 不得重复上传已发布库

- 注册表时间 **2026-10-18 07:43:13.810692 UTC**，publisher/owner **Prefee**，`lingose 0.2.0` 未 yank。
- 正式归档 **4,053,096 字节、41 文件**，SHA-256 **`91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5`**。CLI6.1 候选、最终正常用户 dry-run、实际上传、API/index、匿名下载和新 registry cache 归档全部一致。
- Cargo 实际上传后 Schannel `missing close_notify` 中断，退出码 **101**；立即检查 API/index 已存在精确版本，随后独立下载验证成功。正式上传命令只执行 **1 次**，未重试。原始 `attempt.json` 仍保存中断状态，最终收据明确记录远端成功的 reconciliation，不能把错误退出当未发布再传。
- `lingose 0.1.0` 仍为原摘要且未 yank。**两个库版本均不得重复上传**；后续任何中断恢复先查注册表。

## CLI6.3 精确下一步

1. 核对 Git、当前计划/本收据、库注册表状态与 `lingose-cli 0.2.0` 当前是否存在。CLI 新名称的 publish-new/crate scope 尚未独立读出，不拿旧库发布或 dry-run 当权限证明；如实际拒绝，保留错误并停止盲重试。
2. 当前 CLI manifest 是 `lingose-cli 0.2.0`，依赖 `lingose = { version = "0.2.0", path = "../lingose" }`，仍 `publish=false`。按计划先完成真实归档/注册表依赖/隔离消费候选验证，再解除 CLI 发布保护并重新核定候选、联网 dry-run 和正式上传。若 Cargo 在保护开启时拒绝 package，在隔离受控候选中调整保护，记录该差异，不能提前修改正式保护冒充验证通过。
3. 执行 CLI 真实清单、`.crate` 结构/体积/README 链接/依赖许可及独立解包安装检查；规范化包内 manifest 不含开发 path/patch，源码仍保留 path + version。正式检查使用仓库锁定依赖，不拿本轮解析探针生成的新锁代替。
4. 候选验证后按要求移除 CLI `publish=false`、核对变更后的新候选身份及 `cargo publish -p lingose-cli --dry-run --locked`。已有发布任务授权无需重复询问；凭据不得进入聊天、日志、仓库或交接。
5. 按 CLI6.3 仅发布 CLI，一次标记/远端重查防重复；成功后核对 API/index/download SHA。更新本项说明/收据、计划/交接并聚焦提交；GitHub Release 和正式安装验收分别留 CLI6.4/6.5。

## 本轮验证和可复用证据

- API/index/owner/匿名下载、完整载荷、19 本地链接、官网/具体仓库元数据和注册表 README 均通过。API download/readme 在 JSON Accept 下返回静态 URL，实际归档/HTML 从固定官方静态站获取。
- [docs.rs 0.2.0](https://docs.rs/lingose/0.2.0/lingose/) 和 [新函数](https://docs.rs/lingose/0.2.0/lingose/fn.annotate_ips_skip.html) 200；build `4898279` 列表标记全部成功。文档构建不是其他目标机运行证据。
- checkout 外全新临时 CLI 工程和空 Cargo home 已在线获取注册表库，并通过 offline/locked metadata。源码拷贝当前 CLI，只有去除库 path、加入隔离 workspace 的受控 manifest 差异；原 `publish=false` 保留，无库 path/patch、凭据/旧 cache/根锁复制。cache `.crate`、lock checksum、metadata source 均对应正式库。
- 该探针仅解析/fetch，**不是 CLI .crate、build、install、运行或发布验收**。临时工程路径和原始报告见 `.local/cli62-7578b10/cli-registry-resolution.json`；兼容补丁解析出的锁不是正式发布锁，当前根 Cargo.lock 未改。
- 独立代理再次匿名验证 API/index/下载 SHA、docs.rs 与 21 项引用证据摘要通过。CLI6.1/CLI4.3 的同字节库打包/文档测试/独立消费者证据保留；本轮没有重复全量差分、性能、workspace/MSRV 或正式独立安装。

## 继续保留的边界

- 已有账号/许可确认保存在 `docs/publication-preflight.json`，用户“已确认许可，勾选即可”继续适用于字节未变的来源数据。没有新增独立许可文本；Frequency List 及部分分类逐标签资料缺口仍披露，CC BY 4.0/44 项 notice 不重新授权第三方材料。
- GitHub origin 为 `https://github.com/englishword/lingose-rust.git`，CLI6.1 已确认 Prefee admin/push/maintain 和 repo/workflow scope。仓库仍 private；若需要匿名公开下载，CLI6.4 前须明确可见性处置或公开分发仓库，当前未授权公开全部源码/历史。
- 当前 workflow `contents: read`，只传 CI artifacts；CLI6.4 仍需仅正式标签的 Release 上传路径/权限。五归档和校验和在 `.local/cli52-dist-d16c537/`，旧构建身份 `d16c53773c0fb7e6f21dd2d1544ddcdc549734f3`，原始 run `39101457134`/证据在 `.local/cli52-ci-final/`。CLI manifest/工作流等后续变化要求新候选，不沿用旧 archive SHA/revision。
- Windows 仍依赖 VCRUNTIME140.dll/系统 UCRT；Linux/macOS 仍依赖系统动态库。未做 macOS Developer ID/公证、browser quarantine/Gatekeeper 或旧 OS 验收；CLI4.1 首启 675.43 ms 超预算事实保留。
