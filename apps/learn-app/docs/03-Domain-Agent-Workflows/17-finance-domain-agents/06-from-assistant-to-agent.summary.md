### Core Concept

The shift from Claude in Excel to Cowork is a scope expansion, not a technology change. The same MCP connectors serve both contexts -- inside Excel, Claude analyses within one workbook; through Cowork, Claude orchestrates across multiple applications, carrying context from Excel to PowerPoint to email. The finance plugin packages this orchestration capability into five explicit commands and six passive skills that together support multi-day workflows like the month-end close.

### Key Mental Models

- **Skills vs Commands**: Commands (/reconciliation, /journal-entry) are explicitly invoked and trigger specific workflows. Skills (close-management, variance-analysis) fire automatically in the background whenever Claude judges them contextually relevant. The combination produces specialist behaviour -- commands for control, skills for consistency.
- **Category Placeholder System**: The plugin uses ~~erp, ~~data warehouse, ~~analytics as placeholders rather than naming specific products. This separates workflow knowledge (SKILL.md, owned by the knowledge worker) from connector configuration (.mcp.json, owned by IT). The same plugin works with NetSuite or SAP without modifying a single workflow definition.
- **Plugin Architecture**: Every plugin follows a standard directory structure -- plugin.json (manifest), .mcp.json (connectors), CONNECTORS.md (documentation), commands/ (explicit workflows), skills/ (passive knowledge). Understanding this structure is prerequisite for customising or extending plugins.
- **Month-End Close as Orchestration**: The close workflow spans multiple days and multiple commands, with the close-management skill providing continuous context. Each command builds on the previous day's output, and the skill contextualises every interaction within the close timeline.

### Critical Patterns

- The connector narrative is one ecosystem, not two: Claude in Excel and Cowork share the same MCP connectors, with the difference being orchestration scope
- The category placeholder system (~~erp) is Chapter 15's division of responsibility made concrete: knowledge workers own workflows, IT owns connections
- Passive skills like close-management add value by contextualising every interaction, not just responding to explicit commands

### Common Mistakes

- Thinking Cowork has different connectors from Claude in Excel (they share the same MCP connector set)
- Confusing skills (passive, auto-triggered) with commands (active, explicitly invoked)
- Assuming the plugin requires specific enterprise software (the placeholder system is tool-agnostic by design)

### Connections

- **Builds on**: Lessons 1-5 established Claude in Excel capabilities within a single workbook; this lesson expands to multi-app orchestration through Cowork
- **Leads to**: Lesson 7 introduces the financial-services-plugins suite (investment professional workflows), building on the plugin architecture concepts established here
