# CLI3.2：文本、文件和 stdin 标注输入

从干净的 `main` / `fbb447f` 恢复，完成 `annotate` 子命令的输入和纯文本输出。
命令、日志摘要、输入/源码身份见
[cli-annotation-input-verification.json](cli-annotation-input-verification.json)，
原始日志及本轮辅助脚本在 `.local/cli32-input/`。没有新增或更新依赖。

## 输入和库调用

```sh
lingose annotate "This is an English word."
lingose annotate --skip-top 1000 "This is an English word."
lingose annotate input.txt
lingose annotate --input input.txt
lingose annotate --text "input.txt"
cat article.txt | lingose annotate
```

```powershell
"hello world" | lingose annotate
Get-Content article.txt | lingose annotate
```

位置参数、`--input`、`--text` 互斥；没有显式输入时完整读取 stdin 至 EOF。
位置参数用 `OsString` 保留原生路径，`--input` 用 `PathBuf`，`--text` 用字符串。
自动识别先 `symlink_metadata`：

- 现存实体进入文件分支，只允许普通文件或指向普通文件的符号链接。
  目录、其他实体、失效/循环链接、权限和读取错误均报错，不回退为文字。
- 不存在、无效路径名、路径过长或中间组件不是目录时，按文字解释。
  仅使用相关 ErrorKind 和窄范围 OS 错误码，不吞掉其他探测错误。
  Rust 1.85 尚无 `ErrorKind::InvalidFilename`，所以 Windows/Linux/macOS
  的非法/超长名称补充判断使用各目标的原始码。
- 自动文字分支必须是合法 Unicode，禁止有损转换；现存文件的原生非 UTF-8
  路径仍可读取。显式 `--input` 从不回退，`--text` 从不检查路径。

文件/stdin 按 UTF-8 一次读取完整文本，不去 BOM、不分行；一次调用
`lingose::annotate_ips_skip(&text, skip_top)`，不复制或改动标注算法。
`--skip-top` 为 i64，默认 0；负数验证和 5062 上限处理交给库。
结果通过 `write_all`/`flush` 写 stdout，不追加换行。读取成功、库调用成功后才写结果，
参数或输入失败不会输出部分标注。参数/库参数错误退出 2，I/O/资源错误退出 1。
现有 word 的普通/JSON 输出和 help/version 保持原行为。

## 当前验证

- Windows x86_64 MSVC / Rust 1.93.1：4 项 CLI 单元测试、8 项 word 进程测试、
  8 项 annotate 进程测试全部通过；workspace 合计 122 项 Rust 测试、6 项文档测试，
  1 项既有手动 loader 探针仍忽略。fmt、Clippy `-D warnings`、doc 及 15 项工具
  Python 回归通过。
- 独立 target 下用 Rust 1.85.0 实际编译并通过相同的 20 项 CLI 测试。
  构建/测试使用已有 Cargo cache，均为 offline/locked；依赖和根锁文件未改。
- 直接文字、显式文字、位置文件、显式文件和 stdin 均与库完整结果逐字比较，
  包含空输入、Unicode/组合符、BOM、LF/CRLF/CR、尾部空白、标点、词形与未知词。
  `the\napple` 样例独立确认逐行调用会产生不同结果，防止测试漏掉跨行上下文。
- 验证同名文件/文字、长文字、Windows 非法路径字符、前导连字符、三种输入互斥、
  负数/非法/溢出阈值、0/1000/5062/5063/i64::MAX、缺失文件、目录、无效编码、
  文件/stdin 内 NUL、Windows 独占锁定文件和关闭 stdout。部分读取后失败另有合成
  Read fixture，确认退出 1 且 stdout 为空。
- 固定 P0 中 52 项成功且阈值可用 i64 表示的标注 snapshot，经空目录中的 CLI stdin
  完整逐字比较，零差异；阈值包含 0/1/29/30/31/1000/5061/5062/5063。
  `snapshot-0260` 使用 Python 任意精度大整数，超出现有 Rust i64 契约，明确排除，
  没有修改期望值或用截断阈值冒充原调用；CLI 溢出参数拒绝另有进程测试。
- PowerShell 5.1.26100.9444 的字符串、Get-Content、Unicode 管道及 Git for Windows
  Bash 5.2.37 的 cat、printf、多行/Unicode 管道共 6 项通过。
  PowerShell 实测传入 UTF-8 BOM 和 CRLF；先捕获该管道实际 stdin，再与直接文本
  调用对照，输出按 PowerShell 重发的行比较。Bash 按字节比较，并启用 pipefail、
  明确其 `/usr/bin:/bin` 路径。CLI 输入保真不等于 shell 会原样转发文件字节；
  需要保留原文件字节时使用 `--input`。
- 独立只读代码/状态复核通过；156 个范围外原有受控文件逐字节不变，包含整个库、
  数据/向量、Unicode 表、许可证、锁文件、探针、历史收据与报告。

Unix 原生路径、普通/失效/循环 symlink 的专用测试已写入，但本轮 Windows 未执行；
Git Bash 管道运行的仍是 Windows 二进制，不代表 Linux/macOS 目标机验收。
P0 对照没有重新运行 Python oracle；空目录运行不代表打包或注册表消费。
完整新版差分/性能/workspace MSRV 仍留 CLI4.1。

本轮没有实现 `-o` 或标注 JSON，没有执行真实打包、dry-run、远端操作或发布；
两包仍为 `publish=false`。下一项 CLI3.3 完成输出文件、标注 JSON 及完整 shell 错误契约，
包括失败时不截断既有输出文件。
