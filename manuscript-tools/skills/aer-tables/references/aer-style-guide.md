# AER Table Style Guide

Complete formatting rules for American Economic Review (AER) tables. Apply these rules to every table produced by the skill.

---

## Layout

- **Three horizontal rules only**: top rule, header-separator rule, bottom rule. No other horizontal lines except to separate panels.
- **No vertical rules** anywhere. No cell borders.
- LaTeX implementation: `\toprule`, `\midrule`, `\bottomrule` (booktabs) or tabularray equivalents (tinytable).
- Additional `\midrule` permitted above each panel header and above the goodness-of-fit block.

## Column Headers

- All column headers **centered**.
- Regression tables: model numbers in parentheses — `(1)`, `(2)`, `(3)`, etc.
- If models share a dependent variable, show it as a **spanning header** above the model numbers (e.g., `\multicolumn{3}{c}{Log Wages}`).
- If models have different dependent variables, show each above its column or group of columns.

## Dependent Variable Row

- Displayed as a spanning header row between the top rule and the model number row.
- Italic or plain (both acceptable in AER). Prefer plain for consistency with tinytable/etable defaults.

## Number Formatting

| Element | Format | Example |
|---|---|---|
| Coefficients | 3 decimal places | `0.542` |
| Standard errors | 3 decimal places | `(0.087)` |
| R-squared | 3 decimal places | `0.847` |
| Adjusted R² | 3 decimal places | `0.832` |
| Observations (N) | Integer, comma-separated | `12,450` |
| Other counts | Integer, comma-separated | `1,203` |
| Percentages | 1–2 decimal places | `52.3` |
| Dollar amounts | 2 decimal places, comma-separated | `1,234.56` |

## Stars (Significance)

- Three levels: `*` p < 0.10, `**` p < 0.05, `***` p < 0.01
- Stars placed **after the coefficient value**, on the same line: `0.542***`
- **No stars on standard errors.**
- Star definitions restated in table notes.

## Standard Errors

- Displayed in **parentheses** on the line directly below the coefficient: `(0.087)`
- No stars on the SE line.
- SE type (robust, clustered, etc.) stated in table notes, not in the table body.

## Variable Labels

- Use **readable English labels**, not variable names.
  - Good: `Log GDP per capita`, `Years of education`, `Female`
  - Bad: `log_gdp_pc`, `yrs_edu`, `female_d`
- Interactions: use `$\times$` (e.g., `Treatment $\times$ Post`).
- Squared terms: use superscript (e.g., `Age$^2$`).
- Log transformations: prefix with `Log` (e.g., `Log income`).

## Panel Structure

- Panel headers: **left-aligned**, italic or bold italic.
- Format: `*Panel A: Description*` or `\textit{Panel A: Description}`
- A `\midrule` (horizontal rule) **above** each panel header.
- Panels share the same column structure and alignment.

## Goodness-of-Fit Rows

- Separated from coefficient rows by a `\midrule`.
- Standard rows (in order):
  1. Fixed effects / controls indicators — `Yes` / `No` or checkmarks (`$\checkmark$`)
  2. Observations (N)
  3. R-squared
  4. Adjusted R-squared
  5. Other fit statistics as needed (F-stat, log-likelihood, etc.)
- Row labels left-aligned, values centered under columns.
- For fixest etable: checkmarks are the default for FE indicators with `style.tex("aer")`.

## Notes Section

- Placed **below the bottom rule**.
- Font: `\footnotesize` (or `\small` if table already uses `\footnotesize`).
- Structure:
  1. `\textit{Notes:}` followed by a description of the table.
  2. Standard error description: e.g., "Robust standard errors in parentheses." or "Standard errors clustered at the state level in parentheses."
  3. Star definitions: `* p < 0.10, ** p < 0.05, *** p < 0.01`
  4. Data source (if applicable).
- For tinytable: use the `notes` argument in `tt()` or append manually to .tex.
- For etable: use the `notes` argument.
- Wrap in `threeparttable` environment if using booktabs/etable.

## LaTeX Preamble Requirements

**For tinytable output (tabularray-based):**
- tinytable auto-generates required preamble declarations via `save_tt()`.
- In standalone documents, include the preamble block from `save_tt()` output.
- Key packages loaded by tinytable: `tabularray`, `codehigh`, `float`.

**For fixest etable output (booktabs-based):**
- Required: `\usepackage{booktabs}`, `\usepackage{threeparttable}`
- Optional: `\usepackage{amssymb}` (for `$\checkmark$`)

## Table Sizing

- Default: normal body font size.
- If table is wide: apply `\small` or `\footnotesize` to the table environment.
- Same serif font as body text (do not change fonts).
- For tinytable: `style_tt(fontsize = 0.9)` or wrap in `{\small ... }`.
- For etable: `fitstat.just = "center"` is default; use `adjustbox` or font size commands for wide tables.

## Float Placement

- Tables use `\begin{table}[t]` or `\begin{table}[!htbp]` placement.
- Caption above the table: `\caption{Table Title}`.
- Label for cross-referencing: `\label{tab:identifier}`.
