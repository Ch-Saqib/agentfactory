### Core Concept

Enterprise extensions bridge the gap between generic finance plugin capabilities and an organisation's specific institutional knowledge. Each extension follows the same pattern: identify what the generic plugin lacks, name the institutional knowledge the extension must encode, write SKILL.md instructions that close the gap, and design validation scenarios to test them. The seven domains covered — treasury and cash management, tax provision and compliance, FP&A and budget ownership, M&A integration PMO, ESG reporting, fund administration, and insurance underwriting — each require organisation-specific rules that no generic plugin can infer.

### Key Mental Models

- **Gap-to-Instruction Pattern**: Every extension starts by naming the specific gap between generic capability and organisational requirement, then encodes the institutional knowledge that closes it as testable SKILL.md instructions
- **Selective Engagement**: Students engage with the domains relevant to their professional context rather than mastering all seven — the pattern transfers across domains even if the specifics do not
- **Three-Criteria Prioritisation**: Rank extensions by operational pain (daily friction), knowledge risk (expertise concentration in individuals), and regulatory exposure (compliance urgency) to determine build order
- **Specificity Determines Value**: Generic SKILL.md instructions ("calculate the tax provision") produce generic outputs; organisation-specific instructions that encode actual jurisdictional rates, permanent differences, and valuation methodologies produce outputs that match how the organisation works

### Critical Patterns

- Treasury extensions encode hedging policy rules, banking structure, FX rate sources, and intercompany loan details — without these, the agent may violate the firm's risk mandate
- Tax provision extensions require jurisdictional profiles, permanent/temporary difference classifications, and deferred tax asset valuation methodology
- FP&A extensions encode the CFO's preferred variance bridge format, reforecast trigger thresholds, and seasonal adjustment factors
- Fund administration extensions must encode the exact fee waterfall sequence from the partnership agreement — fee calculation errors are contractual disputes, not rounding differences

### Common Mistakes

- Writing generic SKILL.md instructions instead of organisation-specific ones — the specificity of the instruction determines the quality of the output
- Trying to build all extensions simultaneously instead of prioritising by pain, risk, and regulatory exposure
- Skipping concept boxes for unfamiliar domains — the domain vocabulary is required to write effective SKILL.md instructions

### Connections

- **Builds on**: Chapter 16's Knowledge Extraction Method (extraction, SKILL.md writing, validation) and prior Chapter 17 lessons on generic finance plugins and the financial-services suite
- **Leads to**: Chapter Summary (synthesising the complete finance domain agent architecture) and the extension roadmap exercise that serves as the starting point for real deployment
