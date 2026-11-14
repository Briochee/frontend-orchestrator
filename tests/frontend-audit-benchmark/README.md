# Frontend Design Director: Audit Benchmark v1

A **dependency-free, deliberately imperfect** five-screen storefront operations dashboard for evaluating the *actual quality* of the `frontend-design-director` orchestrator.

## Directory separation (important)

- **`demo-app/`** — the only directory to give to the frontend auditor. It contains actual source, five navigable screens, seeded UI/UX defects, fake data and a minimal smoke test.
- **`evaluator-private/`** — the evaluation key and scoring guidance. **Do not include this directory in the application's `--project` path or send it to the auditing model.** Consult it only after completing and freezing an audit report. Its existence should not be used to inflate audit findings.

## Run locally

From the extracted `frontend-audit-benchmark/` directory:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory demo-app
```

Open `http://127.0.0.1:8765/` in a desktop browser. The routes are:

- `/` — Overview (metrics, revenue SVG, activity feed, fulfillment health)
- `/orders/` — Orders table, live filtering, order-details modal
- `/analytics/` — Revenue chart, acquisition trends, numerical slider
- `/customers/` — Customer cards and search
- `/settings/` — Forms, faux theme toggle, simulated save behavior

The project needs no `npm install` and has no external dependencies or API calls. Node 18+ can optionally run the intentionally limited smoke tests with `cd demo-app && npm test`.

## Run an orchestrator audit

In a **second terminal**, from any directory:

```bash
frontend-director audit --help
```

Use your installed CLI's supported flags. If it supports those shown below:

```bash
frontend-director audit \
  --project "/ABSOLUTE/PATH/TO/frontend-audit-benchmark/demo-app" \
  --url http://127.0.0.1:8765 \
  --depth exhaustive \
  --codex
```

If `--depth` is unsupported, omit it or use the documented equivalent. The URL must point to the running server; otherwise a source-only audit may be produced. The `--codex` flag transmits selected project content and screenshots to the service used by your installed Codex CLI. This fixture contains synthetic data and no credentials.

**Do not** pass the ZIP root as `--project`; pass `demo-app/` only. Do not let the auditing model read `evaluator-private/`.

## Expected evidence coverage

At minimum, a serious visual audit should render all five screens at **1440, 768, and 390 CSS pixels**, producing **15 route/viewport screenshots** (or corresponding clearly documented equivalent evidence). Add 320px and 1920px to test extreme layouts. Capture the orders modal, filtered order results, settings save failure, slider state, mobile navigation, and keyboard focus when safe and supported.

The audit should provide:

1. Source/component/route architecture mapping.
2. Screen-specific visual descriptions grounded in screenshots.
3. Computed or source-grounded color/typography/spacing inventories.
4. Responsive overflow and navigation tests.
5. Interaction-state evidence, including *observed* outcomes.
6. Security data-flow analysis that distinguishes constant `innerHTML` from untrusted input.
7. Independent technical, visual, and behavioral reports with evidence and limitations.

## Safety / baseline rules

- All business records are fictional; email domains end with `.test`.
- There are no real backend writes, payments, logins, or remote API calls.
- The project intentionally contains defects. **Do not fix the app during baseline auditing.** First validate the orchestrator's diagnosis.
- A successful `node --test` or HTTP 200 response does not demonstrate visual correctness, accessibility, or interaction quality.
- If the browser cannot run, report that limitation. Do not fabricate screenshots or claim the UI was inspected visually.

After capturing reports, compare against `evaluator-private/EXPECTED_FINDINGS.md` and fill in `evaluator-private/REVIEW_SCORECARD.md`.
