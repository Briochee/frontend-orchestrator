# Performance audit

Navigation timing values below are single-run browser laboratory observations. They are not field Core Web Vitals and are not comparable across different browsers, networks, routes, cache states, or machine load.

| Route | Viewport | Response (ms) | DOM content loaded (ms) | Load event (ms) | Transfer size (bytes) |
|---|---|---:|---:|---:|---:|
| `/` | home:desktop | 5 | 108 | 109 | 11904 |
| `/` | home:tablet | 1 | 33 | 33 | 11904 |
| `/` | home:mobile | 2 | 40 | 40 | 11904 |
| `/analytics/` | analytics:desktop | 1 | 58 | 58 | 7506 |
| `/analytics/` | analytics:tablet | 1 | 33 | 33 | 7506 |
| `/analytics/` | analytics:mobile | 1 | 43 | 43 | 7506 |
| `/customers/` | customers:desktop | 1 | 28 | 28 | 9397 |
| `/customers/` | customers:tablet | 1 | 31 | 31 | 9397 |
| `/customers/` | customers:mobile | 1 | 42 | 42 | 9397 |
| `/orders/` | orders:desktop | 1 | 42 | 43 | 6851 |
| `/orders/` | orders:tablet | 1 | 38 | 40 | 6851 |
| `/orders/` | orders:mobile | 1 | 31 | 33 | 6851 |
| `/settings/` | settings:desktop | 1 | 37 | 37 | 7330 |
| `/settings/` | settings:tablet | 1 | 27 | 27 | 7330 |
| `/settings/` | settings:mobile | 1 | 36 | 37 | 7330 |

LCP, INP, CLS, bundle analysis, long tasks, and comparative before/after measurements were not collected by this pass.
