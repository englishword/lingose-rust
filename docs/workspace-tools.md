# CLI1.2：workspace 开发工具适配

从 `main` / `40848a4` 的 CLI1.1 结构继续。本阶段只适配开发工具和验证入口，
库接口更名留 CLI2.1，CLI 业务实现留 CLI3。完整命令、输入和日志身份见
[workspace-tools-verification.json](workspace-tools-verification.json)。

## 路径和固定产物

- `tools/reference.py` 的 `ROOT` 仍指仓库根，新增 `LIB_ROOT` 指向
  `crates/lingose`。Python 基线、P0 JSON、开发工具及历史证据留在仓库根；
  库的源码、数据、Rust 向量和 Unicode 许可使用库根。
- exporter/独立 verifier 默认检查库根；向量生成器检查迁移后的 Rust 文件。
  Unicode 生成器将冻结记录中的 `src/` 等逻辑键映射到实际库目录，
  不改历史 manifest 或 provenance 的键。`.local` 的独立输出仍使用原相对布局。
- Unicode 表和许可逐字节比较；两份既有 Unicode 报告保留原文。
  重新生成的报告只允许生成器身份与历史报告不同，其余字段必须完全一致；
  历史生成器身份另通过 `git show 33e72c9:<path>` 的原始字节验证。
  当前检查输出记录磁盘上的真实产物摘要，不将历史生成器说成当前代码。
- 生产数据、P0 期望、Rust 固定向量、Unicode 表和许可证均不重导出或改写。

## 当前验证入口

loader/query/differential/performance 复制的最小工程保留 virtual workspace、
两个成员 manifest 和原根锁文件；库源码/数据按新路径复制，
差分与性能探针保留自己的独立 manifest/锁文件。
库测试明确使用 `-p lingose`，CLI 脚手架不会被当作库测试二进制。
运行目录仍只放获准的二进制和请求/语料，不借用外部词库。

loader、query 和完整 differential 的默认报告名称加 `-0.2.0`，也可用
`--output` 指定新的仓库内路径；已有报告拒绝覆盖。
性能工具接受 `--correctness` / `--regressions`，默认指向新版报告，
必须核验完整差分、成功的全部回归和当前输入摘要，不能把旧结果当作新验收。
性能预算和完整语料身份不变，原首启超预算事实保留。

layout 的新准备/编译/运行目录统一为 `.local/layout-020`，
旧 `.local/layout` 不变。归档估算从库根读取递归源码和实际版本；
估算包不是 Cargo 真实 `.crate`。测量的原始样本写到输出旁的 `.raw.json`，
不覆盖既有 `raw-measurements.json`，且报告/样本路径都须不存在。
四个候选 feature 必须分别构建，禁止 `--all-features`。

准备依赖后，可从仓库根运行：

```powershell
$env:CARGO_HOME = Join-Path (Get-Location) '.local/cargo-home'
$env:CARGO_TARGET_DIR = Join-Path (Get-Location) '.local/cli12-check-target'
D:/Python/Python312/python.exe -I -B -X utf8 -m unittest discover -s tests -v
D:/Python/Python312/python.exe -I -B -X utf8 tools/export_data.py --check
D:/Python/Python312/python.exe -I -B -X utf8 tools/verify_data.py
D:/Python/Python312/python.exe -I -B -X utf8 tools/generate_query_case.py --check
D:/Python/Python312/python.exe -I -B -X utf8 tools/generate_annotation_unicode.py --check
D:/Python/Python312/python.exe -I -B -X utf8 tools/check_queries.py --full-correctness
D:/Python/Python312/python.exe -I -B -X utf8 tools/check_full_differential.py --smoke
D:/Python/Python312/python.exe -I -B -X utf8 tools/prepare_layout_probe.py --check
cargo build --manifest-path tools/layout-probe/Cargo.toml --no-default-features --features static-hash --offline --locked
cargo build --manifest-path tools/differential-probe/Cargo.toml --release --offline --locked
cargo build --manifest-path tools/performance-probe/Cargo.toml --release --offline --locked
```

第一次准备缺失的 layout 开发产物使用 `--write`；已有差异会报错并保留原文件。
多次运行需要新证据路径。完整差分和性能复核的正式执行留 CLI4.1，
届时先生成当前源码身份对应的完整差分及回归报告，再传给性能工具。

## 新版打包入口和历史边界

- `tools/check_workspace_package.py` 默认只读核对当前库 manifest 的明确清单，
  并执行 `cargo package --list -p lingose --offline --locked --allow-dirty`。
  支持 `--archive PATH` 审计已有归档；版本前缀取自库 manifest，
  `.orig` 对照库 manifest，锁文件核对库依赖闭包，不要求与 workspace 锁逐字一致。
  结构审计不代表真实归档消费、许可审核或注册表验收。
- `tools/package_consumer_020.rs` 是独立新版消费者入口，本阶段与旧消费者逐字一致；
  CLI2.1 在新版副本中更新标注名称，历史副本保持原文。
- `tools/check_package.py`、`prepare_package_sources.py`、
  `check_registry_consumer.py`、`package_consumer.rs` 以及 0.1.0 收据保持原身份。
  它们属于旧布局；需要复验时从 `33e72c9` 隔离检出执行。
  新分发声明更新留 CLI4.2，真实库归档和离线消费留 CLI4.3，
  CLI 真实归档及注册表 dry-run 留库发布后的 CLI6.3。

## 本阶段验证范围

验证环境仅为 Windows x86_64 MSVC / Rust 1.93.1 / 固定 Python 3.12.4。
本轮检查包括 Python 回归、基线及全部生成器只读检查、独立数据验证、
隔离 loader/完整库回归与 differential smoke、workspace 工程检查、
差分/性能 release 探针构建，以及 layout 四个互斥 feature 的独立构建。
最终计数和逐项结果以机器证据为准。

本轮不执行完整新版差分/性能验收、其他平台运行、真实 `.crate`、
归档消费、dry-run、上传或远端操作。两个包继续保持 `publish=false`，
库 API 和 CLI 脚手架行为维持 CLI1.1 状态。
