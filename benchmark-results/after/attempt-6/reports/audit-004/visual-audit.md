# Visual design audit

Audit completion status: **incomplete**
Screenshot states: captured 20; integrity-valid 20; attached to visual backend 15; interpreted True; evidence validated True.

## Rendered evidence

The following browser screenshots were captured from the explicitly supplied URL. Only routes and states present in these images were evaluated.

- `/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png` (HTTP 200)
- `/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop-keyboard-focus.png` (HTTP 200)
- `/` / `tablet` 768×1024: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-tablet.png` (HTTP 200)
- `/` / `mobile` 390×844: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png` (HTTP 200)
- `/analytics/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png` (HTTP 200)
- `/analytics/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop-keyboard-focus.png` (HTTP 200)
- `/analytics/` / `tablet` 768×1024: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png` (HTTP 200)
- `/analytics/` / `mobile` 390×844: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png` (HTTP 200)
- `/customers/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png` (HTTP 200)
- `/customers/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop-keyboard-focus.png` (HTTP 200)
- `/customers/` / `tablet` 768×1024: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png` (HTTP 200)
- `/customers/` / `mobile` 390×844: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png` (HTTP 200)
- `/orders/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png` (HTTP 200)
- `/orders/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop-keyboard-focus.png` (HTTP 200)
- `/orders/` / `tablet` 768×1024: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png` (HTTP 200)
- `/orders/` / `mobile` 390×844: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png` (HTTP 200)
- `/settings/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png` (HTTP 200)
- `/settings/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop-keyboard-focus.png` (HTTP 200)
- `/settings/` / `tablet` 768×1024: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png` (HTTP 200)
- `/settings/` / `mobile` 390×844: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png` (HTTP 200)

## Design identity

Design observations below are limited to the attached rendered evidence. Source-defined design tokens are documented separately and are not treated as proof of rendered use.

### Design identity

A restrained operations dashboard with a cool pale canvas, white bordered cards, compact sans-serif interface text, dark navy navigation on desktop, and recurring teal accents. A compact white header replaces the visible desktop rail at tablet and mobile widths. Settings adds a serif page title and violet save action; Orders uses a larger heading, and Analytics uses squarer panel corners. These page-specific treatments sit within a shared shell and palette.

- The supplied desktop assessments describe a consistent dark navigation rail, pale canvas, and white content panels. The stylesheet defines the canvas, surface, ink, border, teal, and card-radius tokens, alongside the shared shell and sidebar styles (assets/styles.css:1, assets/styles.css:2). — `/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png`).
- Across routes, the supplied tablet and mobile assessments describe a compact header replacing the visible rail. The stylesheet applies the single-column shell and off-canvas sidebar at widths up to 800px (assets/styles.css:8). — `/customers/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png`).
- The teal primary action and light card treatment recur on Customers and Orders; the stylesheet supplies shared button and panel treatments (assets/styles.css:2, assets/styles.css:3). — `/orders/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png`).
- Settings is a deliberate typographic and accent-color exception: its title uses Georgia and its primary button is violet (assets/styles.css:4). The supplied assessments show both treatments at desktop and mobile widths. — `/settings/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png`).

### Experience character

The supplied assessments describe a calm, information-led interface. Desktop screens generally make the page heading and primary action easy to find, then use cards, panels, or table rows to group content. On smaller screens, the shell and many content sections reflow, but Analytics, Orders, and Settings retain content wider than the captured viewport. That horizontal clipping interrupts the orderly scan described for the desktop layouts. The overview and customer directory show more successful small-screen stacking.

### Observed strengths

- The overview separates the greeting and actions from the KPI row and supporting panels at desktop, then retains a two-column KPI grid at tablet width. — `/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-tablet.png`).
- Analytics has a clear desktop sequence from page heading to paired analytics panels and the order explorer; the supplied assessment also identifies teal as a repeated chart and action accent. — `/analytics/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png`).
- Customers presents a clear heading and invite action above its search, filters, and card grid; its cards group customer identity and metrics with a divider. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).
- Orders has a clear desktop progression from heading and actions through search and filters to the complete eight-row grid. — `/orders/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png`).
- Settings distinguishes its page heading from its sans-serif card headings and groups its administrative sections into a two-column desktop layout. — `/settings/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png`).

