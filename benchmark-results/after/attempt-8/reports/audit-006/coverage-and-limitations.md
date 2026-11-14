# Coverage and limitations

Audit completion status: **incomplete**
Requested depth: `deep`
Backend: `codex_cli_plus_static`

- Source and style files: 13
- Route candidates discovered: 5
- Routes rendered: 5
- Screenshots captured / attached / interpreted / validated: 20 / 3 / True / False
- Browser navigation failures: 0
- Component profiles: 228
- Viewports: desktop, mobile, tablet
- Passive keyboard focus screenshots: 5
- Browser controls activated: 0

## Known limits

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
