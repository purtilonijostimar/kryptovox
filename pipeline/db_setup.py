#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptovox — Database Setup
Creates all Supabase tables for the Kryptovox project.
Run once to initialise the schema.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey":        KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type":  "application/json",
}

# ── SQL to create all tables ───────────────────────────────────────────────────
# Run this in Supabase SQL Editor:

SCHEMA_SQL = """
-- ============================================================
-- KRYPTOVOX DATABASE SCHEMA
-- Run in Supabase SQL Editor
-- ============================================================

-- Accounts: one row per encounter account
CREATE TABLE IF NOT EXISTS kv_accounts (
    id                      BIGSERIAL PRIMARY KEY,
    created_at              TIMESTAMPTZ DEFAULT NOW(),

    -- Source
    channel                 TEXT,
    audio_file              TEXT UNIQUE,
    episode_title           TEXT,

    -- Witness
    witness_approximate_age INTEGER,
    witness_profession      TEXT,
    witness_group_size      INTEGER,
    witness_context         TEXT,           -- hunting, hiking, driving, camping...
    witness_skeptic_before  BOOLEAN,
    disclosure_delay_years  NUMERIC,

    -- Encounter location
    location_country        TEXT,
    location_state          TEXT,
    terrain_type            TEXT,
    near_water              BOOLEAN,
    elevation               TEXT,

    -- Encounter time
    date_approximate        TEXT,
    time_of_day             TEXT,
    season                  TEXT,
    weather                 TEXT,
    duration_seconds        INTEGER,
    distance_metres         NUMERIC,

    -- Creature
    creature_type           TEXT,           -- dogman, bigfoot, unknown
    height_ft               NUMERIC,
    build                   TEXT,
    hair_colour             TEXT,
    face_type               TEXT,           -- canine, simian, human, hybrid
    eyes_glow               BOOLEAN,
    eyes_colour             TEXT,
    eyes_self_illuminated   BOOLEAN,
    smell_reported          BOOLEAN,
    smell_description       TEXT,
    vocalisation_type       TEXT,
    bipedal                 BOOLEAN,
    quadrupedal_also        BOOLEAN,

    -- Behaviour
    approach_type           TEXT,
    threat_display          BOOLEAN,
    eye_contact             BOOLEAN,
    departure_type          TEXT,

    -- Witness response
    immediate_reaction      TEXT,
    weapon_present          BOOLEAN,
    fled                    BOOLEAN,
    physiological_responses TEXT[],         -- array of: tunnel_vision, paralysis, time_distortion...

    -- Post-encounter
    returned_to_location    BOOLEAN,
    behaviour_changed       BOOLEAN,
    reported_to_authorities BOOLEAN,
    physical_evidence       BOOLEAN,

    -- WCS scores
    wcs_ic                  NUMERIC,        -- Internal Consistency 0-10
    wcs_ss                  NUMERIC,        -- Sensory Specificity 0-10
    wcs_sa                  NUMERIC,        -- Spontaneity & Authenticity 0-10
    wcs_ea                  NUMERIC,        -- Emotional Authenticity 0-10
    wcs_cp                  NUMERIC,        -- Context Plausibility 0-10
    wcs_co                  NUMERIC,        -- Corroboration 0-10
    wcs_total               NUMERIC,        -- Composite 0-10
    wcs_band                TEXT,           -- Exceptional/Strong/Moderate/Weak/Unreliable

    -- Pattern flags
    self_illuminated_eyes   BOOLEAN,
    specific_smell          BOOLEAN,
    paralysis_reported      BOOLEAN,
    post_encounter_change   BOOLEAN,
    minimisation_present    BOOLEAN,

    -- Raw data
    raw_extracted           JSONB,
    raw_wcs                 JSONB,
    notes                   TEXT
);

-- Quotes: notable quotes extracted from accounts
CREATE TABLE IF NOT EXISTS kv_quotes (
    id          BIGSERIAL PRIMARY KEY,
    account_id  BIGINT REFERENCES kv_accounts(id),
    category    TEXT,           -- eyes, smell, behaviour, emotional, departure...
    quote       TEXT,
    context     TEXT,
    timestamp_s NUMERIC
);

-- Emotional markers: timestamped emotional events
CREATE TABLE IF NOT EXISTS kv_emotional_markers (
    id              BIGSERIAL PRIMARY KEY,
    account_id      BIGINT REFERENCES kv_accounts(id),
    marker_type     TEXT,       -- voice_break, crying, long_pause, refused_to_continue
    trigger         TEXT,       -- first_sighting, eye_contact, vocalisation, departure...
    timestamp_s     NUMERIC,
    description     TEXT
);

-- Folklore records: historical and folkloric accounts (Layer 2)
CREATE TABLE IF NOT EXISTS kv_folklore (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    culture         TEXT,
    region          TEXT,
    country         TEXT,
    time_period     TEXT,
    source_title    TEXT,
    source_type     TEXT,       -- primary, ethnographic, oral_tradition...
    entity_name     TEXT,
    entity_type     TEXT,       -- dogman, bigfoot, hybrid, unknown
    isolation_score INTEGER,    -- 0=no plausible contact, 3=likely contact
    -- Descriptor mapping
    height_described        BOOLEAN,
    eyes_illuminated        BOOLEAN,
    bipedal                 BOOLEAN,
    smell_described         BOOLEAN,
    forest_terrain          BOOLEAN,
    aggressive_to_humans    BOOLEAN,
    watches_then_retreats   BOOLEAN,
    -- Raw
    description_text TEXT,
    source_url       TEXT,
    notes            TEXT
);

-- Patterns: discovered patterns with PCS scores
CREATE TABLE IF NOT EXISTS kv_patterns (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    pattern_name    TEXT UNIQUE,
    description     TEXT,
    phenomenon      TEXT,       -- dogman, bigfoot, both
    frequency_pct   NUMERIC,
    account_count   INTEGER,
    pcs_frequency           NUMERIC,
    pcs_cross_cultural      NUMERIC,
    pcs_pre_media           NUMERIC,
    pcs_specificity         NUMERIC,
    pcs_independent_confirm NUMERIC,
    pcs_total               NUMERIC,
    pcs_label               TEXT,       -- Core/Supporting/Emerging/Noise
    historical_matches      INTEGER,
    notes                   TEXT
);

-- Enable Row Level Security (read-only public access)
ALTER TABLE kv_accounts  ENABLE ROW LEVEL SECURITY;
ALTER TABLE kv_quotes    ENABLE ROW LEVEL SECURITY;
ALTER TABLE kv_folklore  ENABLE ROW LEVEL SECURITY;
ALTER TABLE kv_patterns  ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read" ON kv_accounts  FOR SELECT USING (true);
CREATE POLICY "Public read" ON kv_quotes    FOR SELECT USING (true);
CREATE POLICY "Public read" ON kv_folklore  FOR SELECT USING (true);
CREATE POLICY "Public read" ON kv_patterns  FOR SELECT USING (true);

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_accounts_creature  ON kv_accounts(creature_type);
CREATE INDEX IF NOT EXISTS idx_accounts_wcs       ON kv_accounts(wcs_total);
CREATE INDEX IF NOT EXISTS idx_accounts_location  ON kv_accounts(location_country, location_state);
CREATE INDEX IF NOT EXISTS idx_accounts_eyes      ON kv_accounts(eyes_self_illuminated);
CREATE INDEX IF NOT EXISTS idx_accounts_channel   ON kv_accounts(channel);

-- ============================================================
-- END SCHEMA
-- ============================================================
"""


def print_setup_instructions():
    """Print the setup instructions."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              KRYPTOVOX DATABASE SETUP                        ║
╚══════════════════════════════════════════════════════════════╝

1. Go to your Supabase project: https://supabase.com/dashboard
2. Open the SQL Editor
3. Paste and run the SQL below
4. Done — all tables created

════════════════════════════════════════════════════════════════
""")
    print(SCHEMA_SQL)
    print("""
════════════════════════════════════════════════════════════════

After running the SQL, update your .env file:

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

Then run:
    python pipeline/ingest.py --test
""")


def verify_tables():
    """Check if Kryptovox tables exist in Supabase."""
    tables = ["kv_accounts", "kv_quotes", "kv_folklore", "kv_patterns"]
    print("\nVerifying Kryptovox tables in Supabase...\n")
    for table in tables:
        r = requests.get(
            f"{URL}/rest/v1/{table}?limit=1",
            headers=HEADERS
        )
        status = "✅" if r.status_code == 200 else f"❌ ({r.status_code})"
        print(f"  {table:30s} {status}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Verify tables exist")
    parser.add_argument("--sql",    action="store_true", help="Print SQL only")
    args = parser.parse_args()

    if args.verify:
        verify_tables()
    else:
        print_setup_instructions()
