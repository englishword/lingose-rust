# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P2.4，实现分类及完整有序词表（未开始）**。
- P2.3 已完成发音、构词、词族和释义查询；四组大小写别名、默认/显式语言和
  精确优先/有条件小写回退已验证。分类和文本标注仍返回 NotImplemented。
- 分支 `main`，本轮起点 `02ebc47`，开始时工作区干净；聚焦提交及实施历史以 Git 为准。
- `publish=false` 与当前 include 保护继续保留；未执行打包、dry-run 或上传。

## 恢复所需文件

- [todo.md](todo.md)：既定任务与剩余阶段。
- [simple-queries.md](../docs/simple-queries.md)、[query-verification.json](../docs/query-verification.json)：
  P2.3 行为、验证边界、最小副本输入摘要、原始离线 release 测试输出。
- src/query.rs：word→lang→共享 lexicon 的验证/访问顺序；独立字段的拥有所有权输出。
  value_from 接受 loader，供隔离资源夹具使用，公共入口与夹具共用同一路径。
- src/data/mod.rs：Lexicon.find 精确键优先，只有精确词不存在才调用小写变体；
  find_exact 保持原始键语义，供未来标注使用。Field 已作 crate 内转发。
- src/query_case.rs、src/query_case_tables.rs：[Unicode 身份](../docs/query-case.json)、
  tools/generate_query_case.py、third_party/unicode/LICENSE.txt。
- src/data/image.rs：已校验的 Image.label/members/kind/bits/counts，P2.4 分类实现直接复用。
- src/data/tests.rs：独立 wire 夹具和 P2.3 查询测试；src/data/cache_tests.rs：错误/加载顺序夹具。
- tests/api_contract.rs：签名、验证/默认/别名、输出所有权及 16 线程查询，剩余接口仍检验未实现。
  tests/query_vectors.rs 由 tools/generate_query_vectors.py 从固定 P0 snapshot 生成 112 条断言。
- README、examples/query.rs、docs/rust-api.md 已与 P2.3 同步；查询示例和 README 查询可实际执行。
- P0 docs/api.md/reference-baseline.json、tests/fixtures/python-api-v1.json；
  P1 data-layout/performance-budget 及 P2.1 data/、data_meta.rs 均原封不动，继续约束后续行为。

## 已固定实现与边界

- 所有简单查询均共享已验证只读数据，不访问频率资源。精确词条存在即停止，即使所求字段不可用。
  只有首 scalar 为 Python isupper 且后续均非大写，才尝试有变化的小写形式；不清洗或规范化词键。
- 发音三列表独立投影，不借用另一字段或标注资格补值。IPSM 使用 P2.1 已过滤无效依赖的保存值，
  不重算。未知/不可用值仅在资源成功加载后返回空 Vec/None；Data/IncompatibleDataVersion 直接传播。
- Unicode 表固定 CPython 3.12.4 / Unicode 15.0：651 个 Uppercase 范围、1,951 个大写字符、
  1,433 条有变化的单字符完整小写映射；支持标题字符、İ 展开、非 BMP 和基线后字符的稳定行为。
  Final_Sigma 在此回退输入域无法触发（Σ 只能在首位，前面不存在 cased 字符），因此单字符映射
  等价于该输入域的 Python 整串 lower。此函数**不能用于未来标注任意字符串的大小写转换**。
- Unicode License V3 从已审计 TypeScript 参考只读复制；生成器固定参考 HEAD/工作区状态、
  源文件/许可/解释器/基线和输出摘要，拒绝覆盖漂移，开发期生成无需联网。
  相邻仓库和安装包未改动。正式构建/运行无需它们或 Python。
- 现有 data 模块局部 allow(dead_code) 继续覆盖未来分类/标注内部方法；接入时逐步移除。
  不因 P2.3 完成移除 Error::NotImplemented，P5.1 收口后再移除全部占位路径。
- 目前只测 Windows MSVC / Rust 1.93.1；声明的 MSRV 1.85 仍留待 P5.2 实测。
- P4 全量公共 API 差分与性能尚未验收，不能把 112 样例或全 Unicode scalar 摘要称为全库查询差分。
  P2.2 历史冷进程墙钟异常仍由 todo P4.2 跟踪；本轮未重测、未放宽预算。
- P5.3 更新 include 时须补入 data 及 third_party/unicode/LICENSE.txt 等必要分发文件，
  当前 publish=false 保护不变。

## 本轮验证

- 最小 simple_query 三夹具通过后，完成 30 项库测试、9 项公共契约及 1 项含 112 断言的
  P0 向量测试；唯一忽略项是需显式执行的 P2.2 加载器性能探针。
- Unicode 5 项测试含全部 1,112,064 个合法 scalar；逻辑摘要与固定 Python 一致：
  `82f0038842bd8f142215338cc3b3e04ee7269dbe93dfc6446c3dd926a4068837`。
  生成器 --check 及隔离重复生成/拒绝漂移/缺失/输出边界检查通过。
- fmt check、全目标全 feature Clippy -D warnings、5 文档测试、文档构建、55 Python 回归通过。
  examples/query 实际输出 IPA/IPS/ISM/IPSM/词族/英中释义。
- tools/check_queries.py：最小 Cargo/src/资源/测试副本离线 locked release 构建；三测试二进制
  复制到仅含二进制的目录，独立运行上述库/契约/向量测试通过。源输入、固定资源及安装基线
  前后摘要不变；证据记录在 docs/query-verification.json。此项不等于 .crate 离线消费验收。
- 只读并行复核确认查询实现、精确阻断、拥有所有权、错误优先级与 Unicode 方案无阻塞问题。
  两个数据资源、P0 基线和固定向量未修改；无新增 Cargo 依赖。

## 下一步精确动作

1. 核对 Git/本交接/todo，执行 P2.4；不重导数据、不重选布局，也不进入 P3/发布。
2. 阅读 docs/api.md 分类验证/排序条款及 src/data/image.rs 的 label/members/kind 方法。
   以 data::lexicon() 共享资源，接入 kind/kind_with_label、kind_list/kind_list_with_label、labels。
3. kind 先验证 word、再加载资源、再验证精确标签、最后查词；可复用 Lexicon.find 的简单查询规则。
   未注册标签须 InvalidArgument(parameter="label")，不能先把未知词当 false 返回。
   kind_list 无 word 步骤，labels 仅需已验证资源。
4. labels 保留资源注册顺序；kind_list 直接复制已校验有序成员，不重新猜测排序，也不生成别名。
   空类成功返回空列表，false/缺失/错误保持区别。用 P0 全分类完整列表摘要和隔离夹具验证。
5. 更新 tests/api_contract.rs 剩余分类占位断言、README/示例/状态说明；标注继续未实现。
   使用 .local/cargo-home 运行最小相关验证及工程检查，受保护资源与相邻项目保持不变。
6. 完成后更新 todo/handoff 并创建聚焦提交，交接 P3.1，不提前实施后续阶段。