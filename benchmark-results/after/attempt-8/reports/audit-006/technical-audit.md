# Technical and architecture audit

Audit backend: `codex_cli_plus_static`

## Evidence-backed specialist assessment

### frontend_code_auditor · first_pass

Source observations: The frontend is a dependency-free collection of standalone HTML routes using native links, one global stylesheet, a shared navigation/toast module, and route-specific JavaScript modules. The Orders route renders and filters a fixed fixture; the Settings route keeps its simulated form and switch state in the DOM; the Customers route contains static customer-card markup while its module imports but does not use the exported customer fixture. No service layer or external data loading path is present in the included source. The supplied smoke tests cover fixture presence and currency formatting, not route interactions. Rendered observations: None; no screenshots or rendered evidence were supplied. Measurements: None; no browser, runtime, build, or performance measurements were performed. Inferences: The fixed, small local fixture and lack of asynchronous loading provide no source evidence of a performance bottleneck, so no performance defect is asserted. Several narrow-screen overflow findings below are inferred from CSS minimum widths and overflow rules and were not rendered. Hypotheses: Actual viewport behavior and dynamic interaction outcomes remain unverified.

Evidence:
- `package.json:5` — The manifest declares an ES module package and dev/test scripts, with no dependencies listed.
- `index.html:5` — The overview route uses native page links and loads the shared application module at the end of the document.
- `orders/index.html:8` — The Orders route loads the shared module and its route-specific module as separate page modules.
- `src/orders.js:9` — The Orders page filters imported fixed records and rebuilds the table body in response to search or status changes.
- `src/customers.js:1` — The Customers module imports the customer fixture but operates on customer cards already present in the document.
- `tests/smoke.test.mjs:4` — Included tests assert fixture presence and currency formatting only.

Pass-scoped limitations:
- No screenshots or rendered evidence were supplied, so no visual observations are reported.
- No browser, runtime, build, dependency manager, or network request was used; dynamic behavior is assessed from source only.
- Responsive overflow and other user-visible effects are source-based inferences, not measured viewport results.
- No performance measurements were taken; no performance defect is asserted from the included source alone.

### frontend_code_auditor · cross_validation

Source observations: The snapshot contains five standalone HTML routes, a shared stylesheet, shared UI helpers, and route-specific JavaScript modules. The manifest declares ES modules and lists no dependencies. Orders filters fixed local records; the Settings form updates its status and switch state in the DOM; Customers renders cards authored in HTML while its module imports but does not use the customer fixture. The included tests check fixture presence and currency formatting. I found no external data-loading calls in the included source. Rendered observations: None; no screenshots or rendered artifacts were supplied. Measurements: None; no runtime, browser, build, or performance measurements were performed. Inferences: Source supports the security, feedback, data-flow, and accessibility findings below. Narrow-screen overflow is inferred from CSS minimum widths and overflow rules. Hypotheses: Whether those width constraints cause page-level overflow at particular viewport sizes remains unverified.

Evidence:
- `package.json:5` — The manifest declares the package as ES modules and lists dev/test scripts; it contains no dependencies section.
- `index.html:5` — The overview page contains native route links and loads the shared application module.
- `src/orders.js:9` — The Orders module filters imported fixture records and rebuilds the table body when search or status changes.
- `src/customers.js:1` — The customer fixture is imported but search operates on customer cards already in the document.
- `tests/smoke.test.mjs:3` — The included tests assert fixture presence and currency formatting.

Pass-scoped limitations:
- No screenshots or rendered evidence were supplied, so visual findings and viewport-specific outcomes could not be confirmed.
- No project scripts, builds, servers, dependency managers, or network requests were run.
- Findings are based on the supplied source snapshot; dynamic browser behavior and assistive-technology behavior were not exercised.
- The responsive overflow findings are hypotheses from CSS minimum widths and overflow settings, not measured viewport results.
- No performance measurements were taken, and no performance defect is asserted.

## Findings

### TECH-18FF96ED · The Settings failure status conflicts with the still-visible save toast

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `reliability`
- Description: The handler immediately sets the status to “Saved successfully” and shows a toast reading “Saved preferences for …”. For thresholds above 80,000, it changes the status to “Sync failed; your changes were not stored” after 450 ms. The toast helper leaves the earlier message visible for 3,200 ms. The page help text describes this simulated failure sequence, but during the remaining toast time the feedback still suggests the preferences were saved.
- Impact: Users can see a save confirmation at the same time as a status saying their changes were not stored.
- Recommendation: When the simulated failure is reported, replace or dismiss the success toast and make the status text distinguish acknowledgement from completed saving.
- Evidence:
  - `src/settings.js:16` — The save status is set to success before the simulated failure check.
  - `src/settings.js:19` — For thresholds above 80,000, the handler sets a failure status after 450 ms.
  - `src/components.js:9` — The toast is hidden after 3,200 ms, so the original success message remains visible after the failure status is set.
  - `settings/index.html:7` — The field help text describes the simulated failure after a successful acknowledgement.

