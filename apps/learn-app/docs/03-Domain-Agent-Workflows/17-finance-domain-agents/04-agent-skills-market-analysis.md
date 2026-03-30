---
sidebar_position: 4
title: "The Six Agent Skills: Market Analysis"
description: "Learn to use the Comparable Company Analysis and Discounted Cash Flow Agent Skills in Claude in Excel -- building professional comps workbooks and DCF models through structured prompts, live market data, and sensitivity analysis"
keywords:
  [
    "agent skills",
    "comparable company analysis",
    "comps",
    "discounted cash flow",
    "DCF",
    "enterprise value",
    "EV/EBITDA",
    "WACC",
    "sensitivity analysis",
    "Claude in Excel",
    "S&P Capital IQ",
    "financial modeling",
    "valuation",
    "LTM",
  ]
chapter: 17
lesson: 4
duration_minutes: 40

# HIDDEN SKILLS METADATA
skills:
  - name: "Interpret Comparable Company Analysis Output"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Data Literacy"
    measurable_at_this_level: "Student can invoke the Comps Agent Skill, review the peer group for relevance, read the multiples table to identify median and quartile statistics, and explain what an implied valuation range means for a subject company"

  - name: "Construct DCF Model with Agent Skill"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Data Literacy"
    measurable_at_this_level: "Student can invoke the DCF Agent Skill, identify the three inputs with the largest impact on equity value, and interpret the sensitivity table to explain the range of outcomes"

  - name: "Evaluate Sensitivity Analysis for Decision Support"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Analyze"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can read a WACC/terminal-growth sensitivity table, calculate the spread between best-case and worst-case equity values, and explain what that spread implies about model reliability"

learning_objectives:
  - objective: "Invoke the Comps Agent Skill and interpret the resulting multiples table to derive an implied valuation range for a subject company"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Given a comps workbook, student can identify the peer median EV/EBITDA, apply it to a subject company's EBITDA, and explain whether the subject likely trades above or below the median based on its margin profile"

  - objective: "Invoke the DCF Agent Skill and identify which assumptions most affect the equity value output"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Student can change three assumptions in the DCF model and rank them by magnitude of impact on the resulting equity value"

  - objective: "Analyse a sensitivity table to assess the reliability of a valuation conclusion and present the range to a decision-maker"
    proficiency_level: "B1"
    bloom_level: "Analyze"
    assessment_method: "Given a sensitivity table, student can identify the high and low equity values, calculate the spread, and write a one-paragraph summary explaining what the range means for an investment decision"

cognitive_load:
  new_concepts: 6
  concepts_list:
    - "Agent Skills as pre-built analytical workflows (distinct from general workbook assistance)"
    - "Comparable company analysis: peer groups, multiples, implied valuation"
    - "Enterprise value formula and why it differs from market capitalisation"
    - "LTM (trailing twelve months) as the standard comparison timeframe"
    - "WACC formula and its components (cost of equity via CAPM, cost of debt)"
    - "Sensitivity analysis: why a DCF produces a range, not a single answer"
  assessment: "6 concepts at B1 level. The lesson groups them into two natural clusters (comps concepts and DCF concepts) with concept boxes providing just-in-time definitions, keeping each cluster within the 3-5 concept working memory budget for this tier."

differentiation:
  extension_for_advanced: "After completing both exercises, build a combined valuation summary: place the comps-implied EV range and the DCF-implied equity value range side by side. Where do the ranges overlap? Where do they diverge? Write a one-paragraph 'football field' summary explaining which methodology you trust more for this company and why."
  remedial_for_struggling: "Focus on the Comps exercise only. Work through the peer group table and answer one question: 'If the median EV/EBITDA multiple is 9.2x and my company's EBITDA is $51M, what is the implied enterprise value?' If you can do that arithmetic and explain what it means, you have the core skill."

