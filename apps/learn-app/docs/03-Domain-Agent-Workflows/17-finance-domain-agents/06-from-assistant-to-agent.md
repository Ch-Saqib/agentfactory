---
sidebar_position: 6
title: "From Assistant to Agent: Cowork Finance Plugins"
description: "Learn how the architecture shifts from Claude in Excel as an embedded assistant to Cowork as an orchestrating agent, explore the knowledge-work-plugins/finance plugin with its five commands and six skills, and understand the category placeholder system that separates workflow knowledge from connector configuration"
keywords:
  [
    "Cowork",
    "finance plugins",
    "knowledge-work-plugins",
    "orchestrating agent",
    "slash commands",
    "skills",
    "category placeholders",
    "month-end close",
    "MCP connectors",
    "cross-app orchestration",
    "plugin architecture",
    "GL reconciliation",
  ]
chapter: 17
lesson: 6
duration_minutes: 30

# HIDDEN SKILLS METADATA
skills:
  - name: "Plugin Architecture Understanding"
    proficiency_level: "B1"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Digital Content"
    measurable_at_this_level: "Student can explain the structural difference between an embedded assistant (Claude in Excel) and an orchestrating agent (Cowork), describe how skills and commands serve different purposes within a plugin, and identify the components of the plugin directory structure"

  - name: "Workflow Orchestration Comprehension"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can trace a multi-day finance workflow through the five plugin commands and explain which command serves which phase of a month-end close, and can describe how the close-management skill provides passive context throughout"

  - name: "Category Abstraction Understanding"
    proficiency_level: "B1"
    category: "Technical"
    bloom_level: "Analyze"
    digcomp_area: "Digital Content"
    measurable_at_this_level: "Student can explain the category placeholder system (~~erp, ~~data warehouse) and articulate why this design separates workflow knowledge from connector configuration, connecting it to Chapter 15's division of responsibility between knowledge workers and IT"

learning_objectives:
  - objective: "Explain the architectural difference between Claude as an embedded assistant in one application and Claude as an orchestrating agent across multiple applications, identifying why the same MCP connectors serve both contexts with different scope"
    proficiency_level: "B1"
    bloom_level: "Understand"
    assessment_method: "Student can describe the assistant-to-agent shift without conflating connectors with capabilities, and can explain what changes (orchestration scope) and what stays the same (the MCP connector set)"

  - objective: "Describe the knowledge-work-plugins/finance plugin structure, distinguishing between its five commands (explicitly invoked) and six skills (passively activated), and explain how they combine to support a multi-day month-end close workflow"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Given a close scenario (e.g., Day 3 bank reconciliation), student can identify which command to invoke, which skill activates passively, and what output to expect"

  - objective: "Analyse the category placeholder system in CONNECTORS.md and explain how it enables the same plugin to work with different enterprise systems without modifying the workflow definitions"
    proficiency_level: "B1"
    bloom_level: "Analyze"
    assessment_method: "Student can explain why the plugin uses ~~erp rather than 'NetSuite' and trace the division of responsibility: knowledge worker owns SKILL.md, IT owns connector configuration"

cognitive_load:
  new_concepts: 5
  concepts_list:
    - "Architecture shift from embedded assistant (single-app) to orchestrating agent (multi-app)"
    - "Skills (passive, auto-triggered) vs commands (active, explicitly invoked) in Cowork plugins"
    - "Plugin directory structure: plugin.json, .mcp.json, CONNECTORS.md, commands/, skills/"
    - "Category placeholder system (~~erp, ~~data warehouse) for tool-agnostic workflow design"
    - "Month-end close as a multi-day orchestrated workflow using commands and skills together"
  assessment: "5 concepts at B1 level -- within the 7-10 cognitive limit for this tier. Students have spent five lessons working inside Excel; this lesson introduces the Cowork layer as a scope expansion, not a replacement. The concepts build on each other: architecture shift sets up plugin structure, plugin structure introduces skills vs commands, commands drive the workflow example."

differentiation:
  extension_for_advanced: "Read the actual CONNECTORS.md on GitHub (github.com/anthropics/knowledge-work-plugins/blob/main/finance/CONNECTORS.md). Map each ~~category placeholder to the specific MCP servers your organisation uses or could use. For each category that is 'not pre-configured,' research whether an MCP server exists (hint: NetSuite's does). Draft a configuration plan showing which connectors IT would need to set up for full automation of your close workflow."
  remedial_for_struggling: "Focus on the skills vs commands distinction only. Pick one command (/reconciliation) and one skill (close-management). Describe in your own words: when does each one activate? What does each one produce? If you can explain that difference clearly, you have the core concept of this lesson."

