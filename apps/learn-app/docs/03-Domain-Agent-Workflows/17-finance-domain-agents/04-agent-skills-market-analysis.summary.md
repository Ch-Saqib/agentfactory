### Core Concept

Agent Skills are pre-built analytical workflows in Claude in Excel that go beyond general workbook assistance into structured financial deliverables. This lesson covers two market analysis skills: **Comparable Company Analysis (Comps)** and **Discounted Cash Flow (DCF)**. Both connect to live market data through MCP connectors configured in Claude settings -- the same connectors shared across Excel and Cowork -- and produce professionally formatted output. The key insight: Agent Skills handle the arithmetic instantly; the professional skill is choosing the right inputs (peer group for comps, assumptions for DCF) and interpreting the range of outputs.

### Key Mental Models

- **Comps as a market check, not a fundamental valuation**: Comps tells you what the market is paying for similar companies today, using multiples like EV/EBITDA. Enterprise value (market cap plus debt minus cash) provides a capital-structure-neutral comparison. The analyst's judgement -- which companies are truly comparable, and whether the subject deserves a premium or discount -- is the irreplaceable skill.
- **DCF as a range, not a single answer**: A DCF projects future cash flows and discounts them using WACC (weighted average cost of capital). Because WACC and terminal growth rate are estimates, the sensitivity table -- showing equity value across assumption combinations -- is the most honest output. A 1 percentage point change in WACC typically moves equity value by 10-20%.
- **LTM as the standard comparison timeframe**: Trailing twelve months ensures all companies in a comps analysis are compared on the same period, regardless of when their fiscal year ends.

### Critical Patterns

- Agent Skills follow professional formatting conventions (blue inputs, black formulas, green outputs) so the workbook is immediately presentation-ready
- The Comps workflow progresses: invoke skill, review peer group, refine selections, derive implied valuation range -- the review step is where professional judgement enters
- The DCF workflow progresses: invoke skill, identify high-impact assumptions, test scenarios, read sensitivity table -- the interpretation step is where analytical value is created

### Common Mistakes

- Accepting the AI-selected peer group without reviewing whether the companies are genuinely comparable in size, geography, and business model
- Treating the DCF mid-point equity value as a precise answer rather than one point in a range defined by the sensitivity table
- Assuming Agent Skills have their own separate data connectors -- they use the same MCP connectors configured in Claude settings, shared across all Claude tools

### Connections

- **Builds on**: Lesson 3 taught general workbook intelligence (scenarios, debugging, model building); this lesson introduces structured, domain-specific analytical workflows
- **Leads to**: Lesson 5 covers the remaining four Agent Skills (Due Diligence, Teaser, Earnings Analysis, Initiating Coverage) which handle deal preparation and research deliverables
