# Interaction and behavior audit

Audit backend: `codex_cli_plus_static`

## Evidence-backed specialist assessment

### frontend_ux_auditor · first_pass

Source observations: the five routes use direct HTML navigation and share a mobile menu, notification toast, and locally loaded scripts. The orders route filters a fixed fixture and opens a dialog; customers filters cards by name; analytics updates a slider label and a summary count; settings provides local switches and a form with a delayed failure state. Rendered observations: none; no screenshots were attached. Measurements: none were collected for this pass. Inferences: source shows several controls with no event handler, and the mobile settings form has a fixed-width row that can require horizontal scrolling at narrow viewports. Hypotheses: none. Runtime behavior, browser validation, keyboard operation, assistive technology behavior, and touch usability were not exercised.

Evidence:
- `index.html:5` — The overview contains direct links to the other routes and a button to open the mobile navigation.
- `src/app.js:5` — The shared script toggles the mobile menu, closes it on backdrop click or Escape, and uses toast feedback for notifications and the overview export action.
- `src/orders.js:9` — Orders are filtered locally by query and status, with a rendered empty row when no orders match.
- `src/settings.js:11` — The settings form announces success before a delayed threshold-based failure state can replace it.

Pass-scoped limitations:
- No project code, browser, scripts, builds, servers, or dependency managers were executed.
- No rendered screenshots were attached, so no rendered appearance or runtime observations are reported.
- Keyboard, screen-reader, browser-validation, touch, and asynchronous interactions were not exercised; findings are based on static source inspection.
- No runtime measurements were collected; the settings narrow-screen overflow is an inference from CSS constraints, not a measured viewport result.

### frontend_ux_auditor · cross_validation

Source observations: The five static HTML routes use internal links and share a mobile menu and notification feedback. The orders route filters fixture data, customer search hides nonmatching cards, the analytics slider updates its label and uses a two-value threshold for the qualified-order count, and the settings route toggles switch state and updates save feedback. Several displayed customer and order controls have no route-level handlers. Inferences from source: the navigation and icon-button focus rules remove the outline without a focus-specific replacement; the closed mobile sidebar remains in the document while CSS translates it offscreen; and the settings form retains a 720px minimum-width row at the narrow breakpoint, implying horizontal overflow. Rendered observations: none; no screenshot image was attached for this pass. Measurements: none collected or cited. Hypotheses: none retained. Runtime behavior, keyboard operation, touch usability, and assistive-technology behavior were not exercised.

Evidence:
- `index.html:5` — The primary navigation contains internal links to the other route pages.
- `src/app.js:5` — The shared menu handler toggles open classes and updates aria-expanded; the Escape handler only closes the menu.
- `src/orders.js:11` — The orders route filters the imported order fixture by query and status.
- `src/customers.js:7` — Customer search hides cards whose customer name does not match the query.
- `src/analytics.js:5` — The slider handler updates the label and assigns the qualified-order count from a single threshold.
- `src/settings.js:5` — Settings switches toggle aria-checked, and submit reports success before a delayed threshold-based failure.
- `assets/styles.css:4` — The settings row has a 720px minimum width, while the narrow breakpoint changes its column layout without overriding that minimum.
- `assets/styles.css:6` — The focus-visible rule sets outline to none for navigation links and icon buttons.

Pass-scoped limitations:
- Only the supplied source snapshot was inspected; no project code, scripts, builds, servers, or dependency managers were executed.
- No screenshot image was attached, so rendered appearance and runtime interactions were not verified.
- Keyboard, screen-reader, browser-validation, and touch behavior were not exercised; interaction findings are based on static source inspection.
- No runtime measurements were collected. The settings overflow finding is an inference from CSS constraints, not a measured viewport result.
- The markup-rendering finding does not assert script execution; that behavior was not tested.

## Findings

### BEH-03A44AFE · Settings save announces success before a simulated failure

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `save-feedback`
- Description: On submit, the form immediately sets its live status to Saved successfully and shows a success toast. For thresholds above 80,000, the status changes to Sync failed; your changes were not stored 450ms later. The helper text discloses this simulated condition, but the save feedback still announces success before failure.
- Impact: Users and assistive technology can receive conflicting save outcomes for one submission.
- Recommendation: Represent the save as pending until the simulated result is known, then announce only the final success or failure while retaining entered values for retry.
- Evidence:
  - `settings/index.html:7` — The threshold helper text discloses the simulated failure condition and the save-status element is a live region.
  - `src/settings.js:16` — Submit reports success immediately, then changes the status to failure after a timeout for thresholds above 80,000.

