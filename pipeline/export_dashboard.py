#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptovox — Dashboard Export
Aggregates all scored accounts into a single dashboard.json for GitHub Pages.
Run after scoring: python pipeline/export_dashboard.py
"""

import json
from pathlib import Path
from datetime import datetime

ROOT       = Path(__file__).parent.parent
SCORED_DIR = ROOT / "data" / "scored"
OUT_PATH   = ROOT / "docs" / "dashboard.json"

def export():
    accounts = []

    for channel_dir in sorted(SCORED_DIR.iterdir()):
        if not channel_dir.is_dir():
            continue
        for f in sorted(channel_dir.glob("*_wcs.json")):
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            # Strip heavy fields to keep file small
            data.pop("segments", None)
            data["channel_key"] = channel_dir.name
            accounts.append(data)

    output = {
        "generated_at": datetime.now().isoformat(),
        "total":        len(accounts),
        "accounts":     accounts,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported {len(accounts)} accounts → {OUT_PATH}")
    print(f"   File size: {OUT_PATH.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    export()
