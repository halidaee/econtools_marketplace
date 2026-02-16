---
name: dependency-tracker
description: Use when auditing research pipelines in economics projects, checking for stale outputs, broken dependencies between data/scripts/manuscripts, or mapping data flow from raw inputs to final LaTeX outputs
---

# Research Pipeline Dependency Tracker

## Overview

Maps the complete data flow in research projects from raw inputs through intermediate processing to final manuscript outputs. Identifies stale files (code newer than results), broken links (missing files), and undocumented dependencies across R, Stata, Python, and LaTeX.

## When to Use

Use this skill when:
- Starting work on an inherited research project
- Before manuscript submission (verify all outputs are current)
- After modifying analysis code (check what needs regeneration)
- Debugging "why doesn't my change appear in the paper?"
- Documenting the replication pipeline

**Slash command**: `/audit-dag`

## Core Workflow

When `/audit-dag` is invoked:

1. **Scan project for I/O operations** across all languages
2. **Build dependency graph** from raw data → processed data → outputs → manuscript
3. **Check timestamps** for staleness
4. **Report issues** with actionable fixes

## Multi-Language I/O Detection

### R and Quarto (.R, .qmd, .Rmd)

**Read operations** (inputs):
```r
# Base R
read.csv(), read.table(), read.delim(), read.fwf()
readLines()
scan()
load()  # .RData, .rda files
readRDS()
source()  # CRITICAL: Loading other R scripts!

# Tidyverse/readr
read_csv(), read_tsv(), read_delim(), read_fwf()
readr::read_*()

# Data formats
haven::read_dta(), haven::read_sav(), haven::read_sas()
foreign::read.spss(), foreign::read.dta()
readxl::read_excel(), xlsx::read.xlsx()
arrow::read_parquet(), arrow::read_feather()
feather::read_feather()

# Fast readers
vroom::vroom()
data.table::fread()

# Databases
DBI::dbReadTable(), DBI::dbGetQuery()
odbc::dbConnect()

# Structured data
jsonlite::read_json(), jsonlite::fromJSON()
xml2::read_xml(), xml2::read_html()
yaml::read_yaml()

# Swiss-army knife
rio::import()

# Path helpers
here::here()  # Track relative paths
```

**Write operations** (outputs):
```r
# Base R
write.csv(), write.table()
writeLines()
save(), save.image()  # .RData files
saveRDS()
cat(file = "output.txt")  # Often missed!
sink("output.log")  # Log files - CRITICAL
sink()  # Close sink
capture.output(..., file = "output.txt")
dput(file = "object.R")
dump(file = "objects.R")

# Tidyverse/readr
write_csv(), write_tsv(), write_delim()
readr::write_*()

# Data formats
haven::write_dta(), haven::write_sav()
writexl::write_xlsx(), xlsx::write.xlsx()
arrow::write_parquet(), arrow::write_feather()
feather::write_feather()

# Graphics
ggsave()
pdf(), png(), jpeg(), tiff()  # with dev.off()
Cairo::CairoPDF()

# Tables and regression output
stargazer::stargazer(out = "table.tex")
texreg::texreg(file = "table.tex")
texreg::htmlreg(file = "table.html")
modelsummary::modelsummary(output = "table.tex")
gt::gtsave()
knitr::kable()

# Databases
DBI::dbWriteTable()

# Structured data
jsonlite::write_json(), jsonlite::toJSON()
xml2::write_xml()
yaml::write_yaml()

# Swiss-army knife
rio::export()
```

**Special cases**:
```r
# Regression data sources
feols(..., data = dataset_name)
lm(..., data = dataset_name)
glm(..., data = dataset_name)

# Rmarkdown/Quarto YAML headers
output_file: "report.html"  # in YAML
output_dir: "output/"

# Caching (check for stale cache)
drake::loadd(), drake::readd()
targets::tar_read(), targets::tar_load()
```

### Stata (.do, .ado)

**Read operations**:
```stata
use "filename.dta"
import delimited "file.csv"
import excel "file.xlsx"
insheet using "file.csv"
import sasxport5 "file.xpt"
import spss using "file.sav"
odbc load

merge 1:1 id using "other.dta"  # Reading other.dta
merge m:1 id using "other.dta"
append using "other.dta"

do "script.do"  # Running other scripts
run "script.do"
include "script.do"
```

**Write operations**:
```stata
save "output.dta"
export delimited "output.csv"
export excel "output.xlsx"
outsheet using "file.csv"
export sasxport5 "file.xpt"

# Log files - CRITICAL
log using "analysis.log", text replace
log using "analysis.smcl", replace
log close

# Tables and regression output
esttab using "table1.tex"
estout using "table1.tex"
outreg2 using "table1.tex"
outreg2 using "table1.doc"
putexcel set "workbook.xlsx"

# Graphs
graph export "figure1.pdf"
graph export "figure1.png"
graph export "figure1.eps"
graph save "figure1.gph"

# Matrix output
mat2txt, matrix(results) saving("matrix.txt")
```

