# Technical and architecture audit

Audit backend: `codex_cli_plus_static`

## Evidence-backed specialist assessment

### frontend_code_auditor · first_pass

Source observations: This is a dependency-free, multi-page HTML/CSS/JavaScript fixture. Each route duplicates the application shell and loads `src/app.js`; feature routes also load a route-specific module. Shared JavaScript is limited to helpers in `src/components.js`. The orders route imports the order fixture and renders its table into the DOM. The customers page instead filters cards already present in its HTML; `src/customers.js` imports the customer fixture but does not use it. Analytics uses inline chart markup and a small route module, while settings keeps its state in DOM attributes and form fields. The included code shows no asynchronous data loading or backend path, so there is no loading lifecycle to assess.

Rendered observations: None. No rendered evidence or screenshots were supplied, so appearance and actual browser interaction outcomes were not observed.

Measurements: None. No project code, scripts, tests, builds, servers, or dependency managers were executed. Static source indicates that order search filters the fixture and rebuilds the table on each input event; the included fixture has eight orders, so this code alone provides no evidence of a performance problem at fixture scale or at larger scale.

Inferences: The analytics cutoff, settings save feedback, modal keyboard handling, and narrow-width layout issues below are based on source paths only. Their runtime effects were not verified in a browser.

Evidence:
- `README.md:3` — Describes a five-page offline fixture with synthetic data and identifies the shared helpers, data fixture, and route interaction modules.
- `index.html:8` — The overview loads the shared app module; the route pages follow the same shell pattern and add their own feature modules.
- `src/app.js:1` — Owns shared menu, Escape-key menu dismissal, notification toast, and overview export handlers.
- `src/orders.js:9` — Imports the order fixture, filters it from search and status controls, and replaces the table body with generated markup.
- `src/data.js:1` — Defines local order and customer fixtures and a USD formatter; no service or API client is present in this file.
- `src/customers.js:1` — The customer module imports the fixture but filters existing `.customer-card` DOM nodes rather than rendering from that data.
- `analytics/index.html:7` — The analytics route contains its chart markup and cutoff control in the page document.
- `src/analytics.js:5` — The cutoff handler updates the label and chooses between two fixed counts; it does not import a data fixture.
- `src/settings.js:3` — Settings interactions update DOM attributes and text and schedule a simulated save result; no persistence client is imported.
- `tests/smoke.test.mjs:3` — The supplied tests assert fixture length and currency formatting only; no interaction or route behavior is covered in this file.
- `assets/styles.css:6` — Contains the shared layout, focus, animation, and responsive rules, including route-specific minimum widths.

Pass-scoped limitations:
- No screenshots or rendered evidence were supplied, so no visual appearance claims or browser-observed behavior are included.
- No project code, commands, tests, builds, servers, dependency managers, or network requests were executed.
- Responsive effects and dialog interaction outcomes are inferred from static source and were not measured.
- The supplied test source was inspected only; its assertions cover fixture existence and money formatting, not the reported interaction paths.

### frontend_code_auditor · cross_validation

Source observations: The supplied source describes a five-page, offline static fixture with synthetic data. The shared `src/app.js` handles menu and notification behavior; `src/components.js` provides rendering helpers, and feature routes load their own modules. The orders module filters fixture data and renders table rows. The customers module imports customer data but filters cards already in the page. Analytics includes static chart markup and updates its qualified-order count using a two-bucket cutoff rule. Settings toggles switch attributes and simulates save feedback in the DOM. The included source shows no backend or remote-data client. The supplied smoke tests assert fixture presence and currency formatting only.

Rendered observations: None. No screenshots or browser-observed interaction results were supplied.

Measurements: None. No project code, scripts, tests, builds, servers, dependency managers, or network requests were run. No viewport measurements were made.

Inferences: The possible markup execution from the workspace-name input, the timing overlap between settings feedback, dialog keyboard behavior, the dark-mode effect, and narrow-screen overflow are assessed from source only. Their browser effects were not verified.

Evidence:
- `README.md:3` — Identifies the project as an offline, five-page static fixture with synthetic data and lists the shared helpers, data fixture, and route interaction modules.
- `index.html:8` — The overview loads the shared application module.
- `orders/index.html:8` — The orders route loads the shared application module and its route-specific module.
- `src/app.js:5` — Contains shared menu, Escape-key menu dismissal, notification, and overview export handlers.
- `src/components.js:2` — Exports shared rendering helpers.
- `src/orders.js:9` — Filters imported order fixtures by search and status, then replaces the table body with generated rows.
- `src/customers.js:1` — Imports customer fixture data but filters customer cards already present in the document.
- `src/analytics.js:5` — Updates the displayed qualified-order count using a single cutoff comparison between two fixed values.
- `src/settings.js:4` — Changes switch attributes and simulates save status in the DOM, including a delayed failure for qualifying thresholds.
- `tests/smoke.test.mjs:3` — The supplied tests check order fixture presence and USD formatting.

