# Lingose Rust Agent Instructions

## Standard Workflow

For existing projects, **resume from project state before re-planning**.

1. For non-trivial projects, use the active task plan and `tasks/handoff.md` as the cross-session resume state; create them if missing during initial planning. The current plan is `tasks/todo_CLI.md` for the 0.2.0 workspace/CLI work; `tasks/todo.md` records the completed 0.1.0 plan.
2. At session start, reconcile the current repository state first: inspect `git status`, the active branch, recent relevant commits, `tasks/handoff.md`, and the current item in the active task plan.
3. Treat the working tree and Git history as implementation truth, the active task plan as the plan, and `tasks/handoff.md` as a concise resume pointer. If they disagree, determine the real state before continuing.
4. Resume the task identified by `tasks/handoff.md`; otherwise use the first unfinished, unblocked task in the active task plan. Do not recreate or re-approve a valid existing plan.
5. Read only enough code and documentation to safely execute the current task. Expand context on demand; do not scan the entire repository by default.
6. Work on one small, verifiable task at a time. Keep changes focused and avoid unrelated refactoring or unnecessary complexity.
7. Prefer subagents when independent, repetitive, parallelizable, read-heavy, or noisy work benefits from context isolation; return concise results to the main thread. Keep short or tightly dependent work in the main thread, and avoid parallel write-heavy agents when conflicts are likely.
8. Run the smallest relevant verification first. Continue fixing issues caused by the current task until it is verified or genuinely blocked; record newly discovered future work in the active task plan.
9. After a task is completed and verified, update its plan/state and create a focused Git commit unless the user says not to. Never include unrelated pre-existing changes or amend existing commits.
10. Give concise progress updates during execution, but provide comprehensive final summary.
11. Before ending substantial or incomplete work, overwrite `tasks/handoff.md` with the current task/status, relevant files, important decisions or blockers, verification status, and the exact next action.
12. Use Git history as the primary implementation history. Keep the active task plan focused on remaining work and `tasks/handoff.md` focused on resumption; preserve completed version plans and avoid duplicating detailed history between these files.
13. Create nested `AGENTS.md` files only when a subtree has materially different commands, constraints, conventions, or workflows. Do not duplicate parent instructions.

## 项目目标与范围

- 当前需求依据为 [TASK_CLI.md](TASK_CLI.md)，原 [TASK.md](TASK.md) 继续约束核心库；新任务明确变更的部分以新需求及用户已确认选择为准。本文件约束开发流程，[当前任务清单](tasks/todo_CLI.md)安排实施顺序，[交接记录](tasks/handoff.md)指向当前恢复点。
- `lingose 0.1.0` 已发布，原 [P0–P6 计划](tasks/todo.md)已完成；本阶段交付 `lingose 0.2.0` 库和 `lingose-cli 0.2.0`。不得重复上传 `0.1.0` 或把旧版验收作为新版已通过的证据。
- 调整为根 virtual workspace，正式成员为 `crates/lingose` 与 `crates/lingose-cli`，共用根 `Cargo.lock`。开发探针显式隔离，保留其独立锁文件与 profile，不加入交付成员。
- `lingose` 负责数据结构、离线数据、查询及标注算法；`lingose-cli` 负责参数、stdin/stdout、文件、JSON、帮助和错误，二进制名称为 `lingose`。CLI 通过库调用实现业务，不复制算法或词库。
- 实现 `../lingose-python/README.md` 中的公共函数，排除 `lookup()`。不能为了省去完整查询 API 而仅交付网页标注所需的 IPS 数据。
- 用户已选择随包提供全部必要数据；安装后无需额外下载、用户配置、Python、Node 或相邻源码仓库即可离线查询和标注。构建与首次调用均不得隐式联网获取词库。
- TASK 中“开发 npm lingose 时”的性能要求适用于本 Rust crate。TypeScript 包是参考实现，不是本项目的交付物。
- 本阶段 CLI 以简洁为主；网页 DOM 操作、浏览器扩展和新词库维护系统继续排除。winget、scoop 留在任务清单最后，属于延期候选，不阻塞 `0.2.0`。

