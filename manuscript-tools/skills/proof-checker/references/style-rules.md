# Style Rules

## A. Terminology Consistency

### A.1 Capitalization

**Rule**: Capitalize when referring to a specific numbered element; lowercase when generic.

| Context | Correct | Incorrect |
|---|---|---|
| Specific reference | "Figure 1 shows..." | "figure 1 shows..." |
| Specific reference | "Table 3 reports..." | "table 3 reports..." |
| Specific reference | "Section 2 describes..." | "section 2 describes..." |
| Specific reference | "Equation 4 implies..." | "equation 4 implies..." |
| Specific reference | "Appendix B contains..." | "appendix B contains..." |
| Specific reference | "Panel A of Figure 2" | "panel A of figure 2" |
| Specific reference | "Column 3 of Table 1" | "column 3 of table 1" |
| Generic reference | "the figure above" | "the Figure above" |
| Generic reference | "in the following table" | "in the following Table" |
| Generic reference | "across all sections" | "across all Sections" |

**Detection**: Flag when "figure/table/section/equation" + digit appears in lowercase, or when generic usage appears capitalized.

### A.2 Dashes

| Type | Character | Use | Example |
|---|---|---|---|
| Hyphen | `-` | Compound modifiers | "well-known result" |
| En-dash | `--` (LaTeX) or `–` | Ranges, connections | "2010–2015", "cost–benefit" |
| Em-dash | `---` (LaTeX) or `—` | Parenthetical breaks | "the result—surprising as it was—held" |

**Detection**: Flag `-` used in number ranges (should be en-dash), double hyphen in Quarto (should be `–`), spaces around em-dashes (style choice but must be consistent).

### A.3 Percent

**Rule**: Pick one style and be consistent throughout the document.

| Style A | Style B |
|---|---|
| "50%" | "50 percent" |
| "a 10% increase" | "a 10 percent increase" |

**Detection**: Flag mixed usage. In AER, "percent" (spelled out) is more common in prose; "%" is standard in tables and figures.

### A.4 Abbreviations

**Rule**: Pick one style and be consistent.

| Style A | Style B |
|---|---|
| "e.g.," | "for example," |
| "i.e.," | "that is," |
| "cf." | "compare" |
| "et al." | (always abbreviated) |
| "vs." | "versus" |

**Detection**: Flag mixed usage within the same document. Note: "et al." is always abbreviated (never "and others" after first use of full author list).

## B. Acronym Validation

### B.1 First-Use Definition Rule

**Rule**: At first use, write the full term followed by the abbreviation in parentheses. Use the abbreviation only thereafter.

```
CORRECT:  "We use a randomized controlled trial (RCT) to evaluate...
           The RCT was conducted in..."

INCORRECT: "We use an RCT to evaluate..."  (undefined at first use)
INCORRECT: "We use a randomized controlled trial (RCT)...
            The randomized controlled trial shows..."  (redundant after definition)
```

**Detection algorithm**:
1. Find all uppercase sequences of 2+ letters that appear to be acronyms: `\b[A-Z]{2,}\b`
2. Exclude common non-acronym uppercase words: "I", "A", section headers, proper nouns at start of sentences
3. For each acronym, find first occurrence and check if it's preceded by a parenthetical definition pattern: `full term (ACRONYM)`
4. Flag first use without definition as WARNING

### B.2 Common Economics Acronyms

These should all follow the first-use definition rule:

| Acronym | Full term |
|---|---|
| ATE | average treatment effect |
| ATT | average treatment effect on the treated |
| ITT | intention-to-treat |
| IV | instrumental variables |
| OLS | ordinary least squares |
| RCT | randomized controlled trial |
| RDD | regression discontinuity design |
| DID / DiD | difference-in-differences |
| FE | fixed effects |
| RE | random effects |
| 2SLS | two-stage least squares |
| GMM | generalized method of moments |
| LATE | local average treatment effect |
| TOT | treatment on the treated |
| SUTVA | stable unit treatment value assumption |
| CIA | conditional independence assumption |
| MTE | marginal treatment effect |
| MLE | maximum likelihood estimation |
| SE | standard error |
| FDR | false discovery rate |
| FWER | family-wise error rate |
| GDP | gross domestic product |
| CPI | consumer price index |
| PPP | purchasing power parity |
| IRB | institutional review board |
| PAP | pre-analysis plan |

