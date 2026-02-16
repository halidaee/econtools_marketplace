# Style Guide — What Good Output Looks Like

Positive specification of the user's R coding style. Every section has concrete examples. When restyling, the output should match these conventions.

---

## A. Script Headers

**Rule:** 1-3 lines of plain English describing what the script does. No structured metadata, no decorative borders, no attribution.

**Good:**
```r
# Permutation test: shuffle firm labels and re-estimate logit models to
# generate a null distribution for cross-firm agreement.
```

```r
# Load raw data, identify firms, create evaluation/production splits, and save cleaned datasets.
```

**Bad** (39-line template header from `01_prepare_data.R`):
```r
# ============================================================================
# Script: 01_prepare_data.R
# Purpose: Data preparation - load, clean, and prepare data for analysis
#
# This script loads raw CSV files, identifies firms, distinguishes evaluation
# vs production data, processes demographic and psychometric variables, and
# creates cleaned datasets ready for analysis.
#
# Inputs:
#   - Data: analysis/data/raw/test_id=*.csv (raw psychometric assessments)
#   - Metadata: analysis/data/raw/tests_metadata_updated.json
# ...
# Scalability: This script automatically handles N firms
# Parallel: No parallel processing needed
# Dependencies:
#   - Required: tidyverse, lubridate, jsonlite, here
# Author: Refactored for Gentzkow-Shapiro compliance
# Last Modified: 2026-01-11
# ============================================================================
```

---

## B. Variable Naming

**Rule:** snake_case for everything. Straightforward, readable names — concise but not cryptic. No SDE conventions.

| Bad (LLM style) | Good (user style) |
|---|---|
| `PATH_OUTPUT_MODELS` | `output_dir` |
| `RANDOM_SEED` | `seed` |
| `COMPOSITE_SCORES` | `composite_scores` |
| `RETENTION_THRESHOLD_DAYS` | `retention_threshold` |
| `data_combined` | `combined` |
| `data_cleaned` | `cleaned` |
| `data_evaluation` | `eval_data` |
| `risk_category_pooled` | `risk_cat` |
| `number_of_observations` | `n_obs` |
| `FIRM_PATTERNS` | `firm_patterns` |
| `OUT_DIR` | `out_dir` |

**Math notation** (N, K, M) is fine in actual linear algebra / matrix contexts:
```r
# Good — matrix/simulation context
N <- 200
K <- as.integer(round(N^0.4))
```

**Never use:** `data_` prefix on data frames, SCREAMING_SNAKE_CASE for configuration, "slug" terminology.

---

## C. Comments

**Rule:** Full sentences explaining WHY or providing context. Plenty of comments — more than LLM output, but about substance, not play-by-play. Add comments where non-obvious logic has none.

**Good — explains reasoning:**
```r
# Firm A has 3x more evaluation data than Firm B, so we downsample to match
# sizes before comparing prediction agreement.
```

**Good — adds missing context to uncommented code:**
```r
# Drop respondents under 18 — the psychometric instrument is only validated for adults.
filter(age >= 18)
```

**Good — brief section separator in a long script:**
```r
# ---- fit models ----
```

**Bad — narrates the obvious:**
```r
# Load the evaluation data
eval_data <- readRDS("data_evaluation.rds")
```

**Bad — meta-commentary:**
```r
# ABSTRACTION NOTE: Extracted for clarity and reuse
# inline - simple operation used only once
```

**Bad — "End of" markers:**
```r
# End of data preparation section
# ============================================================================
```

---

## D. R Idioms (Always Enforce)

### D1. Assignment: `<-` exclusively
```r
# Good
output_dir <- "results/"
seed <- 12345

# Bad
output_dir = "results/"
```

### D2. Explicit `return()` in every function
```r
# Good
fit_logit <- function(df) {
  fmla <- as.formula(paste("tenure_leq_90 ~", paste(predictors, collapse = " + ")))
  model <- glm(fmla, data = df, family = binomial())
  return(model)
}

# Bad — implicit return
fit_logit <- function(df) {
  fmla <- as.formula(paste("tenure_leq_90 ~", paste(predictors, collapse = " + ")))
  glm(fmla, data = df, family = binomial())
}
```

### D3. Tidyverse for data manipulation; prefer `purrr::map()` when tidyverse is loaded
```r
# Good — purrr is loaded
replications <- map_dfr(seq_len(R), function(r) {
  permuted <- eval_data %>% mutate(firm_perm = sample(firm, n(), replace = FALSE))
  tibble(rep = r, spearman_rho = spearman_corr(p_a, p_b))
})
```

### D4. `library()` calls at top of script
```r
# Good
library(tidyverse)
library(here)

# Bad — scattered or wrapped
source("utils/load_packages.R")
load_required_packages()
```

