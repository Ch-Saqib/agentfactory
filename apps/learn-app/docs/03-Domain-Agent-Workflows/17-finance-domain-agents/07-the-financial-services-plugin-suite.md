---
sidebar_position: 7
title: "The Financial Services Plugin Suite"
description: "Navigate the financial-services-plugins ecosystem — 41 skills, 38 commands, 11 MCP integrations across 7 plugins — understanding the mandatory install order, shared MCP architecture, and end-to-end workflows for investment banking, equity research, private equity, and wealth management"
keywords:
  [
    "financial-services-plugins",
    "plugin suite",
    "MCP connectors",
    "financial-analysis",
    "investment-banking",
    "equity-research",
    "private-equity",
    "wealth-management",
    "LSEG",
    "S&P Global",
    "Cowork plugins",
    "LBO model",
    "IC memo",
    "comps",
    "DCF",
  ]
chapter: 17
lesson: 7
duration_minutes: 40

# HIDDEN SKILLS METADATA
skills:
  - name: "Navigate a Multi-Plugin Ecosystem"
    proficiency_level: "B1"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Digital Literacy"
    measurable_at_this_level: "Student can describe the financial-services-plugins architecture (core plus add-ons with shared MCP connectors), explain the mandatory install order, and select the correct plugin for a given finance workflow"

  - name: "Configure End-to-End Financial Workflows"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can map a professional finance task (earnings update, deal screening, client review) to the correct plugin, command, and MCP data sources, and describe the workflow from data ingestion to deliverable"

  - name: "Evaluate Plugin Customisation Strategies"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Analyze"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can identify which plugin components to customise for a specific firm (connectors, templates, terminology, workflows) and explain the trade-offs between using default plugins and building firm-specific extensions"

learning_objectives:
  - objective: "Explain the shared-core architecture of the financial-services-plugins suite and apply the mandatory install order when setting up the ecosystem"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Student can describe why all MCP connectors live in the core plugin, explain what happens if an add-on is installed without the core, and write the correct install sequence for a given combination of plugins"

  - objective: "Map professional finance workflows to the correct plugin, commands, and MCP data sources"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Given a finance task description, student can identify which plugin handles it, which commands to use, and which MCP providers supply the underlying data"

  - objective: "Analyse the customisation surface of the plugin suite and identify firm-specific adaptations"
    proficiency_level: "B1"
    bloom_level: "Analyze"
    assessment_method: "Student can list the five customisation dimensions (connectors, firm context, templates, workflows, new plugins) and explain which dimension applies to a given firm requirement"

cognitive_load:
  new_concepts: 7
  concepts_list:
    - "Shared-core plugin architecture with mandatory install order"
    - "11 MCP data connectors centralised in the core plugin"
    - "Five end-to-end workflow patterns (Research to Report, Spreadsheet Analysis, Financial Modelling, Deal Materials, Portfolio to Presentation)"
    - "Core plugin commands (/comps, /dcf, /lbo, /one-pager, /ppt-template)"
    - "Four function-specific add-on plugins with domain commands"
    - "Two partner-built plugins (LSEG, S&P Global)"
    - "Five customisation dimensions for firm adaptation"
  assessment: "7 concepts at B1 level — at the upper end of the 7-10 cognitive limit for this tier. The concepts are structured hierarchically (architecture → plugins → customisation) which reduces effective load through progressive disclosure."

differentiation:
  extension_for_advanced: "Choose a finance workflow you perform regularly. Map it to the plugin suite: which plugin handles it, which commands would you use, which MCP providers supply the data, and what firm-specific customisations would you need? Write a one-page integration plan."
  remedial_for_struggling: "Focus on the core architecture: one core plugin with shared data connections, four add-on plugins for different finance functions, mandatory install order. For each add-on, write one sentence describing its primary use case."

