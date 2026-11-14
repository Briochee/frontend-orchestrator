# Visual design audit

Audit completion status: **completed**
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

A restrained, data-focused operations dashboard. Across routes, the visual system uses a pale blue-gray workspace, white panels and controls, dark slate text, fine borders, and teal accents, with a dark blue-gray navigation rail on desktop and a compact white header at tablet and mobile widths. Settings adds a serif page title and violet save action, creating a route-specific variation within the shared system. The polished, businesslike character is an inference from the reported page hierarchy and surfaces.

- Rendered observation: the desktop overview pairs a dark navigation rail and pale workspace; teal appears in the active navigation treatment, icons, chart, and primary action. — `/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png`).
- Rendered observation: at tablet and mobile widths, the overview shows a compact white top bar above the pale canvas, with white KPI cards and teal emphasis. — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).
- Rendered observation: Analytics shares the desktop rail, white top bar, pale canvas, teal active navigation treatment, and neutral panel palette. — `/analytics/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png`).
- Rendered observation: Customers uses the shared blue-gray rail, pale workspace, white cards, and teal accents. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).
- Rendered observation: Orders uses the shared desktop shell and neutral workspace, with teal for the active navigation treatment and primary action. — `/orders/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png`).
- Rendered observation: Settings keeps the shared rail, light canvas, and white cards; its title is serif and its save action is violet. — `/settings/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png`).

### Experience character

The supplied assessments describe a calm, information-forward operations interface. Page titles and section labels establish context, while repeated cards, aligned values, and compact status treatments organize operational data. This is a visual inference only; the supplied default-state views do not establish interaction behavior.

### Observed strengths

- The greeting and actions lead into four KPIs, then a side-by-side revenue chart and activity panel, giving the desktop overview a clear progression. — `/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png`).
- At tablet width, the four KPIs form a two-column arrangement before a wide revenue chart. — `/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-tablet.png`).
- On mobile, the greeting, supporting sentence, and paired actions precede the KPI stack; the visible KPI labels and values remain distinguishable. — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).
- The Analytics desktop hierarchy separates the page introduction, revenue and acquisition panels, and order explorer; teal bars and the Download action provide consistent accenting. — `/analytics/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png`).
- The Customers desktop rail separates global navigation from the directory, and the six customer cards distinguish profile details from account metrics. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).
- At tablet width, customer cards group identity details above a divider and account metrics below it. — `/customers/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png`).
- On mobile, the customer invite and search controls span the content width, with the two filters grouped above the single-column card list. — `/customers/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png`).
- The Orders desktop sequence runs from workspace context and page title through actions, filters, results count, and a table whose visible rows and fields fit in the capture. — `/orders/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png`).
- Thin row dividers, aligned values, and distinct green, amber, and red status pills aid scanning in the desktop Orders table. — `/orders/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png`).
- The Settings desktop breadcrumb and serif title establish the page, while panel headings distinguish workspace details, team access, appearance, and workspace information. — `/settings/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png`).
- In the supplied mobile Settings view, stacked labels and controls maintain a clear vertical reading order. — `/settings/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png`).

### Observed concerns

- Capture limitation: three KPI cards are fully visible and part of a fourth appears; the chart and activity panels are below the captured area. This frame alone does not demonstrate a layout failure. — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).
- Capture limitation: the desktop screenshot cuts off the lower portions of the fulfillment and operational notes panels. — `/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png`).
- Rendered observation: the Acquisition mix panel is mostly beyond the right edge of the tablet capture. The supplied runtime measurement reports a document width of 1080 px at a 768 px viewport. — `/analytics/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png`).
- Rendered observation: the mobile chart extends beyond the right edge, hiding later bars and labels. The supplied runtime measurement reports a document width of 741 px at a 390 px viewport. — `/analytics/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png`).
- Assessment-reported source observation: the second customer card has a smaller corner radius than its peers at all supplied viewport sizes. The visible content does not explain the distinction. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).
- Capture limitation: only the top of the customer list is shown; the appearance below Jordan Lee's partially visible card cannot be assessed from this frame. — `/customers/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png`).
- Rendered observation: the wide Orders table retains its columns at narrow widths, cropping later fields and row actions. The supplied runtime measurements report document widths of 891 px at a 768 px tablet viewport and 886 px at a 390 px mobile viewport. — `/orders/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png`).
- Rendered observation: at tablet width the Orders toolbar wraps, and the View action column falls outside the visible area. — `/orders/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png`).
- Rendered observation: the Settings Workspace details panel and form are cropped at the right edge on mobile. The supplied runtime measurement reports a document width of 781 px at a 390 px viewport. — `/settings/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png`).
- Rendered observation: the Settings Workspace details panel reaches the right edge at tablet width, leaving its right boundary outside the capture. The supplied runtime measurement reports a document width of 786 px at a 768 px viewport. — `/settings/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png`).
- Rendered observation: on desktop, content in the left Settings column extends behind right-side cards, weakening the separation between sections. — `/settings/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png`).

