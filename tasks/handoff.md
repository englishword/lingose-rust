# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P2.1，实现受基线保护的正式数据导出和校验（未开始）**。
- P1.2 已完成：完整必要数据的四布局对比、v1 格式、加载/并发约定和数值预算已固定。
- 分支 `main`，本轮起点 `59404bb`，开始时工作区干净；按 P1.2 聚焦提交收口，历史以 Git 为准。
- 本轮只做开发期布局原型和方案验证；**生产资源、生产加载器及公共查询/分类/标注仍未实现**。
  主 crate 保持 P1.1 骨架，合法调用仍返回 NotImplemented，不将布局负载写成实际 API 性能。

## 关键文件

- [todo.md](todo.md)：剩余计划。
- [data-layout.md](../docs/data-layout.md)：选型、v1 格式、字段/状态、排序和独立加载约定。
- [performance-budget.md](../docs/performance-budget.md)及 JSON：测量方法、固定预算和重现命令。
- [layout-probe-results.json](../docs/layout-probe-results.json)：完整机器/工具链/数据/语料身份、所有计时样本和内存计数、Python 全文输出摘要、测量源码摘要。
- tools/prepare_layout_probe.py：受 P0 保护的完整数据实验投影；--write 初建，--check 重复验证，不是正式生产导出器。
- tools/check_layout_probe.py：独立解码、154 条 P0 snapshot 查询/标签/完整分类顺序校验、Python/Rust 完整逻辑校验。
- tools/run_layout_probe.py：独立 release 构建、7 轮四候选测量、3 次暂停进程内存采样及可选 Python 全文参照。
- tools/layout-probe/：独立、不可发布的 Cargo workspace；FORMAT.md 和 AGENTS.md 说明协议与互斥 feature 命令。
- tests/test_layout_probe.py：空值/空字符串/Unicode/布尔位/回退三态表示和拒绝覆盖保护。
- [rust-api.md](../docs/rust-api.md)、P0 [API 行为契约](../docs/api.md)、[参考基线](../docs/reference-baseline.md)及 JSON、tests/fixtures/python-api-v1.json 继续约束行为。

## 已固定决策

- 选择 static-hash：静态二进制字节视图 + 一次建立、随后只读的借用词键 HashMap。
  原始资源无需解压，避免复制整库字符串；频率保留有序键/原始 NUMBER 二分索引。
- 主词库和频率各自内嵌、各自 OnceLock<Result<_, Error>>。非英语/空文本不访问资源，
  skip_top=0 不触发频率；非零阈值按 Python 先频率再主词库。初始化错误缓存为 Err，不能变空值。
  并发首访/错误缓存尚待 P2.2 实测，本轮未验收。
- v1：112 字节头、小端 u32、字符串偏移池、40 字节 entry、24 类位图及完整有序成员列表。
  主/频率资源分离；保存 source schema、数据及 IPSM 算法版本，资源摘要由生产 manifest/Rust 常量固定。
  UTF-8 字节精确排序，null ID=0xffffffff，不规范化 Unicode、不合并空字符串与 null。
- 完整投影：50,335 精确词键、24 类/209,759 有序成员、10,620 频率词键。
  标注三态 0=阻断、1=缺源可规则回退、2=可用 IPS；本快照 1=246、2=50,089，无状态 0。
  IPA/IPS/IPSM 独立采用；IPSM 跟随实际依赖 ID/状态/原文摘要，不重新推导。
  预存分类业务顺序，因此运行时不必带 rank。生产字段及许可细节见布局文档。
- 正式运行资源预计只需 sha2 0.10.9 系列作完整性检查；当前主 crate 仍 std-only。
  flate2/serde/serde_json 仅探针依赖。以后 Unicode 方案须对照 Python 3.12/Unicode 15.0，
  不自动用 Rust 编译器自带 Unicode 行为替代。
- edition 2024、声明最低 Rust 1.85；本轮仅 Rust/Cargo 1.93.1 / Windows MSVC。
  **MSRV 与其他平台未验证**；publish=false 仍保留。
