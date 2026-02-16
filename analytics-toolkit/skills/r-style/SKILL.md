---
name: r-style
description: Use when the user has FINISHED R analysis code and wants it cleaned up for human readability — removes LLM code smells, rewrites to match personal style. Only use after analysis is complete and outputs are verified, never during initial development or debugging.
---

# R Style Enforcer

Detects LLM code smells in R scripts and rewrites them to match the user's personal coding style, with archive-verify-revert safety. **This is a post-production skill** — use it only after the analysis is complete and outputs are verified. Do NOT use it while first writing or debugging scripts; the verbose LLM patterns (status printing, tryCatch, etc.) are useful during development. This skill is for making finished code readable to humans.

## Constraints

**NEVER:**
- Use this skill during initial development or debugging — LLM patterns (verbose output, tryCatch, etc.) are useful while building; this skill is only for post-production cleanup
- Change statistical logic, model specifications, or results
- Remove code that affects output (only remove style/presentation artifacts)
- Auto-rewrite when outputs cannot be verified — hand off instead
- Introduce new packages not already loaded
- Touch quote style, pipe style (`%>%` vs `|>`), `ifelse()` vs `if_else()`, or `across()` vs `mutate_at()`

**MUST:**
- Archive original to `<filename>_llm_draft.R` before any changes
- Capture output from the original version before editing
- Verify rewritten version produces identical output
- Revert from archive if outputs diverge, reporting what differed
- Flag ambiguous transformations for user review (see escalation policy)
- Use `<-` for assignment exclusively
- Include explicit `return()` in every function
- Prefer `purrr::map()` and friends when purrr/tidyverse is loaded — do NOT convert purrr to lapply
- Search the entire project for callers (`grep -r "function_name"`) before classifying any function as single-use
- Commit with git after each transformation step, using succinct 2-3 sentence commit messages
- Move archived files into a `.drafts/` subfolder (not alongside the working files)

**CAN:**
- Rename variables (SCREAMING_SNAKE_CASE → snake_case, verbose → concise)
- Strip verbose `cat()` / status printing / emoji checkmarks
- Remove template headers, "End of Script" markers, over-documentation
- Inline unnecessary abstractions (only after confirming single-use via project-wide grep)
- Add substantive comments where logic is non-obvious and no comment exists (explain WHY, not WHAT)

## Escalation Policy

**Proceed automatically when:**
- Removing boilerplate (template headers, "End of Script", ASCII dividers, emoji checkmarks, "Step N:" narration, "Next step:" signposts, "Author:" attribution)
- Renaming SCREAMING_SNAKE_CASE to snake_case
- Stripping verbose `cat()` output
- Removing Roxygen on non-package functions
- Removing "ABSTRACTION NOTE" comments
- Dropping `data_` prefixes
- Fixing `=` assignment to `<-`
- Adding explicit `return()`
- Inlining functions confirmed single-use by project-wide grep

**Flag for user when:**
- Removing `tryCatch` that protects genuinely risky operations (file I/O, network)
- Collapsing multiple files into one
- Changing code logic beyond pure style
- Removing a utility file or test file
- Splitting or joining scripts (see scope rules in `references/style-guide.md` §I)

