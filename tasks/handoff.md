# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P1.2，比较数据布局并固定加载、索引和性能预算（未开始）**。
- P1.1 已完成：crate 骨架、Rust 接口契约、基础示例及相关验证齐全。
  P0 行为契约和 311 条固定向量保持原样；本轮只在 docs/api.md 增加 Rust 契约入口。
- 分支 `main`，本轮起点 `f651115`，开始时工作区干净；P1.1 按聚焦提交收口，历史以 Git 为准。
- 本轮结束于 P1.1；**没有生产数据、实际查询/分类/标注实现、性能测量或发布验收**。

## 相关文件

- [todo.md](todo.md)：剩余计划；[Rust 接口契约](../docs/rust-api.md)：全部签名、默认值、所有权、错误及阶段边界。
- [Cargo.toml](../Cargo.toml)、Cargo.lock、src/lib.rs、src/error.rs、src/validation.rs：最小 std-only 工程与参数验证。
- [README](../README.md)、examples/query.rs、examples/annotate.rs：可编译示例，合法调用当前返回明确未实现错误。
- tests/api_contract.rs：7 项接口/参数契约测试；查询值和标注行为尚不属于其验收范围。
- LICENSE 与 SOURCES.md：保留 Python 项目许可、作者署名及来源声明；资源级清单留给 P2.1/P5.1。
- P0 参考：[API 行为契约](../docs/api.md)、[参考基线](../docs/reference-baseline.md)及 JSON、tests/fixtures/python-api-v1.json；工具为 tools/reference.py、tools/audit_reference.py、tools/capture_api_vectors.py。

## 已确定的决策

- `lingose` 0.1.0，edition 2024，声明最低 Rust 1.85；**1.85 尚未安装或实测**。
  当前仅验证 Rust/Cargo 1.93.1、`x86_64-pc-windows-msvc`，不代表跨平台通过。
- 同步 crate 根函数，字符串输入 `&str`；统一 `Result<T, Error>`，拥有所有权的
  Vec<String>/Option<String>/String 或 bool；四组大写名称直接重新导出小写函数。
- 默认入口 meaning/kind/kind_list/annotate_ips，另有 meaning_with_lang、kind_with_label、
  kind_list_with_label、annotate_ips_with_skip_top。默认值分别为 en、CET4、CET4、0。
- skip_top 采用 i64，负值为参数错误，非负值最终按 5062 封顶。P4 大整数向量适配先比较符号和上限再转换，不能先解析 i64；适配器未实现。
- Error 为 non_exhaustive 枚举，区分 InvalidArgument、Data、IncompatibleDataVersion，
  另有仅开发期的 NotImplemented。word/lang/text/负阈值验证已实现；Python 29 字符空白集显式固定。
- 所有通过当前参数验证的调用仍返回 NotImplemented，包括空文本和未知词。
  分类标签待有效资源中的注册表验证；不以硬编码标签抢在资源错误前失败。
  按后续阶段实现时同步替换受影响的占位断言，P5.1 前移除过渡错误与骨架说明。
- 目前无第三方依赖、无 build script；P1.2 再按完整数据实测选择加载与索引方案。
  Cargo include 仅含当前运行源码、示例、README 和许可/来源文件；不带 Python 工具或基线机器路径。
- publish=false 防止尚未实现的骨架发布；P5.3 在完整实现和必要检查通过后移除，并更新生产资源及文档清单。
- 随包提供完整必要数据、离线可用、不公开 lookup/rank、相邻三个参考仓库只读及官网/GitHub 链接等既定范围不变。

## 验证与边界

以下均在 Rust/Cargo 1.93.1、Windows MSVC 执行：

- `cargo fmt --all -- --check`：通过。
- `cargo check --offline --all-targets --all-features`：通过，包含两个示例的编译。
- `cargo clippy --offline --all-targets --all-features -- -D warnings`：通过。
- `cargo test --offline --all-features`：7/7 契约测试、5/5 文档测试通过。
- `cargo test --offline --doc --all-features`：5/5 通过，含两个 no_run 编译示例、一个实际参数错误示例、两个 compile_fail 类型错误示例。
- `cargo doc --offline --no-deps --all-features`：通过，无警告；broken_intra_doc_links 为 deny。
- `cargo package --list --offline --allow-dirty`：当前 12 个文件的分发清单可列出；没有构造真实 .crate、检查压缩体积、独立消费或运行 publish dry-run。
- 元数据、std-only 依赖、保留的完整来源文本与 LICENSE 字节一致性核对通过。
  LICENSE SHA-256：d557539df68e771cc1eedcc91d13f70fca930e508d11eedcafa4b15db49e3744。
  Python 3.12 实际 isspace() 集合与当前 29 字符输入验证表一致。
- P0 固定文件未改动，本轮没有重复全量数据库审计或生成向量；不将既有 Python 对照准备写成 Rust 正确性通过。
- 没有已知业务阻塞。MSRV、生产数据和正式资源错误触发等未完成项按既定后续阶段验证。

## 下一步精确动作

1. 先核对 Git 状态、当前分支、相关提交、本交接和 todo，恢复 P1.2，不重新规划或重做 P0/P1.1。
2. 阅读 docs/rust-api.md 的公开返回/所有权约定及 P0 的数据身份、字段有效性、分类排序、标注回退和频率规则。
3. 在本项目隔离目录（如已忽略的 .local/）建立开发期候选布局/基准原型。
   从已固定安装基线只读取得**全部必要数据**，不能只取 IPS，也不携带完整 Python 审核库。
   保持源库、安装文件及相邻 checkout 不变；漂移须按既有保护处理，不能覆盖基线。
4. 用 release 构建比较紧凑静态索引、压缩加载等方案的原始/压缩体积、冷初始化、热查询、
   完整词表和内存；考虑拥有所有权结果的复制成本。记录机器、工具链、数据及语料摘要、
   重复次数、统计及内存测法，再固定加载/并发约定和数值预算。
5. P1.2 完成并验证后更新状态、聚焦提交并交接 P2.1；不要把原型当作生产导出或查询验收。