teaching_guide:
  lesson_type: "core"
  session_group: 3
  session_title: "Plugin Ecosystem"
  key_points:
    - "The core plugin centralises all 11 MCP data connectors — configure once, share across all add-ons"
    - "Install order is mandatory: core first, then add-ons. Add-ons depend on the core's shared connectors and financial modelling commands"
    - "Each add-on plugin targets a specific finance function: investment banking (deal materials), equity research (coverage reports), private equity (deal sourcing and IC memos), wealth management (client reviews)"
    - "The plugins are starting points — the real value comes from customising connectors, templates, terminology, and workflows for your firm"
  misconceptions:
    - "Students may think each plugin has its own data connections — all MCP connectors are in the core plugin and shared automatically"
    - "Students may assume the plugins produce final deliverables — they produce structured drafts that require professional judgment and review"
    - "Students may think partner plugins (LSEG, S&P Global) are optional extras — they provide proprietary data that significantly extends capability"
  discussion_prompts:
    - "Which of the five end-to-end workflows would save the most time in your current role? What would you need to customise to make it work for your firm?"
    - "The plugins produce drafts, not finals. Where in your workflow is professional judgment most critical — and where would you be comfortable with less review?"
  teaching_tips:
    - "Walk through the MCP connector table — students need to see the breadth of data sources before understanding individual plugin workflows"
    - "Use the LBO concept box as a concrete anchor — even students outside PE benefit from understanding how the financial modelling commands work"
  assessment_checks:
    - question: "Why must the core plugin be installed first?"
      expected_response: "Because all 11 MCP data connectors are centralised in the core plugin. Add-on plugins inherit these connections — without the core, add-ons have no data sources to work with."
    - question: "Name the five end-to-end workflow patterns the suite enables."
      expected_response: "Research to Report, Spreadsheet Analysis, Financial Modelling, Deal Materials, and Portfolio to Presentation."
    - question: "What are the five dimensions for customising the plugins for your firm?"
      expected_response: "Swap connectors (point at your data providers), add firm context (terminology and processes), bring your templates (branded PowerPoint), adjust workflows (match your team's process), and build new plugins (extend the collection)."
---

# The Financial Services Plugin Suite

In Lesson 6, you explored how Claude in Excel's Agent Skills handle individual finance tasks within a single workbook. Now you will see what happens when those capabilities scale into a coordinated ecosystem — 41 skills, 38 commands, and 11 MCP data integrations working together across investment banking, equity research, private equity, and wealth management.

The `anthropics/financial-services-plugins` suite is the largest specialist plugin collection available for Claude. It is not a single tool but an architecture: a core plugin that centralises all data connections, four function-specific add-on plugins built by Anthropic, and two partner-built plugins from LSEG and S&P Global. Understanding this architecture — what connects where, what depends on what, and how to make it yours — is the difference between installing software and building a professional workflow.

## The Shared-Core Architecture

Every plugin in the suite shares one architectural decision: all MCP data connectors live in the core plugin. Install the core once, configure your data connections once, and every add-on you install afterwards inherits them automatically.

This matters because financial workflows pull data from multiple providers simultaneously. A comparable company analysis needs market data from FactSet, financial model data from Daloopa, and credit ratings from Moody's. If each plugin maintained its own connections, you would configure the same providers repeatedly and risk inconsistent credentials across plugins.

**Install order is mandatory.** The core plugin must be installed first; all add-ons depend on it.

```bash
claude plugin marketplace add anthropics/financial-services-plugins

# Install the core plugin FIRST — required
claude plugin install financial-analysis@financial-services-plugins

# Then add function-specific plugins
claude plugin install investment-banking@financial-services-plugins
claude plugin install equity-research@financial-services-plugins
claude plugin install private-equity@financial-services-plugins
claude plugin install wealth-management@financial-services-plugins
```

**Output:**

```
✓ financial-analysis@financial-services-plugins installed (core)
✓ investment-banking@financial-services-plugins installed (add-on)
✓ equity-research@financial-services-plugins installed (add-on)
✓ private-equity@financial-services-plugins installed (add-on)
✓ wealth-management@financial-services-plugins installed (add-on)
```

You can also install from `claude.com/plugins`.

## MCP Data Connectors

All eleven connectors are configured in the core plugin's `.mcp.json` and shared across the entire suite.

