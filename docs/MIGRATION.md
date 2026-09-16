# Legacy content migration

Migration date: 2026-09-16.

Source: `../junwen-log-legacy`, the local checkout of the existing Hugo site. Only source articles and their referenced assets were migrated; the old generated `public/` tree was not copied into the new website.

## Article inventory

Five previously published articles and one existing draft are retained. Chinese titles, article text, dates, tags, author details and contact information remain as authored. The new English slugs remain stable when titles change. All migrated articles declare `contentLanguage: zh-CN`; `categories` was removed because the three content sections provide the primary navigation.

| Source article | New page bundle | Publication date | Status |
| --- | --- | --- | --- |
| CodingBook：从0到1建设一个WSL Ubuntu系统 | `content/posts/wsl-ubuntu-setup/` | 2025-01-25 | Published |
| 微博用户信息抓取手册 | `content/posts/weibo-user-crawler/` | 2024-10-13 | Published |
| 实验室主机连接手册 | `content/posts/lab-server-guide/` | 2024-03-17 | Published |
| 考研经验与回顾 | `content/notes/postgraduate-exam-reflections/` | 2022-04-15 | Published |
| 光影集：洪洞羊獬唐尧故园 | `content/travel/tangyao-garden-yangxie/` | 2022-04-17 | Published |
| 基于RAG的大模型智能助手工作流 | `content/posts/rag-assistant-workflow/` | 2024-12-21T01:16:01+08:00 | Draft; original body was empty |

The postgraduate exam retrospective is a personal long-form note in **Notes**. It is not presented as a new book review. No new personal experiences or biographical claims were invented.

## URL continuity

Each published article contains an alias for its actual legacy URL. The four Chinese paths below were checked against the legacy `public/sitemap.xml` and corresponding canonical HTML. The WSL article was absent from that sitemap, so its exact path was checked against the canonical URL in its generated HTML.

| Old path (decoded for readability) | New path |
| --- | --- |
| `/posts/codingbook-从0到1建设一个wsl-ubuntu系统/` | `/posts/2025/01/25/wsl-ubuntu-setup/` |
| `/posts/微博用户信息抓取手册/` | `/posts/2024/10/13/weibo-user-crawler/` |
| `/posts/实验室主机连接与使用手册/` | `/posts/2024/03/17/lab-server-guide/` |
| `/posts/考研总结/` | `/notes/2022/04/postgraduate-exam-reflections/` |
| `/posts/光影集洪洞羊獬唐尧故园/` | `/travel/2022/04/tangyao-garden-yangxie/` |

GitHub Pages serves Hugo's alias HTML, which redirects to the new canonical page. The old `基于rag的大模型智能助手工作流` and `实验室主机连接与使用手册---副本` generated files had localhost canonical URLs; they were preview artifacts, not evidence that those documents should be newly published. The RAG draft remains excluded from production builds.

## Images

All **17 referenced images** are now local page resources, totaling **20,248,187 bytes** of original assets:

- **8 laboratory screenshots** recovered from `junwen-log-legacy/public/img/实验室连接手册/`. These were not present in its `static/` directory, so preserving only Markdown would have lost them. The copied files are byte-identical to their legacy originals.
- **1 retrospective photo**, `highway.jpg`, copied from `junwen-log-legacy/content/posts/pic/考研总结/highway.jpg`.
- **8 travel photos** downloaded successfully from the exact `user-images.githubusercontent.com` URLs already used by the author's article. Every response was a JPEG, and macOS `sips` confirmed valid pixel dimensions.

Image links now use paths relative to the article's own `index.md`, so they work in an Obsidian content vault and Hugo page bundles. The travel article's old percentage-sized HTML `<img>` elements were converted to Markdown image syntax; the site's image render hook can then emit explicit dimensions, responsive variants and lazy loading. The original photo order is preserved, with no extra image duplicates in the body. The first travel photo is named `feature.jpg` for Blowfish's feature-image discovery. It is an original photograph, not generated artwork.

Travel source manifest:

| Local file | Original source |
| --- | --- |
| `feature.jpg` | https://user-images.githubusercontent.com/22231832/163685255-15c1cc6e-30c3-407f-bacb-6d6180ea3189.jpg |
| `tangyao-02.jpg` | https://user-images.githubusercontent.com/22231832/163685183-e2237ee2-641d-42fb-8e22-4d245319e26e.jpg |
| `tangyao-03.jpg` | https://user-images.githubusercontent.com/22231832/163685407-f95bad5e-2b29-46ff-b87b-b310de188cd6.jpg |
| `tangyao-04.jpg` | https://user-images.githubusercontent.com/22231832/163685412-4697600b-55f9-4325-86f9-c303eea69949.jpg |
| `tangyao-05.jpg` | https://user-images.githubusercontent.com/22231832/163685416-992a3aa5-7721-4bc4-8259-773013da5ded.jpg |
| `tangyao-06.jpg` | https://user-images.githubusercontent.com/22231832/163685404-62ddd05c-3b4f-4746-8bcd-b3a7386504b2.jpg |
| `tangyao-07.jpg` | https://user-images.githubusercontent.com/22231832/163685414-3712f63b-07da-4287-8508-ae533f33097c.jpg |
| `tangyao-08.jpg` | https://user-images.githubusercontent.com/22231832/163685408-0d50bf91-b574-4d43-b8b5-00dadffbf424.jpg |

Original full-resolution resources are retained for future edits. Optimized delivery sizes are generated by Hugo; editing a source photo does not require an external image host. The unreferenced legacy `network_visualization.png` was not migrated because the RAG draft did not reference it.

## Minimal source repair

`实验室主机连接与使用手册.md` opened a fenced SSH config block at step 5 but did not close it after `Port DDD`. One closing fence was added there. This prevents the subsequent instructions and images from being rendered as code. Other Markdown bodies are retained, except for image path/markup changes described above. All migrated fenced-code delimiters are balanced after this repair.

## Five unavailable historical attachments

The retrospective's following download links were already missing from the legacy repository. A HEAD request to each original live article-relative URL returned **HTTP 404** during migration:

1. `考研政治早期笔记.pdf`
2. `写作模板.docx`
3. `杨鸿文老师通信原理讲义.zip`
4. `通信原理知识点_withMarginNotes.pdf`
5. `复试英语问题简略.docx`

Their original links remain in the article so the author can restore the files without reconstructing the intended filenames. To restore a download, place the original file with the exact matching filename into `content/notes/postgraduate-exam-reflections/`. These five links remain unavailable until the originals are recovered; no replacement documents were fabricated.

## Content boundaries

The migration preserves historical writing rather than silently updating its factual or technical advice. For example, the Weibo article's existing `description` still refers to the laboratory server, and its Markdown table of contents includes an unimplemented `requirements.txt` section. These were inherited from the old source and can be edited separately. Old dates and historical statements have not been relabeled as current advice.

## Migration checks

- 6 source articles mapped to 6 page bundles: 5 published, 1 draft.
- All 5 published articles have their exact legacy path in `aliases`.
- All referenced article images resolve to local files; no remote image URLs remain in the migrated article bodies.
- 17 assets decode with valid width and height; no generated substitute images were used.
- Laboratory screenshots and the notes image match source bytes.
- Only the documented missing attachment links remain unresolved locally.
- No source article was committed or published by the migration step itself; the site's build and deployment verification is handled by the implementation workflow.