teaching_guide:
  lesson_type: "core"
  session_group: 2
  session_title: "The Cowork Architecture"
  key_points:
    - "The same MCP connectors work in both Claude in Excel and Cowork -- the difference is scope (single workbook vs multi-app orchestration), not the connector set"
    - "Skills fire passively when contextually relevant; commands are explicitly invoked -- the combination produces specialist behaviour, not just tool access"
    - "The category placeholder system (~~erp, ~~data warehouse) is an architectural insight: plugins describe workflows, IT configures connections"
    - "The month-end close workflow demonstrates how commands and skills work together across multiple days, with the close-management skill providing continuous context"
  misconceptions:
    - "Students may think Cowork has a different set of connectors from Claude in Excel -- it does not. The same MCP connectors work in both contexts."
    - "Students may confuse skills with commands -- skills are passive (Claude applies them automatically), commands are active (you type them explicitly)"
    - "Students may think the plugin requires specific ERP software -- the category placeholder system is tool-agnostic by design"
  discussion_prompts:
    - "Why does the plugin use ~~erp instead of 'NetSuite'? What does this tell you about who the plugin is designed for?"
    - "If you were a controller starting a month-end close, which would you interact with first -- a command or a skill? Why?"
  teaching_tips:
    - "The connector narrative is the most important correction: students must understand that Claude in Excel and Cowork share the same MCP connectors. The difference is what Claude can DO with them -- single-workbook analysis vs multi-app orchestration."
    - "The month-end close walkthrough is the anchor example. Walk through it day by day, showing how commands produce outputs and skills provide context."
  assessment_checks:
    - question: "What changes when Claude operates through Cowork instead of inside Excel?"
      expected_response: "The scope of what Claude can do with the same connectors. In Excel, Claude works within one workbook. Through Cowork, Claude can orchestrate across multiple applications -- carrying context from Excel to PowerPoint, querying enterprise systems, and executing multi-step workflows."
    - question: "What is the difference between a skill and a command in a Cowork plugin?"
      expected_response: "A command is explicitly invoked by typing /command-name and triggers a specific workflow. A skill fires automatically in the background whenever Claude judges it contextually relevant. Commands are what you call; skills are what Claude draws on."
    - question: "Why does CONNECTORS.md use ~~erp instead of naming a specific product?"
      expected_response: "Because the plugin is designed to be tool-agnostic. The workflow definitions (SKILL.md files and commands) describe what needs to happen. The connector configuration (which specific ERP) is managed separately by IT. This separates workflow knowledge from infrastructure decisions."
---

# From Assistant to Agent: Cowork Finance Plugins

In Lessons 1 through 5, you worked inside a single Excel workbook. Claude read your formulas, traced dependencies, tested scenarios, and ran the six Agent Skills -- all within the boundary of one spreadsheet. You close the workbook and the context disappears. You finish the analysis and move to PowerPoint, but that transition is yours to make. Claude cannot follow you.

This lesson crosses that boundary. When Claude operates through the Cowork platform, it is not embedded in Excel the way a sidebar is embedded in a workbook. It is an agent that can act across applications, carry context from one tool to another, and execute multi-step workflows that span the entire production process of a financial deliverable. The most significant change is not the tools Claude can access -- the same MCP connectors you configured for Claude in Excel work in Cowork automatically. The change is what Claude can do with them: orchestrate across applications rather than analyse within one.

## The Architecture Shift: From One Tool to Many

The distinction between an embedded assistant and an orchestrating agent is a scope distinction, not a technology distinction. Consider what happens when a controller needs to produce a monthly management report. The process starts in Excel (pull trial balance, reconcile accounts, generate income statement), moves to PowerPoint (build the CFO deck with variance commentary), and ends with email (distribute to the management team with the key findings summarised). Each transition -- copying numbers, formatting slides, writing the email -- is manual work that consumes time and introduces transcription errors.

Claude in Excel handles the first step well. It can reconcile accounts, generate statements, and analyse variances inside the workbook. But when the controller closes Excel and opens PowerPoint, Claude's context resets. The analysis that took fifteen minutes to produce must be manually carried forward.

Cowork treats these transitions as steps in a single workflow rather than as separate tasks. The controller specifies the outcome -- a formatted management deck with variance commentary based on the March close -- and Claude manages the sequence. The same MCP connectors that pulled the trial balance data in Excel now serve a broader purpose: they feed an orchestrated workflow that spans multiple deliverables.

