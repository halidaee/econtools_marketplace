# AER Figure Specifications

## A. Sizing and Resolution

| Category | Width | Height | Aspect ratio |
|---|---|---|---|
| Single-column | 3.5" (87.5mm) | 2.5"–3.5" | ~1.2:1 to 1.4:1 |
| Full-width | 7" (175mm) | 3.5"–5" | ~1.4:1 to 2:1 |
| Full-page | 7" (175mm) | up to 9" | varies |
| Theory intuition | 2.5" | 2.5" | 1:1 |

- **Vector output** (PDF) is always preferred for line art and plots
- **Raster output** (PNG) at minimum 300 DPI at final print size as backup
- For maps with many polygons or dense scatter plots, 600 DPI may be needed
- File size limit: keep under 10 MB per figure

## B. Typography

| Element | Size range | Weight | Notes |
|---|---|---|---|
| Axis titles | 8–10pt | Normal | Sentence case with units |
| Tick labels | 7–9pt | Normal | Abbreviated if needed |
| Panel labels | 9–11pt | Bold | "(a)", "(b)" or "Panel A:" |
| Legend title | 8–10pt | Normal | Omit if self-evident |
| Legend keys | 7–9pt | Normal | Match data labels |
| Annotations | 7–9pt | Normal/Italic | Sparingly |

- **Font family**: Serif — Times New Roman, Computer Modern, or Palatino
- Use `latex2exp::TeX()` for math notation: Greek letters (`$\alpha$`), subscripts (`$\beta_{1}$`), equations
- All text must be readable at final print size without magnification
- Font family must be consistent within and across all figures in the paper

## C. Color and Grayscale

**Primary palette** (grayscale, ordered light to dark):

| Hex | Approx gray | Use |
|---|---|---|
| `#D9D9D9` | 85% | Lightest fill, background regions |
| `#C4C4C4` | 77% | Secondary fill |
| `#999999` | 60% | Mid-tone, secondary lines |
| `#707070` | 44% | Primary data, darker fills |
| `#363636` | 21% | Darkest, emphasis, text-adjacent |

- **Default to grayscale**; color only when it encodes meaningful information (e.g., treatment groups that map to a conceptual color)
- If color is used, it must remain distinguishable when printed in B&W
- For multiple overlapping lines: combine grayscale with linetype variation
- Linetypes: `solid`, `dashed`, `dotted`, `longdash`, `twodash`, `dotdash`
- Fills: use alpha transparency (0.3–0.6) when overlapping densities/bars

## D. Line Weights and Points

| Element | Size | Notes |
|---|---|---|
| Single data line | 0.5–0.75 | `linewidth` in ggplot2 >= 3.4, `size` before |
| Multiple overlapping lines | 0.4–0.6 | Thinner to reduce clutter |
| Axis lines | 0.5 | Clean, consistent |
| Grid lines | 0.25 | If present; prefer removing |
| Error bars / CIs | 0.4–0.5 | Thinner than data line |
| CI caps (errorbar width) | 0.15–0.25 | Proportional to data range |
| Scatter points | 1.5–2.5 | Smaller with many points |
| Coefficient plot points | 2–3 | Must be clearly visible |
| Reference lines (zero, mean) | 0.3–0.4 | Dashed or dotted, subtle |

## E. Axis and Grid

- **Minimal ticks**: only where data exists; avoid crowding
- **Labels**: sentence case with units in parentheses — "Income (USD thousands)"
- **Thousands separator**: use `scales::label_comma()` for large numbers
- **Percent**: use `scales::label_percent()` or `scales::label_percent(scale = 1)` depending on data
- **Dollar**: use `scales::label_dollar()` for currency
- **Grid**: remove major and minor gridlines by default (theme_tufte handles this); add light horizontal gridlines only if the plot requires precise value reading
- **Axis expansion**: use `expansion(mult = c(0, 0.05))` for bar charts (bars touch x-axis); default expansion for scatter/line
- **Breaks**: use `scales::breaks_pretty()` or specify manually for clean intervals

## F. Panel Labels

Two acceptable styles (pick one and be consistent across the paper):

**Style 1 — Lowercase parenthetical:**
```
(a) First panel    (b) Second panel    (c) Third panel
```

**Style 2 — "Panel" prefix:**
```
Panel A: First panel    Panel B: Second panel    Panel C: Third panel
```

- Placement: **top-left** of each panel, inside the plot area or as facet strip
- With `facet_wrap`/`facet_grid`: use `labeller` argument to customize strip text
- With `patchwork`: use `plot_annotation(tag_levels = "a")` with `tag_prefix = "("`  and `tag_suffix = ")"`
- Font: bold, 9–11pt, same serif family as rest of figure

## G. Legend

- **Position**: inside the plot area (top-right, bottom-right, or top-left) if space allows; otherwise below the plot (`legend.position = "bottom"`)
- **Background**: transparent (`legend.background = element_blank()`)
- **Border**: none (`legend.box.background = element_blank()`)
- **Key size**: large enough to distinguish patterns — `legend.key.size = unit(0.8, "lines")` minimum
- **Title**: omit if legend keys are self-explanatory; otherwise concise
- **Order**: match visual order in the plot (top-to-bottom or left-to-right)
- For multi-panel figures: shared legend below the combined plot, not repeated per panel

## H. Title and Caption

- **NO** `ggtitle()` or `labs(title = ...)` — the figure title is set in the document:
  - LaTeX: `\caption{Descriptive title here}`
  - Quarto: `fig-cap: "Descriptive title here"`
- **NO** `labs(subtitle = ...)` — use the caption or figure notes instead
- **YES** `labs(x = "Label", y = "Label")` for axis labels
- **YES** `labs(caption = "Notes: ...")` ONLY for source attribution or brief notes that must travel with the figure file (rare)

## I. ggsave() Parameters

| Size category | PDF call | PNG call |
|---|---|---|
| Single-column | `ggsave("fig.pdf", width = 3.5, height = 2.5, device = cairo_pdf)` | `ggsave("fig.png", width = 3.5, height = 2.5, dpi = 300)` |
| Full-width | `ggsave("fig.pdf", width = 7, height = 4, device = cairo_pdf)` | `ggsave("fig.png", width = 7, height = 4, dpi = 300)` |
| Full-page | `ggsave("fig.pdf", width = 7, height = 8.5, device = cairo_pdf)` | `ggsave("fig.png", width = 7, height = 8.5, dpi = 300)` |
| Theory intuition | `ggsave("fig.pdf", width = 2.5, height = 2.5, device = cairo_pdf)` | `ggsave("fig.png", width = 2.5, height = 2.5, dpi = 300)` |

- Use `device = cairo_pdf` for proper font embedding in PDFs
- Always specify `width` and `height` in inches (default unit)
- For figures with many overlapping points, bump PNG to `dpi = 600`

## J. Package Dependencies

```r
library(ggplot2)    # Core plotting
library(ggthemes)   # theme_tufte() base
library(scales)     # Axis formatting: label_comma(), label_percent(), label_dollar()
library(latex2exp)  # Math notation in labels: TeX()
```

Optional:
```r
library(patchwork)  # Multi-panel composition with +, /, plot_layout()
library(ggspatial)  # Scale bars and north arrows for maps
library(sf)         # Spatial data for geom_sf()
```
