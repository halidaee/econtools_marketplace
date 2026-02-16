# Verification Workflow

Archive-verify-revert workflow for style transformations. Adapted from `r-parallel/references/seed-handling.md` §I.

---

## A. Why Verification Matters

Style transformations should NEVER change outputs. But mistakes happen: a renamed variable missed in one reference, inlining a function changes scope, removing a `tryCatch` exposes an error that was silently caught. Verification catches these before the user sees broken code.

---

## B. Archive

Before any changes, create a backup in the `.drafts/` subfolder:

```bash
mkdir -p .drafts && cp script.R .drafts/script_llm_draft.R
```

- The `_llm_draft` suffix clearly communicates what the backup is
- `.drafts/` keeps archived files out of the working directory
- Git commit the archive immediately:

```
"Archive LLM draft of script.R before restyling"
```

---

## C. Identify Key Outputs

Scan the script for file writes and key result objects:

- **File writes:** `saveRDS()`, `write_csv()`, `write.csv()`, `ggsave()`, `writeLines()`, `sink()`
- **Last assigned objects** before script end
- **If script is `source()`d from a master:** check what the master expects from this script

Side effects (plots displayed, messages printed) are NOT verified — only data outputs matter.

---

## D. Capture Baseline

Source the archived original in a clean environment and capture all outputs:

```r
# Run original (archived) version
baseline_env <- new.env(parent = globalenv())
source(".drafts/script_llm_draft.R", local = baseline_env)

# Capture file outputs
baseline_files <- list(
  result1 = readRDS("output/result1.rds"),
  result2 = read_csv("output/result2.csv", show_col_types = FALSE)
)

# Capture key objects from the environment
baseline_objects <- list(
  model = baseline_env$model,
  predictions = baseline_env$predictions
)
```

Adapt variable names and file paths to match the specific script being verified.

---

## E. Run Rewritten Version

Same template as D but sourcing the rewritten script. Clean up output files from the baseline run first to ensure the rewritten version produces its own outputs:

```r
# Clean up baseline outputs
file.remove("output/result1.rds")
file.remove("output/result2.csv")

# Run rewritten version
rewrite_env <- new.env(parent = globalenv())
source("script.R", local = rewrite_env)

# Capture file outputs
rewrite_files <- list(
  result1 = readRDS("output/result1.rds"),
  result2 = read_csv("output/result2.csv", show_col_types = FALSE)
)

# Capture key objects
rewrite_objects <- list(
  model = rewrite_env$model,
  predictions = rewrite_env$predictions
)
```

---

## F. Compare

```r
# For numeric results (tolerant of floating-point differences):
all.equal(baseline_files$result1, rewrite_files$result1)
# Should return TRUE

# For character/factor/non-numeric results:
identical(baseline_files$result2, rewrite_files$result2)
# Should return TRUE
```

**What to compare:**
- Every file the original writes (RDS, CSV, TeX, PDF)
- Key result objects in the script's environment

**What NOT to compare:**
- Console output (messages, cat, print) — these are expected to change
- Timing information
- Comments in output files
- Object names (may be renamed by the restyling)

---

## G. If Mismatch — Revert

1. Copy archive back:
```bash
cp .drafts/script_llm_draft.R script.R
```

2. Git commit:
```
"Revert script.R: outputs diverged after restyling, restoring LLM draft"
```

3. Report to user:
   - Which outputs differed
   - Nature of difference (e.g., "result2.csv has 3 fewer rows", "model coefficients differ by >1e-6")
   - Which transformation likely caused it (e.g., "renaming `data_combined` to `combined` — may have missed a reference on line 142")

4. Do NOT retry — hand off to user.

---

## H. If Match — Done

1. Report success
2. List all transformations applied (e.g., "removed 39-line template header, stripped 47 cat() calls, renamed 8 SCREAMING_SNAKE_CASE variables")
3. List any flagged items (ambiguous transforms skipped pending user review)
4. Keep `_llm_draft.R` archive in `.drafts/` — do not delete

---

## I. Scripts That Cannot Be Verified

Some scripts can't be practically verified:
- **Long runtime** (>5 minutes)
- **External dependencies** (API calls, database queries, network access)
- **Interactive input** (user prompts, GUI elements)
- **Non-deterministic** without seed control

For these scripts:
- Apply only **trivially safe transformations**: comment cleanup, header condensing, marker removal, assignment style, adding `return()`
- Flag all **substantive transforms** for user review: variable renaming, function inlining, tryCatch removal
- Report what was and wasn't changed, and why

---

## J. Multi-Script Pipelines

When restyling multiple scripts that form a pipeline (e.g., `00_run_all.R` sources `01_prepare_data.R` through `05_table4_demographics.R`):

1. **Archive ALL scripts first** — copy every script to `.drafts/` before touching any of them
2. **Restyle one at a time, bottom-up** — start with leaf scripts (those that don't source others), then work up to the master script
3. **Verify each independently** before moving to the next
4. **If shared config is restyled** (e.g., renaming `COMPOSITE_SCORES` to `composite_scores` in `config.R`), update all callers simultaneously and verify the full pipeline end-to-end
5. **Git commit after each script** is verified, not in bulk at the end

**Bottom-up order example:**
```
05_table4_demographics.R     # leaf — no downstream dependencies
04_table3_retention.R        # leaf
03_table2_psychometric.R     # leaf
02_table1_dataset_sizes.R    # leaf
01_prepare_data.R            # produces data used by 02-05
utils/config.R               # sourced by everything — restyle last, update all callers
00_run_all.R                 # master — restyle after all children verified
```
