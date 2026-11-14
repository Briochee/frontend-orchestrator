# Route and screen inventory

Discovered 26 route candidate(s) from source conventions, router literals, and local links. Dynamic segments are documented as patterns and were not navigated automatically.

| Route | Type | Source | Discovery | Confidence | Rendered |
|---|---|---|---|---|---|
| `/` | static page | `index.html` | html_file | high | No |
| `/analytics` | page | `index.html` | html_file, internal_link | high | No |
| `/customers` | page | `index.html` | html_file, internal_link | high | No |
| `/index.html` | page | `index.html` | internal_link | low | No |
| `/orders` | page | `index.html` | html_file, internal_link | high | No |
| `/settings` | settings screen | `index.html` | html_file, internal_link | high | No |
| `/analytics/../analytics` | page | `analytics/index.html` | internal_link | low | No |
| `/analytics/../customers` | page | `analytics/index.html` | internal_link | low | No |
| `/analytics/../index.html` | page | `analytics/index.html` | internal_link | low | No |
| `/analytics/../orders` | page | `analytics/index.html` | internal_link | low | No |
| `/analytics/../settings` | settings screen | `analytics/index.html` | internal_link | low | No |
| `/customers/../analytics` | page | `customers/index.html` | internal_link | low | No |
| `/customers/../customers` | page | `customers/index.html` | internal_link | low | No |
| `/customers/../index.html` | page | `customers/index.html` | internal_link | low | No |
| `/customers/../orders` | page | `customers/index.html` | internal_link | low | No |
| `/customers/../settings` | settings screen | `customers/index.html` | internal_link | low | No |
| `/orders/../analytics` | page | `orders/index.html` | internal_link | low | No |
| `/orders/../customers` | page | `orders/index.html` | internal_link | low | No |
| `/orders/../index.html` | page | `orders/index.html` | internal_link | low | No |
| `/orders/../orders` | page | `orders/index.html` | internal_link | low | No |
| `/orders/../settings` | settings screen | `orders/index.html` | internal_link | low | No |
| `/settings/../analytics` | settings screen | `settings/index.html` | internal_link | low | No |
| `/settings/../customers` | settings screen | `settings/index.html` | internal_link | low | No |
| `/settings/../index.html` | settings screen | `settings/index.html` | internal_link | low | No |
| `/settings/../orders` | settings screen | `settings/index.html` | internal_link | low | No |
| `/settings/../settings` | settings screen | `settings/index.html` | internal_link | low | No |

## Coverage boundary

The browser visits only the supplied base URL and any exact paths explicitly provided by the operator. A source route candidate is not proof that a route is reachable or authenticated.
