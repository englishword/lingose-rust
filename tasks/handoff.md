# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P5.3，真实归档、独立离线消费与发布预检（未开始）**。
- P5.2 已完成：Rust/Cargo **1.85.0** 和 **1.93.1** 的工程检查通过，声明 MSRV 保持 1.85。
- 分支 main，本轮起点 7702429，开始时工作区干净；聚焦提交及实施历史以 Git 为准。
- 唯一生产修改：src/data/image.rs 的版本错误 hex 诊断改用预分配 String + write!；
  保留原两位小写十六进制输出，解决 1.85.0 Clippy format_collect。查询/标注逻辑未改。
- Cargo.toml/lock、依赖、资源、派生表、原始许可和所有历史 JSON 未改。
- `publish = false` 及过渡 include 保留；真实归档、dry-run、上传尚未执行。

## 恢复所需文件

- [todo.md](todo.md)：既定后续阶段。
- docs/engineering.md、docs/engineering-verification.json：P5.2 方法、命令、平台/工具链、
  日志摘要与 SHA-256、最终输入身份、初次失败及修复、30 个受保护文件不变的证据。
- README.md、docs/rust-api.md：已同步 Windows x86_64 MSVC 下实际最低版本验证范围。
- docs/distribution-review.md：P5.1 的候选 include 和链接闭包；仍为 P5.3 操作依据。
  当前 include 缺少编译必需 data/*.bin，不能作为最终发布清单。
- SOURCES.md、data/SOURCES.json、data/manifest.json、data/UPSTREAM-SOURCES.md：
  来源身份和许可资料边界；不重写受保护生成记录或历史摘要。
- data/LICENSE 与根 LICENSE 相同，解决保留的 UPSTREAM-SOURCES 中 data/ 相对许可链接；
  third_party/unicode/LICENSE.txt 必须随派生表分发。

## 本轮关键验证

- 两套最终完整工程检查均通过、无 warnings：fmt、全目标/全 feature Clippy -D warnings、
  cargo test、显式 cargo test --doc、cargo doc。每套 102 Rust + 5 文档通过，1 忽略。
  忽略项仍为 P2.2 手动加载器冷进程探针；重复文档检查是同一 5 项，不累计新增覆盖。
- 1.85.0 另通过全目标 check 和两个实际示例；70 项现有 Python 测试通过。
- 原始记录：
  - .local/p52-msrv-checks/report.json：修复前 Clippy 失败；
  - .local/p52-msrv-checks/fixed/report.json：最低版本最终完整通过；
  - .local/p52-stable-checks/report.json：起始当前工具链通过及 Python 70；
  - .local/p52-stable-fixed/report.json：生产修复后当前工具链最终通过；
  - .local/p52-final-docs/report.json：最终文案的两套文档测试/文档构建通过。
- 最终完整轮分别保存实际跑前/跑后输入摘要并核对不变；随后仅 README 文案改变，
  Rust 代码块不变，已针对最终文档另复核。全部 Rust 输入与最后完整工程检查相同。
- 1.85.0 安装在项目 .local/p52-rustup-home；显式工具链准备首次 TLS 中断后，按官方
  版本清单分段下载、核对范围/长度/完整摘要，再由 rustup 校验安装。
  默认用户工具链仍为 stable/1.93.1，没有全局 override 或 rust-toolchain.toml。
- 本轮仅 Windows x86_64 MSVC 与当前锁定依赖；不代表 Linux/macOS/其他目标或未来解析通过。
- 未重测性能/重捕获全量差分；旧 P4/P5.1 证据保留原始身份，不当作当前归档新证据。

## 必须保留的边界

- P5.1 已核对 18 入口、署名及声明；官方链接仍为 https://lingose.com/ 与
  https://github.com/englishword，不编造更具体的仓库 URL。
- Frequency List 固定参考缺单独许可文本/派生分发条件记录，部分外部分类词表缺逐标签
  来源/许可资料；SOURCES 保留实际缺口，不以项目 CC BY 4.0 推定第三方授权。
  P6.1 需复核其处置状态，不能把保留声明写成已独立确认全部分发条件。
- P4.2 历史性能只在固定预热条件下通过；新路径文件首次执行 534.24 ms 超过
  300 ms 的事实保留，不能保证新文件首启延迟。旧正式性能工具会拒绝当前输入身份差异；
  不覆盖历史报告来消除拒绝。
- 所有相邻参考 checkout、安装源库和人工审核资料保持只读；正式 crate 不依赖这些路径。
- 打包、本地 dry-run、真实上传与 crates.io 消费验收分别记录，不互相替代。

## 下一步精确动作

1. 核对 Git、本交接与 todo，恢复 P5.3；工程验证已完成，不重新规划。
2. 先按 docs/distribution-review.md 修改最终 include，补齐两个生产二进制、manifest、
   来源声明、data/LICENSE、Unicode 许可及 README/SOURCES/Rust 契约所链接的叶文档。
3. 本阶段完整实现和工程检查条件已满足，可按既定计划移除 publish=false 保护，再执行
   cargo package --list 和真实 cargo package；核对实际归档文件、链接、必需资源和压缩体积。
   复核当时 Cargo/crates.io 官方大小规则，并分别检查 P1.2 固定的 .crate 预算。
4. 从真实解包内容建立隔离消费工程，不借用 checkout/Python 缓存/相邻仓库数据；准备
   Cargo 依赖后验证离线构建与全部公共 API，记录实际工具链和归档身份。
5. 执行 cargo publish --dry-run 并保留其实际结果；P5.3 只表示本地发布就绪，不上传。
6. 完成本阶段验证、更新 todo/handoff、聚焦提交，交接 P6.1 正式发布条件核对。
