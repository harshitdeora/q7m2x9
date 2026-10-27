# Demo guide — target length 9 minutes 30 seconds

Record the actual running application and your voice. Keep the final video under 10 minutes. Upload to YouTube as **Unlisted**, then open the watch URL in a private/incognito window while signed out. This script is preparation, not a substitute for the required video.

## Part 1: customer pilot presentation (0:00–4:35)

### 0:00–0:40 — Introduce the business problem

Show the Decision workspace at 15 January 2026, 10:00 GMT.

“Your team buys electricity today for delivery tomorrow. Wind changes the amount that needs to be covered elsewhere, but forecasts change as new information arrives. Aeris brings the forecast available at your decision time and the evidence of its later accuracy into one workspace.”

### 0:40–1:35 — Establish the decision context

Point to decision date, as-of time and next-day delivery date.

“We are replaying a decision made on 15 January at 10:00 GMT for delivery on 16 January. The latest publication used here is 09:30. Later updates are excluded. The 10:00 cutoff is configurable and is an illustrative assumption; the pilot does not impose an exchange deadline.”

Show the coverage card. Explain 24 available forecast hours and the publication timestamp.

### 1:35–2:25 — Explain the profile

Show the forecast chart and summary cards.

“The selected profile totals 191.4 GWh of national forecast wind energy. Its average output is 7.98 GW and its peak is 10.85 GW at 21:00. This is national context; it is not this supplier's contractual wind position.”

Toggle actuals off to show the decision-time forecast, then on to show the later comparison. Hover over a point.

“The actual line is available only after delivery. We label it retrospective so that hindsight is never confused with information the buyer had.”

### 2:25–3:30 — Quantify uncertainty honestly

Open Forecast accuracy. Explain that the full-month analysis covers January decision dates, including 31 January for 1 February delivery.

“At this cutoff, the pilot has 744 matched hourly observations. The mean absolute error is about 2,013 MW. Bias is about +1,730 MW, meaning wind was overestimated on average under our matching assumptions. RMSE highlights larger misses. These describe this historical month; they are not a guaranteed reserve margin or tomorrow’s prediction interval.”

Point to daily bars and hourly heatmap. Explain that a buyer can inspect variation rather than trusting one aggregate score.

### 3:30–4:35 — Trace the evidence and close the pitch

Select a day from Daily performance. Expand the hourly table and use Export CSV. Open Data & methodology.

“Every comparison has a target time, forecast, actual, error and publication time. The source snapshot and retrieval details are available for audit. This pilot makes the forecast and its limitations easier to assess. A production phase would agree decision cutoffs, connect your demand and contract positions, and build monitored ingestion before using it for procurement sizing.”

## Part 2: technical review and knowledge transfer (4:35–9:30)

### 4:35–5:20 — Architecture

Show repository structure and README.

“The frontend is React with TypeScript and Recharts. Python FastAPI owns validation, forecast selection and metrics. A compressed, committed snapshot of the two requested public Elexon datasets makes the demo reproducible. Vercel serves React assets and routes API calls to the Python function. Docker provides a portable single-container deployment.”

### 5:20–6:25 — The most important algorithm

Open `backend/analysis.py`, focusing on `decision`.

“We index forecasts by target startTime. For each delivery hour, we filter publications to publishTime less than or equal to the cutoff and choose the latest eligible one. We do this for every target, because different targets can have different publication times. If none exists, we return null. We never use later forecasts to fill a gap.”

Show the inclusive-cutoff test with a forecast exactly at the cutoff and another one second later.

### 6:25–7:15 — Data semantics and metrics

“The brief suggests matching half-hour targets, but actual January WINDFOR targets are hourly. We explicitly average the two FUELHH WIND actual half-hours for each forecast hour. Both halves must exist. This hourly representativeness assumption is documented and needs client validation before operational use. MW is power; daily energy integrates each hourly forecast over one hour.”

Point to `metrics`: MAE, RMSE, signed bias and nearest-rank P90. Explain missing values, zeros, sample counts and weighting by observations.

### 7:15–8:10 — API and frontend practices

Show `backend/app.py`, `/api/docs`, and `src/types.ts`.

“Typed query validation rejects dates outside the pilot. CSV exports preserve the publication timestamps. AbortController avoids stale frontend responses when the user changes dates quickly. Loading and failure states make data availability explicit. The interface has keyboard focus styles, a mobile layout, and reduced-motion support. The monthly result is cached by cutoff; loaded snapshot data is cached per process.”

### 8:10–9:00 — Verification and deployment

Show the test command/results, Dockerfile, CI workflow and Vercel project.

“Ten tests cover cutoff leakage, missing halves and zeros, known metric calculations, the February boundary, snapshot integrity, full-month selection, API validation and export. CI rebuilds the frontend and container. The two-stage Docker build compiles React and runs FastAPI as a non-root user. Dependency inputs and the frontend lockfile are committed.”

Mention actual verification status from `docs/verification.md`; do not claim any unperformed check.

### 9:00–9:30 — Limits and handover

“The snapshot is historical and does not refresh automatically. There are no customer demand data, prices, purchases or claims of savings. The error summaries are retrospective. A production phase would validate source definitions, add a durable ingestion pipeline, and calculate error estimates using only history available at each decision. The README contains startup and deployment instructions and explicitly discloses Codex assistance.”

Finish by showing the public app and repository URLs.