### Observed concerns

- [Rendered observation] At mobile width, the overview's first viewport is KPI-focused; the fourth card is partly at the capture boundary, and later panels are below the captured area. The assessment treats a denser KPI stack as a product-priority decision, not an established defect. — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).
- [Rendered observation] The Analytics acquisition panel is clipped at tablet width, and the chart card extends beyond the mobile viewport. [Measurement] The supplied runtime inventory reports document widths of 1080px at the 768px tablet viewport and 741px at the 390px mobile viewport. The stylesheet sets a 680px minimum width on the chart frame (assets/styles.css:4). — `/analytics/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png`).
- [Rendered observation] The update caption reads as low-emphasis metadata in the supplied desktop assessment. [Hypothesis] Whether that emphasis needs to increase depends on how operationally important the timestamp is. — `/analytics/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png`).
- [Source observation] A second-card radius override gives Morgan Ellis's customer card a sharper corner treatment than the rest of the grid (assets/styles.css:4). [Rendered observation] The supplied desktop assessment reports this difference. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).
- [Rendered observation] The desktop directory leaves a substantial open canvas below the cards and footer note. The supplied assessment identifies this as a composition choice rather than evidence of a defect. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).
- [Rendered observation] The small-screen order table is clipped horizontally: the tablet capture excludes its trailing action column, while the mobile capture shows only partway through Channel. [Measurement] The supplied runtime inventory reports document widths of 891px at 768px and 886px at 390px. The stylesheet sets the table to a minimum width of 870px and overrides the shared table-shell horizontal scrolling with visible overflow on Orders (assets/styles.css:3, assets/styles.css:4). — `/orders/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png`).
- [Rendered observation] At tablet width, the search field is separated from filter controls, with Date range and Archive wrapping to another row. — `/orders/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png`).
- [Rendered observation] Settings content extends beyond the right edge at mobile and tablet widths, and the Workspace details content reaches into the right column's visible area on desktop. [Measurement] The supplied runtime inventory reports document widths of 781px at 390px mobile and 786px at 768px tablet. [Source observation] The stylesheet sets a 720px minimum width on the fixed-field row (assets/styles.css:4); the single-column form-row rule at the narrow breakpoint does not remove that minimum width (assets/styles.css:9). — `/settings/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png`).
- [Computed-style measurement] The supplied sample reports a 1.76:1 foreground/background ratio for a sidebar avatar selector and describes the initials as faint. The sample excluded transparency and inherited compositing, so it is limited to that supplied color pair. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).

### Cross-screen consistency patterns

- The shared shell, navy sidebar, teal active navigation, pale canvas, and white surfaces recur across the desktop assessments. The common shell and sidebar are defined in the stylesheet (assets/styles.css:1, assets/styles.css:2); supplied computed-style samples report the same sampled sidebar and active-link colors across routes. — `/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png`).
- At widths up to 800px, the stylesheet switches to a one-column shell, moves the sidebar off canvas, shows the mobile menu, and reduces top-bar height and content padding (assets/styles.css:8). The supplied assessments describe that compact-header pattern on all routes. — `/customers/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png`).
- The overview and customer directory reflow their card grids from four and three columns at desktop to two columns by tablet and one column at mobile, as reflected in the supplied assessments and stylesheet rules (assets/styles.css:3, assets/styles.css:7, assets/styles.css:9). — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).
- The heading system is not fully uniform: Settings uses a Georgia title, Customers specifies a 27px page heading, and Orders specifies a 35px heading, while the base page-heading style is 29px (assets/styles.css:2, assets/styles.css:4). — `/settings/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png`).
- The supplied assessments describe compact table labels and row separators on Orders at all three widths, but the columns do not reflow. The source combines a generally scrollable table shell with an Orders-specific visible-overflow override (assets/styles.css:3, assets/styles.css:4). — `/orders/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png`).
- Settings' violet save action is a route-specific accent against the shared teal informational palette and neutral surfaces (assets/styles.css:1, assets/styles.css:4). — `/settings/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png`).

