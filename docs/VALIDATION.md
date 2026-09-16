# Validation record — 2026-09-16

The website is live at https://aquariniquemu.github.io/.

## Functional sections and profile revision

- Production output: 51 HTML pages, four published articles, one gallery; Posts and its RSS contain every published article newest first. Tech has two published articles, Notes one, Daily one. The existing RAG draft stays unpublished.
- Existing technical URLs remain unchanged. `/travel/` and the dated travel article have aliases to Daily. The English notebook introduction is absent from output and search.
- The legacy Travel RSS remains available with exactly the Daily feed's articles; the RSS-only compatibility section is absent from search and sitemap. Posts pagination was separately checked with 27 temporary entries across three pages, with no omissions or date-order errors.
- Desktop UI: full navigation reads Posts, Tech, Notes, Daily, Tags, About, followed by appearance and search; menu text measures 14px.
- Cover backdrop bounds match the viewport, starting at (0, 0); it covers the header and both margins. The image uses proportion-preserving cover cropping. Desktop light mode uses 10% opacity; mobile dark mode uses 8%.
- Markdown quote borders and links match purple tags. Show More also has matching text/border color and points to `/posts/`.
- Profile avatar loads as WebP, is circular with a shadow, and measures 144px on desktop / 128px on phones. GitHub and Blog links are present, and the requested introduction is displayed.
- 390px UI: no horizontal overflow on the homepage or covered article; profile, mobile navigation and dark appearance checked.
- Writing workflow: ten isolated regression tests pass, including the three new draft sections, publish/conflict behavior, port reuse after TIME_WAIT, and refusal to interrupt a real listening service.
- The deleted introduction contained the site's two example formulas. Live output now has zero formulas; the MathML render hook remains unchanged and browser-side KaTeX/MathJax remain forbidden.
- See [the change record](CHANGES-2026-09-16-followup.md) for the avatar prompt and implementation details, and [Pages workflow runs](https://github.com/AquariniqueMu/AquariniqueMu.github.io/actions/workflows/deploy.yml) for deployment status.

## Earlier presentation revision

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
