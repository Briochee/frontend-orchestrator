# Behavior and accessibility audit

Audit backend: `codex_cli_plus_static`

## Evidence-backed specialist assessment

### frontend_ux_auditor · first_pass

Source-only assessment: the five routes use native links for navigation and route-specific JavaScript for local search, filters, a record dialog, settings controls, and toast feedback. The toast and settings save status use live-region semantics. The reviewed handlers contain no request lifecycle; the settings form has a delayed simulated failure. Material interaction gaps include off-screen mobile navigation remaining focusable, incomplete modal focus handling, inert directory and order controls, and feedback that can disagree with the resulting settings state. No rendered appearance or live keyboard, touch, or runtime behavior was verified.

Evidence:
- `index.html:5` — The overview uses native links for route navigation and exposes a mobile menu button and notification button in the shared header.
- `src/app.js:5` — The shared handler toggles the mobile menu, closes it on Escape or backdrop click, and sends notification feedback through a toast.
- `src/components.js:5` — Toast feedback is inserted into a role=status, aria-live element and hidden after a timeout; the shared helper sets its content with innerHTML.
- `src/settings.js:11` — Settings submission updates the live status immediately and may replace it with a sync failure after a delay.

### frontend_ux_auditor · cross_validation

Source-only assessment: the five route files use native links for navigation and share a mobile menu, notification button, and toast region. Route scripts implement local search and filtering, an order details dialog, analytics cutoff feedback, and settings controls. The source supports concerns about off-screen sidebar links remaining focusable, a dialog without focus or Escape handling, removed focus outlines, an unnamed notification button, inert controls, and a few actions whose feedback does not match the resulting behavior. No rendered appearance or live keyboard, touch, or assistive-technology behavior was verified.

Evidence:
- `index.html:5` — The overview uses native links for route navigation and includes the shared sidebar and mobile navigation button.
- `src/app.js:5` — The shared handler toggles the mobile menu, closes it on Escape or backdrop click, and sends notification feedback through a toast.
- `src/orders.js:17` — The order View handler reveals the dialog; its close and confirm handlers hide it.
- `src/settings.js:4` — Settings controls update switch state and submit feedback; the save handler can later replace its success status with a failure.

## Findings

### BEH-10081A3C · Customer search can leave a blank directory when there are no matches

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `empty-state`
- Description: The customer search handler hides cards that do not match the name query but does not display an empty state when every card is hidden. The Customers markup contains the card grid and cards but no customer no-results message.
- Impact: A query with no matching names leaves the directory blank without guidance to revise or clear the search.
- Recommendation: Show a no-matching-customers message when no cards match and provide a clear-search recovery action.
- Evidence:
  - `src/customers.js:5` — Search sets each card's hidden property based on the name query; there is no no-match branch.
  - `customers/index.html:7` — The customer grid contains cards but no customer empty-state element.

### BEH-4BCB6A01 · Customer card “More actions” buttons have no action handler

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `directory-actions`
- Description: Customer cards include buttons titled More actions, but the customer route registers no handler for them. The supplied source contains no menu behavior or feedback for these buttons.
- Impact: Users who try to access customer-specific actions reach a dead end.
- Recommendation: Implement the customer action menu or clearly mark the buttons unavailable in the demo.
- Evidence:
  - `customers/index.html:7` — Customer cards include icon buttons titled More actions.
  - `src/customers.js:9` — The customer script handles search and invitations only; it does not wire card action buttons.

### BEH-4C83DB1A · Orders toolbar buttons have no implemented action or feedback

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `unavailable-actions`
- Description: The Orders toolbar presents Export, Columns, Bulk actions, Saved filters, Date range, and Archive as buttons. The supplied Orders handler does not register behavior for these controls. The New order button does provide an explanatory demo toast, but the toolbar controls do not.
- Impact: Users can activate labeled controls without receiving an action or indication that the controls are unavailable.
- Recommendation: Implement the labeled actions or identify them as unavailable in the demo with concise feedback, using the New order message as an existing pattern.
- Evidence:
  - `orders/index.html:7` — The page presents Export, Columns, Bulk actions, Saved filters, Date range, and Archive as buttons.
  - `src/orders.js:16` — The handler registers search/status filtering, row viewing, dialog actions, and New order feedback, but not the toolbar controls.
  - `src/orders.js:26` — New order has an explicit unavailable-in-demo toast.

