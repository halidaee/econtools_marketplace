# Cross-Reference Validation

## A. Quarto Cross-Reference Validation

### A.1 Reference Patterns

References in `.qmd` files that point to labeled elements:

| Prefix | Target | Regex pattern | Example |
|---|---|---|---|
| `@fig-` | Figure | `@fig-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@fig-coefficients` |
| `@tbl-` | Table | `@tbl-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@tbl-sumstats` |
| `@eq-` | Equation | `@eq-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@eq-utility` |
| `@sec-` | Section | `@sec-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@sec-results` |
| `@thm-` | Theorem | `@thm-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@thm-welfare` |
| `@lem-` | Lemma | `@lem-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@lem-monotone` |
| `@cor-` | Corollary | `@cor-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@cor-uniqueness` |
| `@def-` | Definition | `@def-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@def-equilibrium` |
| `@prp-` | Proposition | `@prp-[a-zA-Z0-9][-a-zA-Z0-9]*` | `@prp-existence` |

**Important**: References must NOT be preceded by `[` (which would make them citation keys) or be inside code blocks / inline code.

Regex to extract all references (excluding citations):
```
(?<!\[)@(fig|tbl|eq|sec|thm|lem|cor|def|prp)-[a-zA-Z0-9][-a-zA-Z0-9]*
```

### A.2 Label Definition Patterns

Labels can be defined in four ways in Quarto:

**1. R/Python chunk with label option (figures and tables)**
```
```{r}
#| label: fig-coefficients
#| fig-cap: "Coefficient estimates from baseline specification"

ggplot(...) + ...
```
```
Both `label:` and `fig-cap:` (or `tbl-cap:`) are REQUIRED for the cross-reference to work.

Regex for chunk label:
```
#\|\s*label:\s*(fig|tbl|thm|lem|cor|def|prp)-[a-zA-Z0-9][-a-zA-Z0-9]*
```

Regex for figure caption (must co-occur with fig- label):
```
#\|\s*fig-cap:\s*["'].*["']
```

Regex for table caption (must co-occur with tbl- label):
```
#\|\s*tbl-cap:\s*["'].*["']
```

**2. Inline image with attribute (figures)**
```markdown
![Caption text](path/to/image.png){#fig-label}
```

Regex:
```
!\[.*?\]\(.*?\)\{#(fig)-[a-zA-Z0-9][-a-zA-Z0-9]*\}
```

**3. Section heading with attribute**
```markdown
## Results {#sec-results}
```

Regex:
```
^#{1,6}\s+.*\{#(sec)-[a-zA-Z0-9][-a-zA-Z0-9]*\}
```

**4. Equation with attribute**
```markdown
$$
Y_i = \alpha + \beta X_i + \epsilon_i
$$ {#eq-model}
```

Regex (the attribute follows the closing `$$` on the same or next line):
```
\$\$\s*\{#(eq)-[a-zA-Z0-9][-a-zA-Z0-9]*\}
```

**5. Div-based labels (theorems, etc.)**
```markdown
::: {#thm-welfare}
## Welfare Theorem
Content here.
:::
```

Regex:
```
:::\s*\{#(thm|lem|cor|def|prp)-[a-zA-Z0-9][-a-zA-Z0-9]*\}
```

### A.3 Validation Algorithm

```
1. COLLECT all references:
   - Scan all .qmd files for @prefix-id patterns (excluding code blocks and citations)
   - Record: ref_id, file, line_number, surrounding_text

2. COLLECT all label definitions:
   - Scan for chunk labels (#| label: prefix-id)
   - Scan for inline image labels ({#fig-id})
   - Scan for heading labels ({#sec-id})
   - Scan for equation labels ({#eq-id})
   - Scan for div labels ({#thm-id}, etc.)
   - Record: label_id, file, line_number, definition_type

3. VALIDATE chunk labels:
   - For each fig- label: verify #| fig-cap: exists in same chunk
   - For each tbl- label: verify #| tbl-cap: exists in same chunk
   - If cap is missing: report ERROR (label exists but ref will break)

4. MATCH references to labels:
   - For each reference: look for matching label_id
   - If no match: DANGLING REF → ERROR
   - Compute edit distance to all labels; if distance ≤ 2: suggest near-miss

5. CHECK for orphaned labels:
   - For each label: look for at least one matching reference
   - If no match: ORPHANED LABEL → WARNING

6. REPORT results grouped by severity
```

### A.4 Common Quarto Pitfalls

