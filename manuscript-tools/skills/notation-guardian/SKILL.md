---
name: notation-guardian
description: Use when the user is writing or editing math-heavy Quarto or LaTeX documents, defines new notation, asks about notation consistency, wants to check for symbol conflicts, or mentions notation conventions in economics papers
---

# Notation Integrity Guardian

Maintains a per-project Notation Registry (`.notation-registry.json`) that tracks every mathematical symbol, its meaning, and where it was defined. Checks new notation against existing definitions and standard economics conventions. Works for both `.qmd` (Quarto) and `.tex` (LaTeX) files.

## Constraints

- **NEVER** silently change notation — notation choices are deliberate research decisions
- **ALWAYS** suggest fixes, never auto-apply symbol changes
- **MUST** preserve existing registry entries (don't overwrite without user confirmation)
- **MUST** track custom LaTeX commands (`\newcommand`, `\DeclareMathOperator`) alongside bare symbols

## Escalation Policy

- **Flag immediately**: Same symbol defined with two different meanings in the same paper
- **Suggest**: Non-standard symbol for a well-known concept (e.g., `$u$` for errors when `$\epsilon$` is established)
- **Note quietly**: Minor stylistic preferences (e.g., `\mathrm{Var}` vs `\text{Var}`)
- **Don't flag**: Index variables (`i`, `j`, `k`, `t`) used as subscripts across contexts (these are generic)

## Workflow

### Mode A: Full Scan

Triggered on first use or when user requests "check notation" / "scan notation".

1. Locate all `.qmd`/`.tex` files in the project
2. Scan each file for math environments per `references/detection-patterns.md`
3. Extract symbol definitions and usages
4. Build or update `.notation-registry.json` per `references/registry-format.md`
5. Run conflict detection (same symbol different meaning, different symbol same concept)
6. Compare against conventions in `references/econ-conventions.md`
7. Report results (see output format below)

### Mode B: Incremental Check

Triggered when user is editing a specific file.

1. Read the current file
2. Load existing `.notation-registry.json`
3. For any new symbol definitions in the file, check against registry
4. Flag conflicts or convention deviations immediately
5. Update registry with new entries

### Mode C: New Symbol Introduction

Triggered when user defines a new variable or asks "can I use X for Y?"

1. Check registry for existing use of that symbol
2. Check conventions in `references/econ-conventions.md` for the concept being represented
3. If conflict: suggest alternative symbol with rationale
4. If clean: add to registry, confirm to user

## Output Format

```
Notation Scan: model.qmd

New symbols: 3 added to registry
  theta — average return (parameter) [line 15]
  gamma_i — context parameter (parameter) [line 10]
  s_j — peer signal (variable) [line 22]

Conflicts: 1 found
  !! gamma used as "context parameter" in model.qmd:10
     but as "regression coefficient vector" in ext_valid_rcts.qmd:95
     Suggestion: Use delta or lambda for the regression coefficient

Convention notes: 1
  -- Using \mathbf{P} for probability. Consider \mathbb{P} for consistency
     with modern convention (or keep if project-wide).
```

## Quick Reference

| Check | Rule |
|---|---|
| Same symbol, two meanings | Flag as conflict (high severity) |
| Two symbols, one concept | Suggest consolidation (medium) |
| Non-standard for concept | Note with standard alternative (low) |
| Custom command defined in multiple files | Flag if expansions differ |
| Index variables reused | Don't flag — `i`, `j`, `k`, `t` are generic |
| First occurrence without definition | Warn as "possibly undefined" |
