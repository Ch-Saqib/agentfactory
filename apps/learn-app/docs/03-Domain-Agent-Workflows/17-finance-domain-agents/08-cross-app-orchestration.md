---
sidebar_position: 8
title: "Cross-App Orchestration"
description: "Learn how cross-app orchestration connects Excel analysis to PowerPoint deliverables in a single workflow, why structural consistency eliminates copy-paste disconnection risk, and what distinguishes an AI agent from an AI assistant at the architectural level"
keywords:
  [
    "cross-app orchestration",
    "Excel to PowerPoint",
    "Cowork",
    "structural consistency",
    "agent vs assistant",
    "financial deliverables",
    "one-pager",
    "comps analysis",
    "multi-app workflow",
    "copy-paste risk",
  ]
chapter: 17
lesson: 8
duration_minutes: 25

# HIDDEN SKILLS METADATA
skills:
  - name: "Design Cross-App Workflows"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Content Creation"
    measurable_at_this_level: "Student can describe a multi-step workflow that spans Excel and PowerPoint, identify where context must be carried between applications, and explain why a single-pass approach eliminates disconnection risk compared to manual copy-paste"

  - name: "Evaluate Structural Consistency in Multi-App Outputs"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Analyse"
    digcomp_area: "Information Literacy"
    measurable_at_this_level: "Student can compare the consistency guarantees of a manual copy-paste workflow with a cross-app orchestrated workflow and articulate the specific failure modes that orchestration eliminates"

  - name: "Distinguish Agent Architecture from Assistant Architecture"
    proficiency_level: "B1"
    category: "Conceptual"
    bloom_level: "Analyse"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can explain the architectural difference between an assistant that helps within one application and an agent that executes across applications, using the Excel-to-PowerPoint workflow as a concrete example of why the distinction matters for production deliverables"

learning_objectives:
  - objective: "Describe how cross-app orchestration connects Excel analysis to PowerPoint deliverables in a single continuous workflow, identifying where context is carried and where disconnection risk would arise in a manual process"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Student can walk through the earnings-analysis-to-one-pager workflow, naming each step and explaining what data moves between applications and why a single-pass approach prevents the specific errors that manual copy-paste introduces"

  - objective: "Analyse why structural consistency from cross-app orchestration is architecturally different from manual consistency, explaining the disconnection risk that copy-paste introduces and how single-pass production eliminates it"
    proficiency_level: "B1"
    bloom_level: "Analyse"
    assessment_method: "Student can describe a scenario where a model revision in Excel would leave a manually built PowerPoint deck with stale numbers, and explain why the orchestrated workflow does not have this failure mode"

  - objective: "Distinguish between an AI assistant embedded in a single application and an AI agent orchestrating across applications, using the cross-app workflow as evidence for why the distinction matters in professional finance deliverables"
    proficiency_level: "B1"
    bloom_level: "Analyse"
    assessment_method: "Student can state the architectural difference (scope of operation, context carriage, workflow continuity) and explain why the Excel-to-PowerPoint workflow requires agent architecture rather than assistant architecture"

cognitive_load:
  new_concepts: 4
  concepts_list:
    - "Cross-app orchestration as a single continuous workflow spanning multiple applications"
    - "Structural consistency vs manual consistency (single-pass production vs copy-paste)"
    - "Disconnection risk — how model revisions invalidate manually built deliverables"
    - "Agent vs assistant at the architectural level (workflow execution vs task help)"
  assessment: "4 concepts at B1 level — within the 7-10 cognitive limit for this tier. Students arrive with Claude in Excel experience from earlier lessons and understand the assistant-agent distinction from Lesson 1. This lesson grounds that distinction in a concrete production workflow."

differentiation:
  extension_for_advanced: "Map cross-app orchestration to a workflow in your own professional context. Identify three places where you currently copy data between applications manually. For each, describe the disconnection risk and estimate the time and error cost. Which of the three would benefit most from single-pass orchestration, and why?"
  remedial_for_struggling: "Focus on the concept box about structural consistency. The core idea is: when you copy numbers by hand, the copy can become wrong if the source changes. When the agent produces both outputs in one pass, they cannot be inconsistent. If you can explain that difference in your own words, you have the lesson's central insight."

