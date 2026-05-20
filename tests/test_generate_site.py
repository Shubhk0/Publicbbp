"""Tests for scripts/generate_site.py functions."""

import json
from pathlib import Path

import generate_site


class TestLoadData:
    def test_load_data_missing_files(self, monkeypatch, tmp_path):
        """Returns default empty structure when files don't exist."""
        monkeypatch.setattr(generate_site, "PROGRAMS_FILE", tmp_path / "nonexistent.json")
        monkeypatch.setattr(generate_site, "CHANGELOG_FILE", tmp_path / "nonexistent2.json")
        programs, changelog = generate_site.load_data()
        assert programs == {"metadata": {}, "programs": []}
        assert changelog == {"entries": []}

    def test_load_data_invalid_json(self, monkeypatch, tmp_path):
        """Handles malformed JSON gracefully."""
        bad_programs = tmp_path / "programs.json"
        bad_changelog = tmp_path / "changelog.json"
        bad_programs.write_text("{invalid json!!!")
        bad_changelog.write_text("not json at all")
        monkeypatch.setattr(generate_site, "PROGRAMS_FILE", bad_programs)
        monkeypatch.setattr(generate_site, "CHANGELOG_FILE", bad_changelog)
        programs, changelog = generate_site.load_data()
        assert programs == {"metadata": {}, "programs": []}
        assert changelog == {"entries": []}


class TestGetHtml:
    def _generate_html(self):
        """Helper to generate HTML output for testing."""
        css = generate_site.get_css()
        js = generate_site.get_js()
        programs_json = json.dumps([])
        changelog_json = json.dumps([])
        return generate_site.get_html(
            css=css,
            js=js,
            programs_json=programs_json,
            changelog_json=changelog_json,
            total=0,
            num_platforms=0,
            num_categories=0,
            last_updated="2024-01-01T00:00:00Z",
            cat_options="",
            plat_options="",
        )

    def test_get_html_structure(self):
        """Verify output contains DOCTYPE, html lang, head, body, closing html."""
        html = self._generate_html()
        assert "<!DOCTYPE html>" in html
        assert '<html lang="en">' in html
        assert "<head>" in html
        assert "<body>" in html
        assert "</html>" in html

    def test_get_html_accessibility(self):
        """Verify output contains skip-link, aria-label attributes, role='list' on programs grid."""
        html = self._generate_html()
        assert 'class="skip-link"' in html
        assert "aria-label" in html
        assert 'role="list"' in html

    def test_get_html_theme_toggle(self):
        """Verify output contains theme-toggle button."""
        html = self._generate_html()
        assert 'id="theme-toggle"' in html

    def test_get_html_programs_embedded(self):
        """Verify programs JSON is embedded in script tag."""
        css = generate_site.get_css()
        js = generate_site.get_js()
        programs = [{"name": "Test", "platform": "H1"}]
        programs_json = json.dumps(programs)
        changelog_json = json.dumps([])
        html = generate_site.get_html(
            css=css,
            js=js,
            programs_json=programs_json,
            changelog_json=changelog_json,
            total=1,
            num_platforms=1,
            num_categories=1,
            last_updated="2024-01-01T00:00:00Z",
            cat_options="",
            plat_options="",
        )
        assert "const PROGRAMS =" in html
        assert '"Test"' in html


class TestGetCss:
    def test_get_css_returns_string(self):
        """Verify get_css() returns non-empty string with CSS content."""
        css = generate_site.get_css()
        assert isinstance(css, str)
        assert len(css) > 0
        assert "body" in css
        assert "{" in css


class TestGetJs:
    def test_get_js_returns_string(self):
        """Verify get_js() returns non-empty string with JS functions."""
        js = generate_site.get_js()
        assert isinstance(js, str)
        assert len(js) > 0
        assert "function init" in js
        assert "function render" in js
        assert "function escapeHtml" in js


class TestMain:
    def test_main_generates_file(self, monkeypatch, tmp_path):
        """Use monkeypatch to redirect output to tmp_path and verify index.html is created."""
        # Set up data files
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        programs_file = data_dir / "programs.json"
        changelog_file = data_dir / "changelog.json"
        programs_file.write_text(json.dumps({
            "metadata": {"last_updated": "2024-01-01T00:00:00Z"},
            "programs": [
                {
                    "name": "TestProg",
                    "platform": "HackerOne",
                    "url": "https://example.com",
                    "type": "bounty",
                    "bounty_min": 100,
                    "bounty_max": 5000,
                    "currency": "USD",
                    "managed": True,
                    "category": "Technology",
                    "assets": [],
                }
            ],
        }))
        changelog_file.write_text(json.dumps({"entries": []}))

        # Set up output directory
        docs_dir = tmp_path / "docs"

        # Monkeypatch module-level variables
        monkeypatch.setattr(generate_site, "PROGRAMS_FILE", programs_file)
        monkeypatch.setattr(generate_site, "CHANGELOG_FILE", changelog_file)
        monkeypatch.setattr(generate_site, "DOCS_DIR", docs_dir)

        generate_site.main()

        output_file = docs_dir / "index.html"
        assert output_file.exists()
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "TestProg" in content