### Cross-screen consistency patterns

- The shared shell is stable across routes: desktop uses a dark rail and white top bar, while tablet and mobile use a compact white header; both retain the pale workspace and dark text. — `/analytics/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png`).
- White panels and cards, fine borders, rounded corners, and muted supporting text recur across the routes. Settings assessments also report faint panel shadows. — `/settings/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png`).
- Teal consistently signals emphasis in active navigation, page eyebrows, charts, icons, and primary actions. Settings is a route-specific exception for the save action, which is violet. — `/settings/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png`).
- The overview keeps the date eyebrow, greeting, and supporting sentence in the same order at all supplied sizes; actions move from beside the greeting on desktop to below the introduction at smaller sizes. — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).
- The Customers card structure and palette persist from desktop through tablet to mobile as the grid changes from three columns to two and then one; the reported second-card radius exception persists at each size. — `/customers/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png`).
- Orders controls retain white surfaces, light borders, and dark labels, while teal emphasizes the New order action across supplied sizes. At narrower widths, the table keeps its wide column structure and is cropped. — `/orders/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png`).

### Patterns to preserve

- Keep the distinct dark desktop rail and compact top-bar treatment at smaller viewport sizes. — `/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png`).
- Retain the overview’s repeated KPI hierarchy and teal icon accents. — `/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png`).
- Preserve Analytics’ title hierarchy, neutral palette, teal data emphasis, and desktop panel arrangement. — `/analytics/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png`).
- Keep Customers’ cool-gray canvas, white bordered cards, teal eyebrow and primary action, and the mobile sequence of heading, invite, search and filters, then cards. — `/customers/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png`).
- Preserve the Orders desktop title hierarchy, neutral workspace, aligned table rows, and compact status colors. — `/orders/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png`).
- Keep the Settings title’s serif contrast with sans-serif controls and panel headings, along with the restrained shared palette and card treatment. — `/settings/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png`).

### Refinements supported by the evidence

- At tablet width, fit both Analytics panels within the viewport; stacking them would reveal the Acquisition mix panel in the available width. — `/analytics/` / `tablet` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png`).
- At mobile width, fit the Analytics chart to its panel or provide a clearly indicated contained scroll area so remaining bars and labels can be reached. — `/analytics/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png`).
- Make the Orders table fields and row action reachable at narrow widths. Restoring horizontal scrolling preserves the current table structure; stacked rows would take more vertical space. — `/orders/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png`).
- Allow the Settings form row and panel to fit the available width when the layout stacks so the form fields and panel boundary remain visible. — `/settings/` / `mobile` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png`).

### Options requiring human approval

- Decide whether to keep the reported smaller corner radius on the second Customers card. If it is intentional, clarify the visible reason for the distinct treatment. — `/customers/` / `desktop` (`/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png`).

### Route and viewport reading

