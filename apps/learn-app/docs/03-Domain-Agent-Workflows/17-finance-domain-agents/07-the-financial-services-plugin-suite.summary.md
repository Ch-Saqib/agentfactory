### Core Concept

The financial-services-plugins suite is an ecosystem of 41 skills, 38 commands, and 11 MCP data integrations organised around a shared-core architecture. The **financial-analysis** core plugin centralises all MCP data connectors — configure once, share across all add-ons. Install order is mandatory: core first, then function-specific add-ons (**investment-banking**, **equity-research**, **private-equity**, **wealth-management**) and partner-built plugins (**LSEG**, **S&P Global**).

### Key Mental Models

- **Shared-Core Architecture**: All 11 MCP data connectors live in the core plugin's `.mcp.json`. Add-on plugins inherit these connections automatically — no duplicate configuration. This is why the core must be installed first.
- **Five End-to-End Workflows**: Research to Report, Spreadsheet Analysis, Financial Modelling, Deal Materials, and Portfolio to Presentation. Each moves from raw data to professional deliverable in a single session. The deliverables are structured drafts requiring professional review.
- **Five Customisation Dimensions**: Swap connectors (your data providers), add firm context (terminology and processes), bring templates (branded PowerPoint), adjust workflows (match your team), build new plugins (extend the collection). The plugin skill files are plain Markdown — editable without technical knowledge.

### Critical Patterns

- The core plugin's `/comps`, `/dcf`, and `/lbo` commands produce working Excel files with live formulas and Wall Street colour-coding conventions (blue inputs, black formulas, green outputs)
- Each add-on targets a specific finance function: investment-banking handles deal materials, equity-research handles coverage and earnings, private-equity handles sourcing through IC memos, wealth-management handles client-facing advisory workflows
- Partner plugins (LSEG, S&P Global) bring proprietary data that extends the suite beyond what Anthropic-built plugins provide alone

### Common Mistakes

- Installing add-on plugins before the core — add-ons depend on the core's shared MCP connectors and will not function without them
- Treating plugin outputs as final deliverables — they produce structured drafts that require professional judgment and review before client or committee use
- Ignoring customisation — the default plugins use generic terminology and templates; the real value comes from adapting them to your firm's specific conventions and workflows

### Connections

- **Builds on**: Lesson 6 introduced Agent Skills for individual finance tasks in Excel; this lesson scales to the coordinated plugin ecosystem across all finance functions
- **Leads to**: Lesson 8 teaches how to build your own finance agent skill — moving from consumer of the plugin suite to creator of firm-specific capabilities
