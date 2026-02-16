# R Code Patterns for AER Tables

Code templates for each table type. Use these as the basis for rewriting user scripts.

---

## 1. Regression Table — fixest models (preferred)

Use when the user has `feols()`, `feglm()`, or `fepois()` model objects.

```r
library(fixest)

# --- Models (preserve user's existing model code) ---
m1 <- feols(y ~ x1 + x2 | fe1, data = df, vcov = "hetero")
m2 <- feols(y ~ x1 + x2 + x3 | fe1 + fe2, data = df, vcov = "hetero")
m3 <- feols(y ~ x1 + x2 + x3 + x4 | fe1 + fe2, data = df, vcov = ~cluster_var)

# --- AER-formatted table ---
etable(
  m1, m2, m3,
  tex = TRUE,
  file = "output/table_reg.tex",
  style.tex = style.tex("aer"),
  dict = c(
    x1 = "Years of education",
    x2 = "Experience",
    x3 = "Log income",
    x4 = "Female",
    fe1 = "State FE",
    fe2 = "Year FE"
  ),
  order = c("Years of education", "Experience", "Log income", "Female"),
  # drop = c("control_var1", "control_var2"),  # hide specific coefficients
  headers = list("^:_sym:" = list(
    "(1)", "(2)", "(3)"
  )),
  fitstat = ~ n + r2 + ar2,
  # extralines = list(
  #   "_^Controls" = c("No", "Yes", "Yes"),
  #   "_^Sample" = c("Full", "Full", "Urban")
  # ),
  notes = c(
    "Standard errors in parentheses. * p < 0.10, ** p < 0.05, *** p < 0.01.",
    "Robust standard errors used in columns (1)-(2); standard errors clustered at the state level in column (3)."
  ),
  title = "Effect of Education on Wages"
)
```

**Key `etable` arguments:**
- `style.tex = style.tex("aer")` — applies AER three-line style, checkmarks for FE, etc.
- `dict` — named vector mapping variable names to display labels.
- `order` — vector of label names controlling coefficient display order.
- `drop` / `keep` — hide/show specific coefficients by original name or regex.
- `fitstat` — formula selecting fit statistics: `~ n + r2 + ar2 + f + ivwald + sargan`.
- `extralines` — list of custom rows; prefix with `"_^"` for placement below FE indicators.
- `headers` — custom column headers; `"^:_sym:"` places symbols as column names.
- `notes` — character vector of footnote lines.
- `se.below = TRUE` — default; SEs below coefficients.
- `signif.code` — default is `c("***" = 0.01, "**" = 0.05, "*" = 0.10)`.

---

## 2. Regression Table — any model (modelsummary + tinytable)

Use for `lm()`, `glm()`, `felm()`, `plm()`, `ivreg()`, or mixed model objects.

```r
library(modelsummary)
library(tinytable)

# --- Models (preserve user's existing model code) ---
m1 <- lm(y ~ x1 + x2, data = df)
m2 <- lm(y ~ x1 + x2 + x3, data = df)

# --- AER-formatted table ---
tab <- modelsummary(
  list("(1)" = m1, "(2)" = m2),
  stars = c("*" = 0.10, "**" = 0.05, "***" = 0.01),
  coef_map = c(
    "x1" = "Years of education",
    "x2" = "Experience",
    "x3" = "Log income"
  ),
  gof_map = tribble(
    ~raw,        ~clean,          ~fmt,
    "nobs",      "Observations",  0,
    "r.squared", "R$^2$",         3,
    "adj.r.squared", "Adj. R$^2$", 3
  ),
  output = "tinytable"
)

# Add spanning header for dependent variable
tab <- tab |>
  group_tt(j = list("Log Wages" = 2:3)) |>
  style_tt(j = 2:3, align = "c") |>
  style_tt(i = 0, align = "c")

# Add notes
tab <- tab |>
  group_tt(j = list("\\\\footnotesize{\\\\textit{Notes:} Robust standard errors in parentheses. * p < 0.10, ** p < 0.05, *** p < 0.01.}" = 1))

save_tt(tab, "output/table_reg.tex", overwrite = TRUE)
```

**Notes on modelsummary + tinytable:**
- `coef_map` controls both labels AND order (only listed variables shown).
- `gof_map` with `tribble()` controls which fit stats appear, their labels, and decimal places.
- `add_rows` — tibble of extra rows inserted at a specified position.
- `vcov` argument for robust/clustered SEs: `vcov = "HC1"`, `vcov = ~cluster_var`.
- Column names in `list()` become the header labels.
- `group_tt(j = ...)` adds spanning column headers.
- tinytable output is tabularray-based (not booktabs).

**Adding controls/FE indicator rows with `add_rows`:**
```r
rows <- tribble(
  ~term,         ~"(1)", ~"(2)",
  "State FE",    "No",   "Yes",
  "Year FE",     "No",   "Yes",
  "Controls",    "No",   "Yes"
)
attr(rows, "position") <- c(7, 8, 9)  # row positions (after coefficients)

tab <- modelsummary(
  list("(1)" = m1, "(2)" = m2),
  add_rows = rows,
  # ... other arguments as above
  output = "tinytable"
)
```

