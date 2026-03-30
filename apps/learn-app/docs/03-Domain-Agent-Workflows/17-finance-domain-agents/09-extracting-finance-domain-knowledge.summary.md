### Core Concept

The Knowledge Extraction Method from Chapter 16 applied to a CFO's monthly close workflow surfaces the firm-specific tacit knowledge that generic finance plugins cannot encode — materiality thresholds calibrated to this business, seasonal baseline adjustments, account-level attention patterns, and the sequencing logic that prevents recurring close errors. The gap between a generic plugin and a production-ready finance agent is filled by this extracted knowledge, translated into a SKILL.md with a functional Persona, scoped Questions section, and testable Principles.

### Key Mental Models

- **Generic vs Firm-Specific Knowledge**: A generic plugin applies industry-standard thresholds ($100K or 10%) identically across all companies. Firm-specific knowledge applies different thresholds to different accounts based on operational context — a $5K variance in a dormant account triggers investigation regardless of the firm-wide threshold, while a $50K revenue variance is ignored as normal monthly noise.
- **Five Questions in Finance Context**: Each question surfaces a distinct layer: Q1 targets undocumented heuristics (materiality judgment), Q2 targets override conditions (post-acquisition threshold waivers), Q3 targets leading indicators (AR aging shifts), Q4 targets experience gaps (intercompany elimination sequencing), Q5 targets load-bearing instructions (deferred revenue verification before trusting revenue).
- **Method B Applied to Close Documents**: The close checklist, accounting policies manual, and prior period adjustments log each yield different extraction material through the three-pass framework — explicit rules, practice-vs-policy contradictions, and gap scenarios.

### Critical Patterns

- The variance analysis table is the anchor illustration: the same data produces different responses from a generic plugin versus an experienced CFO, and the difference is traceable to firm-specific tacit knowledge
- Each SKILL.md Principle in the worked example passes the testability criterion — a scenario can be constructed and the agent's compliance confirmed or denied
- The out-of-scope section prevents the agent from attempting close workflows it cannot handle reliably (post-acquisition periods, restructuring entities, policy interpretation)

### Common Mistakes

- Writing SKILL.md Principles that restate accounting standards rather than encoding firm-specific heuristics — "follow GAAP" is not a useful Principle
- Confusing the generic plugin's value (standard workflows) with the SKILL.md's value (firm-specific judgment) — the plugin and the SKILL.md are complementary, not substitutes
- Skipping the out-of-scope definition, allowing the agent to apply standard analysis to non-standard periods (post-acquisition, restructuring) where it will produce misleading results

### Connections

- **Builds on**: Chapter 16 Lessons 2-6 provided the Five Questions, interview technique, and SKILL.md writing method; Lesson 6 of this chapter introduced the generic finance plugin whose limitations this lesson addresses
- **Leads to**: Lessons 10-11 extend the extraction pattern to eleven enterprise areas (credit risk, regulatory reporting, treasury, FP&A, and more), each following the same Five Questions → extraction → SKILL.md pipeline
