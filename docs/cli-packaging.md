# CLI4.3：真实库归档和隔离 CLI 候选

本阶段验证 `lingose 0.2.0` 的真实归档，以及依赖该归档解包内容的本地
`lingose-cli 0.2.0` 候选。完整输入摘要、命令和日志身份见
[验证收据](cli-package-verification.json)。恢复起点为 `main` / `9fe3489`。

## 最终库归档

- 文件：`.local/cli43-3h9dn32c/lingose-0.2.0.crate`，**4,053,096 字节**，41 个文件。
- SHA-256：`91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5`。
- 压缩体积低于原定 **5,000,000 字节**预算；两个运行时二进制资源合计
  **10,460,015 字节**，低于原定 12,000,000 字节预算。
- 2026-10-18 复核的 [Cargo 官方发布说明](https://doc.rust-lang.org/cargo/reference/publishing.html)
  仍列出 10 MB 上限；本项目继续使用更严格的既有预算，同时执行 10,000,000 字节检查。
- 精确核对归档清单、全部有效载荷、库 manifest、规范化依赖声明及库专用锁依赖闭包。
  锁文件按库闭包核对，不能要求它与双包 workspace 的锁文件逐字相同。
- 包内 19 个内联 Markdown 本地文件链接均可解析，三个字面量 Rust include
  均落在归档内。链接检查不包括锚点、引用式 Markdown 或 HTML。
- 必要数据、Unicode 表、许可与便携来源声明身份均保持；明确映射历史记录中的旧路径，
  核对 Unicode 表和库依赖名/版本，没有重新导出数据或重写历史收据。
  未携带开发数据库、工具、缓存或主机绝对路径。

归档在逐字节核对的 workspace 快照内生成，快照没有 `.git`，因此没有
`.cargo_vcs_info.json`。起点提交、原始清单及每个输入摘要单独记录，未伪造 VCS 身份。
[Cargo 打包说明](https://doc.rust-lang.org/cargo/commands/cargo-package.html)
明确区分 manifest 规范化、归档、解包构建和 VCS 信息；这里审计的是实际归档。

## 隔离离线消费和安装

先从已准备的依赖缓存 vendor 到新的仓库外临时目录，再使用空 `CARGO_HOME`、
独立 target 和 `--offline --locked`。Cargo metadata 确认所有依赖源码位于隔离根，
库的 manifest 必须指向真实 `.crate` 解包目录。

- Rust **1.93.1** 与 MSRV **1.85.0** 分别以 release 构建
  `tools/package_consumer_020.rs`，检查全部 18 个公共入口的固定结果、完整 CET4
  成员关系、Unicode、大小写、阈值和错误处理。
- CLI 候选只复制当前 manifest/include 中的文件，追加独立 workspace 表，并将唯一的
  库 path 指向解包库。解析 TOML 验证其他配置不变，锁闭包保持 workspace 中的版本。
  两套工具链分别完成 `cargo install --path ... --offline --locked`。
- 将四个消费者/CLI 可执行文件复制到空运行目录。运行前临时移开解包库、CLI、消费者
  源码和 vendor 目录，运行时 PATH 只有 Windows System32；无需 Python、Node、
  Cargo、外置词库或相邻 checkout。
- 每套工具链执行 **25 个 CLI 场景**，逐字或按精确 JSON 值核对 word、annotate、
  stdin、文件/文本同名、显式输入、空输入、Unicode/CRLF、阈值、JSON、`-o`、
  无效编码、I/O/参数错误、stdout/stderr 和退出码。
- 归档解包后通过 **80 项库测试、7 项文档测试**及文档构建；一项既有手动探针忽略。
  文档测试包含旧标注名称不可用的 compile-fail 检查。
- 安装和运行后复核解包库、候选/消费者的 manifest、锁和源码、vendor 与配置身份；
  新增文件也纳入目录清单摘要。空 Cargo home 未产生 registry cache。

本轮另通过 92 项 Python 回归、workspace fmt、Clippy、131 项 Rust 测试、
7 项文档测试和文档构建。执行平台仅 Windows x86_64 MSVC；其他目标留 CLI5。

## 保护解除、dry-run 和证据边界

先在库/CLI 均 `publish=false` 的状态完成候选验证，收据保留在
`.local/cli43-myh4m6er/report.json`。随后只解除库保护，修正两包 README 中过时的
双包禁用描述，重建并重新验证上述最终候选。库源码、受保护数据及依赖未变。

库 `cargo publish -p lingose --dry-run --locked --all-features` 的临时归档与最终候选
SHA-256 相同，Cargo 明确中止上传。CLI 继续保留 `publish=false`。
沙箱首次联网预检遇到 Schannel `SEC_E_NO_CREDENTIALS`；该失败日志与旧候选保留，
最终在正常用户 TLS 环境完成复验。较早一次脚本预期字符串漏字也保留为失败收据，
按固定 P0 值修正后完整重跑，没有调整产品算法或基线。

第三方来源资料缺口，尤其 Frequency List 缺少独立许可文本的事实继续保留。
本阶段不代表服务端发布接受、账号权限、注册表消费、CLI 真实 `.crate`、GitHub CI
或 Release 已验收。真实发布仍按 CLI6 顺序执行；CLI 的真实打包和注册表 dry-run
须等库 0.2.0 可由注册表解析后在 CLI6.3 完成。

## 重现和后续

```powershell
python -I -B -X utf8 -m unittest discover -s tests -v
python -I -B -X utf8 tools/check_cli_package.py --dry-run
```

验证器每次创建独立收据和隔离目录；联网 dry-run 需要可正常使用 Windows TLS 的
执行环境。它只允许库 dry-run，不会自动改变保护设置或执行真实上传。
0.1.0 专用打包、声明生成、消费者和注册表验收工具保持原身份；需要复验时使用
历史提交的隔离检出。

若任一分发输入改变，或改从 Git checkout 生成包含 VCS 元数据的归档，须重建并重新
绑定候选身份。下一项为 **CLI5.1：核对指定仓库 remote/Actions 条件并建立五平台矩阵**。
