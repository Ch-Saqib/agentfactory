---
sidebar_position: 2
title: "Understanding Workbooks You Didn't Build"
description: "Learn to use Claude in Excel to trace formula dependency chains, map inherited model logic with cell-level citations, and comprehend financial workbooks in minutes rather than hours"
keywords:
  [
    "Claude in Excel",
    "financial model comprehension",
    "formula dependencies",
    "cell-level citations",
    "inherited workbooks",
    "dependency tracing",
    "three-statement model",
    "DCF model",
    "comps model",
    "LBO model",
    "model audit",
    "FP&A",
  ]
chapter: 17
lesson: 2
duration_minutes: 25

# HIDDEN SKILLS METADATA
skills:
  - name: "Trace Formula Dependencies with AI Assistance"
    proficiency_level: "A2"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can open an inherited multi-tab workbook, ask Claude to trace the dependency chain for a specific output cell, and verify the cited cell references by navigating to each one"

  - name: "Interpret Financial Model Structure"
    proficiency_level: "A2"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Information Literacy"
    measurable_at_this_level: "Student can name the four major financial model types (three-statement, DCF, comps, LBO), explain the difference between input cells and formula-calculated cells, and describe what dependency tracing reveals about a model's logic"

  - name: "Verify AI-Generated Cell References"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Analyze"
    digcomp_area: "Safety"
    measurable_at_this_level: "Student can take Claude's dependency trace output, navigate to each referenced cell, confirm the references are accurate, and identify any dependency that Claude may have missed or mischaracterised"

learning_objectives:
  - objective: "Use Claude in Excel to trace the full dependency chain for any output cell in an inherited workbook, producing a plain-language explanation with verifiable cell references"
    proficiency_level: "A2"
    bloom_level: "Apply"
    assessment_method: "Student opens an unfamiliar multi-tab workbook, asks Claude to trace a specific cell's dependencies, and confirms the accuracy of at least three cited cell references by navigating to them"

  - objective: "Distinguish between the four major financial model types and explain how input cells relate to formula-calculated output cells"
    proficiency_level: "A2"
    bloom_level: "Understand"
    assessment_method: "Student can name the four model types, describe what each produces, and explain why understanding the input-output relationship matters for model comprehension"

  - objective: "Evaluate the accuracy of Claude's dependency trace by cross-referencing cited cells against the actual workbook structure"
    proficiency_level: "B1"
    bloom_level: "Analyze"
    assessment_method: "Given Claude's trace output for an unfamiliar model, student navigates to each cited cell, confirms accuracy, and identifies at least one follow-up question to deepen comprehension"

cognitive_load:
  new_concepts: 5
  concepts_list:
    - "Dependency tracing — following formula chains from output back to input cells"
    - "Cell-level citations — Claude's ability to reference specific cells you can click to verify"
    - "Four financial model types — three-statement, DCF, comps, LBO"
    - "Input vs output cells — blue-cell convention for assumptions vs formula-calculated results"
    - "Cascading changes — how modifying one assumption flows through a multi-tab model"
  assessment: "5 concepts at A2-B1 level, within the 5-7 cognitive limit for this tier. The financial model types share a common structure (inputs drive outputs) that provides scaffolding across the set."

differentiation:
  extension_for_advanced: "Open a real financial model from your work and use Claude to map every assumption cell that drives a specific P&L line item. Document which assumptions have the largest impact on the output by asking Claude to rank sensitivity. Compare Claude's dependency map against your own manual understanding of the model."
  remedial_for_struggling: "Start with a simple two-tab workbook where one tab has raw data and the other has formulas referencing it. Ask Claude to explain what one formula does. Navigate to the referenced cell. Repeat with three more formulas until the trace-and-verify pattern feels natural."

teaching_guide:
  lesson_type: "core"
  session_group: 1
  session_title: "Understanding Workbooks You Didn't Build"
  key_points:
    - "Every finance professional inherits models nobody documented — this is the universal starting point for the lesson because it connects immediately to real professional frustration"
    - "Claude traces formula dependency chains and provides cell-level citations — the cell references are clickable in the sidebar, making verification immediate rather than requiring manual tab-hopping"
    - "The four financial model types all share the same fundamental structure: inputs (assumptions) drive calculated outputs — understanding this pattern transfers across model types"
    - "Verification is non-negotiable: Claude's traces must be confirmed by navigating to cited cells, because any AI-generated reference could be incorrect"
  misconceptions:
    - "Students may think Claude replaces the need to understand the model — Claude accelerates comprehension but the professional must still verify and interpret"
    - "Students may assume all financial models follow the same structure — while inputs-drive-outputs is universal, the specific linkages vary significantly between model types"
    - "Students may trust Claude's cell references without verification — the discipline of checking cited cells is the core professional skill this lesson builds"
  discussion_prompts:
    - "Think of a time you inherited a spreadsheet or document someone else built. What was hardest about understanding it? How would dependency tracing have changed that experience?"
    - "Why is it important to verify Claude's cell references rather than trusting them? What could go wrong if a dependency trace contained an error you did not catch?"
  teaching_tips:
    - "Walk through the board call scenario in real time — the urgency makes the value of rapid dependency tracing concrete and memorable"
    - "Emphasise the verification step as a professional discipline, not a lack of trust in the tool — even correct traces need human confirmation in finance"
    - "Use the Concept Box as a reference anchor: students should understand that regardless of model type, the input-output pattern holds"
  assessment_checks:
    - question: "What does Claude provide when it traces a formula dependency chain?"
      expected_response: "A plain-language explanation of the formula logic with specific cell references that you can click in the sidebar to navigate directly to the source cells. The trace shows which input cells drive the output, where those inputs live across tabs, and how the calculation flows."
    - question: "Why should you always verify Claude's cell-level citations?"
      expected_response: "Because any AI-generated reference could be inaccurate — a wrong cell reference in a financial model could lead to incorrect analysis. The professional discipline is to navigate to each cited cell and confirm that the reference matches what Claude described. This verification step is what makes the trace trustworthy."
    - question: "What are the four major financial model types and what do they share in common?"
      expected_response: "Three-statement model (links income statement, balance sheet, cash flow), DCF (projects and discounts future cash flows), comps (compares companies using market multiples), and LBO (models leveraged acquisitions). All four share the same fundamental structure: input cells containing assumptions drive formula-calculated output cells."
