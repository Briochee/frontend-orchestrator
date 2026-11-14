# Frontend audit summary

Project: `northstar-ops-audit-fixture`
Framework signals: Static HTML/CSS/JavaScript (detected from files)
Audit mode: `codex_cli_plus_static`

Audit completion status: **completed**

## Scope and evidence

Inspected 16 repository files; 7 frontend source files and 1 stylesheets were detected.
The source audit did not execute project code, install dependencies, or run scripts.

## Findings by area

- Technical and architecture: 10
- Behavior and accessibility: 12
- Visual design: 7

## Highest-priority findings

- **MEDIUM · BEH-03A44AFE — Settings save announces success before a simulated failure.** Users and assistive technology can receive conflicting save outcomes for one submission.
- **MEDIUM · BEH-0B6E3A8C — Settings form row retains a 720px minimum width at the narrow breakpoint.** On narrow screens, reaching the full row content can require horizontal panning, which complicates use of these settings fields on touch devices.
- **MEDIUM · BEH-27BC877E — Dark mode switch reports an update without changing the workspace appearance.** The confirmation suggests that the appearance changed, while the source only changes the switch itself.
- **MEDIUM · BEH-2AB68BA6 — Workspace name is interpreted as markup in the save confirmation.** A workspace name containing markup can alter the content or structure of the save confirmation, so users may not see the entered name literally.
- **MEDIUM · BEH-671ABAC3 — Customer search has no no-matches feedback.** Users cannot tell from the results area whether the search found no customers or the content failed to appear.
- **MEDIUM · BEH-900CAE98 — Navigation and icon buttons remove their focus outline.** Keyboard users lack a clear focus cue on these controls, making it harder to track their position in the shared navigation and header.
- **MEDIUM · BEH-98F572E7 — Closed mobile navigation remains in the keyboard tab order.** A keyboard user can tab to navigation links while they are visually offscreen, making focus order difficult to follow.
- **MEDIUM · BEH-AFFF18E9 — Analytics cutoff changes the qualified-order count at one hardcoded threshold.** Most slider movements leave the count unchanged, while crossing one threshold produces a large jump that does not reflect the selected minimum as a filtered count.

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

- No project build, test, or dependency-lifecycle scripts were executed; browser navigation did run the frontend page scripts.
- LCP, INP, CLS, and bundle-size measurements were not collected. Browser navigation timing and request data are single-run lab observations; the automated capture did not activate controls.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- 

## Recommended next steps

2. Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
3. Use text-only toast rendering for user-provided values.
4. Calculate the analytics qualified-order metric from a defined dataset.
5. Make settings save feedback reflect the final simulated result.
6. Complete keyboard focus handling for the order dialog and restore a visible focus indicator to shared controls.
7. Reset route-specific minimum widths or keep overflow within dedicated scroll containers at narrow viewports.
8. Render the settings workspace name as text in toast content while keeping any required emphasis markup static.
9. Clarify whether the analytics cutoff is illustrative or should count records, then match the displayed behavior to that intent.
10. Ensure settings success and failure feedback cannot remain visible together.
11. Manage focus entry, containment, Escape dismissal, and restoration for the order dialog.
12. Provide visible focus styling for shared navigation links and icon buttons.
13. Either implement a page theme for Dark mode or identify the setting as simulated.
14. Contain the orders table's minimum width within a local horizontal scroller or another narrow-screen treatment.
15. Let the analytics chart frame fit narrow content or contain its minimum width in a scrollable region.
16. Remove or reset the settings form row's 720px minimum width at the narrow breakpoint.
17. Restore visible focus indicators for navigation and icon buttons, and make closed mobile navigation links unavailable to keyboard focus.
18. Give the order dialog a complete keyboard focus and dismissal flow, including focus entry, containment, Escape dismissal, and focus restoration.
19. Add a customer-search empty state and implement or clearly disable the customer and orders toolbar controls that currently have no handlers.
20. Derive the analytics qualified-order count from data or disclose the coarse simulated metric behavior.
21. Keep settings feedback truthful: do not announce save success until the simulated operation completes, apply or accurately describe switch effects, and render the workspace name as text.
22. Remove the fixed minimum width from the settings form row at narrow breakpoints.
23. Make export/download feedback match whether a file was actually created.
24. Add visible focus treatment to shared navigation and icon buttons, and remove the closed mobile sidebar from keyboard navigation.
25. Complete the order dialog focus lifecycle and add no-matches feedback to customer search.
26. Implement the advertised customer and order toolbar actions or clearly identify controls unavailable in the demo.
27. Align settings and analytics feedback with the state the controls actually apply or the artifact they actually create.
28. Remove the settings row's fixed minimum width at narrow viewports.
29. Adjust the analytics layout breakpoint so both panels fit within the tablet content width.
30. Remove the chart frame's forced minimum width on mobile or make its horizontal scrolling explicit and contained.
31. Keep the desktop title hierarchy, neutral surfaces, teal data accents, and spacious side-by-side panel layout.
32. Stack the analytics panels at tablet widths to keep both panels in view.
33. At mobile widths, choose between fitting the chart to its panel and providing a clearly indicated scroll region.
34. Preserve the existing responsive change from three to two to one customer-card columns.
35. Review whether the sharper corners on the Morgan Ellis card are a deliberate exception; align them with the other cards if not.
36. Confirm the purpose of the second-card radius exception; otherwise use the shared customer-card radius.
37. Refine the narrow-width order table so the fields and row action are discoverable within the viewport, choosing between horizontal scrolling and a stacked row layout based on whether preserving table density or at-a-glance visibility is more important.
38. Refine the narrow-width table presentation so later order fields and row actions can be reached without relying on the table extending past the visible viewport.
39. Let `.fixed-field-row` shrink within its card or switch to a single-column layout at widths where the row no longer fits; verify that the card edges and controls remain inside the viewport.
40. Reset the fixed minimum width when the settings layout stacks, then confirm the form and cards fit within the tablet and mobile viewports.

Technical defects, behavior changes, and subjective design recommendations remain separate. No design or implementation approval is implied by this report.
