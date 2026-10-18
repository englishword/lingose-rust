# CLI5.2：五平台二进制安装包与下载验收

本阶段生成带许可、说明和 SHA-256 的二进制候选，并通过独立原生 job 下载、解包、运行。
目前本地 Windows 打包和独立验证已通过，实际五平台工作流尚待提交后核验；此时不算 CLI5.2 完成。
结果见[机器可读收据](cli-binary-assets-verification.json)。

## 产物及内容

工作流继续使用[五平台原生矩阵](cli-release-ci.md)，固定 Rust 1.93.1，生成：

- `lingose-v0.2.0-windows-x86_64.zip`
- `lingose-v0.2.0-linux-x86_64.tar.gz`
- `lingose-v0.2.0-linux-aarch64.tar.gz`
- `lingose-v0.2.0-macos-x86_64.tar.gz`
- `lingose-v0.2.0-macos-aarch64.tar.gz`
- `SHA256SUMS`：按文件名排序的五行 SHA-256 清单。

每包只有一个与文件名主体相同的顶层目录，包含 `lingose[.exe]`、README、LICENSE、SOURCES、
`manifest.json` 及所需来源/许可全文。Windows/x86 Linux/macOS 共 46 文件，两个 aarch64 包共 48 文件；
差别为条件依赖 `libc` 的两份许可。不会把数据库、Cargo cache、Python 包或构建源码放入安装包。
包内 README 说明安装、查询、文本/文件/stdin、JSON、输出文件、help/退出码及平台前提。

## 许可与平台前提

- 全部 19 个相关 crates.io 包的许可文本从已固定 `.crate` 归档提取，先核验 Cargo.lock 的注册表摘要，
  再与准备好的 cache 文本逐字节比较。x86 目标的闭包为 18 个外部依赖，aarch64 为 19；
  构建期的 `version_check` 单列，不将锁文件内未启用的 proc-macro 依赖当作运行时闭包。
- 原有项目/data/Unicode 许可、UPSTREAM-SOURCES 和 SOURCES.json 原样保留。
  Rust 1.93.1 官方发行版的 `COPYRIGHT-library.html` 保留标准库及平台条件组件的完整声明；
  其范围见 [Rust COPYRIGHT](https://github.com/rust-lang/rust/blob/1.93.1/COPYRIGHT)。
- 新增 [ECDICT 完整 MIT 许可](../release/notices/licenses/ECDICT/LICENSE)，固定到
  [bc015ed2 的许可文本](https://github.com/skywind3000/ECDICT/blob/bc015ed2e24a7abef49fc6dbbb7fe32c1dadaf8b/LICENSE)，
  与原声明的 Copyright (c) 2025 Linwei 一致。该提交仅证明许可快照身份，不冒充原词库版本。
- [notice 清单](../release/notices.json)记录 44 项可用原文、源身份和 SHA-256。
  原文保留上游 CRLF、末尾空行和 HTML 空白；该目录用 `-text -whitespace` 保护，
  以源摘要核对，不为通过代码空白检查而格式化许可原文。
  Frequency List 缺少独立许可文本、部分分类词表缺少逐标签来源/许可的既有缺口继续保留；
  候选内容核验不表示所有第三方材料的再分发权限已解决。CLI6.1 仍须核对处置状态。
- Windows 候选保留已验证的 MSVC 链接方式，实际导入 `VCRUNTIME140.dll`，需要兼容的
  Microsoft Visual C++ v14 x64 Runtime、Windows/UCRT 系统组件；不捆绑微软 DLL。
  [微软运行库说明](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)给出官方安装要求。
- Linux 候选使用系统 glibc/libgcc_s/动态加载器；macOS 使用 libSystem，未提供 Developer ID 签名/公证。
  二进制头中的 OS/符号最低版本只是元数据，执行支持限于实际记录的 runner。

## 打包与独立验收

[打包器](../tools/package_cli_binary.py)仅用 Python 标准库：

1. 核对当前提交的成功构建报告、binary 身份及未变化的构建输入；离线核对实际目标依赖图、
   features、注册表摘要、许可文本和原始来源声明。
2. 验证真实 [PE/ELF/Mach-O 头](../tools/binary_format.py)、CPU 架构、导入库/加载器，写入包内 manifest。
   所有载荷都有字节摘要和模式清单，拒绝多余/缺失文件及错误身份。
3. 固定排序、提交时间、owner/group 和压缩头；同一 binary/输入连续编码两次必须逐字节一致。
   tar 中 binary 为 0755、文档 0644，zip 也写入明确模式。每包另生成 `.sha256`。
4. 独立下载 job 使用同架构新原生 runner，仅 sparse-checkout `tools` 与 `release`，
   显式断言没有 `crates` 和 `.local`。不安装 Rust，不准备 Cargo cache 或词库。
5. 下载 action 核对 CI artifact digest；验证器再核对内部 archive checksum、闭合载荷、
   所有许可原文、版本/提交、架构和权限。在 checkout 外解包，再将同一 executable 复制到单独的
   binary-only 临时目录运行 16 项逐字节 smoke，包含文件输入、Unicode 路径和纯文本/JSON 输出文件。
   原生执行、解包权限和上传是独立步骤；Windows 不宣称核验 POSIX 权限语义。
6. 仅在五个下载 job 全部成功后汇总五包，重新检查载荷/身份并生成总 `SHA256SUMS`。
   汇总 CI artifact `cli52-assets-COMMIT` 只有上述六个分发文件，验收报告另存。

拒绝路径穿越、错误根目录、重复文件、软/硬链接、错误权限和超界载荷；相应保护测试见
[test_cli_binary_package.py](../tests/test_cli_binary_package.py)。实际执行仍使用 OS 系统库；没有声称禁网、
干净 Windows 无运行库也能运行，或浏览器下载后的 macOS Gatekeeper 已通过。

## 当前验证及复跑

本地已通过 99 项 Python 测试、actionlint 1.7.12、Python 语法、fmt 和空白检查。
Windows release 构建的 29 项 CLI 测试和 12 项构建 smoke 通过；ZIP 重复编码一致，
另把验证器/notice/ZIP 复制到 checkout 外、无 crates/cache 的工程，16 项解包后 smoke 全部通过。
记录位于 `.local/cli52-build-final-local/`、`.local/cli52-package-final-local/`、
`.local/cli52-local-sourcefree/`。本轮未改 Rust 源码、核心数据、固定向量或 Cargo manifests/lock，
未重跑 CLI4 的全量差分、性能或注册表验收。

可手动触发非发布验证，下载最终候选：

```powershell
gh workflow run cli-release.yml --repo englishword/lingose-rust --ref main
gh run list --repo englishword/lingose-rust --workflow cli-release.yml
gh run download RUN_ID --repo englishword/lingose-rust --name cli52-assets-COMMIT --dir .local/cli52-assets-RUN_ID
```

当前仓库仍为 private，CI artifacts 保留 14 天并需要认证访问；本地证据应另行保留。
CLI5.2 不创建 tag、GitHub Release 或 crates.io 上传。正式 Release 上传、公开可访问性、
注册表安装和正式 Release 下载仍属于 CLI6，不能以本轮 CI 下载替代。
