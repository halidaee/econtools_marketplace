# analytics-toolkit

R workflow skills for research data analysis projects.

## Skills

### r-parallel
Converts sequential R code to parallel execution using the future ecosystem, with correct seed handling for reproducibility and cross-platform backends.

**Use when**: You want to parallelize R code, speed up R scripts, or convert sequential loops/apply calls to parallel execution.

### r-style
Detects LLM code smells in R scripts and rewrites them to match your personal coding style. Post-production only -- use after analysis is complete and outputs are verified.

**Use when**: You have FINISHED R analysis code and want it cleaned up for human readability.

### renv-manager
Cautious DevOps engineer for R project infrastructure. Manages renv transitions and reproducible R environments with a stability-first approach.

**Use when**: Transitioning R projects to renv, setting up reproducible R environments, or migrating from global package libraries.

### dependency-tracker
Maps complete data flow in research projects from raw inputs through intermediate processing to final manuscript outputs. Identifies stale files, broken links, and undocumented dependencies across R, Stata, Python, and LaTeX.

**Use when**: Auditing research pipelines, checking for stale outputs, or mapping data flow from raw inputs to final LaTeX outputs.
