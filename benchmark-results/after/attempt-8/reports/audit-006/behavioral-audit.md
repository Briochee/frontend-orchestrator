# Behavior and accessibility audit

Audit backend: `codex_cli_plus_static`

## Evidence-backed specialist assessment

### frontend_ux_auditor · first_pass

Source observations: The five routes use ordinary links for navigation. The shared mobile menu opens from its button, closes through the backdrop or Escape, and updates aria-expanded; notifications and supported demo exports show a transient status toast. Orders search and status filtering update the result count and render an empty row when there are no matches. The analytics slider updates its output locally. Customer search hides unmatched cards but does not render an empty state. Settings interactions are local: switches update aria-checked, and the form has a delayed simulated failure path for high thresholds. The included data is described as synthetic and the README describes the fixture as offline. Rendered observations: none; no screenshots are attached and rendered_evidence is empty. Measurements: none taken. Inferences: CSS declares fixed minimum widths for the orders table and settings form row that are likely to cause horizontal overflow at narrow widths; this was not rendered or measured. Hypotheses: the responsive overflow effects need browser confirmation. Network loading and real server recovery behavior are not reachable from the included source, so no claims are made about them.

Evidence:
- `src/app.js:5` — Shared source handlers cover the mobile menu, notifications, and the overview export selector.
- `src/orders.js:9` — Orders source implements local search/status filtering, an empty row, a details dialog, and demo-only order feedback.
- `src/customers.js:5` — Customer search only hides cards; the route module also binds the invite button.
- `src/settings.js:3` — Settings switch and form handlers update local state and schedule a simulated save failure.
- `assets/styles.css:4` — Shared CSS removes focus outlines on navigation and icon buttons and defines fixed responsive widths.
- `README.md:3` — The included project describes itself as an offline five-page static fixture with synthetic data.

Pass-scoped limitations:
- No project code, browser, build, server, dependency manager, or network request was run, per the read-only audit boundary.
- No screenshots were attached and rendered_evidence is empty, so rendered appearance and interaction outcomes were not observed.
- Responsive overflow findings are CSS-based inferences and were not measured at any viewport.
- Loading behavior for a real backend cannot be assessed because the included source uses synthetic local data and contains no request flow.

### frontend_ux_auditor · cross_validation

Source observations: The included page templates use link markup for primary navigation. Shared code opens the mobile menu from its button, closes it through the backdrop or Escape, and updates aria-expanded. Notifications and the supported Overview and Analytics exports call a status toast that hides after a timeout. Orders search and status filters update the result count and render an empty row when nothing matches; the View action reveals order details. Customer search hides unmatched cards without rendering an empty state. The Analytics slider updates its output and qualified-order summary locally. Settings switches update aria-checked; Dark mode also shows a confirmation toast but does not apply a workspace theme. A valid settings submission immediately reports success, then changes the live status to a simulated failure when the threshold exceeds $80,000. Several visible customer, orders, and overview controls have no corresponding source-defined interaction. Rendered observations: none; no screenshots are attached. Measurements: none taken. Inferences: the Orders table has a minimum width of 870px while its shell uses overflow:visible, and the Settings contact row has a 720px minimum width that the mobile rule does not reset. Both are likely to cause horizontal overflow at narrow widths, but this was not rendered or measured. The included README describes an offline fixture with synthetic data; real backend loading and recovery behavior cannot be assessed.

Evidence:
- `src/app.js:5` — The shared handlers toggle the mobile menu, close it on Escape or backdrop activation, update aria-expanded, and bind notifications and the Overview export selector.
- `src/components.js:8` — The shared status toast unhides its element and schedules it to hide after a timeout.
- `src/orders.js:11` — Orders filtering updates the count and renders an empty row; the View handler fills and reveals the details dialog.
- `src/customers.js:5` — Customer search toggles card visibility based on the query.
- `src/analytics.js:5` — The Analytics slider updates its output and qualified-order summary locally.
- `src/settings.js:5` — Settings switches update aria-checked; the form reports success before the threshold-based simulated failure status.
- `assets/styles.css:4` — The stylesheet sets overflow:visible for the Orders table shell, a minimum width for its table and the Settings contact row, and does not reset the latter in the mobile rule.
- `README.md:3` — The README describes the fixture as an offline static frontend with synthetic data.

