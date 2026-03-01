### Core Concept

Finance is the domain where the distinction between an AI assistant and an AI agent becomes concrete and consequential. **Claude in Excel** is an embedded assistant — a standalone Microsoft add-in that lives in a sidebar within one workbook, reading all sheets, formulas, and data to answer questions, debug errors, and produce professional financial deliverables through six pre-built Agent Skills. **Cowork with Excel** is an orchestrating agent — part of the Cowork platform that treats Excel as one node in a multi-step autonomous workflow spanning multiple applications. Both share the same MCP connector ecosystem; the difference is scope, not capability.

### Key Mental Models

- **Assistant vs Agent Architecture**: An embedded assistant operates within one application (deep companion for modelling work). An orchestrating agent operates across applications (workflow automation from Excel to PowerPoint to Word). The architecture you need depends on whether your deliverable lives inside one tool or spans several.
- **Two Layers of Claude in Excel**: Layer 1 is general workbook intelligence — always active, works on any spreadsheet, provides cell-level traceability. Layer 2 is six pre-built Agent Skills — specialist financial workflows (comps, DCF, due diligence, teasers, earnings, initiating coverage) that connect to live market data and produce industry-standard deliverables.
- **Shared MCP Connectors**: Claude in Excel and Cowork do not maintain separate data ecosystems. Any MCP connector configured in your Claude settings (S&P Global, FactSet, PitchBook, Morningstar, and others) works in both environments. The distinction is scope — one workbook versus multi-app orchestration.

### Critical Patterns

- The chapter is structured in three parts: Part One covers Claude in Excel (the embedded assistant), Part Two covers Cowork finance plugins (the orchestrating agent), and Part Three covers enterprise extensions using the Knowledge Extraction Method from Chapter 16
- Users can switch between Sonnet 4.6 and Opus 4.6 models in Claude in Excel for different cost-quality tradeoffs
- Spreadsheets from untrusted sources carry prompt injection risks — Claude reads cell values, formulas, and comments, so malicious instructions can be hidden in workbooks shared during deal processes and audits

### Common Mistakes

- Assuming Claude in Excel and Cowork use separate connector ecosystems — they share the same MCP connectors; the difference is architectural scope
- Confusing the six pre-built Agent Skills with general chat capabilities — the Agent Skills are purpose-built financial workflows, not conversational features
- Thinking Claude in Excel requires the Cowork platform — it is a standalone Microsoft add-in that works independently

### Connections

- **Builds on**: Chapter 16 taught the Knowledge Extraction Method for surfacing tacit knowledge; Chapter 15 taught SKILL.md architecture and the Agent Skills Pattern — this lesson applies both to the finance domain
- **Leads to**: Lesson 2 begins hands-on work with Claude in Excel's general workbook intelligence — understanding models you did not build
