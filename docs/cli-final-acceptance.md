# CLI6.5 注册表安装与最终 Release 运行验收

2026-10-18，Windows 11 x86_64 MSVC / Rust、Cargo 1.93.1 验收通过。
两包 `0.2.0` 的正式注册表消费及最终 Windows Release 下载运行已完成；
CLI6 结束，CLI7 winget/scoop 留待用户另行安排。

[独立收据](cli-final-acceptance-verification.json)记录完整来源和边界。
成功原始证据为 `.local/cli65-dc283d2151ac/report.json`；91 条命令均符合各自预期退出码，
182 份 stdout/stderr 日志的大小和 SHA-256 另行复核通过。

## 注册表来源与离线构建

实时检查 crates.io API 和索引，两版均未 yank，publisher 为 `Prefee`。
新下载的 Cargo cache 归档与正式发布收据一致：

| 包 | 归档字节 / 文件数 | SHA-256 |
| --- | --- | --- |
| `lingose 0.2.0` | 4,053,096 / 41 | `91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5` |
| `lingose-cli 0.2.0` | 16,498 / 7 | `3f2e31e77ac7bdcedecb90871597d9821f60119f437be9a2cd7c523faa894490` |

仓库外新消费工程只声明 `lingose = "=0.2.0"`，使用初始为空的独立 Cargo home。
锁文件由正式注册表解析生成；在线 release 构建及另一全新 target 中的
`cargo build --release --offline --locked` 均通过。

CLI 使用第二个初始为空的 Cargo home，从仓库外执行：

```powershell
cargo install lingose-cli --version 0.2.0 --locked --root <new-online-install-root>
cargo install lingose-cli --version 0.2.0 --locked --offline --root <new-offline-install-root>
```

两次安装使用不同的全新 target 和安装根；依赖准备后才离线执行。
`.crates2.json` 确认安装源为正式 crates.io。metadata 和锁文件检查确认库版本、
全部传递依赖注册表来源及源码路径位于相应新 cache，无 checkout path/patch，
未复制根锁文件、既有 cache、Cargo config 或凭据。Cargo 解包的两包每个文件
均与已验证的正式 `.crate` 原字节对应。

首次完整验收在离线 CLI metadata 阶段失败：宿主安装没有获取全平台依赖图中的
`libc 0.2.190`。失败收据 `.local/cli65-e756e643aa13/` 原样保留。
验收器增加明确记录的在线 `cargo fetch --locked`，并正确区分 CLI 锁文件根包与
带 checksum 的注册表依赖，再用两组全新 cache 完成第二次验收。
首次启动的 Python isolated-mode 导入问题亦已修正；没有更改已发布包。

## 最终 Release 与独立运行

通过既有 gh 认证刷新 [private v0.2.0 Release](https://github.com/englishword/lingose-rust/releases/tag/v0.2.0)
及六项资产，确认 Release ID `416347193`、发布时间、资产 ID/大小/digest、private 状态均未变。
注释标签 `9507ff12eac425612a7f9125ecdd65ffb7cb4095` 仍指向
`cf11a604c8f998a1b4ac67737b3e826cadd40530`。
本轮采用交接允许的方式：刷新远端身份后，复用 CLI6.4 已认证下载的六个正式文件，
重新核对全部 SHA 和 SHA256SUMS；没有重传、移动标签或修改仓库可见性。

Windows 正式 ZIP 内 `lingose.exe` 为 11,286,016 字节，SHA-256：
`4dc4476901165818992836459c76ee88f89a97508865e0fb4d60809ca739b3d6`。
其身份与 CLI6.4 候选和正式下载完全一致。本地注册表构建的可执行文件分别留有
自己的摘要，不要求它们与 CI 二进制逐字节相同。

运行前将消费工程、两组 Cargo cache、四个构建 target 和两个安装根移出原路径。
运行目录只提供五个可执行文件；PATH 仅含 Windows System32，运行用 Cargo home 保持空目录。
没有提供外部词库、Python、Node 或相邻项目文件；系统动态库仍可用，未声称有操作系统断网沙箱。

- 在线、离线库消费者各验证全部 **18 个公开函数**，包含四组大小写别名、新函数
  `annotate_ips_skip`、默认/指定语言和分类、完整 CET4 成员关系、Unicode、阈值及错误处理。
  两次完整输出相同。资源错误的公开类型处理是合成示例，不是词库损坏注入。
- 两份注册表安装 CLI 和一份最终 Release CLI，各 **25 项，共 75 项**通过：
  查询普通/JSON、未知词、help/version、四阈值、stdin、空输入、Unicode/CRLF、
  自动文件、显式文件、同名强制文本、纯文本/JSON 输出文件、缺失文件、无效 UTF-8、
  目录、负阈值、输入冲突及缺失参数。比较固定预期的完整输出、JSON 值及退出码；
  成功 stderr 为空，错误 stdout 为空，输入失败不截断现有输出文件。

独立复核重新解析保留日志中的固定输出，并实际检查隔离 cache、安装记录、
五个运行二进制与九个已隐藏构建路径。六项输出文件内容由 smoke 当场断言后清理，
事后独立日志复核可确认其 stdout 为空，未另行保留这六个临时结果文件。

## 平台范围与保留限制

| 平台 | 本轮 CLI6.5 | 带正式 tag 的既有 CI 证据 |
| --- | --- | --- |
| Windows x86_64 MSVC | 正式注册表在线/离线安装及最终 Release 25 项运行通过 | Windows Server 2022 原生构建与下载候选 16 项运行通过 |
| Linux x86_64 GNU | 最终归档身份复核，未在本轮运行 | Ubuntu 24 / glibc 2.39 原生下载候选 16 项通过 |
| Linux aarch64 GNU | 最终归档身份复核，未在本轮运行 | Ubuntu 24 / glibc 2.39 原生下载候选 16 项通过 |
| macOS x86_64 | 最终归档身份复核，未在本轮运行 | macOS 15.7.9 Intel 原生下载候选 16 项通过 |
| macOS aarch64 | 最终归档身份复核，未在本轮运行 | macOS 15.7.9 ARM 原生下载候选 16 项通过 |

上述既有 CI 为 run `39114174841` 的候选归档运行，五包与最终 Release 全字节一致；
不将其改写为本轮在其他系统执行了最终 Release。详情见[正式发布收据](cli-github-release-publication-verification.json)。
独立复核已重新检查六个正式下载、五个二进制头/摘要及 15 份 build/package/download 报告。

本轮没有改 Rust 源码、词库、固定向量、Cargo.lock、旧版工具或历史收据；验收结束时
248 个原有 tracked 文件摘要不变，随后仅更新当前说明与任务状态。
新验收脚本语法、既有 CLI package 两项保护测试及空白检查通过。
此次未重复全量差分、性能或 MSRV 1.85 验证，沿用并明确区分既有阶段证据；
CLI4.1 新路径首启超预算事实继续保留。
Windows VCRUNTIME140/UCRT、Linux/macOS 系统库前提，macOS 公证/Gatekeeper/旧 OS 未验，
Frequency List 与部分分类来源许可缺口继续沿用既有披露。

没有重复发布两个 crate，没有修改既有 Release，也没有自动推进 winget/scoop。