teaching_guide:
  lesson_type: "core"
  session_group: 2
  session_title: "Market Analysis Skills"
  key_points:
    - "Agent Skills are pre-built workflows that follow professional conventions -- they know the expected format, the standard multiples, and the colour-coding norms of financial deliverables"
    - "Agent Skills connect to MCP connectors configured in your Claude settings (such as S&P Global, PitchBook, Morningstar) -- the same connectors work in both Excel and Cowork"
    - "A comps analysis is not arithmetic -- the professional skill is choosing the right peer group and knowing when a company deserves to trade above or below the peer median"
    - "A DCF does not produce one answer -- it produces a range depending on assumptions that are genuinely uncertain, and the analyst's job is to anchor those assumptions with evidence"
  misconceptions:
    - "Students may think Agent Skills have their own separate data connectors -- in reality, they use the same MCP connectors configured in Claude settings, shared across Excel and Cowork"
    - "Students may treat the DCF equity value as a precise answer rather than the midpoint of a range -- the sensitivity table exists precisely because WACC and terminal growth are uncertain"
    - "Students may accept the peer group uncritically -- professional analysts always review whether the selected companies are genuinely comparable"
  discussion_prompts:
    - "Why might a company with lower margins than its peers still deserve a higher valuation multiple? What non-financial factors could justify a premium?"
    - "If a 1 percentage point change in WACC moves the DCF equity value by 15%, what does that tell you about how much confidence you should place in any single DCF output?"
  teaching_tips:
    - "Walk through the comps scenario first -- it is more intuitive and builds the vocabulary (EV, multiples, LTM) that the DCF section assumes"
    - "Emphasise the sensitivity table as the most important output of a DCF -- the single equity value number is less useful than the range it sits within"
    - "For students without data provider access, the fallback paths using SEC EDGAR and Yahoo Finance produce identical analytical workflows"
  assessment_checks:
    - question: "What is enterprise value and why is it used instead of market capitalisation in comps?"
      expected_response: "Enterprise value is market cap plus debt minus cash -- the total price to acquire a company. It is used because it is capital-structure-neutral: two companies with identical operations but different debt levels have different market caps but similar EVs, allowing fair comparison."
    - question: "What are the three main components of the WACC formula?"
      expected_response: "Cost of equity (estimated via CAPM: risk-free rate plus beta times equity risk premium), cost of debt (adjusted for tax deductibility), and the weights of each (proportion of equity and debt in the capital structure)."
    - question: "Why does a DCF produce a range rather than a single answer?"
      expected_response: "Because the key inputs -- WACC and terminal growth rate -- are estimates, not facts. Small changes in either produce large changes in the output. The sensitivity table shows the range of outcomes across plausible assumption combinations."
---

# The Six Agent Skills: Market Analysis

In Lesson 3, you used Claude in Excel's general intelligence to test scenarios, debug formulas, and build models from descriptions. Those capabilities work with any workbook and any task you describe in natural language. Now you will use something more specific: Agent Skills -- pre-built analytical workflows that know the professional conventions for a particular deliverable type.

This lesson covers two of the six Agent Skills: Comparable Company Analysis (Comps) and Discounted Cash Flow (DCF). These are the two market analysis skills -- the ones an FP&A analyst, investment banker, or equity researcher reaches for when the question is "What is this company worth?" Each skill connects to live market data through MCP connectors configured in your Claude settings, pulls financial data automatically, and produces output formatted the way financial professionals expect to see it.

## What Is an Agent Skill?

An Agent Skill is a pre-built workflow that Claude in Excel invokes to perform a specific, structured financial task. Unlike general workbook assistance -- where you describe what you want in free-form language -- Agent Skills follow established professional templates. The DCF Skill knows how to build a three-stage DCF model. The Comps Skill knows to calculate median and quartile multiples and format them with professional colour-coding.

Agent Skills connect to MCP connectors configured in your Claude settings -- such as S&P Global, PitchBook, and Morningstar. These are the same connectors available across Claude's tools. If you have S&P Global configured in your Claude settings, it works in Excel, in Cowork, and anywhere else Claude operates. The difference between using a connector in Excel versus Cowork is scope: in Excel, the connector serves analysis within one workbook; in Cowork, the same connector can serve multi-application workflows across Excel, PowerPoint, and Word.

## Skill 5: Comparable Company Analysis

The Comps Agent Skill builds a complete comparable company analysis: peer group selection, LTM financial data pull, enterprise value calculation, multiple calculation (EV/EBITDA, EV/Revenue, P/E), median and quartile statistics, and a colour-coded Excel workbook following professional conventions.

