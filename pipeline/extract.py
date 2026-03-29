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

Special fields:

referral_source: How did witness find this platform? Extract verbatim if stated.
referral_type: "peer" (friend/family referred them) / "professional" (ranger, police, employer) / "self" (found it themselves) / "unknown"
hesitation_to_disclose: true if witness describes reluctance, fear, or delay before coming forward
hesitation_description: what specifically held them back (ridicule, career, family, disbelief)
relationship_impact: true if witness describes relationships damaged by their experience or disclosure
relationship_impact_description: who, how, what changed
sought_explanation_before_disclosing: true if witness tried to find a rational explanation before accepting what they saw
witness_demeanour: your assessment of their overall demeanour during the interview — "calm" / "distressed" / "relieved" / "reluctant" / "eager" / "matter_of_fact"

career_risk_score (0–3): How much would this person lose by going public?
  0 = anonymous/retired/nothing to lose
  1 = minor social risk
  2 = professional reputation at stake (police, nurse, teacher, military)
  3 = high-profile, career-ending risk if associated with this claim

narrator_profile: Your assessment of the narrator type based on HOW they tell the story:
  "genuine" — non-linear, self-corrects, admits uncertainty, downplays, sensory-rich
  "fantasy_prone" — enjoys the telling, vivid but generic, seeks validation
  "fabricator" — too clean, too linear, no uncertainty, performed emotion
  "confabulator" — inconsistent in ways suggesting false memory not lying
  "indeterminate" — insufficient data

anomaly_score (0–10): How well do conventional explanations fit?
  0 = easily explained (bear, large dog, misidentification)
  5 = conventional explanation possible but strained
  10 = no conventional explanation accounts for all described details
conventional_explanation: Best possible mundane explanation
conventional_explanation_fit: "strong" / "possible" / "strained" / "implausible"
anomalous_details: List the specific details that resist conventional explanation

light_anomalies: Any unusual light phenomena reported — before, during, or after the encounter.
  orb_timing: "before" / "during" / "after" / "before_and_during" etc.
  orb_behaviour: how it moved — stationary, drifting, erratic, following witness, disappearing
  light_preceded_encounter: true if a light anomaly appeared BEFORE the creature was seen
  creature_associated_with_light: true if the light seemed connected to or emitted by the creature
  ambient_light_change: unexplained brightening, darkening, or colour shift in the environment

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
    "profession_detail": null,
    "group_size": null,
    "context": null,
    "prior_outdoor_experience": null,
    "stated_skeptic_before": null,
    "disclosure_delay_years": null,
    "told_before_this_interview": null,
    "career_risk_score": null,
    "narrator_profile": null,
    "career_risk_notes": null,
    "referral_source": null,
    "referral_type": null,
    "hesitation_to_disclose": null,
    "hesitation_description": null,
    "relationship_impact": null,
    "relationship_impact_description": null,
    "sought_explanation_before_disclosing": null,
    "witness_demeanour": null
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
    "departure_description_quote": null,
    "watches_then_leaves": null,
    "silent_departure": null,
    "felt_known_by_creature": null
  }},
  "witness_response": {{
    "immediate_reaction": null,
    "weapon_present": null,
    "weapon_used": null,
    "fled": null,
    "vehicle_nearby": null,
    "called_for_help": null,
    "physiological_responses": [],
    "physiological_quote": null,
    "paralysis_or_freeze": null,
    "time_distortion": null,
    "infrasound_felt": null,
    "tunnel_vision": null
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
  "light_anomalies": {{
    "any_light_anomaly": null,
    "orbs_reported": null,
    "orb_colour": null,
    "orb_behaviour": null,
    "orb_timing": null,
    "light_preceded_encounter": null,
    "light_followed_encounter": null,
    "ambient_light_change": null,
    "creature_associated_with_light": null,
    "light_description_quote": null,
    "light_anomaly_notes": null
  }},
  "anomaly_assessment": {{
    "anomaly_score": null,
    "conventional_explanation": null,
    "conventional_explanation_fit": null,
    "anomalous_details": []
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

        import re
        raw = message.content[0].text.strip()

        # Extract JSON from response (Claude sometimes adds preamble)
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        else:
            match = re.search(r'\{[\s\S]*\}', raw)
            if match:
                raw = match.group(0)

        try:
            extracted = json.loads(raw)
        except json.JSONDecodeError:
            from json_repair import repair_json
            extracted = json.loads(repair_json(raw))
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
