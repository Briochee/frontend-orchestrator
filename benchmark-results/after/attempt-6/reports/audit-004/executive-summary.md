# Executive summary

Audit completion status: **incomplete**
Project: `northstar-ops-audit-fixture`
Description: Dependency-free multi-route frontend audit benchmark with synthetic data
Framework signals: Static HTML/CSS/JavaScript (detected from files)

The audit contains 10 technical, 13 behavioral, and 9 visual finding(s).

## Coverage

- Source/style files: 13
- Route candidates: 5
- Routes rendered: 5
- Screenshots: 20
- Screenshots attached / interpreted / validated: 15 / True / True
- Browser navigation failures: 0
- Component profiles: 228
- Analysis backend: `codex_cli_plus_static`; requested profile `deep`

## Highest-priority findings

- **HIGH · BEH-99D983B4: Closed mobile navigation remains in the keyboard tab order.** On mobile, keyboard focus can move through navigation links that are off-screen before reaching the visible menu button.
- **MEDIUM · BEH-4C83DB1A: Orders toolbar buttons have no implemented action or feedback.** Users can activate labeled controls without receiving an action or indication that the controls are unavailable.
- **MEDIUM · BEH-516B1BF7: Order details dialog does not manage keyboard focus or Escape dismissal.** Keyboard focus can remain behind a dialog that claims to be modal, leaving users to navigate away from the dialog to reach its controls.
- **MEDIUM · BEH-63C0421C: Dark mode switch reports an update without applying a page theme.** Users receive confirmation that an appearance preference changed while the page surfaces remain unchanged.
- **MEDIUM · BEH-6F91C4EA: The notification button has no accessible name.** Screen-reader users may encounter an unnamed button and cannot identify the notification action before activating it.
- **MEDIUM · BEH-712482AE: Focus outlines are removed from navigation and icon controls.** Keyboard users may have difficulty identifying the currently focused navigation, header, or search control.
- **MEDIUM · BEH-730545E1: Customer segment and sort buttons are inert.** Users cannot segment or sort the directory despite controls that suggest those operations are available.
- **MEDIUM · BEH-7E8E061F: Analytics cutoff changes the qualified-order count only at one threshold.** Users exploring the cutoff may interpret the displayed value as a calculated result even though it changes only at a single threshold.

## Visual design identity

A restrained operations dashboard with a cool pale canvas, white bordered cards, compact sans-serif interface text, dark navy navigation on desktop, and recurring teal accents. A compact white header replaces the visible desktop rail at tablet and mobile widths. Settings adds a serif page title and violet save action; Orders uses a larger heading, and Analytics uses squarer panel corners. These page-specific treatments sit within a shared shell and palette.

## Important coverage limits

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

Human decisions about design, behavior, and implementation remain pending at their existing approval gates.
