# Private expected findings — benchmark evaluator only

**Do not supply this document to the frontend auditing agent.** Open only after its audit artifacts have been generated and frozen. It is an answer key, not a design specification. It cannot substitute for checking live screenshots, browser behavior or source paths.

The fixture contains **five connected screens** and deliberate problems. Several are subjective/context-dependent. An audit should explain impact and evidence, not merely recite a list.

## Critical execution checks (before grading design)

- [ ] Project served over HTTP and opened successfully in an actual browser.
- [ ] `/`, `/orders/`, `/analytics/`, `/customers/`, `/settings/` visited.
- [ ] 1440px, 768px, 390px screenshot coverage (15 route/viewport pairs) or explicit coverage gaps.
- [ ] Screenshots **interpreted by the visual reasoning backend**, not merely written to disk.
- [ ] Source/visual/behavior specialists returned valid structured outputs; failures weren't silently converted to successful audits.
- [ ] No claims of measured Web Vitals or verified accessibility without appropriate testing.

## Expected concrete findings

| ID | Area | Seeded issue / desirable observation | Where to inspect | Evidence to seek |
|---|---|---|---|---|
| F01 | Visual identity | Coherent dark navy navigation shell, pale canvas, white cards, teal accents; different route-level treatments fracture this pattern | `assets/styles.css`, all screenshots | Cross-page comparison + CSS tokens |
| F02 | Typography | Orders title uses 35px while default is 29px; Settings title switches to Georgia; Customers title is 27px | CSS `.orders-page .page-heading`, `.settings-page .page-heading`, `.customers-page .page-heading` | Computed styles plus actual headings |
| F03 | Color | Settings primary button uses violet instead of global teal button; analytics acquisition bar uses standalone violet/gold colors | `.settings-page .btn-primary`, analytics inline styles | Computed CSS + screenshots |
| F04 | Readability | Orders subtitle `#a9b5c2`, analytics caption `#b5bfcb`, settings subtle text `#b5c0cb` on pale surfaces are hard to read | CSS, corresponding screens | Contrast ratio with actual background where measurable |
| F05 | Geometry | Analytics panels have 4px border radius rather than global 14px; Customers second card uses 4px; Orders destructive button radius 2px | CSS & screenshots | Component comparison |
| F06 | Mobile layout | Orders table is 870px wide and `.table-shell` has overflow visible; horizontal overflow at narrow viewports | Orders 390px / 320px | DOM scrollWidth and screenshot |
| F07 | Mobile layout | Settings `.fixed-field-row` has `min-width:720px`, potentially breaking small-screen layout | Settings 390px / 320px | DOM bounding boxes, screenshot |
| F08 | Mobile layout | Analytics `.chart-frame` has `min-width:680px`, causing overflow | Analytics mobile | DOM scrollWidth and screenshot |
| F09 | Accessible focus | `nav-link` and `icon-button` suppress focus-visible outline | CSS; keyboard tab | Keyboard focus and styles |
| F10 | Accessible labeling | Topbar notification icon button has no accessible name | All routes: `#notifications` | DOM semantics / a11y scanner |
| F11 | Modal UX | Orders dialog does not move focus inside, restore focus, or trap focus while open | `src/orders.js` + Orders View action | Keyboard trace and code |
| F12 | Misleading setting | Dark mode switch changes `aria-checked` and shows toast but does not change the visual theme | `src/settings.js` | Toggle + screenshot/theme comparison |
| F13 | Save behavior | Settings reports success immediately; values >80000 trigger later failure, with no rollback of displayed state | `src/settings.js` | Set threshold 85000, save, record before/after feedback |
| F14 | Security data-flow | `toast(message)` uses `innerHTML`; Settings injects uncontrolled workspace name into its message | `src/components.js`, `src/settings.js` | Trace actual call path; **do not execute payloads** |
| F15 | Security false positive | `safeNotice()` uses constant trusted HTML; Orders table uses fixed synthetic record templates | `src/components.js`, `src/orders.js` | Distinguish sink presence from exploitability |
| F16 | Range-slider design | Analytics control spans $1–$100,000 on a linear step-1 scale; fine low-value adjustment is awkward; a log or segmented scale may be appropriate subject to user needs | Analytics page, `src/analytics.js` | Range/step values + actual interaction |
| F17 | Motion accessibility | Infinite beacon animation and multiple transitions have no `prefers-reduced-motion` fallback | CSS `.live-beacon`, `@keyframes`, nav transitions | Styles and media-query inventory |
| F18 | Information density | Orders toolbar has many competing buttons before the data table; assess priorities without assuming all controls should be removed | Orders desktop/mobile | Visual composition + task prioritization |
| F19 | Functional affordances | Several controls look actionable but do nothing meaningful (e.g. dashboard chart period selector, buttons such as Columns / Archive / Review permissions) | Rendered UI + handler inventory | Interaction attempts on safe fixture or source event-handler mapping |
| F20 | Testing | Test suite is only two data-level smoke checks, no route, visual, interaction, or a11y tests | `tests/smoke.test.mjs`, package.json | Test inventory |
| F21 | Cross-page patterns | Shared sidebar, topbar, KPI cards, panels, badges; some components are CSS classes rather than framework components | All HTML, CSS and `src/components.js` | Actual inventory, not fabricated React components |
| F22 | Performance nuance | No external fonts, scripts or backend requests. SVG charts are local and synthetic. Avoid inventing poor LCP/INP or network bottlenecks | App + runtime traces | Explicit measured/unmeasured labeling |

## Known limitations and evaluation cautions

- F01, F18 are interpretive; different defensible assessments are possible.
- An analyzer that identifies every seeded issue by reading this key has **failed the isolation rule**.
- Some issues need interactive inspection; a source-only report should say "inferred from source, not verified in browser".
- A security finding must trace the untrusted input into the `innerHTML` sink. Do not label all HTML-string use as a confirmed vulnerability.
- The benchmark's synthetic UI should not be changed to make the auditor appear more accurate.
- It is acceptable for an auditor to discover legitimate issues not listed here, if they are evidence-backed.
- Do not use this checklist as a quantitative ground truth for subjective design quality; review concrete evidence.
