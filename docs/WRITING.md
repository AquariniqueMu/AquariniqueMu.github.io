# Junwen'Log 写作与发布手册

本地项目：`/Users/junwenyang/Developer/Projects/junwen-log`  
线上地址：[Junwen'Log](https://aquariniquemu.github.io/)  
推荐编辑器：已经安装的 Obsidian；MWeb 也可以直接编辑相同的 Markdown 文件。

## 1. 日常使用：新建 → 写作 → 预览 → 发布

桌面 **Junwen Log** 文件夹里有四个入口，实际应用位于 `~/Applications/Junwen Log/`。可以把常用应用拖到 Dock。

| 应用 | 操作 |
| --- | --- |
| **New Draft** | 选择 Technology / Reading Notes / Travel，输入标题和英文链接名，创建草稿并在 Obsidian 打开。 |
| **Open Writing Vault** | 打开博客的 Obsidian 写作库。 |
| **Preview** | 启动本地预览并打开浏览器；包括草稿，保存文章后自动刷新。 |
| **Publish** | 选择一篇草稿发布，或只发布已保存的网站修改；自动验证、提交、同步、推送，并等待 GitHub Pages。 |

发布前在编辑器保存文件。发布进行中先不要继续修改文件，避免把尚未写完的内容包含进同一次提交。发布完成会出现系统对话框；已确认 Pages 成功时自动打开线上站点。

**Publish 只把所选草稿的 `draft: true` 改为 `false`。** 选择 “Publish saved site changes” 时不修改任何草稿标记。其他草稿仍不会出现在公开网页。已发布文章的修改也会一起提交。

## 2. Obsidian 初始配置

首次使用时，在 Obsidian 的管理库界面选择 **Open folder as vault / 打开文件夹作为仓库**，选择：

```text
/Users/junwenyang/Developer/Projects/junwen-log/content
```

这是博客专用写作库，可以与其他个人库并存。脚本不修改 Obsidian 的全局配置文件；新电脑或移动项目后需要重新用界面选择这个文件夹一次。之后启动器通过 Obsidian URI 自动打开文章。

博客库已提供局部设置：

- 使用系统浅色/深色主题、17px 正文字号、舒适行宽。
- 使用标准 Markdown 链接，采用相对于当前文章的路径。
- 图片粘贴或拖入文章后，保存到该文章所在文件夹。
- 启用文件列表、搜索、大纲、字数等内置功能；不安装社区插件。

`content/.obsidian/` 是本地编辑器设置，不提交 GitHub。Obsidian 中的数学预览与 Hugo 最终的 MathML 排版可能略有不同，**以 Preview 中的实际网页为准**。

Obsidian 官方说明：[URI](https://obsidian.md/help/uri)、[附件位置](https://obsidian.md/help/attachments)、[链接设置](https://obsidian.md/help/settings)。URI 的 `path` 在已注册的库中查找文件，因此第一次注册必须完成。

## 3. MWeb 写作

MWeb 已安装。可以在 MWeb 的外部文件夹模式中添加上面的 `content` 文件夹，也可以用下面的命令直接打开文章：

```sh
cd /Users/junwenyang/Developer/Projects/junwen-log
./scripts/blog open content/notes/my-reading-note/index.md --editor mweb
```

不要另建一份文章导出再覆盖原稿，直接编辑博客目录中的原文件即可。MWeb 的预览、图片管理设置不替代本站构建流程；线上发布统一使用 **Publish**。

## 4. 文章、目录和图片

三个分区都是 Hugo page bundle：一篇文章占一个文件夹，正文是 `index.md`，图片就在旁边。

```text
content/
  posts/learning-rust/index.md
  posts/learning-rust/diagram.png
  notes/a-book-worth-remembering/index.md
  travel/a-weekend-in-hangzhou/index.md
  travel/a-weekend-in-hangzhou/lake.jpg
```

分区含义：`posts` 技术文章，`notes` 读书笔记，`travel` 游记。标题和正文可以写中文，文件夹使用英文小写、数字和短横线；发布后尽量不改文件夹名称，否则网址会变。

新建稿件已经包含以下 front matter：

```yaml
---
title: "一个值得记录的想法"
slug: an-idea-to-remember
date: 2026-09-16T12:00:00+08:00
draft: true
description: ""
tags: []
contentLanguage: zh-CN
---
```

`description` 写一句文章简介；`tags` 可以改成 `[Hugo, Writing]`。日期自动使用上海时区（UTC+8）。`contentLanguage` 是文章语言元数据，取 `en` 或 `zh-CN`，**不会生成中文站/英文站两套页面**。站点界面保持英文。

**无需添加 `math: true`，也不要使用 `katex` shortcode。** 本站统一在构建时生成 MathML。当前固定的主题版本由 `katex` shortcode 触发客户端公式脚本；本站检查器额外禁止 `math: true`，避免写作约定混用。

插入图片采用普通 Markdown，图片与文章放在同一个 bundle：

```md
![West Lake after the rain](lake.jpg)
```

Hugo 会为本地图片生成尺寸和适合屏幕的图片版本；不要改用外部图床来绕过这一流程。给每张图写有意义的替代文字。

行内公式写为 `\(E = mc^2\)`，独立公式使用：

```tex
$$
\int_0^1 x^2\,dx = \frac{1}{3}
$$
```

数学公式、shortcode 画廊等 Hugo 功能在 Obsidian/MWeb 中可能无法完整预览；用 **Preview** 查看最终效果。更多模板和 gallery 用法见 [实施文档](IMPLEMENTATION.md)。

## 5. 命令行完整接口

以下命令均在项目目录运行。也可以用 `scripts/blog` 的绝对路径从任何工作目录启动。

```sh
cd /Users/junwenyang/Developer/Projects/junwen-log

# 新建英文技术草稿，自动打开 Obsidian
./scripts/blog new posts "Learning Rust" --slug learning-rust --open

# 新建中文读书草稿
./scripts/blog new notes "读书：一个值得反复思考的问题" \
  --slug a-question-to-revisit --language zh-CN --open

# 新建后直接使用 MWeb
./scripts/blog new travel "A Weekend in Hangzhou" \
  --slug a-weekend-in-hangzhou --open --editor mweb

# 启动后台预览（关闭 Terminal 后仍继续运行）
./scripts/blog preview

# 只启动服务，不打开浏览器
./scripts/blog preview --no-open

# 停止本站预览
./scripts/blog stop-preview

# 生产构建与质量检查，不提交、不推送
./scripts/blog check

# 只发布指定草稿；也可传这个 index.md 的文件夹路径
./scripts/blog publish content/notes/a-question-to-revisit/index.md --open

# 发布已保存修改，保留全部草稿标记
./scripts/blog publish

# 推送后不等待 GitHub Actions
./scripts/blog publish --no-watch

# 查看状态 / 打开写作库 / 调用原生新建对话框
./scripts/blog status
./scripts/blog open
./scripts/blog gui new
```

`new` 不覆盖已有目录，拒绝路径穿越、不合规 slug 和空标题。所有稿件创建时都设置 `draft: true`。GUI 会根据标题是否含汉字选择初始语言；之后可直接修改 `contentLanguage`。

## 6. 发布具体做什么

1. 确认当前是本站的 `main` 分支，没有未完成的合并或变基，也没有用户提前暂存的改动。
2. 若明确选择了一篇草稿，只修改该稿的 `draft`。
3. 使用生产配置生成临时站点，执行 `scripts/check_site.py --public-dir …`。检查失败则恢复本次修改的草稿标记，不推送。
4. 只暂存允许的站点文件，提交到本地 Git。
5. 执行 `git pull --rebase origin main`。冲突时自动中止本次变基，保留本地提交，不推送、不强制覆盖。
6. 若同步带来新的提交，再验证合并后的站点，然后普通推送到 `origin/main`。
7. GitHub CLI 已登录时，等待本次提交对应的 Pages 工作流完成。工作流失败会报告错误，不会宣称部署成功。

允许目录包括 `content`、`config`、`layouts`、`assets`、`static`、`archetypes`、`scripts`、`docs`、工作流，以及明确的根目录站点文件和主题 submodule。`.obsidian`、`.local`、隐藏目录、`private`/`secrets` 目录、常见密钥文件与缓存排除在自动暂存之外。已跟踪但不在允许范围的改动会让脚本停止，供手动处理。

**草稿不是私密存储。** 本站源码仓库公开；草稿 Markdown 和图片可能随站点修改一起提交到 GitHub，只是不会出现在正式网页。尚不适合公开的材料应放在此仓库以外的个人笔记库，准备公开时再复制过来。

## 7. 常见情况与维护

**预览地址：** <http://localhost:1313/>，仅绑定本机回环地址，不对局域网开放。Preview 包括草稿和未来日期的内容，生产站点不会因此公开它们。日期在未来的文章到期后仍需要一次新的构建，本站没有自动定时发布任务。

**端口占用：** 如果其他程序占用 1313，脚本报告错误而不终止对方进程。可以先停止旧服务，再运行 Preview。

**构建错误：** 对照终端报错修改 Markdown、公式或模板。发布检查使用临时输出目录，不把构建产物加入 Git。

**已有暂存内容：** Publish 不混入你手动 `git add` 的内容。先自行提交，或确认后 `git restore --staged <具体路径>` 取消暂存，再发布。

**网络或 GitHub 部署失败：** 本地稿件和提交仍保留。解决错误后再次 Publish；没有新修改也能重试未完成的推送。若 GitHub 根本没有产生新的工作流，可在仓库 Actions 页面手动重跑失败的部署。

**日志：** 本地预览是 `.local/preview.log`；应用启动日志是 `.local/launcher-new.log`、`launcher-preview.log`、`launcher-publish.log`、`launcher-open.log`。这些文件不进 Git。

**移动项目后重装启动器：**

```sh
python3 scripts/macos/install.py
```

安装器只替换带本站标识的四个应用，保留同名的其他应用；桌面已有同名项目也不会被覆盖。Finder 不便运行应用时，还可双击 `scripts/macos/` 下对应的 `.command` 文件。

**验证写作工具本身：**

```sh
python3 scripts/test_blog.py
```

测试只使用临时目录和本机 Git 仓库，不连接 GitHub、不打开编辑器、不弹发布对话框。
