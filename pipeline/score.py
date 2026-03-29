#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptovox — Witness Credibility Scoring (WCS)
Applies the 6-dimension WCS to extracted accounts.
Uses Claude to score each dimension with rationale and evidence quotes.
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
SCORED_DIR     = ROOT / "data" / "scored"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

WCS_PROMPT = """You are scoring a witness testimony transcript for the Kryptovox academic research project.

This project applies forensic psychology credibility tools to anomalous encounter testimony. Your job is to score how structurally consistent this account is with GENUINE TRAUMATIC MEMORY — not whether the encounter occurred.

High score = account structurally resembles genuine experiential memory
Low score = account structurally resembles fabricated/confabulated narrative

Score each of the 6 dimensions from 0–10 using the rubrics below. Be conservative and precise. Quote specific transcript passages as evidence for each score.

---

DIMENSION RUBRICS:

1. INTERNAL CONSISTENCY (IC) — Does the account hold together with itself?
- 9-10: No contradictions. Stable descriptions throughout. Minor uncertainties acknowledged naturally.
- 7-8: One minor inconsistency, likely memory artifact. Core account stable.
- 5-6: 2-3 inconsistencies. Some description drift. Timeline gaps.
- 3-4: Multiple inconsistencies. Significant description drift.
- 0-2: Major contradictions. Physically impossible timeline. Description fundamentally changes.

2. SENSORY SPECIFICITY (SS) — Real memories encode multi-channel sensory detail.
- 9-10: Rich detail across ≥4 sensory channels (visual/audio/smell/touch/kinesthetic). Strong peripheral detail (what they were doing before, environmental context).
- 7-8: Good detail across 3 channels. Some peripheral detail.
- 5-6: Primarily visual. Some specificity. Minimal peripheral context.
- 3-4: Generic description. One or two channels. No peripheral context.
- 0-2: Bare visual description only. No sensory texture.

3. SPONTANEITY & AUTHENTICITY (SA) — Genuine witnesses volunteer details, correct themselves, admit uncertainty.
- 9-10: Multiple unprompted details. Self-corrections. Uncertainty admissions. "I know how this sounds" type statements. Non-linear account structure.
- 7-8: Some unprompted details. At least one self-correction or uncertainty admission.
- 5-6: Mostly reactive to questions. Some spontaneous detail.
- 3-4: Entirely reactive. Perfect linear narrative. No self-correction.
- 0-2: Scripted-feeling. Resists uncertainty. No spontaneous additions.

4. EMOTIONAL AUTHENTICITY (EA) — The hardest to fake. Weight 25%.
- 9-10: Emotional breaks at narratively appropriate moments (eye contact, vocalisation, departure). Long disclosure delay. Post-encounter life changes. Accurate physiological stress responses (tunnel vision, time distortion, paralysis). Voice quality markers.
- 7-8: Some emotional breaks with clear narrative triggers. Some post-impact described. Meaningful disclosure delay.
- 5-6: Emotional content present but without strong narrative anchoring.
- 3-4: Emotional display without clear triggers. Quick disclosure. Little post-impact.
- 0-2: Flat affect throughout OR performing emotion uniformly (not tied to specific moments).

5. CONTEXT PLAUSIBILITY (CP) — Does the context make basic sense?
- 9-10: Legitimate reason to be there. Geography internally consistent. Activity/time/season coherent.
- 5-7: Mostly plausible. Minor inconsistencies in context.
- 3-4: Some implausible elements.
- 0-2: Context makes little sense or is internally contradictory.

6. CORROBORATION (CO) — Any external support?
- 8-10: Multiple witnesses OR physical evidence AND prior area reports.
- 5-7: One corroborating factor.
- 3-4: Reported to one credible person immediately after.
- 0-2: Entirely uncorroborated solo account.

---

TRANSCRIPT:
{transcript}

---

Return JSON only, no preamble:

{{
  "IC": {{
    "score": 0,
    "rationale": "...",
    "evidence_quotes": ["..."]
  }},
  "SS": {{
    "score": 0,
    "rationale": "...",
    "evidence_quotes": ["..."]
  }},
  "SA": {{
    "score": 0,
    "rationale": "...",
    "evidence_quotes": ["..."]
  }},
  "EA": {{
    "score": 0,
    "rationale": "...",
    "evidence_quotes": ["..."]
  }},
  "CP": {{
    "score": 0,
    "rationale": "...",
    "evidence_quotes": ["..."]
  }},
  "CO": {{
    "score": 0,
    "rationale": "...",
    "evidence_quotes": ["..."]
  }},
  "WCS_raw": 0.0,
  "WCS_band": "Exceptional|Strong|Moderate|Weak|Unreliable",
  "notable_patterns": [],
  "self_illuminated_eyes": false,
  "specific_smell_reported": false,
  "paralysis_or_freeze": false,
  "disclosure_delay_indicated": false,
  "post_encounter_life_change": false,
  "minimisation_phrases": [],
  "scoring_notes": "..."
}}"""

