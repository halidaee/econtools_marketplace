# ggplot2 Code Pattern Templates

## A. Base AER Theme

The foundation for all AER-compliant figures. Builds on `theme_tufte()` with serif fonts, clean axes, and AER sizing.

### Grayscale palette constant

```r
aer_gray <- c(
  light  = "#D9D9D9",
  med1   = "#C4C4C4",
  mid    = "#999999",
  med2   = "#707070",
  dark   = "#363636"
)
```

### Theme function

```r
theme_aer <- function(base_size = 10, base_family = "Times") {
  ggthemes::theme_tufte(base_size = base_size, base_family = base_family) %+replace%
    theme(
      # Text
      text = element_text(family = base_family, size = base_size),
      axis.title = element_text(size = rel(0.9), margin = margin(t = 4, r = 4)),
      axis.text = element_text(size = rel(0.8), color = "black"),
      axis.ticks = element_line(linewidth = 0.3, color = "black"),
      axis.line = element_line(linewidth = 0.5, color = "black"),

      # Grid — remove all
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      panel.background = element_blank(),

      # Facet strips
      strip.text = element_text(size = rel(0.9), face = "bold",
                                margin = margin(b = 4)),
      strip.background = element_blank(),

      # Legend
      legend.background = element_blank(),
      legend.key = element_blank(),
      legend.key.size = unit(0.8, "lines"),
      legend.text = element_text(size = rel(0.8)),
      legend.title = element_text(size = rel(0.85)),

      # Margins
      plot.margin = margin(6, 6, 6, 6)
    )
}
```

---

## B. Coefficient Plot

```r
library(ggplot2)
library(ggthemes)
library(latex2exp)

# --- Data prep (user's code preserved as-is) ---
# df_coef should have: term, estimate, conf.low, conf.high

# --- AER-formatted coefficient plot ---
p <- ggplot(df_coef, aes(x = estimate, y = reorder(term, estimate))) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.3,
             color = aer_gray["mid"]) +
  geom_pointrange(
    aes(xmin = conf.low, xmax = conf.high),
    size = 0.6, linewidth = 0.45, color = aer_gray["dark"],
    fatten = 3
  ) +
  labs(
    x = "Estimate",
    y = NULL
  ) +
  theme_aer(base_size = 10) +
  theme(
    axis.text.y = element_text(hjust = 1, size = rel(0.85))
  )

# --- Export ---
ggsave("fig-coefficients.pdf", p, width = 3.5, height = 3, device = cairo_pdf)
ggsave("fig-coefficients.png", p, width = 3.5, height = 3, dpi = 300)
```

**Horizontal variant** (many variables): Use `coord_flip()` or map terms to y-axis as shown above.

**Multiple models**: Use `position_dodge(width = 0.4)` with a `model` aesthetic mapped to shape or color (grayscale).

---

## C. Distribution / Density Plot

```r
library(ggplot2)
library(ggthemes)
library(scales)

# --- AER-formatted density plot ---
p <- ggplot(df, aes(x = outcome)) +
  geom_density(
    aes(fill = group, linetype = group),
    alpha = 0.4, linewidth = 0.5, color = aer_gray["dark"]
  ) +
  scale_fill_manual(values = c(
    "Treatment" = aer_gray["mid"],
    "Control"   = aer_gray["light"]
  )) +
  scale_linetype_manual(values = c(
    "Treatment" = "solid",
    "Control"   = "dashed"
  )) +
  labs(
    x = "Outcome variable",
    y = "Density",
    fill = NULL,
    linetype = NULL
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
  theme_aer(base_size = 10) +
  theme(
    legend.position = c(0.85, 0.85)
  )

ggsave("fig-density.pdf", p, width = 3.5, height = 2.8, device = cairo_pdf)
ggsave("fig-density.png", p, width = 3.5, height = 2.8, dpi = 300)
```

**Histogram variant**: Replace `geom_density()` with `geom_histogram(aes(y = after_stat(density)), bins = 30, fill = aer_gray["mid"], color = "white", linewidth = 0.2)`.

**Theoretical overlay**: Add `stat_function(fun = dnorm, args = list(mean = m, sd = s), linetype = "dashed", linewidth = 0.5)`.

---

## D. Bar Chart

```r
library(ggplot2)
library(ggthemes)
library(scales)

# --- AER-formatted bar chart ---
p <- ggplot(df, aes(x = category, y = value)) +
  geom_col(
    fill = aer_gray["mid"], color = aer_gray["dark"],
    linewidth = 0.2, width = 0.7
  ) +
  geom_errorbar(
    aes(ymin = value - se, ymax = value + se),
    width = 0.2, linewidth = 0.4
  ) +
  labs(
    x = NULL,
    y = "Mean outcome"
  ) +
  scale_y_continuous(
    labels = label_comma(),
    expand = expansion(mult = c(0, 0.05))
  ) +
  theme_aer(base_size = 10)

ggsave("fig-bar.pdf", p, width = 3.5, height = 2.8, device = cairo_pdf)
ggsave("fig-bar.png", p, width = 3.5, height = 2.8, dpi = 300)
```

