# Seed Handling Reference

Rules for reproducible parallel RNG in the `future` ecosystem.

## A. Why Parallel RNG Is Different

Base R's `set.seed()` initializes a single Mersenne-Twister stream. In parallel execution, each worker process starts with a copy of the parent's RNG state — meaning **all workers generate identical random numbers** if you rely on `set.seed()` alone.

L'Ecuyer-CMRG (`"L'Ecuyer-CMRG"`) solves this by generating **independent substreams** from a single seed via `parallel::nextRNGStream()`. Each worker gets its own substream — no overlap, no correlation, results identical regardless of how tasks are distributed across workers.

The `future` ecosystem handles this automatically when you pass the correct seed argument.

## B. The Golden Rule

```r
# 1. Set ONE seed BEFORE the parallel call
set.seed(12345)

# 2. Pass the seed argument to the future_* function
results <- future_lapply(x, fun, future.seed = TRUE)

# 3. NEVER call set.seed() inside the worker body
# BAD: future_lapply(x, function(xi) { set.seed(42); rnorm(1) })
```

One seed, one argument, zero `set.seed()` inside workers.

## C. Seed Arguments by Package

| Package | Seed argument | Example |
|---|---|---|
| future.apply | `future.seed = TRUE` | `future_lapply(x, fun, future.seed = TRUE)` |
| furrr | `.options = furrr_options(seed = TRUE)` | `future_map(x, fun, .options = furrr_options(seed = TRUE))` |
| doFuture | `.options.future = list(seed = TRUE)` | `foreach(i=1:n, .options.future = list(seed = TRUE)) %dofuture% {}` |
| future (low-level) | `seed = TRUE` | `f <- future(expr, seed = TRUE)` |

## D. What `future.seed = TRUE` Does Internally

1. Switches the RNG kind to L'Ecuyer-CMRG
2. Uses the current `.Random.seed` (set by your `set.seed()` call) as the base
3. Generates one independent seed per element via `parallel::nextRNGStream()`
4. Assigns each element's seed to its worker before execution
5. Results are **reproducible regardless of worker count or scheduling order**

This means running with 2 workers or 8 workers produces identical results — the seed is per-element, not per-worker.

## E. Fixed Integer Seeds vs TRUE

**`future.seed = TRUE`**: Uses the current `.Random.seed` state. Pair with `set.seed(N)` beforehand for reproducibility.

```r
set.seed(42)
result <- future_lapply(1:100, function(i) rnorm(1), future.seed = TRUE)
```

**`future.seed = 12345`**: Explicitly sets the parallel seed to 12345, ignoring the current `.Random.seed` state.

```r
# No set.seed() needed — the seed is embedded in the call
result <- future_lapply(1:100, function(i) rnorm(1), future.seed = 12345)
```

Both are reproducible. Use `TRUE` (with `set.seed()` beforehand) for multi-step workflows where you want a single seed to govern the entire script. Use an integer for isolated, self-contained parallel calls.

## F. Verifying Reproducibility

Test that results are identical across different worker counts:

```r
library(future)
library(future.apply)

# Run 1: 2 workers
set.seed(42)
plan(multisession, workers = 2)
result_a <- future_lapply(1:100, function(i) rnorm(1), future.seed = TRUE)
plan(sequential)

# Run 2: 4 workers
set.seed(42)
plan(multisession, workers = 4)
result_b <- future_lapply(1:100, function(i) rnorm(1), future.seed = TRUE)
plan(sequential)

identical(result_a, result_b)  # Must be TRUE
```

If this returns `FALSE`, something is wrong with seed handling — do not proceed.

## G. Common Seed Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| `set.seed()` inside worker | All workers get same stream; results depend on scheduling | Remove; use `future.seed = TRUE` |
| No seed argument at all | Non-reproducible results across runs | Add `future.seed = TRUE` |
| `future.seed = FALSE` | Explicitly disables parallel-safe RNG | Change to `TRUE` |
| `RNGkind("Mersenne-Twister")` before parallel call | Mersenne-Twister is not parallel-safe | Let `future.seed = TRUE` handle RNG kind automatically |
| Different `set.seed()` values for "different runs" inside workers | Workers collide; results unpredictable | One `set.seed()` before the parallel call only |

## H. When Seeds Are NOT Needed

If worker functions are **purely deterministic** — no calls to `rnorm()`, `runif()`, `sample()`, `rbinom()`, or any other RNG function — then seeds are unnecessary.

- `future.seed = NULL` (the default) is fine and skips the overhead of generating substreams
- This applies to: data transformations, string processing, file parsing, deterministic model scoring

**When in doubt, use `future.seed = TRUE`** — the overhead of generating L'Ecuyer-CMRG substreams is negligible compared to the cost of non-reproducible results in research.

## I. Post-Parallelization Verification and Revert Workflow

### Step 1: Archive

Before any edits, copy the original script to a `.drafts/` subfolder:

```bash
mkdir -p .drafts && cp analysis.R .drafts/analysis_sequential.R
```

The `_sequential` suffix communicates what the backup is. `.drafts/` keeps archived files out of the working directory.

Git commit immediately:
```
"Archive sequential version of analysis.R before parallelizing"
```

### Step 2: Identify key outputs

Scan the script for file writes and result objects:
- **File writes:** `saveRDS()`, `write_csv()`, `write.csv()`, `ggsave()`, `writeLines()`
- **Last assigned objects** before script end
- **If script is `source()`d from a master:** check what the master expects

### Step 3: Run sequential baseline

Source the archived original in a clean environment and capture outputs:

```r
# Run sequential version
seq_env <- new.env(parent = globalenv())
plan(sequential)
set.seed(42)
source(".drafts/analysis_sequential.R", local = seq_env)

# Capture file outputs
seq_files <- list(
  result = readRDS("output/result.rds")
)

# Capture key objects
seq_objects <- list(
  results = seq_env$results
)
```

### Step 4: Run parallel version

Clean up output files from the baseline run first, then source the rewritten script:

```r
# Clean up baseline outputs
file.remove("output/result.rds")

# Run parallel version
par_env <- new.env(parent = globalenv())
plan(multisession)
set.seed(42)
source("analysis.R", local = par_env)

# Capture outputs
par_files <- list(
  result = readRDS("output/result.rds")
)

par_objects <- list(
  results = par_env$results
)

plan(sequential)
```

### Step 5: Compare

```r
# For numeric results (tolerant of floating-point differences):
all.equal(seq_files$result, par_files$result)
# Should return TRUE

# For non-numeric or exact results:
identical(seq_files$result, par_files$result)
# Should return TRUE
```

**What to compare:** every file the original writes, key result objects.

**What NOT to compare:** console output, timing, worker count messages.

### Step 6: If mismatch — revert

1. Copy archive back: `cp .drafts/analysis_sequential.R analysis.R`
2. Git commit: `"Revert analysis.R: parallel outputs diverged from sequential, restoring original"`
3. Report to user: which outputs differed, nature of difference, which parallelization change likely caused it
4. Do NOT retry — hand off to user

### Step 7: If match — done

1. Git commit: `"Verified analysis.R: parallel outputs match sequential"`
2. Report success and list transformations applied
3. Keep `.drafts/analysis_sequential.R` archive — do not delete
