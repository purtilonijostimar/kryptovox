# Kryptovox — Setup Guide

## What you need

- Python 3.10+
- Git
- A GPU helps (NVIDIA recommended for local Whisper) — but not required
- Anthropic API key (Claude — for extraction and scoring)
- OpenAI API key (optional — for Whisper API fallback and embeddings)
- Supabase account (free tier is fine)

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/purtilonijostimar/kryptovox.git
cd kryptovox
```

---

## Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

If you want local Whisper with GPU (recommended for speed):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install openai-whisper
```

If you don't have a GPU (will use CPU — slow but works):
```bash
pip install openai-whisper
```

Or skip local Whisper entirely and use the OpenAI API (costs ~$0.006/minute):
Set `WHISPER_MODE=api` in your `.env`.

---

## Step 3 — Configure environment

Copy the example and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here        # optional (Whisper API fallback)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
WHISPER_MODE=local                     # or "api"
WHISPER_MODEL=large-v3                 # or "base" (faster, less accurate)
```

---

## Step 4 — Set up Supabase tables

```bash
python pipeline/db_setup.py
```

This prints SQL. Copy it into the Supabase SQL Editor and run it.

Verify tables were created:
```bash
python pipeline/db_setup.py --verify
```

---

## Step 5 — Run the pilot (5 episodes)

### Download
```bash
# Download first 5 episodes of Dogman Encounters
python pipeline/download.py dogman_encounters --limit 5
```

### Transcribe
```bash
python pipeline/transcribe.py dogman_encounters --limit 5
```

### Extract structured data
```bash
python pipeline/extract.py dogman_encounters --limit 5
```

### Score (WCS)
```bash
python pipeline/score.py dogman_encounters --limit 5
```

### Load into database
```bash
python pipeline/ingest.py dogman_encounters --limit 5
```

### Check results
```bash
python pipeline/ingest.py --stats
```

---

## Full pipeline (after pilot validated)

```bash
python pipeline/download.py dogman_encounters
python pipeline/transcribe.py dogman_encounters
python pipeline/extract.py dogman_encounters
python pipeline/score.py dogman_encounters
python pipeline/ingest.py dogman_encounters
```

Repeat for each channel.

---

## Model recommendations

| Use case | Whisper model | Speed |
|---|---|---|
| Pilot testing | `base` | Fast (2min audio → 20s) |
| Production | `large-v3` | Slow but best accuracy (~1:1 ratio on CPU, 10x on GPU) |
| API (no GPU) | OpenAI Whisper API | Fast, costs money |

For the full corpus (~500 hours), `large-v3` on GPU is strongly recommended.
On a modern NVIDIA GPU (RTX 3080+), 500 hours transcribes in ~50 hours.

---

## File structure

```
kryptovox/
├── data/
│   ├── audio/              ← downloaded mp3 files, organised by channel
│   ├── transcripts/        ← Whisper output JSON, one per episode
│   ├── extracted/          ← Claude extraction JSON, one per episode
│   └── scored/             ← WCS scored JSON, one per episode
├── pipeline/
│   ├── download.py         ← yt-dlp wrapper
│   ├── transcribe.py       ← Whisper wrapper
│   ├── extract.py          ← Claude extraction
│   ├── score.py            ← WCS scoring
│   ├── ingest.py           ← Supabase ingestion
│   └── db_setup.py         ← Database schema
├── analysis/               ← Analysis scripts (coming soon)
├── docs/                   ← Research documentation
└── .env                    ← Your API keys (never commit this)
```

---

## The data never leaves your machine until Supabase ingestion

- Audio files stay local
- Transcripts stay local
- Only the structured extracted records go to Supabase
- Raw transcripts are never sent to the database

---

## Questions?

Check the docs:
- [VISION.md](docs/VISION.md) — what this is
- [RESEARCH_DESIGN.md](docs/RESEARCH_DESIGN.md) — methodology
- [CREDIBILITY_AND_PATTERNS.md](docs/CREDIBILITY_AND_PATTERNS.md) — WCS system
