# Rust 首版 API 行为基线

本文件固定 P0 的行为契约，不表示 Rust 实现已完成。范围来自相邻 Python [README](../../lingose-python/README.md)：14 个公共名称对应 10 种行为，排除公开 `lookup` 和 `rank`。P1.1 的 Rust 参数类型、默认参数表达、结果所有权、错误类型和最低 Rust 版本见[接口契约](rust-api.md)。

行为与数据基线为本机已安装的 Lingose **0.2.0**，安装目录为 `D:\Python\Python312\Lib\site-packages\lingose`。相邻 Python 源码声明 **0.2.1**，补充四组小写别名；已核对其 `query.py`、`annotation.py`、`ranking.py`、`types.py` 与安装版逐字节相同。安装版没有小写别名，因此对照工具须将小写公共名称显式映射到安装版大写函数，不能把这种映射称为安装版已原生支持。

## 公共行为矩阵

下表使用 Python 参数和结果描述基线语义，不预先规定 Rust 签名。`None` 表示合法不可用值，`[]` 表示合法空列表。

| 公共名称 | 参数与默认值 | 返回与采用规则 |
| --- | --- | --- |
| `ipa` / `IPA` | `word` | 已选择发音配对的 available IPA，返回列表；当前基线至多一个值，不可用或未知词为 `[]`。 |
| `ips` / `IPS` | `word` | 同上，仅投影 IPS；不从其他候选补值。 |
| `ism` / `ISM` | `word` | 已采用且 available 的构词划分，否则 `None`。 |
| `ipsm` / `IPSM` | `word` | 已选择且依赖有效的 IPSM 列表，否则 `[]`。 |
| `root_lemma` | `word` | 已保存且 available 的词族值，否则 `None`；不执行通用词形还原。 |
| `meaning` | `word, lang="en"` | 精确 `en` 或 `zh` 的原始释义，保留换行、词性缩写等；不可用或未知词为 `None`。 |
| `kind` | `word, label="CET4"` | 仅字段 available 且值为布尔 true 时返回 true；未知词、缺失、冲突或明确 false 均为 false。 |
| `kind_list` | `label="CET4"` | 指定分类全部 available/true 成员的有序实际词键；排序规则见下。 |
| `labels` | 无参数 | 按配置顺序返回已注册分类标签；不把 `COLLINS`、`Band` 属性当作分类。 |
| `annotate_ips` | `text, skip_top=0` | 纯文本 IPS 标注字符串；保留输入大小写、空白、标点和非英语词段。Python 的 `skip_top` 为仅限关键字参数。 |

三种发音列表独立投影，长度不保证相同，不能通过索引配对。只有发音组及对应字段均为 available 才采用已选配对；missing、conflict、pending_review、invalid 和未选候选均不补入结果。IPSM 还检查派生算法版本、依赖状态及 IPS/ISM 摘要；缺失或过期的派生记录无可用输出。四组大小写名称行为必须相同。

## 参数、错误与简单查询匹配

- Python 的 `word`、`lang`、`label` 必须为字符串，否则 `TypeError`。`word` 不能为空、含 NUL 或有首尾 `str.strip()` 空白，否则 `ValueError`；内部空格、原有撇号及连字符不清洗。
- `lang` 仅接受精确 `en`、`zh`；分类标签区分大小写，不支持的语言或未注册标签报 `ValueError`。未知词配合非法标签仍报错。
- 检查顺序为：参数类型、word 内容、语言枚举、打开并检查数据库、分类标签，然后查词。`kind_list` 没有 word 检查；`labels` 只有资源检查。
- 资源不存在、不可读、损坏或必要表缺失为 `LexiconDataError`；不兼容或不一致的 schema 版本为其子类 `SchemaVersionError`。Rust 必须将这类失败与合法未知词/空值分开，具体错误表达由 P1.1 决定。

简单查询先按 SQLite BINARY 规则查原字符串，不做规范化、去标点或统一小写。仅在没有精确词条、首字符 `isupper()` 为真且其余字符均不大写时，尝试一次 `word.lower()`：`Apple` 可回退，`US`、`iPhone`、`McDonald` 不可；单个大写字母也适用该条件。命中后原样返回已保存值，不按输入自动给 IPS 首字母大写。

