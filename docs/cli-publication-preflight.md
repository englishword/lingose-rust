# CLI6.1 发布条件核对

2026-10-18 从干净的 `main / 3f27f7a` 恢复。本项审核已完成，**库可进入 CLI6.2**；
CLI 新包权限、真实归档及公开 GitHub 下载仍有下述阶段条件。
完整脱敏记录见 [verification JSON](cli-publication-preflight-verification.json)，
原始响应、日志、字节核对快照和候选在 `.local/cli61-3f27f7a/`。
本轮没有上传 crate、创建标签/Release、更改仓库可见性或修改工作流。

## 授权与许可处置

- 用户指令为“根据 handoff.md 继续CLI6.1”，本轮止于本项。`TASK_CLI.md` 已明确
  两包 `0.2.0` 和指定仓库五平台 Release 的交付目标，不重复审批有效计划。
- [既有发布核对](publication-preflight.json)记录用户“本机具备发布 lingose，账号名 Prefee”
  及“已确认许可，勾选即可”。后者明确包含 Frequency List 和外部分类词表的既有缺口。
- 将确认落盘的 `1313330` 与迁移后路径对照，`data/SOURCES.json`、`UPSTREAM-SOURCES.md`、
  `frequency.bin`、`lexicon.bin` 四个 Git blob 完全相同，因此沿用该用户处置确认；
  逐项 blob 身份写入新收据，无需重复询问。
- 这仍属于**用户确认**，没有取得新增独立第三方许可文件。Frequency List 独立许可、
  部分分类逐标签来源/许可记录的缺口继续保留。项目 CC BY 4.0 和 44 项可用 notice
  不构成第三方资料重新授权或完整独立授权审计。

## 注册表和账号

2026-10-18 07:25 UTC，API 与 sparse index 交叉核对：

| 项目 | 实时结果 | 证据性质 |
| --- | --- | --- |
| `lingose 0.1.0` | 存在、未 yank，原摘要 `fb1a4040…393c6a8` 不变 | 独立 API/index 核对；不得重复上传 |
| `lingose 0.2.0` | API 404，index 没有该版本 | 尚未发布；上传前再查 |
| `lingose-cli` / `0.2.0` | crate/version API 和 index 均 404 | 尚未发现注册，不是名称预留或服务端接受保证 |
| `lingose` owner | `Prefee`，crates.io user ID `379268` | 独立 owner API 核对 |
| GitHub 当前账号 | `Prefee`，GitHub ID `24503861` | 独立认证 API 核对；两系统 ID 不同 |