### Patterns to preserve

- Preserve the dark desktop navigation rail, pale canvas, and white panel contrast that recur across the supplied desktop assessments. — `/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png`).
- Preserve the two-column KPI arrangement and broad revenue panel at tablet width. — `/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-tablet.png`).
- Keep the desktop hierarchy of page title, paired analytics panels, and order explorer. — `/analytics/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png`).
- Keep customer identity and metrics grouped within each card with a divider, along with the two-column tablet and one-column mobile card layouts. — `/customers/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png`).
- Keep the clear desktop sequence from page heading through controls to the complete data grid, along with the restrained slate and teal palette. — `/orders/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png`).
- Preserve the serif Settings title, compact uppercase teal eyebrow, and dark desktop navigation rail. — `/settings/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png`).

### Refinements supported by the evidence

- If faster access to trends is a mobile product priority, explore a denser KPI stack while retaining readable labels and values. — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).
- Adjust the chart and panel sizing so analytics content fits narrow viewports, or make chart-level horizontal scrolling clear. — `/analytics/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png`).
- If the update timestamp is operationally important, consider raising its emphasis while keeping it secondary to the panel heading. — `/analytics/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png`).
- Remove the second-card radius exception so Morgan Ellis's card shares the rounded treatment of the rest of the grid. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).
- Contain the wide Orders table in a deliberate horizontal scroll area at small sizes so off-screen fields remain reachable without widening the page. — `/orders/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png`).
- Refine the fixed-width Workspace details row so the form fits its card at mobile and tablet widths and does not extend into the adjacent card at desktop width. — `/settings/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png`).

### Options requiring human approval

- Before making a substantial mobile density change, decide whether first-viewport trend access outweighs the current generous full-width KPI card spacing. — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).

### Route and viewport reading