Pass-scoped limitations:
- No project code, browser, build, server, dependency manager, or network request was run, as required by the read-only audit boundary.
- No screenshots were attached, so rendered appearance and interaction outcomes were not observed.
- No measurements were taken; the two responsive overflow findings are CSS-based hypotheses.
- Real backend loading and recovery behavior cannot be assessed from the supplied offline synthetic fixture.

## Findings

### BEH-00D61592 · Customer card More actions buttons have no source-defined action

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `card action feedback`
- Description: Customer cards include buttons titled More actions, but the customer module contains no handler for those buttons and the template provides no menu or destination.
- Impact: The repeated action affordance implies that customer-specific options are available from each card, but the supplied source defines no response.
- Recommendation: Connect each button to a customer-specific action menu or clarify that the action is unavailable.
- Evidence:
  - `customers/index.html:7` — Customer cards render More actions buttons.
  - `src/customers.js:9` — The route module binds Invite customer, with no card-action binding.

### BEH-60FE4C17 · Settings reports success before the simulated failure outcome

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `form feedback and recovery`
- Description: A valid form submission immediately sets the live status to Saved successfully and displays a Saved preferences toast. If the threshold exceeds $80,000, a timer changes the live status 450 ms later to Sync failed; your changes were not stored. The form does not provide recovery guidance for that failure.
- Impact: Users may act on the success feedback before the failure announcement and are not told what to do next after the simulated failure.
- Recommendation: Keep the initial and final status consistent with the simulated outcome, and provide a clear next step when saving fails while preserving the entered values.
- Evidence:
  - `src/settings.js:15` — The submit handler posts success feedback before scheduling the threshold-based failure status.
  - `settings/index.html:7` — The threshold hint describes the simulated failure condition and the save status is a polite live region.

### BEH-6931A4BE · Customer segment and sort buttons have no source-defined effect

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `filter and sort interaction`
- Description: The Customers toolbar presents All segments and Newest first as buttons. The customer module binds search and Invite customer interactions but contains no segment or sort handlers, so the supplied source defines no change to the directory for these buttons.
- Impact: Users can attempt to filter or reorder the directory without receiving a source-defined result or explanation.
- Recommendation: Connect the buttons to directory filtering and sorting behavior, or make their unsupported state clear.
- Evidence:
  - `customers/index.html:7` — All segments and Newest first are rendered as buttons in the customer toolbar.
  - `src/customers.js:9` — The route module binds the search input and Invite customer button only.

### BEH-6CE0F8DA · Dark mode switch changes its checked state without changing the workspace theme

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `preference control`
- Description: The Dark mode switch handler changes aria-checked and shows an Appearance preference updated toast. The supplied CSS changes the switch track and thumb for its checked state, but the handler does not apply a theme to the page.
- Impact: Users receive confirmation that an appearance preference changed while the workspace theme remains unchanged in the supplied implementation.
- Recommendation: Apply the selected theme when the switch is activated, or clarify that theme changes are not supported.
- Evidence:
  - `settings/index.html:7` — The control is labeled Dark mode and exposed as a switch.
  - `src/settings.js:5` — The switch handler changes aria-checked, and the theme branch displays a toast.
  - `assets/styles.css:2` — The checked-state rules change the switch track and thumb.

### BEH-8BDB8C95 · Orders Export button is not bound to export feedback

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `export interaction`
- Description: The Orders route renders an Export button without the #export-demo selector used by the shared export handler. The Orders module has no export listener, so the supplied source defines no response to this button.
- Impact: Users receive no source-defined indication that an export was requested or is unavailable when they activate the Orders Export button.
- Recommendation: Bind the Orders export control to an appropriate response or make its unavailable state clear.
- Evidence:
  - `orders/index.html:7` — The Orders Export button has no id or inline behavior.
  - `src/app.js:10` — Shared export feedback is bound to #export-demo.
  - `src/orders.js:26` — The Orders module's handlers do not include an export listener.

### BEH-C0A75AE8 · Customer search can leave an empty grid without feedback

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `search feedback`
- Description: The customer input handler hides each card when its name does not match the query. The Customers template has no empty-state or result-count element, and the customer module does not call the shared renderEmpty helper.
- Impact: When a query matches no customer, the cards disappear without an explanation or recovery hint.
- Recommendation: Show a no-matches message when all cards are hidden, and consider exposing result changes to assistive technology.
- Evidence:
  - `src/customers.js:5` — The input handler only toggles each card's hidden property based on the query.
  - `src/components.js:16` — A shared empty-message helper is defined.
  - `customers/index.html:7` — The customer grid contains static cards and no result-count or empty-state element.

