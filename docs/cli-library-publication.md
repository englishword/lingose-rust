# CLI6.2：lingose 0.2.0 正式发布

**`lingose 0.2.0` 已发布并核验**，注册表接受时间为 **2026-10-18 07:43:13.810692 UTC**，
发布者和 owner 为 **Prefee**，版本未 yank。
见 [crates.io 版本](https://crates.io/crates/lingose/0.2.0)、
[完整脱敏收据](cli-library-publication-verification.json)。
本轮从干净的 `main / 7578b10` 恢复，仅执行 CLI6.2；`lingose-cli` 和 GitHub Release 未发布。

## 一次上传与连接中断处置

上传前重新核对 CLI6.1 的 workspace/库/CLI 上下文输入及字节快照；
API 仍返回 0.2.0 不存在，index 仍只有 0.1.0，owner 为 Prefee。
正常用户 Cargo 环境的最终 dry-run 通过，实际归档与批准候选逐字节相同。

从 `.local/cli61-3f27f7a/source/` 同字节 workspace 快照执行一次：

```powershell
cargo publish -p lingose --locked --all-features --registry crates-io
```

Cargo 完成打包/编译验证并上传后，因 Schannel `missing close_notify` 连接中断退出 **101**。
没有把这一退出码改写成成功，也没有重试上传。立即查询远端发现 API 和 index 已存在 0.2.0，
注册表记录的发布时间、发布者与摘要符合本次候选；随后匿名下载和独立复核确认已接受。
本次正式上传命令总计 **1 次**。原始 `attempt.json`、错误日志和一次执行标记均保留；
后续恢复只继续核验，不再次发布该版本。

## 归档与注册表一致性

| 核对项目 | 结果 |
| --- | --- |
| 包名/版本 | `lingose 0.2.0` |
| 压缩体积/文件 | 4,053,096 字节 / 41 文件 |
| SHA-256 | `91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5` |
| 身份闭合 | CLI6.1 候选、最终 dry-run、实际上传归档、版本 API、sparse index、匿名下载全部一致 |
| 包内检查 | 全部载荷/manifest/19 个本地链接核对；README、SOURCES、许可和数据身份一致，无 VCS 元信息 |
| 元数据 | edition 2024、MSRV 1.85、CC-BY-4.0，官网及具体仓库链接正确 |
| 原版本 | 0.1.0 的原摘要和未 yank 状态不变，未重复上传 |

匿名验证保存 [版本 API](https://crates.io/api/v1/crates/lingose/0.2.0)、
[索引](https://index.crates.io/li/ng/lingose)、owner、README 及
[真实静态归档](https://static.crates.io/crates/lingose/lingose-0.2.0.crate) 的原始响应和 SHA。
API 的 download/readme 路由在 `Accept: application/json` 下返回官方静态 URL；
核验器据此跟随固定官方 URL 获取归档/HTML，而非把 JSON 元数据误认成归档。
注册表 README 包含新函数及官网/仓库链接。

## docs.rs 与 CLI 注册表依赖

[docs.rs 0.2.0](https://docs.rs/lingose/0.2.0/lingose/)、crate 页面、
[annotate_ips_skip 文档](https://docs.rs/lingose/0.2.0/lingose/fn.annotate_ips_skip.html)
和 builds 页面均返回 200，URL 保持 0.2.0。
[build 4898279](https://docs.rs/crate/lingose/0.2.0/builds/4898279) 列表标记
“All builds succeeded”；该文档构建不替代目标机运行或 CLI6.5 安装验收。

在 checkout 外创建全新临时 CLI 工程和空 Cargo home，复制当前 CLI 包输入，
仅将库依赖改为注册表版本并添加隔离 workspace，保留 `publish=false`。
在线 `cargo metadata --format-version 1` 获取依赖，再执行
`cargo metadata --format-version 1 --offline --locked`，两次均通过：

- CLI 的库依赖确为注册表 `lingose 0.2.0`，无 library path/patch/replace。
- metadata 的库源码位于全新 registry cache；lockfile checksum 和 cache 中真实 `.crate`
  与正式摘要一致。没有复制根锁文件、缓存或凭据。
- 这是**依赖解析与获取**，没有构建、安装、运行或发布 CLI，也没有完成其真实打包/dry-run。
  探针新锁文件中的兼容补丁版本不是正式发布锁文件；仓库 `Cargo.lock` 未改。

独立只读复核再次匿名查询 API/index、下载归档、检查 docs.rs 和 21 项引用证据摘要，全部通过。
原始证据位于 `.local/cli62-7578b10/`，隔离工程位置见本地解析收据；
脱敏提交记录将主机路径替换为可读占位符。凭据未进入日志、仓库或交接。

## 下一项与保留边界

**CLI6.3：完成 `lingose-cli 0.2.0` 真实归档、隔离消费、注册表 dry-run 和正式发布。**
库依赖已可由注册表解析，仍需按计划单独核验 CLI 新名称/token scope、真实归档及锁文件。
在候选验证前保留 CLI `publish=false`；解除保护后需重新核定身份，不沿用旧二进制候选 SHA。
`lingose 0.2.0` 与 `0.1.0` 均不得再次上传。

本轮未改生产代码、数据、manifests/lock、许可处置或相邻参考仓库；没有创建 GitHub 标签/Release、
改工作流或 private 可见性。CLI6.1 的许可资料缺口和后续公开 Release 条件继续保留。
