# Common Errors

## A. Quarto-Specific Issues

### A.1 Missing `fig-cap` on Labeled Chunks (Most Common)

**Problem**: A code chunk has `#| label: fig-X` but no `#| fig-cap:`. Quarto generates the figure but does NOT create a cross-referenceable label. All `@fig-X` references render as broken text.

```yaml
# BROKEN — no fig-cap
#| label: fig-results
ggplot(df, aes(x, y)) + geom_point()
```

```yaml
# FIXED — both label and fig-cap present
#| label: fig-results
#| fig-cap: "Scatter plot of treatment effects"
ggplot(df, aes(x, y)) + geom_point()
```

**Same issue for tables**: `#| label: tbl-X` requires `#| tbl-cap:`.

### A.2 Old knitr Syntax vs Quarto Syntax

| knitr (R Markdown) | Quarto | Notes |
|---|---|---|
| `fig.cap = "Caption"` | `#\| fig-cap: "Caption"` | YAML-style chunk options |
| `fig.width = 7` | `#\| fig-width: 7` | Dots become hyphens |
| `fig.height = 5` | `#\| fig-height: 5` | |
| `out.width = "80%"` | `#\| out-width: "80%"` | |
| `results = "asis"` | `#\| output: asis` | Different keyword |
| `echo = FALSE` | `#\| echo: false` | Lowercase boolean |
| `message = FALSE` | `#\| message: false` | |
| `warning = FALSE` | `#\| warning: false` | |
| `label = "fig-X"` in chunk header | `#\| label: fig-X` inside chunk | Label moves inside |

**Detection**: Flag `fig.cap`, `fig.width`, `out.width`, etc. (dot notation) inside Quarto chunks — these are knitr syntax and will be silently ignored.

### A.3 Citation vs Cross-Reference Confusion

| Syntax | Meaning | Renders as |
|---|---|---|
| `@authorYear` | Citation (natbib/citeproc) | "Author (Year)" |
| `[@authorYear]` | Citation in brackets | "(Author Year)" |
| `@fig-results` | Cross-reference to figure | "Figure 1" |
| `[@fig-results]` | INCORRECT — tries to cite "fig-results" | broken citation |

**Detection**: Flag `[@fig-`, `[@tbl-`, `[@eq-`, `[@sec-` as likely cross-reference errors (should not have square brackets).

### A.4 Quarto Include Directives

Quarto uses `{{< include file.qmd >}}` to include other files. When checking cross-references:
- Follow all include directives
- Labels defined in included files are valid targets
- References in included files need labels from ANY file in the project
- Flag if included file doesn't exist

### A.5 Sub-Figures and Sub-Tables

Quarto supports sub-figures with layout attributes:

```markdown
::: {#fig-combined layout-ncol=2}

![First panel](plot1.png){#fig-panel-a}

![Second panel](plot2.png){#fig-panel-b}

Main caption for the combined figure
:::
```

**Cross-reference rules**:
- `@fig-combined` references the whole figure
- `@fig-panel-a` references sub-figure (a)
- Both the div label and sub-figure labels must be present
- Missing the outer div label breaks `@fig-combined`

## B. LaTeX-Specific Issues

### B.1 Unmatched Environments

**Problem**: Every `\begin{env}` must have a matching `\end{env}`.

**Common mismatches**:
- `\begin{figure}` ... `\end{table}` (copy-paste error)
- `\begin{figure*}` ... `\end{figure}` (missing asterisk)
- Nested environments closed in wrong order

**Detection**: Stack-based matching — push on `\begin`, pop on `\end`, verify names match.

### B.2 Unclosed Math Delimiters

| Delimiter | Closing | Notes |
|---|---|---|
| `$` | `$` | Inline math — count must be even per line |
| `\(` | `\)` | Alternative inline math |
| `\[` | `\]` | Display math |
| `$$` | `$$` | Display math (less preferred in LaTeX) |
| `\begin{equation}` | `\end{equation}` | Numbered display |
| `\begin{align}` | `\end{align}` | Numbered aligned |
| `\begin{align*}` | `\end{align*}` | Unnumbered aligned |

