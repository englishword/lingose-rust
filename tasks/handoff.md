# Lingose Rust 交接记录

## 当前任务与状态

- 当前恢复任务：**P0.1，审计并固定参考代码、安装包和数据基线（未开始）**。
- 本次已完成 D0.1：依据 TASK.md 建立并核对项目规范、任务清单与初始交接；Rust 工程、数据导出、测试、性能验收和发布均未开始。
- 当前分支：`main`。实施前仓库干净，唯一提交为 `82fa60d TASK init`，跟踪文件仅 TASK.md，tasks 目录为空。
- 本次只处理文档准备，不自动继续 P0 或创建 Cargo 工程；变更仅含下列三个文档，提交状态和实施历史以 Git 为准。

## 相关文件

- [TASK.md](../TASK.md)：用户需求。
- [AGENTS.md](../AGENTS.md)：保留 Standard Workflow，并补充 Rust/API/数据/性能/发布约束。
- [todo.md](todo.md)：按 P0–P6 划分的执行清单，包含依赖、产物与验收。

## 已确定的决策

- Rust 库名 `lingose`，首版 `0.1.0`，最终上传 crates.io。
- 完整实现 Python README 中的公共函数与四组大小写别名，排除 lookup；内部排序仍保留必要的 rank 数据。
- 用户选择随包提供完整必要数据，安装后无需额外下载或配置即可离线使用。
- 只导出查询和标注需要的数据；不把 Python 完整来源/审核数据库直接塞入 crate。
- 数据与行为使用已安装 Python Lingose 0.2.0；用户确认其与 0.2.1 数据相同，后者的 README 用于补齐别名范围。
- 相邻 Python、TypeScript 和扩展项目只读，不改动其中已有工作区变更。
- Cargo 元数据及 README 均链接 https://lingose.com/ 和 https://github.com/englishword。
- TASK 中关于“npm lingose”的性能表述应用于本 Rust crate；性能预算在 P1.2 经实测固定。

## 已知环境与基线边界

- 规划时检查到 `rustc 1.93.1`、`cargo 1.93.1`，活动工具链为 `stable-x86_64-pc-windows-msvc`；最低支持版本尚未决定或验证。
- 已安装 Python 包位于 `D:\Python\Python312\Lib\site-packages\lingose`，版本为 0.2.0；该版本没有四个小写别名。
- 安装包 lexicon.lpk 为 89,292,019 字节，frequency.sqlite 为 1,929,216 字节；TypeScript 必要数据有精简投影可参考。
- 上述为本次规划时的环境观察，不替代 P0.1 的实际查询库、源码和数据摘要基线；没有运行完整数据审计或 API 验收。
- 相邻仓库若触发 Git ownership 检查，使用命令级 `git -c safe.directory=<明确路径> -C <路径> ...` 只读检查，不修改全局 Git 配置。

## 验证与阻塞

- 已完成：需求文件、Git 状态和参考 README/接口文档阅读；数据分发决策已确认。
- 文档检查通过：UTF-8 无 BOM、本地链接存在、行尾空白检查、需求/API 覆盖、13 条 Standard Workflow、14 个公共名称及 20 个唯一任务编号。仅 D0.1 勾选完成，所有 P0–P6 任务保留未完成。
- 尚未执行 Cargo 编译、测试、基准、打包或发布；当前没有 Cargo.toml。
- 没有已知业务阻塞。首次正式基线审计仍须确认现存缓存可读；不能把缺失数据库当作空词库。

## 下一步精确动作

1. 核对 Git 状态、分支、相关最近提交、本交接和 todo，恢复 P0.1，不重新设计已确认的项目范围。
2. 确认已安装 Python 0.2.0 的源码与资源位置、现存实际查询缓存和频率库；只读审计并固定版本、schema、记录数及摘要，形成可重复的基线核验工具和记录。没有缓存时只恢复至本项目隔离目录。
3. P0.1 验证通过后更新状态和交接并聚焦提交；不要把本次环境观察当作已完成的完整基线审计。
