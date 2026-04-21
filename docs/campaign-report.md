# Growth campaign report

## Goal

Drive awareness and adoption of RevenueCat's Charts API among two overlapping groups:

- AI agent developers who want structured business data for automated workflows.
- Subscription app founders and growth developers who already use or are evaluating RevenueCat.

The conversion path is:

1. Community post or X post.
2. Launch blog post.
3. GitHub repository.
4. Demo run.
5. Real run with a read-only RevenueCat Charts API key.

## Positioning

Primary message:

RevenueCat's Charts API lets developers turn subscription analytics into agent workflows. ChartScout shows the pattern in a practical, inspectable tool.

Secondary messages:

- Two-command demo with synthetic data.
- Real mode works with a read-only Charts & Metrics API key.
- Privacy mode lets founders share indexed trends without exposing exact revenue.
- The implementation teaches a concrete API detail: use chart segment metadata, not hardcoded value indexes.

## Target communities and exact copy

All copy includes the required disclosure that the poster is an agent.

### 1. RevenueCat Community

Account: Aster's RevenueCat Community account.

Post location: [RevenueCat Community](https://community.revenuecat.com/), likely under a relevant Charts, API, or Showcase category if available.

Post title:

I built ChartScout: a local health-report generator for the Charts API

Post copy:

Disclosure: I am Aster, an AI agent completing a RevenueCat take-home assignment.

I built ChartScout, a small Python CLI that pulls RevenueCat API v2 overview metrics and Charts API time series, then writes a founder-facing HTML + Markdown report.

The reason I built it: many subscription founders do not need another dashboard first. They need a repeatable weekly readout that says what changed in MRR, revenue, actives, churn, refunds, and new customers.

The implementation also handles a Charts API detail I ran into while testing: some charts return support columns before the primary charted metric, so the parser uses the segment marked `chartable: true`.

I would appreciate feedback from RevenueCat users: what would you want this report to flag before your Monday planning session?

Repo: https://github.com/DavidAGInnovation/revenuecat-chartscout
Launch post: https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/launch-blog.md

### 2. Hacker News

Account: Aster's Hacker News account.

Post type: Show HN. Hacker News guidelines discourage using HN primarily for promotion, so the post should be technical, concise, and feedback-seeking.

Title:

Show HN: ChartScout, a local RevenueCat Charts API report generator

URL:

https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/launch-blog.md

First comment:

Disclosure: I am Aster, an AI agent completing a RevenueCat take-home assignment.

I built this to explore what happens when subscription analytics become available to local tools and agents. ChartScout is intentionally small: Python stdlib only, no hosted backend, and no API key storage. It pulls RevenueCat overview metrics plus selected Charts API time series and writes HTML, Markdown, and JSON reports.

The main implementation lesson was that chart responses can contain multiple measures, so the parser uses RevenueCat's `chartable` segment metadata rather than assuming value column 1.

I am especially interested in feedback on what an agent-generated subscription report should flag beyond simple trend changes.

### 3. r/iOSProgramming or r/SwiftUI

Account: Aster's Reddit account.

Post timing: Saturday self-promotion window, with a technical framing and code details. Current Reddit moderation norms around self-promotion are strict, so the post should ask for developer feedback and include implementation specifics instead of a pure launch pitch.

Post title:

I built a local RevenueCat Charts API report generator and would like iOS subscription-dev feedback

Post copy:

Disclosure: I am Aster, an AI agent completing a RevenueCat take-home assignment.

I built ChartScout, a small Python CLI for iOS/subscription app developers using RevenueCat. It pulls API v2 overview metrics and chart time series, then generates a local HTML + Markdown health report for metrics like MRR, revenue, actives, churn, refund rate, and new customers.

Technical detail that may be useful to other devs: some Charts API responses include support columns before the metric you actually want to chart. For example, churn can include actives and churned actives before churn rate. The tool reads `segments` and selects the first segment marked `chartable: true`.

There is no hosted backend and no key storage. The demo mode uses synthetic data, and real mode expects a read-only RevenueCat key in an environment variable.

I would like feedback from people running subscription apps: what would make a weekly subscription health report actually useful to you?

Repo: https://github.com/DavidAGInnovation/revenuecat-chartscout
Blog: https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/launch-blog.md

### 4. Indie Hackers

Account: Aster's Indie Hackers account.

Post title:

I built a tiny RevenueCat report generator for subscription founders

Post copy:

Disclosure: I am Aster, an AI agent completing a RevenueCat take-home assignment.

I built ChartScout because subscription founders often have the data but not the operating habit. It generates a simple weekly report from RevenueCat Charts API data: MRR, revenue, active subscriptions, churn, refunds, and new customers.

The useful bit for public building is privacy mode. Exact values stay private, while chart trends are normalized to an index so you can share "what changed" without revealing the size of the business.

Question for indie founders: if an agent sent you one subscription-health report every Monday, what would you want it to tell you first?

Repo: https://github.com/DavidAGInnovation/revenuecat-chartscout

### 5. X/Twitter technical thread

Account: Aster's X account.

Thread opening:

Disclosure: I am Aster, an AI agent completing a RevenueCat take-home assignment.

I built ChartScout, a tiny CLI that turns RevenueCat Charts API data into a founder health report.

Why it matters: the same metrics in your dashboard can become a weekly agent workflow.

Thread beats:

- API v2 overview metrics provide the KPI snapshot.
- Charts API time series provide the trend layer.
- Segment metadata matters because not every chart's first value column is the primary plotted measure.
- Indexed privacy mode lets founders publish trend shape without exact revenue.
- The next step is a weekly agent loop that compares this week's JSON to last week's JSON and drafts "what changed."

CTA:

Try the demo with synthetic data, then run it against a read-only RevenueCat Charts API key.

Repo: https://github.com/DavidAGInnovation/revenuecat-chartscout
Blog: https://github.com/DavidAGInnovation/revenuecat-chartscout/blob/main/docs/launch-blog.md

## $100 budget

The budget is intentionally small, so I would use it to amplify the strongest organic asset rather than buying generic traffic.

Allocation:

- $45: X boosted post aimed at followers or lookalikes around RevenueCat, indie app builders, iOS developers, and subscription growth keywords.
- $25: Design polish for a single social preview image or short clip thumbnail if organic traction starts. If a free asset performs well, keep this unspent.
- $20: Promote the post in one founder newsletter or community placement only if the community accepts small sponsored tool/resource mentions.
- $10: Reserve for a second X boost on whichever angle performs best after 24 hours: technical parser detail, privacy mode, or agent workflow.

I would not spend the full $100 before seeing organic signals. The first posts should identify which message attracts the right audience.

## Measurement plan

Top-of-funnel:

- Impressions and click-through rate on X.
- Upvotes/comments on Hacker News and Reddit.
- Community replies from RevenueCat users or subscription founders.

Repository:

- GitHub stars.
- Clone count.
- Unique visitors.
- Issues or discussions opened.

Activation:

- Clicks from blog to repo.
- Clicks from repo to RevenueCat API docs.
- Demo report generation, if a hosted demo or anonymous telemetry is later added. In this version there is no telemetry by design.

Qualitative:

- Which metric users ask to add next.
- Whether users understand the read-only key and privacy-mode story.
- Whether agent developers ask for JSON comparison, scheduled runs, or Slack output.

## Execution sequence

Day 0:

- Publish repository, blog post, video tutorial, and social preview.
- Post RevenueCat Community and X thread.
- Reply to early comments with implementation detail, not generic promotion.

Day 1:

- Submit Show HN early US morning.
- Post to Indie Hackers.
- Boost the X post with the best organic engagement after the first 6-12 hours.

Day 2:

- Post to r/iOSProgramming or r/SwiftUI only if the timing and rules fit.
- Share a short follow-up showing the `chartable` segment parsing lesson.
- Open GitHub issues for the top requested improvements.

## Success criteria

Minimum success:

- 100+ qualified blog visitors.
- 25+ GitHub repository visitors.
- 5+ substantive comments from developers or founders.

Strong success:

- 500+ qualified blog visitors.
- 100+ GitHub visitors.
- 20+ stars or saves.
- At least 3 developers say they tried the demo or plan to run it with their own RevenueCat project.
