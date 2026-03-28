#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptovox — Database Ingestion
Takes scored extracted accounts and loads them into Supabase.
"""

import os
import json
import requests
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT         = Path(__file__).parent.parent
EXTRACTED_DIR = ROOT / "data" / "extracted"
SCORED_DIR    = ROOT / "data" / "scored"

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
H   = {
    "apikey":        KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "resolution=merge-duplicates",
}


def merge_account(extracted: dict, scored: dict) -> dict:
    """Flatten extracted + scored into a single Supabase row."""
    c   = extracted.get("creature", {})
    enc = extracted.get("encounter", {})
    wit = extracted.get("witness", {})
    beh = extracted.get("behaviour", {})
    wr  = extracted.get("witness_response", {})
    pe  = extracted.get("post_encounter", {})
    src = extracted.get("source", {})

    row = {
        # Source
        "channel":       src.get("channel"),
        "audio_file":    src.get("audio_file"),
        "episode_title": src.get("episode_title"),

        # Witness
        "witness_approximate_age": wit.get("approximate_age"),
        "witness_profession":      wit.get("profession_category"),
        "witness_group_size":      wit.get("group_size"),
        "witness_context":         wit.get("context"),
        "witness_skeptic_before":  wit.get("stated_skeptic_before"),
        "disclosure_delay_years":  wit.get("disclosure_delay_years"),

        # Location
        "location_country": enc.get("location_country"),
        "location_state":   enc.get("location_state_region"),
        "terrain_type":     enc.get("terrain_type"),
        "near_water":       enc.get("near_water"),
        "elevation":        enc.get("elevation"),

        # Time
        "date_approximate": enc.get("date_approximate"),
        "time_of_day":      enc.get("time_of_day"),
        "season":           enc.get("season"),
        "weather":          enc.get("weather"),
        "duration_seconds": enc.get("duration_seconds"),
        "distance_metres":  enc.get("distance_metres"),

        # Creature
        "creature_type":        scored.get("phenomena_type") or c.get("type"),
        "height_ft":            c.get("height_estimate_ft"),
        "build":                c.get("build"),
        "hair_colour":          c.get("hair_colour"),
        "face_type":            c.get("face_type"),
        "eyes_glow":            c.get("eyes_glow"),
        "eyes_colour":          c.get("eyes_colour"),
        "eyes_self_illuminated": c.get("eyes_self_illuminated"),
        "smell_reported":       c.get("smell_reported"),
        "smell_description":    c.get("smell_description"),
        "vocalisation_type":    c.get("vocalisation_type"),
        "bipedal":              c.get("bipedal"),
        "quadrupedal_also":     c.get("quadrupedal_also_observed"),

        # Behaviour
        "approach_type":  beh.get("approach_type"),
        "threat_display": beh.get("threat_display"),
        "eye_contact":    beh.get("eye_contact_made"),
        "departure_type": beh.get("departure_type"),

        # Witness response
        "immediate_reaction":      wr.get("immediate_reaction"),
        "weapon_present":          wr.get("weapon_present"),
        "fled":                    wr.get("fled"),
        "physiological_responses": wr.get("physiological_responses") or [],

        # Post-encounter
        "returned_to_location":    pe.get("returned_to_location"),
        "behaviour_changed":       pe.get("behaviour_change"),
        "reported_to_authorities": pe.get("reported_to_authorities"),
        "physical_evidence":       pe.get("physical_evidence_found"),

        # WCS scores
        "wcs_ic":    (scored.get("IC") or {}).get("score"),
        "wcs_ss":    (scored.get("SS") or {}).get("score"),
        "wcs_sa":    (scored.get("SA") or {}).get("score"),
        "wcs_ea":    (scored.get("EA") or {}).get("score"),
        "wcs_cp":    (scored.get("CP") or {}).get("score"),
        "wcs_co":    (scored.get("CO") or {}).get("score"),
        "wcs_total": scored.get("WCS_raw"),
        "wcs_band":  scored.get("WCS_band"),

        # Pattern flags
        "self_illuminated_eyes": scored.get("self_illuminated_eyes"),
        "specific_smell":        scored.get("specific_smell_reported"),
        "paralysis_reported":    scored.get("paralysis_or_freeze"),
        "post_encounter_change": scored.get("post_encounter_life_change"),
        "minimisation_present":  bool(scored.get("minimisation_phrases")),

        # Raw
        "raw_extracted": extracted,
        "raw_wcs":       scored,
    }

    # Remove None values (let DB use defaults)
    return {k: v for k, v in row.items() if v is not None}


def ingest_account(channel_key: str, stem: str) -> bool:
    """Load one account into Supabase."""
    ex_path  = EXTRACTED_DIR / channel_key / f"{stem}.json"
    wcs_path = SCORED_DIR    / channel_key / f"{stem}_wcs.json"

    if not ex_path.exists():
        print(f"  ❌ No extracted file: {ex_path}")
        return False

    with open(ex_path) as f:
        extracted = json.load(f)

    scored = {}
    if wcs_path.exists():
        with open(wcs_path) as f:
            scored = json.load(f)

    row = merge_account(extracted, scored)

    r = requests.post(
        f"{URL}/rest/v1/kv_accounts",
        headers = H,
        json    = row,
    )

    if r.status_code in (200, 201):
        wcs = row.get("wcs_total", "?")
        print(f"  ✅ Ingested: {stem} | WCS={wcs}")
        return True
    else:
        print(f"  ❌ Failed ({r.status_code}): {r.text[:200]}")
        return False


def ingest_channel(channel_key: str, limit: int = None):
    files = sorted((EXTRACTED_DIR / channel_key).glob("*.json"))[:limit] if limit else sorted((EXTRACTED_DIR / channel_key).glob("*.json"))

    print(f"\n{'='*60}")
    print(f"Ingesting: {channel_key} ({len(files)} accounts)")
    print(f"{'='*60}")

    done = 0
    for f in files:
        if ingest_account(channel_key, f.stem):
            done += 1
    print(f"\n✅ Ingested: {done}/{len(files)}")


def get_stats():
    """Show database stats."""
    r = requests.get(f"{URL}/rest/v1/kv_accounts?select=creature_type,wcs_band,wcs_total", headers={**H, "Prefer": "count=exact"})
    accounts = r.json()
    total = len(accounts)
    if not total:
        print("No accounts in database yet.")
        return

    from collections import Counter
    creatures = Counter(a.get("creature_type") for a in accounts)
    bands     = Counter(a.get("wcs_band") for a in accounts)
    scores    = [a["wcs_total"] for a in accounts if a.get("wcs_total")]
    avg_wcs   = sum(scores) / len(scores) if scores else 0

    print(f"\n📊 Kryptovox Database Stats:")
    print(f"   Total accounts: {total}")
    print(f"   By creature:    {dict(creatures)}")
    print(f"   By WCS band:    {dict(bands)}")
    print(f"   Average WCS:    {avg_wcs:.1f}")

    eyes = sum(1 for a in accounts if a.get("eyes_self_illuminated"))
    smell = sum(1 for a in accounts if a.get("specific_smell"))
    print(f"\n   Self-illuminated eyes: {eyes}/{total} ({eyes/total*100:.0f}%)")
    print(f"   Specific smell:        {smell}/{total} ({smell/total*100:.0f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", nargs="?")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    if args.stats:
        get_stats()
    elif args.channel:
        ingest_channel(args.channel, limit=args.limit)
    else:
        parser.print_help()
