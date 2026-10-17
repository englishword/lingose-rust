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
- shell integration 先完成管道与退出码；网页、浏览器扩展和词库维护排除。winget/scoop 为 CLI7 延期候选。

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
- [ ] CLI1.2 适配开发工具和版本相关路径假设。
  - 依赖：CLI1.1。区分仓库根与库 crate 根，适配导出/验证器、向量生成器、loader/query/differential/performance 工具、打包工具和其测试；消除旧根 `[package]`、`src/data/tests`、0.1.0 归档前缀假设。
  - 历史收据、0.1.0 专用消费者/注册表工具保留身份；新版新增独立消费入口及证据，旧布局复验从历史提交隔离检出。
  - 验收：相关 Python 回归、受保护产物只读 check、当前库验证通过；差分/性能探针独立 locked 构建，layout 探针按原互斥 feature 单独验证，不使用 all-features。新结果不覆盖旧报告。

## CLI2：库接口更名

- [ ] CLI2.1 更名阈值标注入口并更新当前调用。
  - 依赖：CLI1.2。公开 `annotate_ips_skip(&str, i64) -> Result<String>`，移除旧名称；默认入口继续使用零阈值。
  - 更新当前示例、API 文档、受控生成器及测试调用；固定 Python/P0 期望数据不改，历史发布消费者保留原字节，新版消费者单列。
  - 验收：签名检查、新名称阈值向量及旧名称不可用检查通过；覆盖负数、0、1000、5062、超过上限、含 NUL、资源加载顺序，输出与原行为一致。

## CLI3：简洁命令行

- [ ] CLI3.1 建立命令入口并实现单词查询。
  - 依赖：CLI2.1。选用并锁定符合 MSRV 的最小参数/JSON 依赖，建立 help/version 与 `word WORD [--json]`；所有字段直接调用库。
  - 验收：普通输出仅含六个指定字段；JSON 的数组/null/Unicode、未知词与参数错误正确，多个发音不按索引配对；help/version 可独立运行。
- [ ] CLI3.2 实现文本、文件、stdin 标注输入。
  - 依赖：CLI3.1。完成位置参数自动识别、互斥的显式输入、默认 stdin、UTF-8 读取和 `--skip-top`，一次完整文本交给库处理。
  - 验收：任务中的直接文本、现存文件、PowerShell/POSIX 管道示例可用；同名文本通过 --text 强制解释，显式缺失文件/目录/读取失败报错；空输入、Unicode、LF/CRLF、多行与标点输出逐字对应库，不能按行标注破坏上下文。
- [ ] CLI3.3 完成输出文件、JSON 与 shell 错误契约。
  - 依赖：CLI3.2。默认纯结果写 stdout；`-o` 写入所选纯文本/JSON 格式且不重复 stdout；JSON 键严格采用 text/annotate。
  - 验收：纯文本不追加换行，JSON 可被标准解析器读取；错误仅写 stderr，参数/用法错误 2、执行错误 1、成功/合法未知词/help/version 0。覆盖无效编码、I/O 失败、冲突输入，参数/输入/标注失败时不截断既有输出文件；不增加交互界面或 shell 插件。

## CLI4：正确性、工程与本地打包

- [ ] CLI4.1 完成 workspace 回归及性能复核。
  - 依赖：CLI3.3。执行根规范的 fmt、workspace Clippy/测试/doc 检查、受影响 Python 回归和 MSRV 1.85 实测；保存 0.2.0 新证据。
  - 验收：全量查询、全部分类有序词表、固定长文本差分及错误场景保持一致；按原预算复核 release 查询、初始化、并发、内存和 10,000/100,000 词标注（skip_top=0/1000/5062），不截断、不放宽预算，保留历史首启超预算事实。CLI 另测完整进程与 I/O，不拿库微基准代替。
- [ ] CLI4.2 完成新版用户文档和分发声明。
  - 依赖：CLI4.1。更新库/CLI README、API 契约和迁移说明，覆盖安装、全部库能力、六字段查询、文本/文件/stdin、JSON、help、错误、离线行为与官网/具体仓库链接。
  - 验收：库示例可编译，CLI 示例实际运行；两包分别核对依赖与许可，不把新增 CLI 依赖写回旧 loader/分发证据，保留作者和第三方声明。
- [ ] CLI4.3 验证库真实归档和隔离 CLI 候选。
  - 依赖：CLI4.2。检查库真实 `.crate` 清单、压缩体积、包内链接、保护数据和独立解包消费；候选验证合格后解除库 publish=false 保护并执行库 dry-run。
  - 用已解包库和最小 CLI 候选在隔离工程验证离线构建/安装，依赖准备后不能借用 checkout/相邻数据；CLI 二进制在无词库目录运行。
  - 验收：库满足原体积预算及当时注册表规则；全部库入口和两个 CLI 子命令通过。此处 CLI 属于本地候选，待库注册表可用后在 CLI6.3 完成 CLI 真实打包及注册表 dry-run，不提前标为完成。

