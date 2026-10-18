# Lingose Rust 0.2.0 workspace 与 CLI 执行计划

需求：[TASK_CLI.md](../TASK_CLI.md)。核心行为依据：[TASK.md](../TASK.md)。开发约束：[AGENTS.md](../AGENTS.md)。恢复点：[handoff.md](handoff.md)。

目标：将已发布的 `lingose 0.1.0` 迁移为双 crate workspace，交付 `lingose 0.2.0` 与可通过 `cargo install lingose-cli` 安装的 `lingose-cli 0.2.0`，二进制名为 `lingose`；提供简洁离线查询/标注、crates.io 包和五平台 GitHub Releases。

原 [0.1.0 执行计划](todo.md)已完成并作为历史保留。本清单按编号顺序推进，每次只完成一个小任务；每项验证后更新状态、交接并聚焦提交。只勾选实际完成的任务，不将候选构建、dry-run、真实发布或远端消费混为一项证据。

## 已确认的接口与边界

- 两个包统一 `0.2.0`，Release 标签统一 `v0.2.0`；沿用 edition 2024、MSRV 1.85 和原 Python/Unicode/数据基线。
- `annotate_ips_skip(text, skip_top)` 取代 `annotate_ips_with_skip_top`，旧名称移除，不保留别名；`annotate_ips(text)` 和其余库能力保留。
- CLI 只有 `annotate`、`word` 两个业务子命令及 help/version。位置参数是现有普通文件时读取文件，否则按文字；`--input`、`--text` 可显式指定，与位置参数互斥；省略输入读取 stdin。
- `annotate` 支持 `--skip-top`（默认 0）、`-o`、`--json`。UTF-8 输入，纯文本结果保留原换行；输出和错误分流，执行错误不伪装成未知词。
- 标注 JSON 只有 `text`、`annotate`；查询 JSON 只有 `word`、`ipa`、`ips`、`ism`、`ipsm`、`root_lemma`。三种发音为独立数组，可空字段保留 null，CLI 不带释义、词性和分类等辅助字段。
- 核心算法和随包数据仅由库维护，CLI 调用库。首次运行无需下载词库，运行不依赖 Python、Node、Cargo cache 或相邻 checkout。
- shell integration 先完成管道与退出码；网页、浏览器扩展和词库维护排除。用户已安排 CLI7 的 winget/scoop/choco/homebrew 渠道工作，社区上架不阻塞既有 0.2.0 发布。

## CLI0：文档准备

- [x] CLI0.1 更新规范、建立新清单并切换交接恢复点。
  - 产物：更新根 AGENTS、本清单和交接记录；原样保留新需求，原计划与历史证据不改。
  - 验收：三项用户选择和全部新需求有对应任务；UTF-8、相对链接、唯一编号、状态、文档差异及空白检查通过；下一项明确为 CLI1.1。本轮仅完成文档准备。

## CLI1：workspace 与开发工具迁移

- [x] CLI1.1 建立双 crate workspace 并迁移自足库包。
  - 依赖：CLI0.1。根改为 virtual workspace，成员为 `crates/lingose`、`crates/lingose-cli`，共用根锁文件；两包版本 0.2.0，CLI 二进制名为 lingose，脚手架不冒充已实现业务。
  - 将库源码、examples、Rust 集成测试、必要数据和包内文档/许可证迁入自足包；开发期 Python 测试与审计资料保留仓库级位置。先记录身份再移动，适配 include、README 链接、Cargo include 和 `.gitattributes`。
  - 将三个开发探针显式隔离并更新库 path 依赖，保留独立锁文件/profile；CLI 依赖库同时声明本地 path 与版本约束。
  - 验收：metadata 仅显示两个正式成员；库最小构建及现有 Rust 测试通过，CLI 脚手架可构建；数据、固定向量期望值、Unicode 表和许可证内容身份不变。必要的 README/声明路径调整单独记录，不静默改写受保护来源原文。
  - 结果与边界：[迁移记录](../docs/workspace-migration.md)及[独立证据](../docs/workspace-migration-verification.json)。38 文件原字节迁移，两个包均 0.2.0；现有 102 Rust / 5 文档测试、fmt、Clippy、文档、Rust 1.85 编译、探针隔离和仓库外离线示例通过。两包保持 publish=false，CLI 是退出 1 的脚手架，工具适配与接口更名留后续阶段。
