# Writing and maintenance rules for this site

These rules exist so the site stays crawlable and its URLs stay stable
(see the SEO section of the site plan). CI runs `scripts/check.py` on
every build; a red gate blocks deployment.

## URLs

- Post permalinks are **final**: `/posts/:year/:slug/`. Never change the
  permalink pattern in `hugo.toml`, and never rename a published slug.
- If a slug absolutely must change, add the old URL under `aliases:` in
  the post's front matter so Hugo emits a redirect page.
- Slugs: lowercase, hyphens, English words or pinyin. No dates inside the
  slug (the year comes from `date`).

## Front matter (every post)

Create posts with `hugo new posts/<year>/<slug>.md` so the archetype
supplies the fields. Required:

| Field | Rule |
|---|---|
| `title` | Unique across the site |
| `date` | Publication date, `YYYY-MM-DD` |
| `slug` | Matches the file name |
| `description` | **Required.** One or two sentences, hand-written; it becomes the search-result snippet and the social-share text. Must be unique across the site — CI fails otherwise |
| `tags` | **Do not use.** Tagging is disabled site-wide (`disableKinds` in `hugo.toml`, so no `/tags/` pages exist); omit the field entirely |
| `draft` | `true` while writing, `false` to publish |

## Content

- Exactly one `#` (h1) per page — the template renders the title as the
  h1, so start body headings at `##` and do not skip levels.
- Every post links to **at least two** other pages on this site
  (related older post, the front page, a Publications anchor). When a new post
  supersedes an old one, add a backlink in the old post too.
- Numbers and claims carry their sources (links), as in the rest of the
  owner's work.

## Images

- Put images next to the post (page bundle) or in `static/img/`.
- File names are descriptive English phrases (`riscv-pipeline-diagram.png`),
  never `IMG_1234.png` or screenshots with timestamp names.
- Every image gets meaningful `alt` text; the templates/checker require
  `width` and `height` attributes too (CI enforces alt + dimensions on
  raw `<img>` tags — prefer Markdown images via the render hook or write
  the attributes explicitly).
- Keep per-post image weight low; compress before committing.

## Front-page data

- Front-page cards render from `data/publications.yaml`,
  `awards.yaml`. Update the YAML, not the template.
- Text fields are `{en, zh}` maps. v1 renders `en` only and renders it as
  complete HTML (crawler constraint); `zh` may be filled ahead of a
  future language toggle, which must never hide content behind JS.
- An empty list hides its card. Do not invent entries: publications,
  experience, and awards only get real, confirmed items.

## Theme

- Hand-written, minimal: system font stack, one CSS file, no external
  fonts, no JavaScript frameworks, no trackers, no comments in v1.
- All SEO metadata lives in `layouts/partials/head.html` — change it
  there, never per-template.
- Content must be fully readable with JavaScript disabled.
