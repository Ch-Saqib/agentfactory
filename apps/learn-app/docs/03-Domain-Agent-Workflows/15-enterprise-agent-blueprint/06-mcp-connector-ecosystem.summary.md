### Core Concept

The Cowork marketplace provides production MCP connectors for most enterprise systems across CRM, communication, knowledge/document, data/analytics, workflow, financial data, legal research, bio-research, contracting, and enrichment categories. When a required system is not in the marketplace, a custom connector follows a commissioning process with timelines that depend on API maturity: shorter for modern REST APIs, longer for legacy or complex systems. Connector timelines are planning facts that must appear in deployment plans from the outset.

### Key Mental Models

- **Marketplace vs Custom Connectors**: Marketplace connectors cover standard enterprise systems (HubSpot, Jira, Snowflake, FactSet, etc.); custom connectors are built for organisation-specific or niche systems (e.g., a specific Revit installation)
- **Connector Scoping**: Each connector has a scope that restricts what data within the external system the agent can access — a SharePoint connector scoped to one folder is not a limited connector, it is a correctly configured one
- **Custom Connector Specification**: Four elements — which system (precise name/version), what data (specific objects/entities), what queries (filter by X, retrieve by Y), what permissions (read/write, scope restrictions)
- **Timeline as Planning Fact**: Timeline depends on API maturity — shorter for modern REST APIs, longer for legacy/complex systems — connector commissioning must start first because it is on the critical path

### Critical Patterns

- Financial data connectors (LSEG, S&P Global, FactSet, MSCI) and legal research connectors (LegalZoom, DocuSign) require licensed subscriptions — the connector cannot be activated without a valid licence already in place
- Bio-research connectors (PubMed, ClinicalTrials.gov, ChEMBL, Benchling, BioRender) provide structured research data; verify data access terms for each provider
- Custom connector development (SKILL.md) and connector commissioning can run in parallel — but commissioning must start first
- The knowledge worker specifies connector requirements in plain language; IT implements — this is not self-service

### Common Mistakes

- Assuming all connectors are available out of the box — financial and legal connectors require pre-existing licensed subscriptions
- Underestimating custom connector timelines — the shorter timeline is the floor for modern APIs, not a universal target
- Conflating connector scoping with connector capability — scope is a security feature

### Connections

- **Builds on**: Lesson 3 introduced connectors conceptually; this lesson maps the full ecosystem and commissioning process
- **Leads to**: Lesson 7 covers the governance layer — the organisational governance settings that govern how connector-sourced data flows through the plugin
