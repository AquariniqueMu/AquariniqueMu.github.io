# Junwen'Log 实施与维护文档

核对日期：2026-09-16。适用版本：Hugo **0.165.0**、Blowfish **v3.6.0**。

本文记录站点实际采用的架构、附件方案中经过源码核对的修正、迁移边界、部署方式和后续维护方法。日常写作请直接阅读 [WRITING.md](WRITING.md)；旧站文章与附件清单见 [MIGRATION.md](MIGRATION.md)。

> 已于 2026-09-16 完成部署和公网验收：[Junwen'Log](https://aquariniquemu.github.io/)。[首次部署运行记录](https://github.com/AquariniqueMu/AquariniqueMu.github.io/actions/runs/35057756195)显示 build 与 deploy 均成功。详细验收与已知限制见第 10 节。

## 1. 成品范围与设计取舍

站点名称为 **Junwen'Log**，目标地址为 [https://aquariniquemu.github.io/](https://aquariniquemu.github.io/)，源仓库为 [AquariniqueMu/AquariniqueMu.github.io](https://github.com/AquariniqueMu/AquariniqueMu.github.io)。

界面、导航、站点介绍及新建草稿的默认信息使用英文。文章可以是中文，既有中文文章保留原题目、日期和内容；新建中文文章采用英文目录名，不把中文标题自动拼成 URL。

| 分区 | 路径 | 展示方式 |
| --- | --- | --- |
| Technology | `/posts/` | 按年份分组的文字列表，隐藏封面，文章显示目录 |
| Reading & notes | `/notes/` | 文字列表，适合读书笔记和长篇反思；可用 series 组织连续笔记 |
| Travel | `/travel/` | 封面卡片，文章封面作为淡化背景，并按需加载灯箱 |
| About | `/about/` | 简短真实介绍，不编造个人经历 |
| Archive | `/archives/` | 跨三个分区的文章时间线 |

首页采用 Blowfish 的 `homepage.layout = "page"`，显示介绍、三个分区入口、最近 5 篇及 All writing 入口；不设置背景大图。以 `github` 配色为基础，自定义米白底色、克制的绿色强调和细分隔线；默认浅色并支持系统外观与手动切换。正文现采用系统无衬线字体，中文回退到苹方、微软雅黑等系统字体；页面不请求 Inter 或完整中文字体包。标签使用拜占庭紫 `#702963`，深色外观用较亮的 `#d79acb`。

主导航为 **Posts · Archive · Gallery · Tags · 外观切换 · 搜索**；Gallery 指向 `/travel/`，读书笔记仍可从首页、Archive 和标签进入。参照 [Lilian Weng 的文章](https://lilianweng.github.io/posts/2026-07-04-harness/) 实测比例：正文 16px / 1.6、桌面标题 36px、文章单列最大 720px、导航高 60px。日期与字数一行桌面 14px、手机 12px。`layouts/single.html` 与 `partials/toc.html` 将目录置于正文上方，用原生 `details` 默认收起；摘要标题居中，展开后的层级列表左对齐。文章阅读栏整体居中，正文按正常左对齐排版。

保留站内搜索、代码复制、RSS、标签和系列；不用 categories、访问计数或点赞服务。数学在构建时生成 MathML。页面仍可有搜索、菜单、外观切换等 JavaScript，“零 JS 数学”不表示全站完全无 JavaScript。

## 2. 版本与配置审计

本次直接检查了 [v3.6.0 源码](https://github.com/nunocoracao/blowfish/tree/v3.6.0)，没有依赖猜测的配置名。主题固定在 commit `4643c46bd5e921fee51c420575fadebf9f4b3681`，通过 Git submodule 保存指针。[该版本发布页](https://github.com/nunocoracao/blowfish/releases/tag/v3.6.0)为稳定版本；查询时 GitHub latest API 还返回了一个非语义版本 `untagged-…`，因此不以 latest URL 作为安装依据。

主题 README 声明最低 Hugo 0.162.0，主题自身 [Pages workflow](https://github.com/nunocoracao/blowfish/blob/v3.6.0/.github/workflows/pages.yml)使用 0.165.0。本机用 Hugo 0.165.0 对这些模板进行了独立构建验证。

| 附件中的写法或假设 | 核实结果与本项目做法 |
| --- | --- |
| `paginate = 10` | 当前使用 `[pagination] pagerSize = 10`。 |
| `languageCode`、`languageName` | Hugo 自 0.158 起弃用；使用 `locale`、`label`，语言文件为 `languages.en.toml`。 |
| `colorScheme = "github"` | v3.6.0 存在该方案，`one-light` 也存在；本项目选 github。 |
| `homepage.layout = "page"` | 支持；首页正文来自 `content/_index.md`。 |
| `[article] showSummary = true` | 摘要开关属于 `[list] showSummary`，也可由文章 front matter 覆盖。 |
| `showCards = false` 等于关闭封面 | 该开关只影响文字列表的卡片边框与内距；关闭文章列表封面用 `hideFeatureImage = true`。 |
| `_index.md` 参数自动控制全部文章 | 普通参数控制分区页；要传给后代文章，必须写 `cascade.params`。 |
| `math: true` 必然触发主题 KaTeX | v3.6.0 实际由 `katex` shortcode 触发；主题源码没有 `.Params.math` 判断。本项目不使用这个 shortcode，也不要求 `math: true`。 |
| 主题图片一般没有宽高 | v3.6.0 原生图片 hook 已有 `width` / `height`。自定义处理的目的在于 WebP 尺寸策略、明确 srcset 与格式边界。 |
| `extend_head.html` / `extend_footer.html` | 真正扩展名使用连字符：`extend-head.html` / `extend-footer.html`。 |
| 在 extend-footer 按页面加载图库 | 主题 footer 对扩展使用无页面区分键的 `partialCached`，不适合该用途；改用 `extend-head-uncached.html`。 |
| 自定义 shortcode 名为 `gallery` | 会同时触发主题的 Packery 资源；本项目命名为 `photo-gallery`。 |
| 所有模板都改为 `_partials` 新路径 | 主题仍检查 `templates.Exists("partials/...")`；扩展 partial 保留 `layouts/partials/`，否则可能被忽略。独立构建已验证此差异。 |
| `fetch-depth: 0` 会自动采用 Git 日期 | 还要 `enableGitInfo = true` 和明确的 `frontmatter.lastmod` 顺序。发布日期仍读取文章的 `date`。 |
| 放入 comments.html 即启用评论 | 还要 `article.showComments = true`；本项目默认关闭。 |
| `<body>` 天然有分区 class | 主题没有这个保证，不能用未实际生成的 class 编写分区 CSS。 |

核对依据：[主题参数](https://github.com/nunocoracao/blowfish/blob/v3.6.0/config/_default/params.toml)、[head](https://github.com/nunocoracao/blowfish/blob/v3.6.0/layouts/partials/head.html)、[vendor](https://github.com/nunocoracao/blowfish/blob/v3.6.0/layouts/partials/vendor.html)、[footer](https://github.com/nunocoracao/blowfish/blob/v3.6.0/layouts/partials/footer.html)、[文章列表](https://github.com/nunocoracao/blowfish/blob/v3.6.0/layouts/partials/article-link/simple.html)、[Hugo languages](https://gohugo.io/configuration/languages/)、[pagination](https://gohugo.io/configuration/pagination/)、[cascade](https://gohugo.io/configuration/cascade/)。

## 3. 项目结构与配置职责

```text
junwen-log/
├── .github/workflows/        # 构建、校验与 GitHub Pages 发布
├── archetypes/              # 三种分区的新文章模板
├── assets/
│   ├── css/                 # 自定义排版、配色补充
│   ├── js/                  # 图库初始化及主题小型覆盖
│   └── lib/                 # 本地 GLightbox 与许可证
├── config/_default/
│   ├── hugo.toml            # URL、taxonomy、输出、缓存、日期
│   ├── params.toml          # Blowfish 的实际配置项
│   ├── markup.toml          # Markdown、数学、代码高亮
│   ├── languages.en.toml    # 默认英文信息
│   └── menus.en.toml        # 导航
├── content/                 # Obsidian vault；文章和图片
├── docs/                    # 实施、写作、迁移说明
├── layouts/
│   ├── _markup/             # 图片和数学 render hooks
│   └── partials/            # 主题扩展，保留兼容路径
├── scripts/                 # 写作 CLI、安装与验收工具
├── static/                  # favicon 等直接发布的文件
└── themes/blowfish/         # 锁定版本的 submodule
```

`public/` 是构建产物，`resources/_gen/` 是 Hugo 处理资源的缓存。二者不作为源文件提交。编辑器状态、预览状态和本机凭据也不提交。其他机器通过 `git clone --recurse-submodules` 获取主题；已 clone 的仓库可执行 `git submodule update --init --recursive`。

主要配置如下，实际文件为最终依据：

```toml
# config/_default/hugo.toml
defaultContentLanguage = "en"
locale = "en-US"
hasCJKLanguage = true
enableGitInfo = true
buildDrafts = false
buildFuture = false

[pagination]
  pagerSize = 10
[taxonomies]
  tag = "tags"
  series = "series"
[outputs]
  home = ["HTML", "RSS", "JSON"]
[frontmatter]
  lastmod = ["lastmod", ":git", "date"]
```

正文永久链接分别为：

```text
/posts/:year/:month/:day/:slug/
/notes/:year/:month/:slug/
/travel/:year/:month/:slug/
```

旧文章额外保留 `aliases`，见迁移清单。发布后不要随意更改 `date`、目录 slug 或永久链接格式；确有需要时添加旧 URL 的 alias。`lastmod` 可随修订变化，不能用它代替原发布日期。

`contentLanguage` 是本项目的文章参数，不会自动创建第二套中文站点。中文文章设为 `zh-CN`，默认是 `en`。本项目的 `layouts/baseof.html` 将它写入 `<html lang>`，同时在 body 输出 `data-section` 供分区样式使用；导航文字仍保持英文。`hasCJKLanguage = true` 允许 Hugo 对中文进行相应的字数统计；无需把整个界面切换为中文。

分区继承以 Technology 为例：

```yaml
---
title: Technology
cardView: false
groupByYear: true
cascade:
  params:
    showHero: false
    hideFeatureImage: true
    showTableOfContents: true
---
```

Travel 的分区页设置 `cardView: true`，传给文章的设置包含 `hideFeatureImage: false`、`showTableOfContents: false`。文章自己的参数优先于 cascade。当前自定义单页模板不再显示占据正文空间的 Hero；`showHero` 和 `heroStyle` 为迁移保留值，不控制新背景。

`layouts/partials/article-background.html` 从本地 `featureimage` 参数或 bundle 中的 `*feature*`、`*cover*`、`*thumbnail*` 自动选择静态位图，生成最大 1920px WebP 和 640/1024px 候选。图片保持比例完整显示在正文后方，不占文流空间，浅色不透明度 12%、深色 10%，下方渐隐。无封面的文章不输出背景。SVG/GIF 不用作这一装饰背景。

## 4. 数学、图片、画廊与搜索

### 4.1 原生 MathML

`markup.toml` 显式启用 Goldmark passthrough；`layouts/_markup/render-passthrough.html` 调用：

```go-html-template
{{- $opts := dict "displayMode" (eq .Type "block") "output" "mathml" -}}
{{- with try (transform.ToMath .Inner $opts) -}}
  {{- with .Err -}}
    {{- errorf "Math rendering failed in %s: %s" $.Position . -}}
  {{- else -}}
    {{- .Value -}}
  {{- end -}}
{{- end -}}
```

行内用 `\(O(n \log n)\)`，块级用 `$$...$$` 或 `\[...\]`。单个 `$` 不作为分隔符，避免价格与普通美元符号被误识别。错误公式使构建失败，便于发布前定位。

输出为浏览器原生 `<math>`，不依赖 KaTeX CSS、字体或浏览器端渲染库。Blowfish 原本无条件捆绑的小型 `assets/js/katex-render.js` 回调由项目同名文件覆盖；不要在正文加入 `katex` shortcode。检查时查看生产 HTML 和实际脚本请求，而不是仅按 bundle 文件名推断。官方接口说明见 [transform.ToMath](https://gohugo.io/functions/transform/tomath/) 和 [passthrough hook](https://gohugo.io/render-hooks/passthrough/)。

### 4.2 图片与布局稳定性

文章采用 Page Bundle：`index.md` 与它的图片放在同一个目录。正文写普通 Markdown，例如 `![Meaningful description](photo.jpg "Optional caption")`。普通位图以 **1280px** 为正文主图最大宽度、质量 **82** 输出 WebP，并在适用时生成 **480 / 800 / 1280px** 候选；小图不放大。HTML 的 srcset 描述符使用真实尺寸，明确输出 `width`、`height`，让浏览器预留图片空间。移动端 sizes 预留左右 48px，宽屏正文按 720px 选择资源。

不能把 GIF 当作普通照片压缩，否则会丢失动画；模板将 GIF 排除在位图缩放之外。SVG 使用独立分支：从数字 `viewBox` 提取宽高，不调用 SVG 不支持的 `.Width` / `.Height`；没有受支持 viewBox 时明确报错。写作时为 SVG 保留如 `viewBox="0 0 800 600"` 的尺寸定义。本文不把所有 SVG 语法或所有动画格式都列为已验证的兼容范围。

本项目的 Markdown 图片 hook 要求图片能解析为 **本地 Page Resource 或 assets resource**。缺失资源会使构建报错，不会悄悄保留一个坏链接；远程图片和任意 static 相对路径不是这个 hook 的通用降级方式。写作时优先使用文章 bundle。

尺寸属性消除的是图片未预留空间造成的布局跳动，不等于承诺整页 CLS 永远为零；字体、动态内容、灯箱和页面布局仍需实际检查。旧图的原始文件保留，不在发布流程里用 `mogrify` 覆盖它们。新照片建议先把交付副本控制在合理分辨率，再加入 Git；原始素材可另行归档。

### 4.3 按需灯箱

自定义 shortcode 名称为 **`photo-gallery`**。GLightbox 的 JS、CSS 与许可证位于 `assets/lib/`，通过 Hugo 资源指纹生成本地 URL。`extend-head-uncached.html` 用 `.HasShortcode "photo-gallery"` 判断是否引入 CSS、JS 及初始化脚本。

这避免内容渲染先后顺序和 `.Store` 的依赖，也避免主题 `extend-footer` 的跨页面缓存。普通技术文章不加载 GLightbox。全局 `disableImageZoom = true` 关闭主题默认的 medium-zoom，避免两个图库系统同时工作。

把图库照片放在文章的 `images/` 子目录后，可在正文写：

```go-html-template
{{< photo-gallery match="images/*" cols="3" ratio="4/3" >}}
```

默认 match 为 `images/*`、列数为 3、比例为 `4/3`。列数只接受 2、3、4；比例只接受 `1/1`、`4/3`、`3/2`、`16/9`。手机上改为两列。缩略图最大 600px、WebP q80；灯箱大图最大 1800px、WebP q85，均不放大小图。模板仅处理匹配到的可缩放位图，匹配为空会报错。可用资源参数提供标题和替代文字：

```yaml
resources:
  - src: "images/lake.jpg"
    params:
      title: "The lake after the rain"
```

### 4.4 搜索与 RSS

`enableSearch = true` 配合首页 JSON 输出启用 Blowfish 搜索。它使用本地 Fuse 索引，不需要第三方搜索服务。中文连续字串可检索，但这不是完整的中文分词引擎；跨词重排、同义词等不能保证命中。

RSS 位于 `/index.xml`，站点地图 `/sitemap.xml`，爬虫规则 `/robots.txt`。`layouts/rss.xml` 输出三个主要分区的文章全文，并把正文中的根路径 src/href 改写成绝对 URL，便于阅读器访问。为分享和检索填写文章 `description` 或 `summary`。读取旧笔记时保留历史日期，不把内容包装成最近验证过的技术指南。

## 5. 旧站迁移与内容保留

旧仓库本地副本保存在相邻目录 `../junwen-log-legacy`。新站只迁移需要的 Markdown 与引用资源，不把旧 `public/` 全量带进源码。详细逐项记录见 [MIGRATION.md](MIGRATION.md)。

首次迁移保留 **5 篇已发布文章、1 篇原有草稿**；另外新增一篇英文站点介绍。后续按用户要求删除了《实验室主机连接手册》和 8 张附图，当前为 **4 篇旧文章 + 1 篇英文介绍 + 1 篇草稿**。该页的新旧 URL 均不再发布，文件可从 Git 历史恢复。技术文章归入 posts，考研回顾归入 notes，唐尧故园摄影归入 travel；没有把个人回顾虚构成书评，也没有生成虚构旅行经历。

旧的 5 个正式文章地址从旧 sitemap 或生成 HTML 的 canonical 核实后写入 aliases。GitHub Pages 将提供 Hugo 生成的跳转 HTML，导向新日期路径。旧预览产物中的 localhost 地址不作为正式 URL 迁移，也不作为擅自发布草稿的依据。

17 张引用图片全部本地化，原始资源约 **20.25 MB**：8 张实验室截图从旧 `public/img/` 恢复、1 张旧目录照片、8 张文章原来引用的 GitHub 图片。所有图片已确认可解码并有有效尺寸。旧本地图片保持字节一致；在交付 HTML 中优化图片不等于删除原图。

最终游记的“光影留念”段落改为 `photo-gallery match="*.jpg"`：8 张原照片组成网格与灯箱，`feature.jpg` 同时作为文章题图。图片内容和原文保持，展示形式从原来的逐图标记调整为图库；题图再次出现在图库是同一资源的两处呈现，没有新造或替换照片。

实验室指南缺少的一个代码块结束符已补齐，避免后续正文被误渲染为代码。其余修改限于分区元数据、链接路径、图片标记等迁移需要的范围。

考研回顾中的 **5 个历史下载附件**不在旧源仓库中，旧站对应请求也返回 404；保留原链接和文件名以便恢复。将原文件放回该文章 bundle 的同名路径即可。它们是已记录的历史缺失，不能在验收报告中写成“所有旧链接均已恢复”。

本次已获取远端 `main` 历史，并将新工作树连接到既有提交历史；旧站基线 commit 为 `906bdd7`。本地已建立 **`backup-before-blowfish-2026-09-16`** 标签，指向迁移前远端 `main`，计划随首次迁移提交一并推送。新实现作为这个历史之后的普通提交发布，不强推。旧站生成产物从当前版本追踪中移除，但仍存在于旧历史与原始副本中。

## 6. 构建与 GitHub Pages 部署

### 6.1 依赖与版本锁定

常规构建只需要 Hugo 0.165.0、Git、Python 3；本机写作使用 Obsidian，MWeb 可作为替代编辑器。普通发文无需 npm、Go modules 或 Node 构建链。主题以 Git submodule 获取，生产构建不得跟随主题 main 分支自动升级。

安装 Hugo 时从 `gohugoio/hugo` 的 **v0.165.0** release 下载对应包，同时下载该版本校验清单，校验 SHA-256 成功后才解包/安装。CI 执行相同原则，不通过 latest URL 下载二进制。该 release 在 macOS 提供 universal `.pkg`，在 Linux CI 使用 amd64 `.tar.gz`，两者不能混用。

在另一台 Mac 上安装固定版本，可在临时目录执行下列命令并通过系统安装器完成安装：

```sh
mkdir -p /tmp/junwen-hugo-0.165.0
cd /tmp/junwen-hugo-0.165.0
curl -fsSLO https://github.com/gohugoio/hugo/releases/download/v0.165.0/hugo_extended_0.165.0_darwin-universal.pkg
curl -fsSLO https://github.com/gohugoio/hugo/releases/download/v0.165.0/hugo_0.165.0_checksums.txt
grep ' hugo_extended_0.165.0_darwin-universal.pkg$' hugo_0.165.0_checksums.txt | shasum -a 256 --check
# 仅在上一条校验显示 OK 后打开安装器
open hugo_extended_0.165.0_darwin-universal.pkg
```

安装后重新运行 `hugo version`，确认实际命中的版本。当前写作 CLI 优先查找 `~/.local/bin/hugo`，再查 Homebrew 与 PATH；不要因多个 Hugo 安装并存而误以为本机版本已同步。

### 6.2 自动部署过程

Pages 的 Source 必须设为 **GitHub Actions**。具体文件为 [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)，监听 `main` push、pull request，并支持手动触发。PR 只构建与检查，正式分支才上传并部署，过程如下：

1. Checkout 源码，拉取完整历史和主题 submodule。
2. 安装并校验固定版本 Hugo。
3. 恢复图片处理缓存。
4. 取得 GitHub Pages 提供的 base URL，在 production 环境构建。
5. 对生成 HTML 运行站点检查；失败则不上传可部署产物。
6. 上传 Pages artifact，再由部署 job 发布。

工作流全局只授予 `contents: read`；部署 job 另授予 `pages: write`、`id-token: write`，使用 `github-pages` environment。并发组为 `pages-${{ github.ref }}`，`cancel-in-progress: false`。当前 actions 是 checkout@v6、cache@v4、configure-pages@v5、upload-pages-artifact@v4、deploy-pages@v4。

CI 下载 `hugo_extended_0.165.0_linux-amd64.tar.gz` 与 `hugo_0.165.0_checksums.txt`，在 `set -euo pipefail` 下提取匹配行并运行 `sha256sum --check`。成功后只解出 hugo 二进制并安装到 `/usr/local/bin`。流程在版本缺失、下载失败或校验失败时停止。

图片缓存目录是 `resources/_gen/`；当前 `caches.images.dir = ":resourceDir/_gen"`，保留期 720 小时。缓存键为 `hugo-0.165.0-${runner.os}-${hash}`，hash 覆盖 `content/**`、`assets/**`、`layouts/**`、`config/**`，restore key 使用同版本和系统前缀。缓存只是加速，删除缓存后仍应能从源文件完整重建。`public/` 不作为跨版本的源缓存。

`enableGitInfo = true` 与完整 Git history 用于更新时间回退；构建时区使用 Asia/Shanghai。Production 不添加 `--buildDrafts` 或 `--buildFuture`。CI baseURL 使用 configure-pages 输出，保持 canonical、RSS、sitemap、资源路径一致。

### 6.3 首次启用与检查

首次登录 GitHub、授权 GitHub CLI 或在浏览器中确认账户，应由账户持有人完成。授权后可检查：

```sh
gh auth status
git remote -v
git ls-remote --heads origin
git submodule status
./scripts/blog check
```

推送后查看仓库 [Actions](https://github.com/AquariniqueMu/AquariniqueMu.github.io/actions) 中对应 commit 的运行。必须以部署 job 成功和公网站点可访问为完成依据；只看到 `git push` 成功不算部署通过。

线上至少检查：首页、三个分区、英文介绍、一个中文长文、摄影文章、搜索、RSS、站点地图，以及五个旧文章地址。用未带本机预览状态的浏览器访问，确认没有 `localhost`、预览脚本或草稿正文。最后记录成功的 commit SHA、Actions run URL 和访问日期，便于追踪。

## 7. Mac 写作与一键发布

详细步骤见 [WRITING.md](WRITING.md)。本机已安装四个应用到 `~/Applications/Junwen Log/`，桌面有 Junwen Log 快捷目录：**New Draft**、**Open Writing Vault**、**Preview**、**Publish**。启动器已通过 AppleScript 编译和代码签名检查。

`content/` 已通过 Obsidian 界面注册为独立 vault，并实际验证从 CLI 的 Obsidian URI 打开文章。不需要导出插件。使用普通 Markdown 链接，粘贴附件存放到当前文章文件夹，避免 `![[image.png]]` 这种 Hugo 不认识的 wiki 图片语法。MWeb 也已安装，可直接打开同一个 `index.md`。

CLI 使用 Python 标准库，脚本自己定位仓库，不要求 Finder 启动时处于指定目录：

```sh
# 建英文技术草稿并打开编辑器
./scripts/blog new posts "An idea worth keeping" --slug an-idea-worth-keeping --open

# 建中文读书笔记，URL 仍用英文 slug
./scripts/blog new notes "阅读札记" --slug reading-notes --language zh-CN --open

# 含草稿的本机预览；保存后刷新
./scripts/blog preview

# 正式构建与检查
./scripts/blog check

# 只将这一篇草稿改为已发布，然后提交、同步、推送、等待部署
./scripts/blog publish content/notes/reading-notes/index.md --open

# 发布现有站点修改，保留所有 draft 标记
./scripts/blog publish

# 查看状态 / 停止本站预览
./scripts/blog status
./scripts/blog stop-preview
```

预览监听 `127.0.0.1:1313`，包括草稿与未来日期文章；生产检查不包括。可通过 `--editor mweb` 打开 MWeb。创建草稿拒绝覆盖现有 bundle；中文标题和英文 slug 分开输入。

发布过程先构建检查、提交允许目录内的已保存修改，随后同步远端并再次验证，最后普通 push。脚本不自动 stash、不强推、不静默解冲突；出现冲突时保留本地提交并停止。第一次检查失败时，会在内容未被其他操作改写的条件下恢复选中草稿的原状态。

“发布某一草稿”只限定哪一篇 `draft: true` 被改为 false，**不是只提交那一个文件**；其他允许目录中已保存的修改也会进入该次提交。发布前可以运行 status。未指定文章时不会把全部草稿批量公开成网页。

仓库是公开的，`draft: true` 只控制站点页面是否生成，不隐藏已经提交的 Markdown 源码。不打算公开的私人笔记应放在仓库外。

## 8. 可选 Giscus 评论

评论默认关闭：`article.showComments = false`、`giscus.enabled = false`。当前已启用仓库 Discussions 并读取实际仓库与 Announcements category 标识，写入 `[giscus]`；这不等于 GitHub App 已安装或评论服务已可用。

以后启用时依次完成：

1. 仓库保持 public；确认已有 Discussions 及 Announcements category 仍存在。
2. 在 GitHub 安装 Giscus App，选择正确仓库。
3. 用 [giscus.app](https://giscus.app/) 检查实际 repo ID、category ID 和匹配配置与当前 `[giscus]` 一致。
4. 本项目已有 `layouts/partials/comments.html` 与配套脚本；确认服务可用后同时打开 `giscus.enabled` 和 `article.showComments`。
5. 在文章底部按需加载评论，验证浅色/深色切换和键盘操作。

若采用 pathname 映射，评论归属与路径相关。更改 permalink 不会自动迁移旧评论；alias 负责文章跳转，不能替代评论迁移。启用后还应考虑国内网络可达性，并将外部请求单独纳入性能检查。

## 9. 维护、备份与回滚

### 日常维护

- 修改内容后使用 preview；发布前使用 check。更新链接、说明和代码时保留真实发布日期。
- 新图片使用英文文件名和合适的 alt，原图另有备份；不要依靠“后来从 Git 删除文件”清掉历史体积。
- 每隔一段时间检查 Actions 状态、404 与旧附件恢复情况，不需要为一个小博客引入数据库或自建服务器。
- 将源仓库与重要原始素材纳入自己的备份。GitHub 远端、相邻旧站目录和外部素材备份承担不同职责。

### 升级 Hugo 或主题

创建维护分支，只修改一个版本变量或主题指针；记录升级前 commit。升级主题时先阅读 release notes，checkout 明确 tag，再提交新的 submodule 指针。同步更新本机与 CI 的 Hugo 版本及校验资源。

升级后运行生产构建和站点检查，查看数学、图片、图库、搜索、中文长文、深色模式与移动端。尤其要复核上表中的扩展点：`templates.Exists` 路径、`partialCached` 范围、主题新增默认 JS，以及同名 shortcode 冲突。自定义模板不应无条件整份复制新主题，以免覆盖自己的逻辑。

### 回滚一个有问题的发布

优先通过新提交撤销坏改动，保留公开历史。例如已确认 `BAD_COMMIT` 是一次普通提交时：

```sh
git status
git revert BAD_COMMIT
./scripts/blog check
git push origin main
```

将 `BAD_COMMIT` 替换为实际 SHA。工作区有未保存修改或提交是 merge 时，先判断应恢复的范围；不要原样运行带占位符命令或直接 `reset --hard`。如果是主题升级问题，恢复原 submodule 指针，再检查和提交。

新提交会再次触发部署。在它成功前，GitHub Pages 可能仍显示上一次成功版本，这是正常发布行为。需要临时回到已知好版本时，可对相应 Actions 运行采用 GitHub 提供的重新运行方式，但长期以源仓库恢复到一致状态为准。

首次迁移若需要恢复旧站，应以保留的旧源码/历史 commit 为起点，在新分支构建验证后形成恢复提交；不要删除新站目录或强制覆盖远端来“快速恢复”。旧站默认主题和部署设置也应随其历史一并确认。

## 10. 验收记录与未决事项

以下表格保留 2026-09-16 首次上线的本地及线上验收记录。首次上线提交为 `d054d61`，通过 `./scripts/blog publish` 执行推送、等待构建和部署。后续展示修订见 [CHANGES-2026-09-16.md](CHANGES-2026-09-16.md) 与 [VALIDATION.md](VALIDATION.md)：删除实验室指南后，当前生产检查为 52 个 HTML 页面、2 个 MathML 表达式、1 个图库页；正式文章现为 5 篇。新版已在桌面与 390px 手机尺寸核对排版、默认收起目录、导航和深浅外观背景。

| 验收项 | 当前证据或状态 |
| --- | --- |
| 主题 tag 与 Hugo 版本兼容 | 已检查 v3.6.0 源码、最低版本说明和主题 CI；本机 Hugo 0.165.0 存在。 |
| 原生 MathML 模板 | 独立临时站和正式生产构建均通过；正式输出检测到 2 个 `<math>`。 |
| extend-head-uncached 路径 | 已对照构建，`layouts/partials/` 可用，`layouts/_partials/` 被主题存在性检查忽略。 |
| medium-zoom 关闭 | 独立构建确认 `disableImageZoom=true` 不加载相关 JS。 |
| tags/series 替代旧 taxonomy | 独立有效配置输出只含 tags/series；正式配置已采用该设置。 |
| 旧内容迁移 | 5 已发布 + 1 草稿保留，17 图片本地化，5 旧文章 alias 已核实。 |
| 历史下载附件 | 5 个源文件尚缺，旧站也为 404；已列清单，等待作者找回原文件。 |
| 默认英文、中文正文 | baseof 使用 contentLanguage 输出 html lang；生产检查及浏览器验证通过，中文搜索已测试。 |
| 图片宽高与 WebP | 生产 HTML 检查通过：图片具备尺寸，或主题缩略图在固定空间内绝对定位；不据此声称实测 CLS 分数。 |
| 图库仅按需加载 | 生产检查检测到 1 个图库页，HTML 中的图库与 GLightbox 资源条件一致；手机灯箱交互已测试。 |
| 正式构建和站点检查 | 已通过：60 个 HTML 页面、2 个 MathML 表达式、1 个图库页；站内资源目标、草稿排除、搜索 JSON、RSS 全文与 sitemap 校验通过。5 个既有缺失附件单独列入 allowlist，并在输出中提示。 |
| Mac 写作启动器 | 四个应用已安装并完成编译/签名检查；Obsidian content 库已注册，CLI 打开具体文章已通过界面验证。 |
| 浏览器视觉与交互 | 桌面浅色/深色、390px 手机布局、中文搜索、手机灯箱已通过本地浏览器检查；该次检查未见控制台错误。 |
| GitHub 登录、推送与部署 | 已保留完整 main 历史；备份 tag `backup-before-blowfish-2026-09-16` 已推送。Pages 切换为 workflow，首次运行 build 32 秒、deploy 11 秒，均成功。 |
| 公网 HTTP、旧地址、RSS、搜索 | 首页、分区、archives、RSS、JSON、sitemap、robots 均 HTTP 200；5 个旧文章地址返回跳转 HTML；原 RAG draft 地址 HTTP 404，JSON 不含该稿；线上中文搜索“通信原理”能命中考研笔记。RSS 为 6 篇正式文章，按原始日期倒序。 |
| Lighthouse / CLS / LCP | 未给出测量分数；正式上线后才能按确定设备、网络和缓存条件报告。 |
| Giscus | 可选项，未启用，不影响基本博客发布。 |

附件中的 CLS < 0.05、LCP < 2.5 s、Lighthouse > 95 可作为后续性能目标。报告必须附测试环境与日期，不能把目标当成成绩。启用搜索时也应区分未压缩脚本体积和实际网络传输体积，避免把“首屏 < 30 KB”写成未经测量的承诺。

## 11. 常见故障

| 现象 | 检查与处理 |
| --- | --- |
| 页面只有文字、样式缺失 | 检查 submodule 已初始化、主题路径及 CI baseURL。 |
| 新文章本地可见、线上不见 | 查看 draft、date 是否在未来、是否保存并提交，以及部署是否实际成功。 |
| 中文只统计成少数词 | 检查 `hasCJKLanguage` 与文章内容标记，不要仅修改界面 locale。 |
| 数学显示原始分隔符 | 检查 passthrough 和 `_markup/render-passthrough.html`；使用支持的分隔符。 |
| 图片 404 | 先检查文件与 index.md 同 bundle、文件名大小写和相对路径。 |
| 文章里的图库没加载 | 检查 shortcode 是否叫 photo-gallery、partial 是否放在 layouts/partials、实际 CSS/JS 请求是否成功。 |
| 技术页加载 Packery | 检查是否误用了主题的 gallery shortcode。 |
| 更新后页面没有刷新 | 保存 Markdown，查看预览日志；本项目预览已使用 `--disableFastRender`。 |
| 发布说 staging area 非空 | 先看 `git diff --cached`，处理自己已有的暂存修改，再重新发布。 |
| push/rebase 失败 | 本地提交仍保留；检查远端变动和认证，解决冲突后重试，不使用强推。 |
| 端口 1313 被占用 | 查明原预览进程；脚本不会为了启动博客而杀掉不属于本站的进程。 |
| 旧附件点击无内容 | 对照 MIGRATION.md；已知五个文件需要恢复原件。 |

## 12. 本次边界与后续扩展

本次目标是完整静态博客、保留旧写作、可靠的本地编辑与 Pages 发布链路。自定义域名、Cloudflare、Syncthing、Forgejo、语义搜索、中文字体分片和访问统计不作为上线前置条件；如果以后添加，应分别验证收益、资源开销和恢复方式。

GitHub Pages 在不同网络下的访问速度不一致。使用一个新域名或代理不能保证国内所有网络变快，本文不作这一承诺。优先保留可迁移的 Markdown、图片资源和可复现构建，未来更换托管时沿用同一份源内容。
