# CLI2.1：阈值标注入口更名

从 `main` / `24a87fb` 恢复，仅完成 0.2.0 的公共入口更名。
命令、日志和保护文件摘要见
[annotation-api-rename-verification.json](annotation-api-rename-verification.json)。

## 破坏性变更

```rust
let annotate: fn(&str, i64) -> lingose::Result<String> = lingose::annotate_ips_skip;
assert_eq!(annotate("Abandon the book.", 5062).unwrap(), "Abandon the book.");
```

0.1.0 的 `annotate_ips_with_skip_top(text, skip_top)` 已移除，没有弃用或兼容别名。
调用方需要改用 `annotate_ips_skip(text, skip_top)`。
`annotate_ips(text)` 保留，继续调用零阈值入口。
参数类型、返回所有权、错误类型、算法、词库和资源加载顺序均保持不变。

当前根/库 README、库内 API 契约、示例、测试、三个标注向量生成器、
差分/性能探针及 `package_consumer_020.rs` 已同步。差分协议仍使用 opcode 17，
Python oracle 仍调用 `annotate_ips(skip_top=...)`，新报告使用新的 Rust 函数名。
新版消费者的说明和成功消息改为 0.2.0 API 消费，不把源码 smoke 称作归档验收。

## 验证及固定期望

- 新入口的 `fn(&str, i64) -> Result<String>` 编译通过。
  同一消费工程引用旧名称时，以明确的 `E0425` 拒绝编译。
  库 README 的旧名称 `compile_fail` 示例也已纳入持续文档测试。
- 90 项 Python 回归、102 项 Rust 测试及 6 项文档测试通过；
  1 项既有手动 loader 探针仍忽略。workspace fmt、Clippy `-D warnings` 和 doc 通过。
- 新名称沿用已有阈值向量和边界验证：负数、0、1000、5062、5063、
  `i64::MAX`、NUL、阈值校验先于 NUL、无英语词不加载资源、零阈值不加载频率、
  正阈值先频率后词库、完全屏蔽仍传播词库错误、缓存和并发。
- 三个受影响生成器的只读 `--check` 通过。9 个 Rust 文件与改名前副本独立比较，
  只允许入口/调用名及局部变量替换、rustfmt 排版和新版消费者说明/成功消息调整；
  所有固定预期字符串、阈值和错误断言保持原值。四个 Python 工具只改 Rust 名称。
- 隔离 release 回归的 7 个测试二进制通过；差分 smoke 的 881 项完整结果零差异。
  请求、Python 输出和 Rust 输出的字节摘要还与 CLI1.2 的 smoke 相同。
- 差分/性能探针各自以 release/offline/locked 构建；当前源码消费者的 18 个公共入口通过。
  库 `cargo package --list` 仍为 42 项。
- 138 个不在更名范围内的原文件逐字节一致，包含词库、P0 JSON、Unicode 表、
  原算法和资源测试、许可、历史消费者、0.1.0 契约及既有报告。

根 [0.1.0 契约](rust-api.md)与 P3/P4/CLI1 历史材料保留原文，
当前 README 引向[库内 0.2.0 契约](../crates/lingose/docs/rust-api.md)。
旧 `package_consumer.rs`、发布/注册表工具和收据未改。

本轮环境为 Windows x86_64 MSVC / Rust 1.93.1 / 固定 Python 3.12.4。
源码消费者引用当前 checkout，不是归档或注册表消费；未执行真实 `.crate`、dry-run、
发布、其他平台运行或完整新版性能验收。两包仍保留 `publish=false`，
CLI 仍为脚手架。下一项为 CLI3.1 的命令入口和单词查询。
