#!/usr/bin/env bash
#
# Squeeze a hero clip down to something a phone on Tanzanian mobile data can
# actually load, and pull a poster frame out of it.
#
#   ./scripts/optimize_media.sh path/to/raw-footage.mp4 [seconds] [start]
#
#   seconds  length of the loop to keep      (default 14)
#   start    where in the source to cut from (default 3)
#
# Writes three files next to this script's output directory:
#   hero.mp4         the clip, for desktop
#   hero-small.mp4   a narrower cut, if you ever want a mobile source
#   hero-poster.jpg  the still, which is what most visitors will ever see
#
# Upload hero.mp4 as the slide's video and hero-poster.jpg as its image in the
# admin. The site shows the poster immediately and only fetches the clip on a
# wide screen with a connection that can carry it (see main.js).
#
# Why this matters: the file this project shipped with was 18 MB — four
# minutes long, with an audio track that never plays because the hero is
# muted. The same footage cut to 14 seconds with the audio stripped is about
# 1.2 MB. That is the difference between a hero that appears and a hero the
# visitor leaves before seeing.
#
# Needs ffmpeg:  sudo apt install ffmpeg   (or: brew install ffmpeg)

set -euo pipefail

SRC="${1:-}"
LEN="${2:-14}"
START="${3:-3}"
OUT="${OUT_DIR:-./media-optimised}"

if [[ -z "$SRC" || ! -f "$SRC" ]]; then
  echo "usage: $0 <source-video> [seconds] [start-seconds]" >&2
  exit 1
fi

command -v ffmpeg >/dev/null || { echo "ffmpeg is not installed." >&2; exit 1; }

mkdir -p "$OUT"

echo "Source: $SRC"
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height \
        -of default=noprint_wrappers=1 "$SRC" || true

# -an           drop audio: the hero is muted, so it is pure weight
# -movflags     +faststart puts the index at the front so playback can begin
#               before the whole file has arrived
# -crf 28       visually fine for a backdrop sitting behind a dark overlay
echo
echo "-> $OUT/hero.mp4"
ffmpeg -y -v error -ss "$START" -i "$SRC" -t "$LEN" -an \
  -vf "fps=25" \
  -c:v libx264 -profile:v main -crf 28 -preset slow -pix_fmt yuv420p \
  -movflags +faststart "$OUT/hero.mp4"

echo "-> $OUT/hero-small.mp4"
ffmpeg -y -v error -ss "$START" -i "$SRC" -t "$LEN" -an \
  -vf "scale=640:-2,fps=25" \
  -c:v libx264 -crf 30 -preset slow -pix_fmt yuv420p \
  -movflags +faststart "$OUT/hero-small.mp4"

echo "-> $OUT/hero-poster.jpg"
ffmpeg -y -v error -ss "$((START + 2))" -i "$SRC" -frames:v 1 -q:v 4 \
  "$OUT/hero-poster.jpg"

echo
echo "Done:"
ls -lh "$OUT"
echo
echo "Anything over ~2 MB for the clip, cut it shorter or raise -crf."
