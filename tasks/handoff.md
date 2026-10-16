# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P2.2，实现数据加载与查询索引（未开始）**。
- P2.1 已完成并验证：正式受基线保护导出、v1 主词库/频率双资源、manifest、
  Rust 预期常量、来源/许可清单及全记录独立对照。
- 分支 `main`，本轮接手起点 `238de11`，开始时工作区干净；P2.1 聚焦提交以 Git 为准。
- **生产加载器、公共查询/分类/标注仍未实现**；合法公共调用继续返回 NotImplemented。
  `src/data_meta.rs` 尚未接入主 crate，依赖仍为空。`publish=false` 和现有 include 保护保留。

## 关键文件

- [todo.md](todo.md)：既定阶段及剩余计划。
- [data-export.md](../docs/data-export.md)：正式导出规则、产物、重现命令及验证边界。
- [data-verification.json](../docs/data-verification.json)：全记录 Python 对照、输入不变、
  重复导出/隔离重建、Git 换行转换保护及本轮工程检查证据。
- tools/export_data.py：固定 P0 摘要与 require_baseline；SQLite mode=ro/query_only/no_restore；
  一次投影，输入前后核对，已有产物拒绝覆盖，--write 初建或 --check 验证。
- tools/verify_data.py：独立解码/元数据验证，不导入编码器或探针解码器；
  使用已安装 query._lookup、annotation.exact、kind_list 对照全部源记录。
- data/lexicon.bin、frequency.bin、manifest.json、SOURCES.json、UPSTREAM-SOURCES.md：正式产物。
- src/data_meta.rs：预期格式/源数据/算法版本、两资源 SHA-256/体积/计数，P2.2 加载器应直接使用。
- tests/test_export_data.py、test_verify_data.py：37 项新增语义、类型、依赖、篡改及损坏夹具测试。
- .gitattributes：固定生成文件、LICENSE、P0 基线/向量的原始字节，避免 autocrlf 破坏摘要。
- [data-layout.md](../docs/data-layout.md)、[performance-budget.md](../docs/performance-budget.md)
  及 JSON：P1.2 已固定方案/预算，不要重新选型。
- [rust-api.md](../docs/rust-api.md)、[api.md](../docs/api.md)、P0 reference-baseline JSON
  及 tests/fixtures/python-api-v1.json 继续约束实现，P0 文件内容没有修改。

## 固定决策与资源身份

- static-hash：静态二进制字节视图 + 一次建立、随后只读的借用词键 HashMap。
  主词库和频率独立内嵌，各自 OnceLock<Result<_, Error>>，错误也缓存为 Err。
  非英语/空文本不访问资源；skip_top=0 不加载频率，非零按 Python 先频率再主词库。
- v1：112 字节头、小端 u32、UTF-8 偏移池、40 字节 entry、最多 32 类位图及完整有序列表。
  当前 50,335 词/24 类/209,759 成员；频率 10,620 键及原始 1..5062 NUMBER。
  null=0xffffffff，空字符串独立；原始 Unicode/换行/精确大小写不归一化。
- IPA/IPS/IPSM 独立可空；IPSM 跟随存储的依赖 ID/所属词条/字段/状态/算法/文本摘要。
  允许同词条跨发音的实际有效依赖，不重新计算或替换为未采用候选。
- 标注三态 0=阻断、1=纯缺源可规则回退、2=非空可用 IPS。
  真实库状态 1=246、2=50,089，无状态 0；隔离夹具已覆盖状态 0。
- 主词库 10,259,743 字节，SHA-256
  `0f00506a54d8360c3346df6347790811dfd145b98814aa1c12b98c69c0542bd6`。
- 频率 200,272 字节，SHA-256
  `af2813952a826e082a7c683472d067d071a855c0aba47c28e90c1f4829384264`。
  正式流程重新生成并独立全量核对，字节与固定 v1 原型相同，未复制 .local 原型充当正式导出。
- 安装包/实际查询库、相邻只读参考、源审核数据和 P0 向量均未修改。
  原始上游声明逐字节保留；固定参考未附独立 Frequency List 许可文本，P5.1 已列明核对项。
- edition 2024、声明 MSRV 1.85；仅 Windows MSVC / Rust 1.93.1 已验证，MSRV/其他平台未验证。
  P2.2 暂定 sha2 0.10.9 系列用于资源完整性；flate2/serde 不应由探针带入主 crate。

## 本轮验证

- 正式 --write、随后 --check 成功；输入前后全部指纹一致。
- 不同 PYTHONHASHSEED 的 .local/export-replay 完整重建六文件逐字节一致。
- Git index 隔离检出 .local/index-checkout 使用 autocrlf=true/eol=crlf，
  六产物加 LICENSE/P0 基线/向量共九文件逐字节一致，元数据独立校验通过。
- 所有 50,335 条源记录七字段、分类布尔值及 annotation.exact 状态通过；
  24 类完整有序词表、209,759 成员、10,620 频率行和 154 条适用 P0 向量通过。
  使用已安装 Python 3.12.4 / Lingose 0.2.0，详细证据在 data-verification.json。
- 55/55 Python 测试通过，包括 37 项新增。隔离夹具覆盖源库投影后改变、类型、
  false/0、空值/空字符串、组合符/非 BMP、阻断/候选、IPSM 依赖及二进制/元数据篡改。
- 主 crate cargo fmt、Clippy -D warnings、7/7 契约和 5/5 文档测试、文档构建通过；
  尚未接入的 src/data_meta.rs 额外 rustfmt --check 通过。
- 未执行本轮性能实验、cargo package、发布预检或上传；本轮对照耗时不是运行性能验收。
- 没有已知业务阻塞。Git 索引写入需要沙箱提权，按 AGENTS 授权完成阶段提交。

## 下一步精确动作

1. 核对 Git 状态/分支/最近提交、本交接及 todo，恢复 P2.2；保持 P0 和已生成产物身份。
2. 阅读 docs/data-layout.md、data-export.md、src/data_meta.rs 和独立 verify_data.py。
   可参考 tools/layout-probe/src/image.rs 的字节视图，但不能以原型验证替代生产错误路径测试。
3. 实现正式主词库/频率解析与静态 include_bytes!，接入预期常量；核对完整 SHA-256、
   精确格式/schema/算法/数据版本、计数、所有节/引用/UTF-8/排序/成员/状态不变量。
   无 build.rs、恢复、外部缓存或下载；错误不得变成未知词或空列表。
4. 实现两套独立 OnceLock<Result<_, Error>>、借用词键 HashMap 和有序频率索引。
   验证并发首访仅初始化一次、缓存成功/错误、冷热复用及多线程输出一致性。
   保留 Python 规定的资源访问顺序和不用资源的路径，为后续查询/标注接入准备内部入口。
5. 依赖缓存可用 .local/cargo-home；避免修改全局 Cargo 配置。添加 sha2 时更新主 Cargo.lock，
   不带入探针的压缩/JSON 依赖；检查声明 MSRV，但最终最低版本验收仍为 P5.2。
6. 运行 P2.2 最小损坏/不兼容/并发/冷热点检查及相应工程检查；完成后更新状态、聚焦提交，
   交接 P2.3。不要在 P2.2 顺手实现全部查询或开始 P3/发布。
