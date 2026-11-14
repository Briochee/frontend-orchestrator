# Technical and architecture audit

Audit backend: `codex_cli_plus_static`

## Evidence-backed specialist assessment

### frontend_code_auditor · first_pass

Source observations: the five routes are separate HTML documents. Each loads the shared `src/app.js`, and four also load a route-specific module. The shared code is limited to helpers such as toast rendering; route markup and most displayed metrics are authored directly in each HTML file. Orders renders from the fixed `orders` array, while the customer route contains its cards in HTML and its module imports but does not use the `customers` array. The analytics slider updates its label and a fixed two-value count. Inference: this is a small, low-overhead static fixture, but several route interactions are demonstrations rather than data-backed operations. No project code, scripts, tests, builds, or servers were run. There are no attached screenshots, so rendered behavior and visual appearance are not assessed, and no performance measurements are available.

Evidence:
- `index.html:8` — The overview loads the shared app module after its static page markup.
- `orders/index.html:8` — The orders route loads the shared app module and a route-specific orders module.
- `src/orders.js:9` — The orders route filters the imported fixture and rebuilds table rows with innerHTML.
- `src/customers.js:1` — The customers module imports the customers fixture but its handlers filter existing DOM cards.
- `customers/index.html:7` — Customer records are embedded as static cards in the route markup.
- `tests/smoke.test.mjs:4` — The included test source covers fixture presence and currency formatting only; it does not cover route interactions.

## Findings

### TECH-03084977 · Workspace name is inserted into toast HTML

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `security`
- Description: The settings submit handler reads the editable workspace name and interpolates it into a toast message. The shared toast helper assigns that message to `innerHTML`, so markup entered in the field is parsed when the toast is shown. The fixture has no backend or persistence path, which limits this to the current browser session, but the sink should not treat editable text as trusted HTML.
- Impact: A workspace name containing HTML can change the toast DOM and may execute event-handler markup in the page context.
- Recommendation: Build the toast with DOM nodes and set the workspace name through textContent, or make the toast API accept text rather than arbitrary HTML.
- Evidence:
  - `settings/index.html:7` — The workspace name is an editable form input.
  - `src/settings.js:18` — The form value is interpolated into the toast message.
  - `src/components.js:8` — The shared toast helper inserts its argument with innerHTML.

### TECH-291E90DE · Dark mode switch changes its checked state without applying a theme

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `state and behavior`
- Description: Clicking the dark mode switch changes `aria-checked` and announces that the preference was updated, but the handler does not apply a theme class or theme attribute. The stylesheet only styles the switch state itself; no dark theme is selected by this interaction.
- Impact: The control reports a preference change while the workspace appearance remains unchanged.
- Recommendation: Apply a theme state to the document when the switch changes, or adjust the control and feedback to describe a UI-only demo toggle.
- Evidence:
  - `settings/index.html:7` — The switch is labeled Dark mode and described as changing workspace appearance.
  - `src/settings.js:5` — The handler toggles the checked attribute and reports an updated preference.
  - `assets/styles.css:2` — The switch checked state changes the control styling; no theme application is present in the stylesheet rules.

### TECH-45E0725A · User-controlled content reaches an HTML rendering sink

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `security_and_rendering`
- Description: `toast` writes `message` to `innerHTML`. A caller passes a value derived from editable value `team`; the inspected path contains no recognized HTML sanitizer.
- Impact: Markup supplied through the editable value can be parsed as HTML in the current page context.
- Recommendation: Render user-provided values with `textContent` or DOM nodes; if authored markup is required, sanitize it with a reviewed allowlist sanitizer.
- Evidence:
  - `src/components.js:8` — HTML sink receives the traced value.
  - `src/settings.js:18` — Call site supplies the value written to the HTML sink.
  - `src/settings.js:13` — `team` is read from a DOM or browser-provided value.

