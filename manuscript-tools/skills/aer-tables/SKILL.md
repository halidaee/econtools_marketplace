---
name: aer-tables
description: Use when the user has an R script producing a table and wants it formatted for AER or economics journal submission, mentions AER style, booktabs formatting, journal-ready tables, or asks to make a table publication-ready
---

# AER Table Formatting

Rewrite R table-producing scripts to output AER-compliant LaTeX tables with PDF preview.

## Constraints

- **NEVER** change table content: which variables, statistics, columns, or samples are reported.
- **CAN** change R packages and formatting code.
- **MUST** preserve all analysis/estimation code upstream of the table.
- **MUST** ensure all required packages are loaded (`library()` calls).

## Workflow

1. **Read** the user's R script completely.
2. **Identify table type** using the detection table below.
3. **Identify content**: variables, statistics, models, labels, notes, panels.
4. **Rewrite formatting** using templates from `references/r-code-patterns.md`.
5. **Apply rules** from `references/aer-style-guide.md`.
6. **Output .tex file** via `save_tt()` or `etable(..., file=)`.
7. **Add PDF preview** using `preview_tex()` helper from `references/r-code-patterns.md`.
8. **Verify** all required `library()` calls are present.

## Table Type Detection

| Signal | Type | Package |
|---|---|---|
| `feols()` / `feglm()` / `fepois()` models | Regression | `fixest::etable` + `style.tex("aer")` |
| `lm()` / `glm()` / `felm()` / `plm()` / other models | Regression | `modelsummary` + tinytable |
| Mean / SD / min / max / quantile summaries | Summary stats | `modelsummary::datasummary` + tinytable |
| Treatment vs. control group comparison | Balance table | `modelsummary::datasummary_balance` + tinytable |
| Manual data frame → table | Custom | `tinytable::tt()` |

## Quick Reference

- **Rules**: Three horizontal lines only (top, header-sep, bottom). No vertical lines.
- **Stars**: `*` 10%, `**` 5%, `***` 1% — on coefficients only, never on SEs.
- **SEs**: In parentheses, line below coefficient. Type stated in notes.
- **Decimals**: Coefficients/SEs/R² = 3; N = integer with commas.
- **Labels**: Readable English. Interactions: `$\times$`. Logs: prefix `Log`.
- **Headers**: Model numbers `(1)`, `(2)`, etc. Dep var as spanning header.
- **Notes**: Below bottom rule, `\footnotesize`. "*Notes:*" italic, then SE type, stars, source.
- **Output**: `.tex` file + standalone PDF preview via `preview_tex()`.