| Route | Viewport | Hierarchy | Density | Responsive observation | Evidence |
|---|---|---|---|---|---|
| `/` | `desktop` | Supplied rendered assessment: greeting and actions lead, followed by four KPIs, paired revenue and recent-activity panels, then fulfillment health and operational notes. | Moderate to high but grouped; the KPI row and two supporting panels fit the initial content area, with lower panels beginning near the capture boundary. | A persistent left rail and full top bar frame the four-column KPI row and paired panels. Shared shell and sidebar source styles: assets/styles.css:2. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png` |
| `/` | `tablet` | Supplied rendered assessment: greeting and actions sit above a 2×2 KPI grid; the revenue panel follows, with recent activity beginning near the captured image's bottom. | Moderate; KPI cards remain separated and the revenue chart has room for labels and legend. | The compact top bar replaces the visible rail, actions wrap beneath the heading, KPIs use two columns, and panels stack vertically. Grid breakpoints: assets/styles.css:7, assets/styles.css:8. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-tablet.png` |
| `/` | `mobile` | Supplied rendered assessment: compact header, date and greeting, subtitle, actions, then vertically stacked KPI cards. | Cards have generous internal spacing; the captured first viewport is KPI-focused, and the fourth card is partly visible at the capture boundary. | The visible sidebar and profile details are absent from the compact header; actions remain side by side and KPIs use one column. Later panels are below the capture. Small-screen grid rules: assets/styles.css:9. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png` |
| `/analytics/` | `desktop` | Supplied rendered assessment: sidebar and breadcrumb frame the page; Revenue leads into the dominant channel chart and adjacent acquisition metrics, followed by the order explorer. | Moderate and comfortably spaced; the chart is dominant, with acquisition values and summary tiles in the adjacent panel. | Sidebar remains visible, heading and Download action share a row, and both analytics panels fit side by side. Analytics panel and chart-frame overrides: assets/styles.css:4. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png` |
| `/analytics/` | `tablet` | Supplied rendered assessment: title remains prominent and the order explorer is separated beneath the chart; only a narrow edge of the acquisition panel appears at the right. | The visible heading and chart have ample spacing, but the analytics row is wider than the capture and clips the acquisition panel. | Compact header replaces the rail and heading and Download action stack. The analytics row remains overflowing; the supplied runtime inventory reports a 1080px document width at the 768px viewport. Source chart minimum width: assets/styles.css:4. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png` |
| `/analytics/` | `mobile` | Supplied rendered assessment: title and Download action lead into the revenue chart, with the acquisition panel starting below. | The vertical stack has generous spacing, but the chart extends beyond the viewport and only part of the acquisition content appears in the capture. | Compact top bar; heading and action stack. The supplied runtime inventory reports a 741px document width at the 390px viewport. Source chart-frame minimum width: assets/styles.css:4. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png` |
| `/customers/` | `desktop` | Supplied rendered assessment: directory eyebrow and title lead into copy and invite action, then search and filters above a three-column customer grid. | Six cards appear across two rows with generous spacing. The footer note sits beneath them, leaving open canvas below. | Persistent dark sidebar and wide top bar frame the content. The second-card radius exception is present in source (assets/styles.css:4). | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png` |
| `/customers/` | `tablet` | Supplied rendered assessment: compact top bar precedes the directory heading; invite action sits on its own row, followed by search, filters, and a two-column card grid. | All six cards are visible, with room for identity and metric groups. | The rail is out of view and the top bar includes a menu control. Customer grid becomes two columns at the tablet breakpoint (assets/styles.css:7, assets/styles.css:8). | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png` |
| `/customers/` | `mobile` | Supplied rendered assessment: compact top bar and heading lead into full-width invite action, search, filters, and a one-column customer list. | Two cards are fully visible and part of a third appears at the bottom; the visible card spacing is comfortable. | Heading action and toolbar controls stack. The partial third card is at the capture boundary; the assessment does not treat it as a layout failure. One-column grid rule: assets/styles.css:9. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png` |
| `/orders/` | `desktop` | Supplied rendered assessment: dark navigation rail anchors the brand and navigation; content progresses from Orders heading and subtitle to actions, search and filters, result count, and full table. | Moderately dense but readable in the capture; all eight rows, fields, and View buttons fit. | Left rail, full toolbar, and complete table are visible. The source specifies a wide minimum table size for Orders (assets/styles.css:4). | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png` |
| `/orders/` | `tablet` | Supplied rendered assessment: compact header with menu precedes title and actions; search and filters sit above result count and table. | Toolbar wraps across rows. Eight rows are visible vertically, but the trailing action column is outside the captured right edge. | Rail is not visible in the closed-menu capture. Table columns remain wide; runtime inventory reports a document width of 891px at 768px viewport. Orders has an 870px table minimum and visible-overflow override (assets/styles.css:4). | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png` |
| `/orders/` | `mobile` | Supplied rendered assessment: compact header precedes eyebrow and title, actions, search, filters, result count, and table. | Controls occupy several rows; four order rows and part of a fifth are visible, and the table is clipped partway through Channel. | Heading actions share a row and filters wrap across two rows. The table does not reflow. Runtime inventory reports a document width of 886px at 390px viewport; source sets an 870px table minimum and visible overflow (assets/styles.css:4). | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png` |
| `/settings/` | `desktop` | Supplied rendered assessment: breadcrumb and serif page heading lead into two card columns: Workspace details and Team access on the left, Appearance and alerts and Workspace information on the right. Workspace details content reaches beneath the neighboring card's visible area. | Moderate with generous card padding; the form occupies most of the left card, while switch rows and workspace information are comparatively sparse. | Desktop rail and two-column card layout are visible. The source sets a 720px minimum width on the fixed-field row (assets/styles.css:4), consistent with the reported overlap at desktop width. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png` |
| `/settings/` | `tablet` | Supplied rendered assessment: compact top bar precedes eyebrow, title, and subtitle; Workspace details and Team access stack vertically, with Appearance and alerts beginning at the screenshot bottom. | Moderate and vertically spacious, but the first card and its content are clipped at the right edge. | Cards stack and the rail is replaced by the compact header. Runtime inventory reports a 786px document width at 768px viewport; the fixed-field row minimum is 720px (assets/styles.css:4). | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png` |
| `/settings/` | `mobile` | Supplied rendered assessment: compact header with menu, breadcrumb, and notification icons precedes the page title and description, then Workspace details; the next card begins at the capture bottom. | Visible controls are vertically spaced, but the form and its supporting text are clipped horizontally. | Cards continue below the visible area. Runtime inventory reports a 781px document width at 390px viewport; the fixed-field row retains a 720px minimum in source (assets/styles.css:4), while the form-row rule changes to one column at the narrow breakpoint (assets/styles.css:9). | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png` |