**Special patterns**:
```stata
# Working directory changes (affects path resolution)
cd "new/path"

# Temporary files (usually don't track)
tempfile temp_data
tempname temp_matrix

# Preserved data (in-memory, but note the pattern)
preserve
restore
```

### Python (.py, .ipynb)

**Read operations**:
```python
# Pandas
pd.read_csv(), pd.read_table(), pd.read_excel()
pd.read_parquet(), pd.read_feather(), pd.read_hdf()
pd.read_stata(), pd.read_sas(), pd.read_spss()
pd.read_sql(), pd.read_sql_query(), pd.read_sql_table()
pd.read_pickle()
pd.read_json()

# NumPy
np.load(), np.loadtxt(), np.genfromtxt()
np.load()

# Python stdlib
open("file", "r"), open().read()
with open("file") as f:  # Context manager
csv.reader()
json.load()
pickle.load()
yaml.load(), yaml.safe_load()

# Databases
sqlite3.connect()
sqlalchemy.create_engine()

# Scientific formats
h5py.File()  # HDF5
pyarrow.parquet.read_table()

# ML models
joblib.load()  # Common for sklearn
```

**Write operations**:
```python
# Pandas
df.to_csv(), df.to_excel(), df.to_parquet()
df.to_feather(), df.to_hdf(), df.to_stata()
df.to_sql(), df.to_pickle(), df.to_json()

# NumPy
np.save(), np.savez(), np.savetxt()

# Python stdlib
open("file", "w"), open().write()
with open("file", "w") as f:
csv.writer()
json.dump()
pickle.dump()
yaml.dump()

# Logging - CRITICAL for tracking execution
logging.basicConfig(filename='analysis.log')
logging.FileHandler('output.log')

# Graphics
plt.savefig()
fig.savefig()
seaborn plots with plt.savefig()

# Databases
df.to_sql()
cursor.execute()

# Scientific formats
h5py.File()  # HDF5
pyarrow.parquet.write_table()

# ML models
joblib.dump()  # Common for sklearn
torch.save()  # PyTorch models
model.save()  # Keras/TensorFlow
```

**Special patterns**:
```python
# Working directory changes
os.chdir()

# Dynamic paths
glob.glob("data_*.csv")  # Flag as dynamic
pathlib.Path.glob()

# Jupyter/IPython magic
%run script.py  # Running other scripts
```

### LaTeX (.tex)

**Manuscript dependencies**:
```latex
% Sections and text
\input{sections/intro.tex}
\include{sections/methods.tex}
\subfile{sections/results.tex}  % subfiles package

% Tables
\input{tables/table1.tex}
\inputtable{table1}  % Custom command (check preamble)

% Figures
\includegraphics{figures/fig1.pdf}
\includegraphics{figures/fig1.png}
\includegraphics{figures/fig1.eps}
\includestandalone{figures/diagram}  % standalone package

% Code listings
\lstinputlisting{code/analysis.R}  % listings package
\inputminted{python}{code/script.py}  % minted package
\verbatiminput{output.txt}

% Bibliography
\bibliography{references}  % BibTeX (.bib)
\addbibresource{references.bib}  # BibLaTeX
\ExecuteBibliographyOptions{...}

% TikZ externalization (generates PDFs)
\tikzsetnextfilename{diagram1}

% Import package
\import{sections/}{intro.tex}
\subimport{chapters/}{chapter1.tex}
```

**Custom commands** - Must parse preamble:
```latex
% In preamble
\newcommand{\inputtable}[1]{\input{tables/#1.tex}}
\newcommand{\fig}[1]{\includegraphics{figures/#1}}

% Usage expands paths
\inputtable{table1}  % → tables/table1.tex
\fig{fig1.pdf}       % → figures/fig1.pdf
```

## Dependency Classification

### Raw Data Files
**Never written by analysis scripts, only read**

File types:
- Tabular: `.csv`, `.tsv`, `.txt`, `.dat`
- Stata: `.dta`
- SAS: `.sas7bdat`, `.xpt`
- SPSS: `.sav`, `.por`
- Excel: `.xlsx`, `.xls`
- R data: `.RData`, `.rda`, `.rds`
- Modern formats: `.parquet`, `.feather`, `.arrow`
- Databases: `.db`, `.sqlite`, `.sqlite3`
- JSON/XML: `.json`, `.jsonl`, `.xml`
- HDF5: `.h5`, `.hdf5`
- Compressed: `.zip`, `.gz`, `.bz2` (containing data)

