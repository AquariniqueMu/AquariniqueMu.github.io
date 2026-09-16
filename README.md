# Junwen'Log

A personal notebook on **technology, books, and places**, built with Hugo and Blowfish. Navigation and site information are in English; articles can be written in English or Chinese.

- Website: [aquariniquemu.github.io](https://aquariniquemu.github.io/)
- Source: [AquariniqueMu/AquariniqueMu.github.io](https://github.com/AquariniqueMu/AquariniqueMu.github.io)
- [Writing guide / 写作指南](docs/WRITING.md)
- [Implementation guide / 完整实施文档](docs/IMPLEMENTATION.md)
- [Legacy migration record](docs/MIGRATION.md)

## Stack

| Component | Choice |
| --- | --- |
| Generator | Hugo **0.165.0**, pinned locally and in CI |
| Theme | Blowfish **v3.6.0**, pinned Git submodule |
| Appearance | `github` color scheme, plain page homepage, light/dark modes |
| Mathematics | Build-time `transform.ToMath` → native MathML |
| Images | Local page bundles, explicit dimensions and responsive WebP variants |
| Gallery | Custom `photo-gallery` shortcode with locally hosted GLightbox |
| Publishing | GitHub Actions → GitHub Pages |
| Writing | Obsidian content vault, optional MWeb, macOS launchers and a Python CLI |

The source includes five previously published articles, their local images, one preserved draft, and a new English introduction. Historical Chinese titles and publication dates are retained. Old article URLs have aliases to their new canonical URLs. Five historical downloadable attachments were already missing; their exact names and recovery instructions are recorded in [MIGRATION.md](docs/MIGRATION.md).

## Local setup

Clone the theme together with the site:

```sh
git clone --recurse-submodules https://github.com/AquariniqueMu/AquariniqueMu.github.io.git
cd AquariniqueMu.github.io
hugo version
```

Use Hugo 0.165.0, Git, and Python 3. GitHub CLI (`gh`) is used to follow deployment status; authenticate it with `gh auth login` when setting up another machine. Use the checksum-verified installer described in [the implementation guide](docs/IMPLEMENTATION.md#6-构建与-github-pages-部署) to keep the build version reproducible. No Node or npm installation is required for ordinary writing and builds.

```sh
./scripts/blog preview
./scripts/blog check
./scripts/blog stop-preview
```

Preview runs at [localhost:1313](http://localhost:1313/) and includes drafts and future-dated entries. Production builds exclude both. Open the repository's **`content/` directory** as an Obsidian vault, or open the article's Markdown file in MWeb. Read [WRITING.md](docs/WRITING.md) for macOS launchers, editor settings, image handling, and troubleshooting.

## Write and publish

Create an English draft:

```sh
./scripts/blog new posts "An idea worth keeping" --slug an-idea-worth-keeping --open
```

Create a Chinese note while retaining an English URL:

```sh
./scripts/blog new notes "阅读札记" --slug reading-notes --language zh-CN --open
```

Publish one selected draft after saving the file:

```sh
./scripts/blog publish content/notes/reading-notes/index.md --open
```

Publish saved site changes without changing any draft flags:

```sh
./scripts/blog publish
```

The command builds and validates, commits eligible site changes, synchronizes with `origin/main`, validates the synchronized result, pushes, and follows the Pages workflow when GitHub CLI is signed in. It does not force-push or automatically resolve conflicts. A successful push and a successful deployment are reported separately.

Publishing includes other saved changes in the permitted site directories. Review `./scripts/blog status` before publishing. `draft: true` prevents a page from appearing on the website; files committed to this public source repository are still publicly readable.

## Content conventions

```text
content/
├── posts/<english-slug>/index.md   # Technology
├── notes/<english-slug>/index.md   # Reading and reflections
├── travel/<english-slug>/index.md  # Travel and photography
├── about/index.md
└── archives/_index.md
```

Keep an article and its images in the same page bundle. Use ordinary Markdown links rather than Obsidian wiki links. Use `contentLanguage: zh-CN` for Chinese articles. The interface stays English; `hasCJKLanguage = true` enables appropriate CJK word counting.

Use `\(...\)` for inline mathematics and `$$...$$` or `\[...\]` for display mathematics. Do not add a `katex` shortcode. The site renders formulas during the Hugo build and does not load a browser-side mathematics engine.

Use the custom `photo-gallery` shortcode for a lightbox gallery, as documented in [WRITING.md](docs/WRITING.md). The shortcode name intentionally differs from Blowfish's `gallery`, which would load its separate Packery implementation.

## Maintenance

Commit source, configuration, templates, scripts, and the theme submodule pointer. Do not commit generated `public/`, `resources/_gen/`, preview state, editor state, or credentials. The deployment workflow builds the site from source.

Theme and Hugo upgrades are deliberate changes: create a branch, update one component at a time, build, run the checker, and inspect desktop/mobile pages before merging. Keep published dates, slugs, and aliases stable. See [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) for the configuration audit, deployment checklist, rollback procedure, and known limitations.

Giscus comments are optional and disabled. Enabling them requires the repository's Discussions configuration, installation of the Giscus GitHub App, and verified repository/category identifiers; no placeholder comment service is shipped as an active feature.
