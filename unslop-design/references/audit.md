# Audit Rules: Copy, Decorative Chrome, Charts & Surface (`U1`–`U25`, `unslop`)

Apply these rules across every in-scope UI file (in Audit Mode, and as final cleanup in Build Mode). Delete first; rewrite only using verified facts, feature names, and bound data already in the source. Apply in the screen's own language.

## 1. Interface Copy (`U1`–`U8`, `U22`, `unslop`)

- **U1. Eyebrow labels**: Remove small uppercase or tracked kickers (`"FEATURES"`, `"PASSPORT"`) and category pills/dots perched above headings (`"● Product"`). Open directly with the heading.
- **U2. Decorative numbering**: Remove `01 //`, `02`, `[ 01 / 04 ]`, `§`, or Roman numeral prefixes on unordered cards or features. Keep numbers only when sequence is functional (install steps, checkout, ordered commands).
- **U3. Subtitle reflex**: Remove subtitles under headings, pre-H1 lines, item blurbs, and CTA/form reassurance footnotes (`"No credit card required"`, `"Cancel anytime"`, `"Instant setup"`) that restate the heading or add generic filler. Keep only concrete facts shown nowhere else on screen.
- **U4. Botsplaining**: Remove captions narrating visible UI controls (`"Click below to get started"`, `"This panel shows..."`). Keep concise empty states, errors, and destructive confirmations as 1–2 plain sentences stating what happened and the next step from code, without `"Oops!"` or exclamation marks.
- **U5. Leaked design notes**: Remove parenthetical or fourth-wall implementation notes (`"(updates in real time)"`, `"(powered by AI)"`).
- **U6. Status strings**: Replace `·` or `|` chains (`"12 items · Updated 2m ago · Synced · v2.1"`) with the one actionable fact; drop claims of live state unless data-bound.
- **U7. Redundant field cues**: Keep one cue per field. Forms keep a visible `<label>` tied to its control; remove placeholders that merely repeat the label (keep format examples like `"name@company.com"`) and obvious helper text (`"We will use your email..."`), while keeping real constraints (`"At least 12 characters."`). Search fields with a magnifier icon take either a label or placeholder.
- **U8. Staccato & empty slogans**: Rewrite `"Finance. Simplified. Finally."` or `"Built different."` as one plain statement of what the product does using existing page words, or delete.
- **Length & benefit lead**: Keep UI section/card headings and short captions `<= 5` words (hero `<h1>`, errors, empty states, constraints exempt) and lead headings with user benefits over raw internal specs.
- **`unslop` prose filter** (on retained/rewritten full sentences; short UI fragments exempt): cut superficial `-ing` clauses (`"showing strong momentum"`), vague attributions, AI buzzwords (*crucial, delve, enhance, seamless, showcase, pivotal, vibrant, landscape, testament, elevate, unlock, empower, reimagined*), fancy `"is"` verbs (*serves as, stands as, boasts*), `"Not just X, but Y"`, forced rules of three, synonym cycling, false ranges (*"From startups to enterprises"*), em dashes (`—`) and spaced hyphens (` - `) outside verbatim user quotes or empty table cells, mid-sentence clause colons, repeated bold lead-ins, title case (use sentence case), `"In order to"`, generic conclusions, abstract metaphors (*substrate, harness, flywheel, north star*), passive voice, unquantified adverbs (*seamlessly, effortlessly, quickly*), and *utilize/leverage* (use *use*).

## 2. Decorative Chrome, Links & Real-State Test (`U9`–`U11`, `U21`, `U22`, `U24`)

**Real-state distinction**: Keep a status indicator or badge only when rendered dynamically from runtime state, props, or store/query values and paired with semantic markup (`role="status"` or accessible label). Remove static hardcoded `"LIVE"`, `"NEW"`, `"AI"`, `"BETA"`, `"POPULAR"`, pulsing dots (`animate-pulse`), and decorative non-interactive chips/tags of any shape (rounded or square).

- **U11. Decorative emojis & icons**: Remove emojis and decorative icons from headings, KPI titles, tinted icon squares, and text buttons (including decorative icons inside primary CTAs). Keep icons that are the control itself (`aria-label`ed icon buttons), carry non-redundant meaning, or sit uniformly across a toolbar/action menu.
- **U21. Link & button arrows**: Remove `→` (`←` RTL) or trailing `<ArrowRight />` after link/button text. Keep `↗` for external links, `aria-label`ed pagination arrows, and breadcrumb separators.
- **U22. Generic labels**: Replace `"Click here"`, `"Learn more"`, `"Read more"`, `"Submit"` with the specific destination or action derived from `href`/form purpose; if unclear in source, report as an owner task.
- **U24. Edge accent stripes**: Replace decorative thick colored edge bars (`border-l-4`, `border-left: 4px solid ...`, `::before` strips, inset edge shadows) with a `1px` neutral border or tint; preserve stripes only on semantic status alerts (`role="alert"`, error/warning callouts).