### BEH-0B6E3A8C · Settings form row retains a 720px minimum width at the narrow breakpoint

- Severity: **medium**; confidence: **medium**; verification: `static_analysis`
- Category: `responsive-interaction`
- Description: The settings form applies min-width:720px to .fixed-field-row. The max-520px rule changes the row to a single-column grid but does not remove its minimum width. This source constraint implies horizontal overflow on narrower screens; no rendered viewport measurement was collected.
- Impact: On narrow screens, reaching the full row content can require horizontal panning, which complicates use of these settings fields on touch devices.
- Recommendation: Remove or override the fixed minimum width at narrow breakpoints so the form row can fit its available content width.
- Evidence:
  - `settings/index.html:7` — The contact email and default region fields are inside the fixed-field-row.
  - `assets/styles.css:4` — The settings fixed-field-row has a 720px minimum width.
  - `assets/styles.css:9` — The narrow-screen rule changes the form row to one column without overriding its minimum width.

### BEH-27BC877E · Dark mode switch reports an update without changing the workspace appearance

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `settings-behavior`
- Description: Clicking the Dark mode switch toggles aria-checked and displays an appearance-updated toast. The stylesheet changes the switch's own appearance based on aria-checked, but defines no workspace theme behavior tied to this state. The control's description says it uses darker surfaces at night.
- Impact: The confirmation suggests that the appearance changed, while the source only changes the switch itself.
- Recommendation: Apply the selected appearance to the workspace or change the control description and feedback so they match the switch's actual behavior.
- Evidence:
  - `settings/index.html:7` — The Dark mode control is described as using darker surfaces.
  - `src/settings.js:4` — The switch handler toggles aria-checked and reports that the appearance preference was updated.
  - `assets/styles.css:2` — The switch state changes the switch control's background and thumb position.

### BEH-2AB68BA6 · Workspace name is interpreted as markup in the save confirmation

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `feedback-data-rendering`
- Description: The editable workspace name is interpolated into the toast message, and the shared toast helper assigns its message to innerHTML. As a result, markup entered as the workspace name is interpreted in the live confirmation instead of being displayed literally. Runtime script execution was not tested and is not claimed here.
- Impact: A workspace name containing markup can alter the content or structure of the save confirmation, so users may not see the entered name literally.
- Recommendation: Render the submitted name as text in the toast rather than inserting it as HTML.
- Evidence:
  - `settings/index.html:7` — Workspace name is an editable input in the settings form.
  - `src/settings.js:18` — The submitted workspace name is interpolated into the toast message.
  - `src/components.js:8` — The toast helper assigns the supplied message to innerHTML.

### BEH-671ABAC3 · Customer search has no no-matches feedback

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `empty-state`
- Description: The customer search handler only hides cards that do not match the query. The customer grid markup contains no empty-state element, so a query with no matches leaves the grid without an explanation.
- Impact: Users cannot tell from the results area whether the search found no customers or the content failed to appear.
- Recommendation: Show a no-matches message when the search hides every card and make it clear that clearing the query restores the list.
- Evidence:
  - `src/customers.js:5` — The input handler only toggles each card's hidden property based on the query.
  - `customers/index.html:7` — The search input and customer-card grid are present without an empty-state element in the grid markup.

### BEH-8E24D5A9 · Analytics Download confirms an export without creating a downloadable file

- Severity: **low**; confidence: **high**; verification: `static_analysis`
- Category: `download-feedback`
- Description: The Analytics Download button calls a handler that only displays Report exported (demo only). That handler does not create a file, start a download, or provide a follow-up link. This finding is based on the source handler; no click was exercised.
- Impact: Users may expect a report file after receiving the export confirmation but have no artifact to retrieve.
- Recommendation: Generate a demo file or make the button and toast state clearly that demo mode does not create a downloadable artifact.
- Evidence:
  - `analytics/index.html:7` — The route labels the control Download.
  - `src/analytics.js:7` — The download handler only calls toast with an exported confirmation.

### BEH-900CAE98 · Navigation and icon buttons remove their focus outline

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `keyboard-focus`
- Description: The shared stylesheet sets outline:none for .nav-link:focus-visible and .icon-button:focus-visible, and does not define a focus-specific replacement for those selectors. This affects keyboard focus on the shared navigation and icon buttons across the routes.
- Impact: Keyboard users lack a clear focus cue on these controls, making it harder to track their position in the shared navigation and header.
- Recommendation: Provide a visible focus treatment for navigation links and icon buttons, including against the sidebar and header backgrounds.
- Evidence:
  - `assets/styles.css:6` — The focus-visible rule removes the outline from navigation links and icon buttons.

