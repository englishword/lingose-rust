# Lingose Rust 任务交接

## 当前恢复点

- 活动计划：[todo_CLI.md](todo_CLI.md)。**CLI6.4 进行中，不能勾选完成。** CLI6.3 已完成；本轮仅推进 CLI6.4。
- 从干净的 `main / ecbc7ce` 恢复；已准备 `.github/workflows/cli-release.yml`、`tools/publish_cli_release.py`、发布保护测试、`release/README.md`、`release/notes-v0.2.0.md`。当前提交以 Git 历史为准。
- [具体说明](../docs/cli-github-release.md)。仅指定仓库 v0.2.0 tag push 能发布，仅发布 job 有 contents:write；远端 public 与 tag SHA 检查先于任何 Release 写入。上传草稿后核对六个实际下载文件才正式发布；已有 Release 或中断须先检查远端，不覆盖、不自动重试。
- 本地 7 发布测试、7 归档测试、actionlint 1.7.12、Python 编译、fmt/空白检查与独立只读审查通过。正式五目标新候选尚待运行；旧 CLI5.2 run/摘要不代表本轮身份。

## 精确下一步

1. 提交已验证准备，推送 main 触发非发布五目标 CI；记录新的 commit/run、全部原生构建/打包/独立下载结果并下载核对候选与证据。
2. 仓库 `https://github.com/englishword/lingose-rust.git` 实时仍 private；账号 Prefee 有 admin/push/maintain，v0.2.0 tag/Release 均 404。**没有公开全部源码/历史的授权。** 完成可审查候选后向用户确认公开该仓库或另行指定公开分发处；不得擅自改可见性或以 private Release 冒充公开下载。
3. 可见性条件解决后，以候选提交建立 v0.2.0 tag，运行正式 tag Actions。重新核对最终构建身份、五包/SHA256SUMS、版本说明、实际上传与远端下载；失败先检查远端再恢复。
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