:::info What Is a Comparable Company Analysis (Comps)?
Comps values a company by comparing it to similar public companies using market-based multiples. The logic: similar businesses should trade at similar multiples.

**Common multiples:**

- **EV/EBITDA:** Most widely used. Enterprise value divided by EBITDA. Capital-structure-neutral.
- **P/E (Price-to-Earnings):** Share price divided by EPS. Simple but affected by leverage and tax.
- **EV/Revenue:** Used for pre-profit or high-growth companies.

**Process:** Identify 6-10 comparable companies. Calculate their current trading multiples. Find the median and range. Apply to your subject company's financials for an implied valuation range.

**What comps does not capture:** Company-specific factors -- management quality, competitive position, regulatory risk -- that justify trading above or below peers. Comps is a market check, not a fundamental valuation.
:::

:::info What Is Enterprise Value (EV)?
Enterprise value is what you would need to pay to acquire a company entirely, including both equity and debt.

**Formula:** EV = Market Cap + Total Debt + Preferred Stock + Minority Interest - Cash

**Why subtract cash?** You inherit the company's cash when you acquire it, which offsets part of the price. A company with $500M market cap, $200M debt, and $50M cash has an EV of $650M.

**Example:** Company A has 100M shares at $8.50. Market cap = $850M. Debt = $150M. Cash = $30M. EV = $850M + $150M - $30M = $970M. With LTM EBITDA of $97M: EV/EBITDA = 10.0x.

**Why use EV over market cap?** EV is capital-structure-neutral. Two companies with identical operations but different debt levels have different market caps but similar EVs. EV/EBITDA allows fair comparison between differently leveraged businesses.
:::

### Building a Comps Analysis for a Market Check

**Scenario:** You are an FP&A analyst. Your CEO wants a market check -- how does your company's EBITDA margin and revenue growth compare to listed peers, and at what multiple are similar companies trading?

**Your request:**
"Run a comps analysis for [your industry] companies. My subject company has LTM Revenue of $340M and LTM EBITDA of $51M."

The Comps Agent Skill activates. Claude queries your configured data connector for comparable public companies in the specified industry, pulls their LTM financial data and current market data, calculates enterprise values, and builds the comps workbook.

**Reviewing the output:** The generated workbook follows professional conventions: blue input cells for manually adjustable figures, black formula cells, green output cells for the multiples table. The peer group table shows each company's LTM Revenue, LTM EBITDA, EBITDA Margin %, EV, EV/EBITDA, and EV/Revenue. Summary statistics rows show Median, 25th Percentile, and 75th Percentile.

**Refining the peer group:**
"Based on this peer group, what is the implied enterprise value range for my company?"

**Claude's analysis:** "Your EBITDA Margin of 15.0% ($51M / $340M) is below the peer median of 18.3% and below the 25th percentile of 16.7%.

The peer group trades at: Median EV/EBITDA 9.2x, 25th percentile 8.1x, 75th percentile 11.4x.

Applied to your EBITDA of $51M: at 25th percentile (8.1x): implied EV $413M. At median (9.2x): $469M. At 75th percentile (11.4x): $581M.

Note: your EBITDA margin is below the peer 25th percentile. If a potential buyer applies a discount to reflect the margin gap, the relevant multiple may be closer to 7-8x, implying an EV of $357M-$408M. This is a judgement call depending on whether the buyer views your margin as structural or correctable."

The professional skill here is not the arithmetic -- Claude handles that in seconds. The skill is evaluating whether the peer group is right and whether your company deserves to trade at, above, or below the peer median.

:::info LTM -- Trailing Twelve Months
LTM (Last Twelve Months) refers to a company's financial performance over the most recent twelve-month period, regardless of fiscal year end. Used in comps to ensure all companies are compared on the same timeframe.

**Calculation:** LTM = Most Recent Annual Period + Most Recent Partial Period - Prior Year Comparable Partial Period.

**Example:** A company's fiscal year ends December 31. It is now October. LTM revenue = FY2024 revenue + Q1-Q3 2025 revenue - Q1-Q3 2024 revenue. This gives the twelve months ending September 30, 2025 -- the most current full year available.
:::

## Skill 6: Discounted Cash Flow Model

