#!/bin/sh
# Run after installing FFmpeg, or provide FFMPEG=/absolute/path/to/ffmpeg.
# No crop, trimming, speed changes, generated content, or audio in web copies.
# Normalize the source track timestamp to zero and convert full to video range.
set -eu
cd "$(dirname "$0")/.."
SOURCE=${1:-assets-source/hero-original.mp4}
FFMPEG=${FFMPEG:-ffmpeg}
OUT=frontend/public/hero
if ! command -v "$FFMPEG" >/dev/null 2>&1; then
  echo 'FFmpeg is unavailable. Install it, then run scripts/prepare-hero-video.sh [source.mp4].' >&2
  exit 1
fi
[ -f "$SOURCE" ] || { echo "Missing source: $SOURCE" >&2; exit 1; }
mkdir -p "$OUT"
encode() {
  width=$1
  budget=$2
  target="$OUT/hero_scrub_${width}.mp4"
  for gop in 1 2; do
    for quality in 24 26 28 30 32; do
      "$FFMPEG" -hide_banner -loglevel error -y -i "$SOURCE" -map 0:v:0 -an \
        -vf "scale=$width:-2:out_range=tv,setpts=PTS-STARTPTS" -color_range tv -fps_mode passthrough -c:v libx264 -g "$gop" -crf "$quality" \
        -pix_fmt yuv420p -movflags +faststart "$target"
      bytes=$(wc -c < "$target" | tr -d ' ')
      if [ "$bytes" -lt "$budget" ]; then
        echo "$target: $bytes bytes, CRF $quality, GOP $gop"
        return
      fi
    done
  done
  echo "Budget exceeded for $target; choose a smaller encode before shipping." >&2
  exit 1
}
encode 1280 15000000
encode 854 8000000
"$FFMPEG" -hide_banner -loglevel error -y -ss 1 -i "$SOURCE" -an \
  -vf scale=1280:-2 -frames:v 1 -q:v 3 -update 1 "$OUT/hero_poster.jpg"
# Update the same JPEG through the tail, retaining the actual last decoded frame.
"$FFMPEG" -hide_banner -loglevel error -y -sseof -0.3 -i "$SOURCE" -an \
  -vf scale=1280:-2 -q:v 3 -update 1 "$OUT/hero_poster_final.jpg"