**Grouped bars**: Add `aes(fill = group)` + `position = position_dodge(width = 0.7)` + `scale_fill_manual(values = aer_gray[c("light", "mid", "dark")])`.

---

## E. Time Series / Line Plot

```r
library(ggplot2)
library(ggthemes)
library(scales)

# --- AER-formatted time series ---
p <- ggplot(df, aes(x = year, y = value, group = series)) +
  geom_line(
    aes(linetype = series, color = series),
    linewidth = 0.6
  ) +
  scale_color_manual(values = c(
    "Series A" = aer_gray["dark"],
    "Series B" = aer_gray["mid"],
    "Series C" = aer_gray["med1"]
  )) +
  scale_linetype_manual(values = c(
    "Series A" = "solid",
    "Series B" = "dashed",
    "Series C" = "dotted"
  )) +
  labs(
    x = NULL,
    y = "Value (USD thousands)",
    color = NULL,
    linetype = NULL
  ) +
  scale_x_continuous(breaks = breaks_pretty(n = 6)) +
  scale_y_continuous(labels = label_comma()) +
  theme_aer(base_size = 10) +
  theme(
    legend.position = c(0.15, 0.85)
  )

ggsave("fig-timeseries.pdf", p, width = 7, height = 3.5, device = cairo_pdf)
ggsave("fig-timeseries.png", p, width = 7, height = 3.5, dpi = 300)
```

**Date axis**: Replace `scale_x_continuous()` with `scale_x_date(date_breaks = "2 years", date_labels = "%Y")`.

**Event lines**: Add `geom_vline(xintercept = event_date, linetype = "dotted", linewidth = 0.3) + annotate("text", x = event_date, y = Inf, label = "Policy change", vjust = 1.5, hjust = -0.1, size = 2.5, family = "Times")`.

---

## F. Faceted Multi-Panel

### Using facet_wrap / facet_grid

```r
library(ggplot2)
library(ggthemes)

# --- AER-formatted faceted plot ---
panel_labels <- c(
  "groupA" = "(a) First outcome",
  "groupB" = "(b) Second outcome",
  "groupC" = "(c) Third outcome"
)

p <- ggplot(df, aes(x = x_var, y = y_var)) +
  geom_point(size = 1.5, color = aer_gray["dark"], alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 0.5,
              color = aer_gray["dark"], linetype = "dashed") +
  facet_wrap(~ group, scales = "free_y",
             labeller = labeller(group = panel_labels)) +
  labs(
    x = "Independent variable",
    y = "Dependent variable"
  ) +
  theme_aer(base_size = 9) +
  theme(
    strip.text = element_text(hjust = 0, size = rel(1.0), face = "bold")
  )

ggsave("fig-panels.pdf", p, width = 7, height = 3.5, device = cairo_pdf)
ggsave("fig-panels.png", p, width = 7, height = 3.5, dpi = 300)
```

### Using facet_grid (two-dimensional panels)

```r
library(ggplot2)
library(ggthemes)

# --- AER-formatted facet_grid: outcome rows × subgroup columns ---
p <- ggplot(df, aes(x = x_var, y = y_var)) +
  geom_point(size = 1.5, color = aer_gray["dark"], alpha = 0.6) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 0.5,
              color = aer_gray["dark"], linetype = "dashed") +
  facet_grid(outcome ~ subgroup,
             scales = "free_y",
             labeller = labeller(
               outcome  = c("earn" = "Earnings", "hours" = "Hours worked"),
               subgroup = c("male" = "Male", "female" = "Female")
             )) +
  labs(
    x = "Independent variable",
    y = NULL
  ) +
  theme_aer(base_size = 9) +
  theme(
    strip.text = element_text(hjust = 0, size = rel(1.0), face = "bold"),
    strip.text.y = element_text(angle = 0, hjust = 0)
  )

ggsave("fig-grid.pdf", p, width = 7, height = 5, device = cairo_pdf)
ggsave("fig-grid.png", p, width = 7, height = 5, dpi = 300)
```

### Using patchwork