teaching_guide:
  lesson_type: "core"
  session_group: 3
  session_title: "Cross-App Workflows"
  key_points:
    - "Cross-app orchestration connects analysis in one application to deliverables in another without manual data transfer — this is the most powerful demonstration of agent architecture in finance"
    - "The architectural advantage is structural consistency: the PowerPoint is produced from the Excel model in a single pass, so the numbers cannot be disconnected from their source"
    - "Manual copy-paste introduces disconnection risk — if the model is revised, the deck must be manually updated, and any missed update creates an error that is invisible until someone catches it"
    - "The distinction between assistant and agent is concrete here: an assistant helps you build the deck, an agent executes the workflow from model to deck"
  misconceptions:
    - "Students may think cross-app orchestration is just faster copy-paste — the architectural difference is consistency, not speed. Speed is a side effect; the elimination of disconnection risk is the structural advantage"
    - "Students may assume all Claude products support cross-app orchestration — it requires Cowork Team or Enterprise. Claude in Excel is an assistant within one workbook"
    - "Students may underestimate how common copy-paste errors are in practice — in financial services, stale numbers in client deliverables are a serious compliance and reputational risk"
  discussion_prompts:
    - "What is the most expensive copy-paste error you have seen or heard about in a professional context? How would cross-app orchestration have prevented it?"
    - "Why might some organisations still require human review of cross-app outputs even when the numbers are structurally consistent? What does the human reviewer add that the agent cannot?"
  teaching_tips:
    - "The earnings-to-one-pager scenario is the lesson's anchor — walk through it step by step to make the abstract concept concrete"
    - "The concept box on structural consistency is the intellectual core of the lesson — ensure students understand why single-pass production is architecturally different from manual consistency before moving to the exercise"
    - "For students without Cowork access, the manual alternative in the access note IS the lesson — comparing the time and error risk of manual copy-paste to orchestrated output teaches the same concept through contrast"
  assessment_checks:
    - question: "What is the disconnection risk in a manual Excel-to-PowerPoint workflow?"
      expected_response: "When numbers are copied manually from an Excel model to a PowerPoint slide, the slide becomes disconnected from the model. If the model is revised, the slide retains the old numbers unless someone remembers to update every reference. The deck can contain stale or inconsistent data without anyone realising."
    - question: "How does cross-app orchestration eliminate disconnection risk?"
      expected_response: "The agent produces the PowerPoint directly from the Excel model in a single pass. There is no copy step. The numbers in the deck correspond to the model at the time of production. If the model is revised, the workflow is re-run and a new deck is produced — consistency is structural."
    - question: "What is the architectural difference between an assistant and an agent in this context?"
      expected_response: "An assistant operates within a single application — Claude in Excel helps you work inside one workbook. An agent operates across applications — Cowork carries context from Excel to PowerPoint and executes the full workflow. The assistant helps you do tasks; the agent executes workflows."
---

# Cross-App Orchestration

In the previous lessons, you worked with Claude inside a single application — interrogating workbooks, running plugin commands, verifying formulas. Each of those tasks stayed within Excel. This lesson crosses the application boundary: a single workflow that starts with an earnings analysis in Excel and ends with a client-ready PowerPoint deck, with no manual data transfer between the two.

Cross-app orchestration is the most powerful demonstration of what it means for AI to act as an agent rather than an assistant. An assistant helps you within one application. An agent executes a workflow across applications. The difference is not just speed — it is structural consistency. When the agent carries context from Excel to PowerPoint in a single pass, the numbers in the deck cannot be disconnected from the model that produced them. That guarantee does not exist when you copy numbers by hand.

## The Earnings-to-One-Pager Workflow

Consider a concrete scenario. An equity research analyst has just run an earnings analysis on a company. She needs to send a client an updated model and a two-slide summary of the quarter. The traditional process: update the Excel model with new actuals (45 minutes), then build the PowerPoint summary manually (30 minutes). Total: 75 minutes, plus transition time and the risk of transcription errors when copying numbers from Excel to PowerPoint.

