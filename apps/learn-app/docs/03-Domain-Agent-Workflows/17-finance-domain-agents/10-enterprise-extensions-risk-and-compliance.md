---
sidebar_position: 10
title: "Enterprise Extensions — Risk and Compliance"
description: "Design SKILL.md extensions for credit risk frameworks, regulatory reporting automation, investment policy statement compliance, and portfolio attribution — encoding institutional knowledge that generic plugins cannot provide"
keywords:
  [
    "enterprise extensions",
    "credit risk",
    "regulatory reporting",
    "IPS compliance",
    "portfolio attribution",
    "SKILL.md",
    "variance analysis",
    "Basel III",
    "CET1",
    "DSCR",
    "finance domain agents",
    "risk framework",
  ]
chapter: 17
lesson: 10
duration_minutes: 35

# HIDDEN SKILLS METADATA
skills:
  - name: "Design a Credit Risk SKILL.md Extension"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Content Creation"
    measurable_at_this_level: "Student can write SKILL.md instructions encoding sector-specific leverage thresholds, key credit ratios, and escalation conditions derived from institutional experience rather than textbook definitions"

  - name: "Encode Regulatory Compliance Logic in SKILL.md"
    proficiency_level: "B2"
    category: "Applied"
    bloom_level: "Analyze"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can analyze a regulatory framework (SBP, Basel III, or SEC) and translate its requirements into SKILL.md instructions with mandatory sign-off sequences and jurisdiction-specific calculation methodologies"

  - name: "Design Constraint Verification and Attribution SKILL.md Extensions"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Content Creation"
    measurable_at_this_level: "Student can write SKILL.md instructions for IPS constraint verification logic (hard caps, concentration targets, screening exclusions) and portfolio attribution decomposition that distinguish routine compliance from edge cases requiring human judgment"

learning_objectives:
  - objective: "Write SKILL.md instructions for a credit risk extension that encode sector-specific thresholds and escalation conditions from real institutional experience"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Student produces a five-instruction Principles section where each instruction references a specific ratio, threshold, or signal rather than a generic directive"

  - objective: "Analyze a regulatory framework and translate its requirements into SKILL.md instructions with jurisdiction-specific calculation methodologies and mandatory governance gates"
    proficiency_level: "B2"
    bloom_level: "Analyze"
    assessment_method: "Student identifies at least three jurisdiction-specific requirements that differ between regulatory regimes and encodes each as a conditional SKILL.md instruction"

  - objective: "Design SKILL.md constraint verification logic that routes routine compliance checks automatically and edge cases to human judgment, with documentation standards for each path"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Student produces a constraint verification sequence that distinguishes at least three categories of constraint (hard cap, target, screening exclusion) with different handling for each"

cognitive_load:
  new_concepts: 7
  concepts_list:
    - "Extension architecture: what generic plugins lack vs what extensions add"
    - "Credit ratios as SKILL.md instructions (interest coverage, net debt/EBITDA, DSCR, working capital cycle)"
    - "Variance analysis decomposition (volume, price, mix)"
    - "Regulatory capital ratios (CET1, Total Capital, Leverage Ratio)"
    - "IPS constraint categories and verification sequence"
    - "Portfolio attribution (Brinson model, return decomposition)"
    - "Jurisdiction-specific regulatory differences (SBP, Basel III, SEC)"
  assessment: "7 concepts at B1/B2 level — at the upper bound of the 7-10 range for intermediate learners. The concepts are interconnected (each is a different application of the same pattern: encoding institutional knowledge as SKILL.md instructions), which reduces effective cognitive load compared to 7 unrelated concepts."

differentiation:
  extension_for_advanced: "After completing the credit analysis exercise, write a second SKILL.md extension for either regulatory reporting or IPS compliance in your jurisdiction. Compare the two extensions: which required more institutional knowledge vs more regulatory research? What does this tell you about which extensions carry greater knowledge-loss risk when experienced staff leave?"
  remedial_for_struggling: "Focus on the credit risk extension only. Complete the five-instruction exercise using the worked example as a template. The concept boxes provide the financial definitions you need — you do not need prior credit analysis experience to complete the exercise, only the ability to translate a scenario into specific SKILL.md instructions."

