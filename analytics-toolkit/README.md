# Analytics Toolkit

Tools for R workflow optimization in research data analysis: parallel execution, code quality, environment management, and pipeline auditing.

## 📦 Installation

See the marketplace README in the parent directory for installation instructions. Once installed, all tools listed below are available within Claude Code.

## 🛠️ Tools Overview

**r-parallel** — Convert sequential R code to parallel execution using the future ecosystem. Handles seed management for reproducibility and supports cross-platform backends. Use when you want to speed up loops, apply calls, or other sequential operations in R.

**r-style** — Detect and refactor LLM-generated code smells in R scripts. Use after analysis is complete and outputs are verified to clean up code for readability and consistency with your coding style.

> **Note:** This skill is highly opinionated and reflects the original author's personal R coding conventions. After installation, you may want to customize it to match your own style. To do this:
> 1. Navigate to where Claude Code installed the skill:
>    ```bash
>    cd ~/.claude/plugins/cache/econtools_marketplace/analytics-toolkit/1.0.0/skills/r-style/
>    ```
> 2. Open the skill directory in Claude Code:
>    ```bash
>    claude code .
>    ```
> 3. Provide Claude with one of your own R projects as an example and ask it to update the skill's style guidelines to match your coding conventions. This will make the skill's recommendations better aligned with your practices.

**renv-manager** — Manage reproducible R environments using renv. Use when setting up new projects, transitioning existing projects to renv, or migrating from global package libraries to project-level dependency management.

**dependency-tracker** — Map complete data flow in research pipelines from raw inputs through intermediate processing to final manuscript outputs. Identifies stale files, broken links, and undocumented dependencies across R, Stata, Python, and LaTeX. Use when auditing research pipelines, checking for stale outputs, or understanding the complete dependency structure from raw data to publication.
