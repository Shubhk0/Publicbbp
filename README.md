# Public Bug Bounty Programs Database

This repository contains a **detailed, easy‑to‑read** collection of public bug bounty programs.

- The data is stored in `bugbounty_programs_details.md`.
- A GitHub Actions workflow (`.github/workflows/gh-pages.yml`) runs daily (and on every push) to generate a static HTML site from the markdown.
- The generated site is published to the `gh-pages` branch and served via GitHub Pages.

## View the site

🔗 **GitHub Pages URL:** https://shubhk0.github.io/Publicbbp/

The site lists each program with its name, URL, scope, rewards, and guidelines, formatted for quick scanning.

## Updating the data

The workflow automatically refreshes the site daily. You can also push updates to the markdown file manually; the next workflow run will regenerate the HTML.

---
*Last updated: $(date +"%Y-%m-%d %H:%M:%S")*