# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P4.2，验收并优化 release 性能（未开始）**。
- P4.1 已完成：全部 50,335 精确词键的公共查询、完整分类词表、固定完整长文本和必要错误路径验证通过；1,862,690 个公共结果零差异。
- 分支 main，本轮起点 47e4182，开始时工作区干净；提交和实施历史以 Git 为准。
- 本轮只增加正确性工具、夹具、证据及测试模块注册；公共实现、数据布局、生产依赖、Cargo 元数据和固定预算未改。
- 源库、安装包、相邻参考仓库、P0/生产数据/旧向量/Unicode 表与许可/历史证据未修改。
  publish=false/include 保护仍保留至 P5.3；未做性能验收、MSRV、打包、dry-run、上传或 crates.io 验收。

## 恢复所需文件

- [todo.md](todo.md)：既定后续阶段；[全量正确性说明](../docs/full-differential.md)及两个正式 JSON 为本轮验收依据。
- docs/full-differential-verification.json：50,335 词×37 调用、全部标签/完整有序词表、245 条适用 P0 snapshot、18 次规则文本、六份完整语料输出；包含全部输入/工具链/输出身份与 23 条 Python 动态 TypeError 的类型域排除 ID。
- tools/check_full_differential.py：独立枚举真实安装数据库的精确词键，用安装版公共函数生成完整预期；四个小写别名映射到大写，复用只读校验连接，仅缓存当前词的原始 _lookup；不用生产导出器生成期望。
- tools/differential-probe：开发期独立 Cargo 工程，通过 18 个 Rust 公共入口执行完整请求；不新增正式 crate 依赖。最小副本离线 locked release 构建；运行目录只有探针、请求和 Rust 结果，Python 期望保存在外部 capture 目录。
- tests/test_full_differential.py：五项验证器回归，拒绝内部列表重排、Unicode/长文本尾部差异、错误/空值混淆、截断/尾随记录，核对无界整数在窄化前按符号和上限适配。
- tools/generate_error_vectors.py、src/data/p41_query_fixture_tests.rs：两组独立 wire 夹具，211 条断言（14 P0 查询/分类+197 补充）；全部十种 set/selected IPS 不可用状态、精确阻断、独立发音字段、过期/缺失 IPSM、false 分类及完整词表。
- src/data/p41_joint_error_tests.rs：四种主/频率 Data/Version 联合失败，缓存后优先级和参数优先级；全部词被屏蔽后仍返回主库 Data/Version 错误。
- tools/check_queries.py --full-correctness、docs/correctness-regression-verification.json：全部七个测试二进制的最小副本离线 locked release 构建、无资源运行、输出与输入身份；保留 P2/P3 历史报告。不是 .crate 消费验收。
- docs/performance-budget.md、docs/performance-budget.json：P1.2 固定数值预算、完整语料和统计条件，P4.2 不得无解释放宽。
- src/annotation.rs、src/data/mod.rs 及 docs/annotation.md：现有完整标注/独立延迟加载/错误规则。公共查询规则及 API 映射见 docs/{api,rust-api,simple-queries,categories}.md。

## P4.2 可复用的完整输入/期望

- 本轮原始捕获：.local/p41-differential-hk_1s0wj/capture/。
  两份 corpus-{10000,100000}.txt，六份 reference-{词数}-skip-{0,1000,5062}.txt 均为完整文本。
  路径仅为本机恢复便利，权威身份来自正式 JSON；若缺失可重跑全量工具，不能借旧摘要伪造本轮结果。
- 两份语料为 92,862 / 930,474 字节，SHA-256 保持 P1.2 固定值；六份 Python 输出也与 P1.2 原始证据一致。
- 完整 Python/Rust 结果编码均为 26,413,537 字节，SHA-256：
  eee2267dca3ef8c273ad1fbe422a71609dfcb4c378b77cb7b0fa3634e6f6aa49。
- P4.2 的真实公共 API 标注必须使用上述完整输入，逐字核对本轮完整 Python 输出；不要截断文本或以 ASCII 布局负载替代 annotate_ips。
- 其他开发原始捕获与一次被并发源码变动保护拒绝的早期 smoke 均留在 .local；只有正式 JSON 指向的成功捕获用于验收。

## 已固定边界与后续注意

- 沿用全部 P2/P3 规则：简单查询精确优先且有条件小写；标注首个存在词条阻断、字符簇对齐、上下文/缩写/拆词/词形歧义、高频特殊形式保护。
- 负阈值先于 text NUL；无英语词段不加载；非负阈值先截顶 5062，0 只检查主词库，正值先频率后主词库；全部被屏蔽仍验证主词库。
- 频率使用原始最小 NUMBER/保存词形、包含等于阈值、保留 30 缺口及异常 winded ; wind。固定 ASCII 特殊字面域和 Unicode 邻界规则不变。
- Error::NotImplemented 兼容变体仍留至 P5.1 清理；当前所有公共函数已实现。
- P2.2 首进程墙钟异常尚未隔离原因；P4.2 应用真实公共 API 新消费进程复测，保留原始样本，不放宽预算。
- 重复 n't 超长词已无原生栈风险，但逐前缀匹配/规范化仍可能二次复杂度；只在 P4.2 按实际场景评估优化，优化后重跑受影响正确性。
- Frequency List 独立许可文本、最终分发 include、最低版本与其他平台等后续核对仍在 todo 对应阶段。

## 本轮验证

- 全量公共差分：1,862,690 个完整类型/值均相同，再核对完整规范字节身份；24 类/209,759 有序成员加默认 CET4，六份固定长文本的全文输出均通过。
- 102 Rust 测试通过（80 库、22 集成），唯一忽略项为既存加载器手动性能探针；5 文档测试通过。
- 七个隔离 release 测试二进制同样通过全部 102 项，运行目录仅含二进制。
- 61 Python 回归、311 条 P0 固定向量、八个生成器 --check 通过；新增生成器六项保护检查通过。
- fmt、全目标全 feature Clippy -D warnings、文档构建及开发探针格式/Clippy 检查通过。
- 新增代码/工具经过只读独立 review；正式源输入与安装代码/资源前后身份一致，P0/正式数据/历史证据无差异。
- 实际仅验证 Windows MSVC / Rust 1.93.1、固定 Python 3.12.4 / Unicode 15.0；本轮没有建立任何性能达标、MSRV、其他平台或打包/发布结论。

## 下一步精确动作

1. 核对 Git、本交接及 todo，执行 P4.2；先读性能预算/布局条件与两份 P4.1 证据，不重做计划或推进发布。
2. 核对固定输入/输出身份，建立真实公共 API 的 release 消费探针，使用既定优化配置、机器和 7 次独立样本，分开冷进程/首次访问与热调用。
3. 测量各查询、全部完整词表、两份完整语料×三个阈值、内存和并发；每次标注都核对 P4.1 完整期望。记录原始样本、median/nearest-rank p95 与内存方法。
4. 分析冷进程异常与实际不达标项；必要优化后重跑受影响完整差分和错误/并发回归，不删数据、不截文本、不静默改预算。
5. 完成 P4.2 并验证后，更新 todo/handoff、聚焦提交，交接 P5.1；MSRV、打包和正式发布继续按各自阶段执行。
