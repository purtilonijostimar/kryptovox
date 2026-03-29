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

def is_valid_interview(data: dict) -> bool:
    """
    Exclude episodes that are not genuine first-person witness interviews.
    An account is excluded if:
      - interview_count is 0 (no first-person witness)
      - narrator_profile is 'documentary' or 'compilation'
      - WCS_band is 'Unreliable' AND interview_count < 1
    Low-WCS genuine interviews are kept — they belong in the corpus as the weak end.
    Only non-interview format episodes are excluded.
    """
    ic = data.get("interview_count", 1)
    narrator = (data.get("narrator_profile") or "").lower()
    band = data.get("WCS_band", "")

    # Explicit non-interview format
    if narrator in ("documentary", "compilation"):
        return False
    # No first-person witness at all
    if isinstance(ic, (int, float)) and ic < 1:
        return False
    # Unreliable AND no witness — belt-and-suspenders
    if band == "Unreliable" and isinstance(ic, (int, float)) and ic == 0:
        return False

    return True


def export():
    accounts  = []
    excluded  = []

    for channel_dir in sorted(SCORED_DIR.iterdir()):
        if not channel_dir.is_dir():
            continue
        for f in sorted(channel_dir.glob("*_wcs.json")):
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            # Strip heavy fields to keep file small
            data.pop("segments", None)
            data["channel_key"] = channel_dir.name

            if is_valid_interview(data):
                accounts.append(data)
            else:
                excluded.append(f.name)

    output = {
        "generated_at": datetime.now().isoformat(),
        "total":        len(accounts),
        "excluded":     len(excluded),
        "accounts":     accounts,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported {len(accounts)} accounts → {OUT_PATH}")
    if excluded:
        print(f"   ⛔ Excluded {len(excluded)} non-interview episodes:")
        for name in excluded:
            print(f"      {name}")
    print(f"   File size: {OUT_PATH.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    export()
