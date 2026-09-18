from pathlib import Path
import re


def test_release_contract_has_launcher_and_privacy_boundary():
    root = Path(__file__).parents[1]
    assert (root / "tools/awtui-live").is_file()
    text = (root / "docs/INSTALLATION.md").read_text(encoding="utf-8")
    assert "credentials" in text
    assert "raw transcripts" in text
    assert "python3 -m pytest -q" in text


def test_package_version_matches_current_release_line():
    root = Path(__file__).parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    version = re.search(r'^version = "([^"]+)"$', pyproject, re.MULTILINE)
    assert version is not None
    assert version.group(1) == "0.4.3"
