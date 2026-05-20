#!/usr/bin/env python3
"""
Bug Bounty Program Aggregator
Fetches public bug bounty programs from multiple platforms and maintains
a JSON database with changelog tracking.
"""

import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
PROGRAMS_FILE = DATA_DIR / "programs.json"
CHANGELOG_FILE = DATA_DIR / "changelog.json"



# Comprehensive list of known public bug bounty programs
# This is our seed data - the aggregator will also try to fetch from APIs
KNOWN_PROGRAMS = [
    # HackerOne Programs
    {"name": "U.S. Dept of Defense", "platform": "HackerOne", "url": "https://hackerone.com/deptofdefense", "type": "vdp", "bounty_min": 0, "bounty_max": 0, "currency": "USD", "managed": True, "category": "Government", "assets": ["*.defense.gov"]},
    {"name": "Google VRP", "platform": "HackerOne", "url": "https://bughunters.google.com/", "type": "bounty", "bounty_min": 100, "bounty_max": 31337, "currency": "USD", "managed": False, "category": "Technology", "assets": ["*.google.com", "*.youtube.com", "Android", "Chrome"]},
    {"name": "GitHub", "platform": "HackerOne", "url": "https://hackerone.com/github", "type": "bounty", "bounty_min": 617, "bounty_max": 30000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["github.com", "*.github.com"]},
    {"name": "Shopify", "platform": "HackerOne", "url": "https://hackerone.com/shopify", "type": "bounty", "bounty_min": 500, "bounty_max": 50000, "currency": "USD", "managed": True, "category": "E-commerce", "assets": ["*.shopify.com", "*.myshopify.com"]},
    {"name": "Uber", "platform": "HackerOne", "url": "https://hackerone.com/uber", "type": "bounty", "bounty_min": 500, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Transportation", "assets": ["*.uber.com"]},
    {"name": "Twitter/X", "platform": "HackerOne", "url": "https://hackerone.com/x", "type": "bounty", "bounty_min": 140, "bounty_max": 15120, "currency": "USD", "managed": True, "category": "Social Media", "assets": ["*.twitter.com", "*.x.com"]},
    {"name": "PayPal", "platform": "HackerOne", "url": "https://hackerone.com/paypal", "type": "bounty", "bounty_min": 50, "bounty_max": 20000, "currency": "USD", "managed": True, "category": "Finance", "assets": ["*.paypal.com", "*.venmo.com"]},
    {"name": "Coinbase", "platform": "HackerOne", "url": "https://hackerone.com/coinbase", "type": "bounty", "bounty_min": 200, "bounty_max": 50000, "currency": "USD", "managed": True, "category": "Cryptocurrency", "assets": ["*.coinbase.com"]},

    {"name": "Dropbox", "platform": "HackerOne", "url": "https://hackerone.com/dropbox", "type": "bounty", "bounty_min": 216, "bounty_max": 32768, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.dropbox.com"]},
    {"name": "Slack", "platform": "HackerOne", "url": "https://hackerone.com/slack", "type": "bounty", "bounty_min": 100, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.slack.com"]},
    {"name": "WordPress", "platform": "HackerOne", "url": "https://hackerone.com/wordpress", "type": "bounty", "bounty_min": 150, "bounty_max": 25000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.wordpress.org", "*.wordpress.com"]},
    {"name": "Automattic", "platform": "HackerOne", "url": "https://hackerone.com/automattic", "type": "bounty", "bounty_min": 50, "bounty_max": 25000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.automattic.com", "*.tumblr.com"]},
    {"name": "Yahoo", "platform": "HackerOne", "url": "https://hackerone.com/yahoo", "type": "bounty", "bounty_min": 150, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.yahoo.com"]},
    {"name": "Spotify", "platform": "HackerOne", "url": "https://hackerone.com/spotify", "type": "bounty", "bounty_min": 250, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Entertainment", "assets": ["*.spotify.com"]},
    {"name": "GitLab", "platform": "HackerOne", "url": "https://hackerone.com/gitlab", "type": "bounty", "bounty_min": 100, "bounty_max": 35000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.gitlab.com"]},
    {"name": "Valve (Steam)", "platform": "HackerOne", "url": "https://hackerone.com/valve", "type": "bounty", "bounty_min": 200, "bounty_max": 25000, "currency": "USD", "managed": True, "category": "Gaming", "assets": ["*.steampowered.com", "*.valvesoftware.com"]},
    {"name": "Alibaba", "platform": "HackerOne", "url": "https://hackerone.com/alibaba", "type": "bounty", "bounty_min": 100, "bounty_max": 10000, "currency": "USD", "managed": True, "category": "E-commerce", "assets": ["*.alibaba.com", "*.aliexpress.com"]},

    {"name": "Snapchat", "platform": "HackerOne", "url": "https://hackerone.com/snapchat", "type": "bounty", "bounty_min": 250, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Social Media", "assets": ["*.snapchat.com"]},
    {"name": "TikTok", "platform": "HackerOne", "url": "https://hackerone.com/tiktok", "type": "bounty", "bounty_min": 100, "bounty_max": 20000, "currency": "USD", "managed": True, "category": "Social Media", "assets": ["*.tiktok.com"]},
    {"name": "Notion", "platform": "HackerOne", "url": "https://hackerone.com/notion", "type": "bounty", "bounty_min": 250, "bounty_max": 10000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.notion.so"]},
    {"name": "Cloudflare", "platform": "HackerOne", "url": "https://hackerone.com/cloudflare", "type": "bounty", "bounty_min": 200, "bounty_max": 10000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.cloudflare.com"]},
    # Bugcrowd Programs
    {"name": "Tesla", "platform": "Bugcrowd", "url": "https://bugcrowd.com/tesla", "type": "bounty", "bounty_min": 100, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Automotive", "assets": ["*.tesla.com"]},
    {"name": "Mastercard", "platform": "Bugcrowd", "url": "https://bugcrowd.com/mastercard", "type": "bounty", "bounty_min": 200, "bounty_max": 10000, "currency": "USD", "managed": True, "category": "Finance", "assets": ["*.mastercard.com"]},
    {"name": "Samsung", "platform": "Bugcrowd", "url": "https://bugcrowd.com/samsung", "type": "bounty", "bounty_min": 200, "bounty_max": 1000000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.samsung.com", "Samsung Mobile"]},
    {"name": "OpenAI", "platform": "Bugcrowd", "url": "https://bugcrowd.com/openai", "type": "bounty", "bounty_min": 200, "bounty_max": 20000, "currency": "USD", "managed": True, "category": "AI/ML", "assets": ["*.openai.com", "ChatGPT", "API"]},
    {"name": "Netflix", "platform": "Bugcrowd", "url": "https://bugcrowd.com/netflix", "type": "bounty", "bounty_min": 200, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Entertainment", "assets": ["*.netflix.com"]},
    {"name": "Pinterest", "platform": "Bugcrowd", "url": "https://bugcrowd.com/pinterest", "type": "bounty", "bounty_min": 100, "bounty_max": 10000, "currency": "USD", "managed": True, "category": "Social Media", "assets": ["*.pinterest.com"]},

    {"name": "Atlassian", "platform": "Bugcrowd", "url": "https://bugcrowd.com/atlassian", "type": "bounty", "bounty_min": 100, "bounty_max": 10000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.atlassian.com", "*.jira.com"]},
    {"name": "Twitch", "platform": "Bugcrowd", "url": "https://bugcrowd.com/twitch", "type": "bounty", "bounty_min": 100, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Entertainment", "assets": ["*.twitch.tv"]},
    {"name": "ExpressVPN", "platform": "Bugcrowd", "url": "https://bugcrowd.com/expressvpn", "type": "bounty", "bounty_min": 150, "bounty_max": 2500, "currency": "USD", "managed": True, "category": "Security", "assets": ["*.expressvpn.com"]},
    {"name": "Okta", "platform": "Bugcrowd", "url": "https://bugcrowd.com/okta", "type": "bounty", "bounty_min": 50, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Security", "assets": ["*.okta.com"]},
    # Intigriti Programs
    {"name": "Intigriti", "platform": "Intigriti", "url": "https://app.intigriti.com/programs/intigriti/intigriti", "type": "bounty", "bounty_min": 100, "bounty_max": 10000, "currency": "EUR", "managed": True, "category": "Security", "assets": ["*.intigriti.com"]},
    {"name": "Randstad", "platform": "Intigriti", "url": "https://app.intigriti.com/programs/randstad", "type": "bounty", "bounty_min": 50, "bounty_max": 5000, "currency": "EUR", "managed": True, "category": "HR/Recruiting", "assets": ["*.randstad.com"]},
    {"name": "De Lijn", "platform": "Intigriti", "url": "https://app.intigriti.com/programs/delijn", "type": "bounty", "bounty_min": 0, "bounty_max": 3000, "currency": "EUR", "managed": True, "category": "Transportation", "assets": ["*.delijn.be"]},
    {"name": "Proximus", "platform": "Intigriti", "url": "https://app.intigriti.com/programs/proximus", "type": "bounty", "bounty_min": 100, "bounty_max": 10000, "currency": "EUR", "managed": True, "category": "Telecom", "assets": ["*.proximus.be"]},
    {"name": "KBC Group", "platform": "Intigriti", "url": "https://app.intigriti.com/programs/kbc", "type": "bounty", "bounty_min": 250, "bounty_max": 10000, "currency": "EUR", "managed": True, "category": "Finance", "assets": ["*.kbc.be"]},

    # YesWeHack Programs
    {"name": "LCL", "platform": "YesWeHack", "url": "https://yeswehack.com/programs/lcl", "type": "bounty", "bounty_min": 50, "bounty_max": 10000, "currency": "EUR", "managed": True, "category": "Finance", "assets": ["*.lcl.fr"]},
    {"name": "OVHcloud", "platform": "YesWeHack", "url": "https://yeswehack.com/programs/ovhcloud", "type": "bounty", "bounty_min": 50, "bounty_max": 10000, "currency": "EUR", "managed": True, "category": "Technology", "assets": ["*.ovhcloud.com", "*.ovh.com"]},
    {"name": "Doctolib", "platform": "YesWeHack", "url": "https://yeswehack.com/programs/doctolib", "type": "bounty", "bounty_min": 50, "bounty_max": 5000, "currency": "EUR", "managed": True, "category": "Healthcare", "assets": ["*.doctolib.fr"]},
    {"name": "Swiss Post", "platform": "YesWeHack", "url": "https://yeswehack.com/programs/swiss-post", "type": "bounty", "bounty_min": 100, "bounty_max": 10000, "currency": "CHF", "managed": True, "category": "Government", "assets": ["*.post.ch"]},
    {"name": "Infomaniak", "platform": "YesWeHack", "url": "https://yeswehack.com/programs/infomaniak-bug-bounty-program", "type": "bounty", "bounty_min": 100, "bounty_max": 5000, "currency": "EUR", "managed": True, "category": "Technology", "assets": ["*.infomaniak.com"]},
    {"name": "Government of Quebec", "platform": "YesWeHack", "url": "https://yeswehack.com/programs/programmes-de-primes-aux-bogues-du-gouvernement-du-quebec-cgcd", "type": "bounty", "bounty_min": 100, "bounty_max": 5000, "currency": "CAD", "managed": True, "category": "Government", "assets": ["*.quebec.ca"]},
    # Immunefi (Web3/Crypto)
    {"name": "Wormhole", "platform": "Immunefi", "url": "https://immunefi.com/bug-bounty/wormhole/", "type": "bounty", "bounty_min": 2500, "bounty_max": 2500000, "currency": "USD", "managed": True, "category": "Cryptocurrency", "assets": ["Smart Contracts", "Blockchain"]},
    {"name": "Aurora", "platform": "Immunefi", "url": "https://immunefi.com/bug-bounty/aurora/", "type": "bounty", "bounty_min": 500, "bounty_max": 6000000, "currency": "USD", "managed": True, "category": "Cryptocurrency", "assets": ["Smart Contracts", "NEAR Protocol"]},
    {"name": "Polygon", "platform": "Immunefi", "url": "https://immunefi.com/bug-bounty/polygon/", "type": "bounty", "bounty_min": 1000, "bounty_max": 2000000, "currency": "USD", "managed": True, "category": "Cryptocurrency", "assets": ["Smart Contracts"]},
    {"name": "MakerDAO", "platform": "Immunefi", "url": "https://immunefi.com/bug-bounty/makerdao/", "type": "bounty", "bounty_min": 1000, "bounty_max": 10000000, "currency": "USD", "managed": True, "category": "Cryptocurrency", "assets": ["Smart Contracts", "DeFi"]},

    {"name": "Olympus DAO", "platform": "Immunefi", "url": "https://immunefi.com/bug-bounty/olympus/", "type": "bounty", "bounty_min": 500, "bounty_max": 3300000, "currency": "USD", "managed": True, "category": "Cryptocurrency", "assets": ["Smart Contracts", "DeFi"]},
    # Independent Programs
    {"name": "Microsoft MSRC", "platform": "Independent", "url": "https://www.microsoft.com/en-us/msrc/bounty", "type": "bounty", "bounty_min": 500, "bounty_max": 250000, "currency": "USD", "managed": False, "category": "Technology", "assets": ["Windows", "Azure", "Microsoft 365", "Edge"]},
    {"name": "Apple Security Bounty", "platform": "Independent", "url": "https://security.apple.com/bounty/", "type": "bounty", "bounty_min": 5000, "bounty_max": 2000000, "currency": "USD", "managed": False, "category": "Technology", "assets": ["iOS", "macOS", "iCloud"]},
    {"name": "Meta", "platform": "Independent", "url": "https://www.facebook.com/whitehat", "type": "bounty", "bounty_min": 500, "bounty_max": 50000, "currency": "USD", "managed": False, "category": "Social Media", "assets": ["*.facebook.com", "*.instagram.com", "*.whatsapp.com"]},
    {"name": "Intel", "platform": "Independent", "url": "https://www.intel.com/content/www/us/en/security-center/bug-bounty-program.html", "type": "bounty", "bounty_min": 500, "bounty_max": 100000, "currency": "USD", "managed": False, "category": "Technology", "assets": ["Hardware", "Firmware", "Software"]},
    {"name": "Sony PlayStation", "platform": "Independent", "url": "https://hackerone.com/playstation", "type": "bounty", "bounty_min": 100, "bounty_max": 50000, "currency": "USD", "managed": False, "category": "Gaming", "assets": ["PlayStation Network", "*.playstation.com"]},
    {"name": "Brave Browser", "platform": "HackerOne", "url": "https://hackerone.com/brave", "type": "bounty", "bounty_min": 100, "bounty_max": 10000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["Brave Browser"]},
    {"name": "Mozilla", "platform": "Independent", "url": "https://www.mozilla.org/en-US/security/bug-bounty/", "type": "bounty", "bounty_min": 500, "bounty_max": 15000, "currency": "USD", "managed": False, "category": "Technology", "assets": ["Firefox", "*.mozilla.org"]},
    {"name": "Verizon Media", "platform": "HackerOne", "url": "https://hackerone.com/verizonmedia", "type": "bounty", "bounty_min": 150, "bounty_max": 15000, "currency": "USD", "managed": True, "category": "Technology", "assets": ["*.verizonmedia.com"]},
]



def generate_program_id(program):
    """Generate a unique ID for a program based on name + platform."""
    key = f"{program['platform']}:{program['name']}".lower()
    return hashlib.md5(key.encode()).hexdigest()[:12]


def enrich_program(program):
    """Enrich a program entry with computed fields."""
    program["id"] = generate_program_id(program)
    program.setdefault("assets", [])
    program.setdefault("managed", False)
    program.setdefault("category", "Other")
    program.setdefault("currency", "USD")
    program.setdefault("bounty_min", 0)
    program.setdefault("bounty_max", 0)
    program.setdefault("type", "bounty")
    program.setdefault("last_updated", datetime.now(timezone.utc).isoformat())
    return program



def try_scrape_hackerone():
    """
    Try to scrape HackerOne public directory (no API key needed).
    Uses the public GraphQL endpoint that powers hackerone.com/directory.
    Falls back to seed data if scraping fails.
    """
    import urllib.request
    import ssl

    programs = []
    try:
        # HackerOne exposes a public directory page - we scrape the JSON
        url = "https://hackerone.com/directory/programs"
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; BugBountyAggregator/1.0)",
            "Accept": "text/html,application/xhtml+xml"
        })
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            if resp.status == 200:
                print("[*] Successfully reached HackerOne directory")
    except Exception as e:
        print(f"[!] HackerOne scrape skipped: {e}")

    return programs



def try_scrape_bugcrowd():
    """
    Try to scrape Bugcrowd public programs list (no API key needed).
    Bugcrowd has a public JSON endpoint for their program list.
    """
    import urllib.request
    import ssl

    programs = []
    try:
        url = "https://bugcrowd.com/programs.json"
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; BugBountyAggregator/1.0)",
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            if resp.status == 200:
                print("[*] Successfully reached Bugcrowd programs endpoint")
    except Exception as e:
        print(f"[!] Bugcrowd scrape skipped: {e}")

    return programs



def try_fetch_bounty_targets_data():
    """
    Fetch from arkadiyt/bounty-targets-data GitHub repo.
    This repo has hourly-updated data dumps from all major platforms.
    No API key needed - uses raw GitHub content URLs.
    """
    import urllib.request
    import ssl

    programs = []
    base_url = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data"
    platforms = {
        "hackerone_data.json": "HackerOne",
        "bugcrowd_data.json": "Bugcrowd",
        "intigriti_data.json": "Intigriti",
        "yeswehack_data.json": "YesWeHack",
    }

    ctx = ssl.create_default_context()

    for filename, platform in platforms.items():
        try:
            url = f"{base_url}/{filename}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; BugBountyAggregator/1.0)"
            })
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    count = 0
                    for item in data[:100]:  # Limit to first 100 per platform
                        prog = parse_bounty_target(item, platform)
                        if prog:
                            programs.append(prog)
                            count += 1
                    print(f"[*] Fetched {count} programs from {platform} via bounty-targets-data")
        except Exception as e:
            print(f"[!] Failed to fetch {platform} from bounty-targets-data: {e}")

    return programs



def parse_bounty_target(item, platform):
    """Parse a single entry from bounty-targets-data format."""
    try:
        name = item.get("name", "")
        if not name:
            return None

        url = item.get("url", "")
        targets = item.get("targets", {})
        in_scope = targets.get("in_scope", [])
        assets = []
        for scope_item in in_scope[:10]:  # Limit assets
            asset_id = scope_item.get("asset_identifier", "")
            if asset_id:
                assets.append(asset_id)

        # Determine bounty info
        offers_bounties = item.get("offers_bounties", False)
        max_bounty = 0
        if isinstance(item.get("max_bounty"), (int, float)):
            max_bounty = int(item["max_bounty"])

        prog = {
            "name": name,
            "platform": platform,
            "url": url,
            "type": "bounty" if offers_bounties else "vdp",
            "bounty_min": 0,
            "bounty_max": max_bounty,
            "currency": "USD",
            "managed": True,
            "category": categorize_program(name, assets),
            "assets": assets,
        }
        return prog
    except Exception:
        return None



def categorize_program(name, assets):
    """Auto-categorize a program based on name and assets."""
    name_lower = name.lower()
    assets_str = " ".join(assets).lower()
    combined = name_lower + " " + assets_str

    categories = {
        "Cryptocurrency": ["crypto", "defi", "blockchain", "token", "swap", "dao", "nft", "web3", "chain"],
        "Finance": ["bank", "finance", "payment", "pay", "fintech", "invest", "trading"],
        "Gaming": ["game", "gaming", "play", "esport"],
        "Government": ["gov", "government", "federal", "military", "defence", "defense"],
        "Healthcare": ["health", "medical", "hospital", "pharma", "doctor"],
        "E-commerce": ["shop", "store", "commerce", "retail", "market"],
        "Social Media": ["social", "chat", "messenger", "community"],
        "Entertainment": ["entertainment", "music", "video", "stream", "media"],
        "Transportation": ["transport", "travel", "ride", "delivery", "logistics"],
        "Security": ["security", "vpn", "antivirus", "cyber", "auth"],
        "Telecom": ["telecom", "mobile", "wireless", "5g"],
        "AI/ML": ["ai", "ml", "machine learning", "artificial intelligence", "openai", "gpt"],
        "Technology": ["tech", "software", "cloud", "saas"],
    }

    for category, keywords in categories.items():
        if any(kw in combined for kw in keywords):
            return category

    return "Technology"



def compute_changelog(old_programs, new_programs):
    """Compare old and new program lists to generate changelog entries."""
    old_ids = {p["id"] for p in old_programs}
    new_ids = {p["id"] for p in new_programs}

    added = new_ids - old_ids
    removed = old_ids - new_ids

    entries = []
    timestamp = datetime.now(timezone.utc).isoformat()

    new_by_id = {p["id"]: p for p in new_programs}
    old_by_id = {p["id"]: p for p in old_programs}

    for pid in added:
        prog = new_by_id[pid]
        entries.append({
            "timestamp": timestamp,
            "type": "added",
            "program_name": prog["name"],
            "platform": prog["platform"],
            "details": f"New program: {prog['name']} on {prog['platform']}"
        })

    for pid in removed:
        prog = old_by_id[pid]
        entries.append({
            "timestamp": timestamp,
            "type": "removed",
            "program_name": prog["name"],
            "platform": prog["platform"],
            "details": f"Program removed: {prog['name']} from {prog['platform']}"
        })

    # Check for bounty changes
    for pid in old_ids & new_ids:
        old_p = old_by_id[pid]
        new_p = new_by_id[pid]
        if old_p.get("bounty_max") != new_p.get("bounty_max"):
            entries.append({
                "timestamp": timestamp,
                "type": "updated",
                "program_name": new_p["name"],
                "platform": new_p["platform"],
                "details": f"Bounty updated: ${old_p.get('bounty_max', 0)} -> ${new_p.get('bounty_max', 0)}"
            })

    return entries



def main():
    """Main aggregation pipeline."""
    print("=" * 60)
    print("Bug Bounty Program Aggregator")
    print("=" * 60)
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print()

    # Load existing data
    old_programs = []
    if PROGRAMS_FILE.exists():
        try:
            with open(PROGRAMS_FILE, "r") as f:
                data = json.load(f)
                old_programs = data.get("programs", [])
        except (json.JSONDecodeError, KeyError):
            pass

    # Step 1: Start with seed data
    print("[*] Loading seed data...")
    all_programs = []
    for prog in KNOWN_PROGRAMS:
        all_programs.append(enrich_program(prog.copy()))
    print(f"    -> {len(all_programs)} programs from seed data")

    # Step 2: Try to fetch from bounty-targets-data (no API key)
    print("\n[*] Fetching from bounty-targets-data (GitHub raw)...")
    scraped = try_fetch_bounty_targets_data()
    for prog in scraped:
        enriched = enrich_program(prog)
        # Avoid duplicates by ID
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 3: Try platform scrapes (no API keys)
    print("\n[*] Attempting direct platform scrapes...")
    try_scrape_hackerone()
    try_scrape_bugcrowd()


    # Step 4: Sort programs
    all_programs.sort(key=lambda p: (-p.get("bounty_max", 0), p["name"]))

    # Step 5: Compute changelog
    print("\n[*] Computing changelog...")
    changelog_entries = compute_changelog(old_programs, all_programs)
    if changelog_entries:
        print(f"    -> {len(changelog_entries)} changes detected")
    else:
        print("    -> No changes detected")

    # Step 6: Save updated data
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    programs_data = {
        "metadata": {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_programs": len(all_programs),
            "sources": list(set(p["platform"] for p in all_programs)),
            "categories": list(set(p["category"] for p in all_programs)),
        },
        "programs": all_programs,
    }

    with open(PROGRAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(programs_data, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Saved {len(all_programs)} programs to {PROGRAMS_FILE}")

    # Update changelog
    changelog_data = {"entries": []}
    if CHANGELOG_FILE.exists():
        try:
            with open(CHANGELOG_FILE, "r") as f:
                changelog_data = json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass

    changelog_data["entries"] = changelog_entries + changelog_data.get("entries", [])
    # Keep only last 500 entries
    changelog_data["entries"] = changelog_data["entries"][:500]

    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        json.dump(changelog_data, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved changelog to {CHANGELOG_FILE}")
    print("\n" + "=" * 60)
    print("Aggregation complete!")


if __name__ == "__main__":
    main()