- 固定预算包含：最终 .crate <=5,000,000 字节；主初始化含索引 median/p95 <=75/125 ms；
  热查询批次单次 <=2/3 微秒；全部 24 类完整词表一轮 <=30/45 ms；
  真正 annotate_ips 的 10,000 词 <=100/150 ms、100,000 词 <=1,000/1,500 ms，
  每个 skip_top=0/1000/5062 独立达标。内存/冷调用等完整阈值以预算 JSON 为准。
  这些是未来验收约束，Rust 公共 API 尚未达到或测量这些预算。

## 验证及测量

- 完整实验准备 --write 成功，随后 --check 重新投影的全部产物完全一致；输入前后指纹不变。
  P0 基线及 311 条固定向量没有更改；相邻仓库/安装包/源库未写入。
- 四候选 static/static-hash/gzip/hash 均以 release 实测各 7 轮，3 次内存采样；
  完整语料，无截断；参数、工具链和统计详见结果 JSON。
- 选中方案主词库验证+索引的配对中位数/最大值 30.51/33.00 ms；
  加载后工作集约 15.46–15.48 MiB，私有提交约 2.26–2.30 MiB（含运行时）。
- 原始资源共 10,460,015 字节；使用完整资源和当前源码的真实压缩 tar 估算 3,923,273 字节。
  **不是最终 cargo package/.crate 体积验收**，没有运行正式打包或发布。
- 独立 Python 解码：154 条 P0 snapshot 投影/标签/完整有序词表通过；
  全逻辑 FNV 与四 Rust 候选一致：b43994db8bc9403a，逻辑 SHA-256 见布局文档。
  不包含错误夹具、标注语义、全词公共 API 对照或并发验收。
- Python 完整 annotate_ips：两语料 × 三阈值 × 三次，完整输出逐次相同，源指纹不变；
  输出身份在结果 JSON，原文在 .local/layout/reference-<词数>-skip-<阈值>.txt。
  Rust ASCII 片段查找负载不能与其直接计算产品加速比。
- Python 全部 18/18 单元测试通过；主 crate fmt、Clippy、7/7 契约测试和 5/5 文档测试、
  文档构建通过；独立探针 fmt 及四 feature 的 Clippy -D warnings 均通过。
- 本轮测量源码摘要与结果记录一致。只读复核确认统计和预算口径一致。
- 没有已知业务阻塞。P2/P3/P4 的未实现项按既定阶段继续，不能以原型替代。

## 下一步精确动作

1. 核对 Git 状态/分支/最近提交、本交接与 todo，恢复 P2.1；不要重跑已完成的性能实验来重新选型。
2. 阅读 docs/data-layout.md、预算 JSON、tools/layout-probe/FORMAT.md 与准备脚本；
   以 P0 require_baseline/read-only/no_restore 的身份保护为正式导出入口。
3. 实现独立的生产导出/校验流程，按固定 v1 编码主词库和频率两个资源；
   从一个受保护记录流生成 manifest、版本/计数/SHA-256、Rust 预期常量和来源/许可清单。
   输出不能依赖开发机绝对路径、Python 或相邻 checkout。不要把 .local 原型直接提交为生产资源。
4. 在正式导出中完成全记录字段/状态/分类/频率核对，覆盖类型、null/空字符串、原始 Unicode、
   false/0、IPSM 依赖及精确词键；验证输入不变、重复导出一致和篡改输入/输出能被拒绝。
   真实库无状态 0，必须用隔离夹具验证阻断；保留 P0 向量和源身份不变。
5. P2.1 验证后聚焦提交并交接 P2.2；公共数据加载/查询实现在后续阶段。
   .local/layout 资源和二进制被忽略；若丢失可用 prepare_layout_probe.py --write 重建。
   探针的依赖缓存/target 位于 .local/cargo-home 和 .local/layout-target，避免修改全局 Cargo 配置。
