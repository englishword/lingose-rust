# CLI4.2：0.2.0 用户文档与分发声明

从干净的 `main` / `7400e4d` 恢复，仅完成 CLI4.2。新版入口为根 README、
两包 README/SOURCES 和库内 `docs/rust-api.md`。命令、日志、依赖声明和输入摘要见
[验证收据](cli-user-documentation-verification.json)，原始材料位于 `.local/cli42-docs/`。

## 用户文档

- 根 README 提供 workspace 导航、安装/源码构建、查询/标注和库入门。
  两包 README 都指明 `https://lingose.com/` 与具体仓库地址，0.2.0 尚未发布；
  `cargo install lingose-cli` 和固定 0.2.0 安装示例明确是发布后用法。
- 库文档保留全部 18 个入口、独立发音列表、可空值、默认参数、精确词键与有条件
  小写回退、分类顺序、纯文本标注、错误和离线行为。新增可执行迁移示例，修正旧的
  `*_with_skip_top` 泛称；旧名称只在迁移说明/compile-fail 中出现，不恢复兼容别名。
- CLI 文档覆盖六字段 word、文本/文件自动识别、显式输入互斥、stdin、三种阈值
  语义、两字段 JSON、`-o`、help/version、UTF-8、退出码和部分写入边界。
  文件输入/输出避开 shell 重新编码；普通文本保留输入换行，JSON 则转义字符串换行。
- 采用 CLI4.1 的新版 Windows 验收声明，保留新路径首启超预算事实；没有把历史
  0.1.0 收据、本机执行、依赖图解析或源码示例写成归档/注册表/多平台已通过。

## 依赖与来源

两包 SOURCES 分别列出当前启用的依赖版本与本地 manifest 许可。五个计划目标使用
`cargo metadata --offline --locked --filter-platform TARGET` 分别解析，核对结果为：

| 目标 | 库外部依赖数 | CLI 外部依赖总数 |
| --- | --- | --- |
| Windows/Linux/macOS x86_64 | 9 | 18 |
| Linux/macOS aarch64 | 10 | 19 |

aarch64 多出的 `libc` 来自 `cpufeatures` 的条件依赖。这只是解析/声明检查，没有
交叉编译或目标机运行。保留 `version_check` 的原始 `MIT/Apache-2.0` 字段拼写。
未将锁文件中的禁用条件/feature 链全部称作编入二进制的依赖。

作者、Phonemizer/eSpeak NG/ECDICT、Frequency List 和 Unicode 署名均保留。
Frequency List 独立许可文本及部分外部分类逐标签来源/许可记录的既有缺口仍明确保留；
未取得新授权，也未用项目 CC BY 4.0 覆盖第三方许可。原 LICENSE、数据来源和许可、
Unicode 表/许可、历史 loader 和分发摘要均未改；新 CLI 依赖仅在新版声明/收据中记录。
未来独立二进制资产所需许可全文随 CLI5.2 检查，本轮没有制作资产。

## 实际验证

- `cargo fmt --all -- --check`、offline/locked workspace doc tests 和 doc 通过。
  Rust 1.93.1 与实际隔离 Rust 1.85.0 各通过 **7 项文档测试**，包含 3 项 compile-fail。
- 根 README 和 API 契约中额外的 **2 个 Rust 块**逐个编译、执行；现有 query/annotate
  两个库 example 实际执行。直接链接本次 checkout 构建的库，不称作独立归档消费者。
- 两个 README 中 **18 条去重后的 CLI 命令**实际执行；word 两格式的字段、数组和
  null 保持一致，标注纯文本/JSON/输出文件逐字对照直接库调用。另验未知词、参数缺失、
  非法单词、输入冲突、负阈值、缺失文件、空 stdin、i64 上限截顶及无效 UTF-8。
- **5 个 shell 场景**通过：PowerShell 字符串、UTF-8 Get-Content、Unicode；Git Bash
  的 cat 和 printf。PowerShell 输入另用原始 stdin 捕获器留证；本机即使设置无 BOM
  UTF-8 编码仍收到 BOM。宿主重新输出可能改变 CRLF，因此比较解码后的完整行；
  Git Bash 比较完整 UTF-8 字节。文件与直接库输出检查仍逐字进行，没有把 shell
  输出当作原文件字节完全保真的证据。
- 当前 Rust 业务源码、manifest、锁文件、数据、固定 P0、Unicode 及历史证据等
  **165 个范围外原文件摘要不变**。相对链接/显式锚点、包内链接边界、两包元数据、
  全部库入口覆盖和源码声明原有署名均核对；远端 URL 只核对配置，不据此声称可访问。

74 条命令均符合各自预期退出码。首次使用默认 rustup home 的 MSRV 调用遇到受限目录，
随后使用既有 `.local/p52-rustup-home` 中的实际 1.85.0；未下载或更换工具链。
额外 Rust 片段的首次手工链接缺少依赖搜索路径，补入构建的 `deps` 路径后通过。
PowerShell 对照最初假设无 BOM，捕获实际输入后改为按实际字节建立期望。这些都是
验证脚本准备/期望修正，没有修改产品代码或库输出。

本轮没有重复完整差分/性能、真实 `.crate`、dry-run、安装候选、上传或公开发布。
两包继续 `publish=false`。下一项为 **CLI4.3：库真实归档、隔离 CLI 候选及库 dry-run**。
