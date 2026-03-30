### Core Concept

Cross-app orchestration executes multi-step workflows that span multiple applications — connecting Excel analysis to PowerPoint deliverables in a single continuous pass. The architectural advantage is structural consistency: because the agent carries context directly from the model to the deck without a copy-paste step, the output numbers cannot become disconnected from their source. This eliminates the silent-stale-data failure mode that manual transfer introduces.

### Key Mental Models

- **Structural Consistency vs Manual Consistency**: When the agent produces the PowerPoint from the Excel model in a single pass, consistency is guaranteed by architecture. When you copy numbers by hand, consistency depends on remembering to update every reference after every revision — a requirement that fails silently.
- **Disconnection Risk**: The specific failure mode of manual cross-app workflows. After a model revision, any manually built deliverable that references the old numbers contains stale data. The error is invisible until discovered by a reviewer or, worse, a client.
- **Agent vs Assistant (Architectural)**: An assistant operates within one application (Claude in Excel helps inside a workbook). An agent operates across applications (Cowork carries context from Excel to PowerPoint). The distinction is scope of operation and context carriage, not capability within a single tool.

### Critical Patterns

- Cross-app orchestration is available in Cowork Team and Enterprise — Claude in Excel alone is an assistant within one workbook and cannot orchestrate across applications
- The time saving (75 minutes to one continuous workflow) is a side effect — the primary advantage is eliminating disconnection risk
- The production pattern for finance is complementary: Cowork orchestrates the workflow, Claude in Excel audits the model — both architectures serve different purposes

### Common Mistakes

- Treating cross-app orchestration as "faster copy-paste" rather than recognising it as a structurally different consistency model
- Assuming all Claude products support cross-app workflows — it requires Cowork Team or Enterprise
- Underestimating the frequency and severity of copy-paste errors in professional deliverables

### Connections

- **Builds on**: Lessons 1-7 established Claude in Excel capabilities and plugin workflows within a single application; this lesson crosses the application boundary
- **Leads to**: Enterprise extensions and custom deployment patterns that build on the cross-app foundation
