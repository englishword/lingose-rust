# Lingose Rust Agent Instructions

## Standard Workflow

For existing projects, **resume from project state before re-planning**.

1. For non-trivial projects, use `tasks/todo.md` as the execution plan and `tasks/handoff.md` as the cross-session resume state; create them if missing during initial planning.
2. At session start, reconcile the current repository state first: inspect `git status`, the active branch, recent relevant commits, `tasks/handoff.md`, and the current item in `tasks/todo.md`.
3. Treat the working tree and Git history as implementation truth, `tasks/todo.md` as the plan, and `tasks/handoff.md` as a concise resume pointer. If they disagree, determine the real state before continuing.
4. Resume the task identified by `tasks/handoff.md`; otherwise use the first unfinished, unblocked task in `tasks/todo.md`. Do not recreate or re-approve a valid existing plan.
5. Read only enough code and documentation to safely execute the current task. Expand context on demand; do not scan the entire repository by default.
6. Work on one small, verifiable task at a time. Keep changes focused and avoid unrelated refactoring or unnecessary complexity.
7. Prefer subagents when independent, repetitive, parallelizable, read-heavy, or noisy work benefits from context isolation; return concise results to the main thread. Keep short or tightly dependent work in the main thread, and avoid parallel write-heavy agents when conflicts are likely.
8. Run the smallest relevant verification first. Continue fixing issues caused by the current task until it is verified or genuinely blocked; record newly discovered future work in `tasks/todo.md`.
9. After a task is completed and verified, update its plan/state and create a focused Git commit unless the user says not to. Never include unrelated pre-existing changes or amend existing commits.
10. Give concise progress updates during execution, but provide comprehensive final summary.
11. Before ending substantial or incomplete work, overwrite `tasks/handoff.md` with the current task/status, relevant files, important decisions or blockers, verification status, and the exact next action.
12. Use Git history as the primary implementation history. Keep `tasks/todo.md` focused on remaining work and `tasks/handoff.md` focused on resumption; avoid duplicating detailed history between them.
13. Create nested `AGENTS.md` files only when a subtree has materially different commands, constraints, conventions, or workflows. Do not duplicate parent instructions.

## 项目目标与范围

- 需求依据为 [TASK.md](TASK.md)；本文件约束开发流程，[任务清单](tasks/todo.md)安排实施顺序，[交接记录](tasks/handoff.md)指向当前恢复点。
- 开发供程序员和 AI 调用的 Rust 库，Cargo/crates.io 名称为 `lingose`，首版版本为 `0.1.0`。
- 实现 `../lingose-python/README.md` 中的公共函数，排除 `lookup()`。不能为了省去完整查询 API 而仅交付网页标注所需的 IPS 数据。
- 用户已选择随包提供全部必要数据；安装后无需额外下载、用户配置、Python、Node 或相邻源码仓库即可离线查询和标注。构建与首次调用均不得隐式联网获取词库。
- TASK 中“开发 npm lingose 时”的性能要求适用于本 Rust crate。TypeScript 包是参考实现，不是本项目的交付物。
- 首版不扩展到 CLI、网页 DOM 操作、浏览器扩展或新词库维护系统。新增需求单独进入任务清单。

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

- 数据和行为基线为本机已安装的 Python Lingose `0.2.0`。用户确认它与 `0.2.1` 数据相同；后者 README 中的四组小写别名也属于 Rust 首版范围。
- P0 固定安装位置、实际查询数据库、代码/数据版本与摘要后才能导出和对照。不能把相邻 Python 源码目录中的数据库自动当作已安装包的数据。
- `../lingose-python`、`../lingose-typescript`、`../chrome-extension` 都是只读参考；记录所用版本和相关工作区差异，不修改、清理或提交其中的文件。
- Rust 参数类型、默认参数的表达方式、结果所有权和错误类型在 P1.1 统一确定。使用适合 Rust 的接口表达，不逐字照搬 Python 动态类型检查；文档必须说明对应关系。
- 简单查询先精确匹配拼写，再按 Python 查询规则有条件地回退小写；不能统一转小写。文本标注的回退规则与简单查询不同，必须分别对照。
- 三种发音列表可能长度不同，不得按索引假定 IPA、IPS、IPSM 配对。缺失、冲突、待审和无效候选不得当作采用值导出。
- `kind_list` 保留 Python 成员及其词族、rank、原词排序；`rank` 可作为内部排序数据，不因排序需要扩展首版公共 API。
- 标注必须覆盖 `the` 上下文、字符簇大小写、直/弯撇号、连字符、词形回退、未知词括号与高频屏蔽。`skip_top` 使用原始 NUMBER 阈值，包含等于阈值的词形，超过 `5062` 时按上限处理。
- 非法参数、资源错误和不兼容数据版本须与合法未知词结果区分。不得以空列表或空值掩盖词库损坏。