| Route | Viewport | Hierarchy | Density | Responsive observation | Evidence |
|---|---|---|---|---|---|
| `/` | `desktop` | The sidebar and top bar frame the workspace. The greeting and actions lead into four equally presented KPI cards. The revenue chart and recent activity share the next row, with fulfillment and notes starting below. | The visible upper dashboard is moderately dense, with clear gaps between cards and panels. The lower row is only partly captured. | The dark navigation rail is visible. KPIs form one row, and chart and activity panels are side by side. The screenshot ends partway through the lower panels. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png` |
| `/` | `tablet` | A compact top bar precedes the greeting and actions. Four KPIs occupy two rows of two, followed by a wide revenue chart; recent activity begins below it. | The KPI and chart areas have visible spacing. The chart takes most of the width before the capture reaches the activity section. | The desktop rail is not visible in the screenshot and a menu icon appears in the top bar. The image shows the beginning of recent activity but not the rest of the lower page. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-tablet.png` |
| `/` | `mobile` | The compact top bar is followed by the date, greeting, supporting sentence, paired actions, and vertically stacked KPI cards. Three cards are fully visible and part of the fourth appears at the bottom. | There is ample space within each visible KPI card, while vertical stacking means the captured first screen is primarily greeting and KPI content. | The desktop rail is not visible in the screenshot; the top bar includes a menu icon. Actions remain side by side. Chart and activity panels are below the captured area. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png` |
| `/analytics/` | `desktop` | The heading leads into the side-by-side Revenue by channel and Acquisition mix panels, followed by the full-width High-value order explorer and a centered note. Download sits at the upper right. | Comfortable, with clear separation between the chart, acquisition metrics, and order explorer. | The full-height sidebar and desktop top bar remain visible. Both analytics panels fit side by side. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png` |
| `/analytics/` | `tablet` | The heading and Download action stack vertically. The order explorer follows the chart row. Only a narrow edge of the Acquisition mix panel appears at the far right. | The visible chart panel and order explorer have generous internal spacing; horizontal fit is the main visual concern. | The sidebar is replaced by a compact header with a menu icon. The analytics panels remain in a horizontal row, with the second panel mostly outside the screenshot. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png` |
| `/analytics/` | `mobile` | The compact header is followed by the eyebrow, title, wrapped description, full-width Download action, and chart card. The Acquisition mix panel begins below the chart. | The introduction and visible chart content are comfortably spaced, but horizontal overflow hides part of the chart. | The navigation rail is replaced by a menu icon, and the heading/action region stacks. The chart card extends beyond the right edge, leaving later bars and labels out of view. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png` |
| `/customers/` | `desktop` | The side rail and top bar frame the page. The teal uppercase eyebrow leads into the bold title and muted subtitle; the invite action sits opposite the heading. Search and filter controls precede the customer cards. | Six cards form a three-column by two-row grid. The cards separate profile details from metrics, with substantial open canvas below the content in the supplied frame. | The full navigation rail is visible. Search is on the left of the toolbar and filters on the right; the invite action aligns with the page heading. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png` |
| `/customers/` | `tablet` | A compact white top bar precedes the eyebrow, title, and subtitle. The invite action sits below the heading and above the search and filter row; the cards follow. | Six cards form a two-column by three-row grid. Profile details and account metrics remain visually separated within each card. | The side rail is not visible in the screenshot; a menu icon appears in the top bar. The invite action moves below the heading, and the grid changes to two columns. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png` |
| `/customers/` | `mobile` | The top bar and menu icon precede the eyebrow, title, and subtitle. A full-width invite action comes next, then search and filters, followed by the customer cards. | The cards stack vertically with the same profile-and-metrics structure. Two cards are fully visible and a third is partially visible within the supplied frame. | The side rail is not visible in the screenshot; a menu icon appears in the top bar. The invite action and search field span the content width, the filters sit side by side, and the cards use a single column. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png` |
| `/orders/` | `desktop` | The sidebar and breadcrumb establish workspace context; the title anchors the page; actions and filters precede the results count and table. | The eight rows and six labeled fields plus the View action fit in the supplied view, with clear row separation. | The full sidebar and workspace metadata remain visible. All table columns and row actions fit in the screenshot. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png` |
| `/orders/` | `tablet` | The compact top bar precedes a stacked title block, page actions, wrapped filters, results count, and table. | Visible table values remain legible, but the View action column extends beyond the right edge. | The desktop sidebar is replaced visually by a menu control. Header actions and filters wrap; the table keeps its wide layout. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png` |
| `/orders/` | `mobile` | The compact top bar and breadcrumb precede the page heading, action row, full-width search, wrapped filters, results count, and table. | The controls occupy several rows. Only the first table columns fit in the visible area. | The desktop sidebar is replaced visually by a menu control. The filters wrap, and the wide table is cropped after the beginning of Channel. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png` |
| `/settings/` | `desktop` | The breadcrumb and large serif Settings heading lead into the page. Workspace details anchors the left column; Appearance and alerts and Workspace information sit in the right column. The violet save button is the most prominent action. Left-column content extending behind the right-side cards disrupts the otherwise clear grouping. | Moderate density, with generous panel padding and gaps between sections; labels and supporting copy are compact. | Two columns are visible, but left-column form and team-access content extend behind adjacent cards. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png` |
| `/settings/` | `tablet` | The Settings heading remains prominent above the full-width Workspace details panel, followed by Team access. Appearance and alerts begins near the bottom of the screenshot. | Comfortable vertical spacing, with contact email and region arranged side by side in the visible form. | The cards stack vertically, but the Workspace details panel and form content extend to the screenshot’s right edge. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png` |
| `/settings/` | `mobile` | A compact top bar and wrapped page subtitle lead into Workspace details. The title, labels, and save action remain easy to scan vertically. | The visible form has ample vertical separation. The next card is only partly visible at the bottom of the supplied screenshot. | Navigation is collapsed into a compact header and the form fields stack, but the Workspace details panel and its content are cropped at the right edge. | `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png` |