| Provider         | What It Provides                                        | MCP URL                                          |
| ---------------- | ------------------------------------------------------- | ------------------------------------------------ |
| **Daloopa**      | Automated financial model data extraction               | `https://mcp.daloopa.com/server/mcp`             |
| **Morningstar**  | Equity research, fund analysis, valuation data          | `https://mcp.morningstar.com/mcp`                |
| **S&P Global**   | Capital IQ financial data, credit ratings, ownership    | `https://kfinance.kensho.com/integrations/mcp`   |
| **FactSet**      | Market data, financial analytics, portfolio data        | `https://mcp.factset.com/mcp`                    |
| **Moody's**      | Credit ratings, fixed income analytics                  | `https://api.moodys.com/genai-ready-data/m1/mcp` |
| **MT Newswires** | Real-time financial news feeds                          | `https://vast-mcp.blueskyapi.com/mtnewswires`    |
| **Aiera**        | Earnings call transcripts, corporate event intelligence | `https://mcp-pub.aiera.com`                      |
| **LSEG**         | Market data, analytics                                  | `https://api.analytics.lseg.com/lfa/mcp`         |
| **PitchBook**    | Private company, VC, and PE deal data                   | `https://premium.mcp.pitchbook.com/mcp`          |
| **Chronograph**  | Private markets portfolio monitoring                    | `https://ai.chronograph.pe/mcp`                  |
| **Egnyte**       | Document management for deal files                      | `https://mcp-server.egnyte.com/mcp`              |

MCP access requires a subscription or API key from each provider. You configure credentials once in the core plugin; every add-on uses them automatically.

## End-to-End Workflows

The plugins are designed for complete workflows — not point tools. Five patterns span the suite.

| Workflow                      | What It Does                                                                                           | Plugins Involved          |
| ----------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------- |
| **Research to Report**        | Pull real-time data, analyse earnings, generate publication-ready research reports                     | equity-research + core    |
| **Spreadsheet Analysis**      | Build comps, DCF models, and LBO models as Excel workbooks with live formulas                          | core (financial-analysis) |
| **Financial Modelling**       | Populate three-statement models from SEC filings, cross-check against peer data, stress-test scenarios | core + equity-research    |
| **Deal Materials**            | Draft CIMs, teasers, process letters, and pitch deck slides in firm-branded templates                  | investment-banking + core |
| **Portfolio to Presentation** | Screen opportunities, run diligence, build IC memos, track portfolio KPIs                              | private-equity + core     |

Each workflow moves from raw data to professional deliverable in a single session. The deliverables are structured drafts that require professional review — the plugins handle the data assembly and formatting; you provide the judgment.

## Plugin 1: financial-analysis (Core)

The core plugin provides the financial modelling foundation and all shared MCP connectors.

| Command                | What It Produces                                                                               |
| ---------------------- | ---------------------------------------------------------------------------------------------- |
| `/comps [company]`     | Comparable company analysis as Excel workbook — peer group, multiples, implied valuation range |
| `/dcf [company]`       | DCF valuation model with sensitivity tables (WACC x terminal growth rate)                      |
| `/lbo [company]`       | LBO model with entry/exit scenarios, debt schedule, and returns summary                        |
| `/one-pager [company]` | One-page company profile in the firm's PowerPoint template                                     |
| `/ppt-template`        | Register the firm's branded PowerPoint template for all deck outputs                           |

The `/comps` command produces a fully formatted Excel workbook: peer group table with LTM financials from connected MCP providers, enterprise value calculations, EV/EBITDA and EV/Revenue multiples, statistical summary (median, 25th and 75th percentile), and the subject company with implied valuation range. Blue input cells, black formula cells, green output cells — the Wall Street colour-coding convention built in.

The `/dcf` command produces a three-stage DCF: detailed projection period, normalisation year, terminal value using both Gordon Growth Model and exit multiple, WACC calculation with beta sourced from the connected data provider, and a two-way sensitivity table. The model is a working Excel file with live formulas — change an assumption and the sensitivity table updates automatically.

:::info What Is an LBO Model?
A Leveraged Buyout (LBO) model values the acquisition of a company using significant borrowed money — typically 50-70% debt. The acquired company's own cash flows service the debt. Private equity firms use LBOs to acquire companies, improve them over 3-7 years, and sell at a profit.

**Why debt amplifies returns:** Buy a company for $100M using $30M equity and $70M debt. Sell for $130M five years later after repaying debt from operating cash flows, leaving $60M net. Equity return: $60M on $30M invested = 100% total return (15% IRR). Without leverage, the same investment yields 30% total. Debt amplification works in both directions — underperformance can wipe out equity entirely.

