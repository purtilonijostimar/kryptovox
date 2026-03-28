#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptovox — Extraction Pipeline
Sends transcripts to Claude for structured data extraction.
Outputs one JSON record per account conforming to the Kryptovox Account Schema.
"""

import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ROOT          = Path(__file__).parent.parent
TRANSCRIPT_DIR = ROOT / "data" / "transcripts"
EXTRACTED_DIR  = ROOT / "data" / "extracted"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

EXTRACTION_PROMPT = """You are extracting structured data from a witness testimony transcript for the Kryptovox academic research project.

The project studies anomalous bipedal creature encounter testimony. Your job is to extract factual descriptors from what the witness says — not to evaluate whether the encounter occurred.

Be conservative and precise:
- Only fill fields where the witness explicitly states something
- Use null for any field not mentioned
- Use exact witness language in quote fields where specified
- confidence fields are YOUR confidence in the extraction (0.0–1.0), not the witness's credibility

Transcript:
{transcript}

Return a JSON object with this exact structure. Fill every field you can from the transcript:

{{
  "source": {{
    "channel": "{channel}",
    "audio_file": "{audio_file}",
    "episode_title": null
  }},
  "witness": {{
    "approximate_age": null,
    "profession_category": null,
    "group_size": null,
    "context": null,
    "prior_outdoor_experience": null,
    "stated_skeptic_before": null,
    "disclosure_delay_years": null,
    "told_before_this_interview": null
  }},
  "encounter": {{
    "location_country": null,
    "location_state_region": null,
    "terrain_type": null,
    "near_water": null,
    "elevation": null,
    "date_approximate": null,
    "time_of_day": null,
    "season": null,
    "weather": null,
    "duration_seconds": null,
    "distance_metres": null,
    "visibility": null
  }},
  "creature": {{
    "type": null,
    "height_estimate_ft": null,
    "build": null,
    "hair_colour": null,
    "hair_texture": null,
    "face_type": null,
    "face_description_quote": null,
    "eyes_glow": null,
    "eyes_colour": null,
    "eyes_self_illuminated": null,
    "eyes_description_quote": null,
    "smell_reported": null,
    "smell_description": null,
    "smell_description_quote": null,
    "vocalisation_type": null,
    "vocalisation_description_quote": null,
    "bipedal": null,
    "quadrupedal_also_observed": null,
    "hands_described": null,
    "hands_description_quote": null,
    "feet_described": null,
    "size_comparison": null
  }},
  "behaviour": {{
    "how_discovered": null,
    "approach_type": null,
    "movement_description": null,
    "threat_display": null,
    "reaction_to_witness": null,
    "eye_contact_made": null,
    "departure_type": null,
    "departure_description_quote": null
  }},
  "witness_response": {{
    "immediate_reaction": null,
    "weapon_present": null,
    "weapon_used": null,
    "fled": null,
    "vehicle_nearby": null,
    "called_for_help": null,
    "physiological_responses": [],
    "physiological_quote": null
  }},
  "post_encounter": {{
    "returned_to_location": null,
    "behaviour_change": null,
    "behaviour_change_description": null,
    "nightmares_or_intrusive_thoughts": null,
    "reported_to_authorities": null,
    "physical_evidence_found": null,
    "physical_evidence_description": null
  }},
  "testimony_markers": {{
    "minimisation_phrases": [],
    "voice_breaks_detected": null,
    "voice_break_triggers": [],
    "crying_detected": null,
    "long_pauses_detected": null,
    "refused_to_continue": null,
    "self_corrections_count": null,
    "uncertainty_admissions": [],
    "non_linear_structure": null,
    "spontaneous_detail_count": null
  }},
  "extraction_meta": {{
    "extracted_at": "{now}",
    "confidence_overall": null,
    "fields_with_low_confidence": [],
    "notes": null,
    "phenomena_type": null
  }}
}}"""


def extract_transcript(transcript_path: Path, channel_key: str, force: bool = False) -> Path:
    """Extract structured data from a single transcript."""
    import anthropic

    out_dir  = EXTRACTED_DIR / channel_key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (transcript_path.stem + ".json")

    if out_path.exists() and not force:
        print(f"  ⏭️  Skipping (already extracted): {transcript_path.name}")
        return out_path

    print(f"\n🔍 Extracting: {transcript_path.name}")

    with open(transcript_path, encoding="utf-8") as f:
        data = json.load(f)

    transcript_text = data.get("text", "")
    if len(transcript_text) < 500:
        print(f"  ⚠️  Transcript too short ({len(transcript_text)} chars) — skipping")
        return None

    # Truncate if too long for context window (keep first 80k chars — ~2hrs)
    if len(transcript_text) > 80_000:
        transcript_text = transcript_text[:80_000]
        print(f"  ℹ️  Transcript truncated to 80k chars")

    prompt = EXTRACTION_PROMPT.format(
        transcript = transcript_text,
        channel    = channel_key,
        audio_file = transcript_path.stem,
        now        = datetime.now().isoformat(),
    )

    client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    start   = time.time()

    try:
        message = client.messages.create(
            model      = "claude-haiku-4-5",
            max_tokens = 4096,
            messages   = [{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()

        # Extract JSON from response (Claude sometimes adds preamble)
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        extracted = json.loads(raw)
        extracted["_source_transcript"] = str(transcript_path)
        extracted["_extract_time_s"]    = round(time.time() - start, 1)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(extracted, f, ensure_ascii=False, indent=2)

        conf = extracted.get("extraction_meta", {}).get("confidence_overall", "?")
        print(f"  ✅ Done in {time.time()-start:.0f}s | confidence={conf}")
        return out_path

    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parse error: {e}")
        # Save raw response for debugging
        (out_dir / (transcript_path.stem + "_raw.txt")).write_text(raw, encoding="utf-8")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def extract_channel(channel_key: str, limit: int = None, force: bool = False):
    """Extract all transcripts for a channel."""
    tr_dir = TRANSCRIPT_DIR / channel_key
    if not tr_dir.exists():
        print(f"No transcripts for: {channel_key}")
        return

    files = sorted(tr_dir.glob("*.json"))
    if limit:
        files = files[:limit]

    print(f"\n{'='*60}")
    print(f"Extracting: {channel_key} ({len(files)} transcripts)")
    print(f"{'='*60}")

    done = 0
    for f in files:
        result = extract_transcript(f, channel_key, force=force)
        if result:
            done += 1
        time.sleep(0.5)  # rate limit

    print(f"\n✅ Extracted: {done}/{len(files)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kryptovox extraction pipeline")
    parser.add_argument("channel", nargs="?")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.channel:
        extract_channel(args.channel, limit=args.limit, force=args.force)
    else:
        parser.print_help()