### BEH-98F572E7 · Closed mobile navigation remains in the keyboard tab order

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `mobile-navigation`
- Description: At widths up to 800px, CSS moves the sidebar offscreen with transform:translateX(-100%) and moves it back only when the open class is present. The sidebar remains ordinary document content: it is not hidden or inert, and the menu handler changes classes and aria-expanded without changing link focusability.
- Impact: A keyboard user can tab to navigation links while they are visually offscreen, making focus order difficult to follow.
- Recommendation: Remove the closed sidebar from sequential focus navigation and restore its links to the focus order when the menu opens.
- Evidence:
  - `assets/styles.css:8` — The mobile breakpoint translates the sidebar offscreen until it has the open class.
  - `index.html:5` — The sidebar contains navigation anchors and has no hidden or inert state.
  - `src/app.js:5` — The menu state handler toggles classes and aria-expanded without changing the sidebar links' focusability.

### BEH-AFFF18E9 · Analytics cutoff changes the qualified-order count at one hardcoded threshold

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `metric-filtering`
- Description: The explorer describes the cutoff as filtering the summary metric, but the slider handler sets the count to 286 for values at or below 40,000 and 11 above 40,000. It does not calculate matches from the order fixture.
- Impact: Most slider movements leave the count unchanged, while crossing one threshold produces a large jump that does not reflect the selected minimum as a filtered count.
- Recommendation: Calculate the count from order-value data or describe the displayed values as a coarse illustrative demo rather than a filtered metric.
- Evidence:
  - `analytics/index.html:7` — The explorer says the cutoff filters the summary metric over a $1–$100,000 value domain.
  - `src/analytics.js:5` — The slider handler updates the count using only the 40,000 threshold and two fixed counts.
  - `src/data.js:2` — The available order fixture is defined separately from the analytics slider handler.

### BEH-E926C4C5 · Order details dialog has no focus lifecycle or Escape dismissal

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `dialog-keyboard-access`
- Description: The View handler reveals the custom dialog without moving focus. The source does not trap focus while it is open or restore focus to the triggering button when it closes. The shared Escape handler closes only the mobile menu.
- Impact: Keyboard users can remain on the page behind the dialog and may have to navigate through unrelated controls to reach its actions; Escape does not dismiss it.
- Recommendation: Move focus into the dialog when it opens, keep focus within it while open, dismiss it on Escape, and return focus to the triggering View button when it closes.
- Evidence:
  - `src/orders.js:17` — The View handler reveals the dialog; Close and Open record hide it without focus management.
  - `orders/index.html:7` — The dialog is a custom element with role=dialog and aria-modal=true.
  - `src/app.js:8` — The global Escape handler only changes mobile-menu state.

### BEH-F3DAA3F3 · Customer segment, sort, and per-customer action buttons have no handlers

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `inactive-controls`
- Description: The customers page presents All segments, Newest first, and More actions buttons. Its route script handles customer search and the Invite customer button, but does not register behavior for the segment, sort, or per-card action buttons.
- Impact: Users can activate controls that appear to filter, reorder, or open customer actions without any result or explanation.
- Recommendation: Connect these controls to their labeled actions or clearly mark them as unavailable in the demo.
- Evidence:
  - `customers/index.html:7` — The toolbar and customer cards expose the segment, sort, and More actions buttons.
  - `src/customers.js:3` — The route script registers search and invitation handlers only.

### BEH-F62D5BD7 · Orders toolbar actions, including Export, have no handlers

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `inactive-controls`
- Description: The orders page presents Export, Columns, Bulk actions, Saved filters, Date range, and Archive buttons. The route script handles search, status changes, row viewing, dialog controls, and New order feedback, but no handler is registered for these toolbar buttons.
- Impact: Users receive no result or explanation after activating these controls; Archive is especially ambiguous because it is presented as an active action but has no outcome.
- Recommendation: Implement these actions or clearly mark them as unavailable in the demo; keep Archive unavailable until its outcome and confirmation flow are defined.
- Evidence:
  - `orders/index.html:7` — The toolbar includes Export, Columns, Bulk actions, Saved filters, Date range, and Archive buttons.
  - `src/orders.js:16` — The route script registers handlers for search, status, row actions, dialog controls, and New order, with no toolbar-action handler.


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

## Runtime action coverage

Browser collection inspected structural controls and accessible-name signals. It captured one passive Tab focus state per route at desktop when a focusable target was available; it did not activate application controls, submit forms, or claim workflow outcomes. Review source-derived journeys above; unexecuted behavior remains unverified.
