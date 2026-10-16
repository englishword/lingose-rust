# P6.3 crates.io 独立消费验收

**lingose 0.1.0 的正式注册表消费验收已完成，P0–P6 既定任务全部完成。**
本轮从提交 `621818a` 恢复，未再上传。原始命令、源码来源、校验和和 HTTP 证据见
[registry-consumer-verification.json](registry-consumer-verification.json)；可重复检查工具为
[check_registry_consumer.py](../tools/check_registry_consumer.py)。

## 独立工程与真实来源

在 checkout 之外新建临时工程：
`C:/Users/Threadman/AppData/Local/Temp/lingose-p63-385ffe1b2c49/consumer`。
使用新建且初始为空的 Cargo home，以及独立 target；没有复制根 Cargo.lock、
既有 registry cache、已发布候选或相邻项目数据。消费者只复制已固定身份的
`tools/package_consumer.rs` 测试程序，库和全部依赖由 Cargo 从 crates.io 下载。

消费者的依赖声明为：

```toml
[dependencies]
lingose = "=0.1.0"
```

独立 workspace 使用 edition 2024、rust-version 1.85、resolver 3。不存在 path、
patch 或 source replacement。Cargo metadata 显示 `lingose 0.1.0` 和另外十个依赖包
均来自 `registry+https://github.com/rust-lang/crates.io-index`，所有依赖源码路径均在
新临时 Cargo home 内；消费者自己使用单独生成的锁文件。

锁文件 checksum、新缓存中的真实下载、版本 API、sparse index 与 P6.2 正式发布摘要
一致，包大小为 **4,048,633 字节**，SHA-256：

`fb1a40407222053fa2acf6b92be99e59648d8e2a7ceac3c7f20182bbb393c6a8`

还逐文件比对 Cargo 解包源码与该下载归档。所有生产分发输入及 P5/P6.1/P6.2
历史收据前后保持不变；本轮没有读取或复制发布凭据。

## 构建与运行结果

依赖准备后运行以下三组验证，全部退出码为 0：

| 场景 | 构建方式 | 独立运行 |
| --- | --- | --- |
| Rust 1.93.1 正常消费 | `cargo build --locked --release` | 18 入口内容断言通过 |
| Rust 1.93.1 离线消费 | 全新 target，`cargo build --offline --locked --release` | 同上，输出相同 |
| Rust 1.85.0 离线消费 | 另一全新 target，同样 offline/locked/release | 同上，输出相同 |

本次实际平台为 **Windows x86_64 MSVC**。最低版本使用已隔离安装的 Rust 1.85.0，
未修改用户默认工具链；依赖来源仍为本轮新注册表缓存。

每次将已构建 exe 复制到独立运行目录执行；该目录仅有三个 exe，运行环境仅保留
Windows 系统变量、系统 PATH、临时目录和空 Cargo home。三次结果一致，运行时
Cargo home 保持为空。Cargo 的离线开关不等于操作系统级网络隔离，本轮未声称进行
文件访问审计或系统级断网。

复用的消费者逐项调用 18 个公开入口，覆盖四组大小写别名、IPA/IPS/ISM/IPSM、
词族、中英释义、分类/标签、完整 CET4 成员关系与边界样本、标注默认值与阈值、
未知词、大小写/Unicode/空白、参数错误及公开资源错误变体处理。
它是固定 Python 基线字面量的消费 smoke；不是全量差分、全表规范摘要或损坏包注入。
日志中的 `P5.3 packaged consumer passed` 是复用测试程序保留的原成功标记，
本轮 P6.3 来源和结果由新收据中的 registry/lock/cache 证据确定。

## 在线文档与外部链接

以下页面均取得 HTTP 200，并进行了目标内容检查：

- [正式 API 文档](https://docs.rs/lingose/0.1.0/lingose/)和
  [crate 页面](https://docs.rs/crate/lingose/0.1.0)。
- 14 个独立函数页面及首页四个大写重导出别名，共 18 个入口均可到达。
- [docs.rs 构建记录](https://docs.rs/crate/lingose/0.1.0/builds)。
- [官网](https://lingose.com/)和用户指定的 [GitHub 账号页](https://github.com/englishword)；
  正式文档中仍包含两处项目链接。

这是 HTTP 与内容检查，不扩展为浏览器渲染、GitHub 全部动态模块、未经指定的具体
Rust 仓库或其他平台运行验收。docs.rs 文档可用也不代替其他平台的运行测试。

## 记录与复核

- 完整成功原始收据：`.local/p63-registry-385ffe1b2c49/report.json`。
  同目录保留工具源码快照、11 条命令的 stdout/stderr、21 个成功 HTTP 响应及其摘要。
- 首轮 `.local/p63-registry-6fb1b94e8d16/report.json` 的所有构建和消费运行已通过，
  随后 GitHub 响应发生 `IncompleteRead`。该失败原样保留；工具加入最多三次
  传输重试后，在另一个全新工程/空缓存/target 完整重跑并通过。
- 成功轮的 Cargo fetch 也保留了两条 Schannel 连接中断重试警告，Cargo 自动重试后
  成功，退出码 0；不将结果描述为零警告。HTTP 检查本轮无传输重试。
- 独立只读复核已逐项核对 manifest、lock、metadata、新缓存、解包内容、工具快照、
  全部日志/响应摘要、三次构建/运行及历史输入身份，未发现实际不一致。
- 本轮未重跑全量差分或性能。P4.2 的 Windows 新路径首次启动超预算事实继续保留，
  不以发布或消费验收覆盖该历史限制。

需要再次验证时，在依赖工具链已具备的正常用户环境执行
`python tools/check_registry_consumer.py`；它总是新建临时工程和收据，不执行发布。
新版本或新增平台验证应单独立项，不再次上传已发布的 0.1.0。