- [x] CLI1.2 适配开发工具和版本相关路径假设。
  - 依赖：CLI1.1。区分仓库根与库 crate 根，适配导出/验证器、向量生成器、loader/query/differential/performance 工具、打包工具和其测试；消除旧根 `[package]`、`src/data/tests`、0.1.0 归档前缀假设。
  - 历史收据、0.1.0 专用消费者/注册表工具保留身份；新版新增独立消费入口及证据，旧布局复验从历史提交隔离检出。
  - 验收：相关 Python 回归、受保护产物只读 check、当前库验证通过；差分/性能探针独立 locked 构建，layout 探针按原互斥 feature 单独验证，不使用 all-features。新结果不覆盖旧报告。
  - 结果与边界：[工具迁移说明](../docs/workspace-tools.md)及[独立证据](../docs/workspace-tools-verification.json)。90 Python、102 Rust、5 文档测试通过；基线/全部生成器只读检查、50,335 条完整数据核验、隔离库回归、881 项差分 smoke、workspace 检查及独立探针构建通过。101 受保护文件摘要不变；新版包入口仅做清单检查，完整新版差分/性能与真实归档留 CLI4。

## CLI2：库接口更名

- [x] CLI2.1 更名阈值标注入口并更新当前调用。
  - 依赖：CLI1.2。公开 `annotate_ips_skip(&str, i64) -> Result<String>`，移除旧名称；默认入口继续使用零阈值。
  - 更新当前示例、API 文档、受控生成器及测试调用；固定 Python/P0 期望数据不改，历史发布消费者保留原字节，新版消费者单列。
  - 验收：签名检查、新名称阈值向量及旧名称不可用检查通过；覆盖负数、0、1000、5062、超过上限、含 NUL、资源加载顺序，输出与原行为一致。
  - 结果与边界：[更名说明](../docs/annotation-api-rename.md)及[独立证据](../docs/annotation-api-rename-verification.json)。新签名/18 入口消费者通过，旧名称明确报 E0425；90 Python、102 Rust、6 文档测试、3 个生成器只读 check、隔离 release 回归及 881 项差分 smoke 通过。固定预期值不变，138 个范围外原文件摘要不变；未实现 CLI3 或进行发布。

## CLI3：简洁命令行

- [x] CLI3.1 建立命令入口并实现单词查询。
  - 依赖：CLI2.1。选用并锁定符合 MSRV 的最小参数/JSON 依赖，建立 help/version 与 `word WORD [--json]`；所有字段直接调用库。
  - 验收：普通输出仅含六个指定字段；JSON 的数组/null/Unicode、未知词与参数错误正确，多个发音不按索引配对；help/version 可独立运行。
  - 结果与边界：[命令查询说明](../docs/cli-word.md)及[独立证据](../docs/cli-word-verification.json)。锁定最小功能的 Clap/serde_json，11 项 CLI 测试在 Rust 1.93.1 和 1.85.0 通过；workspace 113 项 Rust / 6 项文档测试、fmt、Clippy、doc 及 15 项工具 Python 回归通过。16 词/80 个 P0 字段零差异；真实不等长数组和明确标注的合成多发音分别验证，150 个范围外原文件不变。CLI 标注输入留 CLI3.2，未打包或发布。