### TECH-49AF50F2 · Analytics cutoff count has only two hard-coded outcomes

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `data correctness`
- Description: The analytics page says the order-value cutoff filters a summary metric, but the handler sets the qualified count to 286 for every cutoff at or below 40,000 and 11 above that. It does not filter an analytics dataset or derive the count from the orders fixture, so most slider positions change the displayed amount without meaningfully changing the count.
- Impact: Users cannot explore how the qualified-order count changes across the slider range, and the displayed count is not traceable to route data.
- Recommendation: Calculate the count from an analytics dataset that includes order values, or label the two outcomes as a deliberately simplified demo.
- Evidence:
  - `analytics/index.html:7` — The slider is presented as a cutoff that filters the summary metric.
  - `src/analytics.js:5` — The qualified-order count is selected by a single fixed threshold.
  - `src/data.js:2` — The available order fixture is a separate fixed array; no analytics records are exported.

### TECH-4D7AF6CB · Order dialog lacks a focus lifecycle

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `accessibility`
- Description: Opening the order preview only unhides the element marked `role="dialog"` and `aria-modal="true"`. The handler does not move focus into it, keep keyboard focus inside it, restore focus to the triggering row button on close, or close it on Escape. The shared Escape handler only closes the navigation menu.
- Impact: Keyboard and assistive-technology users may remain behind the modal or tab into background controls while it is marked modal.
- Recommendation: Use a native dialog with an explicit open/close flow, or implement focus entry, focus containment, Escape dismissal, and focus restoration.
- Evidence:
  - `orders/index.html:7` — The order preview is declared modal and contains close and confirm buttons.
  - `src/orders.js:17` — The preview is opened by setting hidden to false; no focus management accompanies the operation.
  - `src/app.js:8` — The global Escape handler only updates the navigation menu state.

### TECH-7113E33A · Customer records have two separate source representations

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `state ownership`
- Description: The customer route embeds record values in its HTML cards, while `src/customers.js` imports the shared customer array but never reads it. Search filters the existing cards through their `data-customer` attributes. The current fixture values appear aligned, but updates to the array will not update the rendered customer directory.
- Impact: Future edits can leave the shared fixture and visible directory out of sync, and the route currently pays to import unused data.
- Recommendation: Choose one source for directory records: render cards from the imported fixture or remove the unused import and treat the HTML cards as canonical.
- Evidence:
  - `src/customers.js:1` — The module imports the customer fixture and filters DOM cards without using the imported array.
  - `src/customers.js:7` — Search logic acts on the pre-existing cards and their data attributes.
  - `customers/index.html:7` — Customer names and profile values are embedded in static card markup.
  - `src/data.js:12` — A separate customer records array is exported from the shared fixture module.

### TECH-7A17A488 · Settings announces success before the simulated save can fail

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `interaction reliability`
- Description: Submitting settings immediately writes “Saved successfully” and shows a success toast. For thresholds above 80,000, the handler changes the live status to a sync failure after 450 ms, while the toast remains visible for 3,200 ms. The route markup documents this simulation, but the success toast is not replaced when the failure state arrives.
- Impact: For the documented failure case, the user can receive success feedback and then see a failure status while the stale success toast remains.
- Recommendation: Wait until the simulated result is known before announcing success, and show only the final outcome in both the status message and toast.
- Evidence:
  - `src/settings.js:16` — Success feedback is issued before the delayed failure branch.
  - `src/settings.js:20` — The status changes to a failure message only after the delay.
  - `src/components.js:9` — The toast remains visible until its independent timeout expires.

### TECH-9E8C53D8 · Settings form row retains a 720 px minimum width on mobile

