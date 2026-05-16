# Public Bug Bounty Programs Database

This repository contains a **detailed, searchable** collection of public bug bounty programs and vulnerability disclosure programs (VDPs).

The data is automatically aggregated from open-source lists such as [ProjectDiscovery](https://github.com/projectdiscovery/public-bugbounty-programs) and [Disclose.io](https://github.com/disclose/diodb).

## View the site

🔗 **GitHub Pages URL:** https://shubhk0.github.io/Publicbbp/

The site lists each program with its name, policy URL, bounty status, swag status, and scope domains, formatted for quick scanning and searching.

## Updating the data

A GitHub Actions workflow (`.github/workflows/gh-pages.yml`) runs daily (and on every push) to:
1. Fetch the latest open-source bug bounty data.
2. Generate a static HTML site.
3. Publish the updated site to the `gh-pages` branch.

You can also run the scripts manually:
```bash
# Fetch and merge the latest data into data/programs.json
python3 scripts/fetch_data.py

# Generate docs/index.html
python3 scripts/generate_site.py
```