> **What Is Cross-App Orchestration?**
>
> Cross-app orchestration is the ability of an AI agent to execute multi-step workflows across multiple applications -- carrying context from one tool to the next and completing the full sequence autonomously.
>
> **Current status:** Excel-to-PowerPoint orchestration is available in research preview through Cowork for Team and Enterprise plans. The analyst specifies the outcome. Claude manages the sequence: analyse in Excel, build the deck in PowerPoint, using the same data connections throughout.

## Skills vs Commands in Cowork

Before exploring the finance plugin, you need to understand the two ways Claude receives domain knowledge in Cowork.

**Skills are passive.** They are instructions encoded in SKILL.md files that fire automatically when Claude judges them relevant. A finance skill might say: "whenever a variance exceeds ten percent, present it as a table with volume, price, and mix components." Claude applies this without being told to -- every time the condition is met.

**Commands are active.** They are explicitly invoked by typing `/command-name`. They trigger a specific, defined workflow. `/reconciliation` always runs the reconciliation workflow. It does not fire unless you call it.

The combination is what makes Cowork plugins behave like trained specialists rather than general assistants. The commands give you explicit control over specific tasks. The skills ensure that everything Claude does in between -- every response, every analysis, every contextual suggestion -- meets the domain standards encoded in the SKILL.md files.

## The knowledge-work-plugins/finance Plugin

The `knowledge-work-plugins/finance` plugin is a finance and accounting plugin designed for Cowork. It supports month-end close, journal entry preparation, account reconciliation, financial statement generation, variance analysis, and SOX audit support.

**Who it serves:** Corporate FP&A teams, controllers, accounting managers, finance business partners, and internal audit teams. This is the operational finance plugin -- the one that keeps the books clean, the close on schedule, and the audit trail intact.

**What it does not do:** This plugin assists with finance and accounting workflows but does not provide financial, tax, or audit advice. All outputs must be reviewed by qualified financial professionals before use in financial reporting, regulatory filings, or audit documentation.

### Plugin Structure

Every plugin in the knowledge-work-plugins collection follows the same file architecture:

```
finance/
+-- .claude-plugin/plugin.json   # Manifest: name, description, version
+-- .mcp.json                    # Tool connections (data sources)
+-- CONNECTORS.md                # Documentation of connected tools
+-- commands/                    # Slash commands you invoke explicitly
|   +-- income-statement.md
|   +-- journal-entry.md
|   +-- reconciliation.md
|   +-- sox-testing.md
|   +-- variance-analysis.md
+-- skills/                      # Domain knowledge Claude draws on automatically
    +-- audit-support/SKILL.md
    +-- close-management/SKILL.md
    +-- financial-statements/SKILL.md
    +-- journal-entry-prep/SKILL.md
    +-- reconciliation/SKILL.md
    +-- variance-analysis/SKILL.md
```

The separation is architecturally important. **Commands** are what you explicitly invoke. **Skills** are what Claude draws on automatically. You call `/reconciliation` when you want to run a reconciliation. Claude draws on the reconciliation SKILL.md whenever reconciliation is contextually relevant -- such as when you paste a trial balance and ask a question about it, even without invoking the command.

### The Five Commands

**`/journal-entry [type] [period]`** -- Generate journal entries with proper debits, credits, and supporting detail. For each entry type, the command produces the full debit/credit structure, the accounting rationale (which GAAP/IFRS standard applies), and the required supporting documentation. Without a connected ERP, you provide the figures. With a connected ERP, the command pulls transaction data automatically.

```
/journal-entry ap-accrual 2025-03
/journal-entry revenue-recognition 2025-03
```

**`/reconciliation [account] [period]`** -- Compare GL balances to subledger, bank, or third-party balances and identify reconciling items. The output is a structured workpaper: GL balance, source of truth balance, net difference, and each reconciling item categorised as timing difference, in-transit item, error requiring correction, or item requiring investigation.

```
/reconciliation bank-USD 2025-03
/reconciliation accounts-receivable 2025-03
```

> **What Is a GL Reconciliation?**
>
> A GL (General Ledger) reconciliation compares the balance recorded in your accounting system to an independent source of truth -- a bank statement, a subledger, or a third-party confirmation -- and explains every difference. The goal is to confirm that every dollar in the GL is real, correctly classified, and properly supported.
>
> **Categories of reconciling items:** Timing differences (transaction in GL but not yet at the bank -- resolves next period). In-transit items (deposit recorded but not yet credited). Errors (wrong amount, wrong account, wrong period -- requires correcting entry). Items requiring investigation (no obvious explanation -- the most important category to resolve before closing).

**`/income-statement [period-type] [period]`** -- Generate an income statement with period-over-period comparison and variance analysis. Current period, prior period, variance, budget, and budget variance for every line. Material variances above a configurable threshold are flagged for investigation.

