"""Tests for scripts/aggregate.py core functions."""

from aggregate import (
    categorize_program,
    compute_changelog,
    enrich_program,
    fetch_url,
    generate_program_id,
    parse_bounty_target,
    validate_program,
)


class TestGenerateProgramId:
    def test_generate_program_id_consistent(self, sample_program):
        """Same input always produces same 12-char hex ID."""
        id1 = generate_program_id(sample_program)
        id2 = generate_program_id(sample_program)
        assert id1 == id2
        assert len(id1) == 12
        # Verify it is valid hex
        int(id1, 16)

    def test_generate_program_id_different_programs(self, sample_program):
        """Different programs get different IDs."""
        other_program = sample_program.copy()
        other_program["name"] = "DifferentProgram"
        id1 = generate_program_id(sample_program)
        id2 = generate_program_id(other_program)
        assert id1 != id2


class TestEnrichProgram:
    def test_enrich_program_fills_defaults(self):
        """Missing fields get filled with defaults."""
        minimal = {"name": "Minimal", "platform": "HackerOne", "url": "https://example.com"}
        enriched = enrich_program(minimal)
        assert enriched["assets"] == []
        assert enriched["managed"] is False
        assert enriched["category"] == "Other"
        assert enriched["currency"] == "USD"
        assert enriched["bounty_min"] == 0
        assert enriched["bounty_max"] == 0
        assert enriched["type"] == "bounty"
        assert "last_updated" in enriched
        assert "id" in enriched

    def test_enrich_program_preserves_values(self, sample_program):
        """Existing values are not overwritten by defaults."""
        original = sample_program.copy()
        enriched = enrich_program(sample_program)
        assert enriched["assets"] == original["assets"]
        assert enriched["managed"] == original["managed"]
        assert enriched["category"] == original["category"]
        assert enriched["currency"] == original["currency"]
        assert enriched["bounty_min"] == original["bounty_min"]
        assert enriched["bounty_max"] == original["bounty_max"]
        assert enriched["type"] == original["type"]


class TestValidateProgram:
    def test_validate_program_accepts_valid(self, sample_program):
        """Valid program returns True."""
        assert validate_program(sample_program) is True

    def test_validate_program_rejects_empty_name(self):
        """Empty or missing name returns False."""
        prog = {
            "name": "",
            "platform": "HackerOne",
            "url": "https://example.com",
            "type": "bounty",
            "bounty_min": 0,
            "bounty_max": 1000,
        }
        assert validate_program(prog) is False

        prog_missing = {
            "platform": "HackerOne",
            "url": "https://example.com",
            "type": "bounty",
            "bounty_min": 0,
            "bounty_max": 1000,
        }
        assert validate_program(prog_missing) is False

    def test_validate_program_rejects_negative_bounty(self):
        """Negative bounty_min returns False."""
        prog = {
            "name": "Test",
            "platform": "HackerOne",
            "url": "https://example.com",
            "type": "bounty",
            "bounty_min": -100,
            "bounty_max": 1000,
        }
        assert validate_program(prog) is False

    def test_validate_program_rejects_min_greater_than_max(self):
        """bounty_min > bounty_max returns False."""
        prog = {
            "name": "Test",
            "platform": "HackerOne",
            "url": "https://example.com",
            "type": "bounty",
            "bounty_min": 5000,
            "bounty_max": 1000,
        }
        assert validate_program(prog) is False

    def test_validate_program_rejects_invalid_type(self):
        """type not in ['bounty','vdp'] returns False."""
        prog = {
            "name": "Test",
            "platform": "HackerOne",
            "url": "https://example.com",
            "type": "invalid",
            "bounty_min": 0,
            "bounty_max": 1000,
        }
        assert validate_program(prog) is False


class TestCategorizeProgram:
    def test_categorize_program_crypto(self):
        """Name containing 'blockchain' categorized as Cryptocurrency."""
        result = categorize_program("MyBlockchain Project", [])
        assert result == "Cryptocurrency"

    def test_categorize_program_finance(self):
        """Name containing 'bank' categorized as Finance."""
        result = categorize_program("SuperBank", [])
        assert result == "Finance"

    def test_categorize_program_default(self):
        """Unknown name categorized as Technology."""
        result = categorize_program("Zxywq Corp", [])
        assert result == "Technology"


