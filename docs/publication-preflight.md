# P6.1 正式发布条件核对

本轮从用户手改提交 `5db98249ef75be4bd2ae38a832b3a99999c9bf99` 恢复。
**P6.1 已完成**；本轮没有上传，P6.2/P6.3 尚未开始。沿用此前不 commit 的要求。
原始命令、输入摘要与脱敏远端观察见 [publication-preflight.json](publication-preflight.json)。

## 条件核对结果

- 用户授权继续 P6.1；手改 README/SOURCES 为本次候选文档依据，未恢复已删除内容。
- 2026-10-16 的 crates.io API 与 sparse index 检查均返回 404，未发现 `lingose`
  或其 `0.1.0` 版本。这是当时的可见状态，不是名称预留或服务端发布承诺。
- 许可处置项按用户本轮确认“已确认许可，勾选即可”完成。范围为此前记录的
  Frequency List 和部分外部分类词表许可资料缺口；未声称取得新的独立审计文件。
- 本机默认 crates.io 令牌已配置。只读认证请求返回网站专用接口/权限范围限制，
  结合官方 `AuthCheck` 源码顺序，可推断服务识别了有效的受限令牌；接口未返回账号
  或发布范围。当前没有可用浏览器可查看登录账号。
- 用户随后确认“本机具备发布 lingose ，账号名Prefee”。因此账号 `Prefee` 及
  允许首次发布 `lingose` 的权限按用户确认记为通过。该结论不来自 dry-run 或 403，
  也不声称已独立读取服务端令牌范围。令牌未进入聊天、仓库或日志。

## 新候选与验证

用户提交相对 P5.3 仅修改 README.md、SOURCES.md；生产代码、资源、Unicode 表、
依赖锁和原始许可均未改。旧候选保留为历史证据，本次建立独立新候选：

- 归档：`.local/p61-5db9824/lingose-0.1.0.crate`。
- 大小：**4,048,633 字节**；**41 个文件**、**13 个有效本地 Markdown 链接**。
- SHA-256：`fb1a40407222053fa2acf6b92be99e59648d8e2a7ceac3c7f20182bbb393c6a8`。
- 源码快照：`.local/p61-5db9824/source`。快照不含 `.git`；通过起点提交和逐文件摘要
  绑定来源，不伪造干净 VCS 身份。JSON 内保留完整分发输入身份。
- 实际 `cargo package --list`、`cargo package --offline --locked --all-features`
  以及逐文件、主机路径、链接和必要资源/许可闭包检查通过。归档小于固定
  5,000,000 字节预算及当日 [Cargo 官方说明](https://doc.rust-lang.org/cargo/reference/publishing.html)
  列出的 10MB 上限。
- 真实归档在独立临时消费工程解包，空 Cargo home 配 vendored 依赖，分别使用
  Rust 1.93.1 和 1.85.0 离线 release 构建；独立运行时的 18 个公共入口内容断言
  通过，两套输出相同，依赖源码均局限隔离目录，未使用注册表缓存。
- 包内当前 README 的 5 个文档测试通过（含 2 个编译失败示例）。PowerShell
  将 Cargo 的标准错误流包装为 `NativeCommandError` 文本；Cargo 实际退出码为 0，
  测试结果全部通过。
- 正常用户环境中的 `cargo publish --dry-run --locked --all-features --registry crates-io`
  通过，并明确 `aborting upload due to dry run`。其实际生成的
  `package-target/package/tmp-crate/lingose-0.1.0.crate` 与上述候选摘要相同。
- `.local/p53-package-9ofxsdk1/report.json` 保留最初沙箱 Schannel 凭据错误。
  其中此前打包和两套消费者均成功；正常用户重试日志单独保存在新候选目录，
  没有关闭 TLS 校验，也没有覆盖原始失败或旧 P5.3 收据。
- 独立只读复核确认所有分发输入与 HEAD、工作区、快照一致，归档与 dry-run 产物
  逐字节相同，原始项目/Unicode 许可及上游声明完整，消费者与文档日志摘要一致。
- 验证平台仍仅 Windows x86_64 MSVC；未重跑全量差分/性能，未重写历史 JSON。

## 后续精确动作

下一阶段为 P6.2。进入该阶段时，立即复核远端名称/版本、配置凭据、候选全部输入和
摘要；使用本轮快照。若输入发生变化，建立新候选及对应验证，不将 checkout 直接重打
的含 VCS 信息归档描述为同一文件。上传中断时先查远端状态，不盲目重传。
P6.2 记录真实上传及索引可用证据；P6.3 再执行从 crates.io 独立安装验收。

认证边界的官方实现参考：[AuthCheck](https://github.com/rust-lang/crates.io/blob/main/src/auth.rs)、
[账号接口](https://github.com/rust-lang/crates.io/blob/main/src/controllers/user/me.rs)、
[令牌接口](https://github.com/rust-lang/crates.io/blob/main/src/controllers/token.rs)、
[发布权限检查](https://github.com/rust-lang/crates.io/blob/main/src/controllers/krate/publish.rs)。
