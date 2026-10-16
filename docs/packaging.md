# P5.3 真实归档、独立消费与发布预检

`lingose` 0.1.0 的本地归档和发布预检已通过；这不是 crates.io 上传或注册表安装验收。
汇总与原始日志身份见 [package-verification.json](package-verification.json)。

## 真实归档

- `.crate` 实测 **4,052,577 字节**，41 个文件，SHA-256：
  `db227b4d53065bca47bf20bc5ea6d4987ff578fd9d3b0f8d98b5c6cda5b7d3ad`。
- 小于 P1.2 固定的 **5,000,000 字节**预算。2026-10-16 复核的
  [Cargo 官方发布说明](https://doc.rust-lang.org/cargo/reference/publishing.html)
  仍列出 10MB 上限；本轮同时用更保守的 10,000,000 字节数值检查，项目预算更严格。
- 最终 include 覆盖生产源码、两个完整二进制资源、manifest/来源声明、两个项目许可
  副本、Unicode 完整许可、示例与用户文档。逐文件核对 tar 内容、摘要和实际 Rust
  include 目标，21 个本地文档链接均在包内可解析。
- 不含维护数据库、缓存、Python/开发工具或本机绝对路径。P5.1 候选的三份开发 JSON
  含安装/缓存路径，改由新 [便携来源摘要](distribution-provenance.json)保留表、许可、
  生成器、解释器与依赖身份；历史 JSON 未改。原始来源身份及许可资料缺口继续保留。

打包在 `.local` 的逐字节核对源码快照中执行，快照没有 `.git`，因此未生成
`.cargo_vcs_info.json`。记录起点提交及每个源码输入的 SHA-256 作为来源身份，
不伪造干净 Git 提交。最终提交不改变候选字节；正式上传前仍须复核这些身份。
`Cargo.toml.orig` 与当前 manifest 一致，规范化 Cargo.toml 中没有本机路径依赖。

## 独立离线消费

消费工程在系统临时目录，从真实 `.crate` 解包，依赖路径只指向解包内容。
先从已有 Cargo 缓存准备 vendored 依赖，然后使用新的空 CARGO_HOME：

- Cargo metadata 中所有源码均位于隔离目录；没有借用当前 checkout、Python 缓存
  或相邻项目数据，空 CARGO_HOME 中没有 registry 缓存。
- Rust/Cargo 1.93.1 和 1.85.0 分别执行 `--release --offline --locked` 构建。
  生成的二进制复制到只有两个可执行文件的运行目录，两者输出相同。
- `tools/package_consumer.rs` 对全部 18 入口执行字面量内容断言，含别名、双语释义、
  大小写、未知/不可用、完整 CET4 词表及逐成员验证、Unicode、频率阈值和参数错误。
  资源错误的外部匹配用合成错误验证接口可用性，不冒充真实损坏资源注入。
- 另对真实包运行库测试、文档测试与文档构建，验证包内测试和文档闭包。
  80 项库测试与 5 项文档测试通过，1 项既有手动探针忽略，文档构建通过。

所有构建/消费步骤离线。开发期 Python 仅负责构造隔离环境和检查证据，正式 crate
和消费者运行不调用 Python，也不读取外置词库。

## dry-run 与执行环境

真实 `cargo publish --dry-run --locked --all-features` 已通过，生成的临时归档与
上述候选逐字节摘要相同。Cargo 输出 `aborting upload due to dry run`，没有真实上传。
该结果不证明账号权限、名称/版本可发布或服务端接受，P6.1 继续分别核对。

最初 `--offline` dry-run 因 Cargo 需要读取注册表 HTTP 元数据而失败；联网重试又遇到
沙箱 Windows Schannel 凭据错误。最终在正常用户环境对同字节、继承工作区读取权限的
快照执行成功。未关闭 TLS 校验或使用注册表替身；失败日志保留。
Cargo 当前将 dry-run 临时归档放在 `package/tmp-crate/`，已对真实文件核对，
未把先前 `cargo package` 的旧输出误当作 dry-run 新结果。

## 重现与后续

```powershell
python -I -B -X utf8 tools/prepare_package_sources.py --check
python -I -B -X utf8 tools/check_package.py
```

验证器每次创建新目录，保留旧 receipt。联网 dry-run 在能够正常使用 Windows TLS 的
用户进程中执行；打包/消费使用已准备的依赖并保持离线。新加的五项小型归档保护测试
覆盖路径穿越/链接/重复/多余文件、载荷身份变化、本机路径、断链及缺少必需资源。
现有加新增的 75 项 Python 测试、根工程格式和 Clippy 均通过。包内命令的 rustup
路径规范化环境提示保留在日志中，没有将其描述为零警告或改变数据/代码来消除提示。

`publish = false` 已按 P5.3 计划移除。正式上传属于 P6；必须先复核授权、账号/名称/版本、
归档身份和已记录的第三方许可资料缺口。若改变任一分发输入或从 Git checkout 重新
生成含 VCS 信息的不同归档，应形成新候选和验证记录，不能复用旧归档 SHA-256。
