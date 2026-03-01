# Chapter 17: Initial Research — Anthropic Finance Offerings

**Date**: 2026-03-01
**Status**: Initial research complete
**Sources verified**: 9 primary sources (see bottom)

---

## 1. Governing Artifact Summary

`Chapter17_Finance_Domain_Agents.md` is a ~1,780-line document in three parts:

| Part                             | Scope                                                  | Lines | Exercises           |
| -------------------------------- | ------------------------------------------------------ | ----- | ------------------- |
| **One**: Claude in Excel         | Standalone add-in: 4 general skills + 6 Agent Skills   | ~720  | 1–10 (numbered)     |
| **Two**: Excel via Cowork        | Finance plugins, financial-services plugins, cross-app | ~580  | 11 + A–D (lettered) |
| **Three**: Enterprise Extensions | 11 custom SKILL.md extension areas                     | ~480  | 12–14 + Final       |

---

## 2. Anthropic's Actual Finance Offerings (Verified Feb/Mar 2026)

### 2.1 Claude in Excel (Standalone Add-in)

**Sources**: [Claude Help Center](https://support.claude.com/en/articles/12650343-use-claude-in-excel), [claude.com/claude-in-excel](https://claude.com/claude-in-excel), [Anthropic: Advancing Claude for Financial Services](https://www.anthropic.com/news/advancing-claude-for-financial-services)

#### Core Details

| Feature                | Verified Detail                                            | Source                     |
| ---------------------- | ---------------------------------------------------------- | -------------------------- |
| **What it is**         | Microsoft Excel add-in, sidebar interface                  | Help Center                |
| **Plans**              | **Pro, Max, Team, Enterprise** (beta)                      | Help Center                |
| **Models**             | Sonnet 4.6 and Opus 4.6 (switchable)                       | Help Center                |
| **Formats**            | .xlsx, .xlsm                                               | Help Center                |
| **Keyboard shortcuts** | Control+Option+C (Mac), Control+Alt+C (Windows)            | claude.com/claude-in-excel |
| **Installation**       | Microsoft AppSource marketplace or manifest XML deployment | Help Center                |
| **Data retention**     | Auto-deleted within 30 days                                | Help Center                |
| **Promo**              | Usage limits doubled through March 19, 2026                | Help Center                |

#### General Capabilities (Layer 1)

- Ask questions about workbooks with **cell-level citations**
- Update assumptions while preserving formula dependencies
- Debug errors (#REF!, #VALUE!, circular references) with root cause tracing
- Build new models or populate existing templates
- Navigate complex multi-tab workbooks
- Native Excel operations: pivot table editing, chart adjustments, conditional formatting (data bars), sort/filter, data validation, print area config

#### 6 Agent Skills (Layer 2 — Pre-built Financial Workflows)

Announced Oct 27, 2025 in [Advancing Claude for Financial Services](https://www.anthropic.com/news/advancing-claude-for-financial-services):

1. **Comparable Company Analysis** — valuation multiples, operating metrics, refreshable with updated data
2. **Discounted Cash Flow Model** — FCF projections, WACC calculations, scenario toggles, sensitivity tables
3. **Due Diligence Data Pack** — processes data room documents into structured Excel with financials, customer lists, contract terms
4. **Company Teaser** — condensed company overviews for pitch books and buyer lists
5. **Earnings Analysis** — quarterly transcripts extraction: metrics, guidance changes, management commentary
6. **Initiating Coverage Report** — industry analysis, company deep-dives, valuation frameworks

**Note**: The Help Center article does NOT use the term "Agent Skills." This terminology comes from the Anthropic blog announcement and press coverage (Geekflare, VentureBeat). The chapter's use of "Agent Skills" is consistent with Anthropic's blog terminology.

#### Data Connectors — Evolution Timeline

The connector set has evolved:

| Date                                 | Connectors Available                                                      | Source                                                                                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Oct 2025** (initial launch)        | Aiera, Third Bridge, Chronograph, Egnyte, LSEG, Moody's, MT Newswires (7) | [Anthropic blog](https://www.anthropic.com/news/advancing-claude-for-financial-services)                                                              |
| **Feb 17, 2026** (MCP support added) | S&P Global, LSEG, Daloopa, PitchBook, Moody's, FactSet (6 named)          | [Help Center](https://support.claude.com/en/articles/12650343-use-claude-in-excel), [Claude tweet](https://x.com/claudeai/status/2023817143096406246) |

**Critical finding**: "All connectors configured in your Claude settings are supported, including custom connectors." This means:

- Claude in Excel does NOT have "its own" separate connectors
- Any MCP connector enabled in Claude settings works in Excel automatically
- The financial-services-plugins MCP connectors (Morningstar, Aiera, etc.) would also work in Excel if configured
- The chapter's claim of 3 separate connectors (S&P Capital IQ, PitchBook, Morningstar) is **wrong** — it's the same shared connector ecosystem

#### Limitations

**Cannot do**: Data tables, macros, VBA
**Not recommended for**: Final client deliverables without review, audit-critical calculations without verification, replacing financial judgment, highly sensitive/regulated data without controls
**Missing enterprise features**: Custom data retention settings, enterprise audit logs, compliance API integration
**No chat history**: Conversations don't persist between sessions

#### Security — Prompt Injection Risks

**Important for chapter**: Help Center explicitly warns about prompt injection in spreadsheets from untrusted sources. Malicious instructions in cells/formulas/comments can trick Claude into:

- Extracting sensitive information via formulas or web searches
- Modifying critical financial records
- Performing destructive actions without verification

**User protections**: Confirmation pop-ups for external data fetching (WEBSERVICE, STOCKHISTORY), imports, dynamic references, command execution, file system access.

**Functions requiring approval**: WEBSERVICE, STOCKHISTORY, STOCKSERIES, TRANSLATE, CUBE\*, IMPORTDATA, IMPORTXML, IMPORTHTML, INDIRECT, DDE, CALL, EVALUATE, FORMULA, IMAGE, FILES, DIRECTORY, RTD

### 2.2 knowledge-work-plugins/finance (Corporate Finance Plugin)

**Source**: [GitHub](https://github.com/anthropics/knowledge-work-plugins/tree/main/finance)

**Audience**: Corporate FP&A teams, controllers, accounting managers, finance business partners, internal audit teams.

**5 Commands**:

- `/journal-entry [type] [period]`
- `/reconciliation [account] [period]`
- `/income-statement [period-type] [period]`
- `/variance-analysis [area] [period-vs-period]`
- `/sox-testing [process] [period]`

**6 Skills** (auto-triggered):

- journal-entry-prep
- reconciliation
- financial-statements
- variance-analysis
- close-management
- audit-support

**Installation**: `claude plugins add knowledge-work-plugins/finance`

### 2.3 CONNECTORS.md + Broader Connector Ecosystem

**Sources**: [CONNECTORS.md](https://github.com/anthropics/knowledge-work-plugins/blob/main/finance/CONNECTORS.md), [claude.com/connectors](https://claude.com/connectors), [Cowork connectors guide](https://pluginsforcowork.com/guides/cowork-connectors/), [NetSuite MCP](https://www.netsuite.com/portal/products/artificial-intelligence-ai/mcp-server.shtml)

**Important distinction**: CONNECTORS.md shows what's **pre-configured in the plugin's `.mcp.json`** — NOT what MCP servers exist globally. The `~~category` placeholder system is designed so users plug in whatever MCP server they have.

#### What the plugin pre-configures (CONNECTORS.md)

| Category             | Placeholder        |  Pre-configured?   | Included Servers                  | Other Options                   |
| -------------------- | ------------------ | :----------------: | --------------------------------- | ------------------------------- |
| **Data warehouse**   | `~~data warehouse` |     Partial\*      | Snowflake*, Databricks*, BigQuery | Redshift, PostgreSQL            |
| **Email**            | `~~email`          |        Yes         | Microsoft 365                     | —                               |
| **Office suite**     | `~~office suite`   |        Yes         | Microsoft 365                     | —                               |
| **Chat**             | `~~chat`           |        Yes         | Slack                             | Microsoft Teams                 |
| **ERP / Accounting** | `~~erp`            | Not pre-configured | —                                 | NetSuite, SAP, QuickBooks, Xero |
| **Analytics / BI**   | `~~analytics`      | Not pre-configured | —                                 | Tableau, Looker, Power BI       |

`*` = Listed but MCP URL not yet populated in `.mcp.json`

#### What exists in the broader Cowork connector ecosystem

| Category           | Available Connectors (verified)                                                                             | Source                                                                                                                                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Data warehouse** | Snowflake, Databricks, BigQuery                                                                             | [Cowork connectors](https://pluginsforcowork.com/guides/cowork-connectors/)                                                                                                                                |
| **ERP**            | NetSuite (Oracle-built MCP server, live)                                                                    | [NetSuite MCP](https://www.netsuite.com/portal/products/artificial-intelligence-ai/mcp-server.shtml), [Oracle blog](https://blogs.oracle.com/developers/talking-to-your-erp-netsuite-meets-claude-via-mcp) |
| **Financial data** | FactSet, S&P Global, LSEG, Daloopa, PitchBook, Morningstar, Moody's, MT Newswires, Aiera, Chronograph, MSCI | [financial-services-plugins](https://github.com/anthropics/financial-services-plugins), [Anthropic blog](https://claude.com/blog/cowork-plugins-finance)                                                   |
| **Document mgmt**  | Box, Egnyte                                                                                                 | [Cowork connectors](https://pluginsforcowork.com/guides/cowork-connectors/)                                                                                                                                |
| **Analytics**      | Amplitude, Hex                                                                                              | [Cowork connectors](https://pluginsforcowork.com/guides/cowork-connectors/)                                                                                                                                |
| **Productivity**   | Notion, Microsoft 365, Slack, Jira, Asana, Linear, Monday, ClickUp                                          | [Cowork connectors](https://pluginsforcowork.com/guides/cowork-connectors/)                                                                                                                                |

**Key insights**:

1. The `~~category` placeholder system is **tool-agnostic by design** — plugins describe workflows in terms of categories, not specific products. Any MCP server in that category works.
2. **ERP MCP servers DO exist** (NetSuite's is built by Oracle) — they're just not pre-configured in this plugin's `.mcp.json`. Users add them.
3. **Data warehouse connectors exist** as first-class Cowork connectors (Snowflake, Databricks, BigQuery).
4. **BI connectors** (Tableau, Looker, Power BI) are NOT yet available as Cowork connectors — this remains a gap.
5. The chapter's month-end close workflows are **achievable** if the org configures the right connectors (e.g., NetSuite MCP + BigQuery). They're not out-of-the-box automated but not aspirational either — they require IT setup.

**Correction from initial research**: My earlier conclusion that "ERP connectors DON'T EXIST YET" was wrong. The CONNECTORS.md only shows what's pre-configured in one plugin, not the MCP ecosystem. NetSuite's MCP server is live and Oracle-built. The chapter's treatment is more accurate than I initially assessed.

### 2.4 financial-services-plugins (Investment Professional Suite)

**Source**: [GitHub](https://github.com/anthropics/financial-services-plugins)

**Scale**: 41 skills, 38 commands, 11 MCP integrations across 7 plugins (5 Anthropic + 2 partner-built)
**License**: Apache 2.0
**Stars**: 4.9k | Forks: 478

**Core Plugin** (install first): `financial-analysis`

- Commands: `/comps`, `/dcf`, `/lbo`, `/one-pager`, `/ppt-template`
- All 11 MCP connectors centralized here, shared across add-ons

**Add-on Plugins**:
| Plugin | Key Commands | Key Workflows |
|--------|-------------|---------------|
| investment-banking | CIM drafting, buyer lists, merger models, strip profiles, deal tracking | — |
| equity-research | `/earnings [company] [quarter]` | Earnings updates, initiating coverage, thesis maintenance, morning notes, screening |
| private-equity | `/source [criteria]`, `/ic-memo [project]` | Deal sourcing, diligence checklists, unit economics, returns analysis, portfolio monitoring |
| wealth-management | `/client-review [client]` | Client meeting prep, financial planning, rebalancing, tax-loss harvesting |

**Partner-Built Plugins**:
| Plugin | Built by | Capabilities |
|--------|----------|-------------|
| LSEG | LSEG | Bond pricing, yield curves, FX carry, options, macro dashboards (8 commands) |
| S&P Global | S&P Global | Company tearsheets, earnings previews, funding digests (multi-audience) |

**11 MCP Connectors** (all verified):

| Provider     | MCP URL                                          |
| ------------ | ------------------------------------------------ |
| Daloopa      | `https://mcp.daloopa.com/server/mcp`             |
| Morningstar  | `https://mcp.morningstar.com/mcp`                |
| S&P Global   | `https://kfinance.kensho.com/integrations/mcp`   |
| FactSet      | `https://mcp.factset.com/mcp`                    |
| Moody's      | `https://api.moodys.com/genai-ready-data/m1/mcp` |
| MT Newswires | `https://vast-mcp.blueskyapi.com/mtnewswires`    |
| Aiera        | `https://mcp-pub.aiera.com`                      |
| LSEG         | `https://api.analytics.lseg.com/lfa/mcp`         |
| PitchBook    | `https://premium.mcp.pitchbook.com/mcp`          |
| Chronograph  | `https://ai.chronograph.pe/mcp`                  |
| Egnyte       | `https://mcp-server.egnyte.com/mcp`              |

### 2.5 Cross-App Orchestration (Excel ↔ PowerPoint)

**Status**: Research preview, available on Cowork Team and Enterprise plans.
**What it does**: Agent carries context from Excel analysis to PowerPoint, building slides from model data without copy-paste.
**Verified by**: Multiple sources (TechCrunch, Anthropic webinar page, VentureBeat)

### 2.6 Plugin Architecture (Verified)

```
plugin-name/
├── .claude-plugin/plugin.json   # Manifest: name, description, version
├── .mcp.json                    # Tool connections (MCP server URLs)
├── CONNECTORS.md                # Documentation of connected tools
├── commands/                    # Slash commands (user-invoked, .md files)
│   └── [command].md
└── skills/                      # Domain knowledge (auto-triggered, .md files)
    └── [skill-name]/SKILL.md
```

Key architectural properties:

- **File-based**: All markdown + JSON, no code, no build steps
- **Tool-agnostic**: Uses `~~category` placeholders, not hardcoded products
- **Composable**: Core plugin provides connectors, add-ons inherit them
- **Customizable**: Edit SKILL.md, swap connectors, add firm templates

---

## 3. Chapter vs. Reality: Fact-Check Matrix

### Accurate (Confirmed)

| Chapter Claim                                              | Source                              |
| ---------------------------------------------------------- | ----------------------------------- |
| 6 Agent Skills in Claude in Excel                          | Help Center, Geekflare, VentureBeat |
| financial-services-plugins: 41 skills, 38 commands, 11 MCP | GitHub README                       |
| All 11 MCP connector URLs                                  | GitHub README (exact match)         |
| Plugin directory structure                                 | GitHub repos                        |
| knowledge-work-plugins/finance: 5 commands, 6 skills       | GitHub README                       |
| Cross-app Excel↔PPT orchestration                          | TechCrunch, Anthropic webinar       |
| LSEG and S&P Global as partner-built plugins               | GitHub README                       |
| Apache 2.0 license                                         | GitHub LICENSE                      |
| Install order: core first, then add-ons                    | GitHub README                       |

### Inaccurate / Needs Correction

| Issue                    | Chapter Says                                                                                            | Reality                                                                                                                                                                                           | Impact                                                                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Plan availability**    | "Max, Team, Enterprise"                                                                                 | **Pro, Max, Team, Enterprise** — Pro added Jan 24, 2026                                                                                                                                           | Minor — update one line                                                                                                                    |
| **Connector separation** | Claude in Excel has 3 own connectors (S&P Capital IQ, PitchBook, Morningstar) separate from Cowork's 11 | **Same MCP connectors** work in both — "any connectors previously enabled in Claude settings automatically work within Excel" ([Claude tweet](https://x.com/claudeai/status/2023817143096406246)) | **Major** — collapses the two-ecosystem narrative; needs rewrite to focus on scope difference (single-workbook vs multi-app orchestration) |
| **Model availability**   | Not mentioned                                                                                           | Users can switch between Sonnet 4.6 and Opus 4.6 in Excel                                                                                                                                         | Minor — worth mentioning for cost/quality tradeoff                                                                                         |

### Corrected from Initial Assessment

| Issue              | Initial Assessment         | Corrected Assessment                                                                                                                                                                                                                                        |
| ------------------ | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ERP automation** | "No ERP MCP servers exist" | **Wrong.** NetSuite MCP exists (Oracle-built, live). CONNECTORS.md only shows what's pre-configured in the plugin, not the ecosystem. Chapter is accurate — workflows require IT to configure the ERP connector.                                            |
| **Data warehouse** | "Only BigQuery works"      | **Partially wrong.** Snowflake, Databricks, BigQuery all exist as Cowork connectors. The `*` in CONNECTORS.md means not pre-configured in the plugin's `.mcp.json`, not "doesn't exist."                                                                    |
| **BI/Analytics**   | "Don't exist yet"          | **Correct but nuanced.** Tableau/Looker/Power BI are NOT available as Cowork connectors. Amplitude and Hex are available but serve different use cases. Waterfall charts CAN be generated by Claude in Excel directly — just not pulled from a BI platform. |

### Remaining Gap

| Feature                                            | Current State                      | Chapter Treatment                                              | Severity                                                                 |
| -------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| BI platform connectors (Tableau, Looker, Power BI) | Not available as Cowork connectors | Chapter mentions "connected to a BI tool" for waterfall charts | Low — Claude can generate waterfall charts in Excel without BI connector |

---

## 4. Design Implications for Chapter 17

### 4.1 Connector Narrative Must Be Rewritten

The chapter's core architectural distinction — "Claude in Excel has its own 3 connectors, Cowork has its own 11" — is wrong. The real distinction is:

- **Claude in Excel**: MCP connectors serve analysis within ONE workbook
- **Cowork plugins**: Same MCP connectors serve MULTI-APP workflows (Excel → PowerPoint → Word)

This is actually a BETTER pedagogical story: same connectors, different scope and orchestration.

### 4.2 The `~~category` Placeholder System Is Worth Teaching

The CONNECTORS.md reveals an elegant architectural pattern: plugins use `~~erp`, `~~data warehouse`, etc. as placeholders. The plugin doesn't care if you use NetSuite or SAP — it describes the WORKFLOW, IT configures the CONNECTION. This perfectly illustrates Ch 15's "division of responsibility" (knowledge worker owns SKILL.md, IT owns connectors) and should be highlighted in Ch 17.

### 4.3 ERP/BI Connector Nuance

The month-end close workflows ARE achievable but require IT to configure connectors:

- **ERP**: NetSuite MCP exists (Oracle-built). SAP doesn't have a first-party MCP server yet but CData offers one.
- **Data warehouse**: Snowflake, Databricks, BigQuery all available as Cowork connectors.
- **BI**: Tableau/Looker/Power BI NOT available. Waterfall charts can be generated in Excel directly.

The chapter should be explicit: "Your IT colleague configures the ERP and data warehouse connectors. Once connected, these workflows are automated. Without them, paste data or upload files — the plugin still works."

### 4.4 Additional Connector: MSCI

The [Anthropic blog post](https://claude.com/blog/cowork-plugins-finance) mentions MSCI as a new MCP connector ("proprietary index data"). Not listed in the financial-services-plugins repo's 11 connectors. Either newer than the repo or a separate Cowork connector. Worth adding.

### 4.5 Exercise Accessibility (unchanged)

Exercises 5–10 require data provider connections (S&P Capital IQ, PitchBook, etc.) that require paid subscriptions. The chapter needs:

- Alternative paths for users without these subscriptions
- Public dataset suggestions (SEC EDGAR, Yahoo Finance) for manual data input
- Clear "what you need" sections with cost/access implications

### 4.6 Knowledge Extraction Method Integration

Part 3 README promises every domain chapter applies the KEM (Ch 16). The chapter:

- References SKILL.md writing in Extensions (Part Three)
- Exercise 12 asks for a credit SKILL.md
- Final Exercise asks for an extension roadmap

Missing: An explicit Method A expert interview walkthrough applied to a finance domain expert. Consider adding a lesson that walks through "CFO interview → 5 questions → extraction → SKILL.md" using the Ch 16 framework.

---

## 5. Proposed Lesson Structure (13 files)

| #   | Title                                           | Source Content                                                           | Exercises   |
| --- | ----------------------------------------------- | ------------------------------------------------------------------------ | ----------- |
| 01  | The Assistant and the Agent                     | Excel-first distinction, comparison table, chapter roadmap               | —           |
| 02  | Understanding Workbooks You Didn't Build        | General intelligence: model comprehension, dependency tracing            | 1           |
| 03  | Scenarios, Errors, and Model Building           | Scenario testing, formula debugging, building from description           | 2, 3, 4     |
| 04  | The Six Agent Skills: Market Analysis           | Comps + DCF with concept boxes (WACC, EV, LTM)                           | 5, 6        |
| 05  | The Six Agent Skills: Deal and Research         | Due Diligence, Teaser, Earnings, Initiating Coverage                     | 7, 8, 9, 10 |
| 06  | From Assistant to Agent: Cowork Finance Plugins | Architecture shift, knowledge-work-plugins/finance, 5 commands, 6 skills | —           |
| 07  | The Financial Services Plugin Suite             | financial-services-plugins core + 4 add-ons + 2 partner, MCP connectors  | A, B, C, D  |
| 08  | Cross-App Orchestration                         | Excel↔PowerPoint workflow, why it's architecturally different            | 11          |
| 09  | Extracting Finance Domain Knowledge             | Method A/B applied to finance, SKILL.md from CFO interview               | —           |
| 10  | Enterprise Extensions: Risk and Compliance      | Extensions 1, 2, 6, 10 (credit, regulatory, IPS, portfolio)              | 12          |
| 11  | Enterprise Extensions: Operations and Strategy  | Extensions 3, 4, 5, 7, 8, 9, 11                                          | 13, 14      |
| 12  | Your Extension Roadmap and Chapter Summary      | Prioritisation, Final Exercise, full recap                               | Final       |
| 13  | Chapter Quiz                                    | Assessment                                                               | —           |

**Change from governing artifact**: Added Lesson 09 (KEM application) to fulfill the Part 3 README promise. This connects Ch 16's methodology to Ch 17's domain.

---

## 6. Open Design Decisions

| #   | Decision                    | Options                                                                                | Recommendation                                                  |
| --- | --------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| 1   | **Connector narrative fix** | (a) Rewrite as same-connectors-different-scope (b) Keep two-ecosystem framing          | (a) — it's more accurate AND better pedagogy                    |
| 2   | **ERP/BI gap**              | (a) Acknowledge explicitly (b) Write as future state (c) Use BigQuery path             | (a) — honesty builds trust; show paste-data fallback            |
| 3   | **Exercise accessibility**  | (a) Require Capital IQ (b) Add public data alternatives (c) Both with primary/fallback | (c) — primary path with connector, fallback with SEC EDGAR data |
| 4   | **KEM integration**         | (a) Dedicated lesson (b) Weave into extensions (c) Skip                                | (a) — new Lesson 09, fulfills Part 3 contract                   |
| 5   | **Pro plan mention**        | (a) Update to include Pro (b) Keep as-is for Agent Skills tier                         | (a) — help center says Pro has access                           |

---

## 7. Sources

1. [Claude Help Center: Use Claude in Excel](https://support.claude.com/en/articles/12650343-use-claude-in-excel)
2. [GitHub: anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins) — README
3. [GitHub: knowledge-work-plugins/finance](https://github.com/anthropics/knowledge-work-plugins/tree/main/finance) — README
4. [GitHub: knowledge-work-plugins/finance/CONNECTORS.md](https://github.com/anthropics/knowledge-work-plugins/blob/main/finance/CONNECTORS.md)
5. [Claude Help Center: Install financial services plugins](https://support.claude.com/en/articles/13851150-install-financial-services-plugins-for-cowork)
6. [Anthropic: Advancing Claude for Financial Services](https://www.anthropic.com/news/advancing-claude-for-financial-services)
7. [TechCrunch: Anthropic enterprise agents push (Feb 24, 2026)](https://techcrunch.com/2026/02/24/anthropic-launches-new-push-for-enterprise-agents-with-plugins-for-finance-engineering-and-design/)
8. [LSEG: Supercharge Claude's Financial Skills](https://www.lseg.com/en/insights/supercharge-claudes-financial-skills-with-lseg-data)
9. [Geekflare: Claude in Excel Financial Agent Skills](https://geekflare.com/news/claude-now-works-inside-excel-as-anthropic-expands-focus-on-financial-services/)
10. [Anthropic Blog: Cowork and plugins for finance](https://claude.com/blog/cowork-plugins-finance)
11. [Cowork Connectors Complete List](https://pluginsforcowork.com/guides/cowork-connectors/) — 38+ connectors by category
12. [NetSuite MCP Server](https://www.netsuite.com/portal/products/artificial-intelligence-ai/mcp-server.shtml) — Oracle-built ERP MCP
13. [Oracle Blog: NetSuite Meets Claude via MCP](https://blogs.oracle.com/developers/talking-to-your-erp-netsuite-meets-claude-via-mcp)
14. [Claude tweet: MCP connectors in Excel](https://x.com/claudeai/status/2023817143096406246) — confirms same connectors work in Excel and Cowork
15. [Claude Help Center: Connectors Directory](https://support.claude.com/en/articles/11724452-use-the-connectors-directory-to-extend-claude-s-capabilities)
16. [Claude Help Center: Pre-Built Connectors](https://support.claude.com/en/collections/17879307-pre-built-connectors)