Detection: File is read by scripts but no script writes it
Status: "SOURCE" in DAG

### Intermediate Assets
**Written by one script, read by another**

Examples:
- `data/cleaned/panel.rds` (output of clean.R, input to analysis.R)
- `data/processed/merged.dta` (output of merge.do, input to analysis.do)

Detection: File is both written AND read across different scripts
Status: "INTERMEDIATE" in DAG

### Manuscript Outputs
**Written by analysis scripts, consumed by LaTeX**

Examples:
- `.tex` table fragments in `tables/`
- `.pdf`, `.png`, `.eps` figures in `figures/`
- `.bib` bibliography files

Detection: File is written by script AND referenced in `.tex` file
Status: "OUTPUT" in DAG

### Ghost Dependencies
**Packages loaded but never used, or unavailable**

Detection:
```r
library(packageName)  # or require()
```
```python
import package
```
```stata
ssc install package
```

Check: Is package actually called in the script? Is it installed in environment?

### Log Files and Execution Records
**Track but handle specially - not part of main DAG**

Examples:
- R: `.log` files from `sink()`, `.Rout` from `R CMD BATCH`
- Stata: `.log`, `.smcl` files from `log using`
- Python: `.log` files from `logging` module
- Cluster jobs: `.out`, `.err` files from SLURM/PBS
- History: `.Rhistory`, `.Rapp.history`

