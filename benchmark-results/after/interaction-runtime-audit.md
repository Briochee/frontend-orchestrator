# Benchmark runtime interaction evidence

This is a separate, read-only Playwright evidence pass against the isolated synthetic app at `http://127.0.0.1:8765/`. It used only same-origin requests, changed no fixture files, and recorded zero page errors, console errors, or blocked external requests. Full machine-readable observations are in `interaction-runtime-evidence.json`.

## Observed behavior

| Screen or control | Runtime observation | Evidence state |
|---|---|---|
| Orders search | `NS-1042` returns 1 of 8 orders; combining it with `Failed` returns 0. `Failed` alone returns 1. An unmatched search shows “No matching results.” | Tested |
| Order details dialog | Enter opens the `role=dialog` element with `aria-modal=true`. Focus remains on the triggering View button outside the dialog. Escape leaves the dialog open. Clicking Close hides it, but focus remains on the now-hidden Close button. | Tested |
| Analytics range | Initial value `$10,000` shows 286 qualified orders. End moves the range to `$100,000` and shows 11. | Tested |
| Customer search | `Jordan Lee` shows one card. An unmatched query hides all cards and no empty-state message appears. | Tested |
| Dark mode | `aria-checked` changes `false` to `true` and a success toast appears; computed `body` and `.app-shell` backgrounds remain unchanged. | Tested |
| Email switch | Space changes `aria-checked` from `true` to `false`. | Tested |
| Settings save | Submitting a threshold of 81,000 first reports “Saved successfully” and shows a toast; after 650ms it reports “Sync failed; your changes were not stored.” | Tested |
| Mobile navigation | The menu button sets `aria-expanded=true` and opens the sidebar/backdrop. Escape sets it back to false and closes the sidebar. | Tested |
| Notifications | Clicking the notification control shows “You are all caught up.” | Tested |

## Limits

- These observations are runtime-verified for this fictional fixture and are not claims about other applications.
- The customer card overflow menu and other controls without an explicit safe workflow were not activated.
- The primary audit browser pass remains passive; these interactions are supplemental evidence and are kept distinct from its screenshot set.
