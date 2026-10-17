# 新任务

## Rust 项目采用 workspace

推荐：

```
lingose-rust/
│
├── Cargo.toml
│
├── crates/
│   ├── lingose/
│   │   ├── Cargo.toml
│   │   └── src/
│   │   └──       # 核心 IPSM library
│   │
│   └── lingose-cli/
│   │   ├── Cargo.toml
│   │   └── src/
│       └──       # CLI
│
└── ...
```

最终：

```
crates.io
   │
   ├── lingose
   │      └── Rust library
   │
   └── lingose-cli
          └── CLI
```

用户：

```
use lingose::...
```

或者：

```
cargo install lingose-cli
```

由于现有项目的结构不是这个结构，需要调整。

目前 lingose 0.1.0 已经发布到 crates.io  ，更新后以 0.2.0 重新发布。

    // 原来lingose以下这个函数名称过长，改成以下函数
    lingose::annotate_ips_skip(text, 1000)



### `lingose`

负责：

- IPS
- ISM
- IPSM
- annotation
- 数据结构
- 核心算法

### `lingose-cli`

负责：

- 命令行参数
- stdin/stdout
- 文件输入输出
- JSON 输出
- shell integration
- help
- error handling

------

CLI 不要做得太复杂，以简洁为主。

例如：

```
lingose annotate "This is an English word."
```

```
lingose annotate --skip-top 1000 "This is an English word."
```

```
lingose annotate input.txt
```

```
lingose annotate input.txt -o output.txt
```

------

加入 stdin

例如：

```
"hello world" | lingose annotate
```

或者：

```
Get-Content article.txt | lingose annotate
```

甚至：

```
cat article.txt | lingose annotate
```

以后 AI agent 就可以直接调用：

```
lingose annotate
```

------

增加一个 JSON 模式

例如：

```
lingose annotate "hello world" --json
```

得到：

```
{
  "text": "hello world",
  "annotate": "..."
}
```

---

```
lingose word hello --json
```

得到：

```
{
  "word": "hello",
  "ipa": "...",
  "ips": "...",
  "ism": "...",
  "ipsm": "...",
  "root_lemma": "..."
}
```

---

CLI 只需要：

```
word
IPA
IPS
ISM
IPSM
root_lemma
```

不要把：

```
中文释义
英文释义
词性
大量辅助字段
等等
```

全部带进去。

------

### 源码/包注册表

发布到：

crates.io

```
cargo install lingose-cli
```

同时建立：

GitHub Releases

发布： https://github.com/englishword/lingose-rust.git  GitHub Actions 自动构建 

```
lingose-v0.x.0-windows-x86_64.zip
lingose-v0.x.0-linux-x86_64.tar.gz
lingose-v0.x.0-linux-aarch64.tar.gz
lingose-v0.x.0-macos-x86_64.tar.gz
lingose-v0.x.0-macos-aarch64.tar.gz
```

---

进一步考虑：不过**没必要马上做**，放在最后。

```
winget install Lingose
```

或者：

```
scoop install lingose
```


