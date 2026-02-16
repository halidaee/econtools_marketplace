# LLM Smell Catalog

Each smell category has: description, detection patterns, and BEFORE/AFTER examples. BEFORE examples are drawn from real LLM-generated code in the user's projects. AFTER examples show the user's preferred style.

---

## S1. Verbose Status Printing

LLMs narrate every step with emoji checkmarks, ASCII-art boxes, step numbering, and celebration messages. This is useful during development but must be stripped from finished code.

**Detection patterns:**
- `cat("✓ ...")` / `cat("✗ ...")`
- `cat(rep("=", N), ...)` boxed headers
- `cat("Step N: ...")`
- `cat("Next step: ...")`
- `cat("Pipeline Complete!")`
- Verbose `cat()` printing stats after every operation

**BEFORE** (from `01_prepare_data.R`):
```r
cat("\n========================================\n")
cat("Step 1: Loading raw data files\n")
cat("========================================\n\n")

cat("Found", length(csv_files), "CSV files:\n")
walk(csv_files, ~cat("  -", basename(.x), "\n"))

# ... 20 lines later ...

cat("\n✓ Combined data:", nrow(data_combined), "rows,", ncol(data_combined), "columns\n")
cat("✓ Extracted test_id from filenames\n")
cat("✓ Removed 'Unnamed: 0' column\n")

# ... at end of script ...

cat("✓ All datasets ready for analysis!\n")
cat("✓ Next step: Run 02_table1_dataset_sizes.R\n\n")
```

**AFTER:**
```r
# Remove ALL cat() status printing. Keep only a single message() at the
# end if it communicates genuinely useful info:

message("Data preparation complete. Outputs written to: ", input_dir)
```

---

## S2. Template Headers

LLMs produce structured headers with Purpose, Inputs, Outputs, Scalability, Parallel, Dependencies, Author, Last Modified — often 20-40 lines of metadata before any code.

**Detection:** Header blocks exceeding ~5 lines with multiple of: Purpose, Inputs, Outputs, Scalability, Parallel, Dependencies, Author, Last Modified.

**BEFORE** (from `01_prepare_data.R`, 39 lines):
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
#   - Config: utils/config.R (firm patterns, thresholds, constants)
#
# Outputs:
#   - Tables: None (this is a data preparation script)
#   - Data: analysis/input/data_cleaned.rds/.csv
#           analysis/input/data_evaluation.rds/.csv
#           analysis/input/data_production.rds/.csv
#           analysis/input/question_section_mapping.rds
#
# Key Analytical Decisions:
#   - Firm identification: Uses regex patterns from config (scalable to N firms)
#   - Retention threshold: 90 days (RETENTION_THRESHOLD_DAYS in config)
#   - Evaluation vs Production split: Presence/absence of retention_days labels
#   - Complete cases: Require all 7 composite scores for inclusion
#   - CDMX aggregation: Standardizes all Mexico City boroughs to "Mexico City"
#
# Scalability: This script automatically handles N firms (current: 2, future: 5+)
#              Firm patterns defined in utils/config.R:FIRM_PATTERNS
#
# Parallel: No parallel processing needed (data loading is I/O bound)
#
# Dependencies:
#   - Required: tidyverse, lubridate, jsonlite, here
#   - Utils: config.R, data_utils.R
#
# Author: Refactored for Gentzkow-Shapiro compliance
# Last Modified: 2026-01-11
# ============================================================================
```

**AFTER:**
```r
# Load raw data, identify firms, create evaluation/production splits, and save cleaned datasets.
```

---

## S3. Over-Documentation

LLMs add Roxygen documentation to non-package functions, write "ABSTRACTION NOTE" justifications for design choices, and narrate what the next line of code does.

**Detection patterns:**
- `#' @param` / `#' @return` / `#' @examples` on non-exported analysis functions
- `# ABSTRACTION NOTE:` comments
- Play-by-play comments: `# Load the data` directly above a `readRDS()` call

**BEFORE** (from `load_packages.R`):
```r
#' Load Required Packages
#'
#' Loads all required packages for the analysis pipeline
#' Checks for missing packages and provides helpful installation instructions
#'
#' @param packages Character vector of package names (default: REQUIRED_PACKAGES)
#' @param auto_install Logical, automatically install missing packages (default: FALSE)
#' @param verbose Logical, print loading messages (default: TRUE)
#' @param include_optional Logical, also check optional packages (default: FALSE)
#'
#' @return Invisible TRUE if successful
#'
#' @examples
#' load_required_packages()  # Check and load
#' load_required_packages(auto_install = TRUE)  # Install if missing
#' load_required_packages(verbose = FALSE)  # Silent loading
```

