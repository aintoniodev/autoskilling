# Build & Redesign Architecture

Apply these architectural, typographic, color, control, and imagery standards in **Build / Redesign Mode** (respecting any explicit user exclusions).

## 1. Opening Composition & Layout Rhythm

- **Match opening format to purpose**: Open news sites, blogs, dashboards, analytics consoles, documentation, directories, utility tools, and minimalist resumes directly into live content, workspace controls, or the document sheet. Keep `100vh` marketing banners off utility/data apps so primary controls and KPIs sit immediately visible in the initial viewport.
- **Break the 50/50 SaaS split hero template**: On hero-led marketing, storefront, event, or portfolio pages, give the display `<h1>` and lead visual full spatial command rather than trapping `<h1>` in a half-width left column opposite a right box with a long paragraph, dual buttons, rule, and 3–4 bottom KPI strip. Choose a composition suited to the brief:
  - Centered monumental display `<h1>` rising above a wide interactive workbench or stage;
  - Full-bleed edge-to-edge photography or living canvas bleeding to `y = 0` with clear figure-ground space for type;
  - Layered `z-index` typography behind a central cutout subject;
  - Wall-to-wall poster typography over deliberate chromatic color-blocking.
- **Tight hero copy**: Pair `<h1>` with at most 1–2 concise lines (`<= 25` words total) and one primary action (or immediate interactive control); omit bottom hero stat/spec strips.
- **Single-line header at `y = 0`**: Keep desktop navigation on one horizontal line with a visibly stronger brand wordmark than nav links. On hero pages, bleed the hero cleanly to `y = 0` behind a borderless header bar and add clean surface separation once scrolled.
- **Sustain craft below the fold**: Vary pacing down to the footer (full-bleed bands, asymmetric editorial splits, interactive stages) using whitespace, `1px` hairline dividers, and subtle surface tint rather than generic 3-column card rows or nested card-in-card boxes.
- **Single focal hierarchy in dashboards**: When redesigning a dashboard with equal-loudness KPI tiles, elevate the primary metric or visual focus so secondary figures support rather than compete.

## 2. Color & Art-Directed Imagery

- **Subject-derived palette**: Draw colors from the domain's real materials and audience rather than warm beige/cream + terracotta on craft briefs or dark slate + neon purple glow on tech. Define clean tokens (`--bg`, `--surface`, `--border`, `--text`, `--text-muted` meeting WCAG AA `>= 4.5:1`, and one deliberate accent); reserve status hues strictly for semantic runtime state.
- **Purposeful visuals**: Match asset aspect ratios to containers, generate/source one unique visual per item, and preserve clean negative space around overlaid type instead of muddy full-screen dark scrims. Omit decorative photos in dense work tools.

## 3. Typography & Interactive Controls

- **At most 2 font families**: Choose 1 versatile sans family across weights or 2 intentional typefaces (beyond reflexive serif-display + generic-sans defaults). Apply `font-variant-numeric: tabular-nums` on the body font for prices, metrics, timers, and counts; load a monospace family only for code, terminal, or API documentation tools.
- **Strict body font-size discipline**: Lock **at most 3 distinct font sizes** across everything below the hero (`4` max only in dense dashboards/data tables; hero `<h1>` and navbar brand wordmark exempt). Differentiate subheadings, buttons, and labels via weight, color, and case rather than extra `20px–24px` steps.
- **Consistent readable scale**: Keep all body paragraphs and bullet/numbered lists at one shared body size (`<= 65ch` measure), render zero text `< 13px` (`0.8125rem`) above the fold, tighten display tracking (`-0.02em` to `-0.05em`), keep headlines whole without `<br><em>` italic splits, and use sentence case across UI labels and table headers.
- **One primary CTA & non-button pickers**: Place at most one primary CTA button per content section. Build view, mode, date-range, filter, and size selectors using connected segmented controls (`role="tablist"` / `role="radiogroup"` / `<input type="radio">`), tabs, switches, `<select>`, or direct canvas manipulation rather than clusters of separate bordered buttons.
- **Purposeful motion**: Name explicit transitioned properties (`transform`, `opacity`, `colors` — never `transition: all`) at `140–240ms` smooth ease-out (`cubic-bezier(0.22, 1, 0.36, 1)`), keep headlines and numbers visible at rest, avoid generic per-section scroll fade-ups, and honor `@media (prefers-reduced-motion: reduce)`.

## 4. Bounded Rendered Verification (Runnable Pages & Apps)

When editing a runnable HTML/web app and local browser tooling (Playwright or preview browser) is available:
- **Serve & wait**: Serve over local HTTP (max 15s ready check, 45s total pass); wait for route content and settled fonts.
- **Inspect desktop + mobile**: Check `1440×900` (above-fold and scrolled) and `390×844` mobile for zero horizontal overflow, `<= 2` loaded font families, below-hero size steps (`<= 3`, `<= 4` dashboards), uniform `<p>`/`<li>` prose size & `<= 65ch` measure, zero `< 13px` above-fold text, `>= 4.5:1` contrast, direct series labels on `<= 4` series, and live interactive state/filters.
- **Repair & teardown**: Run at most one targeted fix pass if rendering reveals defects, re-check, and stop only servers/browsers you launched. If no browser is available, state `"Render: not verified"`.