Pass-scoped limitations:
- No screenshots or rendered evidence were supplied, so appearance and browser-observed behavior were not assessed.
- No project code, scripts, tests, builds, servers, dependency managers, or network requests were executed.
- The responsive overflow findings are hypotheses from CSS declarations; viewport behavior was not measured.
- The interaction, timing, and security findings are static source analyses and were not verified in a browser.

## Findings

### TECH-052F191D · Analytics chart frame retains a 680px minimum width at narrow breakpoints

- Severity: **medium**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive-layout`
- Description: The analytics chart frame has a 680px minimum width. The narrow breakpoint collapses `.layout-2` to one column but does not reset that minimum or add horizontal scrolling to the chart frame. The source supports a risk that the chart or its grid track exceeds the available content width; no rendered viewport evidence was supplied.
- Impact: At narrow widths, the chart region may exceed its content area and cause horizontal overflow.
- Recommendation: Allow the chart frame to shrink at narrow widths or place the fixed-width chart inside a horizontally scrollable region.
- Evidence:
  - `analytics/index.html:7` — The chart frame is nested inside the analytics layout.
  - `assets/styles.css:4` — The analytics chart frame has a 680px minimum width.
  - `assets/styles.css:9` — The narrow breakpoint changes `.layout-2` to one column but does not change the chart frame minimum width.

### TECH-1784E484 · Focus-visible outlines are removed from shared navigation and icon buttons

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `accessibility/focus-indicator`
- Description: The shared stylesheet sets `outline:none` for `:focus-visible` on `.nav-link` and `.icon-button`, without defining a replacement focus indicator in that rule. These classes appear in the shared navigation and top bar across routes.
- Impact: Keyboard users may not have a visible focus location while moving among these shared controls.
- Recommendation: Add a visible `:focus-visible` outline or equivalent focus treatment for `.nav-link` and `.icon-button`.
- Evidence:
  - `assets/styles.css:6` — The shared focus-visible selector removes outlines from navigation links and icon buttons.
  - `index.html:5` — The overview contains shared navigation links and top-bar icon buttons that match the selector.
  - `index.html:6` — The top bar includes an icon button affected by the selector.

### TECH-208AC267 · Order details dialog does not move or constrain keyboard focus

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `accessibility/modal-keyboard`
- Description: Opening an order makes the dialog overlay visible but does not move focus into the dialog. The close handlers only hide it, and the shared Escape-key handler closes the navigation menu without closing the dialog. The dialog is marked `aria-modal="true"`, but the included code does not keep keyboard focus within it or restore focus to the triggering order button.
- Impact: Keyboard users can continue navigating controls behind the visible modal, and Escape does not dismiss it.
- Recommendation: Move focus into the dialog on open, constrain focus while it is open, close it on Escape, and restore focus to the triggering View button.
- Evidence:
  - `orders/index.html:7` — The order preview is marked as a modal dialog and contains Close and Open record buttons.
  - `src/orders.js:17` — The delegated row click handler displays the dialog without moving focus.
  - `src/orders.js:21` — The dialog is made visible, and its close controls only hide it.
  - `src/app.js:8` — The Escape-key handler only calls the navigation-menu close function.

### TECH-389C8841 · Orders table minimum width is not contained by its scroll wrapper

- Severity: **medium**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive-layout`
- Description: The shared `.table-shell` uses horizontal overflow handling, but the orders-specific rule overrides it with `overflow:visible` while setting the table's minimum width to 870px. The narrow breakpoint does not override these orders-specific declarations. This supports a risk of page-level horizontal overflow on narrow screens; the actual rendered effect was not measured.
- Impact: The table can extend beyond the content width instead of scrolling within its wrapper on narrow screens.
- Recommendation: Keep horizontal scrolling on the orders table wrapper at narrow widths, or use a narrow-screen table treatment that contains the table's minimum width.
- Evidence:
  - `assets/styles.css:2` — The shared table wrapper declares horizontal overflow handling.
  - `assets/styles.css:4` — The orders route changes the wrapper overflow to visible and sets the table minimum width to 870px.
  - `assets/styles.css:9` — The narrow breakpoint does not reset the orders table width or wrapper overflow.