**Hand off to user when:**
- Verification fails (outputs differ)
- Structural reorganization needed (changing file dependencies)
- Genuine bugs discovered (report but don't fix)
- Scripts that can't be verified (long-running, external dependencies)

## Workflow

1. Read the complete R script
2. Identify LLM smells using the detection table and `references/smell-catalog.md`
3. Search the entire project for function/variable usage before classifying anything as single-use
4. Classify each transformation: auto-rewrite, flag, or hand-off per escalation policy
5. Evaluate script scope: check if the script should be split (too many responsibilities) or joined with another (see `references/style-guide.md` §I)
6. **Archive**: Create `.drafts/` subfolder if it doesn't exist; copy original to `.drafts/<filename>_llm_draft.R`
7. **Git commit**: Commit the archive with message: `"Archive LLM draft of <filename> before restyling"`
8. **Capture baseline**: Run original, identify and capture key output objects per `references/verification.md`
9. Rewrite using rules from `references/style-guide.md` and patterns from `references/smell-catalog.md`
10. **Git commit**: Commit rewritten file with message describing transformations applied (2-3 sentences)
11. **Verify**: Run rewritten version, compare outputs per `references/verification.md`
12. If match → done. **Git commit** confirming verification passed.
13. If mismatch → **revert** from `.drafts/` archive, **git commit** the revert, report discrepancies, hand off to user
14. Report: list all transformations applied, any flagged items, and verification result

## Detection Table

| Signal in code | Category | Action | Fix |
|---|---|---|---|
| `cat("✓ ...")` / `cat("✗ ...")` | Emoji status | Auto | Remove |
| `cat(rep("=", N), ...)`, boxed headers | ASCII art | Auto | Remove |
| `cat("Step N: ...")` | Step narration | Auto | Remove |
| `cat("Next step: ...")` | Signpost | Auto | Remove |
| 20+ line header with Inputs/Outputs/Scalability | Template header | Auto | Condense to 1-3 lines |
| `# Author: Refactored for X` / `# Last Modified:` | Attribution boilerplate | Auto | Remove |
| `# End of Script` / `# End of X` | Script closer | Auto | Remove |
| `#' @param` / `#' @return` on non-exported functions | Roxygen on analysis code | Auto | Remove or brief comment |
| `# ABSTRACTION NOTE:` | Meta-commentary | Auto | Remove |
| `# Scalability:` / `# Parallel:` / `# Dependencies:` | Metadata comments | Auto | Remove |
| `tryCatch` around `lm()`, `glm()`, `source()` | Defensive model/source | Auto | Remove wrapper |
| `tryCatch` around file I/O, network | Defensive I/O | Flag | Ask user |
| `invisible(list(...))` at script end | SDE return pattern | Auto | Remove |
| `run_script()` wrapper around `source()` | Over-engineered runner | Flag | Suggest direct `source()` |
| `SCREAMING_SNAKE_CASE` variables | SDE naming | Auto | Rename to snake_case |
| `data_` prefix on data frames | SDE naming | Auto | Drop prefix |
| Script producing 3+ independent outputs (tables, figures, datasets) | Scope bloat | Flag | Suggest splitting per §I |
| Two scripts that share >50% logic | Redundant scripts | Flag | Suggest merging per §I |
| Non-obvious logic with no comment | Missing context | Auto | Add substantive comment explaining WHY |
| `=` for assignment | Assignment style | Auto | Replace with `<-` |
| Function without explicit `return()` | Implicit return | Auto | Add `return()` |
| Helper function used once + justification comment | Unnecessary abstraction | Flag | Suggest inlining |
| Utility file with single caller | Over-modularization | Flag | Suggest merging |
| Unit test files for analysis scripts | SDE infrastructure | Flag | Note to user |
| Dual-format figure saving (PDF + PNG) | LLM caution | Flag | Ask user preference |
| 400-line package management utility | Over-engineering | Flag | Suggest `library()` at top |

## Quick Reference

- **Assignment**: `<-` always, never `=`
- **Returns**: explicit `return()` in every function
- **Iteration**: prefer `purrr::map()` when tidyverse is loaded; leave existing purrr/lapply as-is
- **Naming**: snake_case; concise readable names; no SCREAMING_SNAKE_CASE
- **Headers**: 1-3 lines explaining what the script does, not a template
- **Comments**: Full sentences explaining WHY, not narrating WHAT; plenty of them
- **Console**: Minimal; `message()` for genuinely useful info, no emoji/boxes/narration
- **Scope**: One responsibility per script; split bloated scripts, merge redundant ones (flag for user)
- **Git**: Commit at each stage (archive, rewrite, verify) with succinct messages
- **Archives**: `.drafts/` subfolder, never alongside working files
- **Don't touch**: quote style, pipe style, `ifelse` vs `if_else`, `across` vs `mutate_at`, `lapply` vs `map`
