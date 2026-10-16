# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P3.1，实现分词、字符簇对齐和大小写转换（未开始）**。
- P2.4 已完成 kind/kind_with_label、kind_list/kind_list_with_label、labels；全部单词及分类查询
  现已实现并验证。文本标注仍返回 NotImplemented（包括空文本和非英语文本）。
- 分支 `main`，本轮起点 `b897127`，开始时工作区干净；聚焦提交和详细实施历史以 Git 为准。
- 没有新增 Cargo 依赖或重导数据；publish=false/include 保护仍留至 P5.3。
  未执行性能验收、打包、dry-run 或上传。

## 恢复所需文件

- [todo.md](todo.md)：既定任务及剩余阶段。
- [categories.md](../docs/categories.md)、[category-verification.json](../docs/category-verification.json)：
  P2.4 分类行为、覆盖及完整原始离线 release 测试/输入/工具链证据。
- src/category.rs：word→资源→精确 label→词条的顺序；kind 复用 Lexicon.find；
  kind_list/labels 直接复制已校验保存的顺序。*_from 注入 loader 的测试路径与公共调用共用。
- src/query.rs、src/data/mod.rs：简单字段查询、Lexicon.find/find_exact、共享资源缓存；
  for_annotation(has_tokens, skip_top) 仍待真正分词器接入，false 不访问资源，零阈值只访问主词库。
- src/data/image.rs：Field、AnnotationState、已验证只读 image 及标注资格/资源访问；
  主词库与频率仍独立 OnceLock<Result<_, Error>>，错误会缓存并克隆传播。
- src/data/category_tests.rs：独立 wire 分类查询夹具，作为 src/data/tests.rs 子模块；
  cache_tests.rs 含完整公共成员一致性及资源错误/访问顺序测试。
- tests/category_vectors.rs：从固定 P0 生成，包含全部分类完整摘要/成员/错误及测试期 JSON 转义核对；
  tools/generate_category_vectors.py --check 拒绝源摘要或输出字节漂移。
- tests/api_contract.rs：分类占位断言已替换，保留标注未实现断言；有公共列表所有权/16 线程检查。
  tests/test_export_data.py 新增 false/missing/pending/conflict/invalid 分类投影隔离验证。
- tools/check_queries.py --categories：构建最小副本并独立运行四个测试二进制，写 P2.4 报告；
  默认参数仍写 P2.3 报告，本轮保留 docs/query-verification.json 历史证据。
- README、examples/query.rs、docs/rust-api.md：单词和分类示例可实际运行，标注仍未实现。
- [api.md](../docs/api.md)、[rust-api.md](../docs/rust-api.md)、固定 P0 向量及已安装 Python 基线，
  P1 data-layout/performance-budget、P2.1 data/ 和 src/data_meta.rs 继续约束行为且未修改。

## 已固定实现与阶段边界

- 分类注册表仅来自已验证数据，不在代码中硬编码 24 类；精确匹配 label，不 trim/改大小写。
  word 错误先于资源，资源错误先于标签，未知词配非法标签仍为 InvalidArgument(label)。
  labels 只需资源，kind_list 为资源→label；均不访问频率，支持合法空类/零标签注册表。
- kind 复用 P2.3 的精确优先/条件小写回退；精确 false/不可用词条阻断小写 true。
  分类成员不依赖发音或标注状态。列表直接保留 P2.1 业务顺序和实际词键，不运行时排序或生成别名。
  所有公共结果拥有内存，修改不影响缓存。
- 简单查询 casing 固定 CPython 3.12.4/Unicode 15.0，生成表/许可/身份见 docs/query-case.json。
  Final_Sigma 在简单查询回退域无法触发，此 helper **不能用于任意文本的通用小写转换**。
  标注需要独立核对扫描类别、NFD、大小写和特殊字符簇；不能套用编译器 Unicode 版本。
- 现有 data 模块局部 allow(dead_code) 仍覆盖未来标注访问方法，接入时逐步移除。
  Error::NotImplemented 保留给 P3 标注占位，最终清理在 P5.1。
- 真实数据、P0 基线/固定向量、生成 Unicode 表/许可、P2.2/P2.3 历史证据和数值预算均未改。
  相邻参考仓库和安装包/数据库未修改。
- 声明 MSRV 1.85，目前只实测 Windows MSVC/Rust 1.93.1。P4 仍需全查询字段/完整标注联合差分
  及 release 性能；本轮分类完整差分不等于 P4 已完成。P2.2 冷进程异常仍在 todo P4.2 跟踪。
- P5.3 include 须包含 data/ 及 third_party/unicode/LICENSE.txt 等必要资源/许可；当前不移除发布保护。

## 本轮验证

- 当前任务最小相关测试通过后，50 Rust 测试通过：34 库测试、10 公共契约、1 简单向量测试
  （112 条断言）及 5 分类向量测试。唯一忽略项是 P2.2 手动加载器性能探针。
- 24 个标签顺序、24 完整分类列表及默认 CET4 共 25 次完整摘要核对通过，24 类有 209,759 成员；
  含默认重复调用共检查 214,984 个成员。完整 UTF-8 JSON SHA-256 覆盖全部输出，不用首尾替代。
- 公共 kind 对全部 50,335 精确词键×24 类共 1,208,040 组结果与上述完整列表一致。
  空类/空注册表/第 31 位/精确阻断/非 BMP/Unicode/错误传播/所有权和 16 线程分类测试通过。
- 311 条 Python 固定向量只读重新检查一致，56 项 Python 回归通过；源摘要前后不变。
  三个生成器 --check、分类生成器确定性及拒绝覆盖/CRLF 漂移/源摘要篡改检查通过。
- fmt、全目标全 feature Clippy -D warnings、5 文档测试、文档构建和实际查询示例通过。
- 最小副本离线 locked release 构建通过，四个测试二进制在无源码/数据文件的目录独立运行通过；
  输入/源库前后身份不变，证据 docs/category-verification.json。本项不是 .crate 离线消费验收。
- 并行只读复核未发现分类实现、验证顺序、边界和生成测试的正确性问题。

## 下一步精确动作

1. 核对 Git/本交接/todo，执行 P3.1；不重导数据、不重选布局，不提前做 P3.2/P3.3 或发布。
2. 阅读 docs/api.md 的文本/Unicode 条款、已固定 Python annotation.py 的扫描、字符簇对齐和
   大小写相关实现，以及 P0 对应文本向量。核对引用基线，不改相邻代码或安装数据。
3. 明确 Rust 的 Unicode 15.0 类别、NFD 与大小写/特殊字形方案及许可/MSRV；
   简单查询 lower_variant 仅用于简单查询，标注须独立实现精确→直撇号→小写等不同回退规则。
4. 接入 annotate_ips 的基本纯文本流程，保留空白/标点/换行/非英语内容；没有可转换 token
   时原样返回且不访问资源。利用 data::for_annotation 策略，skip_top=0 不访问频率。
   根据 AnnotationState 区分有效 IPS、允许缺源回退和明确阻断，不能把不可用字段当作缺词。
5. 覆盖直接标注、ASCII 英语词段限制、组合符/字符簇/特殊字形、大小写、未知括号、无法对齐、
   空文本/非英语无资源路径和资源错误；本阶段不冒称 the/缩写/复合/词形/频率全部完成。
6. 使用 .local/cargo-home 先跑当前最小测试，再做工程检查；更新阶段性实现/验证边界及
   todo/handoff，创建聚焦提交，交接 P3.2。