# Lingose Rust 交接记录

## 当前任务与状态

- 当前计划：[todo_CLI.md](todo_CLI.md)，需求：[TASK_CLI.md](../TASK_CLI.md)，约束：[AGENTS.md](../AGENTS.md)。
- 本轮从 `main` / `0802ff6` 恢复，保留并接续 main.rs / annotate.rs 的未提交草稿；**CLI3.3 已完成并通过验收**。具体提交见 Git 历史。下一项为 **CLI4.1：workspace 回归及性能复核（未开始）**；本轮到此交接。
- CLI 现有 `word WORD [--json]`、`annotate [TEXT_OR_PATH | --input PATH | --text TEXT] [--skip-top N] [--json] [-o PATH]`、标准 help/version；无显式标注输入时读取 stdin。
- 两包仍为 0.2.0 / `publish=false`，尚未发布 0.2.0；不得重复上传已发布的 0.1.0。本轮未修改库算法、数据、公共 API、manifest、依赖或根锁文件。

## 当前文件和决定

- [标注输出说明](../docs/cli-annotation-output.md)和[新证据](../docs/cli-annotation-output-verification.json)记录输出契约、命令、日志摘要和保护清单。原始日志/脚本在 `.local/cli33-output/`，Rust 1.85 收据在其 `msrv/`；中断草稿的字节副本由 `resume-start.json` 指向，未覆盖原始输入/旧阶段证据。
- `crates/lingose-cli/src/main.rs` 使用已有 Clap/serde_json 实现 `--json` / 原生路径 `-o`；CLI 仍只委托库，无新依赖。
- 标注 JSON 严格只有字符串字段 `text`（原文）、`annotate`（完整库结果），缩进输出并带末尾换行；纯文本直接写库返回字节，不额外加换行。
- 先完成参数解析、完整 UTF-8 输入读取及一次 `annotate_ips_skip` 调用，再创建输出。前置失败不创建或截断输出，同路径输入/输出可用；成功 `-o` 的 stdout 为空。父目录必须存在，既有文件覆盖；实际写入开始后的 I/O 失败可留下部分文件，不承诺原子替换或回滚。
- 诊断只到 stderr；参数/库参数错误 2、I/O/资源错误 1、成功/合法未知词/help/version 0。写和 flush 错误均传播，help/version 不读取输入或打开输出。
- 输入选择/阈值/UTF-8 规则及 word 六字段行为沿用 CLI3.2/3.1，详见原说明。根/CLI README 已补新增输出示例；完整分发文档留 CLI4.2。
- `crates/lingose-cli/tests/annotate.rs` 覆盖新增 JSON/文件/前置失败保护等行为。恢复时两处 OsStr 推断错误已修正；关闭 stdout 的测试先关管道再写/关闭 stdin，利用 EOF 同步避免调度竞态。

## 验证状态

- Windows x86_64 MSVC / Rust 1.93.1：workspace **131 项 Rust 测试、6 项文档测试通过**，1 项既有手动 loader 探针仍忽略；fmt、workspace 全目标/全功能 Clippy -D warnings、doc 通过。Cargo 检查均 offline/locked。
- 已有 `.local/p52-rustup-home` 的 Rust 1.85.0 在独立 `.local/cli33-msrv-target` 实际通过 **29 项 CLI 测试**（4 单元、17 annotate、8 word）和 CLI 全目标/全功能 Clippy -D warnings。此为局部 MSRV 验证，非完整 workspace MSRV 验收。
- 进程检查对照库完整结果，覆盖五种输入、空文本、Unicode/BOM/换行/控制符、JSON 类型及精确键、新/旧文件、同路径、负数/无效/溢出阈值、无效编码/NUL、互斥输入、输出路径错误、Windows 独占锁、关闭 stdout、help/version 和退出码。合成 I/O fixture 验证部分读取后失败、写及 flush 失败；没有声称实际注入损坏词库。
- PowerShell 5.1.26100.9444 / Git for Windows Bash 5.2.37 的 4 项新增检查通过：ConvertFrom-Json / Python json.load 解析 JSON，及 JSON 文件输出且 stdout 为空；shell 对照同二进制直接文本输出，Rust 进程测试另对照库。Git Bash 运行 Windows 二进制，不是 Linux 验收。
- 独立只读实现审阅已完成。158 个范围外原文件摘要不变，含整个库、数据/P0 向量、Unicode 表、许可证、manifest/锁文件、探针和历史证据。新源文件在当前工具链/MSRV 检查期间摘要一致。
- cfg(unix) 的原生非 UTF-8 路径/symlink 项未在本机运行。没有新全量 Python oracle、长文本差分、release 性能、完整 workspace MSRV、归档消费、打包/dry-run、上传或远端操作。

## 下一项的精确恢复动作

1. 核对 Git、本记录和 CLI4.1，读取根 AGENTS.md 的最终验证/性能约束，以及已有 workspace 工具、差分、性能预算与基线收据；只读沿用已固定 Python/Unicode/保护数据，不重新导出数据或重写历史证据。
2. 为 0.2.0 新建独立日志/收据目录，执行根规范 fmt、workspace Clippy/测试/doc、受影响 Python 回归和实际完整 workspace Rust 1.85 检查；本轮局部 MSRV 仅作前置证据。
3. 对照全部查询 API、全部分类有序词表、固定长文本和错误场景；核对当前 `annotate_ips_skip` 调用适配与不可变期望，不能只凭 CLI3 的选定样例宣称全量差分通过。
4. release 构建按原预算复核初始化/查询/并发/内存，以及完整 10,000/100,000 英语词文本的 skip_top=0/1000/5062；保留已有首启超预算事实，不截断文本或放宽预算。CLI 完整进程/I/O 另计，不替代库性能。
5. 处理本项引起的问题并保存新版本证据；更新计划/交接、聚焦提交后交接 CLI4.2。不提前进入打包、注册表或 GitHub Release。
