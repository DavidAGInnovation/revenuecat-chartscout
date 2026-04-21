#!/usr/bin/env python3
"""Generate founder-facing health reports from RevenueCat Charts API data."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import math
import os
import random
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.revenuecat.com/v2"
DEFAULT_CHARTS = ["revenue", "mrr", "actives", "churn", "refund_rate", "customers_new"]
DEFAULT_DELAY_SECONDS = 4.2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pull RevenueCat Charts API data and generate HTML/Markdown health reports."
    )
    parser.add_argument("--project-id", help="RevenueCat project id, for example proj058a6330.")
    parser.add_argument("--project-name", help="Human-readable project name for report titles.")
    parser.add_argument(
        "--api-key-env",
        default="REVENUECAT_API_KEY",
        help="Environment variable containing a RevenueCat API v2 bearer token.",
    )
    parser.add_argument("--currency", default="USD", help="Revenue currency, default USD.")
    parser.add_argument("--start-date", help="ISO date. Defaults to 28 days before end-date.")
    parser.add_argument("--end-date", help="ISO date. Defaults to yesterday in UTC.")
    parser.add_argument(
        "--charts",
        default=",".join(DEFAULT_CHARTS),
        help=f"Comma-separated chart names. Default: {','.join(DEFAULT_CHARTS)}",
    )
    parser.add_argument(
        "--resolution",
        default="0",
        help="Charts API resolution id. Use chart options to discover valid ids; 0 is day.",
    )
    parser.add_argument(
        "--privacy-mode",
        choices=["exact", "indexed"],
        default="exact",
        help="exact shows raw values; indexed normalizes charts to 100 for shareable reports.",
    )
    parser.add_argument("--out-dir", default="reports", help="Output directory.")
    parser.add_argument("--cache-dir", default=".chartscout-cache", help="HTTP cache directory.")
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help="Delay between Charts API calls. Default stays under the 15 rpm rate limit.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Ignore cached API responses and request fresh data.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use deterministic synthetic data instead of the RevenueCat API.",
    )
    return parser.parse_args()


def utc_yesterday() -> dt.date:
    return dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)


def parse_date(value: str | None, default: dt.date) -> dt.date:
    if value is None:
        return default
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid date '{value}'. Use YYYY-MM-DD.") from exc


def ensure_inputs(args: argparse.Namespace) -> tuple[str, str | None, dt.date, dt.date, list[str]]:
    end_date = parse_date(args.end_date, utc_yesterday())
    start_date = parse_date(args.start_date, end_date - dt.timedelta(days=27))
    if start_date > end_date:
        raise SystemExit("--start-date must be on or before --end-date.")

    charts = [chart.strip() for chart in args.charts.split(",") if chart.strip()]
    if not charts:
        raise SystemExit("--charts must include at least one chart name.")

    if args.demo:
        return "demo_project", None, start_date, end_date, charts

    if not args.project_id:
        raise SystemExit("--project-id is required unless --demo is used.")
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Set {args.api_key_env} before running, or use --demo.")
    return args.project_id, api_key, start_date, end_date, charts


def cache_key(path: str, params: dict[str, str]) -> str:
    encoded = urllib.parse.urlencode(sorted(params.items()))
    return hashlib.sha256(f"{path}?{encoded}".encode()).hexdigest()[:24]


def api_get(
    path: str,
    api_key: str,
    params: dict[str, str],
    cache_dir: Path,
    force_refresh: bool,
) -> dict[str, Any]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = cache_key(path, params)
    cache_file = cache_dir / f"{key}.json"
    if cache_file.exists() and not force_refresh:
        return json.loads(cache_file.read_text())

    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}" if params else f"{API_BASE}{path}"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise SystemExit(f"RevenueCat API returned HTTP {exc.code} for {path}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach RevenueCat API: {exc.reason}") from exc

    cache_file.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def fetch_dataset(args: argparse.Namespace, project_id: str, api_key: str | None, start: dt.date, end: dt.date, charts: list[str]) -> dict[str, Any]:
    if args.demo:
        return demo_dataset(start, end, charts)

    assert api_key is not None
    cache_dir = Path(args.cache_dir)
    overview = api_get(
        f"/projects/{project_id}/metrics/overview",
        api_key,
        {"currency": args.currency},
        cache_dir,
        args.force_refresh,
    )
    chart_payloads: dict[str, Any] = {}
    for index, chart_name in enumerate(charts):
        if index:
            time.sleep(max(args.delay_seconds, 0))
        chart_payloads[chart_name] = api_get(
            f"/projects/{project_id}/charts/{chart_name}",
            api_key,
            {
                "realtime": "false",
                "currency": args.currency,
                "resolution": args.resolution,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
            cache_dir,
            args.force_refresh,
        )

    return {
        "project": {"id": project_id, "name": project_id},
        "overview": overview,
        "charts": chart_payloads,
        "range": {"start_date": start.isoformat(), "end_date": end.isoformat()},
        "currency": args.currency,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def demo_dataset(start: dt.date, end: dt.date, charts: list[str]) -> dict[str, Any]:
    random.seed(42)
    days = (end - start).days + 1
    overview = {
        "object": "overview_metrics",
        "metrics": [
            metric("active_trials", "Active Trials", "#", 142, "In total"),
            metric("active_subscriptions", "Active Subscriptions", "#", 3180, "In total"),
            metric("mrr", "MRR", "$", 18420, "Monthly Recurring Revenue"),
            metric("revenue", "Revenue", "$", 20570, "Last 28 days"),
            metric("new_customers", "New Customers", "#", 1920, "Last 28 days"),
            metric("active_users", "Active Users", "#", 42100, "Last 28 days"),
            metric("num_tx_last_28_days", "Transactions", "#", 980, "Last 28 days"),
        ],
    }
    chart_payloads: dict[str, Any] = {}
    for chart_name in charts:
        chart_payloads[chart_name] = demo_chart(chart_name, start, days)
    return {
        "project": {"id": "demo_project", "name": "Demo Subscription App"},
        "overview": overview,
        "charts": chart_payloads,
        "range": {"start_date": start.isoformat(), "end_date": end.isoformat()},
        "currency": "USD",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def metric(metric_id: str, name: str, unit: str, value: float, description: str) -> dict[str, Any]:
    return {
        "object": "overview_metric",
        "id": metric_id,
        "name": name,
        "unit": unit,
        "value": value,
        "period": "P28D",
        "description": description,
        "last_updated_at": None,
        "last_updated_at_iso8601": None,
    }


def demo_chart(chart_name: str, start: dt.date, days: int) -> dict[str, Any]:
    display_names = {
        "revenue": ("Revenue", "$"),
        "mrr": ("MRR", "$"),
        "actives": ("Active subscriptions", "#"),
        "churn": ("Churn", "%"),
        "refund_rate": ("Refund rate", "%"),
        "customers_new": ("New customers", "#"),
    }
    display, unit = display_names.get(chart_name, (chart_name.replace("_", " ").title(), "#"))
    values = []
    base = {
        "revenue": 620,
        "mrr": 18200,
        "actives": 3120,
        "churn": 2.4,
        "refund_rate": 0.7,
        "customers_new": 64,
    }.get(chart_name, 100)
    for offset in range(days):
        date = start + dt.timedelta(days=offset)
        trend = 1 + offset * 0.006
        wave = math.sin(offset / 3) * 0.06
        noise = random.uniform(-0.035, 0.035)
        value = max(base * (trend + wave + noise), 0)
        if chart_name in {"churn", "refund_rate"}:
            value = max(base + math.sin(offset / 4) * 0.35 + random.uniform(-0.12, 0.12), 0)
        values.append([int(dt.datetime.combine(date, dt.time(), dt.timezone.utc).timestamp()), round(value, 2)])

    total = round(sum(row[1] for row in values), 2)
    avg = round(total / len(values), 2) if values else 0
    return {
        "object": "chart_data",
        "category": "demo",
        "display_type": "line",
        "display_name": display,
        "description": f"Synthetic {display.lower()} data for local demos.",
        "start_date": values[0][0] if values else 0,
        "end_date": values[-1][0] if values else 0,
        "yaxis_currency": "USD" if unit == "$" else None,
        "resolution": "day",
        "values": values,
        "summary": {"average": {display: avg}, "total": {display: total}},
        "yaxis": unit,
        "segments": [{"display_name": display, "unit": unit, "decimal_precision": 2}],
    }


def analyze(dataset: dict[str, Any], privacy_mode: str) -> dict[str, Any]:
    overview_metrics = {item["id"]: item for item in dataset["overview"].get("metrics", [])}
    chart_cards = [analyze_chart(name, payload, privacy_mode) for name, payload in dataset["charts"].items()]
    chart_cards = [card for card in chart_cards if card["points"]]
    insights = build_insights(overview_metrics, chart_cards, privacy_mode)
    return {"overview": overview_metrics, "charts": chart_cards, "insights": insights}


def analyze_chart(chart_name: str, payload: dict[str, Any], privacy_mode: str) -> dict[str, Any]:
    raw_points = payload.get("values") or []
    segment = primary_segment(payload)
    value_index = int(segment.get("_value_index", 1))
    series = []
    for row in raw_points:
        if not isinstance(row, list) or len(row) <= value_index:
            continue
        timestamp = row[0]
        value = row[value_index]
        if not isinstance(timestamp, (int, float)) or not isinstance(value, (int, float)):
            continue
        date = dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).date().isoformat()
        series.append({"date": date, "value": float(value)})

    display_name = segment.get("display_name") or payload.get("display_name") or chart_name.replace("_", " ").title()
    unit = segment.get("unit") or payload.get("yaxis") or ""
    chart_values = [point["value"] for point in series]
    normalized = normalize(chart_values) if privacy_mode == "indexed" else chart_values
    latest = chart_values[-1] if chart_values else 0
    previous = chart_values[-2] if len(chart_values) > 1 else latest
    first_half, second_half = split_halves(chart_values)
    trend = pct_change(mean(first_half), mean(second_half))
    latest_change = pct_change(previous, latest)
    summary = payload.get("summary") or {}

    return {
        "name": chart_name,
        "display_name": display_name,
        "description": segment.get("description") or payload.get("description") or "",
        "unit": unit,
        "points": series,
        "render_values": normalized,
        "latest": latest,
        "latest_change": latest_change,
        "period_total": summary_value(summary, "total", display_name, sum(chart_values)),
        "period_average": summary_value(summary, "average", display_name, mean(chart_values)),
        "period_trend": trend,
        "sparkline": sparkline(normalized),
    }


def primary_segment(payload: dict[str, Any]) -> dict[str, Any]:
    segments = payload.get("segments") or []
    if not segments:
        return {}
    for index, segment in enumerate(segments, start=1):
        if isinstance(segment, dict) and segment.get("chartable") is True:
            selected = dict(segment)
            selected["_value_index"] = index
            return selected
    if isinstance(segments[0], dict):
        selected = dict(segments[0])
        selected["_value_index"] = 1
        return selected
    return {}


def summary_value(summary: dict[str, Any], key: str, display_name: str, fallback: float) -> float:
    bucket = summary.get(key) if isinstance(summary, dict) else None
    if isinstance(bucket, dict):
        if display_name in bucket and isinstance(bucket[display_name], (int, float)):
            return float(bucket[display_name])
        for value in bucket.values():
            if isinstance(value, (int, float)):
                return float(value)
    return float(fallback or 0)


def split_halves(values: list[float]) -> tuple[list[float], list[float]]:
    if len(values) < 2:
        return values, values
    midpoint = len(values) // 2
    return values[:midpoint], values[midpoint:]


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0


def pct_change(old: float, new: float) -> float | None:
    if old == 0:
        return None
    return ((new - old) / abs(old)) * 100


def normalize(values: list[float]) -> list[float]:
    baseline = next((value for value in values if value != 0), 1)
    return [round((value / baseline) * 100, 2) for value in values]


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    ticks = ".:-=+*#"
    low = min(values)
    high = max(values)
    if high == low:
        return ticks[3] * len(values)
    return "".join(ticks[min(int((value - low) / (high - low) * (len(ticks) - 1)), len(ticks) - 1)] for value in values)


def build_insights(overview: dict[str, dict[str, Any]], charts: list[dict[str, Any]], privacy_mode: str) -> list[str]:
    by_name = {chart["name"]: chart for chart in charts}
    insights: list[str] = []
    revenue = overview.get("revenue", {}).get("value")
    mrr = overview.get("mrr", {}).get("value")
    active_subs = overview.get("active_subscriptions", {}).get("value")
    active_trials = overview.get("active_trials", {}).get("value")
    transactions = overview.get("num_tx_last_28_days", {}).get("value")

    if privacy_mode == "exact" and revenue and transactions:
        insights.append(f"Average realized revenue per transaction over the last 28 days is {money(revenue / transactions)}.")
    if privacy_mode == "exact" and mrr and revenue:
        ratio = revenue / mrr
        insights.append(f"Last-28-day revenue is {ratio:.2f}x current MRR, a quick check for seasonality or one-time purchase lift.")
    if privacy_mode == "exact" and active_trials and active_subs:
        insights.append(f"Active trials are {active_trials / active_subs * 100:.1f}% of active subscriptions, useful for near-term renewal planning.")

    for key in ["revenue", "mrr", "actives", "customers_new"]:
        chart = by_name.get(key)
        if chart and chart["period_trend"] is not None:
            direction = "up" if chart["period_trend"] >= 0 else "down"
            insights.append(f"{chart['display_name']} is {direction} {abs(chart['period_trend']):.1f}% in the back half of the period versus the front half.")

    for key in ["churn", "refund_rate"]:
        chart = by_name.get(key)
        if chart and chart["latest_change"] is not None:
            direction = "improved" if chart["latest_change"] < 0 else "worsened"
            insights.append(f"{chart['display_name']} {direction} {abs(chart['latest_change']):.1f}% versus the prior data point.")

    if not insights:
        insights.append("Not enough trend data was returned for automated insights; widen the date range or add more chart names.")
    return insights[:6]


def money(value: float) -> str:
    return f"${value:,.2f}"


def format_value(value: float, unit: str, privacy_mode: str) -> str:
    if privacy_mode == "indexed":
        return f"{value:,.1f} index"
    if unit == "$":
        return money(value)
    if unit == "%":
        return f"{value:,.2f}%"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def format_delta(value: float | None) -> str:
    if value is None:
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def render_svg(values: list[float], title: str) -> str:
    if not values:
        return ""
    width, height, pad = 520, 160, 14
    low, high = min(values), max(values)
    span = high - low or 1
    step = (width - pad * 2) / max(len(values) - 1, 1)
    points = []
    for index, value in enumerate(values):
        x = pad + index * step
        y = height - pad - ((value - low) / span) * (height - pad * 2)
        points.append(f"{x:.1f},{y:.1f}")
    escaped_title = html.escape(title)
    return (
        f'<svg role="img" aria-label="{escaped_title}" viewBox="0 0 {width} {height}" class="chart">'
        f'<polyline fill="none" stroke="currentColor" stroke-width="3" points="{" ".join(points)}" />'
        f'<line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" />'
        "</svg>"
    )


def render_html(dataset: dict[str, Any], analysis: dict[str, Any], privacy_mode: str) -> str:
    project = dataset["project"]["name"]
    date_range = dataset["range"]
    cards = []
    for metric_id in ["mrr", "revenue", "active_subscriptions", "active_trials", "new_customers", "active_users"]:
        metric_payload = analysis["overview"].get(metric_id)
        if not metric_payload:
            continue
        value = "Private" if privacy_mode == "indexed" else format_value(metric_payload["value"], metric_payload.get("unit", ""), "exact")
        cards.append(
            f'<article class="kpi"><span>{html.escape(metric_payload["name"])}</span>'
            f"<strong>{html.escape(value)}</strong><small>{html.escape(metric_payload.get('description') or '')}</small></article>"
        )

    chart_sections = []
    for chart in analysis["charts"]:
        latest_value = chart["render_values"][-1] if privacy_mode == "indexed" else chart["latest"]
        chart_sections.append(
            f'<section class="panel"><div><p class="eyebrow">{html.escape(chart["name"])}</p>'
            f'<h2>{html.escape(chart["display_name"])}</h2>'
            f'<p class="metric">{html.escape(format_value(latest_value, chart["unit"], privacy_mode))}</p>'
            f'<p class="muted">Latest change: {html.escape(format_delta(chart["latest_change"]))} - Period trend: {html.escape(format_delta(chart["period_trend"]))}</p>'
            f"</div>{render_svg(chart['render_values'], chart['display_name'])}</section>"
        )

    insights = "".join(f"<li>{html.escape(item)}</li>" for item in analysis["insights"])
    privacy_note = (
        "This report is in indexed privacy mode. Exact values are hidden; chart lines are normalized to the first non-zero data point."
        if privacy_mode == "indexed"
        else "This report shows exact values from the configured RevenueCat project."
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ChartScout report for {html.escape(project)}</title>
  <style>
    :root {{ color-scheme: light; --ink:#172026; --muted:#63707a; --line:#d9e1e7; --accent:#006c67; --paper:#f7f9fb; --card:#ffffff; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font: 16px/1.5 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--paper); color: var(--ink); }}
    main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 42px 0 56px; }}
    header {{ display: grid; grid-template-columns: 1fr auto; gap: 24px; align-items: end; padding-bottom: 28px; border-bottom: 1px solid var(--line); }}
    h1 {{ margin: 0; font-size: clamp(2rem, 5vw, 4.5rem); line-height: .95; letter-spacing: 0; max-width: 760px; }}
    h2 {{ margin: 2px 0 8px; font-size: 1.4rem; letter-spacing: 0; }}
    .eyebrow {{ margin: 0; color: var(--accent); text-transform: uppercase; font-size: .75rem; font-weight: 800; letter-spacing: .08em; }}
    .muted, small {{ color: var(--muted); }}
    .range {{ text-align: right; color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 22px 0; }}
    .kpi, .panel, .insights {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; box-shadow: 0 1px 2px rgba(20, 32, 40, .04); }}
    .kpi {{ padding: 16px; min-height: 132px; display: flex; flex-direction: column; justify-content: space-between; }}
    .kpi span {{ color: var(--muted); font-weight: 700; }}
    .kpi strong {{ display: block; font-size: 2rem; letter-spacing: 0; }}
    .panel {{ margin: 12px 0; padding: 18px; display: grid; grid-template-columns: minmax(210px, .7fr) minmax(280px, 1.3fr); gap: 20px; align-items: center; }}
    .metric {{ margin: 0; font-size: 2rem; font-weight: 800; }}
    .chart {{ width: 100%; min-height: 150px; color: var(--accent); }}
    .chart line {{ stroke: var(--line); stroke-width: 1; }}
    .insights {{ padding: 18px 22px; margin: 24px 0; }}
    .insights li {{ margin: 8px 0; }}
    footer {{ margin-top: 28px; color: var(--muted); font-size: .92rem; }}
    @media (max-width: 760px) {{ header, .panel {{ grid-template-columns: 1fr; }} .grid {{ grid-template-columns: 1fr; }} .range {{ text-align: left; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <p class="eyebrow">RevenueCat Charts API health report</p>
        <h1>{html.escape(project)}</h1>
      </div>
      <p class="range">{html.escape(date_range["start_date"])} to {html.escape(date_range["end_date"])}</p>
    </header>
    <section class="grid">{''.join(cards)}</section>
    <section class="insights"><p class="eyebrow">Agent-generated readout</p><ul>{insights}</ul></section>
    {''.join(chart_sections)}
    <footer>{html.escape(privacy_note)} Generated by ChartScout at {html.escape(dataset["generated_at"])}.</footer>
  </main>
</body>
</html>
"""


