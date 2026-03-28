#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptovox — Acoustic Analysis Pipeline
Extracts prosodic and emotional audio features using librosa.
Aligns features with Whisper transcript timestamps.
Flags segments with significant acoustic deviations — potential emotional markers.
"""

import os
import json
import warnings
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")

ROOT          = Path(__file__).parent.parent
AUDIO_DIR     = ROOT / "data" / "audio"
TRANSCRIPT_DIR = ROOT / "data" / "transcripts"
ACOUSTIC_DIR  = ROOT / "data" / "acoustic"

AUDIO_EXTENSIONS = {'.mp3', '.webm', '.m4a', '.opus', '.ogg', '.wav'}

# ── Thresholds for flagging ────────────────────────────────────────────────────
PITCH_DROP_SD     = 1.2   # z-score: pitch drops >1.2 SD below baseline
PITCH_RISE_SD     = 1.2   # z-score: pitch rises >1.2 SD above baseline
RATE_SLOW_SD      = 1.0   # speaking rate slows >1.0 SD below baseline
VOLUME_DROP_SD    = 1.2   # volume drops >1.2 SD below baseline
PAUSE_THRESHOLD_S = 1.5   # pauses longer than 1.5s within a segment
TREMOR_THRESHOLD  = 0.15  # pitch instability index above this = voice tremor


def load_audio(audio_path: Path, sr: int = 16000):
    """Load audio file, return (samples, sample_rate)."""
    import librosa
    print(f"  Loading audio: {audio_path.name}")
    y, sr_out = librosa.load(str(audio_path), sr=sr, mono=True)
    duration = len(y) / sr_out
    print(f"  Duration: {duration/60:.1f} min | Sample rate: {sr_out}Hz")
    return y, sr_out


def extract_global_features(y: np.ndarray, sr: int) -> dict:
    """
    Extract baseline prosodic features across the full recording.
    Used as baseline to compare segment-level features against.
    """
    import librosa

    # Pitch (F0) via pyin — more accurate than yin for speech
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sr,
        frame_length=2048,
    )
    f0_voiced = f0[voiced_flag & ~np.isnan(f0)]

    # RMS energy (volume proxy)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]

    # Zero crossing rate (voice quality / breathiness proxy)
    zcr = librosa.feature.zero_crossing_rate(y, frame_length=2048, hop_length=512)[0]

    # Spectral centroid (brightness — drops with emotional weight)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    baseline = {
        "duration_seconds":     round(len(y) / sr, 1),
        "pitch_mean_hz":        round(float(np.mean(f0_voiced)), 2) if len(f0_voiced) > 0 else None,
        "pitch_std_hz":         round(float(np.std(f0_voiced)), 2)  if len(f0_voiced) > 0 else None,
        "pitch_median_hz":      round(float(np.median(f0_voiced)), 2) if len(f0_voiced) > 0 else None,
        "voiced_fraction":      round(float(np.mean(voiced_flag)), 3),
        "rms_mean":             round(float(np.mean(rms)), 6),
        "rms_std":              round(float(np.std(rms)), 6),
        "zcr_mean":             round(float(np.mean(zcr)), 6),
        "spectral_centroid_mean": round(float(np.mean(centroid)), 2),
        "spectral_centroid_std":  round(float(np.std(centroid)), 2),
    }

    print(f"  Baseline pitch: {baseline['pitch_mean_hz']} Hz ± {baseline['pitch_std_hz']}")
    print(f"  Voiced fraction: {baseline['voiced_fraction']:.1%}")
    return baseline, f0, voiced_flag, rms, zcr, centroid


def analyse_segment(
    y: np.ndarray,
    sr: int,
    start_s: float,
    end_s: float,
    baseline: dict,
    f0_full: np.ndarray,
    voiced_full: np.ndarray,
    rms_full: np.ndarray,
) -> dict:
    """
    Analyse a single transcript segment (from Whisper timestamps).
    Returns prosodic features and flags for this segment.
    """
    import librosa

    hop_length = 512
    start_frame = int(start_s * sr / hop_length)
    end_frame   = int(end_s   * sr / hop_length)

    # Clamp to array bounds
    start_frame = max(0, start_frame)
    end_frame   = min(len(rms_full) - 1, end_frame)

    if end_frame <= start_frame:
        return None

    # Sample-level slice
    start_sample = int(start_s * sr)
    end_sample   = min(int(end_s * sr), len(y))
    y_seg        = y[start_sample:end_sample]

    if len(y_seg) < sr * 0.5:  # skip segments shorter than 0.5s
        return None

    # Pitch in this segment
    f0_seg     = f0_full[start_frame:end_frame]
    voiced_seg = voiced_full[start_frame:end_frame]
    f0_voiced  = f0_seg[voiced_seg & ~np.isnan(f0_seg)]

    # Volume in this segment
    rms_seg = rms_full[start_frame:end_frame]

    # Speaking rate proxy: voiced frames / total frames
    voiced_rate = float(np.mean(voiced_seg)) if len(voiced_seg) > 0 else 0

    # Pitch tremor: std of pitch within segment (high = unstable/trembling voice)
    pitch_tremor = float(np.std(f0_voiced)) if len(f0_voiced) > 5 else 0

    # Detect long pauses within segment (silences > PAUSE_THRESHOLD_S)
    # Using RMS: frames below 10% of mean RMS = silence
    silence_threshold = baseline["rms_mean"] * 0.1
    silent_frames     = np.sum(rms_seg < silence_threshold)
    silence_duration  = silent_frames * hop_length / sr

    seg_pitch_mean = float(np.mean(f0_voiced)) if len(f0_voiced) > 0 else None
    seg_rms_mean   = float(np.mean(rms_seg))

    # ── Z-scores vs baseline ──────────────────────────────────────────────────
    flags = []

    if seg_pitch_mean and baseline["pitch_mean_hz"] and baseline["pitch_std_hz"]:
        pitch_z = (seg_pitch_mean - baseline["pitch_mean_hz"]) / (baseline["pitch_std_hz"] + 1e-9)
        if pitch_z < -PITCH_DROP_SD:
            flags.append({
                "type":     "pitch_drop",
                "severity": round(abs(pitch_z), 2),
                "note":     f"Pitch {abs(pitch_z):.1f}SD below baseline"
            })
        if pitch_z > PITCH_RISE_SD:
            flags.append({
                "type":     "pitch_rise",
                "severity": round(pitch_z, 2),
                "note":     f"Pitch {pitch_z:.1f}SD above baseline"
            })
    else:
        pitch_z = 0

    if baseline["rms_std"] > 0:
        rms_z = (seg_rms_mean - baseline["rms_mean"]) / (baseline["rms_std"] + 1e-9)
        if rms_z < -VOLUME_DROP_SD:
            flags.append({
                "type":     "volume_drop",
                "severity": round(abs(rms_z), 2),
                "note":     f"Volume {abs(rms_z):.1f}SD below baseline"
            })
    else:
        rms_z = 0

    if voiced_rate < (baseline["voiced_fraction"] - RATE_SLOW_SD * 0.15):
        flags.append({
            "type":     "speech_slowdown",
            "severity": round(baseline["voiced_fraction"] - voiced_rate, 3),
            "note":     f"Speaking rate significantly reduced"
        })

    if silence_duration > PAUSE_THRESHOLD_S:
        flags.append({
            "type":     "long_pause",
            "severity": round(silence_duration, 1),
            "note":     f"Silence of {silence_duration:.1f}s detected within segment"
        })

    if pitch_tremor > TREMOR_THRESHOLD * (baseline.get("pitch_std_hz") or 30):
        flags.append({
            "type":     "voice_tremor",
            "severity": round(pitch_tremor, 2),
            "note":     f"Pitch instability (tremor) detected"
        })

    # Composite emotional weight score
    emotional_weight = min(10.0, sum(f["severity"] for f in flags))

    return {
        "start_s":        round(start_s, 2),
        "end_s":          round(end_s, 2),
        "duration_s":     round(end_s - start_s, 2),
        "pitch_mean_hz":  round(seg_pitch_mean, 2) if seg_pitch_mean else None,
        "pitch_z":        round(pitch_z, 3),
        "rms_mean":       round(seg_rms_mean, 6),
        "rms_z":          round(rms_z, 3),
        "voiced_rate":    round(voiced_rate, 3),
        "silence_s":      round(silence_duration, 2),
        "pitch_tremor":   round(pitch_tremor, 2),
        "flags":          flags,
        "emotional_weight": round(emotional_weight, 2),
        "flagged":        len(flags) > 0,
    }


def analyse_file(audio_path: Path, transcript_path: Path, channel_key: str, force: bool = False) -> Path:
    """
    Full acoustic analysis of one episode.
    Aligns with transcript segments from Whisper output.
    """
    out_dir  = ACOUSTIC_DIR / channel_key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (audio_path.stem + "_acoustic.json")

    if out_path.exists() and not force:
        print(f"  ⏭️  Already analysed: {audio_path.name}")
        return out_path

    print(f"\n🎵 Acoustic analysis: {audio_path.name}")

    # Load transcript for segment timestamps
    with open(transcript_path, encoding="utf-8") as f:
        transcript = json.load(f)
    segments = transcript.get("segments", [])

    if not segments:
        print(f"  ⚠️  No segments in transcript — skipping")
        return None

    import librosa
    y, sr = load_audio(audio_path)

    print(f"  Extracting global features...")
    baseline, f0_full, voiced_full, rms_full, zcr_full, centroid_full = extract_global_features(y, sr)

    print(f"  Analysing {len(segments)} segments...")
    segment_results = []
    flagged_segments = []

    for seg in segments:
        start_s = seg.get("start", 0)
        end_s   = seg.get("end",   0)
        text    = seg.get("text",  "").strip()

        result = analyse_segment(y, sr, start_s, end_s, baseline, f0_full, voiced_full, rms_full)
        if result is None:
            continue

        result["text"] = text
        segment_results.append(result)

        if result["flagged"]:
            flagged_segments.append({
                "start_s":        result["start_s"],
                "end_s":          result["end_s"],
                "text":           text,
                "flags":          result["flags"],
                "emotional_weight": result["emotional_weight"],
            })

    # ── Summary statistics ─────────────────────────────────────────────────────
    weights = [s["emotional_weight"] for s in segment_results]
    top_moments = sorted(flagged_segments, key=lambda x: x["emotional_weight"], reverse=True)[:10]

    # Flag type breakdown
    flag_types = {}
    for seg in flagged_segments:
        for f in seg["flags"]:
            flag_types[f["type"]] = flag_types.get(f["type"], 0) + 1

    output = {
        "meta": {
            "audio_file":      audio_path.name,
            "channel":         channel_key,
            "analysed_at":     datetime.now().isoformat(),
            "total_segments":  len(segment_results),
            "flagged_segments": len(flagged_segments),
            "flagged_pct":     round(len(flagged_segments) / max(len(segment_results), 1) * 100, 1),
        },
        "baseline":     baseline,
        "flag_summary": flag_types,
        "top_emotional_moments": top_moments,
        "segments":     segment_results,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  ✅ Done | {len(flagged_segments)}/{len(segment_results)} segments flagged ({output['meta']['flagged_pct']}%)")
    print(f"  Top flag types: {flag_types}")
    if top_moments:
        print(f"  Highest emotional weight: {top_moments[0]['emotional_weight']:.1f}")
        print(f"  → \"{top_moments[0]['text'][:80]}...\"")

    return out_path


def analyse_channel(channel_key: str, limit: int = None, force: bool = False):
    """Analyse all episodes for a channel."""
    audio_dir = AUDIO_DIR / channel_key
    tr_dir    = TRANSCRIPT_DIR / channel_key

    if not audio_dir.exists():
        print(f"No audio for: {channel_key}")
        return

    audio_files = sorted([
        f for f in audio_dir.iterdir()
        if f.suffix in AUDIO_EXTENSIONS
    ])
    if limit:
        audio_files = audio_files[:limit]

    print(f"\n{'='*60}")
    print(f"Acoustic analysis: {channel_key} ({len(audio_files)} files)")
    print(f"{'='*60}")

    done = 0
    for af in audio_files:
        tr_path = tr_dir / (af.stem + ".json")
        if not tr_path.exists():
            print(f"  ⚠️  No transcript yet for {af.name} — transcribe first")
            continue
        result = analyse_file(af, tr_path, channel_key, force=force)
        if result:
            done += 1

    print(f"\n✅ Analysed: {done}/{len(audio_files)}")


def print_emotional_timeline(acoustic_path: Path, min_weight: float = 1.0):
    """Print a readable timeline of emotional moments for one episode."""
    with open(acoustic_path, encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n🎭 Emotional timeline: {data['meta']['audio_file']}")
    print(f"   Flagged: {data['meta']['flagged_segments']}/{data['meta']['total_segments']} segments\n")

    for moment in data["top_emotional_moments"]:
        if moment["emotional_weight"] < min_weight:
            continue
        mins  = int(moment["start_s"] // 60)
        secs  = int(moment["start_s"] % 60)
        flags = ", ".join(f["type"] for f in moment["flags"])
        print(f"  [{mins:02d}:{secs:02d}] weight={moment['emotional_weight']:.1f} | {flags}")
        print(f"         \"{moment['text'][:100]}\"")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kryptovox acoustic analysis")
    parser.add_argument("channel",   nargs="?",             help="Channel key")
    parser.add_argument("--limit",   type=int,              help="Max files")
    parser.add_argument("--force",   action="store_true",   help="Re-analyse existing")
    parser.add_argument("--timeline", type=str,             help="Print timeline for acoustic JSON file")
    args = parser.parse_args()

    if args.timeline:
        print_emotional_timeline(Path(args.timeline))
    elif args.channel:
        analyse_channel(args.channel, limit=args.limit, force=args.force)
    else:
        parser.print_help()
