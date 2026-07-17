# Design.md — CrowdPulse

## 1. Design Intent
A stadium "operations control room" feel — calm, high-contrast, data-first. Not playful/fan-facing. The organizer using this is scanning for risk under time pressure, so clarity beats decoration.

## 2. Color Palette
- **Background (dark mode base):** `#0B1120` (near-black navy) — control-room feel, reduces eye strain for extended monitoring
- **Surface / cards:** `#141B2D`
- **Primary accent (brand/action):** `#22C55E` (green) — also doubles as "Normal" status
- **Status — Watch:** `#F59E0B` (amber)
- **Status — Critical:** `#EF4444` (red)
- **Text primary:** `#F1F5F9`
- **Text secondary/muted:** `#94A3B8`
- **Borders/dividers:** `#1E293B`
- **AI Ops Brief panel accent:** `#38BDF8` (sky blue) — visually distinguishes AI-generated content from raw data, so evaluators can immediately see what's GenAI-driven vs deterministic

> Rule: status must never be conveyed by color alone (accessibility requirement) — always pair with an icon and text label ("● Critical", not just a red dot).

## 3. Typography
- **Font:** Inter (Google Fonts / Tailwind default stack is fine — no need to self-host)
- **Headings:** 600-700 weight
- **Body:** 400 weight, minimum 16px base size
- **Data/numbers (occupancy %, counts):** tabular-nums, slightly bolder, for scannability
- **Line height:** 1.5 for body text, 1.3 for headings

## 4. Layout
- **Top bar:** app name "CrowdPulse", live/last-updated timestamp, CSV upload button
- **Main grid (two-column on desktop, stacked on mobile):**
  - Left/main: zone status cards in a responsive grid, "AI Ops Brief" panel above or beside them
  - Right/sidebar: Ops Chat widget, persistent
- **Below fold:** Incident log table + export button
- Single page, no routing/navigation needed beyond this — keeps it simple and fast

## 5. Components
- **Zone card:** zone name, occupancy % (large number), status badge (icon + color + text), small capacity/count detail
- **AI Ops Brief panel:** visually framed distinctly (sky-blue left border), shows risk_level, reasoning (1-2 sentences), recommended_action, urgency — clearly labeled "AI-Generated" so it's unambiguous to evaluators
- **Chat widget:** simple message bubbles, user right-aligned, AI left-aligned, input box pinned to bottom of its panel
- **Buttons:** solid green for primary actions (Generate Brief, Upload), outline style for secondary (Export, Mark Actioned)

## 6. Accessibility Requirements (binding, not optional)
- Minimum contrast ratio 4.5:1 for body text, 3:1 for large text/icons (verify actual hex values against WCAG AA, adjust if needed once implemented)
- All interactive elements reachable and operable via keyboard (Tab order logical: upload → generate brief → chat input → export)
- Focus states visible (don't strip default outline without replacing it)
- All icons paired with text or `aria-label`
- Form inputs (CSV upload, chat box) have associated `<label>` elements, not placeholder-only labeling
- Sufficient tap target size (min 44x44px) for buttons

## 7. What to Avoid
- No stock "AI robot" imagery/icons — use simple line icons (status, upload, send) instead, keeps it professional and on-theme
- No unnecessary animation — a subtle loading state while the LLM call is in flight is fine (e.g., a text pulse "Analyzing..."), nothing decorative beyond that
- No light-mode toggle needed for MVP — pick dark control-room theme and execute it well rather than building two half-finished themes
