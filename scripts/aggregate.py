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
                    for item in data:  # Fetch ALL programs, no limit
                        prog = parse_bounty_target(item, platform)
                        if prog:
                            programs.append(prog)
                            count += 1
                    print(f"[*] Fetched {count} programs from {platform} via bounty-targets-data")
        except Exception as e:
            print(f"[!] Failed to fetch {platform} from bounty-targets-data: {e}")

    return programs


def try_fetch_projectdiscovery_chaos():
    """
    Fetch from projectdiscovery/public-bugbounty-programs GitHub repo.
    Contains a curated JSON of public BBP programs with domains.
    No API key needed.
    """
    import urllib.request
    import ssl

    programs = []
    urls_to_try = [
        "https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/main/chaos-bugbounty-list.json",
        "https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/master/chaos-bugbounty-list.json",
    ]

    ctx = ssl.create_default_context()

    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; BugBountyAggregator/1.0)"
            })
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data.get("programs", data) if isinstance(data, dict) else data
                    for item in items:
                        prog = parse_chaos_program(item)
                        if prog:
                            programs.append(prog)
                    print(f"[*] Fetched {len(programs)} programs from ProjectDiscovery/chaos")
                    break
        except Exception as e:
            print(f"[!] ProjectDiscovery chaos fetch failed ({url}): {e}")

    return programs


def parse_chaos_program(item):
    """Parse a program from chaos-bugbounty-list.json format."""
    try:
        name = item.get("name", "")
        if not name:
            return None

        url = item.get("url", "")
        domains = item.get("domains", [])
        bounty = item.get("bounty", False)

        # Determine platform from URL
        platform = "Independent"
        if "hackerone.com" in url:
            platform = "HackerOne"
        elif "bugcrowd.com" in url:
            platform = "Bugcrowd"
        elif "intigriti.com" in url:
            platform = "Intigriti"
        elif "yeswehack.com" in url:
            platform = "YesWeHack"

        return {
            "name": name,
            "platform": platform,
            "url": url,
            "type": "bounty" if bounty else "vdp",
            "bounty_min": 0,
            "bounty_max": 0,
            "currency": "USD",
            "managed": True,
            "category": categorize_program(name, domains),
            "assets": domains[:10],
        }
    except Exception:
        return None


def try_fetch_disclose_db():
    """
    Fetch from disclose/diodb - Open-source vulnerability disclosure
    and bug bounty program database. No API key needed.
    """
    import urllib.request
    import ssl

    programs = []
    urls_to_try = [
        "https://raw.githubusercontent.com/disclose/diodb/master/program-list.json",
        "https://raw.githubusercontent.com/disclose/diodata/master/program-list.json",
    ]

    ctx = ssl.create_default_context()

    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; BugBountyAggregator/1.0)"
            })
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data if isinstance(data, list) else data.get("programs", [])
                    for item in items:
                        prog = parse_disclose_program(item)
                        if prog:
                            programs.append(prog)
                    print(f"[*] Fetched {len(programs)} programs from disclose.io database")
                    break
        except Exception as e:
            print(f"[!] Disclose.io fetch failed ({url}): {e}")

    return programs


def parse_disclose_program(item):
    """Parse a program from disclose.io format."""
    try:
        name = item.get("program_name", item.get("name", ""))
        if not name:
            return None

        url = item.get("policy_url", item.get("url", ""))
        bounty = item.get("bounty", "").lower() == "yes" or item.get("offers_bounty", False)

        # Determine platform
        platform = "Independent"
        pgm_platform = item.get("platform", "").lower()
        if "hackerone" in pgm_platform:
            platform = "HackerOne"
        elif "bugcrowd" in pgm_platform:
            platform = "Bugcrowd"
        elif "intigriti" in pgm_platform:
            platform = "Intigriti"
        elif "yeswehack" in pgm_platform:
            platform = "YesWeHack"

        assets = []
        if item.get("targets"):
            assets = item["targets"][:10] if isinstance(item["targets"], list) else []

        return {
            "name": name,
            "platform": platform,
            "url": url,
            "type": "bounty" if bounty else "vdp",
            "bounty_min": 0,
            "bounty_max": 0,
            "currency": "USD",
            "managed": platform != "Independent",
            "category": categorize_program(name, assets),
            "assets": assets,
        }
    except Exception:
        return None


