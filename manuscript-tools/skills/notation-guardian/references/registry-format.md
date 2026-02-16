# Notation Registry Format

JSON schema for `.notation-registry.json`, symbol categories, and registry management rules.

---

## A. Registry Location and Lifecycle

- **File:** `.notation-registry.json` in the project root directory
- **Created:** automatically on first scan if it doesn't exist
- **Updated:** incrementally as new symbols are found
- **Persists:** across Claude sessions (it's a file on disk)
- **Git:** should be added to `.gitignore` (it's a tool artifact, not paper content)

---

## B. JSON Schema

```json
{
  "version": 1,
  "project_name": "Context",
  "last_scanned": "2026-02-12T15:30:00Z",
  "files_scanned": ["model.qmd", "appendix.qmd", "paper/new.tex"],
  "symbols": {
    "\\theta": {
      "meaning": "average return to technology",
      "category": "parameter",
      "first_defined_in": "model.qmd",
      "first_defined_at": "line 15",
      "definition_text": "The average return $\\theta$ is unknown.",
      "distribution": "\\mathcal{N}(\\mu_\\theta, \\sigma_\\theta^2)",
      "used_in": ["model.qmd", "appendix.qmd", "results.qmd"],
      "conflicts": []
    },
    "\\gamma_i": {
      "meaning": "agent i's context parameter",
      "category": "parameter",
      "first_defined_in": "model.qmd",
      "first_defined_at": "line 10",
      "definition_text": "$\\gamma_i \\sim \\mathcal{N}(0, \\sigma_\\gamma^2)$",
      "distribution": "\\mathcal{N}(0, \\sigma_\\gamma^2)",
      "used_in": ["model.qmd", "intuition.qmd", "appendix.qmd"],
      "conflicts": []
    },
    "\\epsilon_{ivt}": {
      "meaning": "error term in regression specification",
      "category": "error_term",
      "first_defined_in": "ext_valid_rcts.qmd",
      "first_defined_at": "line 95",
      "definition_text": "$\\epsilon_{ivt}$ in regression equation",
      "used_in": ["ext_valid_rcts.qmd", "ext_valid_surveys.qmd"],
      "conflicts": []
    }
  },
  "custom_commands": {
    "\\E": {
      "expansion": "{\\bf E}",
      "meaning": "expectation operator",
      "defined_in": "Paper.qmd",
      "standard_alternative": "\\mathbb{E}"
    },
    "\\R": {
      "expansion": "\\mathbb{R}",
      "meaning": "real numbers",
      "defined_in": "paper/new.tex"
    },
    "\\argmax": {
      "expansion": "\\operatornamewithlimits{argmax}",
      "meaning": "argmax operator",
      "defined_in": "paper/new.tex"
    }
  },
  "conventions_used": {
    "error_term": "\\epsilon",
    "expectation": "\\mathbb{E}",
    "probability": "\\mathbf{P}",
    "variance": "\\text{Var}",
    "covariance": "\\text{Cov}",
    "real_numbers": "\\mathbb{R}",
    "natural_numbers": "\\mathbb{N}",
    "indicator": "\\bm{1}"
  }
}
```

### Field descriptions

| Field | Type | Description |
|---|---|---|
| `version` | integer | Schema version (currently 1) |
| `project_name` | string | Project directory name |
| `last_scanned` | ISO 8601 | Timestamp of most recent scan |
| `files_scanned` | string[] | Relative paths of all files scanned |
| `symbols` | object | Map of symbol string → symbol entry |
| `custom_commands` | object | Map of command string → command entry |
| `conventions_used` | object | Map of concept → notation chosen in this project |

### Symbol entry fields

| Field | Type | Required | Description |
|---|---|---|---|
| `meaning` | string | yes | Plain-English description of what the symbol represents |
| `category` | string | yes | One of the categories in section C |
| `first_defined_in` | string | yes | Relative path to file where first defined |
| `first_defined_at` | string | yes | Line number or location |
| `definition_text` | string | yes | The sentence or equation defining the symbol |
| `distribution` | string | no | Distributional assumption if specified |
| `used_in` | string[] | yes | All files where this symbol appears |
| `conflicts` | array | yes | List of conflict entries (empty if none) |

### Custom command entry fields

| Field | Type | Required | Description |
|---|---|---|---|
| `expansion` | string | yes | LaTeX expansion of the command |
| `meaning` | string | yes | What the command represents |
| `defined_in` | string | yes | File containing the `\newcommand` |
| `standard_alternative` | string | no | More conventional notation, if applicable |

---

## C. Symbol Categories

| Category | Description | Examples |
|---|---|---|
| `parameter` | Model parameters to be estimated or calibrated | `\theta`, `\beta`, `\gamma` |
| `variable` | Random variables, data | `Y`, `X`, `D`, `s_j` |
| `index` | Subscript indices | `i`, `j`, `k`, `t`, `v` |
| `error_term` | Disturbance/noise terms | `\epsilon`, `u`, `\nu` |
| `operator` | Mathematical operators | `\E`, `\Var`, `\argmax` |
| `set` | Sets and spaces | `\mathcal{I}`, `\mathbb{R}`, `\Theta` |
| `distribution` | Distribution families | `\mathcal{N}`, `F` |
| `constant` | Named constants | `N`, `K`, `T` (sample sizes) |
| `function` | Named functions | `f`, `g`, `U` (utility) |

---

## D. Registry Operations

### Initialize

Scan all `.qmd`/`.tex` files in the project. For each math environment, extract symbols and definitions. Populate registry. Set `last_scanned` and `files_scanned`.

### Update

On subsequent scans:
- Add new symbols not yet in registry
- Update `used_in` lists with newly-found usages
- Detect new conflicts
- Update `last_scanned` timestamp
- Do NOT overwrite existing `meaning` or `definition_text` without user confirmation

### Conflict detection rules

1. **Same symbol, different meanings**: `\gamma` defined as "context parameter" in model.qmd but as "regression coefficient vector" in ext_valid_rcts.qmd
2. **Different symbols, same concept**: `\epsilon` used for errors in one file, `u` in another
3. **Redefinition**: Symbol re-defined with different meaning in a later section
4. **Custom command collision**: Two files define `\E` differently

### Conflict entry format

```json
{
  "type": "same_symbol_different_meaning",
  "symbol": "\\gamma",
  "meaning_1": {"text": "context parameter", "file": "model.qmd", "line": 10},
  "meaning_2": {"text": "regression coefficient", "file": "ext_valid_rcts.qmd", "line": 95},
  "severity": "high",
  "suggestion": "Use \\gamma for context parameter (established earlier). Use \\delta or \\lambda for regression coefficient."
}
```

### Conflict types and severity

| Type | Severity | Description |
|---|---|---|
| `same_symbol_different_meaning` | high | One symbol, two meanings |
| `different_symbol_same_concept` | medium | Two symbols for the same concept |
| `redefinition` | high | Symbol meaning changes mid-paper |
| `custom_command_collision` | high | Same `\newcommand` with different expansions |
| `non_standard_convention` | low | Valid but unusual notation choice |
