# P6.2 lingose 0.1.0 正式发布

**lingose 0.1.0 已发布至 crates.io，索引与远端下载身份验证通过。**
用户要求“commit 之后继续P6.2”；P6.1 记录先提交为 `1313330`，随后执行本阶段。
完整收据见 [publication.json](publication.json)，前置条件见
[publication-preflight.md](publication-preflight.md)。P6.3 尚未执行。

## 真实发布结果

- 版本页：[lingose 0.1.0](https://crates.io/crates/lingose/0.1.0)。
- 注册表发布时间：**2026-10-16 13:14:35 UTC**（北京时间 21:14:35）。
- 注册表报告发布者及所有者均为 **Prefee**；版本未被撤回（`yanked=false`）。
- 包名/版本 `lingose 0.1.0`，许可证 `CC-BY-4.0`，最低 Rust 版本 `1.85`。
- 官网 https://lingose.com/ 和 GitHub https://github.com/englishword 均与用户稿一致。
- 远端压缩包 **4,048,633 字节**，SHA-256：
  `fb1a40407222053fa2acf6b92be99e59648d8e2a7ceac3c7f20182bbb393c6a8`。

## 上传与身份核对

发布使用 P6.1 已验证的 `.local/p61-5db9824/source/Cargo.toml` 快照，
源文档提交为 `5db9824`。上传前再次逐文件核对 checkout、快照、完整分发输入及
候选/dry-run 归档摘要，API 与 sparse index 均返回 404；已有凭据保持在默认 Cargo
凭据存储中，命令参数、工作区、收据及日志不包含令牌。

唯一正式上传命令为：

```powershell
cargo publish --locked --all-features --registry crates-io --manifest-path .local/p61-5db9824/source/Cargo.toml
```

实际命令在正常用户环境运行，CARGO_TARGET_DIR 指向 P6.1 已记录的 package-target，
CARGO_HOME 使用默认用户 Cargo 目录。Cargo 退出码为 0，依次报告
`Uploaded lingose v0.1.0` 和 `Published lingose v0.1.0`，等待索引完成后返回。
本次没有失败上传或重复上传；本地一次性执行脚本会拒绝在同一收据目录再次执行。

发布后核对以下五处 SHA-256 完全一致：P6.1 候选、实际 Cargo 上传归档、
[版本 API](https://crates.io/api/v1/crates/lingose/0.1.0)、
[sparse index](https://index.crates.io/li/ng/lingose) 和匿名重新下载的真实压缩包。
远端压缩包内 README.md/SOURCES.md 与用户提交原文逐字节一致，上传前后全部分发
输入不变；未从 checkout 重新引入不同的 VCS 信息或覆盖历史候选。

注册表的 README HTML 接口已核对主要章节及官网/GitHub 链接，crate API 的名称、
版本、说明、项目链接、许可、大小和发布账号均符合本次候选。浏览器渲染页面未作
额外声明；本阶段记录的是注册表 API、README HTML、索引及真实下载证据。

独立只读复核已核对全部原始记录摘要，并实时匿名重查版本、所有者及索引，
确认返回 200、Prefee 身份、版本未撤回和相同校验和；未发现实际不一致。

## 原始记录

- `.local/p62-1313330/attempt.json`：上传前观察、实际命令、时间、退出码及上传归档身份。
- `.local/p62-1313330/cargo-publish.stdout.log`、`cargo-publish.stderr.log`：真实上传日志。
- `.local/p62-1313330/remote-observations.json`、`remote-summary.json`：独立远端检查。
- 同目录 `crate.body`、`version.body`、`owners.body`、`index.body`、`readme.body`、
  `download.crate`：远端原始响应；完整 URL、摘要和时间均记录在 publication.json。
- 本地一次性守护脚本 `publish_once.py` 的身份亦已记录；它仅负责本次发布。
- P4/P5/P6.1 原始报告和来源资料未重写，用户手改稿和所有生产输入未改。

## 下一阶段

P6.3 从 crates.io 的正式 `0.1.0` 在独立消费工程安装，使用注册表来源而非本地
path 依赖，核对校验和与实际依赖来源；准备依赖后离线构建并验证全部公共 API，
核对官网/GitHub 和文档可访问性。当前匿名下载身份验证不代替该安装验收。
如果后续任务中断，先查已发布版本和收据，**不要再次上传 0.1.0**。
