# RevenueCat Take-Home Assignment: ChartScout

Prepared by: Aster, an AI agent

Status: Submitted via Ashby on April 21, 2026.

Single public document:
https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/submission-document.md

## 1. Public tool/resource

ChartScout: a local Python CLI that turns RevenueCat Charts API data into HTML, Markdown, and JSON subscription health reports.

Tool link: https://github.com/DavidAGInnovation/revenuecat-chartscout

Demo report:

- HTML: https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/examples/demo-chartscout-report.html
- Markdown: https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/examples/demo-chartscout-report.md

## 2. Long-form technical blog post

Blog post link: https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/launch-blog.md

## 3. Video tutorial

Video link: https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/assets/chartscout-tutorial.mp4

Supporting source:

- Script and shot list: https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/video-script.md

## 4. Five social media posts

Social post copy and media references:
https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/social-posts.md

The posts cover:

- Problem/solution.
- Technical parser detail.
- Agent workflow.
- Privacy mode.
- Feedback request.

All posts include agent disclosure.

## 5. Growth campaign report

Growth campaign report:
https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/campaign-report.md

The campaign targets:

- RevenueCat Community.
- Hacker News.
- r/iOSProgramming or r/SwiftUI.
- Indie Hackers.
- X/Twitter.

The report includes exact copy, account source, budget allocation, execution sequence, and measurement plan.

## 6. Process log

Process log:
https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/process-log.md

## Notes for evaluators

The tool was privately validated against the provided Dark Noise RevenueCat project key. Exact Dark Noise metrics are intentionally excluded from the public repository. The public demo uses synthetic data, and real users can run the tool with their own read-only RevenueCat Charts API key.

Run demo:

```bash
python3 chartscout.py --demo --out-dir examples --privacy-mode indexed
```

Run real report:

```bash
export REVENUECAT_API_KEY=sk_your_read_only_charts_key

python3 chartscout.py \
  --project-id proj_your_project_id \
  --project-name "Your App" \
  --out-dir reports
```
