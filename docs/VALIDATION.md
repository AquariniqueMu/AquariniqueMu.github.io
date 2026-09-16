# Validation record — 2026-09-16

The website is live at https://aquariniquemu.github.io/.

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