## 公共接口与行为基线

| 接口 | 必须保留的行为 |
| --- | --- |
| `ipa` / `IPA` | 返回已选择且可用的 IPA 列表；无可用值为空列表。 |
| `ips` / `IPS` | 返回已选择且可用的 IPS 列表。 |
| `ism` / `ISM` | 返回采用的构词划分；不可用为空值。 |
| `ipsm` / `IPSM` | 返回依赖仍有效的 IPSM 列表。 |
| `root_lemma` | 返回已保存的词族值，不运行新的通用词形还原。 |
| `meaning` | 返回原始释义；默认英语，支持精确的 `en`、`zh`。 |
| `kind` | 返回分类成员关系；默认分类为 `CET4`。 |
| `kind_list` | 返回指定分类的完整有序词表；默认分类为 `CET4`。 |
| `labels` | 按基线配置顺序返回注册的布尔分类标签。 |
| `annotate_ips` | 对纯文本标注 IPS；默认 `skip_top=0`，保留大小写、空白和标点。 |
| `annotate_ips_skip` | `(&str, i64) -> Result<String>`，显式指定高频屏蔽阈值，沿用原标注行为。 |

- `0.2.0` 将 `annotate_ips_with_skip_top` 更名为 `annotate_ips_skip`，用户已选择移除旧名称，不保留弃用或永久别名；`annotate_ips(text)` 保留。同步当前示例、文档、调用方及受控测试调用，记录破坏性变更；历史证据中的旧名称保留原文。
- 数据和行为基线为已固定的本机 Python Lingose `0.2.0`。用户确认它与 `0.2.1` 数据相同；后者 README 中的四组小写别名继续保留。
- P0 已固定安装位置、实际查询数据库、代码/数据版本与摘要；继续使用并核验该基线，不能把相邻 Python 源码目录中的数据库自动当作已安装包的数据。
- `../lingose-python`、`../lingose-typescript`、`../chrome-extension` 都是只读参考；记录所用版本和相关工作区差异，不修改、清理或提交其中的文件。
- 沿用既有 Rust 参数类型、默认参数表达、结果所有权和错误类型，仅作本阶段明确要求的接口变更。文档说明与 Python 的对应关系，不逐字照搬动态类型检查。
- 简单查询先精确匹配拼写，再按 Python 查询规则有条件地回退小写；不能统一转小写。文本标注的回退规则与简单查询不同，必须分别对照。
- 三种发音列表可能长度不同，不得按索引假定 IPA、IPS、IPSM 配对。缺失、冲突、待审和无效候选不得当作采用值导出。
- `kind_list` 保留 Python 成员及其词族、rank、原词排序；`rank` 可作为内部排序数据，不因排序需要扩展首版公共 API。
- 标注必须覆盖 `the` 上下文、字符簇大小写、直/弯撇号、连字符、词形回退、未知词括号与高频屏蔽。`skip_top` 使用原始 NUMBER 阈值，包含等于阈值的词形，超过 `5062` 时按上限处理。
- 非法参数、资源错误和不兼容数据版本须与合法未知词结果区分。不得以空列表或空值掩盖词库损坏。

## CLI 接口与输入输出