### BEH-4E273598 · Analytics Download control reports an export without creating a file

- Severity: **low**; confidence: **medium**; verification: `static_analysis`
- Category: `download-feedback`
- Description: The button is labeled Download, while its handler only displays “Report exported (demo only)” through the toast. The explicit demo-only wording reduces the risk of users interpreting this as a real export, but the supplied handler does not create or download a file.
- Impact: The control's label implies a downloadable report, but activating it does not produce a file.
- Recommendation: Provide a file download or relabel the control and message as a demo preview.
- Evidence:
  - `analytics/index.html:7` — The primary analytics action is labeled Download.
  - `src/analytics.js:7` — The click handler only shows an export toast with explicit demo-only wording.

### BEH-516B1BF7 · Order details dialog does not manage keyboard focus or Escape dismissal

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `modal-focus`
- Description: Opening an order reveals a dialog marked aria-modal=true, but the handler does not move focus into the dialog, contain Tab navigation, close it on Escape, or restore focus to the View button. The shared Escape handler closes only the mobile menu.
- Impact: Keyboard focus can remain behind a dialog that claims to be modal, leaving users to navigate away from the dialog to reach its controls.
- Recommendation: Move focus into the dialog when it opens, manage focus while it is open, close it on Escape, and return focus to the specific View button that opened it.
- Evidence:
  - `orders/index.html:7` — The order overlay contains a dialog marked aria-modal=true and Close/Open record buttons.
  - `src/orders.js:17` — The View handler reveals the dialog; close and confirm handlers hide it without moving or restoring focus.
  - `src/app.js:8` — Escape invokes setMenu(false); no dialog dismissal is handled there.

### BEH-63C0421C · Dark mode switch reports an update without applying a page theme

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `settings-state`
- Description: The Dark mode switch is described as using darker surfaces at night. Its handler changes aria-checked and displays “Appearance preference updated,” but the supplied handler does not update a page theme. The stylesheet's aria-checked rule changes the switch itself.
- Impact: Users receive confirmation that an appearance preference changed while the page surfaces remain unchanged.
- Recommendation: Apply a page-level theme when the switch changes, or explain that the preference is unavailable in this demo and avoid success feedback that implies it was applied.
- Evidence:
  - `settings/index.html:7` — The Dark mode switch is described as using darker surfaces at night.
  - `src/settings.js:4` — The handler flips aria-checked and reports that the appearance preference was updated.
  - `assets/styles.css:2` — The aria-checked rule changes the switch track and thumb; the supplied styles contain no page-level theme rule.

### BEH-6F91C4EA · The notification button has no accessible name

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `accessible-name`
- Description: The shared header renders the notification button with only an aria-hidden SVG child. The button has no text, aria-label, or title to identify its purpose.
- Impact: Screen-reader users may encounter an unnamed button and cannot identify the notification action before activating it.
- Recommendation: Give the button a concise accessible name such as “Notifications.”
- Evidence:
  - `index.html:6` — The notification button has no text or naming attribute, and its only child SVG is aria-hidden.
  - `analytics/index.html:6` — The Analytics route repeats the unnamed notification button in its shared header.
  - `customers/index.html:6` — The Customers route repeats the unnamed notification button in its shared header.
  - `orders/index.html:6` — The Orders route repeats the unnamed notification button in its shared header.
  - `settings/index.html:6` — The Settings route repeats the unnamed notification button in its shared header.
  - `src/app.js:9` — Activating the notification button currently produces an all-caught-up toast.

### BEH-712482AE · Focus outlines are removed from navigation and icon controls

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `keyboard-focus`
- Description: The stylesheet sets outline:none on focus-visible navigation links and icon buttons. It also sets outline:0 on search inputs, with no focus treatment for the search box in the supplied styles. The navigation and icon controls appear across routes; search inputs appear on Customers and Orders.
- Impact: Keyboard users may have difficulty identifying the currently focused navigation, header, or search control.
- Recommendation: Replace the removed outlines with a visible focus treatment for links and icon buttons, and provide a focus treatment for the search input or its container.
- Evidence:
  - `assets/styles.css:6` — The shared focus-visible rule removes outlines from navigation links and icon buttons.
  - `assets/styles.css:2` — The search input rule sets outline:0; no focus-within treatment is present in the supplied stylesheet.

