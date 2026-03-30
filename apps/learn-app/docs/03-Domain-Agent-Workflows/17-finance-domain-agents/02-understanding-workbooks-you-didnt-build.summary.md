### Core Concept

Every finance professional inherits models nobody documented. Claude in Excel compresses the manual process of tracing formula dependencies by reading the entire workbook and producing plain-language explanations with cell-level citations -- specific cell references you can click in the sidebar to navigate directly to the source. This dependency tracing is Layer 1 of Claude in Excel's capabilities: general workbook intelligence that works on any workbook without configuration.

### Key Mental Models

- **Dependency tracing with cell-level citations**: Claude follows the formula chain from any output cell back through all tabs to the original input cells, citing every cell reference along the way. Clicking a citation navigates Excel directly to that cell.
- **Input vs output cells**: All financial models share one structural pattern -- input cells (blue by convention) contain assumptions you set, output cells contain formulas that calculate results. Understanding which cells are inputs and which are formulas is the first step in comprehending any inherited model.
- **Four model types**: Three-statement (linked financial statements), DCF (discounted future cash flows), comps (relative valuation via multiples), LBO (leveraged acquisition returns). All four follow the same inputs-drive-outputs pattern.

### Critical Patterns

- Always trace dependencies before modifying anything -- a change to one cell can cascade through a multi-tab model in ways you cannot anticipate without mapping the chain first
- Verification is non-negotiable: navigate to each cell Claude cites and confirm the reference is accurate before presenting or acting on the trace
- Cascade analysis reveals which assumptions carry the most weight -- experienced analysts prioritise verifying high-impact inputs first rather than tracing every cell in order

### Common Mistakes

- Trusting Claude's cell references without navigating to the cited cells to verify them -- any AI-generated reference could be inaccurate
- Modifying assumption cells before understanding which downstream outputs they affect -- cascading errors in financial models can produce plausible but wrong results
- Treating all model types as structurally identical -- while inputs-drive-outputs is universal, the specific linkages and conventions vary between three-statement, DCF, comps, and LBO models

### Connections

- **Builds on**: Lesson 1 established the distinction between Claude in Excel (embedded assistant) and Cowork (orchestrating agent); this lesson puts the embedded assistant to work on the most common professional problem
- **Leads to**: Lesson 3 teaches scenario testing, formula error debugging, and building new model structures -- capabilities that build on the model comprehension foundation established here