---

## E. R Idioms (Leave Alone)

These are explicitly NOT to be changed — leave whichever form the code already uses:

- **Quote style**: single vs double quotes — leave as-is
- **Pipe style**: `%>%` vs `|>` — leave as-is
- **`ifelse()` vs `if_else()`** — leave as-is
- **`across()` vs `mutate_at()`** — leave as-is
- **`lapply()` vs `purrr::map()`** — leave whichever is already used

---

## F. Script Structure

Short, focused scripts with a single responsibility. No unnecessary abstractions, no unit tests for analysis scripts, no `invisible(list(...))` return objects.

**Model script template:**
```r
# Brief description of what this script does (1-3 lines).

library(tidyverse)
library(here)

setwd(here())
source("shared/config.R")

# ---- config ----

out_dir <- file.path("output")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
seed <- 12345
set.seed(seed)

# ---- load data ----

eval_data <- readRDS(file.path(input_dir, "data_evaluation.rds")) %>%
  filter(!is.na(tenure_leq_90)) %>%
  drop_na(all_of(composite_scores))

# ---- analysis ----

# ... the actual work ...

# ---- save ----

write_csv(results, file.path(out_dir, "results.csv"))
message("Analysis complete. Outputs written to: ", out_dir)
```

**Key points:**
- Libraries at top
- Config/paths next
- Load data
- Analysis
- Save results
- One `message()` at the end if useful
- No `invisible(list(...))`, no "Pipeline Complete!" celebration

---

## G. Error Handling

No `tryCatch` around normal operations. No defensive boilerplate. No ASCII-art error messages.

**Good — brief, useful stop:**
```r
if (length(firm_levels) < 2) {
  stop("Need at least two firms to run permutation null.")
}
```

**Bad — boxed error message from `data_utils.R`:**
```r
stop(
  "\n========================================\n",
  "ERROR: Cannot Identify Firms\n",
  "========================================\n\n",
  "Your data is missing the 'company_name' column.\n\n",
  "The firm identification process requires this column to match\n",
  "company names against patterns defined in config.R\n\n",
  "Check your input data file and ensure it has a 'company_name' column.\n"
)
```

**Bad — tryCatch around source():**
```r
tryCatch({
  source(script_path, local = TRUE, echo = FALSE)
  cat("✓", script_name, "completed successfully\n")
}, error = function(e) {
  cat("✗ ERROR in", script_name, "\n")
  # ... 20 lines of error formatting ...
})
```

---

## H. Console Output

Minimal output. `message()` for genuinely useful info. No emoji, no boxes, no narration.

**Good:**
```r
message("Permutation null complete.")
message("Outputs written to: ", out_dir)
```

**Bad — emoji/boxes/narration from `01_prepare_data.R`:**
```r
cat("\n========================================\n")
cat("Step 1: Loading raw data files\n")
cat("========================================\n\n")
cat("✓ Combined data:", nrow(combined), "rows,", ncol(combined), "columns\n")
cat("✓ Next step: Run 02_table1_dataset_sizes.R\n\n")
```

---

## I. Script Scope — When to Split or Join

**Think in outputs, not lines.** A script's scope = how many independent outputs it produces (tables, figures, datasets).

**Split when:** A script produces 3+ independent outputs (e.g., data cleaning + table generation + figure creation all in one file). Each output-producing block should be its own script.

**Join when:** Two scripts share >50% of their logic (copy-paste with minor variations), OR a "utility" file is sourced by only one caller and adds no clarity.

**How to evaluate:** Read the full script, identify distinct "output-producing blocks" (each block produces one table, figure, or dataset). If there are 3+ independent blocks, suggest splitting.

**Flag scope changes for user** — never auto-split or auto-join. Present the proposed split/join, explain why, and let the user decide.

**Good scope:** `01_prepare_data.R` → one script (produces one output: cleaned dataset).

**Flag for splitting:** `02_table1_and_figure1_and_demographics.R` → three independent outputs in one file.

---

## J. Archive Management

Archives go in a `.drafts/` subfolder — never leave archived files alongside working scripts.

```bash
mkdir -p .drafts && cp script.R .drafts/script_llm_draft.R
```

The `_llm_draft` suffix clearly communicates what the backup is. Ask the user once whether to add `.drafts/` to `.gitignore`.

---

## K. Git Workflow

Commit after each stage with succinct messages:

- **After archiving:** `"Archive LLM draft of <filename> before restyling"`
- **After rewriting:** `"Restyle <filename>: <2-3 sentence summary of changes>"`
- **After verification:** `"Verified <filename>: outputs match LLM draft"`
- **If reverting:** `"Revert <filename>: outputs diverged after restyling, restoring LLM draft"`
