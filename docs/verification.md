# Verification record

## Completed locally

- Real Elexon snapshot retrieved on 27 October 2026; source URLs and checksum committed.
- Ten Python unittest cases passed, including a full-snapshot check that selected forecasts never exceed the decision cutoff.
- TypeScript compilation and Vite production build passed.
- Frontend dependency installation reported zero known vulnerabilities at installation time.
- The default decision view loaded real values: 15 January 10:00 GMT → 16 January delivery, 24/24 forecasts, latest publication 09:30, 191.402 GWh forecast energy, 858.708 MW realised MAE.
- Accuracy view loaded 744/744 matched observations and full-month metrics.
- Public repository created and local source pushed to `main`.
- GitHub Actions run 40549914945 passed backend tests, frontend build and Docker image build: https://github.com/harshitdeora/q7m2x9/actions/runs/40549914945
- Local Docker Compose image built and started successfully; container reports healthy. In-container HTTP checks returned 200 for the React page and 24-hour coverage for the Python decision endpoint.
- Browser checks: decision workspace and accuracy view load real data; changing the cutoff from 10:00 to 16:00 changes the selected publication from 09:30 to 15:30 and updates the forecast energy from 191.4 to 198.2 GWh.
- Phone-width layout inspected: document clientWidth and scrollWidth were both 375 px (no horizontal page overflow).
- Additional browser checks passed: actuals toggle, 24-row hourly audit table, and next-day navigation updated both delivery date and forecast values.
- Production Vercel deployment reached READY at https://q7m2x9.vercel.app.
- The Vercel project is connected to `harshitdeora/q7m2x9` for automatic GitHub deployments, with user-approved access limited to this repository.
- Unauthenticated production HTTP checks returned 200 for `/`, `/api/health`, `/api/decision`, `/api/accuracy`, and `/api/export`.
- Production 31 January decision returned deliveryDate `2026-02-01`; production full-month statistics matched local calculations.

## In progress / remaining checks

- The assignment's literal incognito-window access check is **not complete**. An attempt to select the native Brave window was blocked by the computer-use policy because it could not determine the current browser URL confidently. Browser interaction stopped at that point. Unauthenticated HTTP access succeeded, but is not claimed as an incognito check. Manually open the production URL and public repository in an incognito window before submission.
- YouTube video has not been recorded or uploaded.

This record is updated as checks complete. A configured workflow is not proof that it has passed.