Visual analysis limitations:

- This synthesis uses the supplied cross-validated route assessments and project evidence summary; screenshots were not reopened in this pass.
- Source citations refer to the inspected stylesheet assets/styles.css. The supplied materials do not provide line-numbered runtime records.
- Rendered observations are limited to the supplied default-state screenshots and assessment notes; interaction states, focus appearances, horizontal panning, scrolled content, and other viewport sizes were not independently reviewed.
- Document-width values are reproduced from the supplied runtime inventory and are not new measurements from this synthesis.

## Route and viewport coverage

- Source route candidates: 5
- Routes rendered: 5
- Screenshots: 20
- Rendered viewports: desktop, mobile, tablet

## Findings

### VIS-6057ED60 · Workspace details form exceeds its available width

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive layout`
- Description: Rendered observation: at mobile width, the Workspace details card and fields continue beyond the screenshot’s right edge, cutting off text. At tablet width, the card also extends beyond the right edge. At desktop width, the form content extends into the area obscured by the Appearance and alerts card. Source observation: assets/styles.css:4 gives .fixed-field-row a 720px minimum width; the mobile rule at assets/styles.css:9 changes the form row’s column count but does not remove that minimum. The row is used by the workspace details form in settings/index.html:7. This source supports the overflow seen in the screenshots; no additional runtime behavior was inspected.
- Impact: At mobile and tablet widths, part of the settings form is outside the visible page area. At desktop width, the form extends into the neighboring card’s area, weakening the separation between the two settings groups.
- Recommendation: Remove the 720px minimum width from the settings form row and let its fields fit within the Workspace details panel. Keep the fields stacked at the mobile breakpoint, then confirm the form remains inside its card across the supplied widths.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png` (mobile) — Rendered observation: at the supplied mobile viewport, the Workspace details card, fields, and helper copy are cut off at the right edge.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png` (tablet) — Rendered observation: the Workspace details card continues beyond the screenshot’s right edge, so its right boundary and surrounding canvas gutter are not visible.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png` (desktop) — Rendered observation: Workspace details form content reaches into the horizontal area covered by the Appearance and alerts card.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png:4` (mobile) — Source observation: assets/styles.css sets min-width:720px on .settings-page .fixed-field-row.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png:9` (mobile) — Source observation: assets/styles.css changes .settings-page .form-row to one column at the mobile breakpoint but leaves the fixed row minimum width in place.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png:7` (mobile) — Source observation: settings/index.html contains the fixed-field-row in the Workspace details form.

### VIS-7222FEFB · Rendered document exceeds the viewport width

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive_overflow`
- Description: document scroll width 1080px exceeds viewport width 768px
- Impact: Content may be clipped or require unintended horizontal scrolling at this captured viewport.
- Recommendation: Inspect the cited route and breakpoint to identify which rendered element causes the overflow before changing the layout.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png` (analytics:tablet) — document scroll width 1080px exceeds viewport width 768px
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png` (analytics:mobile) — document scroll width 741px exceeds viewport width 390px