- [x] CLI3.2 实现文本、文件、stdin 标注输入。
  - 依赖：CLI3.1。完成位置参数自动识别、互斥的显式输入、默认 stdin、UTF-8 读取和 `--skip-top`，一次完整文本交给库处理。
  - 验收：任务中的直接文本、现存文件、PowerShell/POSIX 管道示例可用；同名文本通过 --text 强制解释，显式缺失文件/目录/读取失败报错；空输入、Unicode、LF/CRLF、多行与标点输出逐字对应库，不能按行标注破坏上下文。
  - 结果与边界：[标注输入说明](../docs/cli-annotation-input.md)及[独立证据](../docs/cli-annotation-input-verification.json)。三种显式输入互斥，默认 stdin，完整 UTF-8 文本一次委托库；20 项 CLI 测试在 Rust 1.93.1/1.85.0 通过，workspace 122 项 Rust / 6 项文档测试、fmt、Clippy、doc 和 15 项工具 Python 回归通过。52 项可用 i64 表示的 P0 标注零差异，超大整数样例单列；6 个 PowerShell/Git Bash 管道示例通过，156 个范围外原文件不变。Unix 专用项未在本机运行，`-o`/标注 JSON 留 CLI3.3。
- [x] CLI3.3 完成输出文件、JSON 与 shell 错误契约。
  - 依赖：CLI3.2。默认纯结果写 stdout；`-o` 写入所选纯文本/JSON 格式且不重复 stdout；JSON 键严格采用 text/annotate。
  - 验收：纯文本不追加换行，JSON 可被标准解析器读取；错误仅写 stderr，参数/用法错误 2、执行错误 1、成功/合法未知词/help/version 0。覆盖无效编码、I/O 失败、冲突输入，参数/输入/标注失败时不截断既有输出文件；不增加交互界面或 shell 插件。
  - 结果与边界：[标注输出说明](../docs/cli-annotation-output.md)及[新证据](../docs/cli-annotation-output-verification.json)。接续未提交草稿并修复测试类型推断/关闭管道竞态；两字段字符串 JSON、所选格式文件输出及同路径输入输出已完成。Windows Rust 1.93.1 的 workspace 131 项 Rust / 6 项文档测试、fmt、Clippy、doc 通过；Rust 1.85.0 的 29 项 CLI 测试及 CLI Clippy 通过。4 项 PowerShell/Git Bash JSON 解析/文件输出检查通过，158 个范围外原文件不变。前置失败不创建/截断输出，实际写入失败不保证回滚；Unix 专用项未运行，完整新版差分/性能及 workspace MSRV 留 CLI4.1，两包继续禁止发布。

## CLI4：正确性、工程与本地打包

- [x] CLI4.1 完成 workspace 回归及性能复核。
  - 依赖：CLI3.3。执行根规范的 fmt、workspace Clippy/测试/doc 检查、受影响 Python 回归和 MSRV 1.85 实测；保存 0.2.0 新证据。
  - 验收：全量查询、全部分类有序词表、固定长文本差分及错误场景保持一致；按原预算复核 release 查询、初始化、并发、内存和 10,000/100,000 词标注（skip_top=0/1000/5062），不截断、不放宽预算，保留历史首启超预算事实。CLI 另测完整进程与 I/O，不拿库微基准代替。
  - 结果与边界：[新版验收说明](../docs/cli-workspace-acceptance.md)及[完整汇总](../docs/cli-workspace-acceptance-verification.json)。Rust 1.93.1/1.85.0 完整 workspace 各 131 项 Rust、6 项文档测试及 Clippy/doc 通过，当前 fmt、90 项 Python、基线/P0/导出/八个生成器及独立数据验证通过。新全量差分 1,862,690 个完整结果零差异，七个隔离 release 库测试二进制通过。原运行时间/资源/内存预算全部通过，100,000 词三阈值标注中位数 132.99/180.37/200.51 ms；新路径首启 675.43 ms 仍超 300 ms，单列保留，不混入预热统计。CLI 26 场景/182 个正式进程全文对照通过；164 个范围外原文件不变。Windows 之外未运行，真实归档/dry-run/发布未执行，后续为 CLI4.2。
