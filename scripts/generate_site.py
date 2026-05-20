#!/usr/bin/env python3
"""
Site Generator for Bug Bounty Aggregator.
Generates a modern static site with search, sort, and filter.
All HTML/CSS/JS is embedded - no external dependencies needed.
"""

import json
import logging
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
PROGRAMS_FILE = DATA_DIR / "programs.json"
CHANGELOG_FILE = DATA_DIR / "changelog.json"
DOCS_DIR = REPO_DIR / "docs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_data():
    programs = {"metadata": {}, "programs": []}
    changelog = {"entries": []}
    try:
        if PROGRAMS_FILE.exists():
            with open(PROGRAMS_FILE, "r") as f:
                programs = json.load(f)
            if not isinstance(programs.get("programs"), list):
                logger.error("programs.json has unexpected structure: missing 'programs' list")
                programs = {"metadata": {}, "programs": []}
        else:
            logger.warning("Programs file not found: %s", PROGRAMS_FILE)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse programs.json: %s", e)
    except OSError as e:
        logger.error("Failed to read programs.json: %s", e)

    try:
        if CHANGELOG_FILE.exists():
            with open(CHANGELOG_FILE, "r") as f:
                changelog = json.load(f)
        else:
            logger.warning("Changelog file not found: %s", CHANGELOG_FILE)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse changelog.json: %s", e)
    except OSError as e:
        logger.error("Failed to read changelog.json: %s", e)

    return programs, changelog