teaching_guide:
  lesson_type: "core"
  session_group: 3
  session_title: "Enterprise Extensions"
  key_points:
    - "Generic plugins compute ratios correctly — extensions encode which ratios matter and what the thresholds mean in your specific context"
    - "The gap between a generic plugin and an enterprise extension is institutional knowledge: the sector-specific thresholds, the governance sequences, the judgment calls that experienced professionals make"
    - "Every extension follows the same pattern: identify what the generic plugin lacks, then write SKILL.md instructions using Chapter 16's Persona-Questions-Principles structure"
    - "Regulatory extensions carry the highest compliance urgency because applying the wrong jurisdiction's methodology produces materially incorrect filings"
  misconceptions:
    - "Students may think extensions replace the generic plugins — they layer on top, adding institutional specificity to the generic foundation"
    - "Students may write generic SKILL.md instructions ('analyze credit risk carefully') instead of specific ones ('flag interest coverage below 2.0x in non-cyclical sectors') — the exercise is designed to surface this gap"
    - "Students may assume one extension fits all jurisdictions — regulatory extensions are jurisdiction-specific by design (SBP rules differ from Basel III implementation by national regulators)"
  discussion_prompts:
    - "Which of the four extensions covered in this lesson would create the most value in your organization? Is the answer driven by operational pain, knowledge risk, or regulatory exposure?"
    - "Consider the credit analyst worked example. What would change if you wrote it for a different sector — technology lending vs commercial real estate vs trade finance?"
  teaching_tips:
    - "The concept boxes are reference material, not teaching content — students should read them to understand the financial concepts, then focus on how to encode those concepts as SKILL.md instructions"
    - "The credit analysis exercise is the most important deliverable — ensure students produce specific instructions, not textbook definitions"
  assessment_checks:
    - question: "What is the difference between a generic plugin and an enterprise extension?"
      expected_response: "A generic plugin computes standard financial metrics correctly but without institutional context. An enterprise extension adds your organization's specific thresholds, governance sequences, and judgment calls — the institutional knowledge that determines whether output is immediately usable or requires significant rework."
    - question: "Why must regulatory reporting extensions be jurisdiction-specific?"
      expected_response: "Because each regulator's implementation of Basel III (or equivalent) differs in calculation methodology, filing format, submission timeline, and materiality thresholds. Applying the wrong jurisdiction's methodology produces a materially incorrect filing — not just a formatting error."
    - question: "What does the constraint verification sequence in an IPS compliance extension check first?"
      expected_response: "Hard caps first (violation is never permissible), then concentration targets (violation requires advisor sign-off), then screening exclusions (violation requires client waiver), then liquidity requirements (violation triggers senior advisor review)."
---

# Enterprise Extensions — Risk and Compliance

In Lessons 1 through 9, you learned how Claude in Excel and Cowork's finance plugins handle standard financial workflows: model comprehension, scenario testing, comparable company analysis, and domain-specific commands for investment banking, equity research, private equity, and wealth management. These generic plugins compute ratios correctly, build structurally sound models, and produce professionally formatted deliverables. What they do not encode is what makes your firm's analysis distinctive — the sector-specific leverage thresholds your credit officers apply, the regulatory return formats your compliance team files, the IPS constraints your wealth advisors must verify before every recommendation.

This lesson covers four enterprise extensions that address the most common gaps between generic plugin capability and institutional need. Each follows the same pattern you learned in Chapter 16: identify what the generic plugin lacks, then write SKILL.md instructions using the Persona-Questions-Principles structure to close that gap. The extensions covered here — credit risk, regulatory reporting, IPS compliance, and portfolio attribution — represent the highest-impact areas where institutional knowledge encoded as SKILL.md instructions creates measurable operational value.

## What Enterprise Extensions Are

The generic plugins in Lessons 5 through 9 cover workflows common across financial organisations. They do not encode what makes your firm's analysis distinctive. Enterprise extensions address these gaps. Each extension layers on top of a generic plugin, adding institutional specificity to the generic foundation.

