# Lingose Rust 交接记录

## 当前任务与状态

- 当前任务：**P0.2，API 行为矩阵与固定 Python 对照样例（收尾核验中）**。
- P0.1 已完成：固定已安装 Python Lingose 0.2.0、实际缓存、源码/数据身份，完整审计与重复核验一致。
- 分支 `main`；P0 开始前工作区干净，起点为 `b99849a`。本次按 P0.1/P0.2 分别聚焦提交，实施历史以 Git 为准。
- 本轮只执行 P0，结束后停在 P1.1。尚未创建 Cargo 工程、导出 Rust 生产数据或进行 Rust 性能/发布验收。

## 相关文件

- [todo.md](todo.md)：剩余任务及依赖；[AGENTS.md](../AGENTS.md)：既定开发约束。
- [reference-baseline.md](../docs/reference-baseline.md)、[JSON](../docs/reference-baseline.json)：完整环境、路径、参考仓库状态、数据版本/摘要和审计结果。
- [reference.py](../tools/reference.py)、[audit_reference.py](../tools/audit_reference.py)：只读保护与可重复基线核验。
- P0.2 在工作区准备中的产物：`docs/api.md`、`tools/capture_api_vectors.py`、`tests/test_api_vectors.py`、`tests/fixtures/python-api-v1.json`。尚不能把旧样例文件当作补强后的最终结果。

## 已确定的决策

- `lingose` 0.1.0；随包提供完整必要数据，安装后离线使用；实现 README 的 14 个名称/10 种行为，排除公开 lookup/rank。
- 已安装 0.2.0 是数据/行为基线；相邻 0.2.1 的六个行为模块和两个分发数据资源与其一致，仅版本/别名导出不同。Rust 小写别名由适配层显式对照。
- 数据文件只读，拒绝 sidecar，不隐式恢复；临时规则/错误夹具与真实快照分开。相邻 TypeScript 已有任务文档差异只记录，不修改。
- 保持 https://lingose.com/ 与 https://github.com/englishword 链接；Rust 签名、最低版本和性能预算留给 P1。

## 已知环境与基线边界

- 已安装包位于 `D:\Python\Python312\Lib\site-packages\lingose`；实际查询库为现存用户缓存，不是相邻源码库，完整路径与摘要在 JSON 中。
- 50,335 个精确词键、24 类；频率 5,061 原始行、10,620 词键、上限 5062，保留 NUMBER=30 缺口。
- 安装代码/资源及相邻参考文件前后摘要不变；压缩 payload、15 表 schema/行数/带类型逻辑摘要及显式索引与缓存一致。两个库的完整性和外键检查通过。
- 开发环境为 Python 3.12.4；规划时工具链为 Rust/Cargo 1.93.1、Windows MSVC，不代表最低版本或跨平台验收。

## 验证与阻塞

- `python -I -B -X utf8 tools/audit_reference.py --write`：首次创建成功。
- `python -I -B -X utf8 tools/audit_reference.py --check`：完整重复审计通过，JSON/Markdown 均 unchanged。
- P0.1 的 7 项只读/拒绝恢复/拒绝覆盖/编码/版本解析保护测试通过。
- 含 P0.2 的当前 16 项测试均通过；首轮 310 样例已生成，复核后补强状态阻断与单字母词干夹具，最终候选正在 `.local/python-api-v1-reviewed.json` 重新生成。
- Rust/Cargo 检查尚未执行；不将 Python 对照准备视为 Rust 实现通过。没有已知业务阻塞。

## 下一步精确动作

1. 完成 P0.1 聚焦提交，仅包含基线工具、记录、测试、忽略规则及任务状态。
2. 等待/核对补强后的候选输出；仅更新尚未提交的 API 样例，再运行 `capture_api_vectors.py --check`，确认完整复现、14 名称覆盖及源摘要不变。
3. 完成 P0.2 文档/样例核对并单独提交；更新交接指向 P1.1 后停止。下次恢复时核对 Git 与任务状态，再建立 Rust 工程，不重新规划既定范围。
