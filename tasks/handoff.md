# Lingose Rust 交接记录

## 当前任务与状态

- **P6.1 已完成；下一阶段 P6.2 上传 lingose 0.1.0，本轮未开始**。
- 用户已手改 README.md/SOURCES.md 并提交 `5db9824`；本轮从该提交恢复，开始时
  工作区干净。手改稿保持原样，未恢复删文。沿用此前不 commit 要求，本轮未提交。
- 用户确认“已确认许可，勾选即可”：此前 Frequency List/外部分类词表的许可处置项
  按用户确认完成，未声称新增独立审计文件；历史来源记录不变。
- 用户确认“本机具备发布 lingose ，账号名Prefee”：账号 `Prefee` 和首次发布
  `lingose` 的权限按用户确认通过。默认 Cargo 凭据已配置，令牌未复制或输出。
- 只读 API 返回网站专用接口/范围限制；结合官方源码可推断令牌被服务识别，但无法
  独立读出账号/发布范围。当前无可用浏览器；账号和权限依据是用户确认，而非 403/dry-run。
- crates.io API 与 sparse index 于 2026-10-16 返回 404，未发现 lingose/0.1.0。
  这不是名称预留，上传前必须重查。
- **真实上传、crates.io 独立安装均未执行**，P6.2/P6.3 未勾选。

## 当前候选与证据

- [todo.md](todo.md)：P6 既定顺序。
- [发布条件核对](../docs/publication-preflight.md)与
  [完整脱敏收据](../docs/publication-preflight.json)：条件、逐输入身份、日志索引与边界。
- 新候选：`.local/p61-5db9824/lingose-0.1.0.crate`。
  - **4,048,633 字节，41 文件，13 个有效本地文档链接**。
  - SHA-256 `fb1a40407222053fa2acf6b92be99e59648d8e2a7ceac3c7f20182bbb393c6a8`。
  - 相对旧候选仅 README/SOURCES 分发输入不同；源码、资源、派生表、依赖不变。
- 源码快照：`.local/p61-5db9824/source`；无 `.git` 和 `.cargo_vcs_info.json`。
  以用户提交和完整输入摘要绑定来源；不能将 checkout 直接重打的包当作同一归档。
- 正常用户 dry-run 日志：`.local/p61-5db9824/logs/publish-dry-run.log`。
  实际产物 `.local/p61-5db9824/package-target/package/tmp-crate/lingose-0.1.0.crate`
  与候选身份相同；Cargo 明确因 dry-run 中止上传。
- 包内 5 文档测试日志：`.local/p61-5db9824/logs/package-doc-tests.log`。
- `.local/p53-package-9ofxsdk1/report.json`：新候选初始打包及两套独立消费者成功，
  最后沙箱 dry-run 遇 Schannel 凭据错误；原失败保留，正常用户重试另记成功。
- 旧候选 `.local/p53-readable/lingose-0.1.0.crate`（SHA `db227b4d...`）和原 P5.3
  收据保留为历史，**含旧版文档，不能作为本次手改版发布**。
- docs/packaging.md、docs/package-verification.json、旧 P4/P5 JSON 均未重写。

## 本轮验证与边界

- 新候选真实 package --list/package、逐输入/清单/摘要、必要资源/许可、本地链接及
  主机路径检查通过；低于固定 5,000,000 字节预算和当日官方 10MB 归档限制。
- 真实归档在独立临时工程解包，空 Cargo home 配 vendored 依赖，1.93.1/1.85.0
  各自 offline locked release 构建及 18 公共入口内容断言通过；运行时仅有二进制，
  源码路径局限隔离目录，无 registry cache，两套输出相同。
- 当前包内 5 文档测试、正常用户联网 dry-run 通过，全部分发输入验证后仍不变。
  文档日志的 PowerShell NativeCommandError 包装来自 stderr，Cargo 退出码实际为 0。
- 独立只读复核确认归档、日志及来源身份一致，原始项目/Unicode 许可与上游声明完整。
- 未重跑全量差分/性能；平台仍仅 Windows x86_64 MSVC。P4.2 新路径首启超预算
  的历史事实保留。未改源数据、相邻仓库、安装库或原始历史记录。
- 官网/GitHub 链接保持用户版本，不编造具体仓库地址；令牌不进入聊天、仓库或日志。

## 下一步精确动作

1. 后续进入 P6.2 时，重查远端名称/0.1.0 是否已存在、配置凭据、候选全部输入及摘要。
   不重复询问已确认的许可、账号与发布权限。执行阶段授权以届时用户指令/既有授权为准。
2. 使用本轮 `.local/p61-5db9824/source/Cargo.toml` 准备发布；保留相同分发输入和
   归档身份。输入有变时建立新候选，不把含 VCS 信息的新包冒充本次候选。
3. P6.2 若上传中断，先查远端状态；成功后记录实际上传和索引可用证据。
4. P6.3 从 crates.io 正式版本建立独立工程，依赖获取后离线重跑公共 API 并核对文档链接。