Every extension follows the same structure:

1. **What the generic plugin lacks** — the institutional knowledge gap
2. **What the extension adds** — the SKILL.md instructions that close it
3. **Key instructions to write** — the specific Persona, Questions, and Principles

The eleven extension areas across the chapter span credit risk, regulatory reporting, treasury, FP&A planning, M&A institutional memory, IPS compliance, sector valuation, board and IR packs, multi-entity consolidation, credit portfolio monitoring, and finance business partnering. This lesson focuses on four that carry the highest combination of compliance urgency and knowledge-loss risk.

---

:::info Concept Box: Variance Analysis

Variance analysis compares actual results against a plan (budget or forecast) or prior period to explain _why_ performance differed.

**Volume variance:** Difference explained by selling more or fewer units than planned.
**Price variance:** Difference explained by selling at a higher or lower price.
**Mix variance:** Difference explained by a different product or service mix — even if total volume and average price were on plan, a shift toward lower-margin products reduces profitability.

**Example:** Budget: 1,000 units at $100 = $100,000. Actual: 950 units at $103 = $97,850. Revenue variance: -$2,150. Volume component: 50 fewer units x $100 = -$5,000. Price component: 950 units x $3 upside = +$2,850. Total: -$2,150. A complete variance analysis always shows these components separately — the total masks a volume problem partially offset by pricing strength.

:::

---

## Extension 1: Credit Risk Framework

**What the generic plugin lacks.** Standard credit metrics without your institution's sector leverage thresholds, management quality assessment protocols, or loss-history-derived escalation conditions.

**What the extension adds.** Your firm's actual credit methodology — the specific leverage thresholds per sector, the five ratios on the first page of every credit file, the signals your experienced credit officers read as proxies for management quality.

---

:::info Concept Box: Key Credit Ratios

**Interest Coverage Ratio:** EBIT / Interest Expense. How many times operating profit covers interest payments. Below 2.0x is stressed; below 1.0x means operating income cannot cover interest.

**Net Debt / EBITDA:** Leverage measure. Debt minus cash, divided by EBITDA. Above 4.0x is typically considered highly leveraged for most industries.

**DSCR (Debt Service Coverage Ratio):** Cash available for debt service / total debt service (principal + interest). Below 1.0x means insufficient cash to meet debt obligations.

**Working Capital Ratios:**

- **DSO (Days Sales Outstanding):** (Receivables / Revenue) x 365. How quickly customers pay.
- **DPO (Days Payable Outstanding):** How long the company takes to pay suppliers.
- **DIO (Days Inventory Outstanding):** How long inventory sits before sale.

**Cash Conversion Cycle:** DSO + DIO - DPO. A shorter or negative cycle means the company collects cash from customers before paying suppliers — a sign of strong working capital management.

:::

---

**Key SKILL.md instructions to write:**

- **Sector-specific leverage thresholds** — cyclical sectors carry lower acceptable leverage than defensive sectors at the same credit grade. Your SKILL.md should specify the threshold per sector, not a single generic number.
- **The five financial ratios required on the first page of every credit file**, in your institution's format and calculation methodology.
- **Management quality signals** your experienced credit officers use as proxies for depth and reliability — the qualitative indicators that supplement the quantitative ratios.
- **Non-negotiable escalation conditions** — transaction size thresholds, heightened-risk sectors, borrowers with prior credit events. These are unconditional routing rules, not guidelines.

### Exercise 12: Credit Analysis SKILL.md

**What you need:** 30 minutes. No software required.

Apply the interview framework from Chapter 16 to a credit scenario you have observed.

1. Describe a credit situation — real or hypothetical — where the outcome was better or worse than expected. Write 200 words covering the key signals and the decision that was made.

2. Extract one credit signal from that situation. Write it as a SKILL.md instruction: _"When [condition], [action]."_

3. Identify the ratio or analysis that would surface that signal. Write it: _"Calculate [ratio] as [formula]. Flag as a concern if [threshold]."_

