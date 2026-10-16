# P5.2 工程与最低 Rust 版本验证

在 Windows 11、`x86_64-pc-windows-msvc` 上，当前锁定依赖的 Rust/Cargo **1.85.0**
和 **1.93.1** 均完成工程检查。保持 `rust-version = "1.85"`，不提高 MSRV。
原始命令、日志身份、工具链及输入摘要见 [engineering-verification.json](engineering-verification.json)。

## 实测范围

| 检查 | Rust/Cargo 1.85.0 | Rust/Cargo 1.93.1 |
| --- | --- | --- |
| `cargo check --all-targets --all-features` | 通过 | 未单独运行；Clippy 已编译全部目标 |
| `cargo fmt --all -- --check` | 通过 | 通过 |
| `cargo clippy --all-targets --all-features -- -D warnings` | 通过 | 通过 |
| `cargo test --all-features` | 102 Rust + 5 文档通过，1 忽略 | 102 Rust + 5 文档通过，1 忽略 |
| `cargo test --doc --all-features` | 同一 5 项文档再次通过 | 同一 5 项文档再次通过 |
| `cargo doc --no-deps --all-features` | 通过 | 通过 |
| 运行 query / annotate 示例 | 两个均通过 | 示例已随 Clippy 编译；此前 P5.1 运行通过 |

所有编译、Clippy、测试、文档与示例命令均加 `--offline --locked`，不修改依赖解析，
使用现有 `.local/cargo-home`。fmt 直接检查源码，不获取依赖。
两套工具链的完整最终检查均无 warnings。102 项是 80 库测试与 22 集成测试；
唯一忽略项仍为 P2.2 手动冷进程加载器探针，不将其记为通过。
`cargo test` 与显式 `--doc` 的 5 项是相同测试，不合计为 10 项独立覆盖。

固定开发期 Python 3.12.4 的 70 项现有 unittest 通过。它们验证开发工具保护和格式，
不属于正式 crate 的构建或运行依赖；后续仅 Rust 错误诊断实现改变，没有重跑这些
未受影响的 Python 测试，也没有新增镜像实现的测试。

## 最低版本准备与修复

会话开始时默认工具链只有 1.93.1。Rust 1.85.0、rustfmt 和 Clippy 安装在
`.local/p52-rustup-home`，默认用户工具链仍为 stable/1.93.1。
rustup 初次下载标准库遇到 TLS 响应中断；改用官方版本清单记录的 URL 分段获取，
核对范围、长度与完整 SHA-256，再由 rustup 校验并安装。准备工具链的显式网络操作
与 crate 的离线构建分开记录，没有关闭下载校验或增加词库下载步骤。

1.85.0 的首次 `cargo check` 和格式检查通过，Clippy `-D warnings` 发现
`src/data/image.rs` 的 `hex` 使用 `map(format!).collect()` 触发 `format_collect`。
将该辅助函数改为预分配一个 String，并用 `write!` 追加相同的两位小写十六进制文本；
仅用于不兼容数据版本的诊断，不改变数据解析、查询/标注规则、依赖或资源。
未关闭 lint。修改后先运行最小 Clippy，再执行两套工具链的完整工程复核。
既有版本错误优先级与损坏资源回归继续覆盖该分支。

## 输入与证据边界

修改前的当前工具链通过记录和最低版本 Clippy 失败记录均留在新的 `.local/p52-*`
目录中。最终两套检查各自实际保存跑前、跑后输入摘要，并确认一致；初始 1.93.1
检查的参照由已确认干净的起点 `7702429` 重建，明确区别于最终轮的实际快照。

最终完整检查结束后，仅更新 README 和 Rust 契约的最低版本说明；Rust 代码块不变。
随后对两套工具链重跑文档测试和文档构建，验证最终 README，避免将旧文档身份
表述为当前文档的新验证。代码及固定依赖与完整检查时保持一致。

P0、P2–P4 及 P5.1 原始 JSON 和受保护资源保持不变；旧报告绑定旧输入，
不为本轮修改重写其摘要或将其当作新的全量差分/性能测试。
本阶段没有重测性能或执行真实归档、独立打包消费、dry-run、上传和 crates.io 验收。
`publish = false` 与过渡 include 保留；当前 include 仍需 P5.3 按候选清单补齐。

验证范围限于本次 Windows x86_64 MSVC 及锁定依赖；未验证 Linux、macOS、其他目标
或未来依赖解析。打包和正式发布分别由 P5.3/P6 执行。

## 重现

最低版本检查使用项目隔离安装；工具链和 Cargo 依赖已经准备完毕后：

```powershell
$env:RUSTUP_HOME = Join-Path (Get-Location) '.local/p52-rustup-home'
$env:CARGO_HOME = Join-Path (Get-Location) '.local/cargo-home'
$env:CARGO_TARGET_DIR = Join-Path (Get-Location) '.local/p52-msrv-target'
rustup run 1.85.0-x86_64-pc-windows-msvc cargo check --offline --locked --all-targets --all-features
rustup run 1.85.0-x86_64-pc-windows-msvc cargo fmt --all -- --check
rustup run 1.85.0-x86_64-pc-windows-msvc cargo clippy --offline --locked --all-targets --all-features -- -D warnings
rustup run 1.85.0-x86_64-pc-windows-msvc cargo test --offline --locked --all-features
rustup run 1.85.0-x86_64-pc-windows-msvc cargo test --offline --locked --doc --all-features
rustup run 1.85.0-x86_64-pc-windows-msvc cargo doc --offline --locked --no-deps --all-features
```

当前 1.93.1 的检查在保留用户原有 `RUSTUP_HOME` 的独立进程中执行，使用
`.local/p52-stable-target`；不设置全局 override 或创建 rust-toolchain.toml。
