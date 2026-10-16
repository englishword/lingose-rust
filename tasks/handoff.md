# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P3.3，实现高频词及词形屏蔽（未开始）**。
- P3.2 已完成并验证 the 上下文、明确缩写、连字符、直/弯撇号和 s/es/ed/ing 回退。
  零阈值标注已覆盖固定 Python 的对应规则；尚未做 P4 全量差分或性能验收。
- 分支 main，本轮起点 7a92b7c，开始时工作区干净；提交与详细历史以 Git 为准。
- 无新增 Cargo 依赖、数据重导或布局变更；源库、安装包、相邻参考仓库均未修改。
  publish=false/include 保护保留至 P5.3；未做打包、dry-run、上传或 crates.io 验收。

## 恢复所需文件

- [todo.md](todo.md)：既定阶段及剩余工作。
- [annotation.md](../docs/annotation.md)：P3.1/P3.2 当前规则、Unicode 方案和验证边界。
- src/annotation.rs：annotate_from 扫描与外层上下文、convert/convert_step 转换优先级、
  context_separator、morph_candidates、inflected；Prefix 显式堆栈避免撇号前缀原生递归。
- src/validation.rs：python_whitespace 与参数验证共用固定 29 标量表。
- src/annotation_context_vectors.rs：3,112 上下文分隔符、1,018 词干谓词、
  3,034 词形输入/5,109 候选元组，预期直接来自固定 Python。
- src/data/annotation_context_vectors.rs：20 组独立 wire 夹具/47 全文断言，
  含全部 13 条 P0 零阈值 annotation 夹具；不复用生产数据导出器。
- tests/annotation_context_vectors.rs：全部 16 条 P0 零阈值快照 + 51 条新增全文，
  默认/显式零阈值共 134 公共断言。旧 P0/P3.1 向量文件未改。
- tools/generate_annotation_context_vectors.py：独立 P3.2 生成策略，前后核对固定输入；
  --write 只首次创建，统一预检全部目标，--check 拒绝源或现有产物漂移。
- [annotation-context-verification.json](../docs/annotation-context-verification.json)：
  tools/check_queries.py --annotation-context 的最小副本离线 locked release、
  六测试二进制无资源运行输出、工具链及全部构建输入身份；不是 .crate 消费验收。
- docs/annotation-unicode.json、src/annotation_unicode{,_tables}.rs：仍沿用固定
  Python 3.12.4/UCD 15.0 的扫描、受限 NFD 基础与完整字符簇大小写，不做通用规范化。
- src/data/annotation_tests.rs：旧直接状态夹具及 4,096 连续弯撇号尾缀成功/未知回归。
- tests/api_contract.rs：阈值占位/验证顺序/所有权及 16 线程（现含上下文/复合标注）。
- src/data/{mod,image,cache_tests}.rs：独立主/频率缓存、原始频率阈值与资源顺序。
- docs/api.md、tests/fixtures/python-api-v1.json、tools/reference.py 与固定 installed
  annotation.py：后续继续只读对照；安装位置和全部摘要以 reference-baseline.json 为准。

## 已固定规则与 P3.3 接入点

- 负阈值先于 text NUL；无完整英语词段时，任意非负阈值原样返回且不调用 loader。
  有英语词段且 skip_top=0 只加载主词库，数据损坏/不兼容错误不被未知词结果掩盖。
- 有英语词段且 skip_top>0 仍在资源加载前返回 NotImplemented，operation 为
  annotate_ips_with_skip_top；P3.3 必须移除此占位并真正接入筛选，不能忽略请求。
  Error 变体最终移除仍属 P5.1。
- 文本匹配仍是原词→直撇号→小写→小写直撇号；首个存在条目停止，包括 Fallback/Blocked。
  简单查询的 lower_variant 不用于文本。三态与 Absent 保持独立，不改源数据或共享索引。
- 转换顺序：明确 Blocked→the→Available（失败不救援）→六个明确规则→连字符→撇号→词形。
  Fallback/Absent 允许推导；the 优先于保存的可用值，但不能绕过 Blocked。
