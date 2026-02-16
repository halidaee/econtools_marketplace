# Manuscript Tools

Tools for academic manuscript preparation: citation discovery and management, bibliography quality control, figure and table formatting compliance, and mathematical notation standardization.

## 📦 Installation

Install via the marketplace. See the [parent directory README](../README.md) for instructions.

## ⚙️ Configuration (Required)

**Before using the bibliography tools,** you must configure CrossRef with your email address:

**Option 1: Environment variable**
```bash
export CROSSREF_MAILTO="your.email@domain.com"
```

**Option 2: Config file**
```bash
mkdir -p ~/.config/crossref-mcp
echo '{"mailto": "your.email@domain.com"}' > ~/.config/crossref-mcp/config.json
```

This gives you access to CrossRef's "polite pool" (50 req/s vs 1 req/s). Without it, citation resolution will be slow or fail.

**Optional:** For higher Semantic Scholar rate limits, add an API key to `~/.config/semantic-scholar-mcp/api_key` (see [marketplace README](../README.md) for details).

## 🛠️ Tools Overview

### 📚 Bibliography Management

The bibliography tools are split into two layers: **MCP servers** that provide programmatic access to specific data sources, and **skills** that orchestrate those servers into higher-level workflows.

#### 🔧 MCP Servers

These are the low-level building blocks. Each server exposes a small set of tools that do one thing well.

**bibtex-mcp** — Local operations on `.bib` files. Parses bibliography files into structured indices, scans `.qmd` and `.tex` documents for bare citations (e.g., "Conley and Udry (2010)" written out instead of using `@conley2010learning`), rekeys BibTeX entries to match a project's naming convention, and adds entries to `.bib` files. All operations are local — no network calls.

**crossref-mcp** — Searches the CrossRef API for scholarly metadata by author, title, year, or free text. Returns DOI-based publication records with a confidence score. Can retrieve BibTeX for any work with a DOI, and can find the published journal version of a working paper using title similarity matching.

**semantic-scholar-mcp** — Searches the Semantic Scholar API for paper metadata, abstracts, and citation data. Useful for broader keyword searches and for papers that may not yet have a DOI. Supports an optional API key for higher rate limits.

#### ✨ Skills

These orchestrate the MCP servers into complete workflows.

**bibtex-curator** — The main citation curation workflow. Scans a document for bare citations, resolves each one by checking the existing `.bib` file first, then searching CrossRef and Semantic Scholar if needed, adds new entries to the bibliography, and replaces bare citations with proper citation commands. Also checks whether working papers in the `.bib` file have since been published. Requires all three MCP servers to be installed.

**bibtex-janitor** — Standalone `.bib` file cleanup. Standardizes journal names (e.g., "JPE" to "Journal of Political Economy"), applies title casing with brace-protected acronyms, prunes unnecessary fields (abstracts, keywords, Mendeley metadata), and validates required fields by entry type. Designed for pre-submission cleanup to AER/QJE standards. Does not use the MCP servers — runs its own Python tooling directly.

### 📝 Manuscript Formatting

**aer-figures** — Validate and format figures to American Economic Review standards.

**aer-tables** — Validate and format tables to American Economic Review standards.

**notation-guardian** — Check mathematical notation consistency across a manuscript.

**proof-checker** — Proofread manuscripts for broken cross-references (e.g., dangling `@fig-` or `@tbl-` labels in Quarto), orphaned labels, inconsistent terminology, and undefined acronyms. Works with `.qmd` and `.tex` files, including multi-file projects.

**palette-designer** — Design colorblind-accessible color palettes for figures.

**visual-sync** — Ensure visual consistency across all manuscript elements (figures, tables, captions).

## 📖 Bibliography Workflow: Best Practices

The bibliography tools are designed around a common workflow in economics: you write a draft with citations spelled out in prose, then formalize them before submission. Here is how to get the most out of the tools, and what to be aware of.

### 🔄 Typical workflow

1. **Scan** your document with bibtex-curator. It uses bibtex-mcp's `scan_bare_citations` to find written-out citations like "Banerjee et al. (2013)" that should be proper `@key` or `\cite{key}` commands.

2. **Resolve** each citation. The curator works through several sources in priority order:
   - First, it checks your existing `.bib` file (cheap, fast, no network).
   - If the paper isn't there, it searches your project directory for markdown files that mention the author and year. If you keep reading notes, literature reviews, or paper summaries as `.md` files in your project folder — even informal ones with just titles and abstracts — the curator can use them to identify what a bare citation is actually referring to before hitting external APIs. For example, a file like `notes/lit-review.md` containing:

     ```markdown
     ## Conley and Udry (2010)
     "Learning about a New Technology: Pineapple in Ghana"
     AER, 100(1), 35-69

     Farmers learn about new technologies from neighbors. Uses spatial
     structure of social networks to identify information flows.
     ```

     is enough for the curator to match a bare "Conley and Udry (2010)" in your manuscript to the correct paper and then confirm it via CrossRef or Semantic Scholar. The format doesn't matter much — the curator greps for author names and years, then uses whatever context it finds (titles, journal names, DOIs) to narrow the API search.
   - If local sources don't resolve the citation, it searches CrossRef, then Semantic Scholar. CrossRef tends to be better for published economics papers; Semantic Scholar has broader coverage of working papers and preprints.

3. **Add and replace.** For each resolved citation, the curator rekeys the BibTeX entry to match your project's naming convention (e.g., `conley2010learning`), adds it to your `.bib` file, and replaces the bare citation with the correct command for your document type (Quarto or LaTeX).

4. **Upgrade working papers.** After all citations are resolved, the curator checks whether any `@techreport` or `@unpublished` entries in your `.bib` have since been published as journal articles, using CrossRef's title similarity matching.

5. **Clean up.** Run bibtex-janitor separately to standardize journal names, fix title casing, and prune metadata fields before submission.

### 💡 How to use

In Claude Code, you trigger skills by describing what you want in natural language. The skills activate automatically based on your request. Some examples:

```
Fix the bare citations in paper.qmd
```

This triggers bibtex-curator, which scans the document, resolves citations against your `.bib` file and external APIs, and replaces bare citations with proper commands.

```
Clean up references.bib for AER submission
```

This triggers bibtex-janitor to standardize journal names, fix casing, and prune unnecessary fields.

```
Check if any of the working papers in references.bib have been published
```

This uses crossref-mcp's `find_published_version` to check each `@techreport` and `@unpublished` entry.

```
Find the DOI for Conley and Udry 2010
```

This uses the MCP servers directly — no skill orchestration needed.

```
Format all figures in the manuscript for AER submission
```

This triggers aer-figures to validate dimensions, fonts, and labeling against AER guidelines.

You do not need to name the specific skill or MCP server. Claude Code matches your request to the appropriate tool.

### ⚠️ Limitations

The bibliography tools handle the bulk of routine citation work well: resolving "Author (Year)" prose citations against known databases, managing `.bib` files, and formatting for journal submission. But there are cases where they need your help or where you should review the output.

**Coverage gaps.** Citation resolution depends on CrossRef and Semantic Scholar. Both have excellent coverage of published economics literature, but recent working papers, non-English publications, and older pre-digital works may not be indexed. When a paper cannot be found through either API, you will be asked to provide additional context (a title, DOI, or journal name) or to add the entry manually.

**Ambiguous citations.** The plugin will not guess. If "Smith (2015)" could refer to multiple papers, or if the best API match scores below the confidence threshold, it will ask you to choose. This is intentional — inserting the wrong citation is worse than leaving a bare one.

**Detection limits.** Citation scanning catches standard academic forms like "Author (Year)", "(Author et al., Year)", and common variations, but it uses pattern matching. It may flag non-citation text that resembles these patterns (e.g., "World Bank (2020 fiscal year)"), and it will miss citations written in highly unusual formats. Review the scan results before accepting all replacements.

**Working paper upgrades.** The check for whether a working paper has been published relies on title similarity matching against CrossRef. If a paper's title changed substantially between the working paper and published version, the match may not be found automatically. Providing the author name and working paper year improves results.

**Formatting opinions.** The bibtex-janitor cleanup applies AER/QJE conventions by default: full journal names, title case, field pruning. If your target journal expects different formatting (e.g., abbreviated journal names), review the output before committing.

### 🚦 API rate limits

- **CrossRef**: No API key required. Including a `mailto` address in the configuration gets you into the "polite pool" with better rate limits.
- **Semantic Scholar**: 100 requests per 5 minutes without an API key. Register for a free key at [semanticscholar.org](https://www.semanticscholar.org/product/api) for higher limits.

For typical manuscript curation (scanning one document, resolving 20-30 citations), you are unlikely to hit rate limits. Bulk operations across multiple documents may require pacing or an API key.

## ✍️ Manuscript Formatting Workflow: Best Practices

The formatting tools handle the gap between "analysis code that produces output" and "output that meets journal submission standards." They only change presentation — never statistical content, plotted data, or table values.

### 💡 How to use

```
Format my figures for AER submission
```

Rewrites the formatting layers of your R/ggplot2 figure scripts — themes, colors, fonts, dimensions, export settings — to AER standards. Your data manipulation and statistical content are left untouched. Titles are removed from figures (they belong in LaTeX/Quarto captions).

```
Format this regression table for journal submission
```

Rewrites R table code to produce AER-compliant LaTeX output: booktabs rules (three horizontal lines, no vertical lines), standard star conventions, SEs in parentheses, and proper decimal formatting. Which variables, statistics, and samples are reported does not change.

```
I need a color palette for the figures in my paper
```

You will be asked about your constraints (how many colors, colorblind safety, grayscale compatibility, print vs. digital) before any palette is generated. Most economics journals require grayscale-safe figures, so mention if that applies.

```
My figures use different fonts and colors across scripts — can you make them consistent?
```

All your plotting scripts are audited for inconsistencies in fonts, themes, colors, and line weights. You are shown what differs and asked which style to converge on before anything is changed. For projects with many figures, a shared style file may be suggested.

```
Check my notation for consistency
```

All `.qmd` and `.tex` files are scanned for mathematical symbols. If the same symbol is used with different meanings in different sections, or if non-standard notation is used for a well-known concept (e.g., `$u$` for errors instead of `$\epsilon$`), you are shown the conflicts and asked how to resolve them. Notation is never changed without your confirmation.

```
Check for broken references in my manuscript
```

Scans for dangling `@fig-` and `@tbl-` references, orphaned labels, inconsistent capitalization ("Figure" vs "figure"), undefined acronyms, and prose issues like long sentences or hedging clusters. Returns a report with line numbers and suggested fixes. Nothing is auto-corrected.

### ⚠️ Limitations

**R-specific figure and table formatting.** The figure and table formatters rewrite R and ggplot2 code. If your figures are produced in Stata or Python, they can describe the formatting requirements but will not rewrite the code.

**AER-centric defaults.** The formatters target AER conventions. Most top economics journals (QJE, Econometrica, JPE, ReStud) have similar requirements, but if your target journal has different specifications, mention it explicitly.

**Consultation by design.** Several of these tools — palette design, visual consistency, notation — will ask you questions before acting. This is intentional: getting style decisions right on the first pass saves more time than undoing wrong guesses.