### BEH-CA13B36D · Order details dialog lacks source-defined focus management and Escape dismissal

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `dialog keyboard interaction`
- Description: The View handler fills and reveals the element marked as an aria-modal dialog but does not move focus into it or constrain focus to its controls. The shared Escape listener only closes the mobile menu. The dialog's close and confirm handlers hide it without restoring focus to the invoking View button.
- Impact: Keyboard users may remain focused on content behind the visible dialog and must navigate to its controls themselves; Escape does not dismiss it.
- Recommendation: Move focus into the dialog when it opens, manage keyboard focus within it, close it on Escape, and restore focus to the invoking View button when it closes.
- Evidence:
  - `src/orders.js:17` — The row handler reveals the dialog without moving or trapping focus; the close and confirm handlers hide it.
  - `src/app.js:8` — The document Escape listener calls setMenu(false) only.
  - `orders/index.html:7` — The order details element is marked role=dialog and aria-modal=true.

### BEH-D8F2243A · Orders table is likely to overflow its container on narrow screens

- Severity: **medium**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive touch usability`
- Description: The shared table shell enables horizontal scrolling, but the Orders-specific rule changes its overflow to visible while the table has a minimum width of 870px. This makes page-width overflow likely at narrow viewport widths, but the effect was not rendered or measured.
- Impact: If the inferred overflow occurs on a phone, users may need to pan the page to reach later columns, making surrounding content harder to navigate by touch.
- Recommendation: Preserve horizontal scrolling on the table shell at narrow widths or reflow the table; verify the result in a mobile browser.
- Evidence:
  - `assets/styles.css:2` — The shared table-shell rule sets overflow-x:auto.
  - `assets/styles.css:4` — The Orders override sets overflow:visible and the table min-width to 870px.

### BEH-E3892C71 · Focus indicators are removed from shared navigation, icon buttons, and search inputs

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `keyboard focus visibility`
- Description: The stylesheet explicitly removes :focus-visible outlines from navigation links and icon buttons, and removes the outline from search-box inputs. No alternate focus treatment for these selectors is defined in the supplied stylesheet. The shared navigation and icon buttons occur across routes; search inputs are present on Customers and Orders.
- Impact: Keyboard users may have difficulty identifying the currently focused shared navigation or icon control, and the search inputs lack a stylesheet-defined focus boundary.
- Recommendation: Add a visible focus treatment for the shared links and buttons, and a visible focus-within treatment for search boxes.
- Evidence:
  - `assets/styles.css:2` — The search-box input has outline:0 and no focus-specific treatment is defined for it in the stylesheet.
  - `assets/styles.css:6` — The :focus-visible rule explicitly sets outline:none on navigation links and icon buttons.
  - `customers/index.html:7` — The Customers route contains a search-box input.
  - `orders/index.html:7` — The Orders route contains a search-box input.

### BEH-E523129F · Settings contact row is likely to exceed narrow viewport widths

- Severity: **medium**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive form usability`
- Description: The Settings contact row has a 720px minimum width. The mobile media query changes the form row to one column but does not reset that minimum width. This likely causes horizontal overflow at narrow widths; the effect was not rendered or measured.
- Impact: If the inferred overflow occurs on a phone, completing the contact and region fields may require horizontal panning.
- Recommendation: Reset the fixed minimum width at the mobile breakpoint so the fields can fit the available content width; confirm on a narrow viewport.
- Evidence:
  - `assets/styles.css:4` — The Settings-specific fixed field row has min-width:720px.
  - `assets/styles.css:9` — The mobile rule changes the form-row grid but leaves the minimum width unchanged.

### BEH-F39BAAFE · Orders column, bulk, saved-filter, date-range, and archive buttons have no handlers

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `order management interaction`
- Description: The Orders page presents Columns, Bulk actions, Saved filters, Date range, and Archive as buttons. The Orders module binds search, status, table-row, dialog, and New order interactions, but no handlers for these toolbar controls are defined in the supplied source.
- Impact: Users cannot configure the table, apply the presented filters, run bulk actions, or archive records through these controls based on the supplied source.
- Recommendation: Implement the represented actions or make unsupported controls clear; provide an explicit confirmation if Archive is intended to perform a destructive action.
- Evidence:
  - `orders/index.html:7` — The heading actions and toolbar render the named controls as buttons.
  - `src/orders.js:16` — The route module binds search and status, row/dialog, and New order interactions.
  - `src/orders.js:26` — The final route handler provides New order feedback; no toolbar handler is defined in the module.

