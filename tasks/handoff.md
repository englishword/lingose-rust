# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P3.2，实现上下文与复合词回退（未开始）**。
- P3.1 已完成基础纯文本分词、直接 IPS、字符簇对齐/大小写、未知词中括号；
  所有单词及分类查询继续通过回归。完整标注算法和正阈值频率筛选尚未完成。
- 分支 `main`，本轮起点 `dcc77c1`，开始时工作区干净；提交及详细历史以 Git 为准。
- 没有新增 Cargo 依赖或重导数据。publish=false/include 保护仍保留至 P5.3。
  未执行性能验收、打包、dry-run 或上传；仅验证 Windows MSVC / Rust 1.93.1。

## 恢复所需文件

- [todo.md](todo.md)：既定阶段及剩余工作。
- [annotation.md](../docs/annotation.md)：P3.1 当前行为、Unicode 方案和阶段边界。
- [annotation-unicode.json](../docs/annotation-unicode.json)：固定 Python 3.12.4/UCD 15.0、
  生成器/源代码/许可/输出身份；无通用运行时规范化或编译器 Unicode 依赖。
- [annotation-verification.json](../docs/annotation-verification.json)：最小副本离线 locked release、
  五个二进制无资源目录运行的原始输出、工具链和完整构建输入身份；不是 .crate 消费验收。
- src/annotation.rs：annotate_from 的公共共用路径；word_spans 返回 UTF-8 字节区间，
  is_english 限定完整 ASCII 英语词段；clusters/case_notation 保留完整字符簇及原始形式。
  exact/matched 返回 Available/Blocked/Fallback/Absent；convert 当前仅处理直接可用 IPS。
- src/annotation_unicode.rs 和生成表：固定 isalnum/isalpha/M*、受限 NFD 基础判定，
  原字符簇大小写和精确特殊映射；全部 scalar 测试会调用运行时 base/push_case。
- tools/generate_annotation_unicode.py、tools/generate_annotation_vectors.py：初次 --write、
  后续 --check 拒绝源/现有产物漂移；前后核对固定输入，不覆盖 P0。
- src/annotation_vectors.rs：83 扫描、497 基础、1,024 大小写/对齐向量，
  覆盖全部 298 可接受单标量基础与全部双线体形式，预期直接来自固定 Python。
- tests/annotation_vectors.rs：5 条 P0 及 10 条直接/无词段文本，默认与显式零阈值共 30 断言。
  生成时用 Python 保存状态检查无需成功的 P3.2 推导，不用 Rust 比较结果选样本。
- src/data/annotation_tests.rs（data/tests.rs 子模块）：独立 wire 三态/首个存在变体/
  撇号与大小写优先/无法对齐夹具；cache_tests.rs 使用真实扫描验证资源跳过和错误传播。
- tests/api_contract.rs：基础标注、无词段任意非负阈值、正阈值占位、所有权及 16 线程。
- tools/check_queries.py --annotation：写 P3.1 报告，保留旧 P2.3/P2.4 证据。
- README、docs/rust-api.md、examples/annotate.rs、SOURCES.md：当前阶段行为与来源声明。
- docs/api.md、固定 P0 tests/fixtures/python-api-v1.json、tools/reference.py 和已安装
  Python annotation.py：P3.2 继续使用的行为基线。源文件摘要以 reference-baseline.json 为准。
- src/data/{mod,image}.rs：共享资源、AnnotationState、只读字段和频率；
  for_annotation 仍保留非零阈值频率→主词库顺序，P3.3 才接入实际筛选。

## 已固定实现与阶段边界

- 负阈值先于 text NUL；无完整英语词段时任意非负阈值原样返回且不调用 loader。
  有英语词段且 skip_top=0 仅加载主词库；损坏/不兼容错误不能被括号或未知词掩盖。
- 有英语词段且 skip_top>0 暂在资源加载前返回 NotImplemented，operation 为
  annotate_ips_with_skip_top；P3.3 前不静默忽略频率请求。Error 变体最终移除仍属 P5.1。
- 扫描用固定 Python isalnum()+M*，词内 -/'/’ 只在已有 span 且下一 scalar 为 isalpha 时连接。
  整段仅 ASCII 字母与单个内部分隔符可转换；数字、非英语字母和 Mn/Mc/Me 连段保留原样。