### B.3 Defined-but-Never-Used Detection

**Rule**: If an acronym is defined with "full term (ABBREV)" but the abbreviation never appears again, the definition is unnecessary. Use the full term directly instead.

**Detection**: For each defined acronym, count post-definition uses. If count == 0, flag as WARNING.

## C. Number Formatting

### C.1 Spell Out vs Digits

| Context | Rule | Example |
|---|---|---|
| One through ten in prose | Spell out | "three treatment arms" |
| 11 and above in prose | Digits | "across 15 countries" |
| Starting a sentence | Always spell out | "Twelve participants..." |
| Statistical values | Always digits | "coefficient of 0.23" |
| Numbers with units | Always digits | "5 kilometers", "$200" |
| Percentages | Always digits | "7 percent" or "7%" |
| Sample sizes | Always digits | "N = 5,000" |
| Years | Always digits | "in 2015" |
| Ranges | Always digits | "3–5 years" |
| Adjacent mixed | Consistent within clause | "between 8 and 12 cities" (not "eight and 12") |

**Detection**: Flag numbers one through ten written as digits in running prose (not tables, not statistical values). Flag sentences starting with digits.

### C.2 Thousands Separator

**Rule**: Use commas for numbers >= 1,000 in both prose and tables. Exception: years (2015 not 2,015).

**Detection**: Flag four+ digit numbers without commas that aren't years (1000–2099 range check).

### C.3 Consistent Decimal Places

**Rule**: Within the same context (e.g., a paragraph discussing related estimates, or a column in a table), use consistent decimal places.

**Detection**: In a sequence of related numbers (same sentence or paragraph), flag inconsistent decimal places: "0.23, 0.145, and 0.3" should be "0.230, 0.145, and 0.300" or similar.

## D. Prose Quality

### D.1 Sentence Length

**Rule**: Flag sentences longer than 40 words. Academic writing benefits from concise sentences; long sentences often contain multiple ideas that should be split.

**Detection**: Split on sentence boundaries (`.`, `?`, `!` followed by space and capital letter). Count words. Flag if > 40.

**Exception**: Sentences with lists, quotations, or formal definitions may legitimately be longer.

### D.2 Hedging Density

**Rule**: Flag paragraphs with more than 3 hedging words/phrases.

**Hedging words**: may, might, could, would, should, possibly, perhaps, suggests, appears, seems, likely, unlikely, somewhat, relatively, arguably, tends to, it is possible that, one might argue

**Detection**: Count hedging words per paragraph. Flag if count > 3 per paragraph.

**Note**: Methods sections legitimately use "could" and "would" in conditional statements; weight these less heavily.

### D.3 Passive Voice Density

**Rule**: Flag sections (excluding Methods) where more than 50% of sentences use passive voice.

**Passive voice indicators**: "is/was/are/were/been/being" + past participle (word ending in -ed or irregular past participle)

Common patterns:
- "is estimated" → "we estimate"
- "was conducted" → "we conducted"
- "are reported" → "we report" / "Table X reports"
- "were assigned" → "we assigned" / "the program assigned"

**Detection**: Estimate passive voice per sentence using regex for be-verb + past participle patterns. Flag sections with > 50% passive (excluding Methods/Data sections where passive is conventional).

### D.4 Undefined Technical Terms

**Rule**: Technical terms used in the introduction or abstract should be briefly explained or be standard knowledge for the target audience.

**Common terms that need no definition** for AER audience: regression, fixed effects, instrumental variables, difference-in-differences, standard errors, confidence intervals, p-value, treatment/control

**Terms that should be defined**: domain-specific jargon, custom variable names, country/program-specific abbreviations, novel methodological terms
