#!/usr/bin/env python3
"""Build a bounded source/runtime bundle with an explicit host manifest."""
from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))
from awtui.connect import environment_fingerprint, runtime_manifest, runtime_archive_name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    facts = environment_fingerprint()
    with tarfile.open(args.output, "w:gz") as bundle:
        for source in (ROOT / "src/awtui").glob("*.py"):
            bundle.add(source, arcname=f"awtui/{source.name}")
        manifest = ROOT / ".runtime-manifest.json"
        manifest.write_text(json.dumps(runtime_manifest(facts), sort_keys=True) + "\n", encoding="utf-8")
        bundle.add(manifest, arcname="runtime-manifest.json")
        manifest.unlink()
    print(runtime_archive_name(facts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