def get_css():
    return """
*{margin:0;padding:0;box-sizing:border-box}
:root{--primary:#6366f1;--primary-dark:#4f46e5;--bg:#0f172a;--bg-card:#1e293b;
--bg-hover:#334155;--text:#f1f5f9;--text-muted:#94a3b8;--border:#334155;
--success:#22c55e;--warning:#f59e0b;--danger:#ef4444;--info:#3b82f6}

[data-theme="light"]{--bg:#f8fafc;--bg-card:#ffffff;--bg-hover:#f1f5f9;
--text:#0f172a;--text-muted:#64748b;--border:#e2e8f0}

@media(prefers-color-scheme:light){
:root:not([data-theme="dark"]){--bg:#f8fafc;--bg-card:#ffffff;--bg-hover:#f1f5f9;
--text:#0f172a;--text-muted:#64748b;--border:#e2e8f0}
}

.skip-link{position:absolute;top:-40px;left:0;background:var(--primary);color:#fff;
padding:0.5rem 1rem;z-index:1000;font-size:0.9rem;border-radius:0 0 0.5rem 0;
transition:top 0.2s}
.skip-link:focus{top:0}

body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh}
a{color:var(--primary);text-decoration:none}
a:hover{text-decoration:underline}
.container{max-width:1400px;margin:0 auto;padding:0 1.5rem}
header{background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);
border-bottom:1px solid var(--border);padding:1.5rem 0;position:sticky;top:0;z-index:100}
[data-theme="light"] header{background:linear-gradient(135deg,#ffffff 0%,#f8fafc 100%)}
@media(prefers-color-scheme:light){:root:not([data-theme="dark"]) header{background:linear-gradient(135deg,#ffffff 0%,#f8fafc 100%)}}
.header-content{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem}
.logo{display:flex;align-items:center;gap:0.75rem}
.logo h1{font-size:1.75rem;background:linear-gradient(135deg,var(--primary),#a78bfa);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800}
.logo .badge{font-size:0.7rem;color:var(--text-muted);background:var(--bg-hover);
padding:0.2rem 0.6rem;border-radius:9999px}
.stats-bar{display:flex;gap:2rem;flex-wrap:wrap;align-items:center}
.stat-value{font-size:1.5rem;font-weight:700;color:var(--primary)}
.stat-label{font-size:0.7rem;color:var(--text-muted);text-transform:uppercase}
#theme-toggle{background:var(--bg-card);border:1px solid var(--border);color:var(--text);
padding:0.5rem 0.75rem;border-radius:0.5rem;cursor:pointer;font-size:1rem;
transition:all 0.2s}
#theme-toggle:hover{border-color:var(--primary);background:var(--bg-hover)}

.controls{padding:1.5rem 0;display:flex;flex-wrap:wrap;gap:1rem;align-items:center}
.search-box{flex:1;min-width:250px;position:relative}
.search-box input{width:100%;padding:0.75rem 1rem 0.75rem 2.5rem;background:var(--bg-card);
border:1px solid var(--border);border-radius:0.5rem;color:var(--text);font-size:0.9rem;
outline:none;transition:border-color 0.2s}
.search-box input:focus{border-color:var(--primary)}
.search-box::before{content:"\\1F50D";position:absolute;left:0.75rem;top:50%;
transform:translateY(-50%);font-size:1rem}
select{padding:0.75rem 1rem;background:var(--bg-card);border:1px solid var(--border);
border-radius:0.5rem;color:var(--text);font-size:0.85rem;cursor:pointer;outline:none}
select:focus{border-color:var(--primary)}
.btn{padding:0.75rem 1.25rem;border-radius:0.5rem;border:1px solid var(--border);
background:var(--bg-card);color:var(--text);cursor:pointer;font-size:0.85rem;
transition:all 0.2s}
.btn:hover{background:var(--bg-hover);border-color:var(--primary)}
.btn.active{background:var(--primary);border-color:var(--primary);color:white}

.tabs{display:flex;gap:0.5rem;margin-bottom:1rem;border-bottom:1px solid var(--border);
padding-bottom:0.5rem}
.tab{padding:0.5rem 1rem;border-radius:0.5rem 0.5rem 0 0;cursor:pointer;color:var(--text-muted);
font-size:0.9rem;transition:all 0.2s;border:none;background:none}
.tab:hover{color:var(--text)}
.tab.active{color:var(--primary);border-bottom:2px solid var(--primary);font-weight:600}
.programs-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:1rem;
padding:1rem 0 3rem}
.program-card{background:var(--bg-card);border:1px solid var(--border);border-radius:0.75rem;
padding:1.25rem;transition:all 0.2s;cursor:pointer;position:relative;overflow:hidden;
text-decoration:none;color:inherit;display:block}
.program-card:hover{border-color:var(--primary);transform:translateY(-2px);
box-shadow:0 8px 25px rgba(99,102,241,0.1);text-decoration:none}
.card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem}
.card-name{font-size:1.05rem;font-weight:600;color:var(--text)}
.card-platform{font-size:0.7rem;padding:0.2rem 0.5rem;border-radius:9999px;
font-weight:500;text-transform:uppercase;letter-spacing:0.03em}

.platform-hackerone{background:#494d5f;color:#fff}
.platform-bugcrowd{background:#f06a24;color:#fff}
.platform-intigriti{background:#3b82f6;color:#fff}
.platform-yeswehack{background:#e11d48;color:#fff}
.platform-immunefi{background:#6366f1;color:#fff}
.platform-independent{background:#22c55e;color:#fff}
.platform-hackenproof{background:#8b5cf6;color:#fff}
.platform-openbugbounty{background:#f59e0b;color:#000}
.card-bounty{display:flex;align-items:baseline;gap:0.5rem;margin:0.5rem 0}
.bounty-amount{font-size:1.25rem;font-weight:700;color:var(--success)}
.bounty-range{font-size:0.8rem;color:var(--text-muted)}
.card-meta{display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.75rem}
.meta-tag{font-size:0.7rem;padding:0.15rem 0.5rem;background:var(--bg-hover);
border-radius:9999px;color:var(--text-muted)}
.card-assets{margin-top:0.75rem;font-size:0.75rem;color:var(--text-muted)}
.card-assets code{background:var(--bg);padding:0.1rem 0.4rem;border-radius:0.25rem;
font-size:0.7rem;margin-right:0.25rem}

.changelog-section{padding:1rem 0 3rem}
.changelog-item{display:flex;gap:1rem;padding:0.75rem 1rem;border-left:3px solid var(--border);
margin-bottom:0.5rem;background:var(--bg-card);border-radius:0 0.5rem 0.5rem 0}
.changelog-item.added{border-left-color:var(--success)}
.changelog-item.removed{border-left-color:var(--danger)}
.changelog-item.updated{border-left-color:var(--warning)}
.changelog-type{font-size:0.7rem;font-weight:600;text-transform:uppercase;padding:0.1rem 0.5rem;
border-radius:9999px;white-space:nowrap;height:fit-content}
.type-added{background:rgba(34,197,94,0.1);color:var(--success)}
.type-removed{background:rgba(239,68,68,0.1);color:var(--danger)}
.type-updated{background:rgba(245,158,11,0.1);color:var(--warning)}
.changelog-details{flex:1}
.changelog-name{font-weight:600;font-size:0.9rem}
.changelog-desc{font-size:0.8rem;color:var(--text-muted)}
.changelog-time{font-size:0.7rem;color:var(--text-muted);white-space:nowrap}
.empty-state{text-align:center;padding:4rem 2rem;color:var(--text-muted)}
.empty-state h3{font-size:1.2rem;margin-bottom:0.5rem}
footer{padding:2rem 0;border-top:1px solid var(--border);text-align:center;
color:var(--text-muted);font-size:0.8rem}
.results-count{font-size:0.85rem;color:var(--text-muted);padding:0.5rem 0}
@media(max-width:768px){
.programs-grid{grid-template-columns:1fr}
.header-content{flex-direction:column;align-items:flex-start}
.controls{flex-direction:column}
.search-box{min-width:100%}
}
"""