**Key metrics:** Entry multiple (EV/EBITDA at purchase), exit multiple (EV/EBITDA at sale), IRR (annualised equity return, target 20-25%), MOIC (total proceeds / equity invested, target 3-5x over 5 years).
:::

The `/ppt-template` command registers the firm's branded PowerPoint template. After registration, every deck output — one-pagers, IC memos, earnings summaries — uses the firm's template with the correct logo, fonts, colour scheme, and footer.

## Plugin 2: investment-banking

This plugin handles the full lifecycle of sell-side and buy-side advisory work.

| Capability         | What It Produces                                                                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **CIM**            | Confidential Information Memorandum — executive summary, business overview, financials, management team, competitive positioning, transaction rationale |
| **Teaser**         | Blind profile for initial buyer outreach, anonymous until NDA signed                                                                                    |
| **Process letter** | Bid process documentation for structured auctions                                                                                                       |
| **Buyer list**     | Strategic and financial buyer identification using PitchBook data — screened by sector, geography, size, acquisition history                            |
| **Merger model**   | Accretion/dilution analysis and synergy modelling                                                                                                       |
| **Strip profile**  | Rapid company summary for pitch books                                                                                                                   |
| **Deal tracking**  | Milestone tracking — NDA status, management presentations, bid rounds, exclusivity                                                                      |

The `/cim` and `/one-pager` commands produce documents using the firm's registered template. Register once with `/ppt-template`; every deal document matches house style.

### Exercise A: Investment Banking Workflow

**Time:** 30 minutes. **Requires:** Cowork with the investment-banking plugin installed (financial-analysis core first).

1. Choose a publicly listed company in a sector you know. Run `/one-pager [company]`. Review the output: is the business description accurate? Are the financials correct? Note which data came from MCP providers and which required manual input.

2. Draft a buyer list: _"Identify likely strategic acquirers and financial buyers for [company]. Strategic: companies in adjacent industries with acquisition history and balance sheet capacity. Financial: PE firms with relevant sector thesis and fund size appropriate for this company's EV."_

3. Draft a teaser: _"Draft a one-paragraph teaser introduction for [company] that could be sent to a PE buyer unfamiliar with the sector. Emphasise financial characteristics rather than technical ones."_

4. Probe risk: _"What are the most important risk factors a buyer's counsel would investigate in due diligence for a company in this sector?"_

## Plugin 3: equity-research

This plugin targets sell-side equity research workflows — from post-earnings updates to initiating coverage.

| Capability              | What It Produces                                                                                     |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| **Earnings update**     | Post-earnings note — actual vs consensus, beats/misses, model update, structured note                |
| **Initiating coverage** | First-time coverage report — investment thesis (bull/base/bear), comps, DCF, key risks, price target |
| **Thesis maintenance**  | Tracks key assumptions and flags when events challenge them                                          |
| **Morning note**        | Daily market summary from MT Newswires and Aiera transcripts                                         |
| **Screening**           | New idea generation based on valuation, momentum, or fundamental criteria                            |

The `/earnings [company] [quarter]` command runs the full post-earnings workflow. It pulls actual results from connected MCP providers, compares against consensus, identifies beats and misses, updates the financial model, and produces a structured note.

:::info What Is a Sell-Side vs. Buy-Side Analyst?
**Sell-side analysts** work for investment banks and brokerage firms. They publish equity research reports with buy/hold/sell ratings and price targets for institutional investor clients.

**Buy-side analysts** work for institutional investors — asset managers, hedge funds, pension funds. They analyse to support their own firm's investment decisions and do not publish externally.

The equity-research plugin follows sell-side conventions: consensus estimates comparison, price target methodology, and publication-ready note format.
:::

### Exercise B: Equity Research Workflow

**Time:** 35 minutes. **Requires:** Cowork with the equity-research plugin installed.

1. Choose a company that reported earnings within the last month. Run `/earnings [company] [quarter]`. Review the note structure: does it cover beats/misses, model updates, and forward guidance?

2. Identify the surprise: _"Which line item was most surprising relative to consensus — positive or negative for the forward thesis?"_

3. Draft the lead: _"Draft the opening paragraph of an earnings update for institutional clients. Informative but concise — the client is reading 12 notes this morning."_

