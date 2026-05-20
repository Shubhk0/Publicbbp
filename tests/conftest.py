"""Shared test fixtures for bug bounty aggregator tests."""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to sys.path so we can import from it
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


@pytest.fixture
def sample_program():
    """Return a valid program dict with all expected fields."""
    return {
        "name": "TestProgram",
        "platform": "HackerOne",
        "url": "https://hackerone.com/testprogram",
        "type": "bounty",
        "bounty_min": 100,
        "bounty_max": 10000,
        "currency": "USD",
        "managed": True,
        "category": "Technology",
        "assets": ["*.testprogram.com", "api.testprogram.com"],
    }


@pytest.fixture
def sample_programs_list():
    """Return a list of programs for testing changelog/filtering."""
    return [
        {
            "id": "abc123def456",
            "name": "AlphaBank",
            "platform": "HackerOne",
            "url": "https://hackerone.com/alphabank",
            "type": "bounty",
            "bounty_min": 500,
            "bounty_max": 20000,
            "currency": "USD",
            "managed": True,
            "category": "Finance",
            "assets": ["*.alphabank.com"],
        },
        {
            "id": "111222333444",
            "name": "CryptoChain",
            "platform": "Immunefi",
            "url": "https://immunefi.com/cryptochain",
            "type": "bounty",
            "bounty_min": 1000,
            "bounty_max": 50000,
            "currency": "USD",
            "managed": True,
            "category": "Cryptocurrency",
            "assets": ["Smart Contracts"],
        },
        {
            "id": "aaa111bbb222",
            "name": "GameZone",
            "platform": "Bugcrowd",
            "url": "https://bugcrowd.com/gamezone",
            "type": "bounty",
            "bounty_min": 200,
            "bounty_max": 15000,
            "currency": "USD",
            "managed": True,
            "category": "Gaming",
            "assets": ["*.gamezone.com"],
        },
        {
            "id": "fff000eee999",
            "name": "OpenSource VDP",
            "platform": "HackerOne",
            "url": "https://hackerone.com/opensource",
            "type": "vdp",
            "bounty_min": 0,
            "bounty_max": 0,
            "currency": "USD",
            "managed": False,
            "category": "Technology",
            "assets": ["*.opensource.org"],
        },
    ]


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Create a temporary directory with programs.json and changelog.json for testing load_data."""
    programs_data = {
        "metadata": {
            "last_updated": "2024-01-01T00:00:00Z",
            "total_programs": 1,
            "sources": ["HackerOne"],
            "categories": ["Technology"],
        },
        "programs": [
            {
                "id": "test123",
                "name": "TestProg",
                "platform": "HackerOne",
                "url": "https://hackerone.com/test",
                "type": "bounty",
                "bounty_min": 100,
                "bounty_max": 5000,
                "currency": "USD",
                "managed": True,
                "category": "Technology",
                "assets": ["*.test.com"],
            }
        ],
    }
    changelog_data = {
        "entries": [
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "type": "added",
                "program_name": "TestProg",
                "platform": "HackerOne",
                "details": "New program: TestProg on HackerOne",
            }
        ]
    }

    programs_file = tmp_path / "programs.json"
    changelog_file = tmp_path / "changelog.json"
    programs_file.write_text(json.dumps(programs_data))
    changelog_file.write_text(json.dumps(changelog_data))

    return tmp_path
