# Standard Economics Notation Conventions

Standard symbols by subfield, plus common conflicts and resolution strategies.

---

## A. Universal Conventions (across all subfields)

| Concept | Standard Symbol(s) | Notes |
|---|---|---|
| Outcome / dependent variable | `Y`, `y` | Uppercase for random variable, lowercase for realization |
| Error / disturbance term | `\epsilon`, `\varepsilon`, `u` | `\epsilon` most common in micro; `u` in some macro/econometrics |
| Coefficients | `\beta`, `\alpha`, `\gamma` | `\beta` for slope, `\alpha` for intercept |
| Sample size | `N`, `n`, `T` | `N` for cross-section, `T` for time periods, `n` for subsamples |
| Expectation operator | `\mathbb{E}`, `E`, `\mathrm{E}` | `\mathbb{E}` is most modern; `E` acceptable |
| Probability | `\mathbb{P}`, `\Pr`, `P` | `\mathbb{P}` or `\Pr` preferred |
| Variance | `\mathrm{Var}`, `\sigma^2` | Operator vs. symbol |
| Covariance | `\mathrm{Cov}` | Always roman/upright |
| Normal distribution | `\mathcal{N}(\mu, \sigma^2)` | Script N |
| Real numbers | `\mathbb{R}` | Blackboard bold |
| Indicator function | `\mathbf{1}`, `\mathbb{1}`, `\bm{1}` | Varies; be consistent within paper |
| Convergence in probability | `\xrightarrow{p}`, `\overset{p}{\to}` | |
| Convergence in distribution | `\xrightarrow{d}`, `\overset{d}{\to}` | |
| Sets / collections | `\mathcal{X}` | Calligraphic for sets |
| Matrices | `\mathbf{X}` or `\bm{X}` | Bold uppercase |
| Vectors | `\mathbf{x}` or `\bm{x}` | Bold lowercase |

---

## B. Econometrics / Causal Inference

| Concept | Standard Symbol(s) | Notes |
|---|---|---|
| Treatment indicator | `D`, `T`, `W`, `Z` | `D` most common (Angrist & Pischke); `Z` often reserved for instruments |
| Potential outcomes | `Y(1)`, `Y(0)` or `Y_1`, `Y_0` | Rubin causal model |
| Average treatment effect | `\tau`, `\text{ATE}` | `\tau` for the parameter, ATE for the concept |
| Instrument | `Z` | Almost always Z |
| First stage coefficient | `\pi` | Common in IV literature |
| Reduced form coefficient | `\rho` or `\gamma` | Varies |
| Fixed effects | `\alpha_i`, `\mu_i`, `\delta_t` | Individual FE, time FE |
| Clustered SE | `\hat{\sigma}_c` | c for cluster |
| Regression specification | `Y_{it} = \alpha + \beta X_{it} + \gamma W_{it} + \epsilon_{it}` | Standard panel form |

---

## C. Microeconomics / Theory

| Concept | Standard Symbol(s) | Notes |
|---|---|---|
| Utility function | `U`, `u`, `V`, `v` | `U` for direct utility, `V` for indirect |
| Budget / income | `I`, `M`, `w` | `w` for wealth/wage |
| Prices | `p`, `P` | Lowercase for individual, uppercase for vector |
| Quantities | `q`, `Q`, `x` | |
| Profit | `\pi` | (conflict risk with the constant; context-dependent) |
| Welfare | `W` | |
| Lagrange multiplier | `\lambda` | Shadow price of constraint |
| Discount factor | `\delta`, `\beta` | `\beta` in macro; `\delta` in micro |
| Preference relation | `\succeq`, `\succ`, `\sim` | Weak, strict, indifference |
| Choice set / action set | `A`, `\mathcal{A}` | |
| Type / parameter space | `\Theta`, `\mathcal{T}` | |
| Belief / posterior | `\mu`, `\pi` | Context-dependent |
| Signal | `s`, `\sigma` (as a signal, not std dev) | `s` safest; `\sigma` conflicts with std dev |
| Information set | `\mathcal{I}`, `\mathcal{F}` | `\mathcal{F}` for filtrations |

---

## D. Development / Labor Economics

| Concept | Standard Symbol(s) | Notes |
|---|---|---|
| Treatment / program | `D`, `T` | |
| Adoption decision | `a`, `A` | |
| Village / cluster | `v`, `c` | Subscript |
| Household | `h` | Subscript |
| Time period | `t` | Subscript |
| Wages | `w`, `W` | |
| Human capital | `H`, `h` | |
| Returns to education | `\rho` | Mincer equation |
| Technology parameter | `\theta`, `A` | `A` for TFP; `\theta` for individual-level |

---

## E. Industrial Organization

| Concept | Standard Symbol(s) | Notes |
|---|---|---|
| Firm index | `i`, `j`, `f` | |
| Price | `p`, `P` | |
| Quantity | `q`, `Q` | |
| Marginal cost | `c`, `MC` | |
| Number of firms | `N`, `n` | |
| Market share | `s` | |
| Profit | `\pi` | |
| Demand | `D(p)`, `Q(p)` | |
| Lerner index | `L` | `L = (P - MC) / P` |

---

## F. Common Conflicts to Watch For

| Symbol | Meaning 1 | Meaning 2 | Resolution |
|---|---|---|---|
| `\pi` | Profit | Mathematical constant 3.14... | Context usually resolves; use `\pi_f` for firm profit if needed |
| `\beta` | Regression coefficient | Discount factor | Use `\delta` for discount if `\beta` is coefficients |
| `\sigma` | Standard deviation | Signal/strategy | Use `s` for signals if `\sigma` is std dev |
| `\gamma` | Coefficient vector | Euler-Mascheroni constant | Rare conflict; context resolves |
| `u` | Utility function | Error term | Use `\epsilon` for errors if `u` is utility |
| `\delta` | Discount factor | Fixed effect (time) | Use `\delta_t` for FE, bare `\delta` for discount |
| `W` | Welfare | Wage | Use `w` (lowercase) for wage, `W` for welfare |
| `N` | Sample size | Natural numbers | Use `n` for sample size if `\mathbb{N}` appears |
| `s` | Signal | Market share | Use `\tilde{s}` or context-specific subscript for one |
| `\alpha` | Intercept | Fixed effect | Use `\alpha_i` for FE, `\alpha_0` or `\beta_0` for intercept |
| `\lambda` | Lagrange multiplier | Eigenvalue | Use `\mu` for eigenvalue if `\lambda` is Lagrangian |
| `\mu` | Mean | Belief/posterior | Use `\bar{x}` for sample mean if `\mu` is belief |
| `D` | Treatment indicator | Demand function | Use `D_i` for treatment, `D(p)` for demand |
| `T` | Time periods (total) | Treatment | Use `T` for time, `D` for treatment |

### Resolution principle

When a conflict is detected, prefer the meaning that was **established first** in the paper. Suggest renaming the later usage. If neither is established yet, prefer the more conventional symbol per the tables above.
