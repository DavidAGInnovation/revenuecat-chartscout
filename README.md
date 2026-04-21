# ChartScout

ChartScout is a small command-line tool that turns RevenueCat Charts API data into a founder-facing subscription health report.

It pulls overview metrics plus selected chart time series, handles the Charts API response shape, paces requests for the rate limit, and writes three local artifacts:

- `*-chartscout-report.html`: a shareable report with KPI cards, trend charts, and agent-generated insights.
- `*-chartscout-report.md`: a Markdown version for weekly updates, investor notes, or Slack.
- `*-chartscout-data.json`: the raw API payload for follow-up analysis.

## Why it exists

Subscription app founders often know RevenueCat has the answer, but still need a fast way to ask repeatable questions:

- Is MRR moving differently than last-28-day revenue?
- Are new customers rising while active subscriptions are flat?
- Did churn or refund rate change enough to investigate?
- Can I share a trend report without exposing exact revenue numbers?

ChartScout gives them a local report generator that can be run by a human, a cron job, or an AI agent.

## Quickstart

Run the demo with synthetic data:

```bash
python3 chartscout.py --demo --out-dir examples --privacy-mode indexed
open examples/demo-chartscout-report.html
```

Run it against a RevenueCat project:

```bash
cp .env.example .env
export REVENUECAT_API_KEY=sk_your_read_only_charts_key

python3 chartscout.py \
  --project-id proj_your_project_id \
  --project-name "My App" \
  --start-date 2026-03-24 \
  --end-date 2026-04-20 \
  --out-dir reports
```

The default chart list is:

```text
revenue,mrr,actives,churn,refund_rate,customers_new
```

You can override it:

```bash
python3 chartscout.py \
  --project-id proj_your_project_id \
  --charts revenue,mrr,conversion_to_paying,ltv_per_customer \
  --out-dir reports
```

## Privacy modes

`--privacy-mode exact` shows raw values. Use it for private founder reports.

`--privacy-mode indexed` hides exact KPI values and normalizes each chart line to an index value starting at 100. Use it when you want to publish trend shape without exposing private business metrics.

## API behavior

ChartScout uses RevenueCat API v2:

- `GET /projects/{project_id}/metrics/overview`
- `GET /projects/{project_id}/charts/{chart_name}`

It sends `realtime=false` so it requests the v2 chart path, and it sleeps between chart requests because the Charts & Metrics domain is rate-limited. Responses are cached in `.chartscout-cache/` unless `--force-refresh` is passed.

The code also handles multi-column charts. For example, RevenueCat's churn chart can return support columns like active subscriptions and churned subscriptions before the actual churn rate. ChartScout selects the first segment marked `chartable: true` so the report follows the same primary measure the dashboard would chart.

## Public demo

The checked-in demo report is generated from synthetic data:

- [examples/demo-chartscout-report.html](examples/demo-chartscout-report.html)
- [examples/demo-chartscout-report.md](examples/demo-chartscout-report.md)

The real assignment dataset was used for private validation, but exact third-party subscription metrics are intentionally not committed.

## Deliverables

The assignment package lives in `docs/`:

- [Launch blog post](docs/launch-blog.md)
- [Video script](docs/video-script.md)
- [Social media posts](docs/social-posts.md)
- [Growth campaign report](docs/campaign-report.md)
- [Process log](docs/process-log.md)
- [Single submission document](docs/submission-document.md)

## License

MIT
