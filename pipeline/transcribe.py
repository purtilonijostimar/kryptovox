#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptovox — Transcription Pipeline
Transcribes audio files using OpenAI Whisper.
Supports local model (GPU) or OpenAI API.
Outputs timestamped JSON transcripts.
"""

import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ROOT           = Path(__file__).parent.parent
AUDIO_DIR      = ROOT / "data" / "audio"
TRANSCRIPT_DIR = ROOT / "data" / "transcripts"
WHISPER_MODE   = os.getenv("WHISPER_MODE", "local")
WHISPER_MODEL  = os.getenv("WHISPER_MODEL", "large-v3")


def transcribe_local(audio_path: Path) -> dict:
    """Transcribe using local Whisper model."""
    import whisper
    print(f"  Loading Whisper model: {WHISPER_MODEL}")
    model = whisper.load_model(WHISPER_MODEL)
    print(f"  Transcribing: {audio_path.name}")
    result = model.transcribe(
        str(audio_path),
        language   = "en",
        verbose    = False,
        word_timestamps = True,
    )
    return result


def transcribe_api(audio_path: Path) -> dict:
    """Transcribe using OpenAI Whisper API ($0.006/min)."""
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print(f"  Transcribing via API: {audio_path.name}")
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model            = "whisper-1",
            file             = f,
            response_format  = "verbose_json",
            timestamp_granularities = ["segment"],
        )
    # Normalise to same format as local
    return {
        "text":     response.text,
        "segments": [
            {
                "start": s.start,
                "end":   s.end,
                "text":  s.text,
            }
            for s in response.segments
        ],
        "language": response.language,
    }


def transcribe_file(audio_path: Path, channel_key: str, force: bool = False) -> Path:
    """
    Transcribe a single audio file.
    Returns path to output JSON.
    Skips if transcript already exists unless force=True.
    """
    out_dir = TRANSCRIPT_DIR / channel_key
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / (audio_path.stem + ".json")

    if out_path.exists() and not force:
        print(f"  ⏭️  Skipping (already transcribed): {audio_path.name}")
        return out_path

    print(f"\n🎙️  Transcribing: {audio_path.name}")
    start = time.time()

    try:
        if WHISPER_MODE == "api":
            result = transcribe_api(audio_path)
        else:
            result = transcribe_local(audio_path)

        elapsed = time.time() - start
        duration = result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0

        transcript = {
            "meta": {
                "audio_file":    audio_path.name,
                "channel":       channel_key,
                "transcribed_at": datetime.now().isoformat(),
                "whisper_mode":  WHISPER_MODE,
                "whisper_model": WHISPER_MODEL,
                "duration_seconds": round(duration, 1),
                "transcription_time_seconds": round(elapsed, 1),
            },
            "text":     result["text"],
            "segments": result.get("segments", []),
            "language": result.get("language", "en"),
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)

        word_count = len(result["text"].split())
        print(f"  ✅ Done in {elapsed:.0f}s | {word_count} words | {duration/60:.1f} min audio")
        return out_path

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None


def transcribe_channel(channel_key: str, limit: int = None, force: bool = False):
    """Transcribe all audio files for a channel."""
    audio_dir = AUDIO_DIR / channel_key
    if not audio_dir.exists():
        print(f"No audio found for channel: {channel_key}")
        return

    files = sorted(audio_dir.glob("*.mp3"))
    if limit:
        files = files[:limit]

    print(f"\n{'='*60}")
    print(f"Transcribing: {channel_key} ({len(files)} files)")
    print(f"{'='*60}")

    done = 0
    for audio_path in files:
        result = transcribe_file(audio_path, channel_key, force=force)
        if result:
            done += 1

    print(f"\n✅ Transcribed: {done}/{len(files)} files")


def list_transcripts():
    """Show transcription status."""
    print("\n📝 Transcription status:\n")
    for ch_dir in sorted(TRANSCRIPT_DIR.iterdir()) if TRANSCRIPT_DIR.exists() else []:
        if ch_dir.is_dir():
            files  = list(ch_dir.glob("*.json"))
            audio  = list((AUDIO_DIR / ch_dir.name).glob("*.mp3")) if (AUDIO_DIR / ch_dir.name).exists() else []
            print(f"  {ch_dir.name:30s} {len(files):4d} / {len(audio):4d} transcribed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kryptovox transcription pipeline")
    parser.add_argument("channel", nargs="?", help="Channel key (or 'list')")
    parser.add_argument("--limit", type=int,  help="Max files to transcribe")
    parser.add_argument("--force", action="store_true", help="Re-transcribe existing")
    parser.add_argument("--file",  type=str,  help="Transcribe single file")
    args = parser.parse_args()

    if args.channel == "list" or (not args.channel and not args.file):
        list_transcripts()
    elif args.file:
        p = Path(args.file)
        transcribe_file(p, p.parent.name, force=args.force)
    elif args.channel:
        transcribe_channel(args.channel, limit=args.limit, force=args.force)
