# Zheng Zhou Homepage

This repository contains the source for Zheng Zhou's academic homepage, built with
[Quarto](https://quarto.org/) and deployed with GitHub Pages.

The site includes English and Chinese pages, publication and blog sections, custom
styling, GoatCounter analytics, and a visitor-location map generated from
GoatCounter country statistics.

## Project Structure

The repository keeps Quarto entry pages near the root, while shared static
assets live under `assets/`.

```text
.
├── _quarto.yml                 # English site configuration
├── index.qmd                   # English homepage
├── publications.qmd            # English publications page
├── blog.qmd                    # English blog index
├── links.qmd                   # English links page
├── posts/                      # English blog posts
├── zh/                         # Chinese site
│   ├── _quarto.yml             # Chinese site configuration
│   ├── index.qmd               # Chinese homepage
│   ├── publications.qmd
│   ├── blog.qmd
│   ├── links.qmd
│   └── posts/                  # Chinese blog posts
├── assets/
│   ├── images/                 # Profile and institution images
│   ├── includes/               # Shared HTML snippets
│   ├── styles/                 # Shared SCSS styles
│   └── data/                   # Generated visitor-location data
├── scripts/                    # Maintenance and data-update scripts
├── .github/workflows/          # GitHub Pages deployment workflow
├── LICENSE
└── README.md
```

Generated output is written to `_site/` and is not tracked in Git.

## Requirements

- [Quarto](https://quarto.org/docs/get-started/)
- Python 3.11 or newer, only needed for updating visitor-location data

## Local Development

Preview the English site:

```bash
quarto preview
```

Preview the Chinese site:

```bash
quarto preview zh
```

Render both sites:

```bash
quarto render
quarto render zh
```

The rendered output is written to `_site/`, with the Chinese site under
`_site/zh/`.

## Visitor Map Data

The visitor map reads from `assets/data/visitor-locations.json`. To update it
locally, set a GoatCounter API token and run:

```bash
export GOATCOUNTER_API_TOKEN="your-token"
export GOATCOUNTER_SITE_CODE="zhengzhou"
python scripts/update_visitor_locations.py
```

If no token is provided, the script writes an empty placeholder payload so the
site can still render. The generated JSON file is ignored by Git because it is
refreshed during deployment.

## Deployment

The GitHub Actions workflow in `.github/workflows/publish.yml` builds and deploys
the site to GitHub Pages when changes are pushed to `main`. It also runs on a
hourly schedule to refresh visitor-location data.

For the scheduled visitor updates to work, add `GOATCOUNTER_API_TOKEN` as a
repository secret.

## License

The source code for this website is licensed under the MIT License. See
[LICENSE](LICENSE) for details.

Personal content, academic text, photographs, logos, and third-party assets are
not covered by the MIT License unless explicitly stated otherwise.
