## 新任务

在 `../lingose-python` 项目中创建了 lingose python 模块，并且已经上传到了 PyPI。并且本地电脑已经通过 `pip install lingose` 安装了该模块 0.2.0 (与 0.2.1 版本数据相同)

同时完成 `../chrome-extension`，可在网页中对英文单词进行 IPS notation 标注。

同时完成了 `../lingose-typescript` 包，已经上传 npmjs.com ，包名为 lingose 与 @englishword/lingose （这两个包功能是相同的）

现在我需要开发一个 cargo 包，包的名称为 `lingose`，使用 Rust 开发，最后上传 crates.io  ，第一版版本号为  0.1.0，这样往后程序员或是AI开发时，假如需要对英语单词进行 IPSM 分析与显示，那么便可以直接调用该包。`../lingose-python/README.md` 中的函数都要实现，但 lookup() 函数不需要。 

考虑到运行时对速度有很高的要求，因此在开发 npm lingose 时，要考虑速度性能。

在 cargo 包页面要有 lingose.com 链接，github 链接 https://github.com/englishword，用户若想进一步了解，可以引导进入该网页继续学习。

