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

# Title fragments that reliably identify non-witness-interview episodes
NON_INTERVIEW_TITLE_FRAGMENTS = [
    "q & a", "q&a", "livestream", "live stream",
    "i write books", "we hunt", "we photograph", "we film",
    "documentary", "documentary &", "dogman files",
    "hunting grounds", "part 2",   # compilations
    "author", "researcher", "investigator",
]


def is_valid_interview(data: dict) -> bool:
    """
    Keep only genuine first-person witness interviews.
    Excludes:
      - Any account scoring Unreliable (WCS < 4.0)
      - Episodes with non-interview format titles (Q&A, livestream, documentary, etc.)
      - Episodes where interview_count = 0 or narrator_profile = documentary/compilation
    """
    band    = data.get("WCS_band", "")
    ic      = data.get("interview_count")
    narrator = (data.get("narrator_profile") or "").lower()
    title   = (data.get("audio_file") or data.get("title") or "").lower()

    # Any Unreliable score — not fit for the research corpus
    if band == "Unreliable":
        return False

    # Explicit non-interview narrator profile
    if narrator in ("documentary", "compilation"):
        return False

    # No first-person witness
    if isinstance(ic, (int, float)) and ic < 1:
        return False

    # Title-based safety net for episodes extraction missed
    for fragment in NON_INTERVIEW_TITLE_FRAGMENTS:
        if fragment in title:
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
        "generated_at":    datetime.now().isoformat(),
        "total":           len(accounts),   # always = len(accounts) — what's shown
        "total_processed": len(accounts) + len(excluded),
        "excluded":        len(excluded),
        "accounts":        accounts,
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
