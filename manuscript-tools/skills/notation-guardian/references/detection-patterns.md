# Math Detection Patterns

How to find symbol definitions and usages in Quarto (`.qmd`) and LaTeX (`.tex`) files.

---

## A. Math Environment Detection

### Inline math

- `$...$` — standard inline (Quarto and LaTeX)
- `\(...\)` — LaTeX alternative inline

### Display math

- `$$...$$` — standard display (Quarto and LaTeX)
- `\[...\]` — LaTeX alternative display
- `\begin{equation}...\end{equation}` — numbered equation
- `\begin{equation*}...\end{equation*}` — unnumbered equation
- `\begin{align}...\end{align}` — aligned equations
- `\begin{align*}...\end{align*}` — aligned unnumbered
- `\begin{gather}...\end{gather}` — gathered equations
- `\begin{multline}...\end{multline}` — multiline equation

### Extraction regexes

```
\$([^$]+)\$                                                      # inline $...$
\$\$([^$]+)\$\$                                                  # display $$...$$
\\begin\{(equation|align|gather|multline)\*?\}([\s\S]*?)\\end\{\1\*?\}  # environments
\\\(([^)]+)\\\)                                                  # inline \(...\)
\\\[([^\]]+)\\\]                                                 # display \[...\]
```

---

## B. Symbol Definition Patterns

Natural language patterns that indicate a symbol is being **defined** (not just used).

### Explicit definitions

1. `Let $X$ denote...` / `Let $X$ be...` / `Let $X$ represent...`
2. `Define $X$ as...` / `Define $X =...`
3. `where $X$ is...` / `where $X$ denotes...` / `where $X$ represents...`
4. `$X$ is the...` / `$X$ denotes the...`
5. `We write $X$ for...` / `We use $X$ to denote...`
6. `with $X \in ...$` (domain specification)
7. `$X \sim \mathcal{N}(\mu, \sigma^2)$` (distributional definition)
8. `$X = f(Y, Z)$` followed by explanation

### Definition-by-equation

Symbol appears on LHS for the first time:
- `$\theta_i = \theta + \gamma_i$` — defines `\theta_i` in terms of `\theta` and `\gamma_i`
- `$s_j = \theta_j + \epsilon_j$` — defines `s_j`

### Custom command definitions (LaTeX preamble)

- `\newcommand{\cmd}{expansion}`
- `\renewcommand{\cmd}{expansion}`
- `\DeclareMathOperator{\cmd}{text}`
- `\DeclareMathOperator*{\cmd}{text}`
- `\def\cmd{expansion}`

### Quarto-specific

Check the YAML header `include-in-header` block for custom commands — users embed `\newcommand` definitions there.

### Detection regexes for definitions

```
(?:Let|Define|Denote)\s+\$([^$]+)\$\s+(?:denote|be|as|represent)    # "Let $X$ denote"
(?:where|with)\s+\$([^$]+)\$\s+(?:is|denotes|represents|∈|\in)      # "where $X$ is"
\\newcommand\{(\\[a-zA-Z]+)\}(?:\[\d+\])?\{([^}]+)\}               # \newcommand
\\renewcommand\{(\\[a-zA-Z]+)\}(?:\[\d+\])?\{([^}]+)\}             # \renewcommand
\\DeclareMathOperator\*?\{(\\[a-zA-Z]+)\}\{([^}]+)\}               # \DeclareMathOperator
\\def(\\[a-zA-Z]+)\{([^}]+)\}                                       # \def
```

---

## C. Symbol Extraction from Math Content

### Base symbols (Greek letters)

```
\\(alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega)
```

### Decorated symbols

- Subscripts/superscripts: `X_i`, `X_{ij}`, `X^2`, `X^{(k)}`
- Hats/bars/tildes: `\hat{X}`, `\bar{X}`, `\tilde{X}`, `\vec{X}`
- Styled: `\mathbf{X}`, `\mathbb{X}`, `\mathcal{X}`, `\mathrm{X}`

### Compound symbols (track as single units)

- `\sigma_\gamma^2` — variance of gamma (one concept, not three symbols)
- `\mu_\theta` — mean of theta prior
- `s_j^A` — adjusted signal from j

### Extraction strategy

1. First extract custom commands (`\newcommand` etc.)
2. Then extract Greek letters with their decorations/subscripts
3. Then extract Latin letters used as variables (single uppercase/lowercase in math mode, excluding common operators)
4. Group compound symbols: if `\sigma` appears with `_\gamma^2`, treat `\sigma_\gamma^2` as one entry

---

## D. Usage vs. Definition Heuristic

A symbol is being **defined** if:
- It appears after "Let", "Define", "where", "denote", "represent"
- It appears on the LHS of `=` in a display equation with explanatory text following
- It's in a `\newcommand` or `\DeclareMathOperator`
- It's the first occurrence in the document with surrounding context explaining its meaning

A symbol is being **used** (not defined) if:
- It appears in an equation without surrounding definitional text
- It appears in prose as a reference to a previously-defined quantity
- It appears in a `\cite`, figure caption, or table note as context
- It appears in a well-known identity (e.g., `E[X] = \sum x p(x)` is usage of `E`, `X`, `x`, `p`)

**When ambiguous:** Mark as "usage" and check the registry. If the symbol isn't registered yet, flag it as "possibly undefined — check if this is a new definition."