---

## 3. Summary Statistics Table

Using `modelsummary::datasummary()` with tinytable backend.

```r
library(modelsummary)
library(tinytable)

# --- AER-formatted summary statistics ---
tab <- datasummary(
  (`Years of education` = edu_years) +
  (`Experience` = experience) +
  (`Log hourly wage` = log_wage) +
  (`Female` = female) +
  (`Age` = age) ~
  N + Mean + SD + Min + Max,
  data = df,
  output = "tinytable",
  title = "Summary Statistics"
)

tab <- tab |>
  style_tt(j = 2:6, align = "c") |>
  format_tt(j = c(2), digits = 0, num_fmt = "big.mark") |>  # N as integer
  format_tt(j = 3:4, digits = 3) |>  # Mean, SD
  format_tt(j = 5:6, digits = 2)     # Min, Max

save_tt(tab, "output/table_sumstats.tex", overwrite = TRUE)
```

**With panels:**
```r
# Panel A: Continuous variables
tab_a <- datasummary(
  (`Log wage` = log_wage) +
  (`Experience` = experience) +
  (`Age` = age) ~
  N + Mean + SD + Min + Max,
  data = df,
  output = "data.frame"
)

# Panel B: Binary variables
tab_b <- datasummary(
  (`Female` = female) +
  (`College degree` = college) +
  (`Urban` = urban) ~
  N + Mean + SD + Min + Max,
  data = df,
  output = "data.frame"
)

# Combine into paneled table
combined <- rbind(tab_a, tab_b)
tab <- tt(combined, caption = "Summary Statistics") |>
  group_tt(i = list("Panel A: Continuous Variables" = 1, "Panel B: Binary Variables" = 4)) |>
  style_tt(j = 2:6, align = "c")

save_tt(tab, "output/table_sumstats.tex", overwrite = TRUE)
```

**Key points:**
- Formula LHS: rename variables inline with backtick syntax `` (`Label` = var_name) ``.
- Formula RHS: built-in functions — `N`, `Mean`, `SD`, `Min`, `Max`, `Median`, `P25`, `P75`.
- Custom statistics: define functions, e.g., `SE = function(x) sd(x)/sqrt(length(x))`.
- `output = "data.frame"` useful for combining multiple summaries before passing to `tt()`.

---

## 4. Balance Table

Using `modelsummary::datasummary_balance()` with tinytable backend.

```r
library(modelsummary)
library(tinytable)

# --- AER-formatted balance table ---
tab <- datasummary_balance(
  ~ treatment,
  data = df |> select(treatment, age, income, education, female, married),
  dinm = TRUE,                 # difference in means with t-test
  dinm_statistic = "p.value",  # show p-values (or "statistic" for t-stats)
  fmt = 3,
  output = "tinytable",
  title = "Balance Table: Treatment vs. Control"
)

tab <- tab |>
  style_tt(j = 2:ncol(tab), align = "c")

save_tt(tab, "output/table_balance.tex", overwrite = TRUE)
```

**Key points:**
- Formula: `~ treatment_var` where `treatment_var` is the grouping variable.
- `dinm = TRUE` adds difference-in-means column with significance test.
- `dinm_statistic` controls what test statistic to display: `"p.value"`, `"statistic"` (t-stat), or `"std.error"`.
- Variables selected via formula LHS or by pre-selecting columns in the data frame.
- Rename variables for readable labels before passing to `datasummary_balance()`:
  ```r
  df_labeled <- df |>
    rename(
      `Age` = age,
      `Household income` = income,
      `Years of education` = education,
      `Female` = female,
      `Married` = married
    )
  ```

---

## 5. Custom / General Table

Using `tinytable::tt()` directly for maximum flexibility.

```r
library(tinytable)

# --- Build data frame (preserve user's existing data construction) ---
tab_df <- data.frame(
  Variable = c("GDP growth", "Inflation", "Unemployment", "Trade/GDP"),
  `Pre-reform` = c("3.2", "8.1", "7.5", "42.3"),
  `Post-reform` = c("5.1", "3.4", "5.2", "61.8"),
  `Difference` = c("1.9***", "-4.7***", "-2.3**", "19.5***"),
  check.names = FALSE
)

# --- AER-formatted table ---
tab <- tt(
  tab_df,
  caption = "Economic Indicators Before and After Reform",
  notes = c(
    "\\textit{Notes:} Data from World Bank WDI. Pre-reform: 1990--1999; Post-reform: 2000--2009.",
    "* p < 0.10, ** p < 0.05, *** p < 0.01."
  )
)

tab <- tab |>
  style_tt(j = 2:4, align = "c") |>
  group_tt(j = list("Mean Values" = 2:3, " " = 4)) |>  # spanning header
  format_tt(escape = TRUE)  # escape special chars if needed

save_tt(tab, "output/table_custom.tex", overwrite = TRUE)
```

