# 性能预算与测量方法（P1.2）

本轮固定 [performance-budget.json](performance-budget.json) 中的数值，供后续
P2/P4/P5 验收。**公共查询及 annotate_ips 仍未实现，这些预算尚未通过最终验收。**
布局证据为 [layout-probe-results.json](layout-probe-results.json)，选择与格式见
[data-layout.md](data-layout.md)。不能以本轮布局负载代替端到端标注。

## 条件与统计

- 机器：Intel Core i7-1360P，16 逻辑处理器；Windows 11 build 26200、AMD64，
  操作系统报告物理内存 34,067,963,904 字节。CPU/RAM 分别通过只读注册表和
  GlobalMemoryStatusEx 获取；WMI 在当前沙箱不可用，未把获取失败写成未知机器。
- 工具链：rustc/Cargo 1.93.1，x86_64-pc-windows-msvc，LLVM 21.1.8；Python 3.12.4。
  edition 2024、声明 MSRV 1.85；本轮仍没有在最低版本或其他平台验证。
- 探针 release 配置为 thin LTO、codegen-units=1、strip=true。正式验收消费工程使用
  相同优化配置；库不能控制其他消费项目的 profile，因此结论限于所记录条件。
- Rust 四候选各 7 个独立冷进程样本、7 个热场景样本；每轮按
  static → static-hash → gzip → hash 交替测试。每候选先运行一遍不计入统计的完整负载。
  不清理 OS 缓存、不固定 CPU affinity；桌面其他活动不受控制。
- 使用 Rust Instant 计内部场景时间；外部使用 Python perf_counter。
  报告完整样本、min/median/max 和 nearest-rank p95；7 样本下 p95 即最大值。
  热查询的 p95 是**批次平均每操作时间**的分位数，不是单次调用延迟分布。
- 冷进程模式只初始化、验证并输出报告，不跑热查询。外部退出时间包含进程启动、
  两个资源、索引、完整逻辑校验、JSON 和退出；它不是一次公共 API 调用。
  正式冷调用验收另写仅调用一个公共 API 的独立消费进程。
- 每候选 3 个新进程在初始化前后暂停，使用 GetProcessMemoryInfo 的
  PROCESS_MEMORY_COUNTERS_EX 记录工作集、峰值工作集、私有提交和峰值私有提交。
  记录 absolute 和 delta；加载后测量包含两个资源、索引、逻辑校验和运行时，
  不包含热查询负载。峰值包含初始化临时分配；不称为净堆内存。
  [计数器定义](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex)、
  [读取方法](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo)。

主词库、频率与全部语料身份均在结果 JSON。两个原始资源 SHA-256 分别为：

```text
0f00506a54d8360c3346df6347790811dfd145b98814aa1c12b98c69c0542bd6  image.bin
af2813952a826e082a7c683472d067d071a855c0aba47c28e90c1f4829384264  frequency.bin
```

## 热场景覆盖

- 精确词键的 IPA、IPS、ISM、IPSM、root_lemma、meaning_en、meaning_zh：每场景遍历
  全部 50,335 词两轮，计入完整拥有所有权输出的分配与释放。大小写别名共用函数，
  不单列重复计时；这些投影不是尚未完成的公共 API。
- kind：24 类分别遍历全部词两轮；labels：完整 24 标签 Vec 复制 10,000 次。
- kind_list：全部 24 类有序列表完整复制 10 轮，总共 2,097,590 个词；不只取首尾。
  预算中的“一轮”是总时间除以 10，而非除以 240 后的一次平均分类调用。
- 频率：全部 10,620 键精确查找 10 轮。
- 文本布局负载：对完整 10,000/100,000 词语料扫描 ASCII 字母片段、查索引并复制 IPS，
  分别执行 skip_top=0/1000/5062。原文无截断；该探针会把撇号/连字符词拆成
  10,689/106,911 个片段，不保留文本布局、不执行 the/词形/Unicode 算法。
  场景名为 ascii_exact_ips_layout，不能叫 annotate_ips。

最终 P4 应通过全部公共函数执行参数验证、精确/有条件小写匹配及完整结果复制，
加入未知词、大小写/Unicode 的混合查询，并在以下两份**完整语料**上进行真正标注：

| 英语词数 | 输入 UTF-8 字节 | SHA-256 |
| --- | ---: | --- |
| 10,000 | 92,862 | `8efef7b9731cd7f46059a10ef96368e8a2730e41f1e673bd325b24b2c66b2777` |
| 100,000 | 930,474 | `37c2864e135d8503dbda18c6ed4c5fb37c79bdd85e2e782093d6eae53de9fc58` |

语料来自固定排序真实词键与确定性种子，包括大小写、缩写、连字符、词形、the、
未知词、空白与标点，按完整 `[A-Za-z]+(?:[-'’][A-Za-z]+)*` 计数。
完整 Unicode/非英语/错误覆盖另外执行 P0/P4 对照，不能因为该性能语料主要是英语而省略。

## 固定预算

