from pathlib import Path


def test_release_contract_has_launcher_and_privacy_boundary():
    root = Path(__file__).parents[1]
    assert (root / "tools/awtui-live").is_file()
    text = (root / "docs/INSTALLATION.md").read_text(encoding="utf-8")
    assert "credentials" in text
    assert "raw transcripts" in text
    assert "python3 -m pytest -q" in text
