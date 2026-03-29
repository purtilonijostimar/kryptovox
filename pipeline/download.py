#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptovox — Download Pipeline
Pulls audio from YouTube channels/playlists using yt-dlp.
Saves audio as mp3 + metadata JSON alongside each file.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
AUDIO_DIR = ROOT / "data" / "audio"

# ── Non-interview title filter ─────────────────────────────────────────────────
# Episodes whose titles match any of these fragments are skipped at download time.
# They are not witness interviews and should not enter the pipeline.
# Add to this list as new patterns are identified.
NON_INTERVIEW_FRAGMENTS = [
    # Format types
    "q & a", "q&a", "live stream", "livestream",
    "documentary", "documentary &",
    # Author/researcher episodes (not witnesses)
    "i write books", "we hunt", "we photograph", "we film",
    "author interview", "researcher", "investigator",
    # Compilation/roundup formats
    "hunting grounds", "dogman files",
    # Misc confirmed non-witness episodes
    "dogman encounters q",          # Q&A series
]

def is_interview_title(title: str) -> bool:
    """Return True if the title looks like a genuine witness interview."""
    t = title.lower()
    for fragment in NON_INTERVIEW_FRAGMENTS:
        if fragment in t:
            return False
    return True


# ── Channel Registry ───────────────────────────────────────────────────────────
CHANNELS = {
    "dogman_encounters": {
        "url":      "https://www.youtube.com/@DogmanEncounters",
        "subject":  "dogman",
        "priority": 1,
    },
    "sasquatch_chronicles": {
        "url":      "https://www.youtube.com/@SasquatchChronicles",
        "subject":  "bigfoot",
        "priority": 2,
    },
    "bfro": {
        "url":      "https://www.youtube.com/@BFROofficial",
        "subject":  "bigfoot",
        "priority": 2,
    },
    "bigfoot_society": {
        "url":      "https://www.youtube.com/@TheBigfootSociety",
        "subject":  "bigfoot",
        "priority": 3,
    },
}


def download_channel(channel_key: str, limit: int = None, skip_existing: bool = True):
    """
    Download audio from a channel.
    
    Args:
        channel_key:    Key from CHANNELS dict
        limit:          Max episodes to download (None = all)
        skip_existing:  Skip if mp3 already exists
    """
    if channel_key not in CHANNELS:
        print(f"Unknown channel: {channel_key}. Available: {list(CHANNELS.keys())}")
        return

    ch      = CHANNELS[channel_key]
    out_dir = AUDIO_DIR / channel_key
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Downloading: {channel_key}")
    print(f"URL:         {ch['url']}")
    print(f"Subject:     {ch['subject']}")
    print(f"Output:      {out_dir}")
    if limit:
        print(f"Limit:       {limit} episodes")
    print(f"{'='*60}\n")

    # Build yt-dlp title exclusion filter
    # yt-dlp --match-filter supports basic expressions; we reject titles containing
    # any non-interview fragment by checking each one.
    # We use multiple --reject-title patterns (one per fragment) as the most reliable approach.
    reject_patterns = [f"(?i){frag}" for frag in NON_INTERVIEW_FRAGMENTS]

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--extract-audio",
        "--audio-format",     "best",
        "--audio-quality",    "0",
        "--output",           str(out_dir / "%(upload_date)s_%(id)s_%(title).80s.%(ext)s"),
        "--write-info-json",
        "--write-description",
        "--no-overwrites",
        "--ignore-errors",
        "--sleep-interval",   "2",
        "--max-sleep-interval","5",
    ]

    # Add reject-title filters for non-interview patterns
    for pattern in reject_patterns:
        cmd += ["--reject-title", pattern]

    if limit:
        # --max-downloads is global cap across all tabs/playlists
        # --playlist-end only caps per playlist tab (causes double-downloading)
        cmd += ["--max-downloads", str(limit)]

    cmd.append(ch["url"])

    print(f"Running: {' '.join(cmd[:6])} ... {ch['url']}\n")
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print(f"\n✅ Download complete: {channel_key}")
    else:
        print(f"\n⚠️  Download finished with warnings (some episodes may have failed)")

    # Count what we have
    audio_files = [f for f in out_dir.iterdir() if f.suffix in ('.mp3', '.webm', '.m4a', '.opus', '.ogg')]
    print(f"   Audio files in directory: {len(audio_files)}")
    return audio_files


def list_downloaded():
    """Show a summary of what's been downloaded."""
    print("\n📁 Downloaded audio:\n")
    total = 0
    for ch_key in CHANNELS:
        ch_dir = AUDIO_DIR / ch_key
        if ch_dir.exists():
            files = list(ch_dir.glob("*.mp3"))
            size_mb = sum(f.stat().st_size for f in files) / 1_000_000
            print(f"  {ch_key:30s} {len(files):4d} files  ({size_mb:.0f} MB)")
            total += len(files)
    print(f"\n  Total: {total} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kryptovox audio downloader")
    parser.add_argument("channel",  nargs="?", help="Channel key (or 'all' or 'list')")
    parser.add_argument("--limit",  type=int,  help="Max episodes per channel")
    parser.add_argument("--list",   action="store_true", help="Show downloaded files")
    args = parser.parse_args()

    if args.list or args.channel == "list":
        list_downloaded()
    elif args.channel == "all":
        for key in sorted(CHANNELS, key=lambda k: CHANNELS[k]["priority"]):
            download_channel(key, limit=args.limit)
    elif args.channel:
        download_channel(args.channel, limit=args.limit)
    else:
        parser.print_help()
        print("\nAvailable channels:")
        for k, v in CHANNELS.items():
            print(f"  {k:30s} {v['subject']}")