### Schematic Keep-vs-Remove Boundary Pairs

1. **Runtime State vs. Ornamental Badge/Dot** (decide from data binding, not CSS class):
```jsx
// Decorative (remove): fixed strings or unlinked animations
<span class="tag">NEW</span>
<span class="dot animate-pulse"></span><span>Live</span>

// State-bound (keep): driven by runtime state/store/props with semantic role
{stream.connected && <span role="status" aria-label="Connected" class="indicator" />}
```
*Decision*: Keep status UI wired to live runtime conditions; remove fixed ornamental tags and idle pulses.

2. **Accessible Form Name vs. Redundant Cue** (keep control association and real rules):
```html
<!-- Redundant (cut placeholder and obvious helper): -->
<label for="org-slug">Workspace slug</label>
<input id="org-slug" placeholder="Enter your workspace slug" />
<small>We use this slug to identify your workspace.</small>

<!-- Accessible minimal (keep visible label and real constraint): -->
<label for="org-slug">Workspace slug</label>
<input id="org-slug" />
<small>Lowercase letters and hyphens only.</small>
```
*Decision*: Preserve visible `<label>` (or wrapping label / component label prop) and constraints users cannot guess; cut placeholders and helper text that merely restate the label.

## 3. Charts & KPIs (`U12`–`U16`, `U23`)

- **U12**: Strip chart-type words (`"Bar chart of monthly revenue"` -> `"Monthly revenue"`), or delete if a sibling heading names it.
- **U13**: Delete chart reading instructions (`"Each bar represents..."`, `"Hover over..."`).
- **U14**: Keep one primary encoding per value; remove redundant labels printed over every bar when axes/gridlines exist (keep only focal endpoints/peaks), and cap KPI tiles at label, figure, and at most one concise delta/context line.
- **U15**: Remove outer plot frame boxes, thick axis borders, dark/dense gridlines, 3D effects, shadows, and plot background fills; use at most faint `1px` neutral hairlines (`<= 10%` opacity) and one clean baseline while keeping chart type, data, and series palette intact.
- **U16**: Replace legend boxes with direct end-of-series labels when plotting `<= 4` clearly separated series; keep a legend when `> 4` series, endpoints collide (e.g., narrow mobile widths), or interactive series toggles require one.
- **U23 (Report-only in Audit Mode)**: Flag equal-loudness stat-card walls as an owner task naming which metric deserves primary visual hierarchy.

## 4. Surface Tokens, Motion & Edge Alignment (`U17`–`U20`, `U25`)

Apply in Build Mode, or on the target surface in Audit Mode when visual cleanup / `--surface` is requested (never breaking layout or sibling routes):
- **U17**: Replace hue-to-hue SaaS button/card gradients, gradient text (`bg-clip-text`), colored glow shadows, and decorative blobs with solid surfaces, neutral contrast, and `1px` hairline borders.
- **U18**: Snap off-scale spacing (`mt-[13px]`, `gap: 7px`) to the `4px` modular step scale (`4, 8, 12, 16, 20, 24, 32, 40, 48, 64`; `2, 6, 10, 14` inside controls).
- **U19**: Cap card/KPI/price/UI weights at `500`–`600` (max `700`; architectural hero `<h1>` in Build Mode exempt) instead of `800`/`900`.
- **U20**: Replace `transition: all` / `transition-all` with explicit properties (`colors`, `transform`, `opacity`) at `140–240ms` ease-out; remove `0 -> N` mount counters and generic scroll fade-ups (`opacity: 0`) plus dead animation listeners; include `@media (prefers-reduced-motion: reduce)`.
- **U25**: Align minority off-edge items (sidebar/nav text lines, icon columns, trailing badges/counts, toolbar vertical centerlines) via shared container padding, gap, or CSS variables—never per-item margin hacks (`ml-[3px]`). Ensure buttons and inputs in one container share consistent shape (rounded-rect or pill).

## 5. Locale Fidelity (Localized Pages & Catalogs)

When editing localized pages, catalogs, or templates:
- **Trace ownership first**: Locate the active locale files/configs and runtime interpolation/rendering path before changing strings.
- **Edit only authorized locales**: In a single-locale request, leave all other locale files byte-identical (and keep shared markup safe for sibling routes).
- **Preserve bindings, schema & native voice**: Keep placeholders (`{count}`), plurals, JSON key structure (set cleared optional keys to `""` rather than dropping keys unexpectedly), route `href`s, `lang` attributes, accessible names, intentional locale-specific asymmetries (such as links omitted in one language), clean native punctuation (`«...»`), and idiomatic wording that is already free of slop.
- **Check narrow reflow**: On localized UI edits, verify longer translations wrap cleanly at `390px` width without horizontal overflow or clipped action labels.
