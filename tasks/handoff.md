# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P6.1，核对正式发布条件（未开始）**。
- P5.3 已完成，P5 文档/工程/真实归档与本地预检全部完成；状态仅为 local_upload_ready。
- 分支 main，本轮起点 ab87d51，开始时工作区干净；聚焦提交及实施历史以 Git 为准。
- 已移除 Cargo.toml 的 publish=false，最终 include 覆盖所有必需数据/源码/许可/用户文档。
- 生产 Rust、依赖锁、源数据、派生表及历史 JSON 未改；本轮调整分发元数据/来源说明、
  增加便携摘要、打包工具/消费者与验证证据。
- **未执行真实上传、账号权限核验或 crates.io 安装验收**，这些不能由 dry-run 推断。

## 恢复所需文件与精确候选

- [todo.md](todo.md)：P6 既定阶段。
- docs/packaging.md、docs/package-verification.json：实际归档、输入、命令/日志、隔离消费、
  dry-run、工具方法及保护文件身份；完整原始记录另列在 JSON。
- **候选归档**：.local/p53-readable/lingose-0.1.0.crate
  - 4,052,577 字节；41 文件，21 个本地文档链接。
  - SHA-256 db227b4d53065bca47bf20bc5ea6d4987ff578fd9d3b0f8d98b5c6cda5b7d3ad。
- **候选源码快照**：.local/p53-readable/source。
  - 与当前分发输入逐字节一致，无 .git，不生成 .cargo_vcs_info.json。
  - 来源由起点提交和每个输入 SHA-256 明确绑定，不伪造干净 VCS 身份。
  - Cargo dry-run 的实际新归档在 .local/p53-readable/package-target/package/tmp-crate/
    lingose-0.1.0.crate，已核对与候选完全相同，不能误检查先前 cargo package 的旧输出。
- **实际成功 dry-run 原始记录**：.local/p53-readable-verified/report.json。
  便于正常用户审阅的原始 report/log 副本在 .local/p53-readable/evidence。
- 初始 .local/p53-package-1pq09dd9/report.json 保留 offline dry-run 失败，
  此前打包与两套消费者已通过；独立包内测试见 .local/p53-package-tests/report.json。
- tools/check_package.py：新建快照打包、清单/tar/主机路径/链接/身份检查、空 cache+vendor
  消费者与 dry-run；每次写新 .local 记录，不真实上传。
- tools/package_consumer.rs：18 入口字面量断言；运行时不读外部数据。
- tools/prepare_package_sources.py、docs/distribution-provenance.json：白名单摘取历史 Unicode
  表/许可/解释器/生成器/依赖身份；--check 可核对，不改历史报告。
- SOURCES.md、README.md、docs/rust-api.md：最终分发文档；原署名/许可/资料缺口保留。
  三份含主机路径的 query-case/annotation-unicode/loader-verification JSON 不随 crate 分发；
  原记录保留不变，通过便携摘要保留来源身份。

## 本轮验证与范围

- 真实 cargo package --list 和 cargo package（带离线/锁定）通过；逐文件核对归档与快照，
  Rust include_* 目标、许可/Unicode 表/资源、21 个本地链接完整；没有维护库、缓存、
  Python/开发工具或本机绝对路径。压缩归档小于固定 5,000,000 字节预算。
- 2026-10-16 已复核 Cargo 官方发布说明的 10MB 规则；汇总记载 URL 和保守数值检查。
- 从真实归档在系统临时目录解包，准备 vendored 依赖后使用空 Cargo home；Cargo metadata
  所有源码均局限该目录，registry cache 不存在；1.93.1/1.85.0 分别 offline locked
  release 构建，二进制从只有可执行文件的目录运行，18 入口内容断言与输出均一致。
- 包内 80 库测试、5 文档测试及文档构建通过，1 个既有加载器手动探针忽略。
  75 Python 测试（含 5 项新拒绝性归档保护）、根 fmt/Clippy -D warnings 通过。
  包内 rustup 的路径规范化环境提示如实保留，未宣称零警告。
- 真实 cargo publish --dry-run --locked --all-features 在正常用户环境通过，
  Cargo 明确 aborting upload due to dry run；生成的 tmp-crate 与候选摘要相同。
- offline dry-run 因注册表 HTTP 读取失败，联网沙箱尝试遇 Schannel 凭据错误；
  正常用户重试需可读快照（Python mkdtemp 的初始目录仅创建者可读）。
  同字节快照复制到继承权限的隔离目录后成功，未关闭 TLS 校验或使用替代注册表。
- 当前平台仅 Windows x86_64 MSVC；不代表其他平台或未来依赖解析。未重测性能/
  全量差分，也未重写 P4/P5.1/P5.2 原始 JSON。
- 独立只读复核已验证实际归档闭包、内容及消费者覆盖；最终汇总审阅以本轮记录为准。

## 必须保留的边界

- 官网 https://lingose.com/ 和用户指定 https://github.com/englishword 保持，不编造仓库 URL。
- Frequency List 固定参考缺单独许可文本/派生分发条件记录，部分外部分类词表缺逐标签
  来源/许可资料。保留声明不等于独立核实授权，不能以项目 CC BY 4.0 推定第三方授权；
  P6.1 要核对实际处置状态。
- 所有相邻参考 checkout、安装库和人工审核资料只读；不修改 source identity。
- P4.2 历史仅在固定预热条件下达标；新路径首启 534.24 ms 的超限事实保留，不重新
  捕获/覆盖旧报告来迎合当前输入。预算未放宽。
- 本地归档/离线消费/dry-run/真实上传/注册表消费分别记载；不因 publish=false 已移除
  就把正式发布或账号权限标为通过。令牌不写入日志、仓库或交接记录。

## 下一步精确动作

1. 核对 Git、本交接与 todo，恢复 P6.1；先确定该阶段执行授权、crates.io 账号/名称、
   0.1.0 可发布状态与来源资料缺口处置。已有明确授权不重复询问。
2. 重新核对候选归档、当前分发输入和完整 SHA。若继续使用已验证快照，可对该
   manifest 执行后续正式发布；先准备授权凭据并保持令牌不入日志。
3. 不要把从 Git checkout 直接重新生成的含 VCS 信息归档当作上述同一文件；如果换用
   新归档或修改任一分发输入，建立新候选/身份/相应验证，不覆盖本轮历史收据。
4. P6.1 条件确实满足后才进入 P6.2 真实上传，核对实际上传和索引可用证据；中断时先查
   远端状态，不盲目重传已存在版本。
5. P6.3 再从 crates.io 在独立工程安装正式 0.1.0，准备依赖后离线重跑全部公共 API，
   核对官网/GitHub 与文档可访问性；验证后更新最终交接并聚焦提交。