Visual analysis limitations:

- This is a synthesis of the supplied cross-validated assessments; screenshots were not reopened during this pass.
- Rendered observations, measurements, and inferences are identified in the claims where relevant. No new visual measurements were computed.
- The supplied assessments provide screenshot paths but no repository line numbers for source claims.
- The captures show default states only; interactive states and behavior were not assessed.
- Several mobile and tablet captures end before lower-page content is visible, so those sections cannot be assessed from the supplied frames.

## Route and viewport coverage

- Source route candidates: 5
- Routes rendered: 5
- Screenshots: 20
- Rendered viewports: desktop, mobile, tablet

## Findings

### VIS-4EBF6DF0 · Morgan Ellis’s card has a distinct corner treatment

- Severity: **low**; confidence: **high**; verification: `observed`
- Category: `surface consistency`
- Description: Morgan Ellis’s card has noticeably sharper corners than the other customer cards in the desktop, tablet, and mobile screenshots. Source inspection finds an explicit second-card radius override, so this is an authored visual difference rather than an unexplained rendering variation. The page does not show a corresponding status or other visible reason for the distinction.
- Impact: The isolated radius treatment interrupts the otherwise repeated card styling, and its purpose is not apparent from the displayed customer information.
- Recommendation: Confirm whether the second-card exception is intentional. If no distinction is intended, remove the override so the card uses the shared radius; if it is intended, make the reason for the distinction visible.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png` (desktop) — Morgan Ellis’s first-row card appears sharper-cornered than the other five cards.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png` (tablet) — Morgan Ellis’s card retains the sharper corners in the two-column layout.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png` (mobile) — The fully visible Morgan Ellis card has sharper corners than the Avery Patel card above it.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png:4` (desktop) — Source: `assets/styles.css:2` gives `.customer-card` a 14px radius; `assets/styles.css:4` sets `.customers-page .customer-card:nth-child(2)` to 4px. `customers/index.html:7` places Morgan Ellis second in the grid. The stylesheet establishes that the difference is explicit, but not its product rationale.

### VIS-7222FEFB · Rendered document exceeds the viewport width

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive_overflow`
- Description: document scroll width 1080px exceeds viewport width 768px
- Impact: Content may be clipped or require unintended horizontal scrolling at this captured viewport.
- Recommendation: Inspect the cited route and breakpoint to identify which rendered element causes the overflow before changing the layout.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png` (analytics:tablet) — document scroll width 1080px exceeds viewport width 768px
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png` (analytics:mobile) — document scroll width 741px exceeds viewport width 390px

### VIS-B7A34319 · Order table is cropped at tablet and mobile widths

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive layout`
- Description: Rendered observation: in the supplied mobile view, Order and Customer are visible with only part of Channel; Amount, Status, Date, and the View actions are beyond the right edge. In the tablet view, the table is visible through Date, but the View actions are beyond the right edge. Source observation: `orders/index.html:7` defines the `.table-shell` and table; `assets/styles.css:2` gives `.table-shell` horizontal auto overflow, while `assets/styles.css:4` sets `.orders-page .table-shell { overflow: visible }` and `.orders-page table { min-width: 870px }`. Inference: the route-specific overflow rule removes the table shell’s horizontal overflow while keeping the table wider than the available content, matching the cropped screenshots. No scrolling behavior was exercised.
- Impact: The order attributes and row actions cannot all be scanned in the initial narrow viewport, reducing the table’s usefulness for quick review at these sizes.
- Recommendation: Restore horizontal scrolling on `.table-shell` at narrow widths; its base rule already defines `overflow-x: auto` in `assets/styles.css:2`. This keeps the existing table structure but requires horizontal scrolling to reach later columns. A compact stacked row layout would expose selected fields together but use more vertical space and change the table’s scanning pattern.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png` (mobile) — Only Order, Customer, and the beginning of Channel are visible in the table area.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png` (tablet) — Date values are visible, but the final View actions column is outside the captured viewport.