---

# Understanding Workbooks You Didn't Build

In Lesson 1, you learned the core distinction between Claude in Excel (the embedded assistant that works inside your workbook) and Cowork with Excel (the orchestrating agent that works across applications). Now you will put the embedded assistant to work on the problem every finance professional recognises immediately: understanding a model someone else built.

Every finance professional inherits models. A colleague leaves and you inherit their rolling forecast. A client sends a financial model for due diligence. An analyst who has since moved on built the comps template your team uses and nobody fully understands how it works. In each case, the model calculates -- it produces numbers -- but its internal logic is opaque. The formulas reference cells on tabs you have never opened. The assumptions live in a sheet labelled "Assumptions (OLD)" that may or may not still be the active driver. And the person who could explain it is unavailable, gone, or was never asked to document it in the first place.

Traditional model comprehension requires manual, tedious work: tracing cell references tab by tab, following the formula chain, rebuilding the logic in your head. For a complex model, this takes hours. It is also error-prone -- you can miss a circular reference, overlook a lookup table, or misread which version of an assumption is actually driving the output.

## How Claude Traces Dependencies

Claude in Excel reads the entire open workbook -- all sheets, all formulas, all data. When you ask it about a specific cell, it traces the full dependency chain and explains the logic in plain language with cell-level citations. These citations are not decorative: clicking a cell reference in the Claude sidebar navigates Excel directly to that cell. You can verify every claim Claude makes without manually hunting through tabs.

This is Layer 1 of Claude in Excel's capabilities -- the general workbook intelligence that requires no configuration and works on any workbook. You do not need to invoke a special skill or connect to a data terminal. You open the workbook, open the Claude panel, and ask your question.

The key capability is **dependency tracing with cell-level citations**. When Claude tells you that revenue in cell C15 is driven by a unit volume assumption in cell D8 on the Assumptions tab, you can confirm that in seconds. When it tells you the unit volume comes from a SUMIF on the Sales Forecast tab pulling from a regional breakdown, you can navigate there and see for yourself.

---

> **CONCEPT BOX: What Is a Financial Model?**
>
> A financial model is a spreadsheet that represents how a business or investment performs financially, built from inputs (assumptions) that drive calculated outputs (results). The key model types:
>
> **Three-statement model:** Links the income statement, balance sheet, and cash flow statement. A change in one flows automatically through the others.
>
> **DCF model:** Projects future cash flows and discounts them to today's value to estimate what a business is worth.
>
> **Comps model:** Compares a company to similar businesses using market-based multiples to estimate relative value.
>
> **LBO model:** Models the acquisition of a company using significant debt, projecting equity returns over a holding period.
>
> All models share one structural pattern: **input cells** (blue by convention) contain assumptions you set, and **output cells** contain formulas that calculate results from those inputs. Claude in Excel reads both.

---

## Inheriting a Model Four Hours Before a Board Call

You have just joined a company's FP&A team. Your predecessor left a five-tab Excel model. Nobody documented how it works. The CFO is asking why Q3 revenue shows a 6% variance against budget. The board call is in four hours.

Open the model. Open the Claude panel. Type:

**You:** "What drives the revenue figure in cell C15 on the P&L tab?"

**Claude:** "The revenue in C15 ($4,847K) is calculated as Unit Volume (Assumptions tab, D8: 12,450 units) multiplied by Average Selling Price (Assumptions tab, D12: $389.30). The unit volume comes from the Sales Forecast tab, cell G22, a SUMIF pulling from the regional breakdown in columns H through N. The selling price uses a VLOOKUP referencing the Price List tab, range A3:C47, matching on product code. The 6% variance against budget traces to the unit volume assumption: the budget was set using 13,200 units (Budget tab, D8), versus 12,450 units in the current forecast."

In under thirty seconds: the exact formula logic, the source cells for both inputs, the location of the volume assumption, and the specific cell driving the variance.