- 标注查词为精确→直撇号→原词小写→小写直撇号，首个存在词条即停止，
  包括 Fallback/Blocked，不可为补缺继续小写搜索。简单查询 lower_variant 不用于文本。
- 有效直接值对齐失败即 [原词]；Fallback/Absent 在本阶段同样输出括号，
  但内部状态分离以便 P3.2 接入规则。已有不可用状态不能当作缺词。
- NFD 只检验基础字母与允许 mark 集合，不规范化输出；243 个 NFD 基础 scalar、
  9 个可接受附加 scalar（含 U+0340）、54 个精确特例。附加字符保持原始顺序。
  所有双线体精确映射和 w̄/W̅ 精确特例按 Python 处理；双线体加 mark 不接受。
- the 上下文、明确缩写、缺源连字符/撇号/词形推导仍未实现；当前有保存值的完整复合词
  可直接转换，不能据此宣称完整回退已完成。输入被视为纯文本，不解析 HTML。
- 主/频率独立缓存、简单字段/分类规则、源身份、数据布局、数值预算均未改变。
  data 模块局部 dead_code allowance 仍覆盖未接入频率访问，P3.3 再收口。
- P5.3 include 仍须纳入 data/ 和 third_party/unicode/LICENSE.txt 等必要资源/许可。
  P5.1 继续处理固定参考缺少独立 frequency-list 许可文本的来源问题。
- MSRV 1.85 尚未实测。P4.2 的 P2.2 首进程墙钟异常跟踪不变；本轮非性能验收。

## 本轮验证

- 58 项 Rust 测试通过：40 库测试、11 公共契约、1 标注/1 查询/5 分类向量测试。
  唯一忽略项为 P2.2 手动加载器性能探针。5 文档测试通过。
- 全部 1,112,064 Unicode scalar 扫描属性/受限 NFD 域/有效大小写摘要与固定 Python 一致；
  helper 向量覆盖全部 298 可接受单标量基础及大小写/分隔符/组合符/非 BMP/新版 Unicode 边界。
- 独立只读复核全部标量及 200,000 组确定性组合字符簇，与 Python 一致；
  分词/匹配/状态和阶段边界审查未发现问题；原表数据摘要测试已补强为运行时 helper 调用。
- 56 项 Python 回归、311 条固定 Python 向量、五个生成器 --check、fmt、
  全目标全 feature Clippy -D warnings、文档构建及实际标注示例通过。
- 新向量生成器的缺失输出/首次创建/CRLF 与不同内容漂移拒绝/错误源摘要拒绝检查通过。
- 最小副本离线 locked release 的五个测试二进制在仅含二进制的目录独立运行通过；
  构建输入与已安装 Python/数据库前后身份不变，证据 docs/annotation-verification.json。
  未修改 P0、data/、既有生成表/许可和 P2 历史证据；相邻参考仓库/安装包均未修改。

## 下一步精确动作

1. 核对 Git、本交接和 todo，执行 P3.2；不重导数据、不重选布局，不提前做 P3.3/发布。
2. 读 docs/api.md 的转换优先级和固定 installed annotation.py 的 convert/match/inflected/
   _morph_candidates 及 annotate_ips 上下文判断，核对源摘要；只读参考。
3. 在已有 Match 三态/Absent 及 case_notation/clusters 上接入 the、明确缩写、
   连字符、直/弯撇号及 s/es/ed/ing；保持先状态阻断、再 the、再直接值、后推导顺序。
4. 上下文只跨 Python 空白和指定引号/括号，遇实际标点或空行中断；需固定 Python 空白规则。
   词形需保留多候选歧义、阻断和反生成拼写规则，不能任意选择候选或写回词库。
5. 扩充独立 wire 夹具和固定 Python 全文本向量；已有两个生成器拒绝覆盖不同字节，
   新阶段产物须明确版本化/扩展生成策略，不静默重写 P0 或 P3.1 冻结预期。
6. 使用 .local/cargo-home 先跑最小相关测试，再验证受影响回归；保持正阈值占位，
   更新 todo/handoff 并创建聚焦提交，交接 P3.3。
