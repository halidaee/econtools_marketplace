---
name: proof-checker
description: Use when the user wants to check a Quarto or LaTeX document for broken cross-references, terminology consistency, acronym errors, or writing quality issues. Especially useful for finding broken @fig- or @tbl- references in .qmd files.
---

# Proof / Style Checker

## Overview

Validates cross-references (especially Quarto `@fig-`, `@tbl-` — the most common pain point), checks terminology consistency, tracks acronyms, and flags prose quality issues. Works with `.qmd` and `.tex` files, including mixed Quarto+LaTeX documents.

## Constraints

- **NEVER** auto-change document content — this is a checking/reporting tool only
- **ALWAYS** report issues with file path, line number, and surrounding context
- **MUST** distinguish severity: ERROR (will break output), WARNING (likely mistake), SUGGESTION (style improvement)
- **CAN** suggest fixes, including near-miss label corrections
- **MUST** scan all project files for multi-file documents (follow `{{< include >}}`, `\input{}`, `\include{}`)

## Modes

### Mode A: Full Check (default)

Run all checks in priority order. Triggered by: "proof check", "check this document", "run proof-checker".

### Mode B: Cross-Reference Only

Run checks 1–3 only. Triggered by: "check references", "find broken links", "check refs", "broken references".

### Mode C: Style Only

Run checks 4–8 only. Triggered by: "check writing", "style check", "check prose".

## Check Priority Table

| Priority | Check | Severity | Reference |
|---|---|---|---|
| 1 | Dangling Quarto refs (`@fig-X` with no matching label) | ERROR | `references/crossref-validation.md` §A |
| 2 | Dangling LaTeX refs (`\ref{X}` with no `\label{X}`) | ERROR | `references/crossref-validation.md` §B |
| 3 | Orphaned labels (defined but never referenced) | WARNING | `references/crossref-validation.md` §A–B |
| 4 | Undefined acronyms (used before first definition) | WARNING | `references/style-rules.md` §B |
| 5 | Inconsistent terminology ("Figure" vs "figure" for specific refs) | WARNING | `references/style-rules.md` §A |
| 6 | Number formatting (when to spell out vs digits) | SUGGESTION | `references/style-rules.md` §C |
| 7 | Excessive hedging density (may/might/could/suggests clusters) | SUGGESTION | `references/style-rules.md` §D |
| 8 | Long sentences (>40 words) | SUGGESTION | `references/style-rules.md` §D |

## Workflow

1. **Detect document type**: `.qmd` → Quarto mode; `.tex` → LaTeX mode; both present → mixed mode
2. **Collect all files**: Follow includes/inputs to build complete file list
3. **Run checks** in priority order per the selected mode
4. **Pattern-match known errors** using `references/common-errors.md` (knitr syntax in Quarto, unmatched environments, unclosed math, unescaped special characters)
5. **Near-miss detection**: For dangling refs, compute edit distance to all known labels; suggest matches with distance <= 2
6. **Generate report** in the output format below

## Output Format

```
=== PROOF CHECK REPORT ===

--- ERRORS (2) ---

[E1] DANGLING REF: @fig-regresion
     File: analysis.qmd, Line 142
     Context: "As shown in @fig-regresion, the effect is..."
     Suggestion: Did you mean @fig-regression? (label found at line 87)

[E2] DANGLING REF: @tbl-sumstats
     File: analysis.qmd, Line 45
     Context: "Table @tbl-sumstats presents summary..."
     Suggestion: No similar label found. Check that the code chunk has
                 both `#| label: tbl-sumstats` AND `#| tbl-cap: "..."`

--- WARNINGS (3) ---

[W1] ORPHANED LABEL: {#fig-robustness}
     File: appendix.qmd, Line 210
     This label is defined but never referenced in any document.

[W2] UNDEFINED ACRONYM: "IV" used at line 23 (intro.qmd)
     First definition found at line 89 (methodology.qmd)
     Suggestion: Define as "instrumental variables (IV)" at first use

[W3] INCONSISTENT TERMINOLOGY
     "Figure" (capitalized, 12 occurrences) vs "figure" (lowercase, 3 occurrences)
     when referring to specific numbered figures.
     Lines with lowercase: 45, 102, 198

--- SUGGESTIONS (2) ---

[S1] LONG SENTENCE (47 words): analysis.qmd, Line 156
     "We find that the treatment effect on..."
     Consider splitting into two sentences.

[S2] HEDGING CLUSTER: methodology.qmd, Lines 78–82
     5 hedging words in one paragraph: "may", "might", "could", "possibly", "suggests"
     Consider strengthening language.

=== SUMMARY ===
Errors: 2 | Warnings: 3 | Suggestions: 2
```

## Quick Reference

### Quarto label rules
- Figure from R chunk: needs BOTH `#| label: fig-X` AND `#| fig-cap: "Caption"`
- Figure from image: `![Caption](path){#fig-X}`
- Table from R chunk: needs BOTH `#| label: tbl-X` AND `#| tbl-cap: "Caption"`
- Equation: `$$ ... $$ {#eq-X}`
- Section: `## Heading {#sec-X}`
- Reference syntax: `@fig-X`, `@tbl-X`, `@eq-X`, `@sec-X`

### Acronym rule
Define at first use: "full term (ABBREV)". Use abbreviation only thereafter.

### Number rule
Spell out one through ten in prose. Use digits for 11+, all statistical values, and numbers with units.

### Capitalization rule
"Figure 1" (specific) vs "the figure" (generic). Same for Table, Section, Equation, Appendix, Panel.

### Common econ acronyms
ATE, ATT, ITT, IV, OLS, RCT, RDD, DID, DiD, FE, RE, 2SLS, GMM, LATE, TOT, SUTVA, CIA, MTE, MLE, SE, FDR, FWER, GDP, CPI, PPP
