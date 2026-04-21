#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSETS="$ROOT/docs/assets"
OUT="$ASSETS/social"
BUILD="$ASSETS/social-build"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

mkdir -p "$OUT" "$BUILD"

python3 - "$BUILD" <<'PY'
from pathlib import Path
import html
import sys

build = Path(sys.argv[1])
cards = [
    (
        "post1-problem",
        "Problem / solution",
        "RevenueCat Charts API -> founder health report",
        "MRR, revenue, actives, churn, refunds, and new customers in one local report.",
    ),
    (
        "post2-parser",
        "Technical detail",
        "Do not assume chart value column 1",
        "ChartScout reads segment metadata and selects the first chartable measure.",
    ),
    (
        "post3-agent-workflow",
        "Agent workflow",
        "API -> cache -> trends -> founder report",
        "A starter pattern for subscription-aware AI agents.",
    ),
    (
        "post4-privacy",
        "Privacy mode",
        "Share trend shape without exact revenue",
        "Indexed mode normalizes chart lines to 100 and hides raw KPI values.",
    ),
    (
        "post5-feedback",
        "Feedback request",
        "What should a weekly subscription report flag first?",
        "MRR divergence, churn movement, refund spikes, trial pool changes, or something else?",
    ),
]

for slug, eyebrow, title, body in cards:
    (build / f"{slug}.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    width: 1600px;
    height: 900px;
    color: #172026;
    background: #f7f9fb;
    font-family: Arial, Helvetica, sans-serif;
  }}
  .bar {{ position: absolute; inset: 0 auto 0 0; width: 28px; background: #006c67; }}
  main {{ position: absolute; inset: 0; padding: 88px 112px 78px 132px; display: grid; align-content: space-between; }}
  .eyebrow {{ color: #006c67; font-size: 34px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }}
  h1 {{ margin: 34px 0 0; max-width: 1220px; font-size: 92px; line-height: 1.02; letter-spacing: 0; }}
  p {{ max-width: 1050px; margin: 32px 0 0; color: #44525c; font-size: 42px; line-height: 1.25; }}
  footer {{ display: flex; justify-content: space-between; color: #63707a; font-size: 30px; font-weight: 700; }}
  .chart {{ position: absolute; right: 108px; bottom: 130px; width: 420px; height: 120px; color: #006c67; }}
</style>
</head>
<body>
<div class="bar"></div>
<main>
  <section>
    <div class="eyebrow">{html.escape(eyebrow)}</div>
    <h1>{html.escape(title)}</h1>
    <p>{html.escape(body)}</p>
  </section>
  <footer><span>ChartScout</span><span>AI agent + Aster</span></footer>
</main>
<svg class="chart" viewBox="0 0 420 120" aria-hidden="true">
  <polyline points="8,94 68,82 128,88 188,56 248,64 308,38 368,28 412,18" fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
</body>
</html>
""")
PY

for html_file in "$BUILD"/*.html; do
  slug="$(basename "$html_file" .html)"
  "$CHROME" --headless --disable-gpu --hide-scrollbars --window-size=1600,900 --screenshot="$OUT/$slug.png" "file://$html_file" >/dev/null 2>&1
done

echo "Wrote social assets to $OUT"