**`/variance-analysis [area] [period-vs-period]`** -- Decompose variances into drivers with narrative explanations. Revenue variances split into volume, price, and mix. Operating expense variances split into volume-driven and rate-driven components. The output includes narrative summaries and, when connected to a BI tool, waterfall charts.

**`/sox-testing [process] [period]`** -- Generate SOX 404 control testing workpapers. Control objective, test of design, sample selection with statistical basis, test of operating effectiveness, and deficiency classification template.

### The Six Skills

Skills fire automatically when Claude detects that their domain is relevant.

| Skill                    | When It Activates                                 | What It Adds                                                                  |
| ------------------------ | ------------------------------------------------- | ----------------------------------------------------------------------------- |
| **journal-entry-prep**   | Preparing or reviewing journal entries            | JE best practices, standard accrual types, documentation requirements         |
| **reconciliation**       | Reconciling accounts or investigating differences | GL-to-subledger methodology, reconciling item categorisation, aging standards |
| **financial-statements** | Generating or reviewing financial statements      | GAAP presentation standards, flux analysis methodology                        |
| **variance-analysis**    | Explaining or investigating variances             | Decomposition techniques, materiality thresholds, narrative generation        |
| **close-management**     | Managing month-end or quarter-end close           | Close checklist by day, task sequencing, dependency mapping, status tracking  |
| **audit-support**        | Preparing for or responding to audits             | SOX 404 methodology, sample selection, deficiency classification              |

The close-management skill deserves particular attention. It activates whenever you are in a close context -- even if you are asking Claude a general question about an account balance -- and applies the close checklist lens automatically: is this resolved? Does it need resolution before Day 5? Who owns it?

### Connectors and the Category Placeholder System

The finance plugin works best when connected to your financial data sources. Without connections, you paste data or upload files. With connections, commands pull data automatically. The CONNECTORS.md file documents the connection points -- but it reveals an architectural pattern worth understanding.

The plugin does not reference specific products. Instead, it uses category placeholders:

| Category         | Placeholder          | What It Means                                             |
| ---------------- | -------------------- | --------------------------------------------------------- |
| ERP / Accounting | `~~erp`              | Any accounting system: NetSuite, SAP, QuickBooks, Xero    |
| Data warehouse   | `~~data warehouse`   | Any warehouse: Snowflake, Databricks, BigQuery            |
| Spreadsheets     | `~~office suite`     | Google Sheets or Excel (pre-configured for Microsoft 365) |
| BI / Analytics   | `~~analytics`        | Tableau, Looker, Power BI                                 |
| Document storage | `~~document storage` | Any document management system                            |
| Email            | `~~email`            | Pre-configured for Microsoft 365                          |

This is not a limitation -- it is a design decision. The plugin describes _workflows_. IT configures _connections_. The SKILL.md files and commands say "pull the trial balance from ~~erp" without caring whether the ERP is NetSuite or SAP. When IT configures the `.mcp.json` to point `~~erp` at a NetSuite MCP server, the workflow works automatically. When a different organisation points it at SAP, the same workflow works with no changes to the SKILL.md or commands.

This is Chapter 15's division of responsibility made concrete: the knowledge worker owns the workflow definitions (what the agent should do). IT owns the connector configuration (which systems to connect). Neither needs to modify the other's work.

> **What Is a Month-End Close?**
>
> The month-end close is the process by which a company's accounting team finalises the financial records for a completed calendar month -- reconciling all accounts, posting final journal entries, and producing the management accounts. For most organisations, it takes three to ten business days after month-end.
>
> **Key close tasks by day:** Day 1-2: subledger feeds, bank statement receipt, preliminary trial balance. Day 2-3: AR/AP reconciliation, payroll posting, fixed asset depreciation. Day 3-5: accruals, prepaids, intercompany eliminations. Day 5-7: income statement and balance sheet preparation, flux analysis. Day 7-10: management review, CFO sign-off, distribution.

## Example: The Full Month-End Close Workflow

The month-end close demonstrates how commands and skills work together across multiple days.

**Day 1.** The controller opens Cowork and types: "Let's start the March close." The close-management skill activates automatically. Claude queries the connected data warehouse for each close checklist item's current state, produces the Day 1 status report, and surfaces two blockers: a $3,420 bank reconciliation discrepancy on the USD operating account and a missing intercompany settlement confirmation from Singapore.

**Day 3.** `/reconciliation bank-USD 2025-03`. Claude queries the connected bank data, runs the reconciliation against the GL, and produces a structured workpaper. The $3,420 discrepancy breaks down as: four timing differences totalling $2,180 (checks issued in March, clearing in April), two bank charges totalling $840 not yet posted to the GL (requires journal entry), and one unidentified item of $400 requiring investigation.

