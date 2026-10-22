# weifengpy.github.io

Personal homepage + blog of **weifengpy**, built with [Hugo](https://gohugo.io/)
(extended, pinned version below) and hosted on GitHub Pages.
One repository, one site: the front page is the homepage (project index,
publications, experience), `/posts/` is the blog.

Live site: https://weifengpy.github.io/

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
| `content/about.md` | About page |
| `data/` | Homepage cards as data: `projects.yaml`, `publications.yaml`, `experiences.yaml`, `awards.yaml`. Edit these to update the homepage; empty lists hide their card. Text fields use `{en, zh}` keys; v1 renders `en` only |
| `layouts/` | Hand-written minimal theme (no external theme). `partials/head.html` owns all SEO metadata |
| `assets/css/main.css` | The single stylesheet (Hugo pipeline: minify + fingerprint) |
| `static/` | Files copied verbatim (favicon, future CV/avatar) |
| `scripts/check.py` | SEO gate over the built output |
| `CLAUDE.md` | Writing rules for posts (front matter, links, images) |
| `archetypes/default.md` | `hugo new posts/<year>/<name>.md` template |

## Writing a post

```sh
hugo new posts/2026/my-post.md   # then set description + tags, draft: false
```

See `CLAUDE.md` for the rules CI enforces (description required, internal
links, image alt text, stable slugs).

## TODO (owner to fill in)

- [ ] Real name / display name (v1 shows the GitHub handle `weifengpy` only)
- [ ] One-line bio and current affiliation/employer, if desired
- [ ] Avatar photo (goes to `static/`, referenced from the Overview card)
- [ ] CV PDF (goes to `static/`, linked from About)
- [ ] Decide whether to publish an email address on About (v1: GitHub only)
- [ ] Fill `data/publications.yaml`, `data/experiences.yaml`, `data/awards.yaml`
      with confirmed entries (schemas are documented at the top of each file)
- [ ] Fill `zh` fields in `data/*.yaml` when the homepage gets a language toggle
- [ ] Submit the sitemap in Google Search Console and Bing Webmaster Tools,
      and add the Search Console verification meta tag to `partials/head.html`
- [ ] Later, optionally: custom domain (add `CNAME`, change `baseURL` in
      `hugo.toml` and `BASE` in `scripts/check.py`; GitHub redirects the old
      github.io URLs)
