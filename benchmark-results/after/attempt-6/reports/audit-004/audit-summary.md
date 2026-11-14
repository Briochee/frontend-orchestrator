# Frontend audit summary

Project: `northstar-ops-audit-fixture`
Framework signals: Static HTML/CSS/JavaScript (detected from files)
Audit mode: `codex_cli_plus_static`

Audit completion status: **incomplete**

## Scope and evidence

Inspected 16 repository files; 7 frontend source files and 1 stylesheets were detected.
The source audit did not execute project code, install dependencies, or run scripts.

## Findings by area

- Technical and architecture: 10
- Behavior and accessibility: 13
- Visual design: 9

## Highest-priority findings

- **HIGH · BEH-99D983B4 — Closed mobile navigation remains in the keyboard tab order.** On mobile, keyboard focus can move through navigation links that are off-screen before reaching the visible menu button.
- **MEDIUM · BEH-4C83DB1A — Orders toolbar buttons have no implemented action or feedback.** Users can activate labeled controls without receiving an action or indication that the controls are unavailable.
- **MEDIUM · BEH-516B1BF7 — Order details dialog does not manage keyboard focus or Escape dismissal.** Keyboard focus can remain behind a dialog that claims to be modal, leaving users to navigate away from the dialog to reach its controls.
- **MEDIUM · BEH-63C0421C — Dark mode switch reports an update without applying a page theme.** Users receive confirmation that an appearance preference changed while the page surfaces remain unchanged.
- **MEDIUM · BEH-6F91C4EA — The notification button has no accessible name.** Screen-reader users may encounter an unnamed button and cannot identify the notification action before activating it.
- **MEDIUM · BEH-712482AE — Focus outlines are removed from navigation and icon controls.** Keyboard users may have difficulty identifying the currently focused navigation, header, or search control.
- **MEDIUM · BEH-730545E1 — Customer segment and sort buttons are inert.** Users cannot segment or sort the directory despite controls that suggest those operations are available.
- **MEDIUM · BEH-7E8E061F — Analytics cutoff changes the qualified-order count only at one threshold.** Users exploring the cutoff may interpret the displayed value as a calculated result even though it changes only at a single threshold.

## Visual audit status

Rendered screenshots are registered as evidence. Any appearance conclusions are limited to those rendered views and states.

## Inspection coverage

- Source files profiled: 13
- Route candidates: 5
- Routes rendered: 5
- Component profiles: 228
- Screenshots captured / attached / interpreted / validated: 20 / 15 / True / True
- Viewports: desktop, mobile, tablet
- Application controls activated: none; one passive keyboard Tab focus state may be captured per route.

## Limitations

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

## Recommended next steps

1. Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
2. Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
3. Keep editable settings text out of HTML insertion sinks.
4. Derive analytics results from an explicit data source, or communicate that the slider is only a simplified demonstration.
5. Make settings feedback reflect the final save outcome and ensure preference controls apply the behavior they announce.
6. Give the order dialog a complete focus and dismissal lifecycle.
7. Restore visible keyboard focus indicators for shared navigation and icon controls.
8. Preserve constrained scrolling for wide tables and remove fixed-width form constraints at mobile breakpoints.
9. Use one canonical source for customer directory records.
10. Keep closed mobile navigation out of both keyboard focus order and the accessibility tree; add complete focus management to the order dialog.
11. Restore visible keyboard focus styles and provide an accessible name for the notification button.
12. Implement or clearly identify unavailable order and customer directory controls, including customer-specific action buttons.
13. Show a customer no-results state and make the analytics cutoff reflect a meaningful range of values.
14. Align settings and export success feedback with the result the user actually receives.
15. Address the closed mobile sidebar and order dialog focus behavior, then restore visible focus cues and name the notification button.
16. For controls that currently do nothing, either implement the labeled action or communicate its demo-only availability at the control.
17. Align analytics and settings feedback with the actual outcome, including the cutoff count, download behavior, theme state, and simulated save failure.
18. Consider a more compact mobile KPI presentation only if reducing scroll depth is a product priority; the current screenshot does not establish that the existing stack is a usability failure.
19. Keep the current mobile KPI spacing unless faster first-viewport access to trends is a defined product priority; if it is, compare a denser KPI treatment against the current card readability.
20. Address the chart and panel overflow at tablet and mobile widths, choosing between a scaled chart and a contained, visibly scrollable chart.
21. Consider slightly increasing the contrast or size of the pale “Updated moments ago” note if it is meant to be readily read; this is a subjective visual refinement, not an observed layout failure.
22. Adjust the chart sizing and analytics grid breakpoints so both panels remain within narrow viewports, or provide a clear chart-level horizontal scrolling affordance if the current chart scale must be preserved.
23. Keep the desktop heading, paired analytics cards, and order explorer hierarchy; it is clear and fully visible in the supplied desktop render.
24. Apply the shared rounded corner treatment to every customer card.
25. Increase the contrast of the sidebar footer initials against the avatar background.
26. Use the shared customer-card radius for the Morgan Ellis card at all breakpoints.
27. Give the sidebar footer avatar initials a darker foreground than the muted workspace descriptor.
28. Preserve the existing heading hierarchy, teal invite action, and one-column mobile and two-column tablet adaptations.
29. Contain the table's minimum width in a deliberate small-screen layout and make access to its trailing columns apparent.
30. Restore a contained horizontal scroll area for the orders table at narrow viewport sizes, preserving access to all columns while avoiding page-level width growth.
31. Review the tablet toolbar wrapping: the search field and filters occupy different rows, and Date range and Archive wrap to another row.
32. Allow the workspace details form and its row to shrink within the settings grid, preserving a visible card gutter at mobile and tablet widths and separation from the neighboring card on desktop.
33. Constrain the Workspace details form row to its panel by removing its fixed minimum width; preserve the existing single-column form layout at the mobile breakpoint.

Technical defects, behavior changes, and subjective design recommendations remain separate. No design or implementation approval is implied by this report.
