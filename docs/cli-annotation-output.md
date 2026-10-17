# CLI3.3：标注 JSON、输出文件与 shell 错误契约

恢复时 HEAD 为 `0802ff6`，交接仍指向 CLI3.3，工作区已有 main.rs 和 annotate.rs
未提交草稿。原草稿另存 `.local/cli33-output/resume-start.json` 指向的字节副本；
接续修复测试类型推断及关闭 stdout 的测试竞态，完成本小节验证。
命令、日志与输入身份见 [cli-annotation-output-verification.json](cli-annotation-output-verification.json)。

## 输出与前置失败

```sh
lingose annotate input.txt -o output.txt
lingose annotate "hello world" --json
lingose annotate --input input.txt --json -o output.json
printf 'the\napple' | lingose annotate --json
```

- `--json` 严格输出一个只有 `text`、`annotate` 两个字符串字段的 JSON 对象。
  `text` 保存完整原文；Unicode、BOM、原始换行、引号及控制符经 JSON 转义后可无损解析。
  JSON 使用缩进并带末尾换行；纯文本始终直接写库返回字节，不追加换行。
- `-o PATH` 接受原生路径，写所选格式；成功时 stdout 为空。父目录须存在，已存在文件
  会覆盖；默认输出仍为 stdout，没有新交互界面或 shell 插件。
- 完成参数解析、完整 UTF-8 输入读取和一次 `annotate_ips_skip` 调用后才创建输出文件。
  参数、输入或标注失败不创建新输出、不截断既有输出；输入/输出可以是同一路径。
  文件写入开始后的 I/O 失败可留下部分文件，不承诺原子替换或回滚。
- 结果只到所选目标，诊断只到 stderr。参数/库参数错误为 2，I/O/资源错误为 1，
  成功、合法未知词、help/version 为 0。写入和 flush 的失败均传递到执行错误。
  help/version 在读取输入和创建输出前返回。
- CLI 仍只调用库，不改算法/数据/公共 API、依赖或锁文件。word 普通/JSON 仍只有
  六个指定字段；各输入模式、阈值和 UTF-8 规则沿用 CLI3.2。

## 验证范围

新进程检查覆盖五种输入的两字段 JSON、空输入、Unicode/BOM/LF/CRLF/CR、控制符转义、
纯文本与 JSON 写入新/旧文件、输入输出同路径、参数/输入/标注失败保护、无效编码、
缺失父目录/目录输出、Windows 独占锁、关闭 stdout 和 help/version 不触碰输出。
关闭管道的测试先关闭 stdout，再向 stdin 写入并关闭，确保子进程开始写结果前管道已关，
避免依赖调度时序。部分读取失败与写/flush 失败是明确的合成 I/O fixture；资源错误
只在单元层检查两种公开变体的退出码，没有伪造真实损坏词库的 CLI 注入。

Windows x86_64 MSVC / Rust 1.93.1：workspace 131 项 Rust 测试、6 项文档测试通过，
1 项既有手动 loader 探针仍忽略；fmt、workspace Clippy -D warnings 和 doc 通过。
Rust 1.85.0 在独立 target 目录实际通过 29 项 CLI 测试（4 单元、17 annotate、8 word）
及 CLI Clippy。PowerShell 5.1 与 Git for Windows Bash 5.2 的 4 项新检查通过：
ConvertFrom-Json / Python json.load 解析两字段对象，以及 JSON 文件输出且 stdout 为空。
shell 结果对照同一二进制的直接文本输出，Rust 进程测试另外逐字对照库调用。

158 个范围外原文件摘要不变，包括整个库、保护数据/P0 向量、Unicode 表、许可证、
manifest/锁文件、探针和历史证据。完整命令、日志摘要、计数及保护清单见验证 JSON。
Windows 下未运行 cfg(unix)
的原生非 UTF-8 路径和 symlink 项，不能据此声称 Linux/macOS 验收。
本小节不重复 Python oracle、长文本全量差分或性能预算测量，也没有打包、dry-run、
上传或远端操作；这些按 CLI4 及后续阶段执行。两包保持 `publish=false`。
