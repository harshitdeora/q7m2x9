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

## In progress / remaining checks

- Remaining browser interactions and public production verification.
- Vercel deployment: single-repository integration approved by the user; GitHub identity verification / installation completion is still pending in the browser.
- Public signed-out/private-window access checks after deployment.
- YouTube video has not been recorded or uploaded.

This record is updated as checks complete. A configured workflow is not proof that it has passed.