The DCF Agent Skill builds a complete discounted cash flow model: a projection period (typically 5-10 years), a terminal value calculation, a WACC calculation (with beta sourced from your configured data connector and customisable assumptions), a DCF equity value, and a sensitivity table showing equity value at different WACC and terminal growth rate combinations.

:::info What Is WACC?
WACC -- Weighted Average Cost of Capital -- is the discount rate used in a DCF. It represents the blended required return of both debt and equity investors, weighted by their proportions in the capital structure.

**Formula:** WACC = (E/V x Cost of Equity) + (D/V x Cost of Debt x (1 - Tax Rate))

Where E = market value of equity, D = market value of debt, V = E + D. The tax adjustment reflects that interest on debt is tax-deductible, reducing the after-tax cost of debt.

**Cost of equity** is estimated via CAPM: Cost of Equity = Risk-Free Rate + Beta x Equity Risk Premium. The risk-free rate is the 10-year Treasury yield. Beta measures the company's stock volatility relative to the market.

**Why WACC matters:** A 1 percentage point increase in WACC typically reduces DCF equity value by 10-20%. This sensitivity is why the WACC/terminal growth rate sensitivity table is always included in professional analysis.

**Example:** A company has 60% equity, 40% debt. Cost of equity: 12%. Cost of debt: 5%. Tax rate: 25%. WACC = (0.60 x 12%) + (0.40 x 5% x 0.75) = 7.2% + 1.5% = 8.7%.
:::

### Building a DCF for an Investment Committee

An investment analyst needs to present a DCF valuation tomorrow. She invokes the skill:

"Run a DCF for [company]. Use a 7-year projection period. Pull the current beta and balance sheet data from Capital IQ."

The DCF Agent Skill builds a complete three-stage DCF: projection period with revenue and margin assumptions linked to the Assumptions tab, a mid-cycle normalisation year, and a terminal value using the Gordon Growth Model. The WACC section shows the component calculation with the sourced beta. The sensitivity table shows equity value per share at WACC ranging from 7% to 11% and terminal growth from 1% to 3%.

She then adjusts the revenue growth assumption to test her bear case:

"Change the revenue CAGR assumption in B8 from 12% to 8% and show me the impact on the equity value at the mid-point WACC."

**Claude:** "Updated B8 from 12.0% to 8.0%. DCF equity value at mid-point WACC (9.3%): Reduced from $847M to $694M (-18.1%). Terminal value: $891M (from $1,124M). The sensitivity table has updated across all cells."

The DCF does not produce one answer. It produces a range of answers depending on assumptions that are genuinely uncertain. The analyst's job is to anchor those assumptions with evidence and present the range honestly.

## Exercise 5: Comps Analysis

**What you need:** Claude in Excel with a financial data connector (such as S&P Capital IQ) configured in your Claude settings. Choose any publicly traded industry you know.

:::tip No Data Connector? Use Public Sources
If you do not have S&P Capital IQ or another financial data connector, download comparable company data from SEC EDGAR (10-K filings) or Yahoo Finance and paste it into the workbook manually. The analytical process is identical -- only the data source changes.
:::

1. Invoke the Comps Skill for your chosen industry. Review the peer group Claude selects -- are these genuinely comparable companies? If not, ask Claude to swap in a specific replacement.

2. Once the table is built, ask: "Which company has the highest EBITDA margin? Which has the lowest EV/EBITDA? What do these two facts together suggest about how the market prices profitability in this sector?"

3. Find one company in the peer group that trades at an unusually high or low multiple. Ask: "Why might [company] trade at [multiple]x when the peer median is [median]x? What company-specific factors could explain the premium or discount?"

4. Add a hypothetical subject company row with your own revenue and EBITDA figures. Ask Claude to calculate the implied EV range.

**The key learning:** A comps analysis is not arithmetic. The arithmetic takes seconds. The professional skill is choosing the right peer group and knowing when a company deserves to trade above or below the peer median.

**Target time:** 45 minutes.

## Exercise 6: DCF with Sensitivity Analysis

**What you need:** Claude in Excel with a financial data connector configured in your Claude settings.

:::tip No Data Connector? Use Public Sources
Download beta and financial data from Yahoo Finance or Macrotrends.net. Enter assumptions manually on the Assumptions tab. The modelling process and sensitivity analysis are identical.
:::

