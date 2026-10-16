# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P4.1，完成全量差分与必要错误场景验证（未开始）**。
- P3.3 已完成并验证：正阈值、原始 NUMBER/已存词形屏蔽、标点/数字/短语保护、
  Unicode 边界与上下文交互。全部首版公共函数现已实现；尚未做 P4 全量或性能验收。
- 分支 main，本轮起点 3e1d337，开始时工作区干净；提交和实施历史以 Git 为准。
- 无新 Cargo 依赖、数据重导或布局变更。源库、安装包、相邻参考仓库均未修改。
  publish=false/include 保护保留至 P5.3；未做打包、dry-run、上传或 crates.io 验收。

## 恢复所需文件

- [todo.md](todo.md)：既定阶段和未来核对项；[annotation.md](../docs/annotation.md)为当前完整标注规则。
- src/annotation.rs：annotate_from 的负阈值/NUL→扫描→截顶→加载→保护→重扫描→转换路径；
  Skipped 共享筛选、special_prefix、protected_spans；P3.2 context/compound/morphology仍在此。
- src/data/mod.rs：Frequency 初始化时构建一次只读 special 索引；for_annotation 先频率后主词库。
  data 模块临时 dead_code allowance 已移除；格式、版本、生产资源和原始频率索引未变。
- src/data/cache_tests.rs：真实入口损坏/版本错误/频率→主词库顺序、缓存、截顶、无词段和零阈值短路；
  共享索引 26 项排序和原始序号。src/data/tests.rs 提供独立 frequency_fixture 与 ASCII 域错误夹具。
- tools/generate_annotation_frequency_vectors.py：P3.3 独立生成器，固定代码/数据/解释器/UCD身份；
  --write 仅首次创建，全部目标写前预检；--check 拒绝任何漂移，fixture只在.local临时库。
- src/annotation_frequency_vectors.rs：656 个 Python 字面 IGNORECASE/UTF-8长度/小写成员向量。
- tests/annotation_frequency_vectors.rs：221 输入/248 公共断言，含全部 53 条合法 P0 snapshot
  annotation 和 2 条 ValueError→InvalidArgument；6 条动态 TypeError/调用形式明确位于 Rust 类型域外。
- src/data/annotation_frequency_vectors.rs：6 组独立 wire/226 输入，含全部 23 条 P0 标注夹具，
  另核对 3 条 P0 资源行为；不复用生产导出器或修改真实数据。
- tests/api_contract.rs：所有接口/默认入口、拥有所有权、阈值全范围、16线程与截顶。
- [annotation-frequency-verification.json](../docs/annotation-frequency-verification.json)：
  tools/check_queries.py --annotation-frequency 的最小副本离线 locked release、
  七测试二进制仅含二进制运行目录的输出，以及全部构建输入/工具链身份；不是 .crate 消费验收。
- 旧 P0/P2/P3.1/P3.2 向量、Unicode表/许可和证据保持固定。query_vectors/category_vectors、
  tools/reference.py、docs/api.md、docs/reference-baseline.json 仍是全量差分所需基线入口。
- [performance-budget.md](../docs/performance-budget.md)及 JSON、布局/导出文档记录完整语料、
  预算、数据和算法身份；P4.1 长文本应沿用其完整输入，不截断、不改预算。

## 已固定规则与边界

- 负阈值检查先于 text NUL；没有完整英语词段时任意非负阈值原样返回，不加载资源。
  有词段时先按 min(skip_top,5062) 截顶；0只检查主词库，正值先频率再主词库。
  即使全部词被屏蔽仍检查主词库，损坏/不兼容错误不能被成功文本掩盖。
- 频率 contains 使用 P2.1 已固定的原始最小 NUMBER，包含相等阈值；保留30缺口、
  重复词最早序号和异常 winded ; wind。屏蔽只含保存的词形，不由任意词干扩展。
- 完整词的原始小写/直撇号小写匹配先于 Blocked/the/Available/缩写/拆词/推导。
  连字符各段和撇号前缀共享筛选；inflected 的候选词干不额外应用筛选。
