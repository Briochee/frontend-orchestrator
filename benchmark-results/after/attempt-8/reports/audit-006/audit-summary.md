# Frontend audit summary

Project: `northstar-ops-audit-fixture`
Framework signals: Static HTML/CSS/JavaScript (detected from files)
Audit mode: `codex_cli_plus_static`

Audit completion status: **incomplete**

## Scope and evidence

Inspected 16 repository files; 7 frontend source files and 1 stylesheets were detected.
The source audit did not execute project code, install dependencies, or run scripts.

## Findings by area

- Technical and architecture: 13
- Behavior and accessibility: 12
- Visual design: 4

## Highest-priority findings

- **MEDIUM · BEH-60FE4C17 — Settings reports success before the simulated failure outcome.** Users may act on the success feedback before the failure announcement and are not told what to do next after the simulated failure.
- **MEDIUM · BEH-6931A4BE — Customer segment and sort buttons have no source-defined effect.** Users can attempt to filter or reorder the directory without receiving a source-defined result or explanation.
- **MEDIUM · BEH-6CE0F8DA — Dark mode switch changes its checked state without changing the workspace theme.** Users receive confirmation that an appearance preference changed while the workspace theme remains unchanged in the supplied implementation.
- **MEDIUM · BEH-8BDB8C95 — Orders Export button is not bound to export feedback.** Users receive no source-defined indication that an export was requested or is unavailable when they activate the Orders Export button.
- **MEDIUM · BEH-C0A75AE8 — Customer search can leave an empty grid without feedback.** When a query matches no customer, the cards disappear without an explanation or recovery hint.
- **MEDIUM · BEH-CA13B36D — Order details dialog lacks source-defined focus management and Escape dismissal.** Keyboard users may remain focused on content behind the visible dialog and must navigate to its controls themselves; Escape does not dismiss it.
- **MEDIUM · BEH-D8F2243A — Orders table is likely to overflow its container on narrow screens.** If the inferred overflow occurs on a phone, users may need to pan the page to reach later columns, making surrounding content harder to navigate by touch.
- **MEDIUM · BEH-E3892C71 — Focus indicators are removed from shared navigation, icon buttons, and search inputs.** Keyboard users may have difficulty identifying the currently focused shared navigation or icon control, and the search inputs lack a stylesheet-defined focus boundary.

## Visual audit status

Rendered screenshots are registered as evidence. Any appearance conclusions are limited to those rendered views and states.

## Inspection coverage

- Source files profiled: 13
- Route candidates: 5
- Routes rendered: 5
- Component profiles: 228
- Screenshots captured / attached / interpreted / validated: 20 / 3 / True / False
- Viewports: desktop, mobile, tablet
- Application controls activated: none; one passive keyboard Tab focus state may be captured per route.

## Limitations

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

## Recommended next steps

1. Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
2. Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
3. Replace the user-controlled Settings toast HTML path with text-safe rendering.
4. Make modal focus behavior and keyboard focus indicators explicit for the affected controls.
5. Remove the narrow-screen minimum widths or contain their overflow within the affected components.
6. Make the Analytics cutoff derive its count from a defined dataset and keep save feedback consistent with the final result.
7. Use text rendering for the workspace name in toast messages and make save feedback agree with the final simulated outcome.
8. Calculate the Analytics qualified-order count from a defined dataset, and align the Dark mode control behavior with its label.
9. Manage focus for the Orders dialog and provide authored focus indicators; keep closed mobile navigation out of keyboard navigation.
10. Review the Orders table, Analytics chart frame, and Settings contact row minimum widths at narrow viewports; overflow remains unverified without rendering.
11. Choose a single customer-directory data source and add a reduced-motion override for the live status beacon.
12. Restore visible keyboard focus styling for navigation, icon buttons, and search fields, and give the order dialog a complete focus and Escape-key flow.
13. Add customer-search empty-state feedback and wire or clearly disable the customer toolbar and card actions that currently have no response.
14. Connect route-specific export and order-management controls to behavior or clear unavailable states; replace static chart-period controls with non-interactive labels if they are fixed.
15. Make settings success/failure feedback consistent with the final save outcome and ensure the Dark mode control changes the page theme or communicates its limitation.
16. Preserve horizontal table scrolling and let the settings fields reflow on narrow screens; confirm the source-derived responsive risks in a browser when runtime inspection is allowed.
17. Restore visible keyboard focus cues on the shared navigation, icon buttons, and search boxes.
18. Add keyboard focus management and Escape dismissal to the Orders details dialog.
19. Provide explicit no-results feedback for customer search and source-defined responses for the visible customer and Orders toolbar controls.
20. Make Settings save feedback reflect the simulated outcome before announcing success.
21. Verify the Orders table and Settings contact row at narrow viewports before treating the inferred overflow as confirmed.
22. Consider whether mobile users should see trend context sooner; if so, evaluate a more compact KPI presentation while preserving the current card readability.
23. Preserve the coherent navy, pale-canvas, white-card, and teal treatment visible across the three supplied widths.
24. Treat earlier mobile access to trend and activity context as a product-priority decision; the supplied evidence supports the current KPI-first order but also shows its first-viewport cost.

Technical defects, behavior changes, and subjective design recommendations remain separate. No design or implementation approval is implied by this report.