1. Choose any publicly listed company you follow. Invoke the DCF Skill.

2. Once the model is built, identify the three inputs that most affect the output. Ask Claude: "Which three assumption changes in this model have the largest impact on the equity value?"

3. Test each one individually. For each, ask Claude to show you the cell-level change and the downstream impact.

4. Look at the sensitivity table. Find the combination of WACC and terminal growth rate that produces the highest value and the lowest value. What is the spread between them? What does this spread tell you about the model's reliability?

5. Ask Claude: "If the current share price is [X], what combination of WACC and terminal growth assumptions would be required to justify that price? Is that combination reasonable?"

**The key learning:** A DCF does not produce one answer. It produces a range of answers depending on assumptions that are genuinely uncertain. The analyst's job is to anchor those assumptions with evidence and present the range honestly.

**Target time:** 45 minutes.

## Try With AI

Use these prompts in Claude in Excel or your preferred AI assistant to practise the market analysis skills from this lesson.

### Prompt 1: Peer Group Evaluation

```
I have a comps table for the [INDUSTRY] sector with the following
peer companies and their EV/EBITDA multiples:

[PASTE YOUR PEER GROUP TABLE OR USE THIS EXAMPLE:
Company A: 8.2x, Company B: 9.1x, Company C: 14.7x,
Company D: 7.8x, Company E: 9.5x, Company F: 10.3x]

One company trades at a significantly different multiple from
the others. Identify which one and explain three possible
reasons for the premium or discount. For each reason, tell me
whether it would make you include or exclude that company from
the peer group.
```

**What you're learning:** The hardest part of comps is not calculating multiples -- it is deciding which companies belong in the peer group. An outlier multiple is a diagnostic signal: it could mean the company is genuinely different (exclude it) or that the market knows something the other multiples do not reflect (keep it and investigate). Practising this judgement builds the skill that separates mechanical analysis from professional analysis.

### Prompt 2: Sensitivity Table Interpretation

```
Here is a DCF sensitivity table showing equity value per share
at different WACC and terminal growth rate combinations:

[PASTE YOUR SENSITIVITY TABLE OR USE THIS EXAMPLE:
           Growth 1.5%   Growth 2.0%   Growth 2.5%
WACC 8.0%    $42.10        $47.30        $54.20
WACC 9.0%    $33.80        $37.10        $41.50
WACC 10.0%   $27.60        $29.80        $32.70]

The current share price is $35.00. Answer these questions:
1. What combination of WACC and growth rate justifies the
   current price?
2. Is that combination reasonable? Why or why not?
3. What is the spread between the highest and lowest values?
   What does that spread tell a decision-maker about how much
   confidence to place in any single number from this model?
```

**What you're learning:** A sensitivity table is the most honest output of a DCF because it shows the range of outcomes rather than pretending one number is correct. Reading a sensitivity table is a skill: you need to find where the current market price sits in the grid, assess whether those assumptions are plausible, and use the spread to communicate uncertainty to decision-makers who want a single answer.

### Prompt 3: Football Field Valuation Range

```
I have completed a comps analysis and a DCF for the same company.
Here are the results:

Comps (EV/EBITDA):
- Low peer multiple applied: implies equity value of $28/share
- Median peer multiple: implies $34/share
- High peer multiple: implies $41/share

DCF:
- Bear case (high WACC, low growth): $26/share
- Base case: $36/share
- Bull case (low WACC, high growth): $48/share

Current share price: $33

1. Build a football field summary showing the range from each
   methodology side by side
2. Where does the current price sit within each range?
3. What does the overlap (or lack of overlap) between comps
   and DCF tell me about market consensus vs intrinsic value?
4. If I were presenting this to an investment committee, what
   would my recommendation be and how would I frame the
   uncertainty?
```

**What you're learning:** A single valuation methodology gives a number; combining methodologies gives a range that communicates conviction. The football field format forces you to reconcile what the market says (comps) with what your model says (DCF). When they agree, conviction is high. When they diverge, you need to explain why — and that explanation is where professional judgment lives.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 5: The Six Agent Skills: Deal and Research &rarr;](./05-agent-skills-deal-and-research.md)