**Treatment**:
- Log files indicate script was run (use timestamp)
- Don't include in DAG (logs document execution, not data flow)
- Flag if log is newer than outputs (script ran but didn't produce outputs?)

### Cache and Build Artifacts
**Usually should be regenerated, not tracked in DAG**

Directories to flag but not deeply analyze:
- R: `renv/`, `.Rproj.user/`, `_cache/`, `*_cache/`
- Python: `__pycache__/`, `.ipynb_checkpoints/`, `.pytest_cache/`
- Build systems: `_targets/` (targets package), `.drake/` (drake package)
- knitr/Rmarkdown: `*_files/` directories (HTML widgets, figures)
- LaTeX: `*.aux`, `*.bbl`, `*.blg`, `*.log`, `*.out`, `*.synctex.gz`

**Treatment**: Mention these exist but recommend regenerating rather than tracking dependencies.

## Stale File Detection (Critical)

Compare `stat -f %m` (macOS) or `stat -c %Y` (Linux) timestamps:

### Stale Output Pattern
```
WARN: Script modified after its output
  analysis.R (2025-02-13 14:30)
    → tables/table1.tex (2025-02-12 10:15)
  ACTION: Re-run analysis.R
```

### Stale Input Pattern
```
WARN: Data updated after script last ran
  raw_data.csv (2025-02-13 16:00)
    → clean.R (2025-02-12 14:00)
    → panel.rds (2025-02-12 14:05)
  ACTION: Re-run clean.R (and downstream scripts)
```

### Missing Dependency
```
ERROR: LaTeX references non-existent file
  manuscript.tex calls \includegraphics{figures/fig3.pdf}
    → figures/fig3.pdf DOES NOT EXIST
  ACTION: Generate fig3.pdf or fix reference
```

## Output Format

### DAG Summary (Text-Based Flow)

```
RAW DATA:
  data/raw/census_2020.csv
  data/raw/survey_responses.dta

↓ [clean.R] ↓

INTERMEDIATE:
  data/cleaned/panel.rds (2025-02-12 14:05)

↓ [analysis.R] ↓

OUTPUTS:
  tables/table1.tex (2025-02-12 15:30)
  figures/fig1.pdf (2025-02-12 15:32)

↓ [manuscript.tex] ↓

MANUSCRIPT:
  manuscript.pdf (2025-02-13 09:00)
```

### Warnings Section

**Stale Dependencies:**
```
⚠️  STALE: analysis.R (modified 2025-02-13 14:30)
    Output table1.tex is older (2025-02-12 15:30)
    Re-run: Rscript analysis.R

⚠️  STALE: raw_data.csv (modified 2025-02-13 16:00)
    Script clean.R last ran 2025-02-12 14:00
    Re-run: Rscript clean.R && Rscript analysis.R
```

**Missing Files:**
```
❌ MISSING: manuscript.tex references figures/fig3.pdf
    File does not exist
    Check: ls figures/ for actual filename

❌ MISSING: analysis.R reads data/cleaned/old_panel.rds
    File not found (renamed or deleted?)
```

### Orphans Section

**Orphaned Scripts** (produce no output):
```
🔍 ORPHAN SCRIPT: exploratory.R
   Reads: panel.rds
   Writes: NOTHING
   Status: May be exploratory code or dead code
```

**Orphaned Outputs** (not used by manuscript):
```
🔍 ORPHAN OUTPUT: tables/table_appendix_z.tex
   Created by: analysis.R
   Called by: NONE (not in manuscript.tex or any \input)
   Status: May be unused or missing from LaTeX
```

## Implementation Instructions

### Use Fast Tools

**Prefer `ripgrep` (rg) over grep when available:**
```bash
# Check if ripgrep is available
if command -v rg &> /dev/null; then
  GREP_CMD="rg"
else
  GREP_CMD="grep -r"
fi
```

**Respect `.gitignore` automatically:**
```bash
rg --pattern "read_csv"  # Automatically respects .gitignore
```

**Skip common noise directories:**
```bash
rg --pattern "read_csv" \
   --glob '!renv/' \
   --glob '!node_modules/' \
   --glob '!.git/' \
   --glob '!.Rproj.user/' \
   --glob '!__pycache__/' \
   --glob '!.ipynb_checkpoints/' \
   --glob '!_cache/' \
   --glob '!*_cache/' \
   --glob '!_targets/' \
   --glob '!.drake/' \
   --glob '!.pytest_cache/' \
   --glob '!*.egg-info/' \
   --glob '!venv/' \
   --glob '!env/'
```

### File Scanning Strategy

1. **Glob for relevant files first:**
```bash
find . -type f \( -name "*.R" -o -name "*.qmd" -o -name "*.Rmd" \
     -o -name "*.do" -o -name "*.py" -o -name "*.tex" \) \
     -not -path "*/renv/*" -not -path "*/.git/*"
```

2. **Parse each file for I/O operations**
3. **Build adjacency list** (file → dependencies)
4. **Walk the graph** from raw data to manuscript

### Timestamp Comparison

```bash
# Get modification time (seconds since epoch)
# macOS:
mod_time=$(stat -f %m "$file")

# Linux:
mod_time=$(stat -c %Y "$file")

# Compare
if [ $script_time -gt $output_time ]; then
  echo "STALE: $output_file (script is newer)"
fi
```

## Common Patterns to Watch

### Pattern 1: Hardcoded Paths
```r
# BAD: Hard to track
read_csv("/Users/researcher/data/file.csv")

# GOOD: Trackable with here::here()
read_csv(here::here("data", "raw", "file.csv"))
```

### Pattern 2: Dynamic Filenames
```r
# Hard to track statically
for (year in 2010:2020) {
  read_csv(paste0("data_", year, ".csv"))
}
```
**Solution**: Flag as "DYNAMIC PATH - manual verification needed"

### Pattern 3: Conditional Writes
```python
if not os.path.exists("output.csv"):
    df.to_csv("output.csv")
```
**Solution**: Still track as output (conditional doesn't change dependency)

### Pattern 4: Custom LaTeX Commands
```latex
% User-defined in preamble
\newcommand{\inputtable}[1]{\input{tables/#1.tex}}

% Later used as
\inputtable{table1}  % Expands to tables/table1.tex
```
**Solution**: Parse preamble for custom commands, expand during scan

### Pattern 5: Working Directory Changes
```r
setwd("subdirectory/")
read.csv("data.csv")  # Actually reads subdirectory/data.csv
```
```python
os.chdir("analysis/")
pd.read_csv("input.csv")  # Relative to new working directory
```
```stata
cd "analysis"
use "data.dta"  # Relative to new directory
```
**Solution**: Track working directory state per script; resolve relative paths accordingly. Flag `setwd()`/`os.chdir()`/`cd` as potentially confusing.

### Pattern 6: Source/Run Commands (Script Chains)
```r
source("helper_functions.R")  # Dependency on other script
```
```python
%run preprocessing.py  # In Jupyter
exec(open("utils.py").read())
```
```stata
do "clean_data.do"  # Running another script
```
**Solution**: These create script → script dependencies. Must track and ensure helper scripts are included in DAG.

## Real-World Impact

**Before submission**: Catches the "I edited the code but forgot to regenerate Table 3" error that would delay publication.

**Onboarding**: New RAs can run `/audit-dag` to understand the full pipeline in 30 seconds instead of reading weeks of README files.

**Replication**: Generates documentation for replication packages automatically by showing the exact order of script execution.

## Limitations

- **Dynamic paths**: Can't resolve `paste0("file_", variable, ".csv")` without executing
- **Conditionals**: Doesn't know which branch executes
- **External data**: API calls, database queries not tracked
- **Manual edits**: If you hand-edit a .tex file, timestamp may be misleading

**Solution for dynamic cases**: Flag them and request manual verification.
