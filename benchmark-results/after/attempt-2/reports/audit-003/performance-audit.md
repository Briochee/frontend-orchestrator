# Performance audit

Navigation timing values below are single-run browser laboratory observations. They are not field Core Web Vitals and are not comparable across different browsers, networks, routes, cache states, or machine load.

| Route | Viewport | Response (ms) | DOM content loaded (ms) | Load event (ms) | Transfer size (bytes) |
|---|---|---:|---:|---:|---:|
| `/` | home:desktop | 4 | 132 | 132 | 11904 |
| `/` | home:tablet | 1 | 27 | 27 | 11904 |
| `/` | home:mobile | 1 | 40 | 40 | 11904 |
| `/analytics/` | analytics:desktop | 1 | 56 | 56 | 7506 |
| `/analytics/` | analytics:tablet | 1 | 37 | 37 | 7506 |
| `/analytics/` | analytics:mobile | 1 | 42 | 42 | 7506 |
| `/customers/` | customers:desktop | 1 | 43 | 43 | 9397 |
| `/customers/` | customers:tablet | 1 | 37 | 37 | 9397 |
| `/customers/` | customers:mobile | 1 | 39 | 39 | 9397 |
| `/orders/` | orders:desktop | 2 | 45 | 47 | 6851 |
| `/orders/` | orders:tablet | 1 | 40 | 42 | 6851 |
| `/orders/` | orders:mobile | 1 | 40 | 43 | 6851 |
| `/settings/` | settings:desktop | 2 | 46 | 46 | 7330 |
| `/settings/` | settings:tablet | 1 | 30 | 30 | 7330 |
| `/settings/` | settings:mobile | 1 | 33 | 33 | 7330 |

LCP, INP, CLS, bundle analysis, long tasks, and comparative before/after measurements were not collected by this pass.