def try_fetch_firebounty_rss():
    """
    Fetch from FireBounty RSS feed to discover NEW programs.
    FireBounty crawls many platforms and aggregates them.
    No API key needed - public RSS feed.
    """
    import urllib.request
    import ssl
    import xml.etree.ElementTree as ET

    programs = []
    url = "https://firebounty.com/rss.xml"

    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; BugBountyAggregator/1.0)"
        })
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            if resp.status == 200:
                content = resp.read().decode("utf-8")
                root = ET.fromstring(content)
                # RSS format: <channel><item><title>...</title><link>...</link></item>
                for item in root.findall(".//item"):
                    title_el = item.find("title")
                    link_el = item.find("link")
                    desc_el = item.find("description")

                    if title_el is not None and title_el.text:
                        name = title_el.text.strip()
                        link = link_el.text.strip() if link_el is not None and link_el.text else ""
                        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""

                        # Determine if it's a bounty or VDP from description
                        is_bounty = "bounty" in desc.lower() or "reward" in desc.lower()

                        programs.append({
                            "name": name,
                            "platform": "FireBounty",
                            "url": link,
                            "type": "bounty" if is_bounty else "vdp",
                            "bounty_min": 0,
                            "bounty_max": 0,
                            "currency": "USD",
                            "managed": False,
                            "category": categorize_program(name, []),
                            "assets": [],
                        })

                print(f"[*] Fetched {len(programs)} programs from FireBounty RSS")
    except Exception as e:
        print(f"[!] FireBounty RSS fetch failed: {e}")

    return programs


def try_fetch_hackerone_graphql():
    """
    Scrape HackerOne's public directory using their GraphQL endpoint.
    This endpoint is publicly accessible without authentication -
    it's the same one that powers hackerone.com/directory/programs.
    No API key needed.
    """
    import urllib.request
    import ssl

    programs = []
    url = "https://hackerone.com/graphql"
    ctx = ssl.create_default_context()

    # The public GraphQL query for the directory
    query = {
        "operationName": "DirectoryQuery",
        "variables": {
            "where": {
                "submission_state": {"_eq": "open"},
                "_and": [{"offers_bounties": {"_eq": True}}]
            },
            "first": 100,
            "secureOrderBy": {"started_accepting_at": {"_direction": "DESC"}}
        },
        "query": """query DirectoryQuery($first: Int, $where: FiltersTeamFilterInput, $secureOrderBy: FiltersTeamFilterOrder) {
            teams(first: $first, where: $where, secure_order_by: $secureOrderBy) {
                edges {
                    node {
                        handle
                        name
                        currency
                        offers_bounties
                        base_bounty
                        state
                        started_accepting_at
                        url
                    }
                }
            }
        }"""
    }

    try:
        data = json.dumps(query).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            if resp.status == 200:
                result = json.loads(resp.read().decode("utf-8"))
                edges = result.get("data", {}).get("teams", {}).get("edges", [])
                for edge in edges:
                    node = edge.get("node", {})
                    if node.get("name"):
                        programs.append({
                            "name": node["name"],
                            "platform": "HackerOne",
                            "url": f"https://hackerone.com/{node.get('handle', '')}",
                            "type": "bounty" if node.get("offers_bounties") else "vdp",
                            "bounty_min": 0,
                            "bounty_max": int(node.get("base_bounty", 0) or 0),
                            "currency": node.get("currency", "USD"),
                            "managed": True,
                            "category": categorize_program(node["name"], []),
                            "assets": [],
                        })
                print(f"[*] Fetched {len(programs)} NEW programs from HackerOne GraphQL (no API key)")
    except Exception as e:
        print(f"[!] HackerOne GraphQL scrape failed: {e}")

    return programs


