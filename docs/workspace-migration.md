# CLI1.1：双 crate workspace 迁移

从干净的 `5ae873d` 恢复，完成结构迁移；完整身份、命令和日志摘要见
[workspace-migration-verification.json](workspace-migration-verification.json)。
验证环境为 Windows x86_64 MSVC，默认 Rust/Cargo 1.93.1，另做 Rust 1.85.0 编译检查。

## 工程结构与身份

- 根改为 virtual workspace，正式成员及默认成员仅为 `crates/lingose`、
  `crates/lingose-cli`，两个包均为 0.2.0，共用根锁文件，resolver 为 3。
- 库的 src、完整 data、examples 和六个 Rust 集成测试文件迁入库目录。
  共 38 个文件逐字节一致，包含二进制词库、Unicode 表、生成向量和源码。
  库内相对布局保持不变，原 include_bytes/include_str 无需改动。
- Python 测试、P0 JSON fixture 与历史审计资料留在仓库根。
  根 LICENSE、SOURCES、Unicode 许可和历史来源摘要保留原文并复制到库包；
  CLI 也带原项目许可和来源声明。88 个不在变更范围内的原文件摘要不变。
- 根及两个开发探针的注册表依赖未变。差分/性能探针显式独立，
  依赖路径改到新库目录，其锁文件只改变本地 lingose 版本；原 profile 保留。
  layout 探针原独立 workspace 不变，三个探针均从正式 workspace 排除。
- Cargo include、.gitattributes 和当前 README/API 导航随新布局适配。
  库包文档说明 0.2.0 开发状态；根 API 原件只调整 manifest 链接。
  上游声明与其相邻 data/LICENSE 一起移动，原链接和摘要保持有效。

## 公开状态

[库](../crates/lingose/README.md)继续提供原有接口和数据。
本阶段未做函数更名，当前仍为 `annotate_ips_with_skip_top`，CLI2.1 再改名。
[CLI](../crates/lingose-cli/README.md)仅为脚手架，二进制叫 `lingose`，
运行时 stdout 为空、stderr 明确报告未实现、退出码为 1，不提供业务命令。

两个包均保留 publish=false；库在 CLI4.3、CLI 在 CLI6.3 完成相应验证后解除保护。
历史来源摘要仍绑定其原 0.1.0 锁文件，不是新 workspace 锁文件证明；
新版依赖/分发声明复核属于 CLI4.2。原发布收据及固定消费者未改。

## 实际验证

| 检查 | 结果 |
| --- | --- |
| 库 offline check | 通过 |
| workspace fmt / Clippy -D warnings | 通过 |
| workspace 测试 | 102 Rust + 5 文档通过，1 项原有手动探针忽略 |
| workspace 文档、CLI 构建 | 通过 |
| Rust 1.85.0 workspace 全目标/全部 feature offline locked check | 通过 |
| 正式成员及三个探针独立 metadata | 通过 |
| 差分/性能探针 offline locked check | 通过 |
| cargo package --list | 库 42 项、CLI 8 项，必要资源/许可齐全 |
| 仓库外库源码构建及独立 exe 运行 | query / annotate 两个示例通过 |

首次 workspace 文档构建因 bin/lib 同名出现输出路径碰撞。为 CLI bin 设置
doc=false，并在全新文档 target 重跑后无该警告；原日志保留。

仓库外验证使用独立临时源码目录，复用已准备的 Cargo 依赖；
锁文件为根锁副本，仅移除无关 CLI 条目。随后在只含两个 exe 的目录运行，
Cargo/Rustup home 为空。首次从临时目录查询 metadata 出现一次沙箱路径
canonicalization 警告，metadata 仍正确识别独立库；后续构建和运行通过。
此验证是源码目录自足性检查，不是归档、注册表或系统级断网/文件访问审计。

主要命令（先准备 Cargo 依赖，输出目录限本项目 .local）：

```powershell
$env:CARGO_HOME = Join-Path (Get-Location) '.local/cargo-home'
$env:CARGO_TARGET_DIR = Join-Path (Get-Location) '.local/cli11-check-target'
cargo check -p lingose --lib --offline --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features --offline --locked -- -D warnings
cargo test --workspace --all-features --offline --locked
cargo doc --workspace --no-deps --all-features --offline --locked
cargo build -p lingose-cli --offline --locked
cargo package -p lingose --list --offline --locked
cargo package -p lingose-cli --list --offline --locked
```

本次清单检查发生于提交前，实际加了 --allow-dirty；只检查清单，未生成真实归档。
完整 argv、初次文档警告及修正后日志保留于
`.local/cli11-workspace-b97b1a285c66/`，证据 JSON 固定其摘要。

## 下一项与验证边界

下一项是 [CLI1.2](../tasks/todo_CLI.md)：适配 Python 工具的仓库根/库根及路径假设。
本轮未运行这些尚未适配的工具套件，没有进行新全量 Python 差分、性能测试、
layout 候选构建、其他平台验证、真实 .crate/dry-run、上传或注册表安装。
既有首启超预算及历史许可处置依据继续按原记录解释。
