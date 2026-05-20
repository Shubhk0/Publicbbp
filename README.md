# BBRadar - Public Bug Bounty Programs Aggregator

A comprehensive, open-source aggregator of public bug bounty programs from all major platforms. Think of it as your personal [bbradar.io](https://bbradar.io) - fully open source, self-hosted via GitHub Pages.

## Live Site

**https://shubhk0.github.io/Publicbbp/**

## Features

- **55+ programs** from 6+ platforms (HackerOne, Bugcrowd, Intigriti, YesWeHack, Immunefi, Independent)
- **Real-time search** - filter by name, platform, assets, or category
- **Sort** by bounty amount, name, or platform
- **Filter** by platform, category (15+ categories), and program type (paid/VDP)
- **Changelog tracking** - see what programs were added, removed, or updated
- **Auto-updates** every 6 hours via GitHub Actions
- **No API keys required** - all data fetched via public scraping and open data sources
- **Dark mode UI** - modern, responsive design

## Architecture

```
Publicbbp/
├── data/
│   ├── programs.json        # Main program database
│   └── changelog.json       # Track additions/removals/updates
├── docs/
│   └── index.html           # Generated static site (GitHub Pages)
├── scripts/
│   ├── aggregate.py         # Data aggregation (scraping, no API keys)
│   └── generate_site.py     # Static site generator
└── .github/workflows/
    └── gh-pages.yml         # Auto-update & deploy every 6 hours
```

## Data Sources (No API Keys)

1. **Seed Data** - Curated list of 55+ verified programs with bounty ranges
2. **bounty-targets-data** - Hourly-updated dumps from [arkadiyt/bounty-targets-data](https://github.com/arkadiyt/bounty-targets-data)
3. **Direct scraping** - Public program directory pages (no auth needed)

## How It Works

1. `aggregate.py` runs and collects programs from all sources
2. Deduplicates, enriches, and categorizes programs
3. Compares with previous data to generate changelog entries
4. `generate_site.py` builds a static HTML site with embedded JS
5. GitHub Actions deploys to GitHub Pages automatically

## Running Locally

```bash
# Aggregate data
python3 scripts/aggregate.py

# Generate site
python3 scripts/generate_site.py

# Open the site
open docs/index.html
```

## Program Categories

| Category | Examples |
|----------|----------|
| Technology | Google, Microsoft, GitHub, GitLab |
| Cryptocurrency | Coinbase, Wormhole, MakerDAO |
| Finance | PayPal, Mastercard, LCL |
| Social Media | Meta, Twitter/X, Snapchat, TikTok |
| Gaming | Valve/Steam, Sony PlayStation |
| Government | U.S. DoD, Swiss Post, Quebec |
| AI/ML | OpenAI |
| Automotive | Tesla |
| And more... | Healthcare, E-commerce, Security, Entertainment |

## Contributing

1. Add programs to the `KNOWN_PROGRAMS` list in `scripts/aggregate.py`
2. Run the aggregation: `python3 scripts/aggregate.py`
3. Generate site: `python3 scripts/generate_site.py`
4. Submit a PR!

## License

MIT - See [LICENSE](LICENSE) for details.