With Cowork cross-app orchestration, she runs `/earnings [company] [quarter]` in Cowork. The plugin updates the Excel model with the new actuals, calculates the beats and misses against consensus, and flags the key drivers. She then asks Claude to build a two-slide summary of the earnings analysis for a client — headline financial metrics versus consensus and prior year on slide one, three key takeaways and the impact on the price target on slide two, formatted in the firm's branded PowerPoint template.

Claude carries the analysis context — the numbers, the beats, the key drivers — from the Excel model directly into PowerPoint. The analyst reviews both the Excel model and the PowerPoint slides, makes any adjustments, and sends the client package. Two separate tasks become one continuous workflow.

:::info What Is Cross-App Orchestration?

**Cross-app orchestration** is the execution of multi-step workflows that span multiple applications. Instead of completing work in one application, manually transferring results, and continuing in another, the agent carries context across applications and produces deliverables in a single continuous pass.

**Why it matters for finance:** Professional finance deliverables almost never live in a single application. An earnings analysis starts in Excel and ends in a PowerPoint deck or a Word document. A deal process runs through Excel models, PowerPoint pitch books, and Word memos. Every manual transfer between applications introduces the risk that the output becomes disconnected from the source.

**Current status:** Excel-to-PowerPoint cross-app orchestration is available in Cowork for Team and Enterprise subscribers. It is in research preview and requires the financial-analysis plugin and PowerPoint add-in to be enabled.
:::

## Why Structural Consistency Matters

It is worth pausing on why cross-app orchestration matters beyond the time saving.

When you copy numbers from an Excel model to a PowerPoint slide manually, you introduce a point of failure: the numbers in the deck can become disconnected from the model. An updated model does not automatically update the deck. If you revise an assumption and re-run the model, you must remember to update every slide that referenced the old numbers. Miss one reference, and the deck contains stale data — a silent error that is invisible until someone catches it.

When Cowork orchestrates the Excel-to-PowerPoint workflow, the PowerPoint is produced from the model in a single pass. There is no copy-paste step. The numbers in the deck correspond to the model as it stood when the agent produced the output. If you need to revise, you run the workflow again and get a new deck. Consistency is structural rather than dependent on the analyst remembering to update every reference.

| Workflow Type | Consistency Model | Revision Handling | Error Mode |
| --- | --- | --- | --- |
| Manual copy-paste | Dependent on analyst memory | Must update every reference manually | Silent stale data |
| Cross-app orchestration | Structural (single-pass) | Re-run workflow produces fresh output | None for data transfer |

This is what it means for an AI to act as an agent rather than an assistant. An assistant helps you do the task — it might suggest what to put on the slide, but you still copy the numbers. An agent executes the workflow — it carries the numbers from the model to the deck without you switching applications or transferring anything.

:::caution Access Note

Exercise 11 below requires a Cowork Team or Enterprise subscription with the financial-analysis plugin and PowerPoint add-in enabled. If you are on a Claude Max plan or your organisation has not yet deployed Cowork, you cannot run this exercise as written.

**Alternative for Max-plan users:** Complete steps 1 and 2 using Claude in Excel alone (install the financial-services-plugins via Claude Code if available), then manually copy the three data points to a PowerPoint slide. Compare the time and error risk of that manual approach to what steps 3-4 describe. That comparison IS the lesson this exercise teaches.
:::

## Exercise 11: Cross-App Orchestration

**What you need:** Cowork Team or Enterprise with the financial-analysis plugin installed and PowerPoint add-in access.

**Target time:** 35 minutes.

**Step 1.** Run `/one-pager [company]` for any publicly listed company. Review the PowerPoint output. Check: are the financial figures sourced from the connected data provider or from Claude's training knowledge?

**Step 2.** Open the company's comps table in Excel (use the `/comps` command). Review the Excel workbook in Claude in Excel — use the sidebar and ask: "Is the EV/EBITDA formula in row 8 correctly structured? Show me the cell references."

