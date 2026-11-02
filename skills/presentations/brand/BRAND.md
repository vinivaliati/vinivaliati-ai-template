---
name: vinicius-valiati-brand
version: "1.0.0"
description: >
  Personal brand for Vinicius Valiati's presentations and visual material.
  One identity (palette, type, wordmark) used everywhere; each occasion
  changes density, structure, accent usage and motion, never the identity.

colors:
  # Core
  ink: "#12232E"            # dark surfaces: cover, dividers, closing
  petrol: "#0F7B78"         # primary accent on light surfaces
  petrol-light: "#5FB3AE"   # accent on dark surfaces (petrol fails on ink)
  amber: "#E0A526"          # highlight: the one number or bar the story is about
  paper: "#F5F7F8"          # content slide background
  white: "#FFFFFF"          # cards on paper, text on ink
  # Text
  text: "#17242E"           # body and titles on paper
  muted: "#5E6C77"          # secondary text, sources, axis labels on paper
  on-ink-muted: "#A9B8C2"   # secondary text on ink
  # Lines and neutral data
  line: "#D5DDE2"           # dividers, table rules, gridlines
  bar-neutral: "#B9C6CE"    # context bars that are not the story
  # Semantic (charts and status only, never decoration)
  positive: "#1F7A4D"
  negative: "#B42318"
  steel: "#4F6D8A"          # third chart series

chart-series:               # fixed order for the whole deck
  - petrol
  - amber
  - steel
  - bar-neutral

typography:
  heading:
    family: "Manrope"
    fallback: "Segoe UI, Arial, sans-serif"
    weights: [600, 700, 800]
  body:
    family: "Source Sans 3"
    fallback: "Calibri, Arial, sans-serif"
    weights: [400, 600]
  mono:                     # [SUGGESTION] code, SQL and metric names on technical slides
    family: "IBM Plex Mono"
    fallback: "Consolas, monospace"
    weights: [400, 500]
  wordmark:
    text: "Vinicius Valiati"
    family: "Manrope"
    weight: 800
    letter-spacing: "-0.01em"

# Sizes in points for a 13.333 x 7.5 in (16:9) .pptx slide.
# For HTML at 1920 x 1080 px, multiply by 2 (px = pt x 2).
type-scale:
  cover-title: { size: 44, font: heading, weight: 800, line-height: 1.05 }
  divider-title: { size: 36, font: heading, weight: 800, line-height: 1.1 }
  slide-title: { size: 28, font: heading, weight: 700, line-height: 1.15 }
  subtitle: { size: 20, font: body, weight: 400, line-height: 1.3 }
  body: { size: 18, font: body, weight: 400, line-height: 1.35 }
  body-dense: { size: 14, font: body, weight: 400, line-height: 1.3 }
  label: { size: 12, font: body, weight: 600, letter-spacing: "0.08em", case: upper }
  caption: { size: 11, font: body, weight: 400 }
  big-number: { size: 96, font: heading, weight: 800, line-height: 1.0 }
  kpi-number: { size: 40, font: heading, weight: 700 }
  code: { size: 14, font: mono, weight: 400 }

layout:
  canvas: "16:9, 13.333 x 7.5 in (pptx) / 1920 x 1080 px (HTML)"
  margin-x: "0.6 in"
  margin-top: "0.5 in"
  margin-bottom: "0.45 in"
  grid: "12 columns, 0.25 in gutter"
  footer: "slide number + short section name in caption size, muted, bottom margin"
  corner-radius: "4 pt on cards and callouts; 0 on chart bars and table cells"
  shadows: none
---

# Brand

## Identity in one paragraph

Technical precision with a consultant's clarity. Content lives on calm, light
surfaces so data and conclusions do the work; dark petrol surfaces mark the
moments that frame the story (cover, chapter, closing). Amber is rare on
purpose: it points at the single number the audience must remember.

## Color rules

| Use | Token | Why |
|---|---|---|
| Content background | `paper` | Projects and prints well in client rooms; less glare than pure white |
| Cover, dividers, closing | `ink` | Gives the deck a frame and signals "new part" without decoration |
| Titles and body on light | `text` | Contrast 14.7:1 on `paper` |
| Accent on light (links, key word, icons) | `petrol` | Contrast 4.7:1 on `paper`, 5.1:1 on `white` |
| Accent on dark | `petrol-light` | `petrol` is only 3.2:1 on `ink`; the light variant is 6.6:1 |
| The story number or bar | `amber` | 7.3:1 on `ink`; as a fill on light it reads as "this one" |
| Secondary text | `muted` / `on-ink-muted` | 5.0:1 on `paper` / 7.9:1 on `ink` |

Measured contrast (WCAG 2.x):

