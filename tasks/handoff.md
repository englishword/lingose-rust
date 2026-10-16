# Lingose Rust 交接记录

## 当前任务与状态

- **P6.2 已完成；下一任务 P6.3，从 crates.io 独立安装验收（未开始）**。
- 用户已明确要求“commit 之后继续P6.2”，覆盖此前不 commit 的限制。
  P6.1 记录先提交为 `1313330`；本阶段完成后按项目流程提交 P6.2 记录。
- **lingose 0.1.0 已真实发布并进入索引；不要再次上传同一版本。**
- [版本页](https://crates.io/crates/lingose/0.1.0)；发布时间
  2026-10-16 13:14:35 UTC（北京时间 21:14:35）。注册表发布者及所有者为 `Prefee`，
  版本未撤回；官网/GitHub/许可/名称/版本与候选一致。
- 用户手改 README/SOURCES 提交 `5db9824` 保持原样；生产代码/数据/依赖未改。
  许可处置和发布账号/首次发布权限已由用户确认，P6.1 历史记录保留。

## 发布身份与恢复文件

- [todo.md](todo.md)：P6.3 任务。
- [发布说明](../docs/publication.md)、[完整收据](../docs/publication.json)：
  真实上传、注册表 API、README HTML、索引、匿名下载及原始日志身份。
- [P6.1 核对](../docs/publication-preflight.md)与 JSON：前置验证和完整分发输入。
- 正式发布包：**4,048,633 字节，41 文件，13 个有效本地文档链接**。
- SHA-256：`fb1a40407222053fa2acf6b92be99e59648d8e2a7ceac3c7f20182bbb393c6a8`。
  P6.1 候选、实际上传归档、版本 API、sparse index、匿名重新下载的包全部匹配。
- 本地已发布候选：`.local/p61-5db9824/lingose-0.1.0.crate`；
  源码快照 `.local/p61-5db9824/source`，无 .git，提交/逐文件摘要绑定来源。
- 真实 Cargo 上传归档：
  `.local/p61-5db9824/package-target/package/tmp-crate/lingose-0.1.0.crate`。
- 远端重新下载：`.local/p62-1313330/download.crate`。
- 上传收据/日志：`.local/p62-1313330/attempt.json`、`cargo-publish.*.log`。
  Cargo 退出码 0，明确 Uploaded/Published，等待索引完成；仅一次上传。
- 远端证据：同目录 `remote-observations.json`、`remote-summary.json` 及各 `*.body`。
  本地 `publish_once.py` 拒绝重复执行；若恢复任务不得绕过该重复上传保护。
- 旧 `.local/p53-readable` 候选含旧文档，仅保留历史，不是本次发布包。
- docs/packaging.md、docs/package-verification.json、P4/P5/P6.1 JSON 均为保留历史。

## 已验证与尚未验证

- P6.2 上传前再次检查远端不存在、凭据已配置、候选与全部当前分发输入一致；
  使用正常用户环境运行 cargo publish --locked --all-features --registry crates-io。
- 发布后版本 API/索引/所有者/README HTML/真实下载通过；手改 README/SOURCES 与
  下载包内文件逐字节一致，全部输入前后不变，令牌不进入命令参数、日志或仓库。
- P6.1 两套 Rust 1.93.1/1.85.0 独立离线消费者的 18 入口、5 文档测试及 dry-run
  已通过，但消费者当时使用本地解包 path 依赖，**不计为 P6.3 注册表安装验收**。
- 本阶段未新测其他平台、全量差分/性能，也未声称浏览器页面渲染验证。
  P4.2 新路径首启超预算事实和 Windows x86_64 MSVC 范围继续保留。
- 用户许可确认不描述为独立授权审计；不重写来源数据库/历史收据/相邻仓库。

## 下一步精确动作

1. 核对 Git 与本交接，恢复 **P6.3**。先读取 docs/publication.json，并查远端版本仍为
   上述 SHA；已有真实发布，不执行 cargo publish。
2. 在本项目之外的新临时目录建立独立消费者，依赖为 crates.io 的
   `lingose = "=0.1.0"`，不能使用 path/patch 指向 checkout 或候选解包。
   使用独立 Cargo home/target；依赖准备后，核对 metadata 中 lingose registry 来源、
   Cargo.lock 的 checksum 与正式 SHA，避免借用本地词库或相邻项目。
3. 复用 tools/package_consumer.rs 的 18 入口内容断言（先核对其身份）进行基本调用；
   依赖准备完毕后离线 locked release 构建，并从只有二进制的目录运行。
   平台/工具链覆盖按本阶段实际执行结果记录，不能扩大支持声明。
4. 核对官网/GitHub 和正式版本文档可访问性；docs.rs 可能尚在异步构建，先查实际状态。
5. 验证后勾选 P6.3，新增独立验收证据，更新最终交接并聚焦提交。