class TestComputeChangelog:
    def test_compute_changelog_detects_additions(self):
        """New program in new list creates 'added' entry."""
        old = []
        new = [{"id": "new123", "name": "NewProg", "platform": "HackerOne", "bounty_max": 5000}]
        entries = compute_changelog(old, new)
        assert len(entries) == 1
        assert entries[0]["type"] == "added"
        assert entries[0]["program_name"] == "NewProg"

    def test_compute_changelog_detects_removals(self):
        """Program missing from new list creates 'removed' entry."""
        old = [{"id": "old123", "name": "OldProg", "platform": "HackerOne", "bounty_max": 5000}]
        new = []
        entries = compute_changelog(old, new)
        assert len(entries) == 1
        assert entries[0]["type"] == "removed"
        assert entries[0]["program_name"] == "OldProg"

    def test_compute_changelog_detects_updates(self):
        """Changed bounty_max creates 'updated' entry."""
        old = [{"id": "prog1", "name": "TestProg", "platform": "HackerOne", "bounty_max": 5000}]
        new = [{"id": "prog1", "name": "TestProg", "platform": "HackerOne", "bounty_max": 10000}]
        entries = compute_changelog(old, new)
        assert len(entries) == 1
        assert entries[0]["type"] == "updated"
        assert entries[0]["program_name"] == "TestProg"


class TestParseBountyTarget:
    def test_parse_bounty_target_valid(self):
        """Parses a valid bounty-targets-data format item correctly."""
        item = {
            "name": "ExampleCorp",
            "url": "https://hackerone.com/examplecorp",
            "offers_bounties": True,
            "max_bounty": 15000,
            "targets": {
                "in_scope": [
                    {"asset_identifier": "*.example.com"},
                    {"asset_identifier": "api.example.com"},
                ]
            },
        }
        result = parse_bounty_target(item, "HackerOne")
        assert result is not None
        assert result["name"] == "ExampleCorp"
        assert result["platform"] == "HackerOne"
        assert result["url"] == "https://hackerone.com/examplecorp"
        assert result["type"] == "bounty"
        assert result["bounty_max"] == 15000
        assert "*.example.com" in result["assets"]
        assert "api.example.com" in result["assets"]

    def test_parse_bounty_target_missing_name(self):
        """Returns None for item without name."""
        item = {
            "url": "https://hackerone.com/noname",
            "offers_bounties": True,
            "max_bounty": 5000,
        }
        result = parse_bounty_target(item, "HackerOne")
        assert result is None


class TestFetchUrl:
    def test_fetch_url_returns_none_on_failure(self, monkeypatch):
        """fetch_url returns None when urlopen raises an exception."""
        import urllib.request

        def mock_urlopen(*args, **kwargs):
            raise ConnectionError("simulated network failure")

        monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
        result = fetch_url("https://example.com/test", retries=1, timeout=5)
        assert result is None

    def test_fetch_url_retries_on_error(self, monkeypatch):
        """fetch_url retries the configured number of times before giving up."""
        import urllib.request
        import aggregate

        call_count = {"value": 0}

        def mock_urlopen(*args, **kwargs):
            call_count["value"] += 1
            raise ConnectionError("simulated network failure")

        monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
        # Disable sleep to speed up test
        monkeypatch.setattr(aggregate.time, "sleep", lambda x: None)

        result = fetch_url("https://example.com/test", retries=3, timeout=5)
        assert result is None
        assert call_count["value"] == 3


class TestValidateProgramUrl:
    def test_validate_program_rejects_javascript_url(self):
        """URL with javascript: protocol returns False (XSS prevention)."""
        prog = {
            "name": "Test",
            "platform": "HackerOne",
            "url": "javascript:alert(1)",
            "type": "bounty",
            "bounty_min": 0,
            "bounty_max": 1000,
        }
        assert validate_program(prog) is False

    def test_validate_program_accepts_empty_url(self):
        """Empty URL is acceptable (some programs have no URL)."""
        prog = {
            "name": "Test",
            "platform": "HackerOne",
            "url": "",
            "type": "bounty",
            "bounty_min": 0,
            "bounty_max": 1000,
        }
        assert validate_program(prog) is True

    def test_validate_program_accepts_https_url(self):
        """HTTPS URL is valid."""
        prog = {
            "name": "Test",
            "platform": "HackerOne",
            "url": "https://example.com",
            "type": "bounty",
            "bounty_min": 0,
            "bounty_max": 1000,
        }
        assert validate_program(prog) is True

    def test_validate_program_accepts_http_url(self):
        """HTTP URL is valid."""
        prog = {
            "name": "Test",
            "platform": "HackerOne",
            "url": "http://example.com",
            "type": "bounty",
            "bounty_min": 0,
            "bounty_max": 1000,
        }
        assert validate_program(prog) is True