**BEFORE** (from `data_utils.R`):
```r
# ============================================================================
# ABSTRACTION NOTE: This function is kept as a separate function (even though
# only used once) because:
# 1. Complex logic (50+ lines) with many edge cases (NA, display names, etc.)
# 2. Core to scalability - enables 2 to 5+ firms with NO code changes
# 3. Hard to get right - tested extensively in test_scalability.R
# 4. Central to entire analysis - firm identification is a critical decision
#
# When to inline: If firm logic becomes simpler (e.g., just 2 firms forever,
# no display names, no edge cases) this could be inlined into 01_prepare_data.R
# ============================================================================
```

**AFTER:**
```r
# Brief comment if the function name isn't self-explanatory, or nothing at all:

# Assign firm labels by matching company_name against regex patterns from config.
identify_firms <- function(data, firm_patterns) {
  # ...
}
```

---

## S4. Over-Engineering

LLMs build infrastructure that analysis code doesn't need: package management utilities, `run_script()` wrappers with timing and error logging, `invisible(list(...))` return objects, elaborate config systems.

**Note:** Intentional generalization (e.g., building for N firms) is NOT a smell if the user requested it — ask before removing.

**Detection patterns:**
- `run_script()` wrapper functions around `source()`
- `invisible(list(...))` at script end
- 400-line package management utilities
- Config systems with unused options

**BEFORE** (from `00_run_all.R` — `run_script()` wrapper):
```r
run_script <- function(script_path, script_name) {
  cat("\n", rep("=", 60), "\n", sep = "")
  cat("Running:", script_name, "\n")
  cat(rep("=", 60), "\n", sep = "")

  script_start <- Sys.time()

  tryCatch({
    source(script_path, local = TRUE, echo = FALSE)
    script_end <- Sys.time()
    script_duration <- difftime(script_end, script_start, units = "secs")
    cat("\n", rep("-", 60), "\n", sep = "")
    cat("✓", script_name, "completed successfully\n")
    cat("  Runtime:", round(script_duration, 2), "seconds\n")
    # ... 30 more lines of error handling and formatting ...
  })
}

# Usage:
results <- map(pipeline_scripts, function(s) {
  run_script(s$path, s$name)
})
```

**BEFORE** (from `00_run_all.R` — invisible return):
```r
invisible(list(
  success = n_failed == 0,
  n_total = n_total,
  n_success = n_success,
  n_failed = n_failed,
  duration = elapsed,
  results = results
))
```

**AFTER:**
```r
# Direct source() calls. Script just ends — no invisible return.
source("analysis/code/01_prepare_data.R")
source("analysis/code/02_table1_dataset_sizes.R")
source("analysis/code/03_table2_psychometric_responses.R")
source("analysis/code/04_table3_retention.R")
source("analysis/code/05_table4_demographics.R")

message("Pipeline complete.")
```

---

## S5. Defensive Coding

LLMs wrap everything in `tryCatch`, add input validation boilerplate, and format error messages as ASCII art. Normal R code should just run — and fail clearly when something is actually wrong.

**Detection patterns:**
- `tryCatch` around `source()`, `lm()`, `glm()`, normal operations
- Formatted ASCII-art `stop()` messages
- Input validation boilerplate (`if (!is.data.frame(data)) stop(...)`)

**BEFORE** (from `00_run_all.R` — tryCatch around source):
```r
tryCatch({
  source(script_path, local = TRUE, echo = FALSE)
  cat("✓", script_name, "completed successfully\n")
}, error = function(e) {
  cat("✗ ERROR in", script_name, "\n")
  cat("  Message:", conditionMessage(e), "\n")
  error_msg <- paste0(Sys.time(), ": Error in ", script_name, "\n", ...)
  cat(error_msg, file = "analysis/temp/error_log.txt", append = TRUE)
})
```

**BEFORE** (from `data_utils.R` — boxed stop):
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

**AFTER:**
```r
# Direct source() — no tryCatch wrapper:
source("analysis/code/01_prepare_data.R")

# Brief stop() when genuinely needed:
if (!"company_name" %in% names(data)) {
  stop("Data is missing required 'company_name' column.")
}
```

**Note:** Flag `tryCatch` around genuinely risky operations (file I/O, network calls) for user review — those might be intentional.

---

## S6. SDE Naming Conventions

LLMs default to software-engineering naming: SCREAMING_SNAKE_CASE for constants, `data_` prefixes on data frames, "slug" terminology.

**Detection patterns:**
- `SCREAMING_SNAKE_CASE` variables (`PATH_OUTPUT`, `RANDOM_SEED`, `COMPOSITE_SCORES`)
- `data_` prefix on data frames (`data_combined`, `data_cleaned`)
- "slug" terminology

**Renaming table:**

| LLM name | User style |
|---|---|
| `PATH_OUTPUT` | `output_dir` |
| `PATH_INPUT` | `input_dir` |
| `PATH_RAW_DATA` | `raw_dir` |
| `RANDOM_SEED` | `seed` |
| `COMPOSITE_SCORES` | `composite_scores` |
| `RETENTION_THRESHOLD_DAYS` | `retention_threshold` |
| `FIRM_PATTERNS` | `firm_patterns` |
| `FIRM_DISPLAY_NAMES` | `firm_names` |
| `data_combined` | `combined` |
| `data_cleaned` | `cleaned` |
| `data_evaluation` | `eval_data` |
| `data_production` | `prod_data` |
| `OUT_DIR` | `out_dir` |