def try_fetch_bugcrowd_engagements():
    """
    Scrape Bugcrowd's public engagements endpoint.
    Bugcrowd exposes /engagements.json for their public programs listing.
    No API key needed.
    """
    import urllib.request
    import ssl

    programs = []
    ctx = ssl.create_default_context()

    # Bugcrowd public endpoints to try
    urls = [
        "https://bugcrowd.com/engagements.json?category=bug_bounty&sort_by=promoted&sort_direction=desc&page=1",
        "https://bugcrowd.com/programs.json?sort[]=promoted-desc&hidden[]=false&page[]=1",
    ]

    for url in urls:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    items = data if isinstance(data, list) else data.get("engagements", data.get("programs", []))
                    for item in items:
                        name = item.get("name", item.get("program", {}).get("name", ""))
                        code = item.get("code", item.get("program", {}).get("code", ""))
                        if name:
                            programs.append({
                                "name": name,
                                "platform": "Bugcrowd",
                                "url": f"https://bugcrowd.com/{code}" if code else "",
                                "type": "bounty",
                                "bounty_min": 0,
                                "bounty_max": int(item.get("max_payout", 0) or 0),
                                "currency": "USD",
                                "managed": True,
                                "category": categorize_program(name, []),
                                "assets": [],
                            })
                    if programs:
                        print(f"[*] Fetched {len(programs)} programs from Bugcrowd engagements")
                        break
        except Exception as e:
            print(f"[!] Bugcrowd engagements fetch failed ({url}): {e}")

    return programs


def try_fetch_immunefi_programs():
    """
    Scrape Immunefi's public bounties list.
    Immunefi exposes their programs list via their web app's data.
    No API key needed.
    """
    import urllib.request
    import ssl

    programs = []
    ctx = ssl.create_default_context()

    # Immunefi serves their data via a public JSON endpoint
    urls = [
        "https://immunefi.com/explore/",
        "https://immunefi.com/bounty/",
    ]

    try:
        # Try to fetch the bug bounty listing page and extract JSON data
        url = "https://immunefi.com/_next/data/bounties.json"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                bounties = data.get("pageProps", {}).get("bounties", [])
                for item in bounties:
                    name = item.get("project", "")
                    if name:
                        max_reward = 0
                        try:
                            max_reward = int(item.get("maxBounty", 0) or 0)
                        except (ValueError, TypeError):
                            pass
                        programs.append({
                            "name": name,
                            "platform": "Immunefi",
                            "url": f"https://immunefi.com/bug-bounty/{item.get('id', name.lower().replace(' ', '-'))}/",
                            "type": "bounty",
                            "bounty_min": 0,
                            "bounty_max": max_reward,
                            "currency": "USD",
                            "managed": True,
                            "category": "Cryptocurrency",
                            "assets": item.get("assets", [])[:5],
                        })
                print(f"[*] Fetched {len(programs)} programs from Immunefi")
    except Exception as e:
        print(f"[!] Immunefi fetch failed: {e}")

    return programs


def try_fetch_openbugbounty():
    """
    Fetch programs from Open Bug Bounty.
    They have a public listing that can be scraped.
    No API key needed.
    """
    import urllib.request
    import ssl
    import re

    programs = []
    ctx = ssl.create_default_context()

    try:
        url = "https://www.openbugbounty.org/bugbounty-list/"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html",
        })
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            if resp.status == 200:
                html = resp.read().decode("utf-8", errors="ignore")
                # Extract program entries from the HTML table
                # Pattern: look for domain names in the bounty list
                pattern = r'<a[^>]*href="(/bugbounty/[^"]+)"[^>]*>([^<]+)</a>'
                matches = re.findall(pattern, html)
                for path, name in matches[:200]:  # Limit
                    name = name.strip()
                    if name and "." in name:  # Likely a domain
                        programs.append({
                            "name": name,
                            "platform": "Open Bug Bounty",
                            "url": f"https://www.openbugbounty.org{path}",
                            "type": "bounty",
                            "bounty_min": 0,
                            "bounty_max": 0,
                            "currency": "USD",
                            "managed": False,
                            "category": categorize_program(name, [name]),
                            "assets": [name],
                        })
                if programs:
                    print(f"[*] Fetched {len(programs)} programs from Open Bug Bounty")
    except Exception as e:
        print(f"[!] Open Bug Bounty fetch failed: {e}")

    return programs