```r
library(ggplot2)
library(ggthemes)
library(patchwork)

p1 <- ggplot(df1, aes(x, y)) +
  geom_point(size = 1.5, color = aer_gray["dark"]) +
  labs(x = "X label", y = "Y label") +
  theme_aer(base_size = 9)

p2 <- ggplot(df2, aes(x, y)) +
  geom_line(linewidth = 0.6, color = aer_gray["dark"]) +
  labs(x = "X label", y = "Y label") +
  theme_aer(base_size = 9)

combined <- p1 + p2 +
  plot_annotation(tag_levels = "a", tag_prefix = "(", tag_suffix = ")") &
  theme(plot.tag = element_text(face = "bold", size = 11, family = "Times"))

ggsave("fig-combined.pdf", combined, width = 7, height = 3.5, device = cairo_pdf)
ggsave("fig-combined.png", combined, width = 7, height = 3.5, dpi = 300)
```

**Shared legend with patchwork**: Use `guide_area()` in `plot_layout()`:
```r
combined <- p1 + p2 + guide_area() +
  plot_layout(ncol = 2, guides = "collect") &
  theme(legend.position = "bottom")
```

---

## G. Map

```r
library(ggplot2)
library(ggthemes)
library(sf)

# --- AER-formatted choropleth map ---
p <- ggplot(map_sf) +
  geom_sf(
    aes(fill = value),
    color = "white", linewidth = 0.15
  ) +
  scale_fill_gradient(
    low = aer_gray["light"], high = aer_gray["dark"],
    name = "Value",
    labels = label_comma()
  ) +
  labs(fill = "Outcome") +
  theme_aer(base_size = 9) +
  theme(
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    axis.line = element_blank(),
    axis.title = element_blank(),
    legend.position = c(0.15, 0.25),
    legend.key.height = unit(0.8, "cm"),
    legend.key.width = unit(0.3, "cm")
  )

ggsave("fig-map.pdf", p, width = 7, height = 5, device = cairo_pdf)
ggsave("fig-map.png", p, width = 7, height = 5, dpi = 300)
```

**Discrete choropleth**: Replace `scale_fill_gradient()` with `scale_fill_manual(values = unname(aer_gray))`.

**Scale bar** (optional): Add `ggspatial::annotation_scale(location = "br", width_hint = 0.2)`.

---

## H. Math Notation in Labels

Use `latex2exp::TeX()` to render LaTeX math in axis labels, annotations, and legends.

### Common patterns

```r
library(latex2exp)

# Greek letters
labs(x = TeX(r"($\beta$ coefficient)"))

# Subscripts
labs(y = TeX(r"(Estimate of $\hat{\beta}_{1}$)"))

# Fractions / complex expressions
labs(x = TeX(r"($\frac{\Delta Y}{\Delta X}$)"))

# Superscripts
labs(y = TeX(r"(Income ($\times 10^{3}$ USD))"))

# Multiple Greek
labs(x = TeX(r"($\alpha + \beta \cdot X$)"))
```

### Dynamic label function

For facet labels or legend keys that need math notation:

```r
math_labeller <- function(labels) {
  lapply(labels, function(x) {
    lapply(x, function(val) {
      latex2exp::TeX(paste0("$\\", val, "$"))
    })
  })
}

# Usage in facet
facet_wrap(~ parameter, labeller = math_labeller)
```

### Inline annotation

```r
annotate("text", x = 2, y = 5,
         label = TeX(r"($p < 0.01$)"),
         size = 3, family = "Times")
```

---

## I. Color-to-Grayscale Conversion

When converting an existing color figure to AER-compliant grayscale:

### Common color scale replacements

| Original | Grayscale replacement |
|---|---|
| `scale_color_brewer(palette = "Set1")` | `scale_color_manual(values = unname(aer_gray))` |
| `scale_fill_viridis_c()` | `scale_fill_gradient(low = "#D9D9D9", high = "#363636")` |
| `scale_color_manual(values = c("red", "blue"))` | `scale_color_manual(values = c("#707070", "#363636"))` + linetype |
| `scale_fill_brewer(palette = "Blues")` | `scale_fill_gradient(low = "#D9D9D9", high = "#363636")` |
| `scale_color_hue()` (default) | `scale_color_manual(values = unname(aer_gray))` |

### Linetype alternatives

When grayscale alone is insufficient to distinguish series, add linetype:

```r
# Map same variable to both color and linetype
aes(color = group, linetype = group) +
scale_color_manual(values = c(
  "Group 1" = aer_gray["dark"],
  "Group 2" = aer_gray["mid"],
  "Group 3" = aer_gray["med1"]
)) +
scale_linetype_manual(values = c(
  "Group 1" = "solid",
  "Group 2" = "dashed",
  "Group 3" = "dotted"
))
```

### Shape alternatives for scatter plots

```r
aes(shape = group, color = group) +
scale_shape_manual(values = c(16, 17, 15, 3, 4)) +
scale_color_manual(values = c(aer_gray["dark"], aer_gray["mid"], aer_gray["med1"]))
```

Shapes: 16 = filled circle, 17 = filled triangle, 15 = filled square, 3 = plus, 4 = cross.
