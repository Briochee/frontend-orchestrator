# Color-system analysis

Source declarations are distinguished from actual computed browser samples. Contrast is calculated only for opaque foreground/background pairs with an unambiguous computed background; it is not a complete WCAG audit.

## Source color palette

| Color | Declarations | Source files |
|---|---:|---|
| `#5850b5` | 2 | `assets/styles.css` |
| `#167c87` | 1 | `assets/styles.css` |
| `#182936` | 1 | `assets/styles.css` |
| `#236e74` | 1 | `assets/styles.css` |
| `#238a70` | 1 | `assets/styles.css` |
| `#24645f` | 1 | `assets/styles.css` |
| `#253e48` | 1 | `assets/styles.css` |
| `#25585b` | 1 | `assets/styles.css` |
| `#255f69` | 1 | `assets/styles.css` |
| `#263d4c` | 1 | `assets/styles.css` |
| `#277d78` | 1 | `assets/styles.css` |
| `#2b7b5c` | 1 | `assets/styles.css` |
| `#314653` | 1 | `assets/styles.css` |
| `#31837e` | 1 | `assets/styles.css` |
| `#36a98b` | 1 | `assets/styles.css` |
| `#36b4a3` | 1 | `assets/styles.css` |
| `#3a786d` | 1 | `assets/styles.css` |
| `#435267` | 1 | `assets/styles.css` |
| `#486b75` | 1 | `assets/styles.css` |
| `#526174` | 1 | `assets/styles.css` |
| `#5d6b7b` | 1 | `assets/styles.css` |
| `#7d8b9c` | 1 | `assets/styles.css` |
| `#8390a0` | 1 | `assets/styles.css` |
| `#8d9aab` | 1 | `assets/styles.css` |
| `#8ea3b2` | 1 | `assets/styles.css` |
| `#94a6b6` | 1 | `assets/styles.css` |
| `#96a2b1` | 1 | `assets/styles.css` |
| `#97620f` | 1 | `assets/styles.css` |
| `#97a3b1` | 1 | `assets/styles.css` |
| `#9aafbc` | 1 | `assets/styles.css` |
| `#a84444` | 1 | `assets/styles.css` |
| `#a9b5c2` | 1 | `assets/styles.css` |
| `#afc0cc` | 1 | `assets/styles.css` |
| `#b5bfcb` | 1 | `assets/styles.css` |
| `#b5c0cb` | 1 | `assets/styles.css` |
| `#bd4849` | 1 | `assets/styles.css` |
| `#bfcad4` | 1 | `assets/styles.css` |
| `#cbd8e2` | 1 | `assets/styles.css` |
| `#ccd7df` | 1 | `assets/styles.css` |
| `#d0e7e3` | 1 | `assets/styles.css` |
| `#e0f2e9` | 1 | `assets/styles.css` |
| `#eaf5f3` | 1 | `assets/styles.css` |
| `#ecf5f6` | 1 | `assets/styles.css` |
| `#edf1f6` | 1 | `assets/styles.css` |
| `#eef1f5` | 1 | `assets/styles.css` |
| `#f0fdfb` | 1 | `assets/styles.css` |
| `#f1cecc` | 1 | `assets/styles.css` |
| `#f1f5f8` | 1 | `assets/styles.css` |
| `#f1fafb` | 1 | `assets/styles.css` |
| `#f3faf7` | 1 | `assets/styles.css` |
| `#fbfcfe` | 1 | `assets/styles.css` |
| `#fbfdfd` | 1 | `assets/styles.css` |
| `#fde5e4` | 1 | `assets/styles.css` |
| `#fff0d5` | 1 | `assets/styles.css` |
| `rgba(12,24,38,.45)` | 1 | `assets/styles.css` |
| `rgba(12,24,38,.55)` | 1 | `assets/styles.css` |

## Color tokens

| Token | Value | File |
|---|---|---|
| `--border` | `#e3e8ef` | `assets/styles.css` |
| `--brand-100` | `#d9f0ec` | `assets/styles.css` |
| `--brand-600` | `#147d79` | `assets/styles.css` |
| `--brand-700` | `#0e6561` | `assets/styles.css` |
| `--canvas` | `#f5f7fb` | `assets/styles.css` |
| `--gold` | `#d98a1b` | `assets/styles.css` |
| `--ink-400` | `#8693a5` | `assets/styles.css` |
| `--ink-600` | `#59667a` | `assets/styles.css` |
| `--ink-700` | `#3c4a5e` | `assets/styles.css` |
| `--ink-900` | `#202c3b` | `assets/styles.css` |
| `--red` | `#bd4849` | `assets/styles.css` |
| `--shadow` | `0 4px 16px rgba(31,46,69,.04)` | `assets/styles.css` |
| `--surface` | `#ffffff` | `assets/styles.css` |