### VIS-B464EB67 · The orders table widens the page at tablet and mobile sizes

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive layout`
- Description: Rendered observation: in the tablet screenshot, the trailing action column is beyond the captured right edge; in the mobile screenshot, the table is cut off partway through Channel, so the remaining fields are not initially visible. Source observation: `assets/styles.css:2` gives `.table-shell` horizontal overflow, but `assets/styles.css:4` overrides that for `.orders-page` with `overflow:visible` and sets the table minimum width to 870px. The supplied runtime inventory measures document widths of 891px at the 768px tablet viewport and 886px at the 390px mobile viewport. Inference: the route-specific override allows the wide table to contribute to page-level horizontal overflow instead of containing it in the table shell.
- Impact: On narrow screens, users cannot see all order fields in the initial view, and the supplied measurements show the document wider than the viewport. Page-level horizontal overflow can make the rest of the interface harder to keep in view.
- Recommendation: Restore horizontal scrolling on the orders table shell so the page stays within the viewport and the existing columns remain available by panning the table. This preserves the current table structure but still requires horizontal movement to reach off-screen fields; a compact mobile row layout would reduce panning at the cost of taller rows.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png` (tablet) — Rendered observation: the table extends beyond the viewport to the right of the Date column; its trailing action column is not in view.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png` (mobile) — Rendered observation: only the Order and Customer columns and the start of Channel are visible.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png:4` (mobile) — Source: `assets/styles.css:2` defines horizontal overflow on `.table-shell`; `assets/styles.css:4` overrides it for orders and sets `min-width:870px` on the table.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png` (tablet) — Supplied runtime inventory measurement: document width is 891px at a 768px viewport. The inventory also reports 886px at the 390px mobile viewport.

### VIS-C4210B66 · Rendered document exceeds the viewport width

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive_overflow`
- Description: document scroll width 891px exceeds viewport width 768px
- Impact: Content may be clipped or require unintended horizontal scrolling at this captured viewport.
- Recommendation: Inspect the cited route and breakpoint to identify which rendered element causes the overflow before changing the layout.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png` (orders:tablet) — document scroll width 891px exceeds viewport width 768px
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png` (orders:mobile) — document scroll width 886px exceeds viewport width 390px

### VIS-C5CDFF1E · Sidebar footer initials are much lighter than customer initials

- Severity: **low**; confidence: **medium**; verification: `measured`
- Category: `text contrast`
- Description: Rendered observation: the “NS” letters in the desktop sidebar footer look faint against the mint avatar compared with the darker customer initials. Measurement supplied in the audit inventory: the computed foreground/background sample for `span.avatar` is 1.76:1 against a listed 4.5:1 threshold; this ratio was not independently recalculated, and its stated basis excludes transparency and compositing. Source corroboration: `assets/styles.css:2` sets a muted color on `.sidebar-footer span`, which also matches the footer avatar span.
- Impact: The small workspace monogram is less legible than the customer initials, though the adjacent workspace name remains visible.
- Recommendation: Set a darker foreground specifically for `.sidebar-footer .avatar`, leaving the workspace descriptor text muted.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png` (desktop) — The sidebar footer “NS” initials appear lighter than the customer initials. The 1.76:1 ratio is from the supplied computed-style sample, not a measurement of screenshot pixels.

### VIS-D04FA209 · The mobile first viewport is KPI focused

- Severity: **low**; confidence: **medium**; verification: `observed`
- Category: `mobile information density`
- Description: Rendered observation: the supplied 390×844 screenshot shows the date, greeting, subtitle, paired actions, and first three KPI cards; the fourth card extends beyond the screenshot boundary. The trend and activity panels are not visible in the capture. Source observation: index.html:7 places the four metric cards before the later content panels, and assets/styles.css:9 sets both .grid-4 and .content-grid to one column at widths of 520px or less. Inference: a visitor seeking trend or activity context must scroll past the KPI stack. The screenshot does not show content being lost or clipped from the page; this is a product-priority tradeoff.
- Impact: The captured first viewport exposes KPI values without trend or recent-activity context.
- Recommendation: If quicker access to trends is a product priority on mobile, consider a denser KPI presentation. Keep labels and values easy to scan.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png` (mobile) — The first three cards are fully visible and the fourth is partly visible at the bottom of the 390×844 capture; no trend or activity panel appears within the captured viewport.