4. Write a five-instruction Principles section encoding the most important credit judgment calls you have seen made well or badly. Each instruction should reference a specific ratio, threshold, or signal — not a generic directive.

**The key learning:** A SKILL.md built from a real credit scenario encodes the judgment call that saved or cost money — not a textbook definition of credit analysis. The interview framework applied to credit produces instructions that reflect how experienced credit officers actually think, not how the training manual says they should. A credit agent built on this material asks the right questions. One built on generic ratios calculates them correctly and misses what matters.

---

## Extension 2: Regulatory Reporting Automation

**What the generic plugin lacks.** Standard financial statements without your regulator's specific return formats, calculation methodologies, and submission workflows.

**What the extension adds.** Returns populated from connected data with regulator-defined calculations and a mandatory sign-off sequence before submission.

---

:::info Concept Box: Regulatory Capital Ratios

Bank regulators require banks to hold minimum capital relative to their risk-weighted assets.

**CET1 Ratio (Common Equity Tier 1):** Highest quality capital (ordinary shares + retained earnings) as a percentage of risk-weighted assets. Basel III minimum: 4.5% plus 2.5% conservation buffer. Most large banks target 11-14%.

**Total Capital Ratio:** All regulatory capital tiers as a percentage of risk-weighted assets. Minimum 8% under Basel III.

**Leverage Ratio:** Tier 1 capital as a percentage of total (non-risk-weighted) exposures. Backstop measure. Minimum 3%.

**Why this matters for extensions:** Capital ratio calculations are highly specific to each regulator's Basel III implementation. SBP rules differ from the Fed's DFAST requirements and from the EBA's CRR/CRD implementation. A regulatory reporting agent applying the wrong methodology produces a materially incorrect filing.

:::

---

**Pakistan / SBP-specific note.** The State Bank of Pakistan's prudential regulations for banks and DFIs have specific requirements for capital adequacy reporting, liquidity coverage ratios, and large exposure limits. A custom SBP reporting skill encodes these formats, the quarterly submission timelines, and the materiality thresholds in SBP's Banking Supervision Department circulars.

**Key SKILL.md instructions to write:**

- **Regulator-specific calculation methodology** — which Basel III implementation applies to your institution. SBP rules, Fed rules, EBA rules, and PRA rules each produce different results from the same underlying data.
- **Return formats and filing calendars** — the specific schedules, the data fields, and the quarterly or annual submission deadlines.
- **Mandatory sign-off sequence** — who reviews what, in what order, before any filing leaves the organisation. No filing leaves without General Counsel or CCO sign-off. This is an unconditional escalation condition in every regulatory reporting SKILL.md.
- **Materiality thresholds** — what magnitude of change triggers a formal resubmission versus a commentary note in the next regular filing.

---

## Extension 6: Investment Policy Statement Compliance

**What the generic plugin lacks.** The wealth-management plugin can generate client meeting prep, run rebalancing analysis, and produce performance reports. It does not know that Client A has a 20% maximum in any single equity, that Client B prohibits tobacco and weapons, that Client C is in a restricted trading period, or that Client D's IPS requires a minimum 30% fixed income allocation regardless of market conditions. Without these constraints, every portfolio recommendation is analytically sound and potentially non-compliant.

**What the extension adds.** A mandatory IPS compliance layer that runs before any portfolio recommendation reaches the client — verifying IPS constraints, flagging violations, documenting the compliance check, and routing edge cases to advisor judgment. The compliance check is not optional and not skippable.

---

:::info Concept Box: What Is an Investment Policy Statement (IPS)?

An IPS is a document that defines the investment objectives, constraints, and governance for a client's portfolio. It is the contract between the advisor and the client on how the portfolio will be managed.

**Standard IPS sections:** Investment objectives (return target, income requirements, time horizon), risk tolerance (maximum drawdown, volatility tolerance), constraints (prohibited securities, concentration limits, liquidity requirements, ESG screens), and governance (how changes to the IPS are authorised, review frequency).

