# Preferred Design Skill Integration Benchmark

## Scope

This record covers the Impeccable and Taste Skill (`design-taste-frontend`) integration check run on 2026-11-15. The orchestrator was given a fresh copy of `tests/frontend-audit-benchmark/demo-app/` only. The benchmark application was not modified, and no third-party installation, update, initialization command, script, or hook was run.

## Installed capability state

Discovery found both preferred skills and confirmed that the signed-in Codex backend can invoke separate, read-only structured roles with bounded excerpts from their installed `SKILL.md` files.

| Capability | Verified state | Native provider state | Additional limitation |
|---|---|---|---|
| Impeccable | Version 4.3.1 is verifiable from its cached plugin manifest. Its skill-guided Codex role is callable. | Native plugin enablement was not verified; native plugin execution was not claimed. | Role fallback needs no installation for advisory review. |
| Taste Skill | `design-taste-frontend` is installed and callable through its skill-guided Codex role. Its version is not verifiable from local metadata. | Native plugin state was not queried successfully and remains unverified. | The installed copy lacks `scripts/inspect.mjs` and `references/app-screens.md`; its documented app-screen inspector is unavailable. Node.js and a supported browser are present. |

The readiness report recommends enabling Impeccable through the active provider only if native slash-command workflows are desired, and recommends reviewing the documented Taste Skill update procedure to obtain its missing app-screen workflow. Neither recommendation is required for the role-guided fallback. The active provider was Codex; no source or screenshot data was sent to Claude Code.

## Browser evidence

The fixture server returned HTTP 200 for all five routes and for the stylesheet and JavaScript entry point. The capture produced 20 valid PNGs: all 15 required route/viewport pairs (1440, 768, and 390 pixels across five routes) plus five desktop keyboard-focus states. The manifest records zero page errors. The safe, reversible interaction pass tested six controls across all five routes; it made no post-readiness requests and restored the tested state.

These facts establish capture and interaction evidence only. They do not establish that a full audit completed.

## Full audit outcome

A deep, comprehensive Codex audit was started against the isolated copy. The browser pass completed, but the end-to-end audit remained in `AUDITING` for approximately 45 minutes without returning specialist results. It was then interrupted and the workflow session was paused with its screenshot and discovery artifacts intact. No full post-integration audit report or comparable after-score was produced. The interruption was operational; no Codex timeout or quota error was returned, so neither is claimed as the cause.

## Bounded live collaboration check

To validate real skill and image delivery without repeating the long full audit, the coordinator ran the two preferred roles and one independent reviewer against the captured overview desktop screenshot. Each call used the signed-in Codex CLI, a 180-second timeout, and the same screenshot reference and SHA-256.

- Impeccable completed with its skill excerpt attached, one image attached, and schema-valid findings.
- Taste Skill completed independently with its skill excerpt attached, one image attached, and schema-valid findings.
- The cross-disciplinary reviewer completed with one image attached. It returned four challenges and four Director dispositions.
- Both design contributors identified that the revenue chart has no visible value scale. The reviewer merged the duplicate with explicit finding IDs and made the recommendation conditional on the chart's intended use.
- The reviewer treated the subdued note as a conditional readability concern, deferred the subjective brand-distinctiveness recommendation pending product goals, and qualified a lower-card crop as inconclusive without scrolling evidence.
- No production changes were proposed as approved, and no human approval gate was bypassed.

The first bounded cross-review attempt failed semantic target validation because the returned target did not match exactly one supplied observation ID. The raw returned target was not preserved, so its exact form is unknown. The reviewer prompt now lists the exact permitted IDs, the diagnostic includes the rejected target and allowed IDs, and the repeated live check completed successfully.

## Quality comparison

The preserved full benchmark previously reported a provisional 81.5/100 self-assessment; it was not human-scored. The current one-screen collaboration check is narrower and cannot be scored against the full weighted rubric. It demonstrates real image delivery, separate skill-guided contributions, validated evidence references, cross-review, explicit duplicate consolidation, and evidence-based qualification of unsupported design claims. It does not establish an overall audit-quality increase or replace a completed full audit.

## Local artifacts

The isolated run, screenshot gallery, workflow state, paused full-audit session, and supplemental collaboration JSON are under `/private/tmp/frontend-director-impeccable-benchmark-20261114/`. The two-role and cross-review result is `preferred-design-collaborative-live-check-after-fix.json`. These temporary artifacts were not added to the repository or supplied to the auditing calls as project source.