**Step 3.** From within the same Cowork session, ask: "Take the three most relevant data points from this comps analysis and add them to the one-pager I just generated as a 'Valuation Context' section."

**Step 4.** Observe what happens: Claude carries context from the Excel comps to the PowerPoint one-pager without you switching applications or copying anything. The comps data appears in the deck sourced directly from the model.

**What to observe:** The combination of Cowork plugin (generates the output) and Claude in Excel (interrogates and verifies it) is the production pattern for financial services work. Cowork orchestrates the workflow. Claude in Excel is where you audit the model. The two architectures serve different purposes and complement each other.

## Try With AI

Use these prompts in Anthropic Cowork or your preferred AI assistant to explore cross-app orchestration concepts.

### Prompt 1: Mapping Your Cross-App Workflows

```
I work in [YOUR DOMAIN — e.g., equity research, corporate finance,
consulting, operations]. Map my typical deliverable workflows:

1. List the 3 most common deliverables I produce that span multiple
   applications (e.g., Excel model → PowerPoint deck, data analysis
   → Word report).
2. For each deliverable, identify every point where I currently
   transfer data between applications manually.
3. For each manual transfer point, describe the specific
   disconnection risk — what could go wrong if the source data
   changes after the transfer?
4. Rank the three workflows by: (a) time spent on manual transfer,
   (b) severity of disconnection risk, (c) frequency of production.
   Which workflow would benefit most from cross-app orchestration?
```

**What you're learning:** Professional deliverables rarely live in a single application. This prompt builds your ability to identify where cross-app workflows exist in your own practice and evaluate which ones carry the most disconnection risk. The ranking exercise forces you to prioritise based on impact rather than convenience — the workflow with the highest combination of frequency, time cost, and error risk is the strongest candidate for orchestration.

### Prompt 2: Designing a Cross-App Workflow Specification

```
I need to design a cross-app workflow for this scenario:
[DESCRIBE YOUR SCENARIO — e.g., "Quarterly client reporting:
pull portfolio performance from Excel, generate commentary,
produce a branded PDF report"]

Help me specify the workflow:
1. What data must be carried from the source application to
   the target application? List each data element.
2. What formatting or transformation must happen during the
   transfer? (e.g., raw numbers → formatted table, data →
   chart, model output → narrative summary)
3. What would the human review step look like? What should
   the reviewer check before the output is sent?
4. What is the rollback plan if the output contains an error?
   How would you re-run the workflow after fixing the source?
5. Draft the natural-language instruction you would give to
   Cowork to execute this workflow end-to-end.
```

**What you're learning:** Designing a cross-app workflow requires thinking about data carriage, transformation, and review — not just "move this to that." The specification exercise builds the skill of decomposing a multi-application deliverable into discrete steps that an agent can execute. The rollback question surfaces whether your workflow is re-runnable, which is essential for structural consistency.

### Prompt 3: Error Recovery Design

```
I have designed a cross-app workflow that moves data through
three stages:
1. [SOURCE APP] → extract data
2. [PROCESSING STEP] → transform and calculate
3. [TARGET APP] → format and present

The workflow ran successfully last quarter. This quarter,
the source data has changed: [DESCRIBE A REALISTIC CHANGE —
e.g., "a new business unit was added," "the chart of accounts
was restructured," "a column header was renamed"].

1. At which stage would this change cause the workflow to break
   or produce incorrect output?
2. Would the failure be silent (wrong output, no error) or loud
   (visible error message)? Silent failures are more dangerous —
   explain why for this specific scenario.
3. Design a validation check that would catch this failure before
   the output reaches the end user
4. Write a recovery procedure: once the error is detected, what
   steps restore the workflow to correct operation?
```

**What you're learning:** Cross-app workflows are brittle at their connection points. When source data changes structure — not just values — downstream steps can produce wrong outputs without raising errors. Designing for error recovery before the error occurs is the difference between a workflow that works once and a workflow that works reliably across quarters.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 9: Extracting Finance Domain Knowledge →](./09-extracting-finance-domain-knowledge.md)