def get_js():
    return """
let allPrograms = [];
let changelog = [];
let currentSort = 'bounty_desc';
let currentView = 'programs';

function init(programsData, changelogData) {
    allPrograms = programsData;
    changelog = changelogData;
    initTheme();
    render();
    setupListeners();
}

function initTheme() {
    const saved = localStorage.getItem('bbr-theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
    }
    updateThemeButton();
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    let newTheme;
    if (current === 'light') {
        newTheme = 'dark';
    } else if (current === 'dark') {
        newTheme = 'light';
    } else {
        // No explicit theme set, detect current preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        newTheme = prefersDark ? 'light' : 'dark';
    }
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('bbr-theme', newTheme);
    updateThemeButton();
}

function updateThemeButton() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    const current = document.documentElement.getAttribute('data-theme');
    if (current === 'light') {
        btn.textContent = '\\u263D';
        btn.title = 'Switch to dark mode';
    } else if (current === 'dark') {
        btn.textContent = '\\u2600';
        btn.title = 'Switch to light mode';
    } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        btn.textContent = prefersDark ? '\\u2600' : '\\u263D';
        btn.title = prefersDark ? 'Switch to light mode' : 'Switch to dark mode';
    }
}

function setupListeners() {
    document.getElementById('search').addEventListener('input', debounce(render, 200));
    document.getElementById('platform-filter').addEventListener('change', render);
    document.getElementById('category-filter').addEventListener('change', render);
    document.getElementById('type-filter').addEventListener('change', render);
    document.getElementById('sort-select').addEventListener('change', function() {
        currentSort = this.value;
        render();
    });
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            currentView = this.dataset.view;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            render();
        });
    });
}

function debounce(fn, ms) {
    let timer;
    return function(...args) { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
}


function getFiltered() {
    const query = document.getElementById('search').value.toLowerCase();
    const platform = document.getElementById('platform-filter').value;
    const category = document.getElementById('category-filter').value;
    const type = document.getElementById('type-filter').value;

    let filtered = allPrograms.filter(p => {
        if (query && !p.name.toLowerCase().includes(query) &&
            !p.platform.toLowerCase().includes(query) &&
            !(p.assets||[]).join(' ').toLowerCase().includes(query) &&
            !p.category.toLowerCase().includes(query)) return false;
        if (platform && p.platform !== platform) return false;
        if (category && p.category !== category) return false;
        if (type && p.type !== type) return false;
        return true;
    });

    // Sort
    switch(currentSort) {
        case 'bounty_desc': filtered.sort((a,b) => (b.bounty_max||0) - (a.bounty_max||0)); break;
        case 'bounty_asc': filtered.sort((a,b) => (a.bounty_max||0) - (b.bounty_max||0)); break;
        case 'name_asc': filtered.sort((a,b) => a.name.localeCompare(b.name)); break;
        case 'name_desc': filtered.sort((a,b) => b.name.localeCompare(a.name)); break;
        case 'platform': filtered.sort((a,b) => a.platform.localeCompare(b.platform)); break;
    }
    return filtered;
}


function render() {
    if (currentView === 'changelog') {
        renderChangelog();
    } else {
        renderPrograms();
    }
}

function renderPrograms() {
    const filtered = getFiltered();
    const grid = document.getElementById('programs-grid');
    const count = document.getElementById('results-count');
    count.textContent = filtered.length + ' program' + (filtered.length !== 1 ? 's' : '') + ' found';

    if (filtered.length === 0) {
        grid.innerHTML = '<div class="empty-state"><h3>No programs found</h3><p>Try adjusting your filters or search query.</p></div>';
        return;
    }

    grid.innerHTML = filtered.map(p => {
        const platformClass = 'platform-' + p.platform.toLowerCase().replace(/[^a-z]/g, '');
        const bountyDisplay = p.bounty_max > 0
            ? `<div class="card-bounty"><span class="bounty-amount">$${formatNumber(p.bounty_max)}</span><span class="bounty-range">max bounty${p.bounty_min > 0 ? ' (min $'+formatNumber(p.bounty_min)+')' : ''}</span></div>`
            : `<div class="card-bounty"><span class="bounty-range">VDP - No monetary reward</span></div>`;
        const assets = (p.assets||[]).slice(0,5).map(a => `<code>${escapeHtml(a)}</code>`).join(' ');
        const url = escapeHtml(p.url);
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="program-card" role="listitem">
            <div class="card-header">
                <span class="card-name">${escapeHtml(p.name)}</span>
                <span class="card-platform ${platformClass}">${escapeHtml(p.platform)}</span>
            </div>
            ${bountyDisplay}
            <div class="card-meta">
                <span class="meta-tag">${escapeHtml(p.category)}</span>
                <span class="meta-tag">${p.type === 'bounty' ? '\\u{1F4B0} Paid' : '\\u{1F4CB} VDP'}</span>
                ${p.managed ? '<span class="meta-tag">\\u2713 Managed</span>' : ''}
            </div>
            ${assets ? '<div class="card-assets">' + assets + '</div>' : ''}
        </a>`;
    }).join('');

    document.getElementById('content-programs').style.display = 'block';
    document.getElementById('content-changelog').style.display = 'none';
}


function renderChangelog() {
    const container = document.getElementById('changelog-list');
    document.getElementById('content-programs').style.display = 'none';
    document.getElementById('content-changelog').style.display = 'block';

    if (changelog.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No changes yet</h3><p>Changes will appear here after the next data update.</p></div>';
        return;
    }

    container.innerHTML = changelog.map(entry => {
        const typeClass = 'type-' + entry.type;
        const itemClass = entry.type;
        const time = entry.timestamp ? new Date(entry.timestamp).toLocaleDateString() : '';
        return `<div class="changelog-item ${itemClass}">
            <span class="changelog-type ${typeClass}">${entry.type}</span>
            <div class="changelog-details">
                <div class="changelog-name">${escapeHtml(entry.program_name)} <small>(${escapeHtml(entry.platform)})</small></div>
                <div class="changelog-desc">${escapeHtml(entry.details)}</div>
            </div>
            <span class="changelog-time">${time}</span>
        </div>`;
    }).join('');
}

function formatNumber(n) {
    if (n >= 1000000) return (n/1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n/1000).toFixed(0) + 'K';
    return n.toString();
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
"""



