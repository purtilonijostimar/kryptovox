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


def transcribe_groq(audio_path: Path) -> dict:
    """Transcribe using Groq Whisper API (~100x realtime, $0.111/hr)."""
    from groq import Groq
    import math

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print(f"  Transcribing via Groq: {audio_path.name}")

    # Groq has a 25MB file size limit — chunk if needed
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    print(f"  File size: {file_size_mb:.1f} MB")

    all_text = []
    all_segments = []
    offset_s = 0

    if file_size_mb <= 24:
        # Single request
        with open(audio_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model           = "whisper-large-v3",
                file            = f,
                response_format = "verbose_json",
                language        = "en",
            )
        def _seg(s):
            if isinstance(s, dict):
                return {"start": s.get("start", 0), "end": s.get("end", 0), "text": s.get("text", "")}
            return {"start": s.start, "end": s.end, "text": s.text}

        return {
            "text":     response.text,
            "segments": [_seg(s) for s in (response.segments or [])],
            "language": getattr(response, "language", "en"),
        }
    else:
        # Chunk large files using ffmpeg
        print(f"  File too large — chunking into 20-min segments...")
        import subprocess, tempfile, shutil
        chunk_dir = Path(tempfile.mkdtemp())
        chunk_duration = 1200  # 20 minutes

        try:
            # Split with ffmpeg and convert to mp3
            subprocess.run([
                "ffmpeg", "-i", str(audio_path),
                "-f", "segment", "-segment_time", str(chunk_duration),
                "-acodec", "libmp3lame", "-q:a", "3",
                str(chunk_dir / "chunk_%03d.mp3")
            ], check=True, capture_output=True)

            chunks = sorted(chunk_dir.glob("chunk_*.mp3"))
            print(f"  {len(chunks)} chunks created")

            for chunk in chunks:
                with open(chunk, "rb") as f:
                    resp = client.audio.transcriptions.create(
                        model           = "whisper-large-v3",
                        file            = f,
                        response_format = "verbose_json",
                        language        = "en",
                    )
                all_text.append(resp.text)
                for s in (resp.segments or []):
                    # Groq returns dicts or objects depending on version
                    if isinstance(s, dict):
                        all_segments.append({
                            "start": round(s.get("start", 0) + offset_s, 2),
                            "end":   round(s.get("end",   0) + offset_s, 2),
                            "text":  s.get("text", ""),
                        })
                    else:
                        all_segments.append({
                            "start": round(s.start + offset_s, 2),
                            "end":   round(s.end   + offset_s, 2),
                            "text":  s.text,
                        })
                offset_s += chunk_duration

            return {
                "text":     " ".join(all_text),
                "segments": all_segments,
                "language": "en",
            }
        finally:
            shutil.rmtree(chunk_dir, ignore_errors=True)


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
    return {
        "text":     response.text,
        "segments": [{"start": s.start, "end": s.end, "text": s.text}
                     for s in response.segments],
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
        if WHISPER_MODE == "groq":
            result = transcribe_groq(audio_path)
        elif WHISPER_MODE == "api":
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

    files = [f for f in sorted(audio_dir.iterdir()) if f.suffix in ('.mp3', '.webm', '.m4a', '.opus', '.ogg') and not f.name.endswith('.info.json')]
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
