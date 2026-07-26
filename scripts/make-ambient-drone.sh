#!/usr/bin/env bash
# Synthesizes a subtle ambient bass drone (two detuned low sines + filtered
# brown noise texture + slow tremolo) entirely locally via ffmpeg lavfi —
# no external sample libraries needed.
set -euo pipefail
cd "$(dirname "$0")/.."

DURATION="${1:-246}"
OUT="public/audio/ambient_drone.wav"

ffmpeg -y \
  -f lavfi -i "sine=frequency=55:duration=${DURATION}" \
  -f lavfi -i "sine=frequency=55.4:duration=${DURATION}" \
  -f lavfi -i "sine=frequency=82.4:duration=${DURATION}" \
  -f lavfi -i "anoisesrc=color=brown:amplitude=1:duration=${DURATION}" \
  -filter_complex "\
[0]lowpass=f=180,volume=0.5[a]; \
[1]lowpass=f=180,volume=0.5[b]; \
[2]lowpass=f=260,volume=0.22[c]; \
[3]lowpass=f=140,volume=0.05[n]; \
[a][b]amix=inputs=2:weights=1 1[ab]; \
[ab][c]amix=inputs=2:weights=1 1[abc]; \
[abc][n]amix=inputs=2:weights=1 1[bed]; \
[bed]tremolo=f=0.12:d=0.25[trem]; \
[trem]volume=0.55[out]" \
  -map "[out]" -ac 2 -ar 44100 "$OUT"

echo "Wrote $OUT"