- 固定资源10620键全是小写ASCII，其中26项是数字/标点/短语，初始化一次建立长度降序、
  同长原词升序的特殊索引。匹配层明确拒绝非ASCII频率键；不宣称通用Unicode pattern支持。
- special_prefix 精确实现固定CPython对小写ASCII字面pattern的IGNORECASE域：ASCII大小写
  加 İ/ı/ſ/K；二次str.lower成员拒绝前三者、接受K。不依赖编译器Unicode或新regex库。
- 特殊扫描最左起点、同起点首个匹配项；即使成员/邻界拒绝仍消费整个匹配区间，
  不回退短项或重叠起点。两侧固定Python isalnum/M*或 -/'/’ 阻断，空白按字面匹配。
- 未保护片段重新扫描，保护区整体原样输出；the只看重建后紧邻下一span，不借用缩写/短语内部字母。
- 原有首个存在词条阻断、字符簇对齐/大小写、the空白/引号与精确空行、歧义候选和UTF-8切点不变。
  所有查询和文本推导只读共享数据，不向索引写入推导值。
- 公共入口已无 NotImplemented 返回，但 Error::NotImplemented 兼容变体仍保留至P5.1统一移除。
  v1.85 MSRV/其他平台未实测。重复n't超长词匹配/规范化仍可能二次复杂度，见todo的P4.2备注。
- P2.2首进程墙钟异常、frequency-list独立许可文本、最终分发include等后续项继续在todo中保留。

## 本轮验证

- 98项Rust测试通过：76库、12公共契约、1查询、5分类、1基础标注、1上下文、2频率；
  唯一忽略项仍为旧加载器手动性能探针。5文档测试通过。
- 新helper/public/wire预期均直接来自固定Python；旧Unicode/扫描/字符簇/查询/分类回归通过。
  56项Python回归、311条固定Python向量、七个生成器--check、fmt、全目标全feature
  Clippy -D warnings、文档构建及实际标注示例通过。
- 新生成器16项保护探针通过：缺失/首次创建/重复不变、内容/CRLF漂移、写前全目标预检、
  SOURCE/BASELINE/runtime身份错误拒绝；P0与正式产物前后摘要不变。
  临时证据.local/annotation-frequency-vector-guards.json，不分发。
- 最小副本离线locked release及七个测试二进制无资源目录运行通过，证据见正式JSON。
  生产data/、P0、旧向量、Unicode表/许可和全部历史证据不变；安装代码/资源前后身份一致。
- 独立只读review：307条完整公共输出（含26特殊键的25480个边界位置、160组随机组合）
  和20008个protected helper输入均零差异；证据.local/p33-review/{evidence,helper-evidence}.json。
  这些是P3.3集中验证，不替代P4全量/长文本/性能验收。
- 实际只验证Windows MSVC/Rust 1.93.1；尚未执行MSRV、其他平台、正式打包、发布或性能验收。

## 下一步精确动作

1. 核对Git、本交接及todo，执行P4.1；保留全部既有baseline/产物和预算，不开始P4.2或发布。
2. 先读docs/api.md、data-export/verification和现有生成器/独立wire入口，明确完整对照范围与
   合法参数/未知词/数据错误适配；只读核对installed 0.2.0和全部输入指纹。
3. 构建独立的全量Python→Rust差分流程，对全部50335精确词键逐公共查询字段/别名/语言对照，
   全部24分类完整有序词表与标签对照；不要以当前P0样例或成员/摘要自洽代替完整结果对照。
4. 对既定完整10000/100000英语词语料及固定规则文本，按skip_top=0/1000/5062输出全文，
   与本轮固定Python输出逐字比较并记录输入/输出身份；大整数参数先判符号和5062再适配i64。
5. 复核现有真实资源错误/冲突夹具覆盖，补齐真实数据缺少的必要状态和联合错误路径；
   不把预期资源失败编码成合法空值，不静默重写此前预期来通过检查。
6. 从最小相关测试开始，完成P4.1后记录全量计数/差异及验证证据，更新todo/handoff并聚焦提交，
   交接P4.2。最终性能测量、MSRV、打包/dry-run、正式上传与安装验收各按其既定阶段执行。