4. Test the thesis: _"What are the three key assumptions for consensus revenue over the next two years? How confident should I be in each?"_

5. Challenge yourself: _"If I were a sceptical portfolio manager, what is the one question most uncomfortable for the analyst to answer?"_

## Plugin 4: private-equity

This plugin covers the PE deal lifecycle from sourcing through portfolio monitoring.

| Capability               | What It Produces                                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------------------------- |
| **Deal sourcing**        | Scored opportunity list from PitchBook and Chronograph by sector, geography, revenue, growth, ownership |
| **Diligence checklist**  | Structured checklist — commercial, financial, legal, operational, management workstreams                |
| **Unit economics**       | Cohort analysis, LTV/CAC, payback period for software/consumer businesses                               |
| **Returns analysis**     | IRR and MOIC modelling across entry/exit multiple scenarios                                             |
| **IC memo**              | Investment committee memorandum — the formal recommendation document                                    |
| **Portfolio monitoring** | KPI dashboard — revenue, EBITDA, cash, headcount across portfolio companies                             |

:::info What Is an IC Memo?
An IC (Investment Committee) memo is the formal document presented when recommending a new investment to the firm's decision-making body. Standard sections: (1) Executive summary with recommendation. (2) Company and market overview. (3) Investment thesis — why this, why now. (4) Financial performance and projections. (5) Valuation. (6) Return analysis — base, bull, bear case. (7) Key risks and mitigants. (8) Proposed deal structure.

The plugin produces the structure and populates data sections from connected sources. The investment thesis, risk assessment, and recommendation require professional judgment — the plugin creates the framework, not the conclusion.
:::

### Exercise C: Private Equity Workflow

**Time:** 40 minutes. **Requires:** Cowork with the private-equity plugin installed. PitchBook access needed for sourcing; IC memo can use manually provided data.

1. Run `/source [criteria]` — specify sector, revenue range ($20M-$100M), geography, and ownership type. Review the returned list: are companies genuinely in-criteria?

2. Pick one company. Ask: _"What are the three most important diligence questions for the first two weeks? Focus on deal-killers, not price-refiners."_

3. Draft a one-paragraph investment thesis as if presenting to the IC. Include: why this company, why now, value creation plan, and exit path.

4. Model returns: _"Assume $50M entry EV at 7x EBITDA, 60% debt, 5-year hold, EBITDA growing 15% per year. At exit multiples of 7x and 8x, what is the IRR and MOIC?"_ Verify the arithmetic manually.

5. Stress-test: _"What are the three most common reasons PE-backed companies in this sector underperform the entry thesis? How would I test for each in diligence?"_

## Plugin 5: wealth-management

This plugin handles the adviser's client-facing workflow — from meeting preparation through tax optimisation.

| Capability              | What It Produces                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Client meeting prep** | Pre-meeting brief — performance summary, allocation drift, recent news, tax-loss opportunities, agenda items |
| **Financial planning**  | Goal-based analysis — retirement projections, college funding, estate planning with scenario modelling       |
| **Rebalancing**         | Drift analysis, trade recommendations, IPS constraint check before any trade                                 |
| **Client reporting**    | Quarterly and annual performance reports in the adviser's branded template                                   |
| **Tax-loss harvesting** | Positions with unrealised losses, offset analysis, wash-sale rule compliance                                 |

### Exercise D: Wealth Management Workflow

**Time:** 30 minutes. **Requires:** Cowork with the wealth-management plugin installed. Can use hypothetical client data.

1. Create a hypothetical client: age 58, retired executive, $2M portfolio (60% equities, 30% bonds, 10% alternatives), goal of $120K/year income for 30 years, constraint of no tobacco or weapons companies.

2. Test alignment: _"Does this allocation align with the client's income objectives and risk tolerance? What is the probability of portfolio survival over 30 years at this withdrawal rate?"_

3. Test constraints: _"Which positions in a standard 60/30/10 allocation would violate the ESG constraint? What replacements maintain sector allocation while satisfying the constraint?"_

4. Prepare the meeting: _"Draft a pre-meeting note for a quarterly review. Include performance context, three topics to raise proactively, and two questions to check whether objectives have changed."_

5. Handle the call: _"The client wants to move 20% to cash due to volatility. How do I respond without being dismissive — and what must I document for fiduciary compliance?"_