### VIS-D44BEA4B · Analytics content extends beyond narrow viewports

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive layout`
- Description: Rendered observations: at mobile width, the revenue card is cut off at the right edge and the visible chart shows only Direct and Retail; the acquisition card also extends beyond the captured width. At tablet width, the chart card fills nearly all the visible analytics row and only the acquisition card's left edge appears at the far right. Source observations: `analytics/index.html:7` puts both cards in `.layout-2`; `assets/styles.css:2` defines `.layout-2` as two equal columns; `assets/styles.css:4` sets `.analytics-page .chart-frame` to a 680px minimum width; and `assets/styles.css:9` switches `.layout-2` to one column only at widths up to 520px. Inference: the chart's minimum width contributes to overflow at mobile, and the two-column row remains active at the 768px tablet viewport. The screenshots do not establish whether users can reveal the clipped content with horizontal scrolling.
- Impact: Some chart categories and acquisition metrics fall outside the visible area at the supplied narrow viewports, making the analytics harder to scan and compare.
- Recommendation: At narrow widths, reduce or remove the chart frame's 680px minimum width and stack the analytics cards by tablet width. If retaining the current chart scale is important for label spacing, contain horizontal scrolling within the chart area and make that scrolling evident; that option preserves chart size but requires users to scroll sideways.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png` (mobile) — The revenue card is clipped at the right edge, with only the Direct and Retail category labels visible; the acquisition card also continues beyond the capture width.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png` (tablet) — Only a narrow slice of the acquisition panel is visible at the far right of the analytics row.

### VIS-D61A8742 · Morgan Ellis card has sharper corners than the other customer cards

- Severity: **low**; confidence: **high**; verification: `observed`
- Category: `component consistency`
- Description: Rendered observation: the second card has noticeably squarer corners than the surrounding cards in the desktop, tablet, and mobile screenshots. Source corroboration: `customers/index.html:7` places Morgan Ellis second in the grid; `assets/styles.css:2` gives `.customer-card` a 14px radius, while `assets/styles.css:4` overrides the second card to 4px. No visible distinction explains this exception.
- Impact: The radius exception interrupts the repeated card treatment and draws attention to one record without an apparent semantic reason.
- Recommendation: Remove the second-card radius override so all customer cards use the shared radius.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png` (desktop) — Morgan Ellis’s second card has sharper corners than the first and third cards.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png` (tablet) — The second card appears squarer than the other cards in the two-column grid.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png` (mobile) — The Morgan Ellis card appears squarer than the Avery Patel card above it.

### VIS-F896E8A4 · Rendered document exceeds the viewport width

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive_overflow`
- Description: document scroll width 786px exceeds viewport width 768px
- Impact: Content may be clipped or require unintended horizontal scrolling at this captured viewport.
- Recommendation: Inspect the cited route and breakpoint to identify which rendered element causes the overflow before changing the layout.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png` (settings:tablet) — document scroll width 786px exceeds viewport width 768px
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png` (settings:mobile) — document scroll width 781px exceeds viewport width 390px


## Evidence gaps

- One non-activating Tab focus state is captured per route at desktop when available. Full keyboard order, hover, active, disabled, loading, empty, and error states were not exhaustively captured.
- Light and dark themes were not compared unless screenshots cover both themes.
- Browser runtime captured 0 console/page error(s); see `runtime-evidence.md` for route and viewport details.
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