### TECH-28C8FDB3 · Workspace name is parsed as HTML in the Settings toast

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `security`
- Description: On /settings/, the submit handler reads the editable workspace name, interpolates it into a toast message, and passes that message to a helper that assigns it to innerHTML. A crafted value can therefore be parsed as markup in the page. The included source shows no external or persisted input path; the demonstrated entry point is a user submitting a value in the current page.
- Impact: The current form provides a DOM markup-injection path. The supplied source does not establish a remote attacker or persistence path.
- Recommendation: Render the workspace name as text. If the message needs bold formatting, create the strong element explicitly and set the name through textContent.
- Evidence:
  - `src/settings.js:13` — The handler reads the workspace name from the editable input and inserts it into the toast template.
  - `src/settings.js:18` — The interpolated message is sent to toast on form submission.
  - `src/components.js:8` — The toast helper assigns the supplied message to innerHTML.

### TECH-3AEF02E8 · The animated live status beacon has no reduced-motion override

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `accessibility`
- Description: The shared live-beacon status dot runs an infinite 1.4-second animation. The included stylesheet has responsive media queries but no prefers-reduced-motion rule to suppress or reduce the animation.
- Impact: People who request reduced motion have no author-provided stylesheet override for this repeated animation.
- Recommendation: Add a reduced-motion rule for the live-beacon animation.
- Evidence:
  - `assets/styles.css:6` — The live beacon runs an infinite breathe animation.
  - `assets/styles.css:7` — The included media queries address viewport breakpoints; no reduced-motion override is present.
  - `index.html:6` — The overview route uses the animated status dot in the shared topbar.
  - `orders/index.html:6` — The Orders route uses the animated status dot in the topbar.
  - `customers/index.html:6` — The Customers route uses the animated status dot in the topbar.
  - `analytics/index.html:6` — The Analytics route uses the animated status dot in the topbar.
  - `settings/index.html:6` — The Settings route uses the animated status dot in the topbar.

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

### TECH-4B63B15E · The customer fixture is imported but the directory is driven by HTML cards

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `state ownership`
- Description: The Customers page authors customer records directly as card markup. Its module imports the customer fixture but does not reference it; search filters existing cards by their data-customer attributes. Changes to the imported fixture therefore do not update the page's cards, leaving two representations that can drift.
- Impact: Maintainers can update the exported fixture without changing the directory, and the two representations can diverge.
- Recommendation: Choose one customer source: render the cards from the fixture or remove the unused import and keep the HTML as the explicit source.
- Evidence:
  - `src/data.js:12` — The shared module exports a customer fixture.
  - `src/customers.js:1` — The customer fixture is imported, while search selects existing customer cards.
  - `src/customers.js:7` — Search filters cards using their data-customer attributes.
  - `customers/index.html:7` — Customer records are authored directly as repeated card markup.

### TECH-5742E2FF · The Dark mode switch changes state without applying a dark theme

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `interaction`
- Description: On /settings/, the shared switch handler toggles aria-checked for switches and shows an “Appearance preference updated” toast for theme-switch. The included stylesheet defines a light root palette and switch-state styling, but no dark-theme selector or theme application is present in the supplied source.
- Impact: Users receive state-change and confirmation feedback without a corresponding appearance change in the supplied implementation.
- Recommendation: Apply a dark theme when the switch changes, or revise the control and toast copy so they do not claim an appearance preference was updated.
- Evidence:
  - `settings/index.html:7` — The control is labeled Dark mode and its accompanying copy refers to darker surfaces.
  - `src/settings.js:5` — The handler toggles aria-checked and shows a toast for theme-switch.
  - `assets/styles.css:1` — The stylesheet defines the page palette at :root and switch-state styling without a dark-theme selector.

### TECH-624B8775 · The Orders table can overflow its shell on narrow screens