已存在的精确词条不会因字段不可用而改查另一个小写词条。来源域的精确行同样阻止来源回退：空单元格、待审和冲突不能借小写值补洞。来源匹配结果已经保存在基线数据中；导出时保留其采用结果及标注所需回退资格，不重新合并来源或修订数据。

`kind_list` 先筛选实际词条的 available/true 分类字段，再按以下元组升序排序：

```python
(
    0 if root_available and rank_available else 1,
    root_value if root_available else "",
    rank_value if rank_available else "",
    entry_word,
)
```

缺少任一排序字段的词条全局置后；字符串按原值、区分大小写的 Unicode/BINARY 顺序比较，rank 是完整位置码文本。结果不生成查询别名，也不按来源行序排序。`labels` 按字段配置的 `(ordinal, field_key)` 顺序返回；rank 仅为内部数据。

## 文本、Unicode 与频率规则

`annotate_ips` 先验证 text 为字符串、skip_top 为非 bool 的整数、skip_top 非负及 text 无 NUL。允许空文本、首尾空白；超过 5062 的阈值先按 5062 处理。没有可转换的英语词段时直接返回原文本，无需主词库或频率数据；skip_top=0 不访问频率库。

分词连接 Unicode 字母、数字和组合符，并允许词内直/弯撇号及连字符。仅完整匹配 `[A-Za-z]+(?:[-'’][A-Za-z]+)*` 的词段参与转换，因此与数字、非英语字母或组合符连接的词段保留原样；本接口不解析 HTML。

文本匹配顺序为：原词、同大小写的直撇号形式、小写原形式、小写直撇号形式，去重后遇到首个存在词条即停止。因此全大写和混合大小写文本也可回退，与简单查询不同。只有纯粹 `missing/source_record_missing` 允许后续文本规则；精确词条的空单元格、冲突、待审、invalid 均阻断，不能绕过到另一个大小写词条或拆词规则。

转换按输入每个基础字母与 IPS 的完整组合字符簇对齐，保持输入大小写和撇号样式；支持双线体字母及 `w̄/W̅` 特殊映射。基础字母经 NFD 检查，允许的附加标记为 U+0300、0302、0303、0304、0305、0307、030A、0323。不能按字母完整对齐则返回 `[原词]`，不能按码点猜测；输出不进行通用 Unicode 规范化。

文本规则按以下优先级处理：

1. 高频屏蔽命中即保留输入原词，优先于状态阻断、标注和中括号。
2. 通过状态检查后，`the` 按下一英语词首字母 a/e/i/o/u 选 `ṫhē`，其余及文本结尾选 `ṫhe̊`；保持输入大小写。这是字母规则，不猜测 hour/university 的首音。只跨空白、引号和 `()[]`，不跨逗号等其他标点或空白段落；单换行可跨。
3. 其他完整词已有可用 IPS 时优先采用，包括已有缩写和复合词；无法对齐时直接标未知，不继续猜测。
4. 完整词缺源时，允许 don't、doesn't、aren't、I'm、you're、o'clock 六个明确文本规则；允许直撇号词条服务弯撇号输入。规则不写入主词库。
5. 连字符词逐段转换，未知段单独加括号；其他撇号词先尝试已知前段并保留后缀，n't 优先尝试前面的词干；没有可用前段时整个词加括号。
6. s/es/ed/ing 词形回退须反生成原拼写，支持尾 e、辅音后 y、ie→y 和辅音双写；保留仍对应输入字母的词干标注，新增或改变字母使用原拼写，不推断后缀读音。多个可用候选得出不同输出，或候选被已有不可用状态阻断，均保留 `[原词]`。`is` 不可由单字母 `i` 推导；bus、age/singe/tinge/queue 等遵循固定 Python 规则。

频率阈值使用原始 NUMBER，包含 `NUMBER <= skip_top` 的 LEMMA 和 INFLECTIONS，小写词键比较，重复词取最小序号；不按行数或压紧后的序号解释。NUMBER=30 的缺口、原始异常 token 均保留。带标点缩写和短语按完整形式及词边界保护，优先较长形式，不能把相邻未知词一起屏蔽。频率资源错误与未知词区分。

## 对照入口、样例边界与源码依据

开发对照入口为 `tools/capture_api_vectors.py`，固定样例为 [python-api-v1.json](../tests/fixtures/python-api-v1.json)，数据身份见 [参考基线](reference-baseline.md)。每个公共名称均有对照入口，小写名称通过文件中的 aliases 显式映射到已安装大写函数。