**Why IPS compliance is non-trivial:** A typical wealth management firm manages hundreds or thousands of client portfolios, each with a unique IPS. Remembering every constraint for every client is not a realistic expectation for a human advisor with a large book. The IPS compliance extension automates this: the client's constraints are encoded once and verified automatically with every recommendation.

:::

---

**Key SKILL.md instructions to write:**

- **Client constraint database structure** — how each client's IPS constraints are encoded: the format for concentration limits (hard cap vs target vs floor), the taxonomy for excluded securities (individual securities vs sectors vs ESG screens), the format for liquidity requirements, and how restricted period rules are handled.
- **Constraint verification sequence** — the order in which constraints are checked: hard caps first (violation is never permissible), then concentration targets (violation requires advisor sign-off), then screening exclusions (violation requires client waiver), then liquidity requirements (violation triggers senior advisor review).
- **Edge case routing** — the conditions requiring advisor judgment rather than automated compliance: when a constraint appears to conflict with the client's stated return objective, when a market event causes a position to breach a concentration limit through appreciation rather than trading, when a client requests a trade that would violate their own IPS.
- **Documentation standards** — the minimum documentation for every recommendation: the IPS constraint check result, the advisor's confirmation, and — for any case requiring judgment — the advisor's written rationale. This documentation is the evidence of fiduciary compliance in any regulatory examination.

---

## Extension 10: Portfolio Attribution and Risk Decomposition

**What the generic plugin lacks.** The generic portfolio reporting commands produce performance numbers — total return, benchmark-relative return, sector weightings. They do not decompose that performance into the decisions that produced it. A portfolio manager who sees "+2.3% relative to benchmark" does not know whether that came from being overweight in the right sectors (allocation), picking the right securities within those sectors (selection), or a combination of the two. Without attribution, performance reporting is a scoreboard without a game analysis.

**What the extension adds.** A portfolio attribution skill that decomposes total return into allocation, selection, and interaction effects using the Brinson attribution model — and a risk decomposition layer that maps portfolio risk to its factor sources.

---

:::info Concept Box: Attribution Analysis

**Brinson Attribution** decomposes the difference between portfolio return and benchmark return into three components:

- **Allocation effect:** The value added (or lost) by overweighting or underweighting sectors relative to the benchmark. If you overweighted technology and technology outperformed, your allocation to technology added value.
- **Selection effect:** The value added by picking securities within a sector that outperformed or underperformed that sector's benchmark return. If your technology stocks returned 15% while the benchmark technology sector returned 12%, your selection within technology added 3%.
- **Interaction effect:** The combined effect of allocation and selection decisions — the additional return from overweighting a sector in which you also had superior stock selection.

**Total Return Decomposition:** Portfolio return = benchmark return + allocation effect + selection effect + interaction effect. This decomposition tells the portfolio manager _why_ performance differed from the benchmark, not just _how much_ it differed.

:::

---

**Key SKILL.md instructions to write:**

- **Attribution methodology** — which Brinson variant your firm uses (arithmetic vs geometric, single-period vs multi-period linking), the benchmark against which attribution is calculated, and the sector classification system (GICS, ICB, or a custom taxonomy).
- **Risk factor decomposition** — the factors your firm tracks (market beta, sector, style, currency, credit, duration) and the methodology for isolating each factor's contribution to portfolio risk and return.
- **Reporting format** — how attribution results are presented to portfolio managers vs clients vs investment committees. Each audience requires different granularity and different emphasis.
- **Threshold alerts** — the allocation or selection effects that trigger review: a sector allocation drift beyond the permitted range, a selection effect that indicates a systematic stock-picking pattern (positive or negative), or a tracking error that exceeds the mandate's permitted range.

---

## The Pattern Across All Extensions

Every extension in this lesson follows the same three-step pattern:

| Step                           | What You Do                                                                       | Why It Matters                                                                                  |
| ------------------------------ | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1. Identify the gap            | Name what the generic plugin computes correctly but without institutional context | Prevents building an extension that duplicates the plugin instead of extending it               |
| 2. Write specific instructions | Encode thresholds, sequences, and escalation conditions from real experience      | Ensures the extension reflects how experienced professionals actually work                      |
| 3. Add governance gates        | Define who reviews what before output reaches production                          | Protects against compliance violations that correct calculations with wrong methodology produce |

