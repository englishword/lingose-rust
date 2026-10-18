# CLI6.4 GitHub Release

**已完成：在 private 仓库正式发布 v0.2.0，六个资产认证下载与候选逐字节一致。**

用户明确选择“目前以 private 发布 Release”。因此保持指定仓库 private，
验收范围为认证且有仓库权限的用户可查看和下载，不要求或声明匿名公开下载。

## 正式发布身份

- [Release v0.2.0](https://github.com/englishword/lingose-rust/releases/tag/v0.2.0)，ID `416347193`，
  正式接受时间 **2026-10-18 09:16:55 UTC**，非草稿、非预发布，发布者 `github-actions[bot]`。
- 注释 tag `v0.2.0` 对象 `9507ff12eac425612a7f9125ecdd65ffb7cb4095`，
  解引用提交 **`cf11a604c8f998a1b4ac67737b3e826cadd40530`**，全过程未移动标签。
- [正式 Actions 39114174841](https://github.com/englishword/lingose-rust/actions/runs/39114174841)，
  attempt 1 的五构建/五下载/汇总共 11 job 成功；attempt 2 仅重跑失败的发布 job 后全部 12 job 成功。
- [正式收据](cli-github-release-publication-verification.json)。最终原始证据在
  `.local/cli64-final-39114174841/`，六个正式下载在其 `release-downloads/`。
  首次失败完整证据在 `.local/cli64-ci-39114174841/` 与 `.local/cli64-publish-first/`。
  核验脚本 `.local/cli64-preparation/collect_final.py`。
- 前次 `1b7e62a / 39113070606` 的非发布候选与[旧收据](cli-github-release-verification.json)
  保留原字节，不将其摘要当成本次正式身份。

| 资产（共有前缀 `lingose-v0.2.0-`） | 字节 | SHA-256 |
| --- | ---: | --- |
| windows-x86_64.zip | 4,358,023 | `bf3d61609208c721d7e84b6ed44c91256385080c04ca6c7823f35e256a57b474` |
| linux-x86_64.tar.gz | 4,449,340 | `5adfe2aa6a3d9ff3ec3a091ace8e821d98e014193297118b4ecb99926481d287` |
| linux-aarch64.tar.gz | 4,433,406 | `572d85200121a0aac718e01fe7f6614adc4739caf6a012d7d1e2441d66715ca2` |
| macos-x86_64.tar.gz | 4,421,219 | `56e039f17e50a32a21d35dece6da20ce429dec8b4936565556e49a510191b4dd` |
| macos-aarch64.tar.gz | 4,482,603 | `28c1067255acc4bc3be023e976adf708b6885a1d0e53d144aae8d0bcf6d04755` |

第六个资产 `SHA256SUMS` 为 506 字节，SHA-256
`97c8dae2ccfb1bbbdf242c40199cfda1fa50ed75519af0b3951b6c1b675e2ac2`。
每包 46/48 文件，包含可执行文件、README、LICENSE、来源声明、manifest 及所需许可原文。

## 构建、上传与下载证据

[工作流](../.github/workflows/cli-release.yml)仅在指定仓库的精确 tag push 发布，
只有发布 job 具有 `contents: write`，其他 job 为只读；分支、PR、手动运行只生成候选。
[发布器](../tools/publish_cli_release.py)先核对 private 可见性、tag 提交及六文件闭合身份，
再保存创建意图、建立草稿、上传六文件、实际下载核对字节和包内身份，最后转为正式发布。
已有同标签 Release（含草稿）即停止，不覆盖资产，不自动重试。

- 五目标原生 release 构建：147 次 CLI 测试、35 次归档保护、35 次发布保护、60 次构建 smoke，
  隔离下载 job 的 80 次原生 smoke 全通过；其 checkout 没有 crates 或本地缓存。
- 两次发布共保留 19 份 service artifacts：17 份候选/验证资料，及失败/成功各一份发布报告。
  两份同名报告按创建时间和其内部 run_attempt 区分，不能假设数值 ID 按时间递增。
  全部 service ZIP 摘要、构建日志/实际二进制、57 build/54 packaging 输入及汇总报告已核对。
- 五个实际最终归档的 manifest 与 build/package/download 三份报告及实际构建二进制直接对应。
  许可/来源/安装说明、依赖、闭合载荷、架构、权限和提交身份均通过。
- CI 在草稿阶段下载核对全部六资产；正式发布后，本机以 Prefee 的既有 gh 登录再次下载六资产，
  核对远端 ID/状态/大小/digest，并与最终 CI 候选逐字节比较，全部一致。
  本项不将发布后的字节核验记作 CLI6.5 的二进制运行验收。
- 本地初始 7 发布/7 归档测试、actionlint 1.7.12、Python 语法、fmt、空白检查与独立审查通过；
  错误诊断修复后为 8 发布/7 归档测试。正式 tag 内运行的是当时的 7 项发布测试。

## 首次失败与恢复

attempt 1 发布 job `117637028824` 在创建草稿的 POST 失败。立即核对远端 releases 为空、
Release API404，失败报告没有 release_id；没有资产上传或已接受的 Release。
原脚本捕获后丢弃了服务端错误正文，因此无法断言其精确 HTTP 状态码；已在 main 修复诊断并补测。

当时远端 main 为 `8a2dc48`，其 workflow 与 tag 不同。
[GitHub Release API 规则](https://docs.github.com/en/rest/releases/releases?apiVersion=latest#create-a-release)
要求这类目标的令牌额外具备 workflow 写权限，而 GITHUB_TOKEN 无法取得该权限。
这是与本次现象相符的原因推断；保留其证据限制。
先将默认分支同步到 `b8eab21`，API 确认其 workflow 与 tag 同 blob
`0b50de0c2842f82b32ca88da3b368048f5e6ae19`，再次确认远端无 Release 后，
只重跑原失败发布 job。attempt 2 的 job `117637970533` 成功，最终仅创建一个 Release，上传六个资产。
没有改 tag、重新构建五平台或使用本地伪造 CI 身份。

一次只读 artifact 下载 EOF 保留不完整文件/错误后重取，最终匹配服务端摘要。
推送 main 返回重复 ref 竞态，但独立 API 确认远端已经是准确提交，未盲重推。
这些记录不覆盖首次发布失败或旧候选证据，凭据未进入仓库/日志。

## 阶段边界与下一步

未修改 Rust 源码、词库、固定向量、根锁、相邻参考仓库、已发布 crate 或其 README，
未重传任何 crates.io 版本。来源许可确认沿用既有处置，Frequency List/分类资料缺口继续披露。
Windows VCRUNTIME140/UCRT、Linux/macOS 系统动态库前提、macOS 未签名/公证、Gatekeeper/旧 OS 未验，
以及首启超预算事实仍保留在安装说明和版本说明中。

下一项 **CLI6.5**：新 cache 的注册表库消费者和 `cargo install lingose-cli --version 0.2.0 --locked`，
依赖准备后离线复跑；下载本次 private Release 并执行最终二进制运行验收。
本项只完成正式上传与认证下载身份核验，未提前执行 CLI6.5。
