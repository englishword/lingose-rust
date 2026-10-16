# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P5.2，工程检查和最低版本验证（未开始）**。
- P5.1 已完成：README/接口契约、元数据核对、来源声明及开发期过渡错误清理已验证。
- 分支 main，本轮起点 e139695，开始时工作区干净；实施和聚焦提交以 Git 历史为准。
- 生产变更仅移除未被调用的 `Error::NotImplemented` 及 Display 分支；开发差分桥同步
  删除其映射。查询/标注算法、依赖、生产资源、派生表和固定基线未改。
- `publish = false` 和现有过渡 include 保留；尚未验证 MSRV、真实归档、dry-run 或发布。

## 恢复所需文件

- [todo.md](todo.md)：后续既定阶段。
- README.md、docs/rust-api.md：18 个公共入口、默认参数、所有权、参数顺序、离线和错误行为。
  README 五个 Rust 代码块作为 crate rustdoc 测试；examples/query.rs 和 annotate.rs 均可运行。
- docs/distribution-review.md：P5.1 审查范围、声明缺口及 P5.3 候选 include。
  当前 include 仍缺编译必需数据，不能当作最终发布清单。
- docs/p5-documentation-verification.json：本轮命令结果、当前身份、受保护文件身份、
  40 个候选文件、21 个本地链接，以及历史证据与当前输入的差异。
- SOURCES.md：保留署名/工具版本/许可链接，补充当前审查说明，不推定第三方授权。
- data/LICENSE：新增与根 LICENSE 逐字节相同的副本，修复原始 UPSTREAM-SOURCES 中
  `(LICENSE)` 的 data/ 相对链接；两份均为 SHA-256 d557539d…3744。
  `.gitattributes` 保留其原始字节，相关新/改文档和 receipt 使用 LF。
- data/SOURCES.json、data/manifest.json、data/UPSTREAM-SOURCES.md：受保护的 P2.1 原始
  产物未改；SOURCES.json 中“P5.1 待审查”是生成时状态，由当前说明补充，不重写摘要。
- 当前 smoke 原始证据：.local/p41-smoke-89egrloa/smoke-evidence.json；匹配全部当前输入，
  881 项完整公共结果零差异。它不能代替 P4.1 的 1,862,690 项正式全量证据。

## 关键决定与边界

- Cargo 名称/版本/作者/许可证、官网与 https://github.com/englishword 原已符合需求，未改元数据。
- 根 LICENSE 与原始 UPSTREAM-SOURCES 仍与固定 Python 参考逐字节一致；相邻 Python
  HEAD b36baf6d55fa259ecc38acea9e881ae6d1477d33、工作树干净，只读访问。
- Frequency List 固定参考缺单独许可文本/本次派生分发条件记录，部分外部分类词表缺
  逐标签来源/许可记录；已准确保留缺口。Phonemizer/eSpeak NG/ECDICT 保留上游署名及
  许可链接，未获取新增授权或声称全部第三方分发条件已独立核实。P6.1 需复核处置状态。
- P4.1/P4.2 原始 JSON 未改。README/SOURCES、error.rs、差分桥及测试说明现已改变，
  历史报告不可描述为当前输入的新验证。正式性能工具会按既定身份保护拒绝当前差异，
  不为消除该拒绝而覆盖旧报告；本轮未重测性能。
- P4.2 历史结果仅在固定完整预热条件下通过；新路径文件首次执行 534.24 ms，超过
  300 ms 的事实仍保留，不保证首次文件执行或其他平台延迟。详见 docs/performance.md。
- 新增许可副本和候选链接清单不代表实际归档已合格；正式 include 修改属于 P5.3。

## 本轮验证

- 102 Rust 测试（80 库、22 集成）、5 文档测试、5 差分工具 Python 测试通过。
  唯一忽略项仍为 P2.2 手动加载器探针。
- 根工程和差分桥 fmt、全目标/全 feature Clippy `-D warnings` 通过。
- 文档构建、两个实际示例、Cargo metadata、18 入口/元数据/本地链接核对通过。
  文档构建发现 README 许可证链接需 `./LICENSE`，修正后通过；Rust 代码块未改。
- 当前输入的 881 项差分 smoke 零差异；固定安装输入及受保护文件前后摘要不变。
- 仅 Windows MSVC / Rust/Cargo 1.93.1；未运行最低版本、归档、dry-run 或上传。
- 原始全量/P4 性能证据和固定预算均未重写；独立只读审阅的两项发现均已修复。

## 下一步精确动作

1. 核对 Git、本交接和 todo，恢复 P5.2，不重做计划或提前发布。
2. 检查实际可用工具链；在声明最低 Rust 1.85 上执行真实验证，准确记录可用平台。
   本阶段前不要将 1.93.1 通过推断为 MSRV 通过；必要工具链准备按实际环境处理。
3. 使用项目现有 `.local/cargo-home` 缓存，执行 P5.2 必需的格式、Clippy、完整测试、
   文档测试和文档构建；开发脚本使用 D:/Python/Python312/python.exe 的固定基线。
   需要新阶段证据时另建 receipt，不调用会覆盖 P4 原始报告的正式验证模式。
4. 完成并验证 P5.2 后更新 todo/handoff、聚焦提交，再交接 P5.3。
5. P5.3 才移除发布保护并修改 include，采用 docs/distribution-review.md 的候选清单，
   对真实归档清单/体积/许可和链接、独立离线消费及 dry-run 逐项实测。
