# Lingose Rust 交接记录

## 当前任务与状态

- 当前计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，约束：[AGENTS.md](../AGENTS.md)。
- 本轮从干净的 `main` / `003a128` 恢复，**CLI4.1 已完成并通过本机验收**；具体提交见 Git 历史。下一项为 **CLI4.2：新版用户文档和分发声明（未开始）**；本轮到此交接。
- 两包仍为 `0.2.0` / `publish=false`，尚未发布。未重复上传 0.1.0，未修改库/CLI 业务实现、数据、P0 期望、Unicode 表、manifest、依赖、锁文件、历史证据或相邻参考仓库。
- 当前 CLI 为 `word WORD [--json]` 和 `annotate [TEXT_OR_PATH | --input PATH | --text TEXT] [--skip-top N] [--json] [-o PATH]`，无显式输入读取 stdin；接口和输出契约沿用 CLI3。

## 当前文件和决定

- [CLI4.1 说明](../docs/cli-workspace-acceptance.md)及[验收汇总](../docs/cli-workspace-acceptance-verification.json)是本轮入口，完整命令/日志/身份收据在 `.local/cli41-acceptance/` 和 `.local/cli41-regression/`。
- 新版独立证据为 `docs/full-differential-verification-0.2.0.json`、`correctness-regression-verification-0.2.0.json`、`performance-verification-0.2.0.json`、`cli-process-verification-0.2.0.json`；旧版报告保持原样。通用工具中的 P4.1/P4.2 标签表示沿用的方法，不是借用旧版验收。
- 全量差分捕获在 `.local/p41-differential-dpvncxg4/`，库性能在 `.local/p42-performance-qj3cyjsi/`，真实 CLI 进程在 `.local/cli41-process-ro5ys0hc/`。这些目录保留完整输入、原始样本/日志和二进制身份，不覆盖历史。
- 新增 `tools/check_cli_process.py`，对当前完整差分/回归身份先验证，在最小 workspace 副本 release/offline/locked 构建 CLI；每个场景完整预热一次，再测七个新进程，计时后逐字/完整 JSON 对照 Python 期望。CLI 使用默认 release profile，库探针仍使用原 thin LTO profile。
- `.gitattributes` 仅追加七条新工具/新报告的 LF 规则。工程回归先完成并保留其原属性文件摘要；该后续元数据差异在总收据中明确记录，未改已编译/测试的代码。

## 验证状态与边界

- Windows x86_64 MSVC，Rust 1.93.1 和实际 Rust 1.85.0：完整 workspace Clippy（全目标/全功能，-D warnings）、各 131 项 Rust 测试、6 项文档测试、doc 均通过；当前 fmt 通过。1 项既有手动 loader 探针仍忽略。Cargo 构建/检查均 offline/locked。
- 工程代理 26 条命令通过，97 项输入逐条及整批前后相同。90 项 Python 回归、固定安装基线审计、P0 捕获、导出及全部八个生成器只读检查通过。独立数据验证通过 50,335 条记录、24 类/209,759 个成员、10,620 个频率词和 154 项适用 snapshot。
- 全量公共差分 **1,862,690 个完整结果，零差异**；全部精确词键每词 37 调用、25 个完整有序列表、245 条适用 P0、规则及六组完整长文本均覆盖。23 项 Python 动态类型/调用形式域排除逐 ID 保留。完整 Python/Rust 结果流 26,413,537 字节、SHA-256 `eee2267dca3ef8c273ad1fbe422a71609dfcb4c378b77cb7b0fa3634e6f6aa49`，也与旧版完整结果一致。
- 七个隔离 release 库测试二进制共 102 项通过，1 项既有探针忽略；运行目录无源码或外置词库。错误/资源损坏/冲突/并发等已有夹具全部继续验证。
- 原 P1.2 运行时间、原始资源和内存预算全部通过，没有放宽阈值。预热后新进程查询中位数/p95 为 36.03/38.75 ms；完整 100,000 词 skip_top=0/1000/5062 中位数分别为 132.99/180.37/200.51 ms。每时间场景七样本；内存每组三个新进程逐个验绝对峰值；八线程同步首次调用七轮通过。
- **新路径首次执行仍超 300 ms**：库探针 675.43 ms（进程创建等待 636.82 ms、主库初始化 27.00 ms），单列而不纳入固定预热后的七样本统计；历史超限记录保留。CLI 首次 word JSON 进程 865.67 ms 另列；具体 OS 组件未确定。
- CLI 26 场景、26 次预热、182 个正式新进程全文对照通过；完整 10,000/100,000 词、三阈值、纯文本/JSON、stdin→stdout / 文件→文件及 word 两格式均覆盖。CLI 无新增数值门槛，进程/I/O 耗时与库预算分开；合成构建超时另验原始部分输出与失败状态留证，不冒充实际构建失败。
- 164 个范围外原文件摘要不变，独立审阅入口为本轮汇总。仅在 Windows 实际执行，cfg(unix) 项未运行；没有真实 `.crate`、打包消费、dry-run、注册表或远端发布。

## 下一项的精确恢复动作

1. 核对 Git、本记录和 CLI4.2；只读查看当前根/库/CLI README、库内 `docs/rust-api.md`、两包 manifest 和来源/许可声明，保留 0.1.0 历史契约及发布收据。
2. 完成 0.2.0 用户文档：全部库能力及可编译示例、`annotate_ips_skip` 更名/旧名移除、六字段查询、文本/文件/stdin、JSON/-o、help/错误、离线数据和 shell 编码边界。安装示例包含 `cargo install lingose-cli`，同时准确说明当前 0.2.0 尚未发布。
3. 核对官网 `https://lingose.com/`、具体仓库 `https://github.com/englishword/lingose-rust` 链接；链接配置不代表 Git remote 或远端访问/发布已验证。
4. 分别核对库和 CLI 的依赖/许可声明，保留作者与第三方署名，不把新 CLI 依赖写回旧 loader/分发证据。实际编译文档示例并运行 CLI 示例，声明仅限已验证范围。
5. 验证后更新计划/交接并聚焦提交，下一项再进入 CLI4.3 的真实库归档/隔离 CLI 候选；本小节不提前打包、dry-run、上传或公开发布。
