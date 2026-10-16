# Lingose Rust 交接记录

## 最终状态

- **P6.3 已完成，P0–P6 既定任务全部完成。当前没有待执行的既定阶段。**
- 本轮从 `621818a` 恢复；用户要求继续 P6.3，已完成正式注册表独立消费、离线验收和
  文档链接检查。按项目流程提交本阶段工具与证据；未再上传。
- **lingose 0.1.0 已发布，不得重复上传同一版本。**
- [正式版本](https://crates.io/crates/lingose/0.1.0)，发布时间
  2026-10-16 13:14:35 UTC，发布者/所有者 `Prefee`，未撤回。
- 用户手改 README/SOURCES（`5db9824`）及全部生产数据/代码/依赖保持不变。
  许可和账号权限确认依据、原始来源及历史证据保持原记录，不扩大为独立授权审计。

## 发布与验收身份

- 正式压缩包：**4,048,633 字节，41 文件，13 个有效包内文档链接**。
- SHA-256：`fb1a40407222053fa2acf6b92be99e59648d8e2a7ceac3c7f20182bbb393c6a8`。
  P6.1 候选、实际上传包、P6.2 远端下载/索引及 P6.3 新 Cargo cache 下载全部一致。
- [P6.3 验收说明](../docs/registry-consumer.md)与
  [完整证据](../docs/registry-consumer-verification.json)是本次最终消费记录。
- [发布说明](../docs/publication.md)、[发布收据](../docs/publication.json)保留真实上传证据；
  P6.1 及 P4/P5 历史记录未重写。
- `tools/check_registry_consumer.py`：可重复的只读验收工具，每次新建工程/cache/target/收据；
  不发布、不读取凭据、不复制旧 registry cache 或根 Cargo.lock。
- 固定消费者 `tools/package_consumer.rs` 身份仍为
  `1f8c62db06cfc3b7b390dd5c711cdb5daab320de63d5549eb7ce8fcdd94f5f9d`。

## P6.3 实际验证

- 独立工程：
  `C:/Users/Threadman/AppData/Local/Temp/lingose-p63-385ffe1b2c49/consumer`。
  依赖 `lingose = "=0.1.0"`，无 path/patch/source replacement；初始 Cargo home 为空。
- Cargo metadata/锁文件证明正式 crates.io 来源，11 个 registry 包的全部源码局限
  新 cache；checksum/真实下载/解包逐文件身份通过，根锁文件及相邻项目未借用。
- Windows x86_64 MSVC / Rust 1.93.1 正常 locked release 构建通过；另用各自全新 target
  完成 1.93.1/1.85.0 的 offline locked release 构建。三次独立 exe 运行的 18 个入口
  内容断言通过、输出相同；运行目录只有 exe，运行环境 Cargo home 为空。
- 固定字面量 smoke 涵盖公共查询、分类、标注、Unicode、阈值及错误；不等于全量
  差分/完整列表规范摘要，资源错误变体为合成兼容性检查，不是损坏包注入。
- docs.rs 正式 API/crate/builds、14 函数页和四大写别名、官网/GitHub 均 HTTP 200，
  目标内容/链接通过。未声称浏览器渲染或全部 GitHub 动态模块验收。
- 成功原始收据：`.local/p63-registry-385ffe1b2c49/report.json`，
  同目录工具快照/日志/21 个 HTTP 响应均保留并独立复核。
- 首轮 `.local/p63-registry-6fb1b94e8d16/report.json` 保留 Github IncompleteRead：
  构建/消费当时已通过。加入有限传输重试后，另建新工程完整通过。
  成功轮 Cargo fetch 仍有两条 Schannel 自动重试警告，最终退出 0，未宣称零警告。
- 生产输入与历史收据前后身份不变。未重测全量差分/性能或其他平台；
  P4.2 新路径首启超预算的事实继续保留。离线标志不扩展为系统级断网/文件访问审计。

## 后续恢复动作

1. 当前无未完成的既定任务；按用户新指示再立项，不重跑发布或重建历史证据。
2. 如需重复消费验证，执行 `python tools/check_registry_consumer.py`；
   依赖已安装的 Rust 1.93.1 默认工具链和 `.local/p52-rustup-home` 内的 1.85.0。
   Cargo 联网在沙箱可能遇 Schannel 凭据错误，可在正常用户环境执行同一只读工具，
   不关闭 TLS 校验。每次收据独立，不覆盖旧记录。
3. 新平台、性能问题或新版本应单列范围；保留当前正式版本与用户手改文档的来源身份。
