# CLI6.4 GitHub Release

状态：准备与非发布验证中，尚未创建 `v0.2.0` 标签或 Release。

从干净的 `main / ecbc7ce` 恢复。实时核对账号为 Prefee，对指定 origin
`englishword/lingose-rust` 有 admin/push/maintain 权限；仓库仍为 private，
标签和 Release API 均为 404。本项没有修改仓库可见性；公开全部源码与历史尚无授权。

[工作流](../.github/workflows/cli-release.yml)沿用五目标原生构建、独立下载运行和六文件汇总。
新增发布 job 仅响应指定仓库的 `v0.2.0` tag push，仅该 job 获得 `contents: write`。
普通分支、PR 和手动运行继续只产生候选。工作流与安装说明已变，必须生成新候选；
CLI5.2 的摘要与提交不作为本次构建身份。

[发布器](../tools/publish_cli_release.py)核对运行上下文、六文件集合、SHA256SUMS、
五个内部 manifest、架构、权限与全部许可/说明，以及远端 public 可见性和 tag 解引用提交。
已有同标签 Release（包括草稿）立即停止，不覆盖资产。
先保存意图再创建草稿，上传六文件，逐个下载并核对服务端摘要、字节和包内身份，
成功后才转为正式发布。失败保存 Release ID 与状态；恢复须先核对远端，不能盲重试。
具体操作依据 [GitHub CLI 发布文档](https://cli.github.com/manual/gh_release_create)
与 [Release API](https://docs.github.com/en/rest/releases/releases)。

[版本说明](../release/notes-v0.2.0.md)及包内 README 已准备，保留系统运行库前提、
macOS 未签名/公证、旧 OS 未验、首启预算及第三方资料来源缺口。
不修改已发布 crate 的载荷、README、数据或注册表版本。

本地 7 项发布保护测试、7 项归档保护测试、actionlint 1.7.12、Python 编译、fmt 与空白检查通过；
独立代理只读审查通过。五平台新运行结果待补录。CLI6.5 注册表名称安装和最终下载运行未执行。
