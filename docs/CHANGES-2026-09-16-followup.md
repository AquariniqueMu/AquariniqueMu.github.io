# Functional sections and profile update — 2026-09-16

This revision supersedes the navigation and cover behavior in the earlier presentation update.

## Navigation and content

- **Posts** (`/posts/`) lists every published article across Tech, Notes, and Daily, newest first. Its RSS feed includes the same articles as the homepage feed.
- **Tech** (`/tech/`) contains technical articles, **Notes** (`/notes/`) accepts notes of any kind, and **Daily** (`/daily/`) contains everyday life and travel.
- The navigation is **Posts · Tech · Notes · Daily · Tags · About · appearance · search**, with 14px desktop link text.
- Existing technical article URLs remain under `/posts/YYYY/MM/DD/slug/`. New source bundles live in `content/tech/`.
- Travel source bundles moved to `content/daily/`. The old `/travel/` listing and dated travel article URL redirect to Daily. Original migration aliases remain.
- The old `/travel/index.xml` subscription continues to serve Daily entries. Its compatibility section emits RSS only and is excluded from search, lists, and the sitemap.
- The English introduction “A quieter home for these notes” was removed from the website, feeds, and search. Four published articles and one unpublished draft remain.
- New Draft and the CLI now create `tech`, `notes`, or `daily` bundles. Posts is an aggregate, not a draft category.

## Appearance

- The homepage profile includes the supplied photo, **Junwen**, GitHub and Blog links, with a circular avatar and a soft shadow. Its desktop size is 144px; phones use 128px. Hugo publishes an optimized 320px WebP.
- Intro: “This is Junwen. I'm documenting what I learn, what I read, and what I experience along the way.” The earlier aside about curiosity and languages was removed.
- Markdown blockquote borders and links, tag borders/text, profile links, and Show More use the same purple variables. Show More links to Posts.
- Cover photos occupy a fixed layer across the **entire viewport**, including page margins and the area behind navigation. `object-fit: cover` preserves proportions while cropping to fill the screen. The background stays in place while scrolling; it does not occupy article space. Opacity is 10% in light mode and 8% in dark mode.

## Avatar editing record

The built-in imagegen tool was used to color grade the user-supplied dog photograph. The project asset is `assets/img/avatar-graded.png`. The original attachment is unchanged. Website CSS supplies the round crop and shadow.

Prompt:

> Use case: lighting-weather. Edit target: the supplied real photograph of a small sleeping white long-haired dog nestled in pink and white blankets. Asset: personal blog avatar. Change ONLY photographic color grading: neutral creamy whites, gently reduce the yellow/gray cast, slightly soften the pink saturation, modestly lift shadow detail and add subtle clean contrast. Keep the same dog, identical facial anatomy, closed eyes, black nose, fur, pose, blankets, toys, composition, all object details and photoreal texture. Do not replace, regenerate, retouch anatomy, or add any objects. Keep the entire original photograph framing. No text, no border, no graphic shadow; circular cropping and shadow will be added by the website CSS. Natural, tender, quiet editorial photo.

## Validation

The production checker verifies that Posts and its feed contain all published articles in date order. The removed introduction contained the only published math examples, so the checker no longer requires two formulas in live content; the native MathML hook and prohibition of client-side math remain in place. Final build and browser checks are recorded in [VALIDATION.md](VALIDATION.md).
