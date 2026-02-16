# Research Tools Marketplace

**Economics research skills for Claude Code** — streamline R analytics workflows and manuscript preparation with integrated tools for data analysis, bibliography management, and publication formatting.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/halidaee/Claude_Plugins)

---

## 📦 What's Included

This marketplace provides two integrated plugin collections with 12+ skills and MCP servers:

### [📊 Analytics Toolkit](./analytics-toolkit)

R workflow optimization for research data analysis

| Skill                  | Purpose                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| **r-parallel**         | Convert sequential R code to parallel execution (future ecosystem) |
| **r-style**            | Detect and refactor LLM code smells in R scripts                   |
| **renv-manager**       | Set up and manage reproducible R environments                      |
| **dependency-tracker** | Map data flow and identify stale outputs in research pipelines     |

### [📝 Manuscript Tools](./manuscript-tools)

Academic manuscript preparation with citation, formatting, and bibliography tools

#### MCP Servers

- **semantic-scholar-mcp** — Search Semantic Scholar API for papers and citations
- **crossref-mcp** — Query CrossRef metadata and publication versions
- **bibtex-mcp** — Local BibTeX parsing, citation scanning, and management

#### Skills

| Skill                 | Purpose                                        |
| --------------------- | ---------------------------------------------- |
| **aer-figures**       | AER-compliant figure formatting and validation |
| **aer-tables**        | AER-compliant table formatting and validation  |
| **bibtex-curator**    | BibTeX reference curation and quality control  |
| **bibtex-janitor**    | Automated BibTeX cleanup and normalization     |
| **notation-guardian** | Mathematical notation consistency checking     |
| **palette-designer**  | Color palette design with auto-preview         |
| **proof-checker**     | Cross-reference and formatting proofreading    |
| **visual-sync**       | Visual consistency across manuscript elements  |

---

## 🚀 Installation

To install the plugins, first install the marketplace. Go inside Claude Code and run:

```bash
/plugin marketplace add halidaee/econtools_marketplace
```

Then, install the plugins:

```bash
/plugin install analytics-toolkit@econtools_marketplace
/plugin install manuscript-tools@econtools_marketplace
```

---

## ⚠️ Token Usage Note

These plugins include multiple MCP servers and skills that are loaded into Claude's context when active. While powerful, they can be token-heavy if all plugins remain enabled simultaneously.

**Two approaches to manage token usage:**

### Option 1: Global install + enable/disable as needed

Install both plugins globally, then disable when not actively using them:

```bash
/plugin disable analytics-toolkit    # When not working with R code
/plugin disable manuscript-tools     # When not preparing manuscripts
```

Re-enable when needed:

```bash
/plugin enable analytics-toolkit     # When working with R code
/plugin enable manuscript-tools      # When preparing manuscripts
```

### Option 2: Project-specific installation

Install plugins only in the projects where you need them. This prevents them from loading in unrelated work.

Even within a single research project, you may want to toggle between plugins depending on your task—analytics tools for data analysis, manuscript tools for writing. You won't typically need both active at the same time.

---

## Semantic Scholar API Key (Optional)

The manuscript tools search Semantic Scholar to resolve citations and retrieve paper metadata. This works out of the box without any setup — unauthenticated requests share a pool of 1,000 requests per second across all users, which is more than enough for typical use.

However, if you plan to curate citations across many documents or run the tools frequently, you may want your own API key. An API key gives you a dedicated rate limit (1 request per second to start, with higher limits available) and ensures your requests are not affected by other users' traffic.

Getting a key is free and takes a few minutes:

1. Go to [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api)
2. Scroll to the API key request form (or click "Request an API Key")
3. Fill in your name, email, and a brief description of your use case. The form will ask which endpoints you plan to use — this project uses:
   - `GET /graph/v1/paper/search` (keyword search)
   - `GET /graph/v1/paper/{paper_id}` (paper metadata and BibTeX)
4. You will receive your API key by email
5. Save the key to `~/.config/semantic-scholar-mcp/api_key`:

   ```bash
   mkdir -p ~/.config/semantic-scholar-mcp
   echo "YOUR_KEY_HERE" > ~/.config/semantic-scholar-mcp/api_key
   ```

The tools will pick up the key automatically on the next run. If no key is found, they fall back to unauthenticated access.

---

## 📖 Documentation

- **[Analytics Toolkit Docs](./analytics-toolkit/README.md)** — R workflow details
- **[Manuscript Tools Docs](./manuscript-tools/README.md)** — Citation and formatting guides

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details

---

## 🤝 Contributing

Issues and pull requests welcome. Each plugin maintains its own scope:

- **analytics-toolkit** — R-specific and language-agnostic workflows
- **manuscript-tools** — Citation and manuscript formatting

---

## 💬 Questions?

Refer to individual plugin READMEs or open an issue. For integration questions, check the MCP documentation in [manuscript-tools/mcps](./manuscript-tools/mcps).

```

```