The four extensions in this lesson share a common thread: each encodes knowledge that is institutional (specific to your organisation), jurisdictional (specific to your regulator), or both. A generic plugin applies the same logic everywhere. An extension applies _your_ logic, in _your_ context, subject to _your_ governance requirements.

## Try With AI

### Prompt 1: Credit Extension Stress Test

```
I am building a credit risk SKILL.md extension for my
organisation. I have written five Principles encoding
our key credit judgment calls.

Here are my five Principles:
[PASTE YOUR FIVE PRINCIPLES FROM THE EXERCISE]

For each Principle:
1. Write a test scenario where the Principle should fire
2. Write a test scenario where the Principle should NOT fire
   (edge case near the boundary)
3. Predict how my current instruction would handle the
   edge case
4. If the instruction is too vague to handle the edge case
   correctly, suggest a more specific version

Focus on the boundaries — the thresholds where
reasonable professionals might disagree on the right call.
```

**What you're learning:** The boundary between "fire" and "do not fire" is where SKILL.md instructions reveal their precision. A Principle that says "flag high leverage" is untestable. A Principle that says "flag net debt/EBITDA above 4.0x in non-cyclical sectors, above 3.0x in cyclical sectors" is testable — and the AI can generate edge cases at 3.9x in a sector that sits between cyclical and non-cyclical. These boundary scenarios are the most diagnostic test of whether your instructions encode real institutional judgment or textbook generalities.

### Prompt 2: Regulatory Extension Gap Analysis

```
I need to build a regulatory reporting SKILL.md extension
for [YOUR JURISDICTION AND REGULATOR].

Help me identify the jurisdiction-specific requirements
that a generic Basel III implementation would miss:

1. What calculation methodology differences exist between
   my regulator's implementation and the generic Basel III
   framework?
2. What filing formats and submission deadlines are
   specific to my jurisdiction?
3. What governance gates (sign-off sequences) does my
   regulator require before submission?
4. What materiality thresholds trigger special reporting
   requirements?

For each gap you identify, draft a SKILL.md instruction
that encodes the jurisdiction-specific requirement.
Format each as: "When [condition], [action]."
```

**What you're learning:** Regulatory reporting is where the gap between generic and institution-specific is widest — and where the consequences of using the wrong methodology are most severe. Using AI to systematically identify jurisdiction-specific requirements accelerates the research phase of building the extension. The AI surfaces regulatory requirements you might miss; your expertise validates which ones apply to your institution and how they interact with your existing processes.

### Prompt 3: Investment Policy Compliance Check

```
I need to build an IPS (Investment Policy Statement) compliance
extension. Here is my fund's policy:

- Maximum single-issuer concentration: [X%]
- Minimum credit quality: [e.g., BBB-/Baa3]
- Asset class limits: equities [X%], fixed income [X%],
  alternatives [X%]
- Currency exposure: unhedged foreign currency capped at [X%]

[USE YOUR ACTUAL POLICY OR THESE DEFAULTS:
Single issuer: 5%, Min credit: BBB-, Equities: 60%,
Fixed Income: 30%, Alternatives: 15%, Unhedged FX: 10%]

1. Draft four SKILL.md instructions that encode each policy
   limit as a testable rule
2. For each rule, write one scenario where a trade would
   trigger the limit and should be flagged
3. For each rule, write one edge case near the boundary — a
   trade that is technically compliant but warrants a warning
4. Design the escalation path: when a limit is breached, who
   is notified, in what order, and what information must the
   notification contain?
```

**What you're learning:** IPS compliance is the most operationally critical extension because a breach can trigger regulatory consequences. The discipline of encoding policy limits as testable rules — with explicit boundary cases and escalation paths — ensures the agent catches violations before they become compliance events. The edge cases near boundaries are where professional judgment matters most.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 11: Enterprise Extensions — Operations and Strategy →](./11-enterprise-extensions-operations-and-strategy.md)
