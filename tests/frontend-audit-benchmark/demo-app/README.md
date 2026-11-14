# Northstar Ops — Synthetic Operations Dashboard

An offline, five-page static frontend fixture intended for UI quality assessment. No external network requests and no real user data.

## Run

From this directory: `python3 -m http.server 8765 --bind 127.0.0.1`

Open: `http://127.0.0.1:8765/`

## Structure

- `index.html`: overview/dashboard
- `orders/index.html`: order queue
- `analytics/index.html`: analytics
- `customers/index.html`: customer directory
- `settings/index.html`: workspace preferences
- `assets/styles.css`: global tokens, layout, components, responsive styles
- `src/components.js`: shared UI helpers
- `src/data.js`: synthetic fixtures
- `src/*.js`: route interaction handlers
- `tests/smoke.test.mjs`: narrow automated smoke tests

This fixture is not intended as production code. Evaluate it as-is before proposing changes. Do not claim to have inspected the rendered interface unless browser evidence was actually collected.