def get_html(css, js, programs_json, changelog_json, total, num_platforms,
             num_categories, last_updated, cat_options, plat_options):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BBRadar - Public Bug Bounty Programs Aggregator</title>
<meta name="description" content="Comprehensive aggregator of public bug bounty programs. Search, sort, and filter.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x1F3AF;</text></svg>">
<style>{css}</style>
</head>
<body>
<a href="#main-content" class="skip-link">Skip to main content</a>
<header>
<div class="container header-content">
<div class="logo">
<h1>&#x1F3AF; BBRadar</h1>
<span class="badge">Public Bug Bounty Aggregator</span>
</div>
<div class="stats-bar">
<div class="stat"><div class="stat-value">{total}</div><div class="stat-label">Programs</div></div>
<div class="stat"><div class="stat-value">{num_platforms}</div><div class="stat-label">Platforms</div></div>
<div class="stat"><div class="stat-value">{num_categories}</div><div class="stat-label">Categories</div></div>
<button id="theme-toggle" aria-label="Toggle light/dark mode">&#x263D;</button>
</div>
</div>
</header>

<main id="main-content" class="container">
<div class="controls">
<div class="search-box">
<input type="text" id="search" placeholder="Search programs, platforms, assets..." aria-label="Search programs">
</div>
<select id="platform-filter" aria-label="Filter by platform">
<option value="">All Platforms</option>
{plat_options}
</select>
<select id="category-filter" aria-label="Filter by category">
<option value="">All Categories</option>
{cat_options}
</select>
<select id="type-filter" aria-label="Filter by type">
<option value="">All Types</option>
<option value="bounty">Paid Bounty</option>
<option value="vdp">VDP (No Pay)</option>
</select>
<select id="sort-select" aria-label="Sort programs">
<option value="bounty_desc">Bounty: High to Low</option>
<option value="bounty_asc">Bounty: Low to High</option>
<option value="name_asc">Name: A-Z</option>
<option value="name_desc">Name: Z-A</option>
<option value="platform">Platform</option>
</select>
</div>