### TECH-4253843F · Dark mode switch changes state without changing the page theme

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `interaction-state`
- Description: The settings handler toggles `aria-checked` on the switches. For `theme-switch`, it also displays a toast, but the included handler does not apply a page theme class or attribute. The settings page describes the switch as Dark mode and says it uses darker surfaces at night; the stylesheet changes the switch control's checked styling but does not define a dark page theme.
- Impact: The switch indicates that dark mode is enabled while the page surfaces remain governed by the light theme styles.
- Recommendation: Apply a page theme state with corresponding surface styles, or describe the control as a simulated preference if that is the intended demo behavior.
- Evidence:
  - `settings/index.html:7` — The control is labeled Dark mode and its description promises darker surfaces.
  - `src/settings.js:5` — The handler changes the switch's `aria-checked` attribute and shows a toast for the theme switch.
  - `src/settings.js:6` — The theme branch shows a toast but applies no theme state.
  - `assets/styles.css:4` — The checked switch state changes the control's appearance.

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

### TECH-6F91CC80 · Workspace name is parsed as HTML in the save toast

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `security/dom-xss`
- Description: The settings form accepts an editable workspace name, and its submit handler interpolates that value into a toast message. The shared toast helper assigns the message to `innerHTML`, so the value is parsed as markup. A crafted value containing active markup may execute in the submitting page, subject to browser security policy. The supplied source does not show persistence or another user's ability to supply this value, so the evidenced input path is limited to the current session.
- Impact: A crafted workspace name may introduce active markup into the current page. Cross-user or stored execution is not established by the included source.
- Recommendation: Render the workspace name as text. If the toast needs bold text, keep the markup static and insert the name as a text node.
- Evidence:
  - `settings/index.html:7` — The workspace name is an editable required input.
  - `src/settings.js:13` — The submit handler reads the workspace-name value and interpolates it into the toast message.
  - `src/settings.js:18` — The interpolated message is passed to the toast helper.
  - `src/components.js:8` — The toast helper assigns its message to `innerHTML`.

### TECH-D31452AF · Settings form row retains a 720px minimum width on mobile

- Severity: **medium**; confidence: **medium**; verification: `hypothesis`
- Category: `responsive-layout`
- Description: The settings form's `.fixed-field-row` has a 720px minimum width. At the narrow breakpoint the row changes to a one-column grid, but its minimum width remains. The source supports a risk that the row exceeds its panel or the available page width; no rendered layout was measured.
- Impact: The settings form row may extend beyond its panel at narrow widths.
- Recommendation: Reset the row's minimum width at the narrow breakpoint so its one-column layout can fit the available panel width.
- Evidence:
  - `settings/index.html:7` — The settings form contains the fixed-field row for contact email and region.
  - `assets/styles.css:4` — The settings-specific row sets a 720px minimum width.
  - `assets/styles.css:9` — The narrow breakpoint changes the settings form row to one column but leaves its minimum width in place.

### TECH-DE0DE4CC · Settings can show success feedback alongside a simulated save failure

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `reliability/save-feedback`
- Description: On submission, the handler immediately sets the status to `Saved successfully` and shows a success toast. For thresholds above 80,000, the status changes to `Sync failed; your changes were not stored` after 450 ms. The toast helper keeps the toast visible for 3.2 seconds unless another toast replaces it, so the success toast can remain while the failure status is shown. This timing conflict is inferred from source; it was not observed in a browser.
- Impact: During the toast's remaining display time, users may see a success message and a failure status at once.
- Recommendation: Show success only after the save outcome is known, or replace and clear the success toast when the failure status is set.
- Evidence:
  - `settings/index.html:7` — The form copy identifies values above 80,000 as a simulated failed save.
  - `src/settings.js:16` — The handler immediately sets the status to success and displays the save toast.
  - `src/settings.js:20` — For thresholds above 80,000, the status changes to failure after 450 ms.
  - `src/components.js:9` — The toast is hidden after a 3.2-second timer.

### TECH-FD057A39 · Analytics cutoff updates the count using a fixed two-bucket rule