## Partner-Built Plugins

Two additional plugins are built and maintained by data partners, bringing proprietary data directly into Claude workflows.

**LSEG Plugin** — prices bonds, analyses yield curves, evaluates FX carry trades, values options, and builds macro dashboards using LSEG financial data. Eight commands covering fixed income, FX, equities, and macro analysis.

```bash
claude plugin install lseg@financial-services-plugins
```

**S&P Global Plugin** — generates company tearsheets, earnings previews, and funding digests powered by S&P Capital IQ data. Supports multiple audience types: equity research, IB/M&A, corporate development, and sales.

```bash
claude plugin install spglobal@financial-services-plugins
```

## Making the Plugins Yours

The plugins are starting points, not finished products. The real power comes from customisation across five dimensions.

| Dimension             | What You Change                                        | Example                                                             |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------------------------- |
| **Swap connectors**   | Edit `.mcp.json` to point at your data providers       | Replace FactSet with Bloomberg if that is your firm's provider      |
| **Add firm context**  | Update skill files with your terminology and processes | Change "comps" to "trading comps" if that is your firm's convention |
| **Bring templates**   | Register your branded PowerPoint with `/ppt-template`  | Every deck output matches your style guide                          |
| **Adjust workflows**  | Modify skill instructions to match your team's process | Add an ESG section to IC memo if your firm requires it              |
| **Build new plugins** | Follow the standard structure to create new plugins    | Build a compliance plugin for regulatory reporting workflows        |

The plugin skill files are plain Markdown — readable and editable without technical knowledge. Fork the repository, make your changes, and your firm's version of the suite reflects how your team actually works.

## Try With AI

Use these prompts in Cowork or your preferred AI assistant to explore the plugin ecosystem.

### Prompt 1: Plugin Selection

```
I work in [YOUR FINANCE FUNCTION — e.g., equity research,
investment banking, private equity, wealth management].

My most time-consuming weekly task is [DESCRIBE THE TASK].

Based on the financial-services-plugins suite:
1. Which plugin handles this task?
2. Which specific command would I use?
3. Which MCP data providers would supply the underlying data?
4. What would the output look like — and what would I still need
   to do manually before the deliverable is client-ready?
```

**What you're learning:** Mapping real workflows to plugin capabilities requires understanding three layers: which plugin owns the function, which command executes it, and which MCP providers supply the data. This prompt practises all three layers with your actual work.

### Prompt 2: Customisation Planning

```
My firm has these specific requirements that differ from the
default plugin configuration:

1. We use [DATA PROVIDER] instead of [DEFAULT PROVIDER]
2. Our [DOCUMENT TYPE] requires a section on [ADDITIONAL TOPIC]
3. Our team calls [CONCEPT] by the name [FIRM TERM]

For each requirement:
- Which file in the plugin would I modify?
- What is the specific change?
- Are there any dependencies or side effects to consider?
```

**What you're learning:** Customising plugins means understanding their internal structure — which files control data connections, which control document templates, and which control terminology. This prompt practises reading the plugin architecture as a system you can modify, not a black box you accept as-is.

### Prompt 3: Plugin Integration Testing

```
I have configured three plugins for my finance workflow:
- [PLUGIN 1 — e.g., Comparable Company Analysis]
- [PLUGIN 2 — e.g., Earnings Analysis]
- [PLUGIN 3 — e.g., Initiating Coverage Report]

These plugins need to work together on a single deliverable.

1. Map the data flow between these three plugins: what output
   from Plugin 1 becomes input to Plugin 2 or Plugin 3?
2. Identify any format mismatches — places where one plugin's
   output format does not match another plugin's expected input
3. Design a test scenario: give me a specific company and
   situation where I would invoke all three plugins in sequence,
   and describe what the final deliverable should look like
4. What is the most likely failure mode when these plugins
   interact, and how would I detect it before sending the
   deliverable to a client?
```

**What you're learning:** Individual plugins work in isolation; professional workflows require plugins to work together. The data flow mapping reveals where plugins connect and where they can break. Designing an integration test before relying on a multi-plugin workflow is the same discipline as testing a financial model before presenting it — the cost of finding errors before the client meeting is far lower than finding them during it.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 8: Cross-App Orchestration →](./08-cross-app-orchestration.md)