def render_markdown(dataset: dict[str, Any], analysis: dict[str, Any], privacy_mode: str) -> str:
    project = dataset["project"]["name"]
    date_range = dataset["range"]
    lines = [
        f"# ChartScout report for {project}",
        "",
        f"Range: {date_range['start_date']} to {date_range['end_date']}",
        f"Privacy mode: {privacy_mode}",
        "",
        "## KPI Snapshot",
        "",
        "| Metric | Value | Context |",
        "| --- | ---: | --- |",
    ]
    for metric in analysis["overview"].values():
        value = "Private" if privacy_mode == "indexed" else format_value(metric["value"], metric.get("unit", ""), "exact")
        lines.append(f"| {metric['name']} | {value} | {metric.get('description') or ''} |")

    lines.extend(["", "## Insights", ""])
    for item in analysis["insights"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Chart Trends", "", "| Chart | Latest | Latest Change | Period Trend | Sparkline |", "| --- | ---: | ---: | ---: | --- |"])
    for chart in analysis["charts"]:
        latest_value = chart["render_values"][-1] if privacy_mode == "indexed" else chart["latest"]
        lines.append(
            f"| {chart['display_name']} | {format_value(latest_value, chart['unit'], privacy_mode)} | "
            f"{format_delta(chart['latest_change'])} | {format_delta(chart['period_trend'])} | {chart['sparkline']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project_id, api_key, start, end, charts = ensure_inputs(args)
    dataset = fetch_dataset(args, project_id, api_key, start, end, charts)
    if args.demo:
        dataset["project"]["name"] = "Demo Subscription App"
    elif dataset["project"]["name"] == project_id:
        dataset["project"]["name"] = args.project_name or project_id

    report = analyze(dataset, args.privacy_mode)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = "demo" if args.demo else project_id
    html_path = out_dir / f"{slug}-chartscout-report.html"
    md_path = out_dir / f"{slug}-chartscout-report.md"
    json_path = out_dir / f"{slug}-chartscout-data.json"
    html_path.write_text(render_html(dataset, report, args.privacy_mode))
    md_path.write_text(render_markdown(dataset, report, args.privacy_mode))
    json_path.write_text(json.dumps(dataset, indent=2, sort_keys=True))

    print(f"Wrote {html_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
