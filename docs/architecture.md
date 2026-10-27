# Technical handover

## Responsibilities

`scripts/ingest.py` owns upstream HTTP requests and normalisation. It requests forecast publications by publication date and actuals by settlement date, capturing enough early publications to support January 1 decisions and actuals through February 1. The manifest preserves every request URL and a checksum. No ingestion endpoint is exposed publicly.

`backend/analysis.py` owns pure analytical rules. Selection uses timezone-aware datetimes. `decision` accepts injected forecast and actual maps for meaningful boundary testing. The default source loader indexes once per process. `month` caches up to 48 cutoff summaries; it recomputes safely on a cold start. Returning null rather than fabricating values is part of the analytical contract.

`backend/app.py` owns typed HTTP input, date-range validation, JSON and CSV output. The Docker process additionally mounts a built React directory. Vercel routes static files independently and uses `api/index.py` as the Python function entrypoint.

`src/main.tsx` owns the presentation and user interactions. API response contracts are in `src/types.ts`. A selected date and time drive fresh requests with cancellation. Day controls navigate January decisions; the accuracy view spans the whole month at the selected cutoff. Full-month results are deliberately labelled retrospective. Charts expose evidence visually; data tables and CSV make it inspectable without reading a chart.

## Why this architecture

The pilot is small, read-only, historical and bounded to public Elexon data. A checked-in snapshot is simpler and more reliable than making several upstream requests during each page load. It provides a fixed input for reviewers and removes the need for runtime keys, a database, queues or scheduled infrastructure. The backend is real Python and executes the analytical rules; the frontend does not reproduce those calculations as independent business logic.

One container supports local portability. Vercel provides the requested hosted sample through static and Python builders. No custom domain or paid integration is required.

## Important analytical caveats

- National metered-wind context is not the supplier's contracted generation.
- Hourly forecast representativeness versus half-hour actual means is an explicit matching assumption. Verify this against business expectations and current dataset semantics before operational adoption.
- Latest captured actual revisions are evaluation targets; they do not represent information known at the purchase cutoff.
- Full-month error statistics include outcomes later than individual January decisions. They are retrospective evaluation only, not ex-ante risk estimates.
- P90 absolute error is an empirical descriptor. It is not a calibrated prediction interval or suggested trading buffer.
- No prices, demand, existing positions, purchase volumes or savings are inferred.

## Operational next steps

Agree the client’s actual auction gate and timezone convention; validate generation coverage and target-period interpretation; build durable, monitored ingestion with completeness and revision tracking; add portfolio/demand/contract sources if procurement sizing is required; implement trailing historical evaluation using only outcomes known at each decision; and extend monitoring, authentication and service-level objectives as the scope requires.