- Severity: **medium**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive layout`
- Description: The base table shell enables horizontal scrolling, but the Orders-specific rule changes its overflow to visible while the table has a minimum width of 870 px. This allows the table to extend beyond its shell at narrower widths. Page-level overflow at a given viewport is inferred from the CSS and was not rendered.
- Impact: On narrow screens, users may need to scroll the page horizontally to reach table content rather than scrolling within the table shell.
- Recommendation: Keep horizontal scrolling on the table shell at narrow widths or provide a table layout that fits the available content width.
- Evidence:
  - `assets/styles.css:2` — The base table shell enables horizontal overflow scrolling.
  - `assets/styles.css:4` — The Orders override sets shell overflow to visible and table min-width to 870 px.
  - `orders/index.html:7` — The Orders route places its table inside a table-shell.

### TECH-714EFD82 · The analytics cutoff changes the count through a hardcoded threshold

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `data correctness`
- Description: The Analytics page describes the cutoff as filtering the summary metric. Its handler displays 286 for values up to 40,000 and 11 above 40,000. The module imports the money formatter and toast but no order collection, so the included source does not calculate the qualified count from order records.
- Impact: The displayed qualified-order count is not computed from the included order records and only changes at one cutoff boundary.
- Recommendation: Calculate the count from an explicit analytics dataset and the selected cutoff, or revise the control copy to describe the two-value demo mapping.
- Evidence:
  - `analytics/index.html:7` — The page says the cutoff filters the summary metric and exposes a $1–$100,000 range.
  - `src/analytics.js:5` — The displayed count switches between two literal values at a 40,000 boundary.
  - `src/analytics.js:1` — The module imports money and toast, not an order collection.
  - `src/data.js:2` — The included shared order collection contains eight fixed records.

### TECH-85739D51 · The Analytics chart frame retains a 680 px minimum width

- Severity: **medium**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive layout`
- Description: The Analytics-specific chart frame has min-width:680px. The responsive rules collapse the surrounding grid but do not change that minimum width or introduce a scroll container for the frame. Overflow at specific viewports is inferred from CSS and was not rendered.
- Impact: The chart frame may extend beyond the available mobile content width.
- Recommendation: Remove or reduce the fixed minimum width at narrow breakpoints, or provide a deliberate horizontal scroll container for the chart.
- Evidence:
  - `assets/styles.css:4` — The Analytics chart frame has a 680 px minimum width.
  - `assets/styles.css:9` — The responsive rules collapse grids but do not override chart-frame sizing.
  - `analytics/index.html:7` — The chart frame contains the revenue-by-channel SVG.

### TECH-8716C62C · The visually closed mobile sidebar remains keyboard-focusable

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `accessibility`
- Description: At widths up to 800 px, the stylesheet moves the closed sidebar offscreen with a transform. The shared menu handler toggles its open class and aria-expanded, but does not hide or make the closed sidebar inert. Its navigation links remain in the document's sequential focus order.
- Impact: At mobile widths, keyboard focus can move to navigation links while the sidebar is visually offscreen.
- Recommendation: Synchronize the closed menu state with inert or another mechanism that removes the sidebar links from sequential focus, then restore their focusability when opened.
- Evidence:
  - `assets/styles.css:8` — The mobile breakpoint moves the closed sidebar offscreen and reveals it with the open class.
  - `src/app.js:5` — Menu state changes the sidebar and backdrop classes and aria-expanded only.
  - `index.html:5` — The sidebar contains the route navigation links.

### TECH-8F46F764 · Authored focus outlines are suppressed on navigation, icon buttons, and search inputs

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `accessibility`
- Description: The stylesheet sets outline:none for focused navigation links and icon buttons, and outline:0 for search inputs. It contains no focus-visible or focus-within replacement for these selectors. The shared navigation and icon buttons appear across the routes; search inputs are present on Orders and Customers.
- Impact: Keyboard users may have no authored visual indicator for focus on these controls.
- Recommendation: Add a visible focus treatment for these controls, including a focus-within treatment for the search box if its child outline remains suppressed.
- Evidence:
  - `assets/styles.css:2` — Search inputs inside search-box suppress their outline.
  - `assets/styles.css:6` — Focused nav links and icon buttons suppress their focus-visible outline, without a replacement focus selector in the included stylesheet.
  - `orders/index.html:6` — The Orders route includes a search input and shared navigation icon buttons.

### TECH-D66B9BA8 · The Settings contact row retains a 720 px minimum width

- Severity: **medium**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive layout`
- Description: The Settings contact-email/region row uses the fixed-field-row class, whose min-width is 720 px. At the narrow breakpoint, form rows become one column, but this minimum width remains. Overflow at specific viewports is inferred from CSS and was not rendered.
- Impact: The form row may extend beyond narrow content widths and cause horizontal scrolling.
- Recommendation: Remove the minimum width at the narrow breakpoint so the single-column row can fit its container.
- Evidence:
  - `assets/styles.css:4` — The Settings fixed-field row has a 720 px minimum width.
  - `assets/styles.css:9` — The narrow breakpoint changes form rows to one column without overriding the fixed-field minimum width.
  - `settings/index.html:7` — The affected contact email/region row has both form-row and fixed-field-row classes.

### TECH-DC86D393 · The order dialog does not manage keyboard focus

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `accessibility`
- Description: On /orders/, the overlay contains a dialog marked aria-modal=true. Opening it only removes the hidden state; the handler does not move focus into the dialog or contain Tab navigation. The close and confirm handlers hide it without restoring focus, and no dialog-specific Escape handler is present.
- Impact: Keyboard users may remain focused on background content or tab into it while the page declares the dialog modal.
- Recommendation: Move focus into the dialog when it opens, contain focus while it is open, close it on Escape, and restore focus to the triggering View button.
- Evidence:
  - `orders/index.html:7` — The overlay contains a dialog marked aria-modal=true with Close and Open record buttons.
  - `src/orders.js:17` — The dialog is revealed without moving focus.
  - `src/orders.js:24` — Close and confirm hide the dialog without restoring focus or handling Escape.


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
