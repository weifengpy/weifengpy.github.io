# weifengpy.github.io

Personal homepage + blog of **Wei Feng** (weifengpy on GitHub), built with [Hugo](https://gohugo.io/)
(extended, pinned version below) and hosted on GitHub Pages.
One repository, one site: the front page is the profile — bio and
publications (the former About page; `/about/` redirects there); the
blog post list lives on `/posts/`.

Live site: https://weifengpy.github.io/

Content note: the bio, experience, and publications content was
consolidated on 2026-10-21 from the previous Google Sites homepage
(sites.google.com/site/weifengdm). LinkedIn details — job title, the
September 2019 start at Meta, and the Highlights wording — follow a
screenshot the owner provided on 2026-10-21; the public LinkedIn page
itself sits behind a login wall and was not read directly.

## Toolchain

- Hugo **v0.168.0 extended** (same version pinned as `HUGO_VERSION` in
  `.github/workflows/hugo.yml`). Install from the official GitHub release
  `hugo_extended_0.168.0_<platform>.tar.gz` and verify against the release
  checksums file.
- Python 3 (only for the SEO gate script).
- No Node, no npm, no external fonts or JavaScript frameworks.

## Local preview

```sh
hugo server            # http://localhost:1313/  (drafts hidden)
hugo server -D         # include drafts
```

## Build + checks (what CI runs)

```sh
hugo --gc --minify
python3 scripts/check.py public   # SEO gate: descriptions, canonicals,
                                  # image alt/size, JSON-LD, sitemap
```

## Deployment

Push to `main`. The GitHub Actions workflow in `.github/workflows/hugo.yml`
builds the site, runs the SEO gate, and deploys to GitHub Pages
(build type: workflow). Nothing is deployed by hand.

## Layout of this repo

| Path | What |
|---|---|
| `hugo.toml` | Site config. Permalinks for posts are **final**: `/posts/:year/:slug/` |
| `content/posts/` | Blog posts (Markdown, one folder per year) |
| `content/_index.md` | Front page: the profile (bio text; the cards below it come from `data/`) |
| `content/about.md` | Redirect stub: `/about/` forwards to the front page |
| `data/` | Front-page cards as data: `publications.yaml`, `awards.yaml`. Edit these to update the front page; empty lists hide their card. Text fields use `{en, zh}` keys; v1 renders `en` only |
| `layouts/` | Hand-written minimal theme (no external theme). `partials/head.html` owns all SEO metadata |
| `assets/css/main.css` | The single stylesheet (Hugo pipeline: minify + fingerprint) |
| `static/` | Files copied verbatim (favicon, future CV/avatar) |
| `scripts/check.py` | SEO gate over the built output |
| `CLAUDE.md` | Writing rules for posts (front matter, links, images) |
| `archetypes/default.md` | `hugo new posts/<year>/<name>.md` template |

## Color themes

The site ships a light and a dark theme. The default choice is
automatic, and a toggle button in the header
overrides it. The rule:

- **A manual choice wins.** The toggle's label names the theme it will
  switch to. Clicking it flips the theme at once and stores the choice
  in `localStorage` under the key `theme`; the choice survives reloads
  and navigation, and the automatic boundary re-checks never override
  it. To return to automatic, clear that key (for example run
  `localStorage.removeItem("theme")` in the browser console) and reload.
- Otherwise, with JavaScript, a tiny inline script in `<head>` sets
  `data-theme` on `<html>` from the **visitor's local time** before
  first paint: light from 07:00 to 18:59, dark from 19:00 to 06:59.
  While a page stays open it re-checks at the next 07:00 / 19:00
  boundary and switches live.
- Without JavaScript, CSS falls back to the **device preference**
  (`@media (prefers-color-scheme: dark)`); the toggle button is then
  inert.
- If the time and device signals disagree, **time wins** (it is the
  more dynamic of the two signals). To change the hours, edit the
  `pick()` function in `layouts/partials/head.html`.

Both palettes live in `assets/css/main.css` as CSS variables on `:root`
(light) and `:root[data-theme="dark"]`; both meet WCAG AA contrast for
body text and links (at least 4.5:1). `meta theme-color` starts per-scheme in
`layouts/partials/head.html`; the inline script re-points it at the
active theme whenever the theme is applied or toggled.

## Writing a post

```sh
hugo new posts/2026/my-post.md   # then set description + tags, draft: false
```

See `CLAUDE.md` for the rules CI enforces (description required, internal
links, image alt text, stable slugs).

## TODO (owner to fill in)

- [x] Real name / display name — site now shows **Wei Feng**
- [x] One-line bio and current affiliation/employer — bio filled from
      the previous homepage and the owner's LinkedIn screenshot
- [ ] Avatar photo (goes to `static/`, referenced from the front page)
- [ ] CV PDF (goes to `static/`, linked from the front page)
- [x] Email address — published on the site (fengwei824@gmail.com, as
      listed on the previous homepage)
- [x] Fill `data/publications.yaml` —
      consolidated from the previous homepage on 2026-10-21
- [ ] Fill `data/awards.yaml` with confirmed entries (still empty; the
      card stays hidden until then)
- [x] Add the Google Scholar profile link — the previous homepage did
      not expose an exact profile URL, so none was invented
- [ ] Fill the remaining `zh` fields in `data/*.yaml` (bio zh filled; publications pending) and add a
      language toggle to the site
- [ ] Submit the sitemap in Google Search Console and Bing Webmaster Tools,
      and add the Search Console verification meta tag to `partials/head.html`
- [ ] Later, optionally: custom domain (add `CNAME`, change `baseURL` in
      `hugo.toml` and `BASE` in `scripts/check.py`; GitHub redirects the old
      github.io URLs)
