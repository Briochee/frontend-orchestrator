# Executive summary

Audit completion status: **incomplete**
Project: `northstar-ops-audit-fixture`
Description: Dependency-free multi-route frontend audit benchmark with synthetic data
Framework signals: Static HTML/CSS/JavaScript (detected from files)

The audit contains 13 technical, 12 behavioral, and 4 visual finding(s).

## Coverage

- Source/style files: 13
- Route candidates: 5
- Routes rendered: 5
- Screenshots: 20
- Screenshots attached / interpreted / validated: 3 / True / False
- Browser navigation failures: 0
- Component profiles: 228
- Analysis backend: `codex_cli_plus_static`; requested profile `deep`

## Highest-priority findings

- **MEDIUM · BEH-60FE4C17: Settings reports success before the simulated failure outcome.** Users may act on the success feedback before the failure announcement and are not told what to do next after the simulated failure.
- **MEDIUM · BEH-6931A4BE: Customer segment and sort buttons have no source-defined effect.** Users can attempt to filter or reorder the directory without receiving a source-defined result or explanation.
- **MEDIUM · BEH-6CE0F8DA: Dark mode switch changes its checked state without changing the workspace theme.** Users receive confirmation that an appearance preference changed while the workspace theme remains unchanged in the supplied implementation.
- **MEDIUM · BEH-8BDB8C95: Orders Export button is not bound to export feedback.** Users receive no source-defined indication that an export was requested or is unavailable when they activate the Orders Export button.
- **MEDIUM · BEH-C0A75AE8: Customer search can leave an empty grid without feedback.** When a query matches no customer, the cards disappear without an explanation or recovery hint.
- **MEDIUM · BEH-CA13B36D: Order details dialog lacks source-defined focus management and Escape dismissal.** Keyboard users may remain focused on content behind the visible dialog and must navigate to its controls themselves; Escape does not dismiss it.
- **MEDIUM · BEH-D8F2243A: Orders table is likely to overflow its container on narrow screens.** If the inferred overflow occurs on a phone, users may need to pan the page to reach later columns, making surrounding content harder to navigate by touch.
- **MEDIUM · BEH-E3892C71: Focus indicators are removed from shared navigation, icon buttons, and search inputs.** Keyboard users may have difficulty identifying the currently focused shared navigation or icon control, and the search inputs lack a stylesheet-defined focus boundary.

## Visual design identity

A restrained operations dashboard with a pale cool-gray workspace, white rounded panels with thin borders, dark blue-gray text, and teal accents. Desktop uses a dark sidebar; tablet and mobile show a compact top bar.

## Important coverage limits

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

Human decisions about design, behavior, and implementation remain pending at their existing approval gates.
