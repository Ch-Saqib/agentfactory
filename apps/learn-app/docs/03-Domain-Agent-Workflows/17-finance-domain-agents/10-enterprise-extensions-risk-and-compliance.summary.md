### Core Concept

Enterprise extensions close the gap between generic finance plugins and institutional need by encoding organisation-specific knowledge as SKILL.md instructions. Generic plugins compute financial ratios and produce standard deliverables correctly — extensions add the sector-specific thresholds, jurisdiction-specific regulatory methodologies, client-specific constraints, and governance sign-off sequences that determine whether output is immediately usable or requires significant rework. Each extension follows the same three-step pattern: identify the gap, write specific instructions, add governance gates.

### Key Mental Models

- **Generic vs Extension:** The generic plugin knows how to calculate interest coverage ratio; the credit risk extension knows that below 2.0x is stressed in non-cyclical sectors but below 3.0x is already concerning in cyclical sectors. The difference is institutional context.
- **Variance Decomposition:** Volume, price, and mix components explain _why_ performance differed from plan — the total variance alone masks which drivers are within management control and which are not.
- **Constraint Verification Sequence:** IPS compliance checks follow a strict hierarchy — hard caps first (never violable), concentration targets (require sign-off), screening exclusions (require waiver), liquidity requirements (trigger review) — routing routine compliance automatically and edge cases to human judgment.
- **Brinson Attribution:** Decomposes portfolio outperformance into allocation (right sectors), selection (right securities), and interaction effects — transforming a single return number into a diagnostic of which investment decisions created value.

### Critical Patterns

- Every extension layers on top of a generic plugin — it does not replace it
- Regulatory extensions are jurisdiction-specific by design: SBP, Basel III, SEC, and EBA implementations produce different results from the same underlying data
- SKILL.md instructions must reference specific ratios, thresholds, and signals — generic directives like "analyze credit risk carefully" fail the testability criterion from Chapter 16
- Governance gates (mandatory sign-off sequences) are unconditional routing rules, not guidelines — they appear as non-negotiable escalation conditions in every compliance-sensitive extension

### Common Mistakes

- Writing generic SKILL.md instructions instead of institution-specific ones — "flag high leverage" vs "flag net debt/EBITDA above 4.0x in non-cyclical sectors"
- Assuming one regulatory extension works across jurisdictions — CET1 calculation methodologies differ between SBP, Fed, and EBA
- Treating IPS constraints as a flat checklist rather than a hierarchical verification sequence with different handling per constraint type
- Building extensions that duplicate generic plugin functionality instead of layering institutional knowledge on top

### Connections

- **Builds on**: Chapter 16's Knowledge Extraction Method (Persona-Questions-Principles structure for SKILL.md writing), Lessons 5-9 (generic finance plugin workflows that extensions layer on top of)
- **Leads to**: Lesson 11 (chapter summary), and the practical deployment of enterprise extensions in the reader's own organisation