WCS_WEIGHTS = {
    "IC": 0.20,
    "SS": 0.20,
    "SA": 0.15,
    "EA": 0.25,
    "CP": 0.10,
    "CO": 0.10,
}

WCS_BANDS = [
    (8.5, "Exceptional"),
    (7.0, "Strong"),
    (5.5, "Moderate"),
    (4.0, "Weak"),
    (0.0, "Unreliable"),
]


def calculate_wcs(scores: dict) -> float:
    total = sum(scores[k] * WCS_WEIGHTS[k] for k in WCS_WEIGHTS if k in scores)
    return round(total, 2)


def get_band(wcs: float) -> str:
    for threshold, label in WCS_BANDS:
        if wcs >= threshold:
            return label
    return "Unreliable"


def score_transcript(transcript_path: Path, channel_key: str, force: bool = False) -> Path:
    """Score a single transcript."""
    import anthropic

    out_dir  = SCORED_DIR / channel_key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (transcript_path.stem + "_wcs.json")

    if out_path.exists() and not force:
        print(f"  ⏭️  Already scored: {transcript_path.name}")
        return out_path

    print(f"\n📊 Scoring: {transcript_path.name}")

    with open(transcript_path, encoding="utf-8") as f:
        data = json.load(f)

    transcript_text = data.get("text", "")
    if len(transcript_text) < 500:
        print(f"  ⚠️  Too short — skipping")
        return None

    if len(transcript_text) > 30_000:
        # Take first 20k + last 10k — captures intro context and emotional peak/resolution
        transcript_text = transcript_text[:20_000] + "\n\n[...]\n\n" + transcript_text[-10_000:]

    prompt = WCS_PROMPT.format(transcript=transcript_text)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    start  = time.time()

    try:
        message = client.messages.create(
            model      = "claude-haiku-4-5",
            max_tokens = 3000,
            messages   = [{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        result = json.loads(raw)

        # Calculate WCS
        dim_scores = {k: result[k]["score"] for k in WCS_WEIGHTS if k in result}
        wcs = calculate_wcs(dim_scores)
        band = get_band(wcs)

        result["WCS_raw"]      = wcs
        result["WCS_band"]     = band
        result["scored_at"]    = datetime.now().isoformat()
        result["channel"]      = channel_key
        result["audio_file"]   = transcript_path.stem
        result["score_time_s"] = round(time.time() - start, 1)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  ✅ WCS: {wcs:.1f} ({band})")
        for k in WCS_WEIGHTS:
            if k in result:
                print(f"     {k}: {result[k]['score']:.0f}")
        return out_path

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def score_channel(channel_key: str, limit: int = None, force: bool = False):
    tr_dir = TRANSCRIPT_DIR / channel_key
    if not tr_dir.exists():
        print(f"No transcripts for: {channel_key}")
        return

    files = sorted(tr_dir.glob("*.json"))[:limit] if limit else sorted(tr_dir.glob("*.json"))

    print(f"\n{'='*60}")
    print(f"Scoring: {channel_key} ({len(files)} transcripts)")
    print(f"{'='*60}")

    results = []
    for f in files:
        path = score_transcript(f, channel_key, force=force)
        if path:
            with open(path) as fp:
                results.append(json.load(fp))
        time.sleep(0.5)

    if results:
        wcs_scores = [r["WCS_raw"] for r in results]
        avg = sum(wcs_scores) / len(wcs_scores)
        bands = {}
        for r in results:
            b = r.get("WCS_band", "?")
            bands[b] = bands.get(b, 0) + 1

        print(f"\n📊 Summary for {channel_key}:")
        print(f"   Scored:  {len(results)} accounts")
        print(f"   Avg WCS: {avg:.1f}")
        print(f"   Bands:   {bands}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kryptovox WCS scorer")
    parser.add_argument("channel", nargs="?")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.channel:
        score_channel(args.channel, limit=args.limit, force=args.force)
    else:
        parser.print_help()