- [x] CLI4.2 完成新版用户文档和分发声明。
  - 依赖：CLI4.1。更新库/CLI README、API 契约和迁移说明，覆盖安装、全部库能力、六字段查询、文本/文件/stdin、JSON、help、错误、离线行为与官网/具体仓库链接。
  - 验收：库示例可编译，CLI 示例实际运行；两包分别核对依赖与许可，不把新增 CLI 依赖写回旧 loader/分发证据，保留作者和第三方声明。
  - 结果与边界：[用户文档说明](../docs/cli-user-documentation.md)及[新版收据](../docs/cli-user-documentation-verification.json)。根/两包 README、当前 API 契约及两包来源声明已更新；安装命令明确为发布后用法。Rust 1.93.1/1.85.0 各 7 项文档测试、额外 2 个 Rust 块、2 个库 example、18 条 CLI 示例及 5 个 shell 场景通过；标注逐字对照直接库调用。五目标依赖图离线核对，库 9/10、CLI 18/19 个外部依赖的版本/许可匹配；165 个范围外原文件不变。PowerShell 实际 stdin BOM 和宿主换行边界已留证；没有打包、dry-run、上传或多平台运行，两包仍 publish=false。下一项为 CLI4.3。
- [x] CLI4.3 验证库真实归档和隔离 CLI 候选。
  - 依赖：CLI4.2。检查库真实 `.crate` 清单、压缩体积、包内链接、保护数据和独立解包消费；候选验证合格后解除库 publish=false 保护并执行库 dry-run。
  - 用已解包库和最小 CLI 候选在隔离工程验证离线构建/安装，依赖准备后不能借用 checkout/相邻数据；CLI 二进制在无词库目录运行。
  - 验收：库满足原体积预算及当时注册表规则；全部库入口和两个 CLI 子命令通过。此处 CLI 属于本地候选，待库注册表可用后在 CLI6.3 完成 CLI 真实打包及注册表 dry-run，不提前标为完成。
  - 结果与边界：[打包说明](../docs/cli-packaging.md)及[独立收据](../docs/cli-package-verification.json)。真实库归档 41 文件、4,053,096 字节，低于 5,000,000 字节预算；19 个包内链接、3 个 Rust include、全部载荷/库锁闭包/Unicode 与许可身份核对通过。Rust 1.93.1/1.85.0 分别从真实解包库离线构建 18 入口消费者并安装最小 CLI 候选，各通过 25 个 CLI 场景，源码/词库目录移开后仍可运行。最终库 dry-run 成功且临时归档摘要一致；沙箱 TLS 失败日志保留。92 项 Python、workspace 131 项 Rust / 7 项文档测试、fmt/Clippy/doc 及包内 80 项库 / 7 项文档测试通过。仅解除库发布保护，CLI 继续 publish=false；未上传、未做 CLI 注册表打包或多平台运行。下一项为 CLI5.1。

## CLI5：GitHub Actions 与五平台资产