**Row grouping (panels):**
```r
tab <- tt(combined_df) |>
  group_tt(i = list(
    "\\textit{Panel A: Developed Countries}" = 1,
    "\\textit{Panel B: Developing Countries}" = 6
  ))
```

**Column spanning headers:**
```r
tab <- tt(df) |>
  group_tt(j = list(
    "OLS" = 2:3,
    "IV" = 4:5
  ))
```

**Cell-level formatting:**
```r
tab <- tt(df) |>
  style_tt(i = 1:3, j = 2, bold = TRUE) |>     # bold specific cells
  style_tt(i = 0, align = "c") |>               # center header row
  format_tt(j = 2:4, digits = 3) |>             # 3 decimal places
  format_tt(j = 5, digits = 0, num_fmt = "big.mark")  # integer with commas
```

---

## 6. PDF Preview Helper

Reusable function to compile any .tex table into a standalone PDF for quick visual inspection.

```r
#' Compile a .tex table file into a standalone PDF preview
#'
#' @param tex_file Path to the .tex file (from save_tt or etable)
#' @param open Logical; open the PDF after compilation (macOS)
preview_tex <- function(tex_file, open = TRUE) {
  # Read the table .tex content
  tex_lines <- readLines(tex_file)
  tex_body <- paste(tex_lines, collapse = "\n")

  # Detect if tinytable (tabularray) or booktabs
  is_tabularray <- any(grepl("tblr|tabularray", tex_lines))
  is_booktabs <- any(grepl("\\\\toprule|\\\\midrule|\\\\bottomrule|booktabs", tex_lines))

  # Build preamble
  preamble <- c(
    "\\documentclass[11pt, border=10pt]{standalone}",
    "\\usepackage[T1]{fontenc}",
    "\\usepackage{lmodern}",
    "\\usepackage{amssymb}  % for checkmark"
  )

  if (is_tabularray) {
    # tinytable uses tabularray; extract preamble lines from the .tex file
    # tinytable save_tt() often includes preamble comments/declarations
    tabularray_preamble <- tex_lines[grepl("^\\\\usepackage|^\\\\NewTableCommand|^\\\\newcommand|^\\\\DefTblrTemplate|^\\\\SetTblrStyle", tex_lines)]
    preamble <- c(preamble,
      "\\usepackage{tabularray}",
      "\\usepackage{float}",
      "\\usepackage{graphicx}",
      "\\usepackage{codehigh}",
      "\\usepackage[normalem]{ulem}",
      "\\usepackage{bookmark}",
      tabularray_preamble
    )
    # Remove preamble lines from body so they aren't duplicated
    tex_body_lines <- tex_lines[!grepl("^\\\\usepackage|^\\\\NewTableCommand|^\\\\newcommand|^\\\\DefTblrTemplate|^\\\\SetTblrStyle|^\\\\documentclass|^\\\\begin\\{document\\}|^\\\\end\\{document\\}", tex_lines)]
    tex_body <- paste(tex_body_lines, collapse = "\n")
  } else if (is_booktabs) {
    preamble <- c(preamble,
      "\\usepackage{booktabs}",
      "\\usepackage{threeparttable}",
      "\\usepackage{graphicx}"
    )
  }

  # Assemble standalone document
  doc <- paste(c(
    preamble,
    "",
    "\\begin{document}",
    "",
    tex_body,
    "",
    "\\end{document}"
  ), collapse = "\n")

  # Write standalone .tex file
  standalone_file <- sub("\\.tex$", "_preview.tex", tex_file)
  writeLines(doc, standalone_file)

  # Compile with tinytex
  if (!requireNamespace("tinytex", quietly = TRUE)) {
    message("Install tinytex: install.packages('tinytex'); tinytex::install_tinytex()")
    return(invisible(NULL))
  }

  pdf_file <- tinytex::lualatex(standalone_file, pdf_file = sub("\\.tex$", ".pdf", standalone_file))

  message("PDF preview: ", pdf_file)

  # Open on macOS
  if (open && Sys.info()["sysname"] == "Darwin") {
    system2("open", pdf_file)
  }

  invisible(pdf_file)
}
```

**Usage:**
```r
# After saving a table
save_tt(tab, "output/table_reg.tex", overwrite = TRUE)
preview_tex("output/table_reg.tex")

# Or with etable output
etable(m1, m2, tex = TRUE, file = "output/table_reg.tex",
       style.tex = style.tex("aer"))
preview_tex("output/table_reg.tex")
```

**Notes:**
- Requires `tinytex` R package and a TinyTeX installation (`tinytex::install_tinytex()`).
- Uses `lualatex` for Unicode support and modern font handling.
- The `standalone` document class with `border=10pt` produces a cropped PDF of just the table.
- For tabularray tables, the function extracts preamble declarations that tinytable embeds in the .tex output.
- The preview file is saved as `*_preview.tex` / `*_preview.pdf` alongside the original.