## Rendered contrast samples

| Route / viewport | Selector | Foreground / background | Ratio | Sampled threshold |
|---|---|---|---:|---:|
| `/` / `home:desktop` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `a.nav-link` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `a.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `article.metric-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.metric-icon` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `article.metric-card#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.metric-icon#2` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `article.metric-card#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.metric-icon#3` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `article.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `button.btn.btn-small` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `i.legend-dot` | `rgb(89, 102, 122)` / `rgb(20, 125, 121)` | 1.18:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `i.legend-dot.gray` | `rgb(89, 102, 122)` / `rgb(191, 202, 212)` | 3.5:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `article.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.activity-icon` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `span.activity-icon#2` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `span.activity-icon#3` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `article.panel#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `span.badge.active` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop` | `div.track` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `div.track#2` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `div.track#3` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `div.notice` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `a.nav-link` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `a.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `article.metric-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.metric-icon` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `article.metric-card#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.metric-icon#2` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `article.metric-card#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.metric-icon#3` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `article.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `button.btn.btn-small` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `i.legend-dot` | `rgb(89, 102, 122)` / `rgb(20, 125, 121)` | 1.18:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `i.legend-dot.gray` | `rgb(89, 102, 122)` / `rgb(191, 202, 212)` | 3.5:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `article.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.activity-icon` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.activity-icon#2` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.activity-icon#3` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `article.panel#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `span.badge.active` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:desktop:focus-1` | `div.track` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `div.track#2` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `div.track#3` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `div.notice` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:desktop:focus-1` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `a.nav-link` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `a.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `article.metric-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.metric-icon` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `article.metric-card#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.metric-icon#2` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `article.metric-card#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.metric-icon#3` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `article.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `button.btn.btn-small` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `i.legend-dot` | `rgb(89, 102, 122)` / `rgb(20, 125, 121)` | 1.18:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `i.legend-dot.gray` | `rgb(89, 102, 122)` / `rgb(191, 202, 212)` | 3.5:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `article.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.activity-icon` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `span.activity-icon#2` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `span.activity-icon#3` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `article.panel#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `span.badge.active` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:tablet` | `div.track` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `div.track#2` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `div.track#3` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `div.notice` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:tablet` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `a.nav-link` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `a.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `article.metric-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.metric-icon` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `article.metric-card#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.metric-icon#2` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `article.metric-card#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.metric-icon#3` | `rgb(49, 131, 126)` / `rgb(234, 245, 243)` | 4.03:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `article.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `button.btn.btn-small` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `i.legend-dot` | `rgb(89, 102, 122)` / `rgb(20, 125, 121)` | 1.18:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `i.legend-dot.gray` | `rgb(89, 102, 122)` / `rgb(191, 202, 212)` | 3.5:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `article.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.activity-icon` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `span.activity-icon#2` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `span.activity-icon#3` | `rgb(39, 125, 120)` / `rgb(236, 245, 246)` | 4.42:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `article.panel#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `span.badge.active` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/` / `home:mobile` | `div.track` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `div.track#2` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `div.track#3` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `div.notice` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/` / `home:mobile` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `input` | `rgb(16, 16, 16)` / `rgb(255, 255, 255)` | 19.03:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `a.nav-link#3` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/analytics/` / `analytics:desktop` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/analytics/` / `analytics:desktop` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `article.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `article.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `div.track` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `div.track#2` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `div.track#3` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `section.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `input` | `rgb(16, 16, 16)` / `rgb(255, 255, 255)` | 19.03:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `a.nav-link#3` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `article.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `article.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `div.track` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `div.track#2` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `div.track#3` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `section.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:desktop:focus-1` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `input` | `rgb(16, 16, 16)` / `rgb(255, 255, 255)` | 19.03:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `a.nav-link#3` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/analytics/` / `analytics:tablet` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/analytics/` / `analytics:tablet` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `article.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `article.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `div.track` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `div.track#2` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `div.track#3` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `section.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:tablet` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `input` | `rgb(16, 16, 16)` / `rgb(255, 255, 255)` | 19.03:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `a.nav-link#3` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/analytics/` / `analytics:mobile` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/analytics/` / `analytics:mobile` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `article.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `article.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `div.track` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `div.track#2` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `div.track#3` | `rgb(32, 44, 59)` / `rgb(238, 241, 245)` | 12.48:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `section.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/analytics/` / `analytics:mobile` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/customers/` / `customers:desktop` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/customers/` / `customers:desktop` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `div.search-box` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `button.btn#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `article.customer-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `span.avatar#3` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `article.customer-card#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `article.customer-card#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `div.search-box` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `button.btn#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `article.customer-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `span.avatar#3` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `article.customer-card#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `article.customer-card#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:desktop:focus-1` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/customers/` / `customers:tablet` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/customers/` / `customers:tablet` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `div.search-box` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `button.btn#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `article.customer-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `span.avatar#3` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `article.customer-card#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `article.customer-card#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:tablet` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/customers/` / `customers:mobile` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/customers/` / `customers:mobile` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `div.search-box` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `button.btn#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `article.customer-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `span.avatar#3` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `article.customer-card#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `article.customer-card#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/customers/` / `customers:mobile` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `a.nav-link#2` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.nav-count` | `rgb(240, 253, 251)` / `rgb(49, 70, 83)` | 9.45:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `div.search-box` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `select` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn#3` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn.btn-danger` | `rgb(189, 72, 73)` / `rgb(255, 255, 255)` | 5.02:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `section.table-shell` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.avatar#3` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge.paid` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge-dot` | `rgb(43, 123, 92)` / `rgb(43, 123, 92)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn.btn-small` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge.pending` | `rgb(151, 98, 15)` / `rgb(255, 240, 213)` | 4.59:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge-dot#2` | `rgb(151, 98, 15)` / `rgb(151, 98, 15)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn.btn-small#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge.paid#2` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge-dot#3` | `rgb(43, 123, 92)` / `rgb(43, 123, 92)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn.btn-small#3` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge.failed` | `rgb(168, 68, 68)` / `rgb(253, 229, 228)` | 4.9:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge.paid#3` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop` | `span.badge.pending#2` | `rgb(151, 98, 15)` / `rgb(255, 240, 213)` | 4.59:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `div.modal-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `button.btn.btn-primary#2` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `a.nav-link#2` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.nav-count` | `rgb(240, 253, 251)` / `rgb(49, 70, 83)` | 9.45:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `div.search-box` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `select` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn#3` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn.btn-danger` | `rgb(189, 72, 73)` / `rgb(255, 255, 255)` | 5.02:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `section.table-shell` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.avatar#3` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge.paid` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge-dot` | `rgb(43, 123, 92)` / `rgb(43, 123, 92)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn.btn-small` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge.pending` | `rgb(151, 98, 15)` / `rgb(255, 240, 213)` | 4.59:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge-dot#2` | `rgb(151, 98, 15)` / `rgb(151, 98, 15)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn.btn-small#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge.paid#2` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge-dot#3` | `rgb(43, 123, 92)` / `rgb(43, 123, 92)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn.btn-small#3` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge.failed` | `rgb(168, 68, 68)` / `rgb(253, 229, 228)` | 4.9:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge.paid#3` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `span.badge.pending#2` | `rgb(151, 98, 15)` / `rgb(255, 240, 213)` | 4.59:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `div.modal-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `button.btn.btn-primary#2` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:desktop:focus-1` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `a.nav-link#2` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.nav-count` | `rgb(240, 253, 251)` / `rgb(49, 70, 83)` | 9.45:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:tablet` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:tablet` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `div.search-box` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `select` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn#3` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn.btn-danger` | `rgb(189, 72, 73)` / `rgb(255, 255, 255)` | 5.02:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `section.table-shell` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.avatar#3` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge.paid` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge-dot` | `rgb(43, 123, 92)` / `rgb(43, 123, 92)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn.btn-small` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge.pending` | `rgb(151, 98, 15)` / `rgb(255, 240, 213)` | 4.59:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge-dot#2` | `rgb(151, 98, 15)` / `rgb(151, 98, 15)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn.btn-small#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge.paid#2` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge-dot#3` | `rgb(43, 123, 92)` / `rgb(43, 123, 92)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn.btn-small#3` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge.failed` | `rgb(168, 68, 68)` / `rgb(253, 229, 228)` | 4.9:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge.paid#3` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:tablet` | `span.badge.pending#2` | `rgb(151, 98, 15)` / `rgb(255, 240, 213)` | 4.59:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `div.modal-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `button.btn.btn-primary#2` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:tablet` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `a.nav-link#2` | `rgb(240, 253, 251)` / `rgb(37, 88, 91)` | 7.67:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.nav-count` | `rgb(240, 253, 251)` / `rgb(49, 70, 83)` | 9.45:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:mobile` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:mobile` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `div.search-box` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `select` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn#3` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn.btn-danger` | `rgb(189, 72, 73)` / `rgb(255, 255, 255)` | 5.02:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `section.table-shell` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.avatar#3` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge.paid` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge-dot` | `rgb(43, 123, 92)` / `rgb(43, 123, 92)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn.btn-small` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge.pending` | `rgb(151, 98, 15)` / `rgb(255, 240, 213)` | 4.59:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge-dot#2` | `rgb(151, 98, 15)` / `rgb(151, 98, 15)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn.btn-small#2` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge.paid#2` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge-dot#3` | `rgb(43, 123, 92)` / `rgb(43, 123, 92)` | 1.0:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn.btn-small#3` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge.failed` | `rgb(168, 68, 68)` / `rgb(253, 229, 228)` | 4.9:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge.paid#3` | `rgb(43, 123, 92)` / `rgb(224, 242, 233)` | 4.41:1 | 4.5:1 (below sampled threshold) |
| `/orders/` / `orders:mobile` | `span.badge.pending#2` | `rgb(151, 98, 15)` / `rgb(255, 240, 213)` | 4.59:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `div.modal-card` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `button.btn.btn-primary#2` | `rgb(255, 255, 255)` / `rgb(20, 125, 121)` | 4.95:1 | 4.5:1 (meets sampled threshold) |
| `/orders/` / `orders:mobile` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:desktop` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:desktop` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `section.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `input#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `select` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `input#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(88, 80, 181)` | 6.5:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `section.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `div.notice` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `section.panel#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `button.switch` | `rgb(0, 0, 0)` / `rgb(204, 215, 223)` | 14.35:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `button.switch#2` | `rgb(0, 0, 0)` / `rgb(20, 125, 121)` | 4.24:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:desktop` | `button.switch#3` | `rgb(0, 0, 0)` / `rgb(20, 125, 121)` | 4.24:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:desktop` | `div.notice#2` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `section.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `input#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `select` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `input#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(88, 80, 181)` | 6.5:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `section.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `div.notice` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `section.panel#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `button.switch` | `rgb(0, 0, 0)` / `rgb(204, 215, 223)` | 14.35:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `button.switch#2` | `rgb(0, 0, 0)` / `rgb(20, 125, 121)` | 4.24:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `button.switch#3` | `rgb(0, 0, 0)` / `rgb(20, 125, 121)` | 4.24:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `div.notice#2` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:desktop:focus-1` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:tablet` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:tablet` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `section.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `input#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `select` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `input#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(88, 80, 181)` | 6.5:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `section.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `div.notice` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `section.panel#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `button.switch` | `rgb(0, 0, 0)` / `rgb(204, 215, 223)` | 14.35:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `button.switch#2` | `rgb(0, 0, 0)` / `rgb(20, 125, 121)` | 4.24:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:tablet` | `button.switch#3` | `rgb(0, 0, 0)` / `rgb(20, 125, 121)` | 4.24:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:tablet` | `div.notice#2` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:tablet` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `html` | `rgb(0, 0, 0)` / `rgb(245, 247, 251)` | 19.58:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `header` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `aside` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `input` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `aside.sidebar` | `rgb(203, 216, 226)` / `rgb(24, 41, 54)` | 10.26:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `span.nav-count` | `rgb(175, 192, 204)` / `rgb(49, 70, 83)` | 5.27:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `span.avatar` | `rgb(154, 175, 188)` / `rgb(208, 231, 227)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:mobile` | `header.topbar` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `span.status-pill` | `rgb(58, 120, 109)` / `rgb(243, 250, 247)` | 4.85:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `span.status-dot.live-beacon` | `rgb(58, 120, 109)` / `rgb(54, 169, 139)` | 1.76:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:mobile` | `span.avatar#2` | `rgb(36, 100, 95)` / `rgb(208, 231, 227)` | 5.3:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `section.panel` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `input#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `select` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `input#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `button.btn.btn-primary` | `rgb(255, 255, 255)` / `rgb(88, 80, 181)` | 6.5:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `section.panel#2` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `div.notice` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `button.btn` | `rgb(67, 82, 103)` / `rgb(255, 255, 255)` | 7.95:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `section.panel#3` | `rgb(32, 44, 59)` / `rgb(255, 255, 255)` | 14.14:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `button.switch` | `rgb(0, 0, 0)` / `rgb(204, 215, 223)` | 14.35:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `button.switch#2` | `rgb(0, 0, 0)` / `rgb(20, 125, 121)` | 4.24:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:mobile` | `button.switch#3` | `rgb(0, 0, 0)` / `rgb(20, 125, 121)` | 4.24:1 | 4.5:1 (below sampled threshold) |
| `/settings/` / `settings:mobile` | `div.notice#2` | `rgb(72, 107, 117)` / `rgb(241, 250, 251)` | 5.45:1 | 4.5:1 (meets sampled threshold) |
| `/settings/` / `settings:mobile` | `div.toast` | `rgb(255, 255, 255)` / `rgb(37, 62, 72)` | 11.28:1 | 4.5:1 (meets sampled threshold) |
