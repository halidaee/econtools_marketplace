---
name: aer-figures
description: Use when the user has an R/ggplot2 figure script and wants it formatted for AER or economics journal submission, mentions publication-ready figures, or asks to make a figure journal-compliant
---

# AER Figure Formatter

## Overview

Rewrites R/ggplot2 figure code for AER compliance: sizing, resolution, fonts, grayscale-compatible palettes, panel labels, and export settings. Preserves all data manipulation and statistical content — only changes formatting and presentation layers.

## Constraints

- **NEVER** change plotted data or statistical content (geom mappings, model estimates, data transformations)
- **CAN** change: theme, colors, fonts, dimensions, labels, legend, panel labels, ggsave parameters
- **MUST** preserve all upstream data code (loading, cleaning, merging, modeling)
- **MUST** ensure all required packages are loaded (`library()` calls at top)
- **MUST** output both PDF (vector) and PNG (300 DPI raster) via `ggsave()`
- **MUST NOT** add `ggtitle()` or `labs(title = ...)` — titles belong in LaTeX/Quarto captions

## Workflow

1. **Read** the user's R script end-to-end
2. **Identify figure type** using the detection table below
3. **Determine size category** based on content complexity and target layout
4. **Apply AER rules** from `references/aer-figure-specs.md` (sizing, fonts, colors, line weights)
5. **Rewrite ggplot code** using the matching template from `references/ggplot-patterns.md`
6. **Add ggsave()** calls with correct dimensions, DPI, and format
7. **Return** the rewritten script with comments marking what changed

## Figure Type Detection

| Signal in code                                                        | Type             | Primary formatting concern                                    |
| --------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------- |
| `geom_point` + `geom_errorbar` / `geom_linerange` / `geom_pointrange` | Coefficient plot | Point/CI visibility, zero-reference line                      |
| `geom_density` / `stat_function` / `geom_histogram` / `geom_freqpoly` | Distribution     | Smooth curves, grayscale-compatible fill distinction          |
| `geom_col` / `geom_bar`                                               | Bar chart        | Bar width, grayscale-compatible contrast, error bars          |
| `geom_line` + time/date variable on x-axis                            | Time series      | Line weight >= 0.5, linetype variation for series             |
| `facet_wrap` / `facet_grid`                                           | Multi-panel      | Panel labels (a)/(b), margins, shared legend                  |
| `geom_sf` / `geom_polygon` + map data                                 | Map              | Grayscale-compatible choropleth, boundary lines, minimal axes |

When multiple signals are present, treat the combination (e.g., faceted coefficient plot) and apply rules for both types.

## Size Categories

| Category         | Width         | Height    | Use case                    |
| ---------------- | ------------- | --------- | --------------------------- |
| Single-column    | 3.5" (87.5mm) | 2.5"–3.5" | Simple single-panel figures |
| Full-width       | 7" (175mm)    | 3.5"–5"   | Multi-panel, wide figures   |
| Full-page        | 7" (175mm)    | up to 9"  | Complex multi-panel layouts |
| Theory intuition | 2.5"          | 2.5"      | Small inline diagrams       |

## Quick Reference

- **Font**: Serif (Times/Computer Modern), minimum 8pt at final print size
- **Palette**: Grayscale — `#D9D9D9`, `#C4C4C4`, `#999999`, `#707070`, `#363636`
- **Color**: Color palette designed should be grayscale-compatible. Color should only be used when it encodes meaningful information.
- **Lines**: >= 0.5 weight for data lines, 0.25 for grid (or remove grid)
- **Title**: None — use LaTeX/Quarto `\caption{}` or `fig-cap:`
- **Output**: PDF (vector) + PNG (300 DPI) via `ggsave()`
- **Base theme**: `ggthemes::theme_tufte()` customized with serif font and AER sizing
- **Math labels**: Use `latex2exp::TeX()` for Greek letters, subscripts, equations