- 仅提供 `word WORD [--json]` 和 `annotate` 两个业务子命令，以及标准 help/version。`annotate` 支持可选位置参数、`--input PATH`、`--text TEXT`、`--skip-top N`、`-o PATH` 和 `--json`；位置参数、`--input`、`--text` 互斥，无显式输入时读取 stdin。
- 用户已选择自动识别：位置参数是已存在的普通文件时按文件读取，其余按文本；目录、文件读取或权限错误不得伪装为文本回退。显式 `--input` 的路径不存在时报错，`--text` 始终按文字解释。
- 文本文件和 stdin 按 UTF-8 读取，非法编码报错。纯文本标注保留输入的大小写、空白、换行和标点，不额外追加换行；`--skip-top` 默认 0，验证及上限处理交给库。
- `annotate --json` 仅返回 `{"text": 原文, "annotate": 标注结果}`；`-o` 将所选格式写入文件，成功时 stdout 不重复输出。默认结果写 stdout，诊断写 stderr，结果中不混入进度信息。
- `word --json` 仅包含 `word`、`ipa`、`ips`、`ism`、`ipsm`、`root_lemma`；发音保持独立数组，`ism`/`root_lemma` 为字符串或 null。普通输出也仅显示这些字段，不加入释义、词性、分类或审核字段。此限制不缩减库 API 或数据。
- 参数/用法错误退出码为 2，I/O、资源或其他执行错误为 1，成功及合法未知词为 0；help/version 为 0。shell integration 首版落实为可组合的 stdin/stdout/stderr 和退出码，不扩展交互界面或 shell 插件。

## 数据保护与可重复构建

- 不修改源数据、人工审核结果、已有首选、来源身份、相邻参考仓库或 Python 安装文件。
- SQLite 仅用于开发期基线审计与数据导出，按明确存在的路径只读打开，使用 `mode=ro` 与 `query_only`；禁止因路径错误而新建数据库。需要恢复参考快照时使用本项目隔离目录，不覆盖现有缓存。
- 导出前后核对输入摘要，保留数据版本、算法/格式版本、记录数量和输出 SHA-256。已有基线变化须明确处理，不能静默重写基线以通过检查。
- 保留精确词键、Unicode 字符和组合符、字符串换行、空值、布尔值及零值；不得用通用真值判断吞掉合法 `false` 或 `0`。
- 仅分发公共查询和标注需要的有效字段、回退资格、排序及频率索引，不携带 Python 的完整来源和审核数据库。
- Rust 的索引排序、散列及 Unicode 处理须有自己的明确约定并对照验证；不能直接套用 JavaScript 的 UTF-16 分桶或排序来替代业务顺序。
- 保留原项目许可证、作者署名和第三方来源声明；派生 Unicode 表等资源同时保留相应许可。不得将项目许可证视为对第三方材料的重新授权。
- 开发脚本和基线记录可依赖 Python；正式 crate 的构建与运行不得依赖开发机绝对路径或相邻项目。
- 迁移前后核对受保护数据、P0 向量期望值、Unicode 表和许可证身份；路径变化采用明确映射，不重新导出词库或改写历史证据以适配新路径。需要适配的新版本调用代码与固定预期值分别核验。
- `lingose` 包内自足地包含源码、必要数据、README、来源声明和许可证；`include_bytes!`/`include_str!` 不越出其打包边界。开发工具区分仓库根与库 crate 根，检查 `.gitattributes`、生成器、探针和打包器的路径假设。
- 保留 `0.1.0` 专用发布收据、固定消费者和注册表验收工具，新版本新增独立消费者/收据。旧工具依赖旧布局时在对应历史提交的隔离检出运行，不将其重写为 `0.2.0` 验收。

## 性能与验证

- 先保证正确性，再用真实完整数据比较加载和索引方案。避免每词重复打开数据、全库解析或重建索引；复用已加载的只读数据，并验证并发调用安全。
- 沿用 P1.2 已固定的数值预算及测试条件；为新 workspace/API/CLI 记录新证据，不为通过验收而无解释地放宽预算。已有新路径首启超预算的历史事实继续保留，CLI 进程/I/O 耗时单独记录。
- 基准必须使用 release 构建，区分冷进程/首次访问与已加载数据的热调用；记录机器、工具链、数据和语料摘要、重复次数、统计方法及内存测法。
- 性能场景包含各查询 API、完整分类列表、10,000/100,000 英语词的完整文本，以及 `skip_top=0/1000/5062`。不得用索引查找微基准替代端到端标注时间，也不得截断文本以达标。
- 对照 Python 的完整输出，覆盖未知词、大小写、Unicode、词形、标点、非英语文本和字段不可用状态。实际测试覆盖与支持声明保持一致，不把 Windows 本地通过写成全部平台通过。
- 沿用 edition 2024、MSRV 1.85；新增 CLI 依赖须符合最低版本并实际验证。先运行当前任务最小相关验证；最终对正式 workspace 执行以下检查，开发探针按各自约束单独验证：

