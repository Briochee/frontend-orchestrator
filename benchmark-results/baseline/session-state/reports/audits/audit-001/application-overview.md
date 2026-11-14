# Application overview

Name: `northstar-ops-audit-fixture`
Purpose: Dependency-free multi-route frontend audit benchmark with synthetic data
Framework signals: Static HTML/CSS/JavaScript (detected from files)
Language signals: CSS, HTML, JavaScript

## User-facing route candidates

- `/` — static page (from `index.html`; methods: html_file).
- `/analytics` — page (from `index.html`; methods: html_file, internal_link).
- `/customers` — page (from `index.html`; methods: html_file, internal_link).
- `/index.html` — page (from `index.html`; methods: internal_link).
- `/orders` — page (from `index.html`; methods: html_file, internal_link).
- `/settings` — settings screen (from `index.html`; methods: html_file, internal_link).
- `/analytics/../analytics` — page (from `analytics/index.html`; methods: internal_link).
- `/analytics/../customers` — page (from `analytics/index.html`; methods: internal_link).
- `/analytics/../index.html` — page (from `analytics/index.html`; methods: internal_link).
- `/analytics/../orders` — page (from `analytics/index.html`; methods: internal_link).
- `/analytics/../settings` — settings screen (from `analytics/index.html`; methods: internal_link).
- `/customers/../analytics` — page (from `customers/index.html`; methods: internal_link).
- `/customers/../customers` — page (from `customers/index.html`; methods: internal_link).
- `/customers/../index.html` — page (from `customers/index.html`; methods: internal_link).
- `/customers/../orders` — page (from `customers/index.html`; methods: internal_link).
- `/customers/../settings` — settings screen (from `customers/index.html`; methods: internal_link).
- `/orders/../analytics` — page (from `orders/index.html`; methods: internal_link).
- `/orders/../customers` — page (from `orders/index.html`; methods: internal_link).
- `/orders/../index.html` — page (from `orders/index.html`; methods: internal_link).
- `/orders/../orders` — page (from `orders/index.html`; methods: internal_link).
- `/orders/../settings` — settings screen (from `orders/index.html`; methods: internal_link).
- `/settings/../analytics` — settings screen (from `settings/index.html`; methods: internal_link).
- `/settings/../customers` — settings screen (from `settings/index.html`; methods: internal_link).
- `/settings/../index.html` — settings screen (from `settings/index.html`; methods: internal_link).
- `/settings/../orders` — settings screen (from `settings/index.html`; methods: internal_link).
- `/settings/../settings` — settings screen (from `settings/index.html`; methods: internal_link).

## Detected frontend infrastructure

- Build tools: not detected
- Styling: {}
- Component libraries: not detected
- State/data libraries: not detected
- Test infrastructure: not detected

The route list and infrastructure are repository-derived signals. They do not prove that a route is reachable or describe application intent beyond the recorded project description.
