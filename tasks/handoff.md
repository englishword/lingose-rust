# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P2.3，实现发音、构词、词族和释义查询（未开始）**。
- P2.2 已完成：正式双资源加载/固定身份及结构校验、借用词键 HashMap、有序频率二分、
  独立 OnceLock 成功/错误缓存、访问顺序、并发首访及离线副本验证。
- 分支 `main`，本轮接手起点 `f620843`，开始时工作区干净；聚焦提交以 Git 为准。
- 公共函数仍按 P1.1 返回 NotImplemented；尚未接入查询值、分类或文本标注。
  数据层已验证不等于公共 API 已验收，publish=false/include 保护仍留到 P5.3。

## 恢复所需文件

- [todo.md](todo.md)：既定任务与剩余阶段。
- [data-loader.md](../docs/data-loader.md)、[loader-verification.json](../docs/loader-verification.json)：
  正式加载器说明、全部样本/机器/依赖/源码和资源摘要、隔离运行证据。
- src/data/mod.rs：Resources、lexicon()、Lexicon.find_exact、Frequency.contains、
  for_annotation(has_tokens, skip_top)；两资源独立 OnceLock<Result<_, Error>>。
- src/data/image.rs：固定 v1 解析器及不可变借用视图。内部下标只来自验证过的索引/有界循环，
  不可直接用于未经检查的外部输入。Field/AnnotationState、原始字段/分类/频率访问均在此。
- src/data/tests.rs：12 项独立 wire 夹具，含版本/摘要/边界/Unicode/32 标签/三态/变异。
- src/data/cache_tests.rs：10 项真实资源/缓存/并发/全量身份测试及 1 个显式运行的 release 探针。
- src/lib.rs：公共签名和过渡返回。data 模块有局部 allow(dead_code)，后续接入时逐步移除。
- src/validation.rs：Python 空白集、词/语言/标注参数验证；src/error.rs：已验证的 Data 和
  IncompatibleDataVersion（可 Clone）；NotImplemented 仍保留给未实现阶段。
- src/data_meta.rs、data/：P2.1 资源与元数据原封不动，正式解析器直接使用其预期身份。
- tools/check_loader.py：最小源码/资源副本离线 release 构建及七新进程的加载器检查，非公共基准。
- Cargo.toml/lock：唯一新增直接依赖 sha2 0.10.9；未加入压缩/JSON/数据库/网络依赖。
- [rust-api.md](../docs/rust-api.md)、[api.md](../docs/api.md)、P0 基线/向量及
  [data-layout.md](../docs/data-layout.md)/固定预算继续约束行为。

## 已固定实现与边界

- 主资源静态字节视图 + 借用 &'static str 的 HashMap，不复制整库字符串。
  字节引用使用 static，已通过完整字节模式计数确认最终测试二进制每资源只嵌入一份；
  修正前 const 版本的两份资源及七轮测量身份/样本作为历史证据保留。
  频率是独立静态有序表，二分原始 NUMBER，不为 skip_top 重建集合。
- 先核对 header/magic，再核对固定 format/schema/算法/源数据版本；版本不匹配返回
  IncompatibleDataVersion，优先于该头变化造成的 SHA 不符。其余损坏返回 Data。
- 全摘要/大小/计数/checked arithmetic/UTF-8 及每个字符串边界/排序/引用/成员范围/
  位图等价/标注状态/频率范围均校验一次。错误缓存且随后克隆返回，不变成未知词。
- for_annotation 的 has_tokens 由未来 P3 分词器提供；false 不用资源，阈值零只主词库，
  非零先频率后主词库。仅验证了此私有策略，未声明非英语/空文本公共标注成功。
- 当前 10,620 个频率键已逐条证实全部 ASCII。解析器检查 ASCII 大写/空/NUL/顺序，
  不运行编译器 Unicode 小写转换；其他 UTF-8 保留，真实资源精确身份由固定 SHA 保证。
- 实际公共查询的精确键优先/有条件小写尚未实现。Python 3.12/Unicode 15.0 规则仍需
  P2.3 明确处理，不能直接默认使用 Rust 编译器自带 Unicode 版本替代。
- 全部 P2.1 资源、生成常量、P0 基线/向量和固定数值预算未修改。
  .gitattributes 补充加载器测量输入的 LF 约定，保证后续检出可核对源码字节摘要。
- 声明 MSRV 1.85，实际只测 Rust/Cargo 1.93.1 / Windows MSVC。已声明依赖最低版本
  均不高于 1.85，7 个依赖无声明（保留 null），不是实际最低版本通过的证据。

## 本轮验证

- 22 项新增 Rust 测试通过（12 独立格式/损坏/全截断/逐字节变异 + 10 真实数据/缓存测试）。
  两种资源类型、全部精确词键/频率键、借用指针位置、完整逻辑内容通过。
- Rust 全逻辑 SHA-256 与 P2.1 独立 Python 相同：
  `30c5cd54d9fcf6cc7bdf0d8d99dd7d87f9763e3f65189596aae3c972702d2bd3`。
- 16 线程并发首访各资源只初始化一次、同对象/同字符串；并发失败也只初始化一次，
  正确缓存 Data/IncompatibleDataVersion，验证先频率后主资源及各自独立失败。
- fmt、Clippy 全目标全 feature -D warnings、7 契约/5 文档测试、文档构建、55 Python 测试通过。
- 最小 Cargo/src/双资源副本离线 locked release 构建，通过单独复制的二进制从不含数据/
  源码的目录运行七个新进程；未借用相邻项目或 Python 数据，也未运行打包/上传。
- 最终 static 轮加载/索引中位数/最大值 23.42/33.87 ms，频率 0.599/0.616 ms；缓存精确键查找中位数
  13.56 ns（不含公共验证/大小写/拥有所有权的输出）。计数器仅测试模式启用。
- 两轮首进程墙钟 806.48/732.77 ms。原因未隔离，旧 const 和最终 static 两组原始七样本均保留；
  P4.2 已列出真实公共 API 冷进程复测/分析项，不放宽预算或声称 P4 性能已通过。
- 源码复核未发现重大正确性/安全问题。无业务阻塞；Git 提交需已授权的沙箱写入提权。

## 下一步精确动作

1. 核对 Git/本交接/todo 后执行 P2.3；不重跑布局选型或受保护数据导出。
2. 阅读 docs/rust-api.md、docs/api.md 的简单查询部分及固定 Python 查询规则。
   以 data::lexicon() 共享加载；需要时在 data 模块增加内部 Field 转发或查询辅助，
   不扩展公共 API，也不在此阶段提前实现分类和文本标注。
3. 完成 ipa/IPA、ips/IPS、ism/ISM、ipsm/IPSM、root_lemma、meaning/meaning_with_lang。
   精确词存在即停止；仅在精确键不存在且 Python 允许时回退小写。明确 Unicode 15.0
   大写判断/小写映射方案并对照。语言仍只接受 en/zh，验证顺序按契约。
4. 保留独立发音列表、原始空字符串/Unicode/换行。只有加载成功后的未知/不可用结果
   才返回 Vec::new()/None；加载错误直接传播。IPSM 取已验证的投影值，不重算候选。
5. 更新相应 P1.1 契约测试及示例/状态文档，用 P0 样例和隔离缺失/无效/精确阻断/
   大小写/资源错误夹具验证；分类/标注继续返回 NotImplemented，P5.1 才最终移除变体。
6. 使用 .local/cargo-home 运行当前最小验证和工程检查，保持数据/源库/相邻仓库不变。
   完成后更新任务与交接、聚焦提交，交接 P2.4。不要进入 P3 或发布阶段。