读取当前 Cargo 凭据仅在内存中进行，未输出、复制或保存令牌。两个只读认证探针分别返回
website-only 和 endpoint-scope 的 403；按 [crates.io AuthCheck 源码](https://raw.githubusercontent.com/rust-lang/crates.io/main/src/auth.rs)
顺序，它们与已识别的 scoped token 一致。这是推断，不能据此读出准确账号、
`publish-update` / `publish-new` 或具体 crate scope。

库账号能力沿用用户既有确认并结合当前 owner；**不能把旧 `lingose` 发布或本次 dry-run
当作新名称 `lingose-cli` 的令牌权限证明**。CLI6.3 的实际权限仍须在该阶段核验；
若上传发生权限拒绝，停止处理并保留结果，不能盲目重试或记录为已发布。

## 精确候选与本次验证

重新按当前字节复制 workspace 快照，不复制 `.git`，未制造 VCS 信息。
用该快照重新执行库真实打包及 Cargo 解包编译验证，归档检查通过：

| 项目 | 结果 |
| --- | --- |
| 库包 | `lingose-0.2.0.crate`，41 文件，4,053,096 字节 |
| SHA-256 | `91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5` |
| 结构与来源 | 全部输入、19 个本地链接、3 个 Rust include、Unicode/许可与便携声明通过 |
| 体积 | 低于项目固定 5,000,000 字节预算 |
| 文档测试 | 从新解包库运行，7 项通过 |
| 联网 dry-run | `cargo publish -p lingose --dry-run --locked --all-features --registry crates-io` 退出 0；明确中止上传 |
| dry-run 归档 | `tmp-crate` 中归档与候选逐字节相同 |

全部库打包输入以及新归档与 [CLI4.3 收据](cli-package-verification.json)完全一致。
原 Windows Rust 1.93.1 / 1.85.0 独立消费者的 18 入口证据继续适用于这些相同字节；
本轮没有重复独立消费、完整差分、性能或整个 workspace 检查。
[Cargo 官方发布规则](https://doc.rust-lang.org/cargo/reference/publishing.html)已刷新：
文档列出 10MB `.crate` 限制，dry-run 不上传。项目的更小预算未放宽。

库候选在 `.local/cli61-3f27f7a/lingose-0.2.0.crate`，源码为其 `source/` workspace。
CLI6.2 应先核对当前库与该快照全部输入，再从同字节快照发布。
收据同时绑定根 `Cargo.toml` / `Cargo.lock` 的 `workspace_inputs`，覆盖 workspace 打包上下文。
直接对后续 Git 提交打包可能新增 `.cargo_vcs_info.json`，须另立候选，不能沿用本摘要。

五平台目录 `.local/cli52-dist-d16c537/` 仍严格含五归档和 `SHA256SUMS`。
本次重验五个摘要、manifest、闭合载荷、架构、模式及许可全文，全部通过；
57 项 build 输入与 53 项 packaging 输入均与 CLI5.2 收据相同。
构建身份仍为 `d16c53773c0fb7e6f21dd2d1544ddcdc549734f3`，
[原生 CI run 39101457134](https://github.com/englishword/lingose-rust/actions/runs/39101457134)
实时仍为 completed/success。完整 SHA 见新收据及 [CLI5.2 说明](cli-binary-assets.md)。
本轮未重跑这些二进制，不把旧下载验收计为新执行次数。

采集器曾将 dry-run 归档误定位到 `package/`；Cargo 本身成功，随后从实际
`package/tmp-crate/` 核对已有文件，未重复运行 Cargo。成功日志和纠正说明均保留。

## GitHub Release 的具体条件

origin 和目标仓库均为 `https://github.com/englishword/lingose-rust.git`。
认证 API 确认当前账号具备 admin/push/maintain，OAuth scopes 含 `repo`、`workflow`；
仓库未 archived/disabled，远端 main 与本轮起点一致，无 `v0.2.0` 标签和任何 Release。

仓库仍为 **private**。可以创建仅有权限者可下载的 Release；若需要匿名公开下载，
CLI6.4 前须明确可见性处置或公开分发仓库。当前任务没有授权公开全部源码/历史，
本轮不变更可见性，也不声称公开 Release 已就绪。

仓库默认 workflow permission 虽为 write，现有 workflow 明确 `contents: read`，
且只上传 CI artifacts，没有 Release 发布 job。CLI6.4 仍需：

1. 增加仅对正式标签执行的上传路径及所需 `contents: write`，不让 PR 触发写入。
2. 确定最终提交与 `v0.2.0` 对应身份，保留五个 build/package/download 的实际证据。
3. 上传五个规定名称的归档、`SHA256SUMS` 和版本说明，再从正式 Release 下载核对。

现有 `d16c537` 安装包属于旧候选。后续解除 CLI `publish=false`、改工作流或其他输入后，
须重新核定最终候选，不能把旧归档 revision 改称新提交。
[GitHub 官方 Release 说明](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
已核对所需写权限；本轮没有实写 Release。

平台限制继续适用：Windows 需兼容的 Visual C++ v14 x64 Runtime 和系统 UCRT；
Linux/macOS 仍依赖系统动态库。没有捆绑微软 DLL、Developer ID/公证或 browser
quarantine/Gatekeeper 验收。实际 runner 通过不证明所有旧 OS 可运行。

## 下一步

**CLI6.2：仅发布并核验 `lingose 0.2.0`。** 上传前刷新版本/owner 和快照输入，
核对实际 Cargo 归档摘要，成功后验证 API、index、匿名下载 SHA、docs.rs 及 CLI 注册表解析。
上传中断时先查远端，不盲重试；`0.1.0` 永不重复上传。CLI6.3–6.5 仍未执行。