### BEH-FE228712 · Overview chart period button has no source-defined effect

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `time range interaction`
- Description: The Overview revenue panel presents Last 6 months as a button, but the shared app module contains no handler for this control and the chart data is static in the supplied page source.
- Impact: Users may expect the displayed period to change, but the supplied source defines no response to this button.
- Recommendation: Make the button update the displayed period or present the fixed period as non-interactive text.
- Evidence:
  - `index.html:7` — The revenue panel presents Last 6 months as a button.
  - `src/app.js:10` — The shared handlers bind the menu, notifications, and export selector; no chart-period handler is defined.


## Evidence and limitations

- Audit status is incomplete. Required specialist `frontend_visual_auditor` did not complete both structured passes.
- Review partial findings, correct the listed evidence or backend gaps, then retry with: frontend-director audit --project /private/tmp/frontend-director-benchmark-20261114/demo-app --url http://127.0.0.1:8765/ --depth deep --codex
- No project build, test, or dependency-lifecycle scripts were executed; browser navigation did run the frontend page scripts.
- LCP, INP, CLS, and bundle-size measurements were not collected. Browser navigation timing and request data are single-run lab observations; the automated capture did not activate controls.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.
- frontend_visual_auditor first pass failed for /analytics/: BackendFailure: Codex exited with status 1: ERROR: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 3:34 PM.
ERROR: You’ve hit your usage limit.
- frontend_visual_auditor first pass failed for /customers/: BackendFailure: Codex exited with status 1: ERROR: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 3:34 PM.
ERROR: You’ve hit your usage limit.
- frontend_visual_auditor first pass failed for /orders/: BackendFailure: Codex exited with status 1: ERROR: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 3:34 PM.
ERROR: You’ve hit your usage limit.
- frontend_visual_auditor first pass failed for /settings/: BackendFailure: Codex exited with status 1: ERROR: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 3:34 PM.
ERROR: You’ve hit your usage limit.
- Cross-screen visual synthesis failed; per-route screenshot assessments were retained: BackendFailure: Codex exited with status 1: ERROR: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 3:34 PM.
ERROR: You’ve hit your usage limit.

## Suggested next steps

- Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
- Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
- Replace the user-controlled Settings toast HTML path with text-safe rendering.
- Make modal focus behavior and keyboard focus indicators explicit for the affected controls.
- Remove the narrow-screen minimum widths or contain their overflow within the affected components.
- Make the Analytics cutoff derive its count from a defined dataset and keep save feedback consistent with the final result.
- Use text rendering for the workspace name in toast messages and make save feedback agree with the final simulated outcome.
- Calculate the Analytics qualified-order count from a defined dataset, and align the Dark mode control behavior with its label.
- Manage focus for the Orders dialog and provide authored focus indicators; keep closed mobile navigation out of keyboard navigation.
- Review the Orders table, Analytics chart frame, and Settings contact row minimum widths at narrow viewports; overflow remains unverified without rendering.
- Choose a single customer-directory data source and add a reduced-motion override for the live status beacon.
- Restore visible keyboard focus styling for navigation, icon buttons, and search fields, and give the order dialog a complete focus and Escape-key flow.
- Add customer-search empty-state feedback and wire or clearly disable the customer toolbar and card actions that currently have no response.
- Connect route-specific export and order-management controls to behavior or clear unavailable states; replace static chart-period controls with non-interactive labels if they are fixed.
- Make settings success/failure feedback consistent with the final save outcome and ensure the Dark mode control changes the page theme or communicates its limitation.
- Preserve horizontal table scrolling and let the settings fields reflow on narrow screens; confirm the source-derived responsive risks in a browser when runtime inspection is allowed.
- Restore visible keyboard focus cues on the shared navigation, icon buttons, and search boxes.
- Add keyboard focus management and Escape dismissal to the Orders details dialog.
- Provide explicit no-results feedback for customer search and source-defined responses for the visible customer and Orders toolbar controls.
- Make Settings save feedback reflect the simulated outcome before announcing success.
- Verify the Orders table and Settings contact row at narrow viewports before treating the inferred overflow as confirmed.
- Consider whether mobile users should see trend context sooner; if so, evaluate a more compact KPI presentation while preserving the current card readability.
- Preserve the coherent navy, pale-canvas, white-card, and teal treatment visible across the three supplied widths.
- Treat earlier mobile access to trend and activity context as a product-priority decision; the supplied evidence supports the current KPI-first order but also shows its first-viewport cost.