```powershell
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo test --workspace --all-features --locked
cargo test --workspace --doc --all-features --locked
cargo doc --workspace --no-deps --all-features --locked
cargo package -p lingose --list
cargo package -p lingose --locked
cargo publish -p lingose --dry-run --locked
cargo package -p lingose-cli --list
cargo package -p lingose-cli --locked
cargo publish -p lingose-cli --dry-run --locked
```

- 上述发布命令按阶段执行。库未进入注册表时，先验证库真实归档与隔离 CLI 构建；库 `0.2.0` 注册表依赖可解析后，再完成 CLI 真实归档及注册表 dry-run，不把临时 path 依赖验证记为注册表验收。
- CLI 集成验证覆盖文本/路径同名、显式输入、stdin、Unicode、换行、空输入、未知词、阈值、JSON 类型、输出文件、无效编码、I/O/参数错误和退出码；与库完整结果对照。

## 文档、打包与发布

- 两包 Cargo 元数据和 README 提供 `https://lingose.com/` 与用户指定的仓库 `https://github.com/englishword/lingose-rust`（Git clone URL 为末尾加 `.git`）。保留原有作者与第三方署名；配置链接不代表 Git remote、权限或远端发布已验证。
- 文档提供可编译的库查询/标注示例、旧函数更名说明、`cargo install lingose-cli`、`lingose word`、文本/文件/stdin/JSON 示例、help 和错误说明，引导访问官网学习。
- 两个 crate 分别检查真实压缩 `.crate` 的体积、文件清单、包内链接和依赖/许可声明；沿用库既定体积预算，正式发布前复核 [Cargo 发布规则](https://doc.rust-lang.org/cargo/reference/publishing.html)。开发数据库、缓存和历史主机路径不进入交付包。
- 打包后的独立库消费工程和 CLI 安装工程不能借用当前 checkout、Python 缓存或相邻数据；依赖准备完成后验证离线构建、全部库 API 基本调用及 CLI 行为。CLI 运行仅需分发二进制，不额外下载词库。
- `lingose-cli` 对库的依赖同时声明本地 path 与发布版本约束；真实发布按 `lingose 0.2.0` → 注册表依赖可用 → CLI 打包/dry-run → `lingose-cli 0.2.0` 顺序执行。
- 正式发布在 CLI6 单独执行，核对该阶段已有授权、两包名称/版本、账号权限、Git remote 和 GitHub Release 条件；已有授权不重复询问。令牌不写入仓库、日志或交接记录。
- GitHub Actions 自动构建五个目标：`x86_64-pc-windows-msvc`、`x86_64-unknown-linux-gnu`、`aarch64-unknown-linux-gnu`、`x86_64-apple-darwin`、`aarch64-apple-darwin`。Release 标签为 `v0.2.0`，资产名称分别为 `lingose-v0.2.0-windows-x86_64.zip`、`lingose-v0.2.0-linux-x86_64.tar.gz`、`lingose-v0.2.0-linux-aarch64.tar.gz`、`lingose-v0.2.0-macos-x86_64.tar.gz`、`lingose-v0.2.0-macos-aarch64.tar.gz`，附许可、使用说明和 SHA-256 清单。
- CI 构建、原生/仿真运行、资产上传分别留证；交叉编译通过不等于目标机运行通过。本地打包、dry-run、真实 crates.io 上传、注册表安装、GitHub Release 和下载后运行分别记录。