def try_fetch_hackenproof():
    """
    Fetch from HackenProof's public programs listing.
    No API key needed.
    """
    import urllib.request
    import ssl

    programs = []
    ctx = ssl.create_default_context()

    try:
        url = "https://hackenproof.com/programs"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/html",
        })
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            if resp.status == 200:
                content = resp.read().decode("utf-8", errors="ignore")
                # Try JSON parse first
                try:
                    data = json.loads(content)
                    items = data if isinstance(data, list) else data.get("programs", [])
                    for item in items:
                        name = item.get("name", item.get("title", ""))
                        if name:
                            programs.append({
                                "name": name,
                                "platform": "HackenProof",
                                "url": item.get("url", f"https://hackenproof.com/programs"),
                                "type": "bounty",
                                "bounty_min": 0,
                                "bounty_max": int(item.get("max_bounty", 0) or 0),
                                "currency": "USD",
                                "managed": True,
                                "category": categorize_program(name, []),
                                "assets": [],
                            })
                except (json.JSONDecodeError, ValueError):
                    pass
                if programs:
                    print(f"[*] Fetched {len(programs)} programs from HackenProof")
    except Exception as e:
        print(f"[!] HackenProof fetch failed: {e}")

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

    # Step 3: Fetch from ProjectDiscovery chaos list (no API key)
    print("\n[*] Fetching from ProjectDiscovery/chaos...")
    chaos_programs = try_fetch_projectdiscovery_chaos()
    for prog in chaos_programs:
        enriched = enrich_program(prog)
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 4: Fetch from disclose.io database (no API key)
    print("\n[*] Fetching from disclose.io database...")
    disclose_programs = try_fetch_disclose_db()
    for prog in disclose_programs:
        enriched = enrich_program(prog)
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 5: Fetch from FireBounty RSS (no API key)
    print("\n[*] Fetching from FireBounty RSS feed...")
    firebounty_programs = try_fetch_firebounty_rss()
    for prog in firebounty_programs:
        enriched = enrich_program(prog)
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 6: HackerOne GraphQL public scrape (no API key)
    print("\n[*] Scraping HackerOne public GraphQL directory...")
    h1_programs = try_fetch_hackerone_graphql()
    for prog in h1_programs:
        enriched = enrich_program(prog)
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 7: Bugcrowd public engagements (no API key)
    print("\n[*] Scraping Bugcrowd public engagements...")
    bc_programs = try_fetch_bugcrowd_engagements()
    for prog in bc_programs:
        enriched = enrich_program(prog)
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 8: Immunefi programs (no API key)
    print("\n[*] Fetching Immunefi programs...")
    immunefi_programs = try_fetch_immunefi_programs()
    for prog in immunefi_programs:
        enriched = enrich_program(prog)
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 9: Open Bug Bounty scrape (no API key)
    print("\n[*] Scraping Open Bug Bounty...")
    obb_programs = try_fetch_openbugbounty()
    for prog in obb_programs:
        enriched = enrich_program(prog)
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 10: HackenProof (no API key)
    print("\n[*] Fetching HackenProof programs...")
    hp_programs = try_fetch_hackenproof()
    for prog in hp_programs:
        enriched = enrich_program(prog)
        existing_ids = {p["id"] for p in all_programs}
        if enriched["id"] not in existing_ids:
            all_programs.append(enriched)
    print(f"    -> Total after merge: {len(all_programs)} programs")

    # Step 11: Try legacy platform scrapes (no API keys)
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