**Your follow-up:** "Which cells on the Assumptions tab do I need to change to model a scenario where unit volume recovers to 13,000 by month-end?"

**Claude's adaptation:** "Update cell D8 on the Assumptions tab from 12,450 to 13,000. This flows through to: Sales Forecast G22 (via the SUMIF), P&L C15 (via the product formula), P&L C32 (gross profit), and Cash Flow D8 (via the linked net income line). No other cells require manual intervention."

Notice what happened in that exchange. You asked a specific question. Claude traced the dependency chain and showed you cell references you could verify. Then you refined the question based on what Claude revealed -- asking about scenario modelling because the trace showed you exactly where the variance originated. Claude adapted its response to your follow-up, mapping the cascade of changes through the model. Neither question alone produced the full picture; the iteration did.

### The Verification Step

Before you present anything from this trace to the CFO, navigate to each cell Claude cited:

1. Go to Assumptions tab, cell D8. Confirm it shows 12,450.
2. Go to Assumptions tab, cell D12. Confirm it shows $389.30.
3. Go to Sales Forecast tab, cell G22. Confirm the SUMIF formula references the regional breakdown.
4. Go to Budget tab, cell D8. Confirm it shows 13,200.

This takes under two minutes. It is the professional discipline that separates using an AI tool responsibly from using it recklessly. In finance, a wrong cell reference in a board presentation is a career-damaging error. The trace accelerates comprehension; the verification makes it trustworthy.

---

## Practice Exercise 1: Model Comprehension

**What you need:** Any multi-tab Excel workbook with formulas. A free three-statement template from Macabacus or Wall Street Prep works well. If you do not have one, any workbook with formulas spanning multiple tabs will demonstrate the same principles.

**Your tasks:**

1. Find any calculated output cell and ask Claude: "What drives the value in [cell]? Trace the full dependency chain."
2. Navigate to each cell Claude references. Confirm they are correct.
3. Ask: "If I wanted to change [one assumption], which cells would I update and what would flow automatically?"
4. Ask: "Is there any cell in this workbook that references [a source range] in an unexpected way?"

**The discipline to build:** Always trace dependencies before touching anything. A change to a seemingly isolated cell can cascade through a large model in ways you cannot anticipate without mapping the chain first.

**Target time:** 20 minutes.

---

## Try With AI

Use these prompts in Claude in Excel or your preferred AI assistant to practise model comprehension.

### Prompt 1: Dependency Mapping

```
I have an Excel workbook open with multiple tabs. Pick any output
cell on the first tab that contains a formula.

1. Tell me what the cell calculates
2. Trace the FULL dependency chain — every cell that contributes
   to this value, across all tabs
3. For each dependency, tell me: the cell reference, which tab
   it's on, and whether it's a hardcoded input or another formula
4. Draw the dependency tree showing the hierarchy from final
   output back to original inputs

After your trace, I will verify three of your cell references
by navigating to them. Tell me which three to check first and why.
```

**What you're learning:** Dependency mapping is the foundation of model comprehension. By asking Claude to distinguish between hardcoded inputs and formula-calculated cells, you build the mental model of how assumptions flow through to outputs. Verifying three references builds the professional discipline of never trusting a trace without confirmation.

### Prompt 2: Cascade Analysis

```
I want to understand how sensitive this model is to its assumptions.

1. Identify the three input cells in this workbook that affect
   the largest number of downstream formulas
2. For each one, list every output cell that would change if
   I modified the input
3. Rank them by impact: which input, if wrong, would cause the
   most significant error in the model's final outputs?
4. For the highest-impact input, show me the exact cascade path
   from input to final output, step by step

I will use this to decide which assumptions to verify first
when I inherit an unfamiliar model.
```

**What you're learning:** Not all assumptions carry equal weight. Cascade analysis teaches you to prioritise verification effort -- checking the high-impact inputs first, rather than tracing every cell in order. This is the same prioritisation that experienced financial analysts apply instinctively; the prompt makes it explicit and systematic.

### Prompt 3: Assumption Audit

```
I have inherited an Excel workbook that I did not build. Before I
use any of its outputs for a decision, I need to audit its
assumptions.

1. Scan the workbook for all hardcoded input cells — cells that
   contain a typed value rather than a formula
2. For each hardcoded input, classify it as:
   (a) A structural constant (e.g., tax rate, discount rate)
   (b) A data point that should update periodically (e.g., revenue
       figure, headcount)
   (c) A placeholder or test value that was never replaced
3. Flag any hardcoded input whose value looks stale — for example,
   a date from a prior period or a round number that suggests an
   estimate rather than an actual
4. Recommend an update sequence: which assumptions should I verify
   first, second, and third before trusting this model's outputs?
```

**What you're learning:** Inherited models often contain assumptions that were current when the model was built but have since gone stale. The distinction between structural constants, periodic data, and placeholder values determines your audit priority. This prompt builds the discipline of never trusting a model's outputs until you have verified that its inputs reflect current reality.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 3: Scenarios, Errors, and Model Building ->](./03-scenarios-errors-and-model-building.md)
