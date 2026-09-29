# The directions page

What the stage B page contains. It is one self-contained, interactive HTML
page, built after loading the `artifact-design` skill and following its page
contract (a short title, colour tokens on `:root` with dark mode, scripts
only from the allowed CDNs, works at phone width with no horizontal scroll).

## Structure

1. **Header**: product name, what is being redesigned, the date, and the
   three problems from the audit the directions must solve.
2. **Shared UX strip**: the information architecture (tabs or sidebar), the
   key flows, and a note that every direction below uses exactly this
   structure.
3. **Direction switcher**: a segmented control or list of the 5 to 6
   directions. Switching changes the whole page's mockups in place so the
   owner compares the same screen across directions. A keyboard shortcut
   (1 to 6) helps.
4. **Per direction**:
   - Name and one-line thesis ("Pit Wall: the calm of a race engineer's
     screen").
   - Who it is for and what it says about the product.
   - Palette (light and dark swatches with contrast ratios), type pairing
     with a sample ramp, shape language (radius, borders, depth), density.
   - Motion personality mapped onto the `delight-spec` tokens (for example
     "crisp: release damping 0.75" versus "playful: release damping 0.55").
   - The key screens as **live mockups** in a phone frame and a desktop
     frame: tappable, with press states, one real transition, light and dark
     toggle.
   - **What it trades away** (every direction gives something up: density,
     warmth, speed of reading, brand recognition).
5. **Comparison table**: direction by criteria (legibility at a glance,
   brand fit, conversion screen clarity, build cost, risk).
6. **How to answer**: "Reply with the name of one direction, and anything
   you would change about it."

## Making the directions genuinely different

Vary at least three of these axes between any two directions:

- Colour temperature and saturation (monochrome, one vivid accent, full
  palette).
- Type (grotesque, humanist, serif display, monospace data).
- Surface (flat, layered glass, card stacks, edge to edge).
- Density (glanceable big numbers, analyst tables).
- Imagery (none, photography, illustration, data visualisation as hero).
- Motion personality (crisp, soft, playful, cinematic), always within the
  token ranges.

Two directions that differ only in accent colour count as one.

## RaceModel example set (illustration only)

1. **Pit Wall**: dark, monospace data, one signal colour, dense tables.
2. **Paddock Club**: light, warm serif display, generous white space.
3. **Lights Out**: black and five reds, bold condensed type, dramatic
   motion on reveals.
4. **Telemetry Glass**: layered translucent surfaces, charts as the hero.
5. **Grid Card**: collectible driver cards, playful springs, toy feel
   strongest.
6. **Broadcast**: TV-graphics language, strong bars and tickers.

## Mockup rules

- Real content (real drivers, real race names, the product's own numbers),
  not lorem ipsum.
- The conversion screen (paywall) appears in every direction, honest by the
  `paywall-and-pricing` rules.
- Every mockup is reachable by keyboard and has alt text or labels; the
  page itself passes AA contrast in both themes.
