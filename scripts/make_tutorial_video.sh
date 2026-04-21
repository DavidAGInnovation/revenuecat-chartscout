#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSETS="$ROOT/docs/assets"
SLIDES="$ASSETS/slides"
BUILD="$ASSETS/video-build"
OUT="$ASSETS/chartscout-tutorial.mp4"
VOICE="$BUILD/voice.aiff"
CONCAT="$BUILD/concat.txt"
FONT="/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

mkdir -p "$BUILD"
rm -f "$BUILD"/slide*.mp4 "$CONCAT" "$OUT"

say -v Samantha -r 178 -f "$ROOT/docs/video-voiceover.txt" -o "$VOICE"

for i in 1 2 3 4 5 6 7; do
  python3 - "$SLIDES/slide${i}.txt" "$BUILD/slide${i}.html" <<'PY'
import html
import sys
source, target = sys.argv[1], sys.argv[2]
text = open(source).read()
open(target, "w").write(f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<style>
  body {{ margin:0; width:1280px; height:720px; background:#f7f9fb; color:#172026; font-family: Arial, sans-serif; }}
  .bar {{ position:absolute; inset:0 auto 0 0; width:22px; background:#006c67; }}
  main {{ padding:76px 90px; white-space:pre-wrap; font-weight:700; font-size:44px; line-height:1.28; }}
  footer {{ position:absolute; left:90px; bottom:48px; color:#63707a; font-size:22px; }}
</style>
</head>
<body>
<div class='bar'></div>
<main>{html.escape(text)}</main>
<footer>ChartScout tutorial</footer>
</body>
</html>""")
PY
  "$CHROME" --headless --disable-gpu --hide-scrollbars --window-size=1280,720 --screenshot="$BUILD/slide${i}.png" "file://$BUILD/slide${i}.html" >/dev/null 2>&1
  ffmpeg -y \
    -loop 1 -t 14 -i "$BUILD/slide${i}.png" \
    -vf "format=yuv420p" \
    -c:v libx264 -pix_fmt yuv420p -r 30 "$BUILD/slide${i}.mp4" >/dev/null 2>&1
  printf "file '%s'\n" "$BUILD/slide${i}.mp4" >> "$CONCAT"
done

ffmpeg -y \
  -f concat -safe 0 -i "$CONCAT" \
  -i "$VOICE" \
  -c:v copy -c:a aac -shortest "$OUT"

echo "Wrote $OUT"