**Caveat:** If a SCREAMING_SNAKE_CASE variable is defined in a shared config file and used across multiple scripts, renaming requires updating all callers. Flag for user review rather than auto-renaming across files.

---

## S7. Boilerplate Markers

LLMs add decorative section dividers, "End of Script" markers, and attribution lines that serve no informational purpose.

**Detection patterns:**
- `# End of Script` / `# End of X`
- `# ============================================================================` as pure decoration (60+ char divider lines)
- `# Author: Refactored for X compliance`
- `# Last Modified: YYYY-MM-DD`

**BEFORE** (from `01_prepare_data.R`):
```r
# ============================================================================
# End of Data Preparation Script
# ============================================================================
```

```r
# Author: Refactored for Gentzkow-Shapiro compliance
# Last Modified: 2026-01-11
```

```r
# ============================================================================
# 1. Load Raw Data
# ============================================================================
```

**AFTER:**
```r
# Remove all. Brief section separators are acceptable for major sections
# in longer scripts:

# ---- load data ----
```

---

## S8. Test Infrastructure

LLMs sometimes generate `tests/` directories with `test_that()` and `expect_equal()` for analysis scripts — appropriate for R packages, not for analysis code.

**Detection:** `tests/` directory adjacent to analysis code with `test_that()`, `expect_equal()`.

**Action:** Flag for user — note that the user's style does not include unit tests for analysis scripts, but do NOT auto-delete. The user may want to keep them during development and remove later.

---

## S9. Unnecessary Abstraction

LLMs extract every block into a named function, even when used once, and justify it with "ABSTRACTION NOTE" comments. They also create utility files with single callers and massive package management infrastructure.

**CRITICAL:** Before classifying any function as single-use, `grep -r "function_name"` across the entire project. Only flag for inlining if truly called once.

**Detection patterns:**
- Helper functions with "ABSTRACTION NOTE" justification comments
- Utility files with a single caller (confirmed by project-wide grep)
- Package management utilities that replace `library()`

**BEFORE** (from `load_packages.R` — 408 lines to do what `library()` does):
```r
CORE_PACKAGES <- c("tidyverse", "here", "lubridate")
DATA_PACKAGES <- c("jsonlite", "readr")
MODELING_PACKAGES <- c("tidymodels", "ranger", "kernlab", "xgboost", "nnet", "vip")
PARALLEL_PACKAGES <- c("future", "doFuture", "progressr")
OUTPUT_PACKAGES <- c("tinytable", "ggplot2", "pROC")

REQUIRED_PACKAGES <- unique(c(CORE_PACKAGES, DATA_PACKAGES, ...))

load_required_packages <- function(packages = REQUIRED_PACKAGES,
                                   auto_install = FALSE,
                                   verbose = TRUE,
                                   include_optional = FALSE) {
  # ... 60 lines of package checking, installing, loading ...
}

load_core_packages <- function(verbose = TRUE) { ... }
load_modeling_packages <- function(verbose = TRUE) { ... }
load_all_packages <- function(verbose = TRUE) { ... }
check_package_versions <- function(packages = REQUIRED_PACKAGES) { ... }
check_minimum_versions <- function(min_versions = list()) { ... }
check_r_version <- function(min_version = "4.0.0") { ... }
check_system_compatibility <- function() { ... }
save_session_info <- function(output_file = "...") { ... }
list_required_packages <- function() { ... }
install_all_packages <- function() { ... }
```

**AFTER:**
```r
# At the top of each script that needs these packages:
library(tidyverse)
library(here)
library(lubridate)
```

**Action for justification comments:** Auto-remove "ABSTRACTION NOTE" and similar meta-commentary. Flag function/file removal only after confirming single-use via project-wide grep.

---

## S10. Miscellaneous

### Dual-format figure saving
LLMs often save figures in both PDF and PNG "just in case." Flag and ask the user which format they prefer.

```r
# LLM pattern — flag for user:
ggsave("figure1.pdf", plot = p, width = 8, height = 6)
ggsave("figure1.png", plot = p, width = 8, height = 6, dpi = 300)
```

### Assignment style
```r
# Bad
output_dir = "results/"

# Good
output_dir <- "results/"
```

### Missing explicit `return()`
```r
# Bad — implicit return
spearman_corr <- function(x, y) {
  suppressWarnings(cor(x, y, method = "spearman", use = "complete.obs"))
}

# Good — explicit return
spearman_corr <- function(x, y) {
  return(suppressWarnings(cor(x, y, method = "spearman", use = "complete.obs")))
}
```
