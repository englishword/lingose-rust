# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，流程：[AGENTS.md](../AGENTS.md)。
- **CLI6.1 已完成条件核对；下一项是 CLI6.2：仅发布并核验 `lingose 0.2.0`。** 本轮止于 CLI6.1，没有上传任何 crate、创建标签/Release、改仓库可见性或工作流。
- 从干净的 `main / 3f27f7a6db7c46960914dce730762d97dee065c9` 恢复；本轮提交以 Git 历史为准，不 amend。仅新增发布核对文档/收据及更新计划/交接。
- [发布核对说明](../docs/cli-publication-preflight.md)、[完整脱敏收据](../docs/cli-publication-preflight-verification.json)；本地原始响应、日志、快照和候选：`.local/cli61-3f27f7a/`。

## CLI6.2 精确下一步

1. 刷新 crates.io API/index：截至 2026-10-18 07:25 UTC，`lingose` 只有已发布且未 yank 的 `0.1.0`，owner 为 `Prefee`；`0.2.0` 及整个 `lingose-cli` 尚不存在。不存在不是名称预留。不要重复上传 `0.1.0`，任何上传中断后先查远端。
2. 核对新收据的 `workspace_inputs`（根 Cargo.toml/Cargo.lock）、`library_inputs`、`cli_inputs` 与当前 checkout 及 `.local/cli61-3f27f7a/source/` 快照一致；库候选 `.local/cli61-3f27f7a/lingose-0.2.0.crate` 为 **4,053,096 字节、41 文件**，SHA-256 **`91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5`**。
3. 从该同字节 workspace 快照执行库真实发布，沿用正常用户已配置凭据，不输出、复制或保存令牌。该快照不带 `.git`，输入/归档与 CLI4.3 相同；直接从后续提交打包可能新增 VCS 信息，不能沿用本摘要。库已解除 publish=false，CLI 仍为 false。
4. 本轮联网 `cargo publish -p lingose --dry-run --locked --all-features --registry crates-io` 成功，实际文件位于 `dryrun-target/package/tmp-crate/`，与候选逐字节相同。真实上传时再次核对实际归档；新 target/cargo 环境不得暗中改锁文件/来源。不要把 `.local/cargo-home` 的无凭据验证环境误当作用户发布凭据环境。
5. 成功后核对真实上传记录、API/index/download SHA、docs.rs 和元数据链接，等待注册表库依赖可解析；更新 CLI6.2 收据/计划/交接并聚焦提交。CLI6.3 以后仍按计划单独执行。

## 已核对的授权、许可与权限

- 用户已明确要求两包 0.2.0 及指定仓库五平台 Release。已有确认记录在旧 `docs/publication-preflight.json`：账号能力“本机具备发布 lingose，账号名 Prefee”；许可“已确认许可，勾选即可”。不重复询问同一授权。
- 许可确认对应的 `1313330` 与当前 `SOURCES.json`、`UPSTREAM-SOURCES.md`、`frequency.bin`、`lexicon.bin` 四项 Git blob 完全相同，沿用既有用户处置。**未取得新增独立许可文件**；Frequency List 独立许可、部分分类逐标签来源/许可缺口仍保留，44 项 notice 和 CC BY 4.0 不能冒充全面再授权。
- 当前库 owner API 独立确认 Prefee。Cargo token 存在；只读探针的 website-only/scope 403 与识别到 scoped token 一致，但未读出准确账号或发布 scope。库能力保留原用户确认；旧库发布和 dry-run 不证明新包 `lingose-cli` 的 publish-new/crate scope，CLI6.3 如遭权限拒绝须停止并记录。
- GitHub 认证账号 Prefee，仓库 admin/push/maintain；OAuth scopes 含 repo/workflow，已有设备授权有效。origin 是 `https://github.com/englishword/lingose-rust.git`。仓库仍 **private**，无 `v0.2.0` 标签或 Release。

## 后续 GitHub Release 条件

- 当前 workflow 明确 `contents: read`，只上传 CI artifacts；仓库默认 write 不覆盖该显式设置。CLI6.4 须增加仅正式标签可走的上传路径/权限，并确定最终候选提交。
- private 仓库可创建需权限访问的 Release；若目标是匿名公开下载，CLI6.4 前须明确可见性处置或公开分发仓库。当前指令未授权公开全部源码/历史，本轮不变更可见性，不宣称公开下载就绪。
- 五归档及 SHA256SUMS：`.local/cli52-dist-d16c537/`，本轮全部摘要/载荷/架构/模式/notice 重验通过，57 build/53 packaging 输入不变。候选身份仍为 `d16c53773c0fb7e6f21dd2d1544ddcdc549734f3`，原生 run [39101457134](https://github.com/englishword/lingose-rust/actions/runs/39101457134) 实时成功；本轮没有重跑二进制。
- 后续 CLI manifest（解除 publish=false）、工作流/notice/源码变化都需新候选身份，不把旧 archive SHA 或 revision 当作新构建。原始 17 CI artifact 与日志在 `.local/cli52-ci-final/`；正式 Release 下载验收仍属 CLI6.5。
- Windows 依赖 VCRUNTIME140.dll 和系统 UCRT，未捆绑微软 DLL；Linux/macOS 系统动态库仍需可用。未做 macOS Developer ID/公证或 browser quarantine/Gatekeeper 验收，旧 OS 支持不能从 runner 推断。

## 本轮验证范围

- 新库真实归档/编译、41 文件、19 链接、3 Rust include、来源/Unicode/许可、7 文档测试与联网 dry-run 通过；dry-run 归档完全一致，输入不变。
- 所有库打包输入和归档与 CLI4.3 完全相同，沿用其独立消费者证据；本轮没有重复全量差分、性能、workspace/MSRV 或独立安装。CLI4.1 首启 675.43 ms 超预算历史不变。
- 原始采集脚本 `.local/cli61_collect.py` 仅为本地审计，不入分发包。dry-run 后采集器曾找错归档路径，已用已有 `tmp-crate` 文件完成校验，未重复执行 Cargo；成功日志/纠正说明保留。
