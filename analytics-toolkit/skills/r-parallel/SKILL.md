---
name: r-parallel
description: Use when the user wants to parallelize R code, speed up R scripts, or convert sequential loops/apply calls to parallel execution using the future framework
---

# R Parallelizer

Converts sequential R code to parallel execution using the future ecosystem, with correct seed handling for reproducibility and cross-platform backends.

## Constraints

**NEVER:**
- Change statistical logic or results
- Use `set.seed()` inside parallel workers
- Recommend `plan(multicore)` — not cross-platform (unreliable on macOS, unavailable on Windows)
- Delete the original sequential code — archive it first
- Use `parallel`, `doParallel`, or `doSNOW` — everything uses the `future` ecosystem

**MUST:**
- Use `plan(multisession)` as default backend
- Enable parallel-safe RNG seeds (L'Ecuyer-CMRG) via the appropriate seed argument
- Preserve all upstream data/analysis code
- Ensure all `library()` calls present for new packages
- Archive the original script to `.drafts/<filename>_sequential.R` before any edits
- Run a verification test comparing sequential vs parallel output for equivalence
- Commit with git after each stage (archive, rewrite, verify/revert) with succinct messages
- Hand off to the user if verification fails or if the parallelization is non-trivial and stuck

**CAN:**
- Restructure loop/apply patterns into parallel equivalents
- Add `progressr` progress reporting for long tasks

## Escalation Policy

**Ask user when:**
- Sequential dependency is ambiguous
- Code modifies global state or writes files in a loop
- Non-exportable objects detected (DB connections, external pointers)
- Original code has `set.seed()` calls with unclear intent

**Hand off to user when:**
- Verification test fails (sequential != parallel output) — revert from `.drafts/` archive, commit the revert, and explain what was attempted
- Parallelization is non-trivial and multiple attempts haven't succeeded
- The pattern doesn't fit any known template

**Proceed when:**
- Loop body is purely functional
- Apply/map calls with stateless functions
- Bootstrap/MC/permutation patterns
- Independent model fits

## Workflow

1. Read script completely
2. Identify parallelizable patterns using the detection table below
3. Check disqualifiers per `references/pitfalls.md`
4. **Archive**: Create `.drafts/` subfolder if needed; copy original to `.drafts/<filename>_sequential.R`
5. **Git commit**: `"Archive sequential version of <filename> before parallelizing"`
6. Determine package: `future.apply` (base R), `furrr` (purrr), `doFuture` (foreach)
7. Rewrite using templates from `references/future-patterns.md`
8. Apply seed rules from `references/seed-handling.md`
9. Add `plan(multisession)` setup block at top
10. Add `library()` calls for new packages
11. Optionally add `progressr` progress reporting
12. **Git commit**: `"Parallelize <filename>: <2-3 sentence summary of changes>"`
13. **Verify**: Run both sequential and parallel versions, compare outputs per `references/seed-handling.md` §I
14. If match → done. **Git commit**: `"Verified <filename>: parallel outputs match sequential"`
15. If mismatch → **revert** from `.drafts/` archive, **git commit** the revert, report what diverged, and hand off to the user

## Detection Table

| Signal in code | Category | Parallel replacement | Package |
|---|---|---|---|
| `for (i in ...) { results[[i]] <- ... }` | Accumulating for-loop | `future_lapply()` | future.apply |
| `lapply(x, fun)` | Base apply | `future_lapply(x, fun)` | future.apply |
| `sapply(x, fun)` | Base apply | `future_sapply(x, fun)` | future.apply |
| `vapply(x, fun, type)` | Base apply | `future_vapply(x, fun, type)` | future.apply |
| `mapply(fun, x, y)` / `Map(fun, x, y)` | Base apply | `future_mapply(fun, x, y)` | future.apply |
| `tapply(x, index, fun)` | Base apply | `future_tapply(x, index, fun)` | future.apply |
| `replicate(n, expr)` | Replication | `future_lapply(1:n, function(i) expr)` | future.apply |
| `purrr::map(x, fun)` | purrr | `furrr::future_map(x, fun)` | furrr |
| `purrr::map_dfr(x, fun)` | purrr | `furrr::future_map_dfr(x, fun)` | furrr |
| `purrr::map2(x, y, fun)` | purrr | `furrr::future_map2(x, y, fun)` | furrr |
| `purrr::pmap(list, fun)` | purrr | `furrr::future_pmap(list, fun)` | furrr |
| `foreach(i=...) %do% {...}` | foreach | `foreach(i=...) %dofuture% {...}` | doFuture |
| Nested loops → matrix/list | Nested loop | Flatten to single `future_lapply()` | future.apply |

## Quick Reference

- **Backend**: `plan(multisession)` always
- **Seeds**: `future.seed = TRUE` / `furrr_options(seed = TRUE)` / `.options.future = list(seed = TRUE)`
- **Globals**: auto-detected; explicit via `future.globals` / `future.packages`
- **Progress**: `library(progressr); handlers(global = TRUE); with_progress({ ... })`
- **Cleanup**: `plan(sequential)` at end
- **Workers**: `availableCores()` to detect; `plan(multisession, workers = N)` to set
- **Archives**: `.drafts/` subfolder, `_sequential` suffix, never alongside working files
- **Git**: Commit at each stage (archive, rewrite, verify/revert) with succinct messages
