# CLI6.4 GitHub Release

状态：**用户已明确选择 private Release，正在执行正式 tag 发布；CLI6.4 尚未完成。**
尚未创建 `v0.2.0` 标签或 Release，也未修改仓库可见性。

从干净的 `main / ecbc7ce` 恢复。实时核对账号为 Prefee，对指定 origin
`englishword/lingose-rust` 有 admin/push/maintain 权限；仓库仍为 private，
标签和 Release API 均为 404。本项没有修改仓库可见性；公开全部源码与历史尚无授权。

[工作流](../.github/workflows/cli-release.yml)沿用五目标原生构建、独立下载运行和六文件汇总。
新增发布 job 仅响应指定仓库的 `v0.2.0` tag push，仅该 job 获得 `contents: write`。
普通分支、PR 和手动运行继续只产生候选。工作流与安装说明已变，必须生成新候选；
CLI5.2 的摘要与提交不作为本次构建身份。

[发布器](../tools/publish_cli_release.py)核对运行上下文、六文件集合、SHA256SUMS、
五个内部 manifest、架构、权限与全部许可/说明，以及用户指定的远端 private 可见性和 tag 解引用提交。
已有同标签 Release（包括草稿）立即停止，不覆盖资产。
先保存意图再创建草稿，上传六文件，逐个下载并核对服务端摘要、字节和包内身份，
成功后才转为正式发布。失败保存 Release ID 与状态；恢复须先核对远端，不能盲重试。
具体操作依据 [GitHub CLI 发布文档](https://cli.github.com/manual/gh_release_create)
与 [Release API](https://docs.github.com/en/rest/releases/releases)。

[版本说明](../release/notes-v0.2.0.md)及包内 README 已准备，保留系统运行库前提、
macOS 未签名/公证、旧 OS 未验、首启预算及第三方资料来源缺口。
不修改已发布 crate 的载荷、README、数据或注册表版本。

## 已完成的新候选验证

准备提交为 `1b7e62a7a03419586a09eb8b8cddf8396b91d518`；
[非发布运行 39113070606](https://github.com/englishword/lingose-rust/actions/runs/39113070606)
的五构建、五独立下载运行、汇总共 11 job 全部成功，发布 job 按预期跳过。
新收据见 [verification JSON](cli-github-release-verification.json)；原始 17 份 service ZIP、
API 响应及报告在 `.local/cli64-ci-39113070606/`，收据核验脚本在 `.local/cli64-preparation/collect.py`。

- 147 次 CLI 测试、35 次归档保护测试、35 次发布保护测试、60 次构建 smoke、
  80 次实际下载后原生 smoke 通过；下载 runner 没有 crates 或本地词库。
- 独立下载全部 17 份 artifact，逐一核对 GitHub service ZIP digest，实际构建日志/二进制摘要、
  57 个当前 build 输入及 54 个 packaging 输入均匹配。核对汇总报告、每目标归档与最终候选字节，
  从实际归档的 manifest 直接连接 build/package/download 三份二进制身份。
- 五包的闭合载荷、实际架构、权限、全部许可/来源/安装说明、依赖和版本/提交身份通过；
  仍为每包 46/48 文件。五个目标都已原生运行，但这不是正式 Release 下载验收。
- 本地 7 项发布保护测试、7 项归档保护测试、actionlint 1.7.12、Python 编译、fmt 与空白检查通过，
  独立代理只读审查通过。没有 Rust、数据、根锁或已发布 crate 载荷变化，未重复全量差分/性能。

可审查的六文件目录：
`.local/cli64-ci-39113070606/cli52-assets-1b7e62a7a03419586a09eb8b8cddf8396b91d518/`。

| 资产（共有前缀 `lingose-v0.2.0-`） | 字节 | SHA-256 |
| --- | ---: | --- |
| windows-x86_64.zip | 4,358,023 | `2f05412741738a447885ae91b4689dfd5e6561cc07cba6f764ebe01bce7bfbb6` |
| linux-x86_64.tar.gz | 4,449,337 | `7a2efc36a3774b4a3fcebaff8c9557386e14b0d3818ca675c093f8fa5e9a9e33` |
| linux-aarch64.tar.gz | 4,433,407 | `fe1d3788414845f1d06a461b93d3b424777f0d01920394bda9fad2d359b8a25e` |
| macos-x86_64.tar.gz | 4,421,219 | `b7ebee89b53d7e79720f657be8377cdc342a0dc5437fbb005150e6c4097ed8d2` |
| macos-aarch64.tar.gz | 4,482,610 | `e8dfd8c0a70c59afb7fb924364e00d6ac3fb57b09b2d22fc980ceba26c9bd1ef` |

`SHA256SUMS` 为 506 字节，SHA-256
`19589384fb39e57fae058394371529c54898d29e8e012abc0d404a3242141a42`。
这些是本轮候选摘要，不能写成正式 Release 上传或下载已通过。

默认 Git 凭据助手不能无交互提供账号，改用仅本次命令的 gh 凭据助手推送成功，
没有改全局配置或输出令牌。一份只读 artifact 下载遇 unexpected EOF；保留截断文件/错误后重取，
最终匹配服务端摘要。收据器的仓库 API 尾斜杠也已纠正；不涉及发布重试或远端写入。

## 精确剩余动作

用户随后明确指示“目前以 private 发布 Release”，据此沿用指定仓库并保持 private。
本项验收调整为有仓库权限的认证用户可访问 Release 与下载资产；不要求也不声明匿名公开下载。
发布器精确要求 private，不提供修改仓库可见性的代码。版本说明明确认证与仓库访问前提。

由于发布条件、workflow 和包内说明变化，`1b7e62a` 仅保留为前次准备身份；
`v0.2.0` 必须指向新的已验证实现提交。正式 tag Actions 重新完成五目标候选与下载验证，
再由发布 job 上传/复核，新增独立正式收据，不覆盖前次候选收据。
CLI6.5 新 cache 注册表名称安装和最终 Release 运行验收仍留下一项；
其中 Release 下载沿用用户选择的认证访问范围。
