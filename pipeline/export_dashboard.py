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

ROOT          = Path(__file__).parent.parent
SCORED_DIR    = ROOT / "data" / "scored"
EXTRACTED_DIR = ROOT / "data" / "extracted"
OUT_PATH      = ROOT / "docs" / "dashboard.json"

import sys
sys.path.insert(0, str(Path(__file__).parent))
from download import NON_INTERVIEW_FRAGMENTS as NON_INTERVIEW_TITLE_FRAGMENTS


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


def flatten_extracted(extracted: dict) -> dict:
    """
    Flatten the nested extracted JSON into a single-level dict.
    Nested sections: witness, encounter, creature, behaviour, anomalies,
    community, analysis, extraction_meta.
    Scoring fields (WCS etc.) stay at top level.
    """
    flat = {}

    # Preserve top-level scalar fields
    for k, v in extracted.items():
        if not isinstance(v, dict):
            flat[k] = v

    # Flatten known nested sections
    NESTED_SECTIONS = [
        "witness", "encounter", "creature", "behaviour",
        "anomalies", "community", "analysis", "extraction_meta", "source",
    ]
    for section in NESTED_SECTIONS:
        if section in extracted and isinstance(extracted[section], dict):
            for k, v in extracted[section].items():
                # Don't overwrite if already set at top level
                if k not in flat:
                    flat[k] = v

    return flat


def merge_account(scored_path: Path, channel_key: str) -> dict:
    """
    Merge extracted fields + scored fields into one flat record.
    Extracted fields (flattened) form the base; scored fields overwrite on conflict.
    """
    with open(scored_path, encoding="utf-8") as f:
        scored = json.load(f)

    # Corresponding extracted file: strip _wcs suffix
    stem = scored_path.stem.replace("_wcs", "")
    extracted_path = EXTRACTED_DIR / channel_key / (stem + ".json")

    if extracted_path.exists():
        with open(extracted_path, encoding="utf-8") as f:
            raw_extracted = json.load(f)
        flat_extracted = flatten_extracted(raw_extracted)
        # Scored fields win on conflict (WCS scores are authoritative)
        merged = {**flat_extracted, **scored}
    else:
        merged = scored

    # Strip heavy fields
    for key in ("segments", "full_transcript", "raw_text", "_source_transcript"):
        merged.pop(key, None)

    # Strip verbose WCS rationale text — keep scores and evidence quotes
    for dim in ("EA", "SA", "IC", "SS", "DC", "CO", "CP", "NC"):
        if dim in merged and isinstance(merged[dim], dict):
            merged[dim].pop("rationale", None)

    merged["channel_key"] = channel_key
    return merged


def export():
    accounts  = []
    excluded  = []

    for channel_dir in sorted(SCORED_DIR.iterdir()):
        if not channel_dir.is_dir():
            continue
        for f in sorted(channel_dir.glob("*_wcs.json")):
            data = merge_account(f, channel_dir.name)

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