时间均为 release、数据正确性已通过之后的阈值。所有阈值保留在 JSON 中供后续自动读取。

| 场景 | 中位数上限 | p95 上限 |
| --- | ---: | ---: |
| 主词库首次初始化，含摘要、结构验证及词键索引 | 75 ms | 125 ms |
| 频率资源首次初始化 | 5 ms | 10 ms |
| 新消费进程首次公共查询，含进程启动/退出 | 200 ms | 300 ms |
| 各热查询 API 批次平均单次，含 owned 输出 | 2 微秒 | 3 微秒 |
| labels 完整 owned 列表 | 5 微秒 | 10 微秒 |
| 全部 24 类词表一轮完整 owned 复制 | 30 ms | 45 ms |
| annotate_ips 完整 10,000 词，每个阈值分别达标 | 100 ms | 150 ms |
| annotate_ips 完整 100,000 词，每个阈值分别达标 | 1,000 ms | 1,500 ms |

体积：最终 `.crate` ≤ 5,000,000 字节，全部原始运行资源 ≤ 12,000,000 字节。
加载后独立消费进程：工作集 ≤ 32 MiB、私有提交 ≤ 8 MiB、峰值私有提交 ≤ 12 MiB。
完整 100,000 词标注期间：峰值工作集 ≤ 96 MiB，峰值私有提交 ≤ 64 MiB。
内存上限按每个新进程样本分别检查，至少 3 个；不得用均值掩盖超限。
标注峰值须包括完整输入、输出及算法暂存，不截断文本或排除结果缓冲区。

阈值依据：选中原型主词库验证加索引的配对样本中位数/最大值为 30.51/33.00 ms，
冷进程退出最大值 93.61 ms，全部分类复制中位数 18.21 ms，热投影低于 0.4 微秒。
预算为生产参数、Unicode 规则、错误检查和桌面波动留出空间；不据此宣布生产达标。
端到端标注的 100/1,000 ms 是本轮固定的响应时间目标；当前原型不能验证完整算法
是否能达到它。P4.2 必须在完整正确性通过后实际测量，超限就修复并重新验证。

## Python 完整标注参照

已安装 Python 0.2.0 在相同完整语料、每场景 3 次的完整标注中位数：

| 英语词数 | skip_top=0 | skip_top=1000 | skip_top=5062 |
| --- | ---: | ---: | ---: |
| 10,000 | 3,644.36 ms | 3,534.47 ms | 2,771.29 ms |
| 100,000 | 26,480.76 ms | 21,919.39 ms | 17,286.00 ms |

计时包括 Python 函数内部资源打开/缓存与完整输出生成，不包括外部编码和 SHA-256；
不清空 OS 缓存。每场景 3 次完整结果完全相同，完整 UTF-8 输出和 SHA-256 已保存。
这仅记录对照实现条件，不用它与 Rust ASCII 布局负载计算加速比。后续真正的
Rust annotate_ips 输出必须逐字相同，结果 JSON 的六组输出摘要可用于核验。

## 重现

开发 Python 命令使用明确的已安装基线，并通过 mode=ro、query_only 和禁止恢复保护：

```powershell
python -I -B -X utf8 tools/prepare_layout_probe.py --write
python -I -B -X utf8 tools/prepare_layout_probe.py --check
python -I -B -X utf8 tools/check_layout_probe.py
python -I -B -X utf8 -m unittest discover -s tests -p test_layout_probe.py -v
```

首次 --write 创建到已忽略的 .local/layout；存在不同内容时拒绝覆盖。
独立探针与主 crate 分开，首次依赖准备可联网；数据不联网取得。依赖准备好之后：

```powershell
$env:CARGO_HOME = Join-Path $PWD '.local/cargo-home'
$env:CARGO_TARGET_DIR = Join-Path $PWD '.local/layout-target'
cargo fetch --manifest-path tools/layout-probe/Cargo.toml --locked
python -I -B -X utf8 tools/run_layout_probe.py --output .local/layout/rerun-results.json --repeats 7 --python-reference --python-repeats 3
```

runner 构建四个互斥 feature 并复制各自二进制，构建与测量顺序执行，后续构建使用
--offline --locked。输出文件必须不存在，保留历史测量，不覆盖本轮已提交证据。
复测无需再次测 Python 时可省略 --python-reference；预算不会随新测量自动修改。
在新的 shell 中运行上述环境变量设置，避免影响主 crate 的常规 Cargo 验证路径。

探针锁定 flate2 1.1.10/miniz_oxide 0.9.1、sha2 0.10.9、serde 1.0.229 和
serde_json 1.0.154；gzip 使用纯 Rust 后端，无额外 C 压缩库。
[flate2 后端说明](https://docs.rs/flate2/1.1.10/flate2/)。
主 crate 当前仍为 P1.1 std-only 骨架，不发布探针或 .local 数据。

硬件、工具链或语料变化时先记录条件差异；预算变更必须保留失败样本、原因、
正确性影响及明确理由，形成聚焦变更，不能无解释地放宽阈值以通过验收。
