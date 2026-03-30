### Core Concept

This lesson covers three general capabilities of Claude in Excel that complete the foundation layer before the six pre-built Agent Skills: scenario testing without breaking formulas, formula error diagnosis from symptom to source, and building model structures from plain-language descriptions. Each capability is preceded by the financial concept boxes needed to use it — sensitivity analysis, DCF fundamentals, common Excel errors, EBITDA, and the three financial statements.

### Key Mental Models

- **Non-destructive scenario testing**: Claude modifies input cells directly, reports downstream impacts with cell references, and Ctrl+Z reverts all changes — eliminating the choice between overwriting the base case and building a scenario manager. Combined scenario impacts compound rather than add, and Claude shows the actual combined effect.
- **Error tracing as chain analysis**: Formula errors propagate through dependency chains. The visible #REF! in a summary cell may originate from an OFFSET formula broken three sheets away by a structural change. Claude traces the full chain in seconds, replacing fifteen minutes of manual cell-by-cell investigation.
- **Specification-driven model building**: The quality of a model Claude builds is proportional to the specificity of the instruction. A specification with named tabs, explicit line items, and stated linkage requirements produces a working starting point; a vague prompt produces a model that must be rebuilt.

### Critical Patterns

- Scenario testing reveals which assumptions a conclusion depends on most — sensitivity analysis identifies where to focus analytical effort
- The text-number formatting mismatch is the most common invisible error in financial models imported from accounting systems — SUM silently excludes text-formatted cells
- Model building with AI follows the same spec-first pattern taught throughout this book: front-load precision in the specification, then validate the output against it

### Common Mistakes

- Running scenarios by overwriting the base case without a revert plan — Claude plus Ctrl+Z eliminates this risk
- Assuming all formula errors have the same root cause — each error type (#REF!, #VALUE!, #DIV/0!, #N/A) has a distinct cause and diagnostic approach
- Writing vague model specifications ("build me a financial model") instead of specifying tabs, line items, and linkage requirements
- Trusting that numbers displayed in cells are actually numeric — text-formatted numbers look identical but are silently excluded from calculations

### Connections

- **Builds on**: Lesson 2 taught model comprehension (tracing dependencies, mapping logic); this lesson uses the same Claude in Excel interface for scenario testing, error diagnosis, and model construction
- **Leads to**: Lesson 4 introduces the six pre-built Agent Skills (Layer 2), starting with Comparable Company Analysis and DCF — which build on the DCF and EBITDA concept boxes introduced here