**Day 4.** `/journal-entry bank-charges 2025-03`. Claude generates the entry: debit Bank Charges Expense $840, credit Cash -- USD Operating $840, with transaction references and a note that this entry requires controller review before posting.

**Day 5.** `/variance-analysis revenue 2025-Q1 vs budget`. Claude pulls Q1 actuals from the data warehouse and the budget from the BI platform. Revenue is $2.3M below budget (-4.1%), decomposed as: volume shortfall $3.1M adverse (unit volume 8.2% below budget), price $0.8M favourable (average selling price 2.1% above budget due to product mix shift toward premium SKUs). Narrative generated. CFO-ready in fifteen minutes.

**Day 6.** `/income-statement monthly 2025-03`. The full management P&L with current month, prior month, YTD actual, YTD budget, and YTD variance columns, formatted in the firm's standard template, with material variances flagged and narrative summaries for the top three. Ready for distribution.

**SOX season.** `/sox-testing revenue-recognition 2025-Q1`. Control testing workpapers: control objective (revenue recognised in accordance with ASC 606), test of design, sample selection with statistical methodology, test of operating effectiveness template, and deficiency classification guide.

Throughout this entire workflow, the close-management skill is active in the background. On Day 3, when the controller runs the bank reconciliation, the skill contextualises the output: it flags the $400 unidentified item not just as an outstanding reconciling item but as a blocker that must be resolved before Day 5 close activities can proceed. On Day 5, when the variance analysis is complete, the skill checks it against the close checklist and marks the revenue review as complete.

## Try With AI

Use these prompts in Cowork or your preferred AI assistant to explore the concepts from this lesson.

### Prompt 1: Plugin Architecture Exploration

```
I want to understand how a Cowork finance plugin is structured.

Given this directory layout:
- .claude-plugin/plugin.json (manifest)
- .mcp.json (connector configuration)
- commands/ (5 .md files: journal-entry, reconciliation,
  income-statement, variance-analysis, sox-testing)
- skills/ (6 directories, each with SKILL.md: journal-entry-prep,
  reconciliation, financial-statements, variance-analysis,
  close-management, audit-support)

Explain:
1. What happens when I type /reconciliation in Cowork?
2. What happens when I paste a trial balance WITHOUT typing
   any command?
3. Why are there both a reconciliation command AND a
   reconciliation skill?
```

**What you're learning:** The distinction between commands (explicit invocation) and skills (passive activation) is the core architectural concept of Cowork plugins. Understanding when each fires -- and why both exist for the same domain -- reveals how the plugin produces specialist behaviour rather than just providing tool access.

### Prompt 2: Category Placeholder Analysis

```
The knowledge-work-plugins/finance plugin uses category
placeholders in its workflow definitions:

- ~~erp (could be NetSuite, SAP, QuickBooks, Xero)
- ~~data warehouse (could be Snowflake, Databricks, BigQuery)
- ~~analytics (could be Tableau, Looker, Power BI)

Help me understand this design:
1. Why doesn't the plugin just say "NetSuite" instead of ~~erp?
2. Who is responsible for mapping ~~erp to a specific product?
3. What happens to the workflow definitions (SKILL.md and
   commands) when a company switches from NetSuite to SAP?
4. How does this connect to the idea that knowledge workers
   own workflows and IT owns infrastructure?
```

**What you're learning:** The category placeholder system is a concrete implementation of separation of concerns. By understanding who owns what -- knowledge workers own the SKILL.md, IT owns the .mcp.json -- you can see how plugins scale across organisations without requiring workflow rewrites for each enterprise's technology stack.

### Prompt 3: Close Workflow Design

```
I'm a controller at a mid-market company starting the March
month-end close. Walk me through which Cowork finance plugin
commands I would use on each day of a 7-day close:

Day 1: Initial status and blocker identification
Day 2-3: Account reconciliations
Day 4: Journal entries for reconciling items
Day 5: Variance analysis and management reporting
Day 6: Income statement and distribution prep
Day 7: SOX documentation (if applicable)

For each day:
- Which command(s) would I invoke?
- Which skill(s) would fire automatically?
- What output would I expect?
- What human judgment is still required?
```

**What you're learning:** A month-end close is not a single task but a multi-day workflow where each step builds on the previous one. By mapping commands and skills to specific close days, you develop the ability to orchestrate financial workflows through Cowork rather than treating each command as an isolated tool.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 7: The Financial Services Plugin Suite -->](./07-the-financial-services-plugin-suite.md)