- Severity: **low**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive layout`
- Description: The settings stylesheet keeps `.fixed-field-row` at a 720 px minimum width. The mobile media rule changes the form row to one column but does not reset that minimum width, so the row can remain wider than the settings content at narrow viewports. This is inferred from CSS; no rendered viewport evidence was supplied.
- Impact: On narrow screens, form controls may extend beyond the content area and require horizontal page scrolling.
- Recommendation: Remove the fixed minimum width at the mobile breakpoint and let the fields stack within the available content width.
- Evidence:
  - `assets/styles.css:4` — The settings-specific form row has a fixed minimum width.
  - `assets/styles.css:9` — The mobile rule changes the form row grid but does not change its minimum width.
  - `settings/index.html:7` — The workspace form uses the fixed-field-row class.

### TECH-BD7E30E3 · Orders table overflow override disables its horizontal scroll container

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `responsive layout`
- Description: The shared table shell is configured for horizontal scrolling, but the orders-specific rule changes its overflow to visible while the table has a minimum width of 870 px. On narrower content areas, the table can extend beyond the shell instead of scrolling within it. This is a source-based layout conclusion; no viewport rendering was available.
- Impact: At narrow widths, the table may widen the page and make neighboring content harder to reach without page-level horizontal scrolling.
- Recommendation: Keep horizontal scrolling on the table shell while retaining the table minimum width, or provide another constrained overflow container.
- Evidence:
  - `assets/styles.css:2` — The base table shell enables horizontal scrolling.
  - `assets/styles.css:4` — The orders override sets overflow visible and the table minimum width to 870 px.

### TECH-E622F0EB · Keyboard focus outlines are removed from navigation and icon buttons

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `accessibility`
- Description: The stylesheet explicitly removes the `:focus-visible` outline for navigation links and icon buttons without adding another focus indicator in that rule. This affects the shared sidebar links and icon controls, including the menu and notifications buttons.
- Impact: Keyboard users may not be able to identify which of these controls currently has focus.
- Recommendation: Provide a visible focus style for these selectors, such as an outline with adequate offset and contrast.
- Evidence:
  - `assets/styles.css:6` — The focus-visible rule sets outline to none for both selectors.
  - `index.html:6` — The shared header includes icon buttons and the sidebar contains navigation links.


## Evidence and limitations

- Audit status is incomplete. Required specialist `frontend_code_auditor` did not complete both structured passes.
- Review partial findings, correct the listed evidence or backend gaps, then retry with: frontend-director audit --project /private/tmp/frontend-director-benchmark-20261114/demo-app --url http://127.0.0.1:8765/ --depth deep --codex
- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.
- The audit used only the supplied source snapshot and inventory; no network requests were made.
- No project code, tests, build, server, or dependency lifecycle was executed.
- No rendered screenshots were attached, so visual appearance and actual viewport behavior were not observed.
- Performance behavior was not measured; comments about overhead are limited to the small static module and data structure visible in source.
- frontend_code_auditor cross-validation pass was unavailable; first-pass findings were retained: ValueError: technical finding used unsupported evidence kind: inventory
- No rendered evidence was attached, so visual appearance was not assessed.
- No project code, scripts, server, build, dependency manager, or network request was run; keyboard, touch, and live browser behavior were not directly verified.
- The analytics metric's intended calculation and the product decisions behind currently inert controls are not defined in the supplied source.
- This is a static source audit; no project code, scripts, builds, servers, or dependency commands were run.
- No rendered screenshots were attached to the task evidence, so appearance and live keyboard, touch, and assistive-technology behavior were not verified.
- Several controls may be intentionally demonstrative. Findings about whether those controls should perform a full action depend on product intent, noted with requires_human_decision.
- The review is based on the supplied viewport screenshots and read-only source inspection. No project code was executed.
- The screenshots capture viewport-sized views rather than full-page images, so they do not show all below-the-fold content at tablet and mobile sizes.
- No alternate scroll positions or interaction states were assessed.
- This pass assesses only route / at the supplied desktop, tablet, and mobile default-state screenshots. Other routes listed in the inventory are outside the supplied screenshot set for this assessment.
- The mobile and tablet images show only the top portions of their pages, so below-the-fold appearance and density cannot be assessed from these renders.
- The assessment is visual; no interaction states were evaluated.
- This assessment uses only the supplied default-state screenshots and the included analytics source files; it does not infer interaction behavior.
- The screenshots show viewport captures rather than complete page captures, so content below the visible mobile area was not assessed.
- Only the supplied default-state screenshots for `/analytics/` at desktop, tablet, and mobile sizes were visually assessed.
- The mobile screenshot is a viewport capture and does not show the complete page below the visible region.
- No interaction or horizontal scrolling behavior was inferred from the screenshots.
- This assessment uses the supplied default-state screenshots and snapshot files only; it does not infer interaction behavior.
- The mobile screenshot shows only the first part of the customer list within the captured viewport, so content below that view was not visually assessed.
- The screenshots show only the default state; interaction and focus states were not visually assessed.
- The mobile capture ends partway through the third card, so lower-page content was not assessed visually.
- The supplied contrast ratio is a computed-style sample from the audit inventory and was not independently recalculated. No project code, browser, build, or server was run.
- The assessment covers only the supplied default-state screenshots. It does not establish how horizontal scrolling or any other interaction behaves.
- Only the supplied default-state screenshots and included source were reviewed. Interactions, horizontal panning, other states, and dimensions outside the supplied runtime inventory were not independently verified.
- The visual review uses only the supplied default screenshots for /settings/ at desktop, tablet, and mobile. No scrolled screenshots or interaction states were inspected.
- The review used only the supplied default screenshots and source snapshot. Scrolled content, interaction states, and additional viewport sizes were not inspected.
- The app, scripts, builds, and server were not run. The overflow mechanism is supported by source inspection and visible screenshot evidence, not a new runtime measurement.
- This synthesis uses the supplied cross-validated route assessments and project evidence summary; screenshots were not reopened in this pass.
- Source citations refer to the inspected stylesheet assets/styles.css. The supplied materials do not provide line-numbered runtime records.
- Rendered observations are limited to the supplied default-state screenshots and assessment notes; interaction states, focus appearances, horizontal panning, scrolled content, and other viewport sizes were not independently reviewed.
- Document-width values are reproduced from the supplied runtime inventory and are not new measurements from this synthesis.

## Suggested next steps

- Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
- Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
- Keep editable settings text out of HTML insertion sinks.
- Derive analytics results from an explicit data source, or communicate that the slider is only a simplified demonstration.
- Make settings feedback reflect the final save outcome and ensure preference controls apply the behavior they announce.
- Give the order dialog a complete focus and dismissal lifecycle.
- Restore visible keyboard focus indicators for shared navigation and icon controls.
- Preserve constrained scrolling for wide tables and remove fixed-width form constraints at mobile breakpoints.
- Use one canonical source for customer directory records.
- Keep closed mobile navigation out of both keyboard focus order and the accessibility tree; add complete focus management to the order dialog.
- Restore visible keyboard focus styles and provide an accessible name for the notification button.
- Implement or clearly identify unavailable order and customer directory controls, including customer-specific action buttons.
- Show a customer no-results state and make the analytics cutoff reflect a meaningful range of values.
- Align settings and export success feedback with the result the user actually receives.
- Address the closed mobile sidebar and order dialog focus behavior, then restore visible focus cues and name the notification button.
- For controls that currently do nothing, either implement the labeled action or communicate its demo-only availability at the control.
- Align analytics and settings feedback with the actual outcome, including the cutoff count, download behavior, theme state, and simulated save failure.
- Consider a more compact mobile KPI presentation only if reducing scroll depth is a product priority; the current screenshot does not establish that the existing stack is a usability failure.
- Keep the current mobile KPI spacing unless faster first-viewport access to trends is a defined product priority; if it is, compare a denser KPI treatment against the current card readability.
- Address the chart and panel overflow at tablet and mobile widths, choosing between a scaled chart and a contained, visibly scrollable chart.
- Consider slightly increasing the contrast or size of the pale “Updated moments ago” note if it is meant to be readily read; this is a subjective visual refinement, not an observed layout failure.
- Adjust the chart sizing and analytics grid breakpoints so both panels remain within narrow viewports, or provide a clear chart-level horizontal scrolling affordance if the current chart scale must be preserved.
- Keep the desktop heading, paired analytics cards, and order explorer hierarchy; it is clear and fully visible in the supplied desktop render.
- Apply the shared rounded corner treatment to every customer card.
- Increase the contrast of the sidebar footer initials against the avatar background.
- Use the shared customer-card radius for the Morgan Ellis card at all breakpoints.
- Give the sidebar footer avatar initials a darker foreground than the muted workspace descriptor.
- Preserve the existing heading hierarchy, teal invite action, and one-column mobile and two-column tablet adaptations.
- Contain the table's minimum width in a deliberate small-screen layout and make access to its trailing columns apparent.
- Restore a contained horizontal scroll area for the orders table at narrow viewport sizes, preserving access to all columns while avoiding page-level width growth.
- Review the tablet toolbar wrapping: the search field and filters occupy different rows, and Date range and Archive wrap to another row.
- Allow the workspace details form and its row to shrink within the settings grid, preserving a visible card gutter at mobile and tablet widths and separation from the neighboring card on desktop.
- Constrain the Workspace details form row to its panel by removing its fixed minimum width; preserve the existing single-column form layout at the mobile breakpoint.
