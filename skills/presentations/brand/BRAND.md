---
name: vinicius-valiati-brand
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
  mono:                     # code, SQL and metric names on technical slides
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
| Titles and body on light | `text` | Highest contrast for reading |
| Accent on light (links, key word, icons) | `petrol` | The identity color, readable on light surfaces |
| Accent on dark | `petrol-light` | `petrol` fails contrast on `ink` |
| The story number or bar | `amber` | Rare, so it reads as "this one"; a fill on light, never text |
| Secondary text | `muted` / `on-ink-muted` | Sources, labels and captions |

Measured contrast (WCAG 2.x):

| Foreground / background | Ratio | Allowed for text |
|---|---|---|
| `text` / `paper` | 14.71 | yes |
| `muted` / `paper` | 5.03 | yes |
| `petrol` / `paper` | 4.74 | yes |
| `petrol` / `white` | 5.09 | yes (either way) |
| `text` / `white` | 15.81 | yes |
| `muted` / `white` | 5.40 | yes |
| `amber` / `paper` | 2.04 | **no**: fills only |
| `white` / `ink` | 16.08 | yes |
| `amber` / `ink` | 7.34 | yes (either way: text on an amber fill) |
| `petrol` / `ink` | 3.16 | **no**: use `petrol-light` |
| `petrol-light` / `ink` | 6.55 | yes |
| `on-ink-muted` / `ink` | 7.91 | yes |
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
Generated decks do not embed fonts (python-pptx cannot). Install the three
families, or embed them before sending (PowerPoint for Windows: File ›
Options › Save › Embed fonts in the file; all three are OFL, so embedding is
allowed). The fallbacks above cover the worst case. Always send a PDF too.

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
- Language follows the audience: Portuguese for Brazilian clients and the
  team, English for portfolio and international audiences.

## Occasion profiles

Same identity, different behavior. The `presentations` skill asks the
occasion first and applies one of these profiles.

| Occasion | Perception | Density | Accent usage | Cover | Motion |
|---|---|---|---|---|---|
| Status report | Consultative, sober | High (`body-dense` allowed, tables welcome) | `amber` only on the metric that changed most | Dark, minimal | None |
| Kickoff | Consultative, structured | Medium | `petrol` for structure (phases, owners); `amber` on the key date or goal, when there is one | Dark | None |
| Technical / portfolio (EN) | Technical, precise | Medium; code and diagrams allowed | `petrol` for system components; `amber` on the result | Dark | Progressive build on architecture slides (HTML version) |
| Pitch | Modern, impactful | Low: one idea per slide, up to 2 big numbers | `amber` on the big numbers; more dark slides allowed | Dark | None |
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

## Don't

- Gradients, shadows, stock photos of people, clip art or emoji.
- More than one `amber` element per slide, except the pitch profile with two
  big numbers.
- Logos of clients or employers on templates; client logos enter only in a
  client deck, supplied by the client.
- Colors, fonts or sizes outside the tokens above; if one is missing, ask.
