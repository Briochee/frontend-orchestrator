# HTML sink data-flow review

This is a conservative static trace of straightforward HTML assignments. It does not execute payloads or prove exploitability beyond the source path described.

## `src/components.js:8` — Editable input reaches sink without recognized sanitization

- Context: `toast`
- Sink value: `message`
- Trace assessment: `editable value `team``
- Recognized sanitizer: no
- Data-flow evidence:
  - `src/settings.js:18` — Call site supplies the value written to the HTML sink.
  - `src/settings.js:13` — `team` is read from a DOM or browser-provided value.

## `src/components.js:14` — Constant markup string

- Context: `safeNotice`
- Sink value: `'<strong>Demo workspace</strong> Changes are simulated locally.'`
- Trace assessment: `a constant markup string`
- Recognized sanitizer: no
- Data-flow evidence: no caller or source path was established; this sink is not classified as exploitable.

## `src/orders.js:14` — Rendered value comes from a local literal data array

- Context: `render`
- Sink value: `found.length?found.map(o=>`<tr><td class="order-id">${o.id}</td><td>${customerCell(o.customer,o.email)}</td><td>${o.channel}</td><td>${money(o.total)}</td><td>${statusBadge(o.status)}</td><td>${o.date}</td><td><button class="btn btn-small" data-open="${o.id}">View</button></td></tr>`).join(''):`<tr><td colspan="7">${renderEmpty()}</td></tr>``
- Trace assessment: `a local literal data array`
- Recognized sanitizer: no
- Data-flow evidence:
  - `src/orders.js:11` — Rendered collection is derived from this local assignment.
  - `src/data.js:2` — Imported values originate from a local exported literal array.

Only a direct, recognized DOM/browser input flow is raised as a security finding. Constant template markup and source-local literal datasets are documented without being treated as confirmed injection vulnerabilities.