### BEH-730545E1 · Customer segment and sort buttons are inert

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `directory-controls`
- Description: The Customers page presents All segments and Newest first as buttons. The customer script handles search and invitation feedback only; it does not change the cards or provide feedback for either button.
- Impact: Users cannot segment or sort the directory despite controls that suggest those operations are available.
- Recommendation: Implement the segment and sort actions, or make their unavailable demo status clear.
- Evidence:
  - `customers/index.html:7` — All segments and Newest first are presented as toolbar buttons.
  - `src/customers.js:5` — The only registered customer-page handlers are for search input and the invite button.

### BEH-7E8E061F · Analytics cutoff changes the qualified-order count only at one threshold

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `filter-feedback`
- Description: The slider ranges from 1 to 100,000 and its adjacent copy says it filters a summary metric. The handler displays 286 for every value up to 40,000 and 11 for every value above 40,000. This leaves the displayed count unchanged across most of the slider range and changes it only at one boundary.
- Impact: Users exploring the cutoff may interpret the displayed value as a calculated result even though it changes only at a single threshold.
- Recommendation: Make the two-scenario behavior explicit or define a documented data model that updates the count across the slider range.
- Evidence:
  - `analytics/index.html:7` — The slider spans 1–100,000 and the adjacent copy describes filtering a summary metric.
  - `src/analytics.js:5` — The qualified-order count has only two fixed outcomes based on whether the slider value exceeds 40,000.

### BEH-99D983B4 · Closed mobile navigation remains in the keyboard tab order

- Severity: **high**; confidence: **high**; verification: `static_analysis`
- Category: `keyboard-navigation`
- Description: At widths up to 800px, the sidebar is moved off-screen with a transform. The menu handler changes the sidebar class and aria-expanded state but does not hide or disable the closed sidebar for keyboard navigation. Because the sidebar precedes the main content in the markup, its links can receive focus before the menu button while off-screen.
- Impact: On mobile, keyboard focus can move through navigation links that are off-screen before reaching the visible menu button.
- Recommendation: Remove the closed sidebar from sequential focus and the accessibility tree, and restore it when the menu opens. Keep aria-expanded synchronized with that state.
- Evidence:
  - `assets/styles.css:8` — The mobile closed state applies transform:translateX(-100%); the open state reverses the transform.
  - `src/app.js:5` — Menu state toggles CSS classes and aria-expanded; it does not synchronize an inert or hidden state.
  - `index.html:3` — The sidebar and its navigation links occur before the main header containing the menu button.
  - `orders/index.html:3` — The Orders route uses the same sidebar-before-header document order.

### BEH-9FC6B376 · Settings save briefly reports success before a simulated failure

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `form-feedback`
- Description: On submit, the handler immediately sets the live status to “Saved successfully” and shows a success-like toast. If the alert threshold exceeds 80,000, it changes the live status to “Sync failed; your changes were not stored” after 450 ms. The toast remains visible for 3.2 seconds. The form copy explicitly describes this simulated success-then-failure sequence, and the final status clearly reports the failure; the supported concern is the brief overlapping feedback.
- Impact: For the simulated failure case, the success-like toast remains visible after the live status changes to failure, so users receive overlapping outcome messages.
- Recommendation: Keep the simulated success-then-failure behavior clear, but replace or dismiss the success toast when the failure status appears.
- Evidence:
  - `settings/index.html:7` — The form says values above $80,000 simulate a failed save after a successful acknowledgement; save status has aria-live=polite.
  - `src/settings.js:15` — The submit handler announces success, shows a saved-preferences toast, and later sets failure status above the threshold.
  - `src/components.js:8` — Toast feedback stays visible for 3,200 ms unless replaced.

### BEH-EE5CAE05 · Overview chart period button does not change the chart

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `chart-controls`
- Description: The Revenue performance panel presents a Last 6 months button, but the chart is static markup and the overview handler does not register behavior for the period control.
- Impact: Users cannot change the displayed chart period through a control that is presented as a button.
- Recommendation: Implement period selection or present the current period as non-interactive text until alternate ranges are supported.
- Evidence:
  - `index.html:7` — The Revenue performance panel includes a Last 6 months button.
  - `src/app.js:6` — The overview handler wires the mobile menu, notifications, and report-export demo control; it does not wire a chart period control.


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
