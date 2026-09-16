# Validation record — 2026-09-16

The website is live at https://aquariniquemu.github.io/.

## Presentation revision

- Production check after removing the lab-server guide: 52 HTML pages, two MathML expressions, one gallery page; local assets, draft exclusion, search JSON, RSS and sitemap pass.
- Desktop measurements: 720px article column, 16px/1.6 body, 36px title, 14px metadata, 60px navigation. At 390px the metadata is 12px and the article fits without horizontal overflow.
- Native table of contents starts closed and expands on click on desktop and mobile. Duplicate handwritten contents lists were removed from the WSL and Weibo articles.
- Tag text and borders use Byzantine purple in light mode and a lighter purple in dark mode, including the Tags index.
- Cover background checked in both appearances and at 390px: aspect ratio preserved, 12%/10% opacity, no in-flow hero banner.
- Mobile menu order verified: Posts, Archive, Gallery, Tags. Desktop places appearance and search after these links.
- Archive description removed; the deleted guide is absent from production pages and search JSON.
- Deployment results are recorded in the repository's [Pages workflow](https://github.com/AquariniqueMu/AquariniqueMu.github.io/actions/workflows/deploy.yml).

## Initial deployment record

- Initial source commit: `d054d61`.
- Successful deployment: https://github.com/AquariniqueMu/AquariniqueMu.github.io/actions/runs/35057756195
- Production check: 60 HTML pages, two MathML expressions, one gallery page, local links/assets, draft exclusion, valid search JSON, full-content RSS, sitemap.
- Local image pipeline smoke: SVG with viewBox receives intrinsic dimensions; GIF remains untransformed.
- Desktop UI: light and dark appearances, Chinese search, chronological archive.
- 390 px UI: readable article, no horizontal overflow, working photo lightbox.
- Mac workflow: six isolated CLI regression tests; real production check; background preview; four compiled/signed launchers; registered Obsidian content vault and verified URI opening of an article.
- Public HTTP: homepage, three sections, archive, RSS, JSON, sitemap, robots, math article and travel article return 200. Five old article URLs serve redirect HTML. The preserved RAG draft URL returns 404 and is absent from public search.
- Public RSS: six published entries in original publication-date order.
- Public Chinese search: 通信原理 finds the postgraduate-exam reflection.

Known limitations: five pre-existing downloadable attachments are missing (see MIGRATION.md); Giscus awaits app authorization and remains disabled. No Lighthouse score or measured CLS/LCP claim is made. Draft source files in this public repository are publicly readable even though drafts are excluded from the published website.
