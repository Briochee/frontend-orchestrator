# Executive summary

Audit completion status: **completed**
Project: `northstar-ops-audit-fixture`
Description: Dependency-free multi-route frontend audit benchmark with synthetic data
Framework signals: Static HTML/CSS/JavaScript (detected from files)

The audit contains 10 technical, 12 behavioral, and 7 visual finding(s).

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

- **MEDIUM · BEH-03A44AFE: Settings save announces success before a simulated failure.** Users and assistive technology can receive conflicting save outcomes for one submission.
- **MEDIUM · BEH-0B6E3A8C: Settings form row retains a 720px minimum width at the narrow breakpoint.** On narrow screens, reaching the full row content can require horizontal panning, which complicates use of these settings fields on touch devices.
- **MEDIUM · BEH-27BC877E: Dark mode switch reports an update without changing the workspace appearance.** The confirmation suggests that the appearance changed, while the source only changes the switch itself.
- **MEDIUM · BEH-2AB68BA6: Workspace name is interpreted as markup in the save confirmation.** A workspace name containing markup can alter the content or structure of the save confirmation, so users may not see the entered name literally.
- **MEDIUM · BEH-671ABAC3: Customer search has no no-matches feedback.** Users cannot tell from the results area whether the search found no customers or the content failed to appear.
- **MEDIUM · BEH-900CAE98: Navigation and icon buttons remove their focus outline.** Keyboard users lack a clear focus cue on these controls, making it harder to track their position in the shared navigation and header.
- **MEDIUM · BEH-98F572E7: Closed mobile navigation remains in the keyboard tab order.** A keyboard user can tab to navigation links while they are visually offscreen, making focus order difficult to follow.
- **MEDIUM · BEH-AFFF18E9: Analytics cutoff changes the qualified-order count at one hardcoded threshold.** Most slider movements leave the count unchanged, while crossing one threshold produces a large jump that does not reflect the selected minimum as a filtered count.

## Visual design identity

A restrained, data-focused operations dashboard. Across routes, the visual system uses a pale blue-gray workspace, white panels and controls, dark slate text, fine borders, and teal accents, with a dark blue-gray navigation rail on desktop and a compact white header at tablet and mobile widths. Settings adds a serif page title and violet save action, creating a route-specific variation within the shared system. The polished, businesslike character is an inference from the reported page hierarchy and surfaces.

## Important coverage limits

- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.

Human decisions about design, behavior, and implementation remain pending at their existing approval gates.