| Foreground / background | Ratio | Allowed for text |
|---|---|---|
| `text` / `paper` | 14.71 | yes |
| `muted` / `paper` | 5.03 | yes |
| `petrol` / `paper` | 4.74 | yes |
| `petrol` / `white` | 5.09 | yes |
| `white` / `petrol` | 5.09 | yes |
| `amber` / `paper` | 2.04 | **no**: fills only |
| `white` / `ink` | 16.08 | yes |
| `amber` / `ink` | 7.34 | yes |
| `petrol` / `ink` | 3.16 | **no**: use `petrol-light` |
| `petrol-light` / `ink` | 6.55 | yes |
| `ink` / `amber` | 7.34 | yes (text on an amber fill) |
| `positive` / `paper` | 4.95 | yes |
| `negative` / `paper` | 6.12 | yes |
| `steel` / `paper` | 5.03 | yes |

## Typography rules

- Titles in Manrope, everything else in Source Sans 3. Two families per slide,
  three only on technical slides that show code (mono).
- Never go below 11 pt. If content needs smaller type, it needs another slide
  or an appendix.
- Numbers that line up (tables, KPI rows) use tabular figures.
- Headings never use all caps; only `label` does, with letter spacing.

### Fonts in .pptx

Google Fonts render correctly only where they are installed or embedded.
Every template embeds the fonts (PowerPoint for Windows: File › Options › Save ›
Embed fonts in the file; all three families are OFL, so embedding is allowed)
and declares the system fallback above for the worst case. Before sending a
deck to a client, export a PDF as well.

## Wordmark

Typographic only: "Vinicius Valiati" in Manrope ExtraBold, -0.01em tracking.

- On `ink`: `white`. On `paper` or `white`: `text`. Never in accent colors.
- Cover: bottom left, inside the margins, 14 pt.
- Content slides: none; the footer carries slide number and section.
- Closing slide: same as cover, with contact line underneath in `caption`.
- Do not abbreviate, stack on two lines or add a symbol.

## Voice

- **Action titles.** Every content slide title is a full-sentence conclusion,
  at most two lines: "OTIF dropped 4 pp in September because of late
  carriers", not "OTIF".
- **Direct and assertive.** Short sentences, active voice, no marketing
  adjectives ("robust", "cutting-edge", "seamless").
- **Numbers carry units and a comparison:** "91% OTIF, down from 95%".
- **Every chart has a source line** in `caption`, `muted`.
- **No em dashes** anywhere: use a comma, colon, period or parentheses.
- Language follows the audience: Portuguese for Brazilian clients and the
  team, English for portfolio and international audiences.

## Occasion profiles

Same identity, different behavior. The `presentations` skill asks the
occasion first and applies one of these profiles.

| Occasion | Perception | Density | Accent usage | Cover | Motion |
|---|---|---|---|---|---|
| Status report | Consultative, sober | High (`body-dense` allowed, tables welcome) | `amber` only on the metric that changed most | Dark, minimal | None |
| Kickoff | Consultative, structured | Medium | `petrol` for structure (phases, owners); `amber` on the key date or goal | Dark | None |
| Technical / portfolio (EN) | Technical, precise | Medium; code and diagrams allowed | `petrol` for system components; `amber` on the result | Dark | Progressive build on architecture slides only |
| Pitch | Modern, impactful | Low: one idea per slide, up to 2 big numbers | `amber` on the big numbers; more dark slides allowed | Dark, large title | Progressive build only |
| 1:1 and feedback | Human, close | Low; questions over statements | Almost none; `petrol` for section labels | Light (no dark cover) | None |

## Charts

- Prefer bars and lines. Use a donut only for parts of a whole with at most
  5 slices; never a pie with a 3D effect.
- Bars start at zero; no truncated axes.
- One story per chart: the bar or point the title talks about is `amber`; the
  rest are `bar-neutral`. Multiple series follow `chart-series` order and keep
  the same color across the whole deck.
- Label values directly on bars or line ends; avoid legends when there are
  2 series or fewer.
- Gridlines in `line`, at most 4, or none when values are labeled.
- `positive` and `negative` only for deltas and status, always paired with a
  sign or arrow (color must never be the only signal).
- Source line under every chart.

## Do and don't

- Do: one message per slide; if it needs a second message, it needs a
  second slide.
- Do: conclusion first (executive summary or Situation · Complication ·
  Resolution) for any audience that may leave early.
- Do: end client decks with a concrete ask, owner and date.
- Don't: `amber` as text on light surfaces (2.0:1).
- Don't: `petrol` as text on `ink` (3.2:1); use `petrol-light`.
- Don't: gradients, shadows, stock photos of people, clip art or emoji.
- Don't: more than one `amber` element per slide, except the pitch profile
  with two big numbers.
- Don't: logos of clients or employers on templates; client logos enter
  only in a client deck, supplied by the client.

## Instructions for AI agents

1. Read this file fully before generating any slide, template or visual piece.
2. Use only the tokens above; no loose hex values, fonts or sizes. If a need
   is not covered, ask Vinicius instead of inventing a token.
3. Ask the occasion first and apply its profile.
4. Check every text color against the contrast table; never use a pair
   marked "no".
5. Titles are action titles; verify each one states a conclusion.
6. Scan the final text for em dashes and remove them.