## 数据保护与可重复构建

- 不修改源数据、人工审核结果、已有首选、来源身份、相邻参考仓库或 Python 安装文件。
- SQLite 仅用于开发期基线审计与数据导出，按明确存在的路径只读打开，使用 `mode=ro` 与 `query_only`；禁止因路径错误而新建数据库。需要恢复参考快照时使用本项目隔离目录，不覆盖现有缓存。
- 导出前后核对输入摘要，保留数据版本、算法/格式版本、记录数量和输出 SHA-256。已有基线变化须明确处理，不能静默重写基线以通过检查。
- 保留精确词键、Unicode 字符和组合符、字符串换行、空值、布尔值及零值；不得用通用真值判断吞掉合法 `false` 或 `0`。
- 仅分发公共查询和标注需要的有效字段、回退资格、排序及频率索引，不携带 Python 的完整来源和审核数据库。
- Rust 的索引排序、散列及 Unicode 处理须有自己的明确约定并对照验证；不能直接套用 JavaScript 的 UTF-16 分桶或排序来替代业务顺序。
- 保留原项目许可证、作者署名和第三方来源声明；派生 Unicode 表等资源同时保留相应许可。不得将项目许可证视为对第三方材料的重新授权。
- 开发脚本和基线记录可依赖 Python；正式 crate 的构建与运行不得依赖开发机绝对路径或相邻项目。

## 性能与验证

- 先保证正确性，再用真实完整数据比较加载和索引方案。避免每词重复打开数据、全库解析或重建索引；复用已加载的只读数据，并验证并发调用安全。
- P1.2 记录候选布局的原始/压缩体积、初始化耗时、热查询与内存，并固定数值预算及测试条件。不得为通过验收而无解释地放宽预算。
- 基准必须使用 release 构建，区分冷进程/首次访问与已加载数据的热调用；记录机器、工具链、数据和语料摘要、重复次数、统计方法及内存测法。
- 性能场景包含各查询 API、完整分类列表、10,000/100,000 英语词的完整文本，以及 `skip_top=0/1000/5062`。不得用索引查找微基准替代端到端标注时间，也不得截断文本以达标。
- 对照 Python 的完整输出，覆盖未知词、大小写、Unicode、词形、标点、非英语文本和字段不可用状态。实际测试覆盖与支持声明保持一致，不把 Windows 本地通过写成全部平台通过。
- 先运行当前任务最小相关验证；最终发布准备执行以下检查，并记录结果。工程尚未建立时不得声称这些命令已通过。

```powershell
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
cargo test --doc --all-features
cargo doc --no-deps --all-features
cargo package --list
cargo package
cargo publish --dry-run
```

## 文档、打包与发布

- Cargo 元数据和 README 均提供 `https://lingose.com/` 与用户指定的 `https://github.com/englishword`。未核实实际仓库 URL 时不自行编造更具体的仓库地址。
- README 提供可编译的 Rust 查询与标注示例，解释 IPA、IPS、ISM、IPSM、默认参数、错误与离线数据行为，引导访问官网继续学习。
- 检查真实压缩 `.crate` 的体积和文件清单，而不是拿原始数据大小代替归档大小。当前 [Cargo 发布说明](https://doc.rust-lang.org/cargo/reference/publishing.html)列出的上限为 10 MB；正式发布前复核当时规则。
- 打包后的独立消费工程不能借用当前 checkout、Python 缓存或相邻项目中的数据；依赖准备完成后验证离线构建及全部公共 API 的基本调用。
- 正式发布在 P6 单独执行，核对该阶段的执行授权、crates.io 名称、账号权限和版本；已有授权不重复询问。令牌不写入仓库、日志或交接记录。
- `cargo publish --dry-run`、本地打包、真实上传和从 crates.io 安装验收分别记录；不将前一项成功描述为后一项已完成。