## CLI5：GitHub Actions 与五平台资产

- [ ] CLI5.1 建立五平台 release 构建矩阵。
  - 依赖：CLI4.3。先核对/配置用户指定仓库的 Git remote、Actions 访问及运行条件，准备非发布触发验证；若外部权限阻塞，记录具体恢复动作，不把本地 YAML 检查记为 CI 通过。
  - 配置 Windows x86_64 MSVC、Linux x86_64/aarch64 GNU、macOS x86_64/aarch64；核对当时可用 runner/工具链，以 locked release 构建 CLI，开发探针不进入发布构建。
  - 验收：工作流区分只构建与发布资产，标签规则为 v0.2.0；可在正式 Release 前验证产物。每个目标留构建日志及运行方式，原生/仿真 smoke 验证 word、annotate、stdin、JSON，不能把仅交叉编译描述为运行通过。
- [ ] CLI5.2 验证安装包与下载后运行。
  - 依赖：CLI5.1。生成以下资产，包含 lingose/lingose.exe、使用说明及所需许可/来源声明，并生成 SHA-256 清单。
    - `lingose-v0.2.0-windows-x86_64.zip`
    - `lingose-v0.2.0-linux-x86_64.tar.gz`
    - `lingose-v0.2.0-linux-aarch64.tar.gz`
    - `lingose-v0.2.0-macos-x86_64.tar.gz`
    - `lingose-v0.2.0-macos-aarch64.tar.gz`
  - 验收：名称、目标架构、解包目录、可执行权限和校验和正确；脱离源码的解包运行有各目标证据。未运行目标单列，不扩大支持声明，不把 CI artifact 当作已发布 Release。

## CLI6：crates.io 与 GitHub 正式发布

- [ ] CLI6.1 核对本阶段发布条件。
  - 依赖：CLI5.2。核对已有执行授权、两包 0.2.0 名称/版本可用性、账号权限、许可处置、候选身份和具体 GitHub 仓库 remote/Release 条件；已有授权不重复询问。
  - 验收：验证记录明确哪些是用户确认、哪些是独立核对；敏感凭据不进入仓库、日志或交接。保留 0.1.0 正式包与证据，不重复上传。
- [ ] CLI6.2 发布 lingose 0.2.0 并确认注册表可用。
  - 依赖：CLI6.1。上传已核定库包，核对版本、索引、归档 SHA-256、docs.rs 和元数据链接，等待真实 CLI 注册表依赖可解析。
  - 验收：真实上传与注册表下载身份一致，单独记录上传/索引状态；失败或部分成功先核查远端，不能重复盲传。
- [ ] CLI6.3 完成 CLI 真实归档、预检并发布。
  - 依赖：CLI6.2。使用注册表的 lingose 0.2.0 完成 `cargo package -p lingose-cli`、清单/压缩体积/许可核对与隔离消费；验证合格后解除 CLI publish=false 保护，完成 `cargo publish -p lingose-cli --dry-run`，再上传。
  - 验收：归档中规范化 CLI manifest 不含开发 path/patch（源码保留 path + version）；真实归档和 dry-run 均有独立记录，上传后核对版本/索引/下载身份。前置库发布不等于 CLI 已发布。
- [ ] CLI6.4 发布 GitHub Release 资产。
  - 依赖：CLI6.3。以与候选对应的 v0.2.0 标签运行 GitHub Actions，向指定仓库 Release 发布五个资产、校验和及版本说明。
  - 验收：五个实际下载资产与候选/构建记录对应，许可及安装说明齐全；远端 Release 可访问，有实际上传证据，不用本地文件存在替代。
- [ ] CLI6.5 完成注册表安装与 Release 下载验收。
  - 依赖：CLI6.4。全新消费工程引用 `lingose = "=0.2.0"`，新 cache 执行 `cargo install lingose-cli --version 0.2.0 --locked`；依赖获取后分别离线复跑，再验 Release 下载二进制。
  - 验收：来源是正式注册表，无 checkout path/patch；完整库 API smoke、新函数及 CLI 查询/标注/JSON/文件/stdin 通过，运行无需外部词库。记录各平台实际结果、版本/归档身份、未验项，更新最终交接。

## CLI7：延期候选

- [ ] CLI7.1 评估 winget / scoop 安装渠道（延期，不阻塞 0.2.0）。
  - 依赖：CLI6.5；仅在用户后续安排该任务时执行。评估清单、签名/校验和、更新与维护成本，单列实现及验收，不因本轮规划自动提交包管理器仓库。