- the 只看紧邻下一 scanner span，整段必须为英语；只跨 29 个 Python 空白及
  双/单直引号、‘’“”、()[]。空行精确按 Python 正则 \n\s*\n 中断；两个 CR 可以跨，
  LF+引号+LF 可以跨。hour/university 是首字母规则，不猜测首音。
- 连字符各段以下一段原文为上下文，末段继承外层上下文；未知段分别括号。
  撇号优先 n't 前词干，再第一撇号前段；前段没有外层上下文，成功后缀原样保留。
  Python 字符切点明确映射到 UTF-8 字节边界。显式栈保持深度优先及备选前缀顺序。
- 词形须反生成拼写，保留对齐词干字符簇、新增/改变字母用原拼写。
  任一候选 Blocked 即阻断；无值或无法对齐候选忽略；最终输出去重后恰好一个才采用。
  bus、age/singe/tinge/queue、尾 e、辅音 y、ie→y、双写规则不作语言学扩展。
- P3.3 应让频率屏蔽先于上述状态与推导，并让连字符各段/撇号前缀共享同一屏蔽集合。
  data::for_annotation 已保留正阈值频率→主词库访问顺序；频率 contains 使用原始序号，
  但标点/短语保护、上限和实际筛选尚未接入；局部 dead_code allowance 留待该阶段收口。
- 受保护 P0、data/、Unicode 生成表/许可及 P2/P3.1 历史证据均不变。
  P5.3 分发清单仍须包含 data/ 和 third_party/unicode/LICENSE.txt。
  P5.1 继续处理固定参考缺少独立 frequency-list 许可文本的来源问题。

## 本轮验证

- 83 项 Rust 测试通过：64 库、11 公共契约、1 查询、5 分类、1 旧标注、1 新上下文向量。
  旧加载器手动性能探针仍是唯一忽略项；5 文档测试通过。
- 新固定 helper/public/wire 向量全部一致，旧全 Unicode scalar/字符簇/扫描和 P2 回归通过。
  56 项 Python 回归、311 条固定 Python 向量、六个生成器 --check、fmt、
  全目标全 feature Clippy -D warnings、文档构建及实际标注示例通过。
- 新生成器校验缺失输出/首次创建/重复不变/内容和 CRLF 漂移拒绝、全目标写前预检、
  错误源摘要拒绝；正式产物及固定参考前后身份不变。
- 最小副本离线 locked release 的六个测试二进制在仅含二进制的目录运行通过，
  证据 docs/annotation-context-verification.json；不是打包后的独立消费验收。
- 独立只读审查对 53,184 个词形输入、16,192 个分隔符及 12,000 组合成状态转换逐字对照，
  无遗留正确性问题；临时探针证据 .local/review-p32/review-evidence.json（不分发）。
- 实际验证仅 Windows MSVC / Rust 1.93.1，MSRV 1.85 和其他平台仍未实测。
  重复 n't 的超长单词已无原生栈风险，但匹配/规范化仍有二次复杂度；不构成本轮性能声明。

## 下一步精确动作

1. 核对 Git、本交接和 todo，执行 P3.3；不重导数据、不改布局，不提前做 P4/发布。
2. 核对固定输入身份，只读 installed annotation.py 的 _skipped_words、_protected_spans、
   annotate_ips 和 convert 中 skipped 优先级；读 docs/api.md 的原始 NUMBER/短语边界规则。
3. 在无词段短路之后把非负阈值按 5062 截顶，通过 for_annotation 加载所需资源；
   零阈值继续不访问频率，正阈值资源错误不得被成功标注或括号结果掩盖。
4. 接入完整词频屏蔽及带标点形式/短语的最长优先、完整边界保护，再扫描未保护片段；
   核对 Python IGNORECASE、Unicode 边界及上下文与保护区交互，不把相邻未知词一起屏蔽。
5. 新阶段向量与证据另行版本化，保持 P0/P3.1/P3.2 固定产物；独立 wire 覆盖原始序号缺口、
   重复词最小序号、阈值相等、0/1000/5062/超上限、撇号与词形屏蔽和错误加载顺序。
6. 使用 .local/cargo-home 先跑最小相关验证，再跑受影响回归，更新 todo/handoff、聚焦提交，
   完成 P3.3 后交接 P4.1；不把这一步自动扩展为性能验收或发布。