```powershell
python -I -B -X utf8 tools/capture_api_vectors.py --check
python -I -B -X utf8 -m unittest discover -s tests -v
```

初次生成使用 `--write`，已有内容不同则拒绝覆盖；`--check` 不写固定产物。真实快照查询在禁止恢复的 guard 内执行，前后核对代码/资源摘要；构造和破坏数据库仅发生在隔离临时夹具中。未声明预期的异常会中止捕获，不能作为合法空值存入向量。

每条向量含 source、call 和 expected。source 区分 snapshot、fixture、resource-fixture；fixture_spec 描述隔离数据，不代表真实词库内容。`expected.value` 保留原始类型和完整文本；`expected.error` 固定 Python 异常类别，不要求 Rust 复刻 Python 文案或调用签名错误，具体映射由 P1.1 确定。

真实分类列表的 `expected.ordered_list` 记录 length、sha256、head、tail，摘要覆盖**完整有序列表**，首尾十词只是方便人工检查。摘要输入为无 BOM、无末尾换行、紧凑的 UTF-8 JSON（ensure_ascii=false，对象键排序，禁止 NaN，不做 Unicode 规范化）；固定文件本身采用缩进 JSON 方便审阅。隔离夹具的短词表直接记录完整 value。

`{"$integer":"十进制整数"}` 是调用参数中的大整数标签，避免使用浮点数编码超大 skip_top。Python 对照先还原整数；后续 Rust 对照须按语义判断符号和上限，再截至 5062，不应先塞入有限宽整数而溢出。

当前固定记录含 311 条向量：268 条 snapshot、37 条 fixture、6 条 resource-fixture，覆盖全部 14 个公共名称及 24 个分类的完整有序列表摘要（另含默认 CET4 调用）。37 条规则夹具包含可观察的 empty_cell/conflict/invalid 回退阻断及小写 i 的单字母词干限制。

真实快照样例用于固定当前维护值、精确词键、分类成员/顺序及文本输出。隔离夹具用于真实快照不一定包含的路径：空字段阻断、发音列表不等长、非首个候选被选中、过期 IPSM、冲突、Unicode 无法对齐、词形歧义及数据错误。夹具预期不能作为真实数据库的词条状态；例如 Python 查询测试中的 `present` 冲突是夹具，实际维护值已经审核。P0 固定样例不替代 P4 全量对照。

建议规则向量覆盖大小写、未知词、语言/分类错误、完整分类列表、the 跨标点/段落、组合字符和双线体、六组缩写、复合词部分未知、词形反生成及歧义、skip_top=0/1000/5062、阈值相等/超上限、频率短语边界和资源错误；具体哪些向量已记录，以固定样例和生成工具为准。

以下行号对应本次已读的相邻参考源码；其身份由 P0 基线记录固定，未来源码变化不能静默替换本契约：

| 依据 | 已读位置与用途 |
| --- | --- |
| [Python README](../../lingose-python/README.md) | 25–64 行：必需公共函数、小写别名、标注和分类入口。 |
| [Python 包导出](../../lingose-python/src/lingose/__init__.py) | 7–17 行：0.2.1 别名与导出；安装 0.2.0 不含这四个赋值。 |
| [查询实现](../../lingose-python/src/lingose/query.py) | 45–115 行：资源、参数、条件小写回退和标签；154–211 行：字段与派生有效性；213–353 行：精确词键、结果投影、分类及排序。 |
| [标注实现](../../lingose-python/src/lingose/annotation.py) | 17–128 行：阈值、特殊字符簇、扫描和短语保护；138–185 行：词形候选；194–283 行：匹配和回退；286–333 行：参数、上下文及完整文本输出。 |
| [Python API 契约](../../lingose-python/docs/api.md) | 11–56 行：简单查询语义；107–137 行：排序及夹具边界；163–180 行：标注规则。 |
| [查询测试](../../lingose-python/tests/test_query.py) | 120–212 行：查询、精确状态、Unicode、排序和参数；214–311 行：资源、版本和过期派生夹具。 |
| [标注测试](../../lingose-python/tests/test_annotation.py) | 103–155 行：参数、Unicode、大小写和阻断；157–244 行：缺源、频率及 the；246–332 行：词形、复合、缩写和数据错误。 |