| Problem | Symptom | Cause | Fix |
|---|---|---|---|
| Chunk label without `fig-cap` | `@fig-X` renders as literal text "?@fig-X?" | Quarto needs both label AND caption to register a cross-referenceable figure | Add `#\| fig-cap: "Caption text"` to the chunk |
| Chunk label without `tbl-cap` | `@tbl-X` renders as literal text | Same as above for tables | Add `#\| tbl-cap: "Caption text"` to the chunk |
| Wrong prefix in label vs ref | `@fig-X` but label is `{#tbl-X}` | Copy-paste error | Ensure label and reference prefixes match |
| Underscore vs hyphen | `#\| label: fig_results` but ref is `@fig-results` | Quarto uses hyphens, not underscores | Change label to `fig-results` |
| Duplicate label IDs | Two chunks with `#\| label: fig-results` | Copy-paste, forgotten rename | Give each chunk a unique label |
| Label in caption text | `#\| fig-cap: "Results {#fig-results}"` | Confusion about where label goes | Label goes in `#\| label:`, not inside caption |
| Missing `#\|` prefix | `label: fig-results` (no `#\|`) | knitr vs Quarto syntax confusion | Add `#\|` prefix: `#\| label: fig-results` |
| Old knitr syntax | `fig.cap = "Caption"` | Pre-Quarto R Markdown syntax | Convert to `#\| fig-cap: "Caption"` |
| Ref inside code block | `` `@fig-results` `` | Ref is inside inline code | Remove backticks around the reference |
| Space after `@` | `@ fig-results` | Typo | Remove space: `@fig-results` |
| Citation vs cross-ref confusion | `[@fig-results]` | Square brackets make it a citation | Remove brackets: `@fig-results` |
| Label in YAML vs chunk | `fig-cap` in YAML header vs chunk | Quarto chunk options take precedence | Use chunk-level `#\|` options for per-figure captions |

## B. LaTeX Cross-Reference Validation

### B.1 Reference Commands

| Command | Regex pattern | Example |
|---|---|---|
| `\ref{...}` | `\\ref\{([^}]+)\}` | `\ref{fig:coefficients}` |
| `\autoref{...}` | `\\autoref\{([^}]+)\}` | `\autoref{tab:sumstats}` |
| `\eqref{...}` | `\\eqref\{([^}]+)\}` | `\eqref{eq:utility}` |
| `\pageref{...}` | `\\pageref\{([^}]+)\}` | `\pageref{sec:results}` |
| `\cref{...}` | `\\cref\{([^}]+)\}` | `\cref{fig:coefs,fig:robust}` |
| `\Cref{...}` | `\\Cref\{([^}]+)\}` | `\Cref{tab:main}` |
| `\nameref{...}` | `\\nameref\{([^}]+)\}` | `\nameref{sec:intro}` |

**Note**: `\cref` and `\Cref` can contain comma-separated lists of labels.

### B.2 Label Definitions

| Convention prefix | Environment | Regex |
|---|---|---|
| `fig:` | figure | `\\label\{fig:([^}]+)\}` |
| `tab:` | table | `\\label\{tab:([^}]+)\}` |
| `eq:` | equation | `\\label\{eq:([^}]+)\}` |
| `sec:` | section | `\\label\{sec:([^}]+)\}` |
| `thm:` | theorem | `\\label\{thm:([^}]+)\}` |
| `lem:` | lemma | `\\label\{lem:([^}]+)\}` |
| `app:` | appendix | `\\label\{app:([^}]+)\}` |

General label regex: `\\label\{([^}]+)\}`

**Placement rule**: `\label{}` must appear AFTER `\caption{}` in figure/table environments, or AFTER `\section{}`/`\subsection{}` for sections. A `\label{}` before `\caption{}` may reference the section instead of the figure.

### B.3 Validation Algorithm

```
1. COLLECT all references:
   - Scan all .tex files for \ref{}, \autoref{}, \eqref{}, \pageref{}, \cref{}, \Cref{}
   - Expand comma-separated lists in \cref{} commands
   - Exclude commented lines (starting with %)
   - Record: ref_id, file, line_number, command_type

2. COLLECT all label definitions:
   - Scan all .tex files for \label{} commands
   - Exclude commented lines
   - Record: label_id, file, line_number, enclosing_environment

3. CHECK label placement:
   - For figure/table environments: verify \label appears after \caption
   - If before: WARNING (label may reference wrong element)

4. MATCH and REPORT:
   - Same as Quarto algorithm: dangling refs → ERROR, orphaned labels → WARNING
   - Near-miss detection with edit distance ≤ 2

5. CHECK for common issues:
   - Empty \ref{} or \label{}
   - Spaces inside labels: \label{fig: coefs} (will fail)
   - Mixed conventions: some labels use fig: prefix, others don't
```

### B.4 Cross-File References

LaTeX documents often span multiple files. To validate cross-file references:

1. **Find the root document**: Look for `\documentclass{}` or the file specified in a Makefile/latexmk config
2. **Trace includes**: Recursively follow `\input{filename}` and `\include{filename}`
   - `\input{}` may or may not include `.tex` extension
   - `\include{}` always adds `.tex`
   - Check both `filename` and `filename.tex`
3. **Build global label/ref maps** across all included files
4. **Report with file paths**: Always include which file a label or ref appears in

Regex for includes:
```
\\input\{([^}]+)\}
\\include\{([^}]+)\}
```

## C. Mixed Documents

Quarto files may contain raw LaTeX blocks:

```markdown
```{=latex}
\begin{figure}
\includegraphics{plot.pdf}
\caption{Results}
\label{fig:results}
\end{figure}
```
```

**Validation rules for mixed documents:**

1. Check BOTH reference systems:
   - Quarto `@fig-X` references
   - LaTeX `\ref{fig:X}` references inside `{=latex}` blocks
2. Labels inside `{=latex}` blocks are LaTeX labels (use `\ref{}` not `@`)
3. Labels outside `{=latex}` blocks are Quarto labels (use `@` not `\ref{}`)
4. Flag cross-system references as ERROR: e.g., `@fig-X` referencing a `\label{fig:X}`
5. Quarto `{{< include file.qmd >}}` directives: scan included files too
