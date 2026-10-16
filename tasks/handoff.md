# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P5.1，完成用户文档、元数据和来源声明（未开始）**。
- P4.2 已完成：P1.2 固定完整预热/OS 缓存条件下，真实公共 API 的运行时间、
  原始资源与内存预算全部通过；数值预算未修改。新文件首次执行超限另列，见下方边界。
- 分支 main，本轮起点 6c8a71b，开始时工作区干净；聚焦提交及实施历史以 Git 为准。
- 本轮仅增加性能工具、测试、正式证据和文档，以及相应 Git 文件规则；
  生产实现/数据/依赖/Cargo 元数据、P0/P4.1/既往证据、源库和相邻参考仓库未改。
- publish=false/include 保护保留；未执行最低版本验证、打包、dry-run、上传或 crates.io 验收。

## 恢复所需文件

- [todo.md](todo.md)：后续既定阶段；[性能说明](../docs/performance.md)说明完整方法及范围。
- docs/performance-verification.json：正式原始样本、预算判定、机器/工具链/输入/可执行文件身份；
  为 .local/p42-performance-bc6s84hu/report.json 的逐字节副本，全部输入/源基线前后不变。
- tools/check_performance.py、tools/performance-probe：最小副本 offline locked release 消费探针，
  thin LTO、codegen-units=1、strip=true；真实公共调用，完整 owned 输出和全文核对。
- tests/test_performance.py：9 项验收保护，含样本/场景/全文标记缺失、p95 极值、绝对内存峰值、
  单位转换和失败子进程日志保留；内存握手有整体 watchdog。
- docs/performance-budget.{md,json}：P1.2 固定条件与数值；原始 JSON 保持不变。
- docs/full-differential-verification.json、docs/correctness-regression-verification.json：P4.1 历史全量
  正确性/隔离 release 证据；本轮逐项核对所有输入身份，无生产修改，未重捕获或重写旧证据。
- docs/{api,rust-api,simple-queries,categories,annotation}.md：现有行为契约；README、Cargo.toml、
  SOURCES.md、data/SOURCES.json、third_party/unicode/LICENSE.txt 是 P5.1 的相关文件。

## 关键结果与边界

- 7 个独立时间样本，min/median/max/nearest-rank p95（7 样本 p95=max），无异常值剔除。
  66 组全词键/混合查询、24 类完整词表、10,000/100,000 词×三个阈值均达标；
  100,000 词中位数 117.84/167.74/188.88 ms，全部完整输出与 P4.1 Python 期望相同。
- 新进程首次公共查询在固定完整预热条件下中位数/p95 45.84/49.33 ms。
  **新路径文件第一次执行仍为 534.24 ms，超过 300 ms**；其中 Popen 返回前为 495.69 ms，
  库内首调用 26.78 ms。四份相同字节的新路径 control/query 对照中无库调用也有创建等待。
  仅定位到库调用之外的父进程创建阶段，未识别 OS 组件，不归因具体扫描器。
  artifact-first 与诊断全部保留；正式统计遵循 P1.2 先完整预热，不保证新文件首次执行延迟。
- 每个内存场景 3 个新进程、所有绝对值分别验收；100,000 词三个阈值均通过，
  全局峰值工作集/私有提交为 21,110,784 / 9,302,016 字节。包含完整输入/输出和临时分配；
  Python 期望在快照后才载入。7×8 个并发首访线程的完整 100,000 词输出核对通过。
- 重复 n't 长词仍有二次成本，4,096 次尾缀补充样本 29.721 ms，无原生栈风险；
  当前完整真实语料有充足余量，未增加缓存或改写算法。
- 本轮仅 Windows 11/MSVC/Rust 1.93.1；不代表 MSRV、其他平台、归档或发布验收。

## 本轮验证

- 正式性能自动验收 passed_under_fixed_warmup_conditions；原始资源 10,460,015 字节。
- 102 Rust 测试（80 库、22 集成）、5 文档测试、70 Python 测试通过；
  唯一忽略项仍为 P2.2 手动加载器探针。根工程与开发探针 fmt/Clippy -D warnings 通过。
- 正式 JSON 与原始 report 完全相同，自动预算重判定和全部输入身份复核通过；
  P4.1 的 1,862,690 项全量差分结论因所有相关输入不变而继续有效。
- 工具和测量范围经过独立只读审阅。首次执行超限已明确记录，未放宽预算。

## 下一步精确动作

1. 核对 Git、本交接及 todo，执行 P5.1，不重做计划或提前进入打包/发布。
2. 对照全部已实现公共 API 整理 README、可编译例子、默认参数、错误与离线行为；
   保留官网与用户指定 https://github.com/englishword，不编造具体仓库 URL。
3. 移除过渡 Error::NotImplemented 变体和相关占位断言/文档，更新开发工具中的错误映射；
   该变更会改变 P4.1/P4.2 输入身份，明确区分历史证据与下一阶段的新验证。
4. 核对作者/项目/Unicode/第三方声明及未来 include；Frequency List 基线缺独立许可文本，
   不以项目许可证推定其授权，不伪造来源证明。
5. 完成 P5.1 最小相关验证、更新 todo/handoff 并聚焦提交，交接 P5.2；
   最低版本、真实 .crate 体积、独立打包消费、dry-run 和正式上传仍按后续阶段执行。