<div class="tabs">
<button class="tab active" data-view="programs">Programs</button>
<button class="tab" data-view="changelog">Latest Changes</button>
</div>

<div id="content-programs">
<div id="results-count" class="results-count"></div>
<div id="programs-grid" class="programs-grid" role="list"></div>
</div>

<div id="content-changelog" style="display:none">
<div id="changelog-list" class="changelog-section"></div>
</div>
</main>

<footer>
<div class="container">
<p>BBRadar - Open Source Bug Bounty Aggregator | Data updated: {last_updated}</p>
<p>Data sourced from public program listings. No API keys used.</p>
<p><a href="https://github.com/Shubhk0/Publicbbp">GitHub Repository</a></p>
</div>
</footer>

<script>
{js}
const PROGRAMS = {programs_json};
const CHANGELOG = {changelog_json};
document.addEventListener('DOMContentLoaded', () => init(PROGRAMS, CHANGELOG));
</script>
</body>
</html>'''



def main():
    programs_data, changelog_data = load_data()
    programs = programs_data.get("programs", [])
    metadata = programs_data.get("metadata", {})
    changelog = changelog_data.get("entries", [])[:50]

    total = len(programs)
    platforms = sorted(set(p["platform"] for p in programs))
    categories = sorted(set(p["category"] for p in programs))
    last_updated = metadata.get("last_updated", "Unknown")

    programs_json = json.dumps(programs, ensure_ascii=False)
    changelog_json = json.dumps(changelog, ensure_ascii=False)

    cat_options = "".join(f'<option value="{c}">{c}</option>' for c in categories)
    plat_options = "".join(f'<option value="{p}">{p}</option>' for p in platforms)

    css = get_css()
    js = get_js()

    html = get_html(
        css=css, js=js,
        programs_json=programs_json,
        changelog_json=changelog_json,
        total=total,
        num_platforms=len(platforms),
        num_categories=len(categories),
        last_updated=last_updated,
        cat_options=cat_options,
        plat_options=plat_options,
    )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    html_path = DOCS_DIR / "index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] Generated site at {html_path}")
    print(f"    {total} programs | {len(platforms)} platforms | {len(categories)} categories")


if __name__ == "__main__":
    main()
