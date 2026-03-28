# Kryptovox — Data Pipeline
**Version 0.1 | March 2026**

---

## Overview

```
YouTube channels
    ↓ yt-dlp (audio extraction)
Audio files (.mp3)
    ↓ Whisper (transcription)
Raw transcripts (.txt / .json with timestamps)
    ↓ Claude (structured extraction)
Per-account JSON records (extraction schema)
    ↓ Supabase (storage + query)
Kryptovox database
    ↓ Analysis layer (Python)
Findings + visualisations
```

---

## Phase 1 — Audio Acquisition

### Primary Sources
| Channel | Subject | Est. Episodes | Priority |
|---|---|---|---|
| Dogman Encounters (Vic Cundiff) | Dogman | 500+ | 🔴 First |
| BFRO (official) | Bigfoot | 200+ | 🟡 Second |
| Bigfoot Society | Bigfoot | 300+ | 🟡 Second |
| Sasquatch Chronicles | Bigfoot | 400+ | 🟡 Second |
| Missing 411 (Paulides) | Disappearances | 100+ | 🟢 Later |

### Tool: yt-dlp
```bash
# Download audio only from entire channel
yt-dlp -x --audio-format mp3 \
  --output "%(channel)s/%(upload_date)s_%(title)s.%(ext)s" \
  --write-info-json \
  --write-description \
  https://youtube.com/@DogmanEncounters
```

Metadata saved alongside each file: upload date, title, description, video ID.

---

## Phase 2 — Transcription

### Tool: OpenAI Whisper (local)
Run locally on GPU for speed and cost efficiency. Whisper `large-v3` model for best accuracy on accents and emotional speech.

```python
import whisper
model = whisper.load_model("large-v3")
result = model.transcribe("episode.mp3", language="en")
# result['segments'] → timestamped chunks
```

**Output per episode:**
- Full transcript text
- Timestamped segments (for locating emotional markers)
- Word-level confidence scores

**Storage:** Raw transcripts in `data/transcripts/` as `.json` files, one per episode.

---

## Phase 3 — Structured Extraction

### Tool: Claude (Haiku for speed/cost, Sonnet for quality check)

Each transcript is chunked and sent to Claude with a structured extraction prompt. Output: JSON conforming to the Kryptovox Account Schema.

### Kryptovox Account Schema v0.1

```json
{
  "account_id": "DE_0342",
  "source": {
    "channel": "Dogman Encounters",
    "episode": 342,
    "published": "2021-08-14",
    "url": "https://youtube.com/..."
  },
  "witness": {
    "anonymous_id": "W-DE-0342",
    "approximate_age": 45,
    "profession_category": "outdoor_worker",
    "group_size": 1,
    "context": "hunting"
  },
  "encounter": {
    "location": {
      "state": "Michigan",
      "country": "USA",
      "terrain": "dense_forest",
      "proximity_to_water": true,
      "elevation": "low"
    },
    "date_approximate": "2018",
    "time_of_day": "dusk",
    "season": "autumn",
    "duration_seconds": 45,
    "distance_metres": 30
  },
  "creature": {
    "type": "dogman",
    "height_estimate_ft": 7.5,
    "build": "muscular",
    "hair_colour": "dark_brown",
    "face_type": "canine",
    "eyes": {
      "glow": true,
      "colour": "amber",
      "self_illuminated": true
    },
    "smell_reported": true,
    "smell_description": "musky_rotten",
    "vocalisation": "growl",
    "bipedal": true,
    "quadrupedal_also": false
  },
  "behaviour": {
    "approach_type": "stationary_observed",
    "movement": "fluid",
    "threat_display": false,
    "reaction_to_witness": "held_eye_contact",
    "departure": "retreated_into_treeline"
  },
  "witness_response": {
    "immediate": "freeze",
    "weapon_present": true,
    "weapon_used": false,
    "vehicle_nearby": false,
    "fled": true
  },
  "testimony_markers": {
    "voice_break": [{"at_seconds": 847, "trigger": "eye_contact_description"}],
    "crying": [{"at_seconds": 1203, "trigger": "creature_departure"}],
    "long_pause": [{"at_seconds": 623, "trigger": "first_sighting"}],
    "minimisation": ["I know how this sounds", "you're going to think I'm crazy"],
    "refusal_to_continue": false,
    "overall_credibility_markers": ["consistent_timeline", "specific_sensory_detail", "reluctant_to_share"]
  },
  "extraction_confidence": 0.87,
  "notes": "Witness was an experienced hunter, 20+ years in Michigan woods. Account internally consistent."
}
```

---

## Phase 4 — Database

### Supabase tables

**accounts** — one row per encounter account
**testimony_markers** — normalised emotional marker events (linked to account_id + timestamp)
**descriptors** — normalised physical descriptors per account
**sources** — channel/episode metadata
**folklore_records** — historical records (Layer 2)
**cross_references** — links between modern accounts and historical records

---

## Phase 5 — Analysis

### Planned analyses

**Descriptor clustering**
Which physical traits co-occur? Is there a statistically consistent "encounter profile" or multiple distinct subtypes?

**Geographic distribution**
Heatmap of encounters by terrain type, proximity to water, elevation. Do Dogman and Bigfoot occupy distinct territories?

**Temporal patterns**
Time of day, season, year. Is there a trend in reporting (more reports = more awareness, or genuine increase)?

**Emotional marker analysis**
At what narrative moments do witnesses break down? Is the pattern consistent across independent accounts?

**Cross-cultural consistency**
Do accounts from different countries, collected independently, describe the same physical traits at statistically significant rates?

**Fabrication resistance analysis**
Compare descriptor variance in Kryptovox accounts vs known fabricated accounts (hoaxes that were later admitted). Genuine accounts typically show higher internal consistency and more specific sensory detail.

---

## Phase 6 — Slovenian Research Thread

Separate pipeline for historical record:

1. ZRC SAZU digital archive — search for volkodlak, divji mož (wildman), gozdni možje
2. Štrekelj's folk poetry collection — systematic review for relevant entities
3. Regional ethnographic journals (Traditiones, Glasnik SED)
4. Outreach to Slovenian ethnologists / folklorists
5. Potential field interviews with elderly rural informants in forested regions

---

## Cost Estimate (rough)

| Component | Cost |
|---|---|
| yt-dlp downloads | Free |
| Whisper local transcription | ~€0 (GPU time) or ~$0.006/min via API |
| Claude extraction (Haiku) | ~$0.25 per 100K tokens → ~$15–30 for full corpus |
| Supabase | Free tier sufficient to start |
| **Total initial run** | **~$30–50** |

---

## Next Steps

- [ ] Set up yt-dlp on local machine (Windows or dedicated server)
- [ ] Test Whisper transcription on 5 episodes — validate output quality
- [ ] Draft Claude extraction prompt — test on 10 transcripts
- [ ] Define final Supabase schema
- [ ] Begin Dogman Encounters download (priority channel)
