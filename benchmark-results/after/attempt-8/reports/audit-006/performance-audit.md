# Performance audit

Navigation timing values below are single-run browser laboratory observations. They are not field Core Web Vitals and are not comparable across different browsers, networks, routes, cache states, or machine load.

| Route | Viewport | Response (ms) | DOM content loaded (ms) | Load event (ms) | Transfer size (bytes) |
|---|---|---:|---:|---:|---:|
| `/` | home:desktop | 4 | 94 | 95 | 11904 |
| `/` | home:tablet | 1 | 25 | 25 | 11904 |
| `/` | home:mobile | 1 | 26 | 26 | 11904 |
| `/analytics/` | analytics:desktop | 1 | 45 | 45 | 7506 |
| `/analytics/` | analytics:tablet | 1 | 32 | 33 | 7506 |
| `/analytics/` | analytics:mobile | 1 | 30 | 31 | 7506 |
| `/customers/` | customers:desktop | 1 | 25 | 26 | 9397 |
| `/customers/` | customers:tablet | 1 | 25 | 25 | 9397 |
| `/customers/` | customers:mobile | 1 | 34 | 34 | 9397 |
| `/orders/` | orders:desktop | 1 | 64 | 66 | 6851 |
| `/orders/` | orders:tablet | 1 | 52 | 54 | 6851 |
| `/orders/` | orders:mobile | 1 | 31 | 32 | 6851 |
| `/settings/` | settings:desktop | 1 | 31 | 31 | 7330 |
| `/settings/` | settings:tablet | 3 | 50 | 50 | 7330 |
| `/settings/` | settings:mobile | 1 | 32 | 32 | 7330 |

LCP, INP, CLS, bundle analysis, long tasks, and comparative before/after measurements were not collected by this pass.