**Detection**: Track open/close delimiters. Flag unclosed math at end of paragraph or section.

### B.3 Common Typos and Syntax Errors

| Error | Correct | Notes |
|---|---|---|
| `\textit something` | `\textit{something}` | Missing braces |
| `\cite {key}` | `\cite{key}` | Space before brace |
| `\cite{}` | `\cite{key}` | Empty citation |
| `\cite{key1; key2}` | `\cite{key1, key2}` | Semicolon should be comma |
| `\cite{key1,key2}` | `\cite{key1, key2}` | Missing space (works but inconsistent) |
| `\ref {fig:x}` | `\ref{fig:x}` | Space before brace |
| `\being{figure}` | `\begin{figure}` | Typo in \begin |
| `\lable{fig:x}` | `\label{fig:x}` | Common typo |
| `\captoin{...}` | `\caption{...}` | Common typo |
| `\includegraphics[width=\textwidth]` | `\includegraphics[width=\textwidth]{file}` | Missing filename |

### B.4 `\label` Placement

**Rule**: In `figure` and `table` environments, `\label{}` must appear AFTER `\caption{}`.

```latex
% CORRECT
\begin{figure}
  \includegraphics{plot.pdf}
  \caption{Results of baseline estimation}
  \label{fig:baseline}
\end{figure}

% INCORRECT — label before caption, references the section number
\begin{figure}
  \label{fig:baseline}
  \includegraphics{plot.pdf}
  \caption{Results of baseline estimation}
\end{figure}
```

**Detection**: In figure/table environments, flag `\label` appearing before `\caption`.

### B.5 natbib Citation Issues

| Error | Problem | Fix |
|---|---|---|
| `\citep{key` | Missing closing brace | Add `}` |
| `\citet[p. 5]{key}` | Correct (optional arg) | No fix needed |
| `\cite{key1 key2}` | Missing separator | Add comma: `\cite{key1, key2}` |
| Key not in .bib | Undefined citation | Add entry to .bib or fix key |
| `\bibliography{}` empty | No bibliography file | Add .bib filename |

## C. Cross-Platform Issues

### C.1 Line Endings

| Platform | Line ending | Hex |
|---|---|---|
| Unix/macOS | LF (`\n`) | `0A` |
| Windows | CRLF (`\r\n`) | `0D 0A` |

**Problem**: Mixed line endings can cause subtle parsing issues in LaTeX and Quarto. Some regex patterns may fail to match across CRLF line boundaries.

**Detection**: Flag files with mixed line endings (some LF, some CRLF).

### C.2 File Path Separators

**Problem**: `\input{sections\results.tex}` (backslash) works on Windows but fails on Unix.

**Rule**: Always use forward slashes in `\input{}`, `\include{}`, `\includegraphics{}`:
```latex
\input{sections/results}    % CORRECT (cross-platform)
\input{sections\results}    % Windows-only, will fail on Unix
```

**Detection**: Flag backslash path separators in LaTeX include commands.

### C.3 Unescaped Special Characters

LaTeX special characters that must be escaped in text mode:

| Character | Escaped form | Context |
|---|---|---|
| `&` | `\&` | Common in institution names, data descriptions |
| `%` | `\%` | Percentages in text |
| `#` | `\#` | Number signs |
| `_` | `\_` | Variable names in text |
| `$` | `\$` | Dollar amounts in text (not math mode) |
| `~` | `\textasciitilde` | URLs, file paths |
| `^` | `\textasciicircum` | Superscripts outside math |
| `{` | `\{` | Literal braces |
| `}` | `\}` | Literal braces |

**Detection**: Flag unescaped special characters in text mode (outside math delimiters and command arguments where they're expected).

**Common case**: Unescaped `%` in prose — "a 50% increase" should be "a 50\% increase" in LaTeX (but "a 50% increase" is correct in Quarto).

**Common case**: Unescaped `&` in author affiliations or data source names.

**Common case**: Unescaped `_` when mentioning variable names inline — "the variable gdp_per_capita" should be "the variable gdp\_per\_capita" or wrapped in `\texttt{gdp\_per\_capita}`.