### VIS-C4210B66 · Rendered document exceeds the viewport width

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive_overflow`
- Description: document scroll width 891px exceeds viewport width 768px
- Impact: Content may be clipped or require unintended horizontal scrolling at this captured viewport.
- Recommendation: Inspect the cited route and breakpoint to identify which rendered element causes the overflow before changing the layout.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-tablet.png` (orders:tablet) — document scroll width 891px exceeds viewport width 768px
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-mobile.png` (orders:mobile) — document scroll width 886px exceeds viewport width 390px

### VIS-DD67CD35 · Settings content exceeds its available width

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive layout`
- Description: Rendered observation: at desktop width, left-column form content extends behind the right-side cards. At tablet and mobile widths, the Workspace details card and its form are cropped at the right edge. Source observation: `settings/index.html:7` applies the `fixed-field-row` class; `assets/styles.css:4` sets that row to `min-width:720px`. The layout stacks at `assets/styles.css:7`, and the form fields stack at `assets/styles.css:9`, but neither rule resets that minimum. Inference: the retained minimum width causes the narrow-screen clipping and contributes to the desktop overlap.
- Impact: The screenshots show part of the settings form hidden at tablet and mobile widths, and desktop content visually competing with or passing behind the right-side cards.
- Recommendation: Remove the 720px minimum for this row or override it when the settings grid stacks; allow the fields to fit the available column. This may stack or narrow fields earlier, while preserving the two-column desktop form where space permits.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png` (desktop) — The left-column content visibly continues beneath the adjacent right-side cards.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-tablet.png` (tablet) — The Workspace details panel and form reach the screenshot’s right edge without a visible right boundary.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-mobile.png` (mobile) — The Workspace details panel and form controls are cut off at the viewport’s right edge.

### VIS-EC4BFE9A · Analytics content extends beyond tablet and mobile viewports

- Severity: **medium**; confidence: **high**; verification: `observed`
- Category: `responsive overflow`
- Description: In the tablet screenshot, the Acquisition mix panel is mostly beyond the right edge. In the mobile screenshot, the chart card and chart continue beyond the right edge, and only Direct and Retail are visible. The CSS keeps `.layout-2` in two columns except below 520px, while `.analytics-page .chart-frame` retains a 680px minimum width; the analytics markup places both panels inside `.layout-2` (assets/styles.css:2,4,9; analytics/index.html:7).
- Impact: The supplied tablet view does not show the Acquisition mix content, and the mobile view omits later channel bars and labels. Neither screenshot shows a dedicated horizontal-scroll cue for this content.
- Recommendation: At tablet widths, stack the two analytics panels so the Acquisition mix panel remains visible. At mobile widths, either size the chart to the panel or place it in an explicitly scrollable chart region with a visible cue. Scaling makes all bars visible at once but reduces their spacing; contained scrolling preserves spacing but requires a horizontal gesture.
- Evidence:
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-tablet.png` (tablet) — The Acquisition mix panel is reduced to a narrow visible edge at the right boundary. Source corroboration: `assets/styles.css:2` retains a two-column grid; `analytics/index.html:7` places both panels in it.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png` (mobile) — The chart card continues past the right edge, and only the first two bars and labels appear. Source corroboration: `assets/styles.css:4` sets a 680px minimum chart-frame width; `assets/styles.css:9` changes `.layout-2` to one column below 520px.
  - `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-mobile.png:4` (mobile) — Implementation observation: `assets/styles.css:2` declares `.layout-2` as two equal columns, `assets/styles.css:4` sets `.analytics-page .chart-frame` to `min-width:680px`, and `assets/styles.css:9` applies the one-column override only below 520px. `analytics/index.html:7` contains both panels in the grid.

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
- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.