- [x] CLI5.1 建立五平台 release 构建矩阵。
  - 依赖：CLI4.3。先核对/配置用户指定仓库的 Git remote、Actions 访问及运行条件，准备非发布触发验证；若外部权限阻塞，记录具体恢复动作，不把本地 YAML 检查记为 CI 通过。
  - 配置 Windows x86_64 MSVC、Linux x86_64/aarch64 GNU、macOS x86_64/aarch64；核对当时可用 runner/工具链，以 locked release 构建 CLI，开发探针不进入发布构建。
  - 验收：工作流区分只构建与发布资产，标签规则为 v0.2.0；可在正式 Release 前验证产物。每个目标留构建日志及运行方式，原生/仿真 smoke 验证 word、annotate、stdin、JSON，不能把仅交叉编译描述为运行通过。
  - 结果与边界：[矩阵说明](../docs/cli-release-ci.md)、[完整收据](../docs/cli-release-ci-verification.json)及[实际成功运行](https://github.com/englishword/lingose-rust/actions/runs/39097471918)。指定 private 仓库 origin/admin/push/Actions 已核验，用户完成 workflow scope 授权并成功推送；构建提交为 `4e00367`。五目标 locked release 构建、共 147 项 CLI 测试（Windows/macOS 各 29、Linux 各 30）、60 项原生 smoke 及五份 CI artifact 上传通过；独立下载核对服务端 zip digest、全部报告/日志/binary 摘要及 57 项完全相同的输入。修复 CI 暴露的 NUL 设备名 fixture、macOS 非 UTF-8 路径测试/错误分类和 Windows example CRLF，保留首次失败与第二次输入差异证据。Windows workspace 131 项 Rust / 7 项文档测试、fmt/Clippy/doc、MSRV 1.85 的 29 项 CLI 测试通过。没有创建 tag/Release 或上传 crates.io；正式带许可安装包及下载后运行留 CLI5.2，运行环境支持声明限于实际 runner。
- [x] CLI5.2 验证安装包与下载后运行。
  - 依赖：CLI5.1。生成以下资产，包含 lingose/lingose.exe、使用说明及所需许可/来源声明，并生成 SHA-256 清单。
    - `lingose-v0.2.0-windows-x86_64.zip`
    - `lingose-v0.2.0-linux-x86_64.tar.gz`
    - `lingose-v0.2.0-linux-aarch64.tar.gz`
    - `lingose-v0.2.0-macos-x86_64.tar.gz`
    - `lingose-v0.2.0-macos-aarch64.tar.gz`
  - 验收：名称、目标架构、解包目录、可执行权限和校验和正确；脱离源码的解包运行有各目标证据。未运行目标单列，不扩大支持声明，不把 CI artifact 当作已发布 Release。
  - 结果与边界：[安装包说明](../docs/cli-binary-assets.md)、[完整收据](../docs/cli-binary-assets-verification.json)及[实际运行](https://github.com/englishword/lingose-rust/actions/runs/39101457134)。`d16c537` 上的五 build/package、五独立 downloaded-native 和汇总共 11 job 全通过；147 次 CLI 测试、35 次 archive guard、60 次构建 smoke、80 次实际下载后 smoke 通过。17 份 service zip 摘要、五安装包/SHA256SUMS、闭合载荷、架构/权限/许可及 57 构建/53 打包输入独立核验一致；本机下载 Windows 包另有 16 项无源码 smoke。就绪六文件在 `.local/cli52-dist-d16c537/`，原始证据在 `.local/cli52-ci-final/`；每包 46/48 文件，压缩约 4.36–4.48 MB。固定 44 项许可/来源原文，保留 Windows VCRUNTIME140 前提、Frequency List/分类许可缺口及 private/14 天 CI 访问边界。本地 99 项 Python、fmt/actionlint/语法/空白检查通过；无 Rust/数据/锁文件变化，未创建 tag/Release 或上传 crates.io。下一项为 CLI6.1。

## CLI6：crates.io 与 GitHub 正式发布

- [x] CLI6.1 核对本阶段发布条件。
  - 依赖：CLI5.2。核对已有执行授权、两包 0.2.0 名称/版本可用性、账号权限、许可处置、候选身份和具体 GitHub 仓库 remote/Release 条件；已有授权不重复询问。
  - 验收：验证记录明确哪些是用户确认、哪些是独立核对；敏感凭据不进入仓库、日志或交接。保留 0.1.0 正式包与证据，不重复上传。
  - 结果与边界：[发布条件核对](../docs/cli-publication-preflight.md)及[新收据](../docs/cli-publication-preflight-verification.json)。API/index 确认库 0.2.0 和 CLI 尚未发布，库 owner 为 Prefee；沿用已有账号/许可用户确认，四项数据与来源 blob 和确认时完全相同，独立许可资料缺口继续披露。新库包 41 文件/4,053,096 字节及 SHA 与 CLI4.3 完全一致，真实打包、7 文档测试、联网 dry-run 和五归档身份复核通过。GitHub admin/repo/workflow 权限实时核对；仍 private、无 v0.2.0/Release，现工作流只上传 CI artifact。库可进入 CLI6.2；CLI 新名称 token scope 未独立读出，公开下载可见性和 Release 上传路径留对应阶段处理。没有上传、改可见性或创建标签/Release；本轮止于 CLI6.1。
- [x] CLI6.2 发布 lingose 0.2.0 并确认注册表可用。
  - 依赖：CLI6.1。上传已核定库包，核对版本、索引、归档 SHA-256、docs.rs 和元数据链接，等待真实 CLI 注册表依赖可解析。
  - 验收：真实上传与注册表下载身份一致，单独记录上传/索引状态；失败或部分成功先核查远端，不能重复盲传。
  - 结果与边界：[库正式发布](../docs/cli-library-publication.md)及[新收据](../docs/cli-library-publication-verification.json)。注册表于 2026-10-18 07:43:13.810692 UTC 接受 0.2.0，publisher/owner Prefee、未 yank；4,053,096 字节/41 文件，候选、实际上传、API/index/匿名下载 SHA 均为 91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5。Cargo 上传后 Schannel 连接中断退出 101，立即核对远端确认已接受，未重试（正式上传仅 1 次）；错误日志原样保留。docs.rs 0.2.0/新函数及 build 4898279 成功；checkout 外空 cache 的真实 CLI 注册表依赖在线/离线 metadata 通过，未冒充构建/安装/运行或 CLI 发布。0.1.0 和保护数据不变；本轮止于 CLI6.2，下一项 CLI6.3。
- [x] CLI6.3 完成 CLI 真实归档、预检并发布。
  - 依赖：CLI6.2。使用注册表的 lingose 0.2.0 完成 `cargo package -p lingose-cli`、清单/压缩体积/许可核对与隔离消费；验证合格后解除 CLI publish=false 保护，完成 `cargo publish -p lingose-cli --dry-run`，再上传。
  - 验收：归档中规范化 CLI manifest 不含开发 path/patch（源码保留 path + version）；真实归档和 dry-run 均有独立记录，上传后核对版本/索引/下载身份。前置库发布不等于 CLI 已发布。
  - 结果与边界：[CLI 正式发布](../docs/cli-cli-publication.md)及[完整收据](../docs/cli-cli-publication-verification.json)。受保护候选通过后移除 CLI publish=false 并重验；最终包 7 文件/16,498 字节，SHA 3f2e31e77ac7bdcedecb90871597d9821f60119f437be9a2cd7c523faa894490。根锁仅映射库注册表来源及正式 SHA，其余身份/依赖边不变；当前/1.85 两工具链各 25 项隔离离线安装后运行及18项Windows启用依赖许可通过，两次联网dry-run同字节。首次正式上传被403权限拒绝（Cargo101），核查API/index404后等待用户更新凭据；用户确认cargo login后以独立标记进行第二次尝试，Cargo0，注册表2026-10-18 08:36:22.922509 UTC接受，publisher/owner Prefee、未yank。API/index/匿名下载与候选全字节一致，README/元数据通过；两次上传仅一次接受，原拒绝记录保留、无盲重试。29项CLI测试/fmt通过，库/数据/根锁未变；本轮止于CLI6.3，下一项CLI6.4。
- [x] CLI6.4 发布 GitHub Release 资产。
  - 依赖：CLI6.3。以与候选对应的 v0.2.0 标签运行 GitHub Actions，向指定仓库 Release 发布五个资产、校验和及版本说明。
  - 验收：五个实际下载资产与候选/构建记录对应，许可及安装说明齐全；远端 Release 可访问，有实际上传证据，不用本地文件存在替代。
  - 用户后续选择：**目前以 private 发布 Release**。保持指定仓库 private，以认证且有权限的访问验收；不要求或声明匿名公开下载。发布条件/说明调整后建立新候选提交，正式 tag 重新构建并保存独立发布收据。
  - 结果与边界：[Release 正式记录](../docs/cli-github-release.md)及[独立正式收据](../docs/cli-github-release-publication-verification.json)。private Release `416347193` 于2026-10-18 09:16:55 UTC正式发布；v0.2.0解引用cf11a60，未改可见性/标签。run39114174841的十一项候选job全成功，147次CLI测试、35/35次归档/发布保护、60/80次构建/下载原生smoke通过。第一次创建草稿失败，核实远端为空后先同步默认分支workflow，再只重跑发布job；attempt2成功，原失败/19份service artifacts均保留。五包及SHA256SUMS的服务端digest、实际认证下载、全部载荷/二进制/许可/说明与最终CI候选一致；不冒充匿名公开访问或CLI6.5运行验收。旧候选收据不覆盖、已发布crate不重传；下一项CLI6.5。
- [x] CLI6.5 完成注册表安装与 Release 下载验收。
  - 依赖：CLI6.4。全新消费工程引用 `lingose = "=0.2.0"`，新 cache 执行 `cargo install lingose-cli --version 0.2.0 --locked`；依赖获取后分别离线复跑，再验 Release 下载二进制。
  - 验收：来源是正式注册表，无 checkout path/patch；完整库 API smoke、新函数及 CLI 查询/标注/JSON/文件/stdin 通过，运行无需外部词库。记录各平台实际结果、版本/归档身份、未验项，更新最终交接。
  - 结果与边界：[最终验收说明](../docs/cli-final-acceptance.md)及[独立收据](../docs/cli-final-acceptance-verification.json)。Windows x86_64/Rust 1.93.1，仓库外两个全新 Cargo cache 分别完成精确库依赖消费与正式名称 CLI 安装，在线/全新 target 离线 locked 构建安装通过；两包归档 SHA、全部解包字节、metadata/锁文件/安装来源通过。移开构建工程/cache/target/安装根后，两份18入口库消费者及三份CLI各25项、共75项运行通过，包含最终Windows Release；91条命令预期退出码、182日志摘要独立通过。刷新private Release/标签/六资产后复用并重验正式认证下载，身份未变；其余平台仅列既有tag原生候选CI及最终字节对应，不外推本机运行。首次离线metadata缺libc的失败原样保留，修正依赖准备和根包检查后使用全新cache重验；248个原有tracked文件在验收时未变，无源码/数据/锁/旧收据变化，未重传/移tag/改可见性。CLI6完成，CLI7仅待用户后续安排。

## CLI7：包管理器渠道

用户于 2026-10-18 安排继续，并指定 winget → scoop → choco → homebrew 顺序；仓库现已 public。沿用 CLI6 的正式资产，不重新发布 crate、移动 tag 或覆盖历史收据。社区仓库提交/审核与本地清单、安装测试分别记录。

- [x] CLI7.1 WinGet：核对公开下载、名称与当前规范，准备三文件 portable ZIP 清单，验证 schema 和实际安装条件。
  - 三文件 schema/客户端 validate、公开正式 ZIP 安装、8 项原生功能测试、通知保留及卸载通过；社区 PR/索引未提交。通过的 Windows job 属于 run `39126125352`。
- [x] CLI7.2 Scoop：核对 Main/Extras 门槛，准备本仓库自有 bucket，验证架构、摘要、解压目录、shim 和更新规则。
  - 公开自有 bucket 精确提交、安装/shim 8 项、通知保留、官方 checkver/autoupdate 当前版本 hash/URL/extract_dir、卸载/重装通过；缺运行库 guard 的本地正/负检查通过。未进入 Main/Extras。
- [x] CLI7.3 Chocolatey：准备下载型包、运行库依赖及源码链接，执行真实 pack 与安装/卸载验证；不把 nupkg 生成当作社区上架。
  - 本地及 CI 真实 pack、依赖解析/本地 feed 安装、shim 8 项、通知保留、同版本强制重装及卸载通过；下载型 nupkg 无内嵌 exe，尚未上传社区。
- [x] CLI7.4 Homebrew：核对 core 门槛，准备本仓库自有 tap，验证实际目标上的安装、功能与卸载；披露未验平台。
  - 公开自有 tap 在 macOS 15.7.9 Intel/Apple Silicon 原生安装、formula test、各 8 项命令检查、通知保留、重装/卸载通过；未提交 core，初版不提供 Linux Homebrew。
- [x] CLI7.5 汇总渠道状态与后续社区提交步骤，更新当前 README/交接；保留审核、签名、公证、来源许可与平台限制。
  - [渠道说明](../docs/cli-package-channels.md)、[验收收据](../docs/cli-package-channels-verification.json)。run `39126125352` 三 job 全通过，五实例/40 项；三个服务 artifact ZIP 实际下载 SHA/大小通过，六次先前失败及原始日志单列。247 个范围外原文件不变，旧 crate/Release/tag/收据未改；Scoop bucket/macOS tap 已公开可用，WinGet 社区 PR 与 Chocolatey 社区上传/审核尚未执行。CLI7 的渠道准备/原生验收完成，社区上架需后续安排。
