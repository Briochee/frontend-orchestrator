# Frontend audit review scorecard (private evaluator)

Fill this in **after** the audit, with evidence. Keep the raw artifacts unchanged for reproducible comparisons.

| Dimension | Weight | Score (0–5) | Evidence / short rationale |
|---|---:|---:|---|
| Rendered accuracy | 25% | | |
| Design intelligence | 20% | | |
| Component understanding | 15% | | |
| Behavioral depth | 15% | | |
| Evidence and coverage | 15% | | |
| Recommendations | 10% | | |

Weighted score (out of 100): sum(score/5 * weight).

## Required gates before assigning high scores

- Browser source URL, route visits, viewport sizes and screenshot paths are recorded.
- The visual report names actual visual facts and ties them to screenshots.
- The code auditor successfully ran; schema failure cannot be labeled successful.
- The behavioral auditor distinguishes observed interactions from inferred ones.
- The visual auditor actually saw image content; screenshot path references alone are insufficient.
- Source/DOM/computed-style claims are differentiated from screenshots.
- Coverage gaps and tool errors are explicit; a final `complete` state requires appropriate gates.

## Manual F-ID checks

Record which of F01–F22 the report genuinely finds and supports. An unsupported mention does not count. Finding all 22 is **not** mandatory; prioritize critical coverage and evidence.

- Correct, well-supported findings:
- Incorrect or fabricated claims:
- Important missed findings:
- Observed visual inconsistencies outside seed list:
- Low-value generic recommendations:
- Report references valid in real filesystem:

## Retest protocol

Run the same fixture, routes, viewport set, and environment after each orchestrator change. Compare the factuality, coverage and usefulness against the previous run. Do not inflate the score because the report is longer. Keep original reports and screenshots for comparison.