- Severity: **low**; confidence: **medium**; verification: `static_analysis`
- Category: `data-integrity`
- Description: The analytics page says the cutoff filters the summary metric, but the handler displays `286` for every cutoff up to 40,000 and `11` above 40,000. It imports no analytics dataset and does not count records. The page is also identified as a fictional demo, so whether this is a defect depends on whether the control is intended to demonstrate a functional filter or an illustrative response.
- Impact: If users are meant to interpret the value as a filtered count, most cutoff changes do not produce a count derived from records.
- Recommendation: If the metric is meant to function as described, calculate it from an analytics dataset. If it is illustrative, label the control and count as a demo behavior.
- Evidence:
  - `analytics/index.html:7` — The slider is labeled as a minimum order value and the page says the cutoff filters the summary metric.
  - `src/analytics.js:1` — The module imports only money formatting and the toast helper, not an analytics dataset.
  - `src/analytics.js:5` — The count is selected by one 40,000 comparison between two fixed strings.


## Evidence and limitations

- No project build, test, or dependency-lifecycle scripts were executed; browser navigation did run the frontend page scripts.
- LCP, INP, CLS, and bundle-size measurements were not collected. Browser navigation timing and request data are single-run lab observations; the automated capture did not activate controls.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- 

## Suggested next steps

- Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
- Use text-only toast rendering for user-provided values.
- Calculate the analytics qualified-order metric from a defined dataset.
- Make settings save feedback reflect the final simulated result.
- Complete keyboard focus handling for the order dialog and restore a visible focus indicator to shared controls.
- Reset route-specific minimum widths or keep overflow within dedicated scroll containers at narrow viewports.
- Render the settings workspace name as text in toast content while keeping any required emphasis markup static.
- Clarify whether the analytics cutoff is illustrative or should count records, then match the displayed behavior to that intent.
- Ensure settings success and failure feedback cannot remain visible together.
- Manage focus entry, containment, Escape dismissal, and restoration for the order dialog.
- Provide visible focus styling for shared navigation links and icon buttons.
- Either implement a page theme for Dark mode or identify the setting as simulated.
- Contain the orders table's minimum width within a local horizontal scroller or another narrow-screen treatment.
- Let the analytics chart frame fit narrow content or contain its minimum width in a scrollable region.
- Remove or reset the settings form row's 720px minimum width at the narrow breakpoint.
- Restore visible focus indicators for navigation and icon buttons, and make closed mobile navigation links unavailable to keyboard focus.
- Give the order dialog a complete keyboard focus and dismissal flow, including focus entry, containment, Escape dismissal, and focus restoration.
- Add a customer-search empty state and implement or clearly disable the customer and orders toolbar controls that currently have no handlers.
- Derive the analytics qualified-order count from data or disclose the coarse simulated metric behavior.
- Keep settings feedback truthful: do not announce save success until the simulated operation completes, apply or accurately describe switch effects, and render the workspace name as text.
- Remove the fixed minimum width from the settings form row at narrow breakpoints.
- Make export/download feedback match whether a file was actually created.
- Add visible focus treatment to shared navigation and icon buttons, and remove the closed mobile sidebar from keyboard navigation.
- Complete the order dialog focus lifecycle and add no-matches feedback to customer search.
- Implement the advertised customer and order toolbar actions or clearly identify controls unavailable in the demo.
- Align settings and analytics feedback with the state the controls actually apply or the artifact they actually create.
- Remove the settings row's fixed minimum width at narrow viewports.
- Adjust the analytics layout breakpoint so both panels fit within the tablet content width.
- Remove the chart frame's forced minimum width on mobile or make its horizontal scrolling explicit and contained.
- Keep the desktop title hierarchy, neutral surfaces, teal data accents, and spacious side-by-side panel layout.
- Stack the analytics panels at tablet widths to keep both panels in view.
- At mobile widths, choose between fitting the chart to its panel and providing a clearly indicated scroll region.
- Preserve the existing responsive change from three to two to one customer-card columns.
- Review whether the sharper corners on the Morgan Ellis card are a deliberate exception; align them with the other cards if not.
- Confirm the purpose of the second-card radius exception; otherwise use the shared customer-card radius.
- Refine the narrow-width order table so the fields and row action are discoverable within the viewport, choosing between horizontal scrolling and a stacked row layout based on whether preserving table density or at-a-glance visibility is more important.
- Refine the narrow-width table presentation so later order fields and row actions can be reached without relying on the table extending past the visible viewport.
- Let `.fixed-field-row` shrink within its card or switch to a single-column layout at widths where the row no longer fits; verify that the card edges and controls remain inside the viewport.
- Reset the fixed minimum width when the settings layout stacks, then confirm the form and cards fit within the tablet and mobile viewports.
