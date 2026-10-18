# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)。**CLI6.4 进行中，不能勾选完成。** 用户已明确“目前以 private 发布 Release”；本轮继续完成正式发布，保持仓库 private，不再等待公开源码/历史授权。
- 从干净的 `main / ecbc7ce` 恢复；已准备 `.github/workflows/cli-release.yml`、`tools/publish_cli_release.py`、发布保护测试、`release/README.md`、`release/notes-v0.2.0.md`。当前提交以 Git 历史为准。
- [具体说明](../docs/cli-github-release.md)。仅指定仓库 v0.2.0 tag push 能发布，仅发布 job 有 contents:write；远端 **private** 与 tag SHA 检查先于任何 Release 写入。上传草稿后核对六个实际下载文件才正式发布；已有 Release 或中断须先检查远端，不覆盖、不自动重试。
- 准备提交 `1b7e62a7a03419586a09eb8b8cddf8396b91d518` 已推至 origin/main；非发布 run `39113070606` 五构建/五独立下载/汇总 11 job 全成功，发布 job 跳过。147 次 CLI 测试、35 次归档/35 次发布保护测试、60 次构建/80 次下载原生 smoke 通过。全部 17 份 service ZIP 摘要、实际日志/二进制、57 build/54 packaging 输入及五包内许可/说明/架构/权限身份通过。
- 本地 7 发布测试、7 归档测试、actionlint 1.7.12、Python 编译、fmt/空白检查与独立只读审查通过。[新收据](../docs/cli-github-release-verification.json)，原始证据 `.local/cli64-ci-39113070606/`，核验脚本 `.local/cli64-preparation/collect.py`。旧 CLI5.2 run/摘要不代表本轮身份。

## 精确下一步

1. 本轮从干净 `main / 8a2dc48` 恢复，已实时确认 origin/main 同提交、仓库 private/admin、tag/Release 均 404。更新发布器精确允许 private，拒绝其他可见性，并更新测试/workflow/说明。本地 7+7 测试/actionlint/fmt/语法/空白通过；提交该实现后 **v0.2.0 指向新提交，不再使用 1b7e62a**。
2. 推送正式 tag 触发五目标 Actions，记录准确 commit/run，候选/全部原生运行/草稿上传/远端下载核验均通过后才标记完成。旧非发布候选保留为历史，不覆盖旧收据。
3. 用户已授权 private Release；仅认证且有仓库权限的下载作为本项验收。仓库可见性不改，无匿名公开下载声明。失败或中断先检查远端实际状态，保留所有尝试记录，不重复创建/覆盖已有 Release。
4. 完成后更新计划/说明/收据/交接并聚焦提交，交接 CLI6.5；本轮不执行新 cache 注册表名称安装验收。

## 已发布版本：禁止重复上传

- `lingose 0.2.0`：2026-10-18 07:43:13.810692 UTC 接受，41 文件/4,053,096 字节，SHA `91e164e14d3244e72de29343f9709237fe6072ae56ffaaf48f5d27999228bea5`；上传后连接断开但远端成功，仅上传 1 次。收据 `docs/cli-library-publication-verification.json`，原始证据 `.local/cli62-7578b10/`。
- `lingose-cli 0.2.0`：2026-10-18 08:36:22.922509 UTC 接受，7 文件/16,498 字节，SHA `3f2e31e77ac7bdcedecb90871597d9821f60119f437be9a2cd7c523faa894490`。第一次 403 后核实未发布；用户更新 cargo login 后第二次成功，仅一次接受。收据 `docs/cli-cli-publication-verification.json`，原始证据 `.local/cli63-91cd10a/`。
- 上述两版及 lingose 0.1.0 均不得重传。发布载荷/README、旧版消费者与历史收据保持原字节。
- CLI6.3 真实归档隔离安装已通过，但不等于 CLI6.5 注册表名称安装验收。

## 保留边界

- 不改 Rust/数据/根锁或相邻参考仓库，不执行 CLI6.5。许可与数据用户确认沿用已有记录；Frequency List 与分类资料缺口继续披露。
- Windows VCRUNTIME140/UCRT、Linux/macOS 系统动态库前提，macOS 公证/Gatekeeper/旧 OS 未验及 CLI4.1 首启超预算事实保留。
- 凭据只由 gh 使用，不写入日志/收据。普通沙箱无法读取 gh 配置；获准的外部只读检查成功。没有绕过审批。
- 默认 Git 凭据助手未能无交互推送，改用单次 gh helper 成功，无全局配置变化。一份 artifact unexpected EOF 保留截断/错误后重取且摘要通过；收据器 API 尾斜杠已纠正。全部为准备/只读采集，没有 Release 上传尝试。
