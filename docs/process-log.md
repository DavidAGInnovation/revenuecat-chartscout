# Process log

Date: 2026-04-21

## 1. Read the assignment

I extracted the four-page PDF and identified six required deliverables:

- Public tool/resource.
- 1,500+ word technical launch post.
- 1-3 minute video tutorial.
- Five X/Twitter posts.
- Growth campaign report with at least three target communities, exact copy, account source, measurement plan, and $100 budget.
- Process log.

I also noted the instruction to disclose that I am an agent in campaign copy.

## 2. Researched RevenueCat Charts API

I used RevenueCat's public API v2 docs and changelog to confirm:

- Base API v2 URL: `https://api.revenuecat.com/v2`.
- Overview endpoint: `/projects/{project_id}/metrics/overview`.
- Chart endpoint: `/projects/{project_id}/charts/{chart_name}`.
- Chart options endpoint: `/projects/{project_id}/charts/{chart_name}/options`.
- Charts & Metrics rate limit behavior.
- `realtime=false` can request v2 chart behavior.
- Chart responses include metadata, values, summaries, and segment information.

I then tested the assignment key. The key could list the Dark Noise project and read overview metrics for project `proj058a6330`.

## 3. Chose the tool concept

I considered a hosted dashboard, a library wrapper, and a report generator. I chose a local CLI report generator because it better matches the role's mix of developer advocacy and growth:

- It is easy to inspect and trust.
- It keeps API keys local.
- It can be run by humans, CI, cron, or agents.
- It turns the Charts API into a concrete weekly founder workflow.
- It creates useful educational content around real API behavior.

The tool name is ChartScout.

## 4. Built the CLI

I implemented `chartscout.py` using Python standard library only. Key implementation choices:

- Environment-variable API key instead of CLI key argument in docs, to avoid encouraging secrets in shell history.
- HTTP cache directory to avoid repeated API calls during iteration.
- Default pacing between chart requests to stay under the Charts & Metrics rate limit.
- Demo mode with deterministic synthetic data so public readers can try the tool without credentials.
- HTML, Markdown, and JSON outputs.
- `exact` and `indexed` privacy modes.

## 5. Validated against real Charts API data

I ran the tool privately against Dark Noise using:

```bash
REVENUECAT_API_KEY='[redacted]' python3 chartscout.py \
  --project-id proj058a6330 \
  --project-name 'Dark Noise' \
  --out-dir private-reports \
  --privacy-mode exact \
  --start-date 2026-03-24 \
  --end-date 2026-04-20 \
  --charts revenue,mrr,actives,churn,refund_rate,customers_new
```

The first real run exposed an important chart parsing issue: churn and refund-rate responses include support columns before the primary charted metric. I patched the parser to use the first `segments` entry marked `chartable: true`.

I intentionally ignored `private-reports/` in git because exact third-party subscription metrics should not be committed to a public repository.

## 6. Created public demo output

I generated the public demo report with:

```bash
python3 chartscout.py --demo --out-dir examples --privacy-mode indexed
```

The demo output uses synthetic data and is safe to publish:

- `examples/demo-chartscout-report.html`
- `examples/demo-chartscout-report.md`
- `examples/demo-chartscout-data.json`

## 7. Wrote launch and growth assets

I wrote:

- `docs/launch-blog.md`: a long-form launch post with code snippets and Mermaid architecture diagram.
- `docs/social-posts.md`: five X/Twitter posts, each with agent disclosure.
- `docs/campaign-report.md`: communities, exact post copy, account source, $100 budget, execution sequence, and measurement plan.
- `docs/video-script.md`: tutorial voiceover and shot list.
- `docs/submission-document.md`: single public document that links all assignment deliverables.

## 8. Tradeoffs

Hosted web app vs local CLI:

I chose local CLI for trust, speed, and secret handling. A hosted version would be more visually impressive, but it would also create API-key storage and security questions that are unnecessary for the assignment.

Exact report vs public report:

I used the assignment key for private validation, but public assets use synthetic or indexed data. This demonstrates the API without exposing exact metrics from a third-party app.

No dependencies vs richer charts:

I used Python stdlib and inline SVG. That keeps the tool easy to audit. A later version could add richer charts or Slack output.

## 9. Tools used

- `pdftotext` to extract the assignment.
- `curl` and `jq` to inspect RevenueCat API responses.
- Python 3.14 to implement and validate the CLI.
- RevenueCat API v2 documentation and changelog.
- GitHub CLI for publishing readiness checks.

