# Performance audit

Navigation timing values below are single-run browser laboratory observations. They are not field Core Web Vitals and are not comparable across different browsers, networks, routes, cache states, or machine load.

| Route | Viewport | Response (ms) | DOM content loaded (ms) | Load event (ms) | Transfer size (bytes) |
|---|---|---:|---:|---:|---:|
| `/` | home:desktop | 18 | 115 | 115 | 11904 |
| `/` | home:tablet | 1 | 29 | 29 | 11904 |
| `/` | home:mobile | 1 | 32 | 32 | 11904 |
| `/analytics/` | analytics:desktop | 3 | 55 | 56 | 7506 |
| `/analytics/` | analytics:tablet | 1 | 43 | 43 | 7506 |
| `/analytics/` | analytics:mobile | 1 | 45 | 45 | 7506 |
| `/customers/` | customers:desktop | 1 | 32 | 32 | 9397 |
| `/customers/` | customers:tablet | 1 | 27 | 27 | 9397 |
| `/customers/` | customers:mobile | 1 | 27 | 27 | 9397 |
| `/orders/` | orders:desktop | 1 | 35 | 37 | 6851 |
| `/orders/` | orders:tablet | 1 | 45 | 47 | 6851 |
| `/orders/` | orders:mobile | 1 | 32 | 34 | 6851 |
| `/settings/` | settings:desktop | 1 | 54 | 54 | 7330 |
| `/settings/` | settings:tablet | 1 | 40 | 40 | 7330 |
| `/settings/` | settings:mobile | 1 | 39 | 39 | 7330 |

LCP, INP, CLS, bundle analysis, long tasks, and comparative before/after measurements were not collected by this pass.
