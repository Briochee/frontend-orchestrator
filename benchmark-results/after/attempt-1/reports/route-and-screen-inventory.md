# Route and screen inventory

Discovered 6 route candidate(s) from source conventions, router literals, and local links. Dynamic segments are documented as patterns and were not navigated automatically.

| Route | Type | Source | Discovery | Confidence | Rendered |
|---|---|---|---|---|---|
| `/` | static page | `index.html` | html_file | high | No |
| `/index.html` | page | `index.html` | internal_link | low | No |
| `/analytics/` | page | `index.html` | html_file, internal_link | high | No |
| `/customers/` | page | `index.html` | html_file, internal_link | high | No |
| `/orders/` | page | `index.html` | html_file, internal_link | high | No |
| `/settings/` | settings screen | `index.html` | html_file, internal_link | high | No |

## Coverage boundary

The browser visits only the supplied base URL and any exact paths explicitly provided by the operator. A source route candidate is not proof that a route is reachable or authenticated.
