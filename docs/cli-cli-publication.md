# CLI6.3：lingose-cli 0.2.0 正式发布

**`lingose-cli 0.2.0` 已发布并核验。** 注册表接受时间为
**2026-10-18 08:36:22.922509 UTC**，publisher/owner 为 **Prefee**，版本未 yank。
最终候选、两次 dry-run、实际上传与匿名下载逐字节一致。
第一次上传被令牌权限拒绝；用户更新本机凭据后，第二次独立受保护尝试成功。
见 [crates.io 版本](https://crates.io/crates/lingose-cli/0.2.0) 和
[完整脱敏收据](cli-cli-publication-verification.json)。

## 最终候选

| 项目 | 核验结果 |
| --- | --- |
| 包名 / 二进制名 | `lingose-cli 0.2.0` / `lingose` |
| 真实归档 | 16,498 字节，7 文件 |
| SHA-256 | `3f2e31e77ac7bdcedecb90871597d9821f60119f437be9a2cd7c523faa894490` |
| 载荷 | `Cargo.toml`、`Cargo.toml.orig`、`Cargo.lock`、`LICENSE`、`README.md`、`SOURCES.md`、`src/main.rs` |
| 库依赖 | 正式注册表 `lingose 0.2.0`，SHA `91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5` |
| 元数据 | edition 2024、MSRV 1.85、CC-BY-4.0、原作者、官网与具体仓库链接一致 |

先在正式 manifest 保留 `publish=false` 时验证受保护候选：7 文件、16,506 字节，
SHA `0400ccbbe12d25579e3713a9ef1f28b4d4639c72f0e345b9c19fa634413b9c9e`。
随后只移除 CLI 发布保护并重验最终候选；README 同步移除“尚未发布”前提，
安装命令现已可用于正式版本。根 README 同步发布状态；库包输入、根锁、Rust 实现、数据和许可证均未改。

归档来自逐字节核对的 workspace 快照，未携带或伪造 VCS 元信息。
规范化 manifest 中没有开发库 path、git、patch、replace 或 workspace 依赖；
原始 manifest 继续保留 `path + version`。包内 binary 的 `path = "src/main.rs"`
是目标源码路径。根锁的所有外部版本、checksum 和依赖边完全保留，仅显式将本地
`lingose 0.2.0` 行映射为正式注册表来源与 checksum；没有采用 CLI6.2 探针的新锁。

全部载荷及 3 个包内 Markdown 文件链接通过检查，无词库副本、开发数据库、工具、
缓存或绝对主机路径。CLI 包不包含集成测试，未把包内测试缺席说成回归通过。
Windows 实际启用的 18 项外部依赖版本/许可逐项匹配 CLI4.2 声明。

## 真实归档的隔离安装

受保护及最终候选分别解包到 checkout 外的新临时目录；各用全新空 `CARGO_HOME`，
没有拷贝用户配置、凭据或旧缓存。先在线 fetch，再执行 offline/locked metadata 和安装。
库及所有依赖来源均为 crates.io；下载的库归档摘要与已发布版本一致。

Rust **1.93.1** 和 **1.85.0** 均从真实 CLI 解包目录执行：

```text
cargo install --path <unpacked-cli> --root <isolated-install> --locked --offline
```

两套工具链分别完成 25 个固定预期场景，包括六字段查询、未知词、help/version、
标注阈值、UTF-8/CRLF、stdin、空输入、文件/同名文本、JSON、输出文件及错误退出码。
运行前移开源码与 cache 原路径，PATH 仅保留 System32，从仅含二进制的目录调用。
两个阶段合计 100 个运行场景；最终阶段 50 个通过。另有本轮 checkout 的
29 项 CLI 测试及 fmt 检查通过；没有重复全量差分/性能或完整 workspace 回归。
这里验证的是解包归档安装；正式注册表名称安装仍留 CLI6.5。

## dry-run、权限拒绝与凭据更新

联网执行 `cargo publish -p lingose-cli --dry-run --locked --registry crates-io` 成功，
其归档与最终候选逐字节相同。遵循 [Cargo 发布规则](https://doc.rust-lang.org/cargo/reference/publishing.html)，
包体积低于当时文档的 10 MB 限额。

首次上传前再次检查版本 API/index 不存在，并以独占方式创建
`.local/cli63-91cd10a/attempt.json`，随后执行：

```text
cargo publish -p lingose-cli --locked --registry crates-io
```

Cargo 退出 **101**，服务端返回：

```text
403 Forbidden: this token does not have the required permissions to perform this action
```

随后匿名核对版本 API 和 index 均为 404。`attempt.json` 和原始 stdout/stderr 保留，
没有删除标记或用相同凭据重试。原始证据在 `.local/cli63-91cd10a/`，
候选收据分别为 `guarded-verified/report.json`、`final/report.json`；
`prepared.json` 记录 dry-run，`after-attempt-state.json` 记录拒绝后的远端状态。

原令牌不足以发布新名称；错误本身无法区分 endpoint scope 与 crate scope。
用户随后确认“已创建令牌并完成 cargo login”；本机凭据修改时间也晚于被拒尝试。
首次创建需要允许 `publish-new` 且 crate 范围包含 `lingose-cli`。
这两类范围彼此独立，见 [crates.io 令牌说明](https://blog.rust-lang.org/2023/06/23/improved-api-tokens-for-crates-io/)
和 [scope 定义](https://rust-lang.github.io/rfcs/2947-crates-io-token-scopes.html)。令牌不进入聊天或仓库。
更新凭据后再次核对远端仍不存在、候选输入未变，重新执行同字节联网 dry-run。
第二次尝试使用独立的 `attempt-2.json`、`publish-2.*.log`、`publish-target-2/`，
首次拒绝记录不覆盖。Cargo 明确报告 Uploaded/Published 并退出 **0**。
正式上传命令合计 **2 次**：首次被拒、第二次接受，接受后的版本禁止重复上传。

## 注册表验收

[版本 API](https://crates.io/api/v1/crates/lingose-cli/0.2.0)、
[sparse index](https://index.crates.io/li/ng/lingose-cli) 及
[匿名静态归档](https://static.crates.io/crates/lingose-cli/lingose-cli-0.2.0.crate)
均对应最终候选的 16,498 字节与 SHA。下载载荷逐字节一致，重新执行完整归档检查通过。
owner/publisher、未 yank、edition/MSRV、许可、官网/仓库元数据及注册表 README 均通过；
README 含正式安装命令且没有“尚未发布”前提。
download/readme API 在 JSON Accept 下返回官方静态 URL，核验器跟随固定官方地址取得真实内容。
`remote-verification-2.json` 保存匿名核验原始收据。

独立代理此前已核对 136 项候选/首次尝试引用证据和 18 项依赖许可；
第二次上传新增22项引用及7个匿名端点独立核验通过，连同最终收据共303项引用、
280个独立路径摘要闭合；匿名归档与候选逐字节一致。外部临时 EXE 的独立重算摘要受读沙箱限制，
主核验器已记录安装后二进制摘要，安装/运行日志已独立核对。
库0.1.0/0.2.0的远端摘要与未yank状态再次核对不变。

沙箱 Schannel TLS 失败、临时核验脚本的清单/分隔符适配，以及一次审批服务额度中断
均留在准备记录中；正常用户环境重新验证通过，没有绕过审批。

## 后续边界

CLI6.3 已完成。CLI6.4 的 tag/Release/工作流上传路径和仓库公开下载可见性，
以及 CLI6.5 的正式注册表安装/Release 下载验收均未执行。库 `0.1.0`、`0.2.0`
不得重复上传；库已发布归档和既有历史收据不改。
现有五平台 CI 证据仍保留，当前 manifest/README 变化要求 CLI6.4 构建新的候选资产。
许可沿用用户对未变来源字节的既有确认，Frequency List/部分分类资料缺口继续披露。
