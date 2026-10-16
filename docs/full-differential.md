# P4.1 全量正确性验证

P4.1 使用固定的已安装 Python Lingose 0.2.0 作为期望来源，直接比较 Rust 公共函数的
完整返回值。原始证据分为[公共全量差分](full-differential-verification.json)和
[隔离 release 回归](correctness-regression-verification.json)。本阶段不验收性能预算、
MSRV、其他平台、`.crate` 归档或发布。

本轮共比较 **1,862,690** 个完整公共结果，零差异。Python/Rust 完整结果编码均为
26,413,537 字节，SHA-256 为
`eee2267dca3ef8c273ad1fbe422a71609dfcb4c378b77cb7b0fa3634e6f6aa49`。
102 项 Rust 测试（另有一个既存手动性能探针忽略）、5 项文档测试、61 项 Python
回归、311 条 P0 向量及八个生成器 `--check` 均通过；fmt、全目标全 feature
Clippy `-D warnings`、文档构建和开发探针格式/Clippy 检查通过。七个隔离离线
release 测试二进制同样通过全部 102 项 Rust 测试。

## 全量公共接口对照

`tools/check_full_differential.py` 只读打开 P0 指定的安装数据库，按
`word COLLATE BINARY` 枚举全部 50,335 个精确词键。每个词键执行 37 次公共调用：

- `ipa/IPA`、`ips/IPS`、`ism/ISM`、`ipsm/IPSM` 八个名称。
- `root_lemma`、默认英语 `meaning`、显式 `en` 和 `zh` 释义。
- 默认 CET4 `kind` 和全部 24 个显式分类的 `kind_with_label`。

另外比较 `labels`、默认 CET4 词表和全部 24 个分类的完整有序词表，后者实测合计
209,759 个成员位置；不是只比较首尾或 Rust 成员关系的自洽摘要。

Python 0.2.0 的四个小写别名映射至其大写函数。批量查询复用一个通过原始
`query._open_database` 校验的只读连接，并仅缓存当前词的原始 `_lookup` 结果；公共
函数、参数校验及结果投影保持原实现。数据来自实际 Python 查询，不读取 Rust
资源、正式导出器或布局探针的投影结果。该适配只减少重复打开数据库和重复查询，
不改变待比较的值；原生 Python 的 311 条 P0 向量另行完整复核。

P0 的 268 条 snapshot 中，245 条可由 Rust 已固定的类型和调用方式表达，全部
重新执行并与固定 P0 结果核对，再进入公共差分流；其余 23 条 Python 动态类型或
调用形式 `TypeError` 在报告中逐 ID 列出。合法未知词、空列表、空值、false 与
`InvalidArgument` 各自保留独立编码。错误文案不属于跨语言契约。

差分探针 `tools/differential-probe` 只依赖本 crate，通过 18 个 Rust 公共入口执行
请求。协议保留完整 UTF-8 字符串、有序列表、布尔值、空值和错误类别；Python
逐条读取并比较类型及完整值，最后确认两份完整规范编码逐字节相同。发现任何
差异、截断、多余记录或未知错误类别即失败，不产出成功报告。五项验证器回归
测试检查列表内部重排、Unicode 组合形式、长文本尾部差异、错误与空结果混淆、
截断/尾随记录，以及超大整数适配。

## 完整文本

沿用 P1.2 已固定的 10,000 和 100,000 英语词语料。独立按精确词键重建后，首先
核对 `performance-budget.json` 的完整输入字节数和 SHA-256，再分别调用
`skip_top=0/1000/5062`，保留六份完整 Python 输出。它们还必须与 P1.2 既存的完整
Python 输出身份一致，不能静默替换旧预期。两份输入及六份输出的身份均进入报告，
全文参与 Rust 对照，原始文本保留在报告指向的 `.local/.../capture` 中，供 P4.2 复用。

另有 18 次规则文本调用，覆盖上下文、大小写、Unicode、直/弯撇号、缩写、连字符、
词形、特殊频率短语、标点、空白及非英语文本；P0 的全部适用 snapshot 标注也在
上述 245 条中。Python 无界整数先判断符号和 5062 上限，再编码成 Rust i64；不能
先窄化而溢出。未知词等合法结果不以异常代替，未声明的 Python 异常直接中止。

## 必要错误与冲突夹具

`tools/generate_error_vectors.py` 从固定 P0 及安装版 Python 生成独立期望，使用
一次性 SQLite 夹具和 Rust 既有的独立 wire 编码器，不调用生产导出器。两组测试
包含全部 14 条 P0 查询/分类夹具，以及 197 条补充调用，合计 211 条断言。

补充覆盖 pronunciation set 与 selected IPS 字段各五种状态：纯缺源、empty_cell、
pending_review、conflict、invalid。精确词条阻止借用小写词条；各字段仍独立投影。
还覆盖非首个候选、IPA/IPS/IPSM 长度不同、过期/缺失 IPSM、false 分类、完整分类
列表及标注阻断。生成器在调用 oracle 前固定 P0、安装输入、解释器和 Unicode
身份，拒绝覆盖不同内容，结束后复核原始身份。

`src/data/p41_joint_error_tests.rs` 另用生产加载入口组合主词库与频率资源的
`Data`/`IncompatibleDataVersion` 四种失败，验证两种错误均缓存后仍按当前调用
选择正确错误，参数检查仍先执行；全被高频屏蔽的英语输入仍检查主词库。两种
主词库错误均不能变成成功文本。已有解析器变异、版本/摘要/结构、查询/分类/
标注冲突、并发及资源优先级测试继续完整运行。

六条 P0 resource-fixture 与公共差分流分别验证：0306/0310/0311 对应 Rust
主资源 Data/Version/结构损坏入口；0307/0308/0309 对应频率缺失、零阈值和无英语
词段短路。Rust 使用嵌入式镜像，不要求模拟 Python 的 SQLite 文件布局和缺表文案。

## 隔离、重现与结果边界

两种校验均核对固定输入的前后身份。公共探针在最小源码副本中执行
`cargo build --release --offline --locked`，运行目录仅含二进制、请求和 Rust
结果，不含 Python 期望或词库文件。另一个校验构建并运行全部七个 release 测试
二进制，运行目录只有这些二进制。源码副本、生成输入、安装代码和数据库的身份
在运行后复核；原有基线、资源和历史证据保持不变。

```powershell
python -I -B -X utf8 tools/check_full_differential.py --smoke
python -I -B -X utf8 tools/check_full_differential.py
python -I -B -X utf8 tools/generate_error_vectors.py --check
python -I -B -X utf8 tools/check_queries.py --full-correctness
```

完整对照须读取本机 P0 固定安装数据；正式 crate 的构建和运行不需要 Python 或
相邻仓库。`--smoke` 只验证小范围连接及编码，报告写入 `.local`，不能替代正式
全量证据。正式运行的原始请求/结果保留在新建 `.local` 目录，既存捕获不覆盖。

本轮实际环境为 Windows MSVC / Rust 1.93.1、固定 Python 3.12.4 / Unicode 15.0。
性能测量与优化仅在 P4.2 按既定预算执行；本阶段 release 正确性通过不等于性能
达标。最低版本、打包、dry-run 和正式上传继续按 P5/P6 的独立任务执行。
