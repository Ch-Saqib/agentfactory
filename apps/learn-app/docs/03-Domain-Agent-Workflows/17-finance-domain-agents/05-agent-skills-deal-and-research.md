---
sidebar_position: 5
title: "The Six Agent Skills: Deal and Research"
description: "Learn to use the four deal-focused and research-focused Agent Skills — Due Diligence Data Pack, Company Teaser, Earnings Analysis, and Initiating Coverage Report — and understand the non-negotiable boundaries of AI-assisted financial analysis"
keywords:
  [
    "due diligence",
    "company teaser",
    "earnings analysis",
    "initiating coverage",
    "agent skills",
    "Claude in Excel",
    "financial analysis",
    "M&A",
    "equity research",
    "quality of earnings",
    "consensus estimates",
    "blind profile",
  ]
chapter: 17
lesson: 5
duration_minutes: 45

# HIDDEN SKILLS METADATA
skills:
  - name: "Due Diligence Analysis"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can invoke the Due Diligence Skill, interpret the structured data pack, identify red flags in three-year financial trends, and distinguish between anomalies that require investigation and those that are normal features of a business model"

  - name: "Earnings Interpretation"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Analyze"
    digcomp_area: "Information-and-Data-Literacy"
    measurable_at_this_level: "Student can compare reported actuals against consensus estimates, identify beat/miss patterns across revenue, margin, and EPS, and articulate what the pattern suggests about where the business is performing ahead of or behind expectations"

  - name: "Research Framework Design"
    proficiency_level: "B1"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Digital-Content-Creation"
    measurable_at_this_level: "Student can use the Initiating Coverage Skill to generate a structural framework, evaluate peer group selections, and draft a three-sentence investment thesis distinguishing bull case from bear case"

learning_objectives:
  - objective: "Apply the Due Diligence and Company Teaser skills to produce professional deal-focused deliverables, interpreting red flags and framing anonymous business profiles"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Student invokes the Due Diligence Skill on a public company, identifies at least two red flags from the data pack, and explains whether each requires investigation or is a normal business feature"

  - objective: "Analyse post-earnings data by comparing reported actuals against consensus estimates and identifying beat/miss patterns that reveal where a business is performing ahead of or behind expectations"
    proficiency_level: "B1"
    bloom_level: "Analyze"
    assessment_method: "Student reviews an earnings output, identifies the lines that beat and missed, and articulates what the pattern suggests about the company's trajectory"

  - objective: "Apply the Initiating Coverage framework to generate a structural research report, evaluate peer group composition, and draft a concise investment thesis"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Student runs the Initiating Coverage Skill, identifies one peer to remove and one to add with justification, and writes a three-sentence thesis with bull case and key risk"

cognitive_load:
  new_concepts: 6
  concepts_list:
    - "Due diligence and quality of earnings adjustments"
    - "Red flag identification in financial data (DSO expansion, capex underinvestment, customer concentration)"
    - "M&A teaser structure and anonymisation"
    - "Earnings season, consensus estimates, and beat/miss analysis"
    - "Initiating coverage report structure and peer group evaluation"
    - "Non-negotiable boundaries of AI-assisted financial analysis"
  assessment: "6 concepts at B1 level. Students already understand Claude in Excel and the first two Agent Skills (Comps and DCF) from Lesson 4. These four skills follow the same invocation pattern, reducing novelty. The concept boxes front-load domain knowledge before each skill."

differentiation:
  extension_for_advanced: "For the Initiating Coverage exercise, go beyond the three-sentence thesis. Write a full investment thesis paragraph that includes a non-consensus view — something you believe about the company that the market is not pricing. Use the comps table and DCF from Claude to support your argument with specific multiples and growth rates."
  remedial_for_struggling: "Focus on the Due Diligence and Company Teaser skills first — these have the most structured outputs and the clearest success criteria. For Due Diligence, concentrate on the three-year trend analysis: is revenue growing faster than receivables? Is capex keeping up with depreciation? These two checks reveal most red flags."
---

# The Six Agent Skills: Deal and Research

In Lesson 4, you used the Comparable Company Analysis and DCF Model skills to produce market-analysis deliverables — valuation outputs grounded in live data with cell-level transparency. Now you will work through the remaining four Agent Skills, which shift from market analysis to deal execution and equity research. These skills produce the deliverables that investment bankers, corporate development teams, and equity research analysts create under time pressure: due diligence packs, M&A teasers, post-earnings updates, and initiating coverage frameworks.

The pattern is the same as Lesson 4. Each skill connects to the same data sources (S&P Capital IQ, PitchBook, FactSet), produces structured output with traceable cell references, and is designed to compress hours of manual work into minutes of AI-assisted analysis. What changes is the professional context: these four skills operate in situations where judgment matters more than calculation — where the analyst's job is not to produce the numbers but to decide what the numbers mean.

## Skill 7: Due Diligence Data Pack

> **What Is Due Diligence?**
>
> Due diligence ("DD") is the process of investigating a company before a transaction — an acquisition, an investment, or a lending decision. The goal is to verify that the business is what it appears to be, identify risks, and surface anything that should affect the price or terms.
>
> **Financial due diligence** focuses on the quality of earnings: is the reported EBITDA a true run-rate measure, or is it inflated by one-off items? Are revenue recognition policies consistent? Are working capital levels sustainable?
>
> **Key quality of earnings adjustments:** Add back one-time restructuring costs, non-recurring legal settlements, and management compensation above market rate (in an owner-managed business). Subtract revenue from discontinued contracts and above-normal gains on asset sales. The result is **Adjusted EBITDA** — a better proxy for ongoing profitability than reported EBITDA.
>
> **Red flags the data pack surfaces:** Revenue concentration (one customer at 40% of revenue), receivables growing faster than revenue, capex consistently below depreciation (underinvestment), or large undisclosed related-party transactions.

The Due Diligence Skill produces a structured data pack for a target company: financial summary (income statement, balance sheet, cash flow for the last three years), key ratio analysis, capital structure summary, customer and revenue concentration data where available from S&P Capital IQ, and a flagging section that surfaces anomalies requiring deeper investigation.

### Example: First-Pass DD on a Potential Acquisition Target

A corporate development analyst has been asked to do a first-pass assessment of a mid-market software company. She has the company name and three years of public filing data. She needs a structured view in two hours.

She invokes the Due Diligence Skill in Claude in Excel. Claude queries S&P Capital IQ, pulls three years of financial data, calculates key ratios, and produces the structured pack.

She then works through it in conversation:

**She asks:** "What are the most notable trends in this company's financial history over the last three years?"

**Claude:** "Three trends stand out. First, revenue has grown 18% per year but accounts receivable have grown 34% per year — DSO has expanded from 47 days to 71 days, suggesting either deteriorating collection efficiency or aggressive revenue recognition close to period-end. Second, reported EBITDA margin is 22%, but EBITDA-to-operating cash flow conversion is only 61% — significantly below the software sector median of 82%. The gap is driven by the working capital build and above-sector stock-based compensation. Third, capex has been flat at $3.2M per year while depreciation has risen to $6.8M — the company is under-investing relative to its asset base."

**She asks:** "If I were a buyer doing full diligence, what are the three questions I would most want answered before agreeing to a price?"

**Claude identifies** the receivables question (collections problem vs. revenue recognition risk), the stock-based compensation question (how SBC distorts the headline EBITDA multiple), and the customer concentration question (one customer at approximately 22% of revenue). Each answer traces back to specific cells in the data pack.

That is a professionally useful first-pass in under 30 minutes. The analyst did not calculate ratios — she interpreted them. Claude surfaced the questions. She decided which ones matter.

### Exercise 7: Due Diligence Data Pack (35 min)

**What you need:** Claude in Excel with S&P Capital IQ connected. Choose any publicly listed company with at least three years of filing history — ideally a mid-size company you know nothing about, so the exercise is genuine discovery.

1. Invoke the Due Diligence Skill. While it runs, write down three questions you already have about the company.

2. When the pack is generated, look at the three-year financial history. Ask Claude: "Are there any trends in this data that would raise questions in a due diligence process? Look specifically at receivables vs. revenue growth, capex vs. depreciation, and any year with an unusually large non-cash item."

3. Ask: "What is this company's EBITDA-to-operating cash flow conversion ratio for each of the three years? How does it compare to what you would expect for a company in this industry?"

4. If the anomalies section is populated, ask Claude to explain each one. For each, ask: "Is this a red flag that would require investigation, or a normal feature of this company's business model?"

5. Ask: "If I were a buyer and agreed to pay 10x LTM EBITDA, what would I need to believe about this company's future performance to earn a 15% return on that investment?"

**The key learning:** Due diligence is not ratio calculation. Ratios are the starting point — they surface the questions. The professional's job is to decide which questions matter, which are explainable, and which require investigation before a price can be agreed.

:::tip Fallback: Without S&P Capital IQ
Without S&P Capital IQ, use SEC EDGAR to download the company's 10-K filings for the last 3 years. Calculate the key ratios manually in Excel and ask Claude to interpret the trends.
:::

## Skill 8: Company Teaser

> **What Is an M&A Teaser?**
>
> A teaser (or "blind profile") is the first document a potential buyer receives in an M&A process. It describes the business without naming it, to gauge interest before the seller decides to share confidential information. It typically covers: industry and business overview, key financial metrics (revenue, EBITDA, growth rate), competitive differentiation, and why the business is being sold.
>
> If a buyer expresses interest after receiving the teaser, they sign a **Non-Disclosure Agreement (NDA)** and receive the full Confidential Information Memorandum (CIM) — a detailed document that includes the company's name, customer lists, projections, and management team.
>
> A well-written teaser generates enough interest to produce 15-25 NDA signings; a poorly written one generates 3-5. The difference is usually in how compellingly the business is characterised in the anonymous description — which is where Claude's language generation is most useful.

The Company Teaser Skill generates a one-to-two page blind profile for use in M&A sell-side processes. It pulls financial highlights, generates an anonymised business description, formats the output in a standard teaser structure, and produces the final document in the firm's registered template.

### Example: Preparing a Teaser for a Family-Owned Manufacturer

An M&A banker is running a sell-side process for a privately held precision manufacturer. The owner wants to test market interest before committing to a full process. The banker needs a teaser for Monday morning but it is Friday afternoon.

**He types:** "Generate a teaser for a precision components manufacturer. Key metrics: Revenue $47M growing 12% per year, EBITDA $9.4M (20% margin), 85% revenues from three end markets (aerospace, medical, defence), average customer tenure 11 years, no single customer above 18% of revenue. Location: Midwest US. Reason for sale: founder retirement after 30 years."

The Teaser Skill produces a two-page PDF: an anonymised headline, a business overview describing the company's capabilities without identifying it, the financial summary with the three-year growth trend, a competitive highlights section (long customer tenure, diversified end-market exposure, proprietary tooling), and a transaction overview section describing the process timeline.

**He then asks:** "The teaser reads as too technical in the business overview section. Rewrite it for a private equity generalist who does not know the precision manufacturing industry."

**Claude** rewrites the business overview with less technical jargon and more emphasis on the financial characteristics — recurring revenue nature of the customer relationships, the margin profile relative to industry benchmarks, and the founder-transition narrative that creates a clear rationale for the sale. The banker guided the framing; Claude executed the rewrite. The result is a document neither would have produced alone — the banker's positioning judgment combined with Claude's ability to restructure prose on demand.

### Exercise 8: Company Teaser (25 min)

**What you need:** Claude in Excel with the financial-analysis plugin installed. No real company data required — hypothetical figures work.

1. Invent a simple business: choose an industry, give it a revenue size ($10M-$200M), an EBITDA margin, a growth rate, and a reason for sale. Write these down in 3-4 sentences.

2. Invoke the Teaser Skill with this description. Review the output. Is the anonymisation effective — could a reader identify the company from the description? If yes, ask Claude to make it more generic.

3. Ask: "Rewrite the competitive highlights section to emphasise the characteristics that would be most compelling to a private equity buyer rather than a strategic acquirer."

4. Ask: "What financial information am I missing that a professional teaser would typically include? What would a sophisticated buyer want to see?"

**The key learning:** A teaser is a marketing document, not a financial model. The analytical content matters, but the framing — why this business is distinctive, why the timing makes sense, why a buyer should spend time on it — is what drives NDA signings. Claude handles the structure and drafting; the banker's judgment is in how the business is positioned.

## Skill 9: Earnings Analysis

> **Earnings Season and Consensus Estimates**
>
> Publicly traded companies report financial results quarterly. "Earnings season" refers to the six-week period after each quarter when most companies report.
>
> **Consensus estimates** are the average of analysts' published financial forecasts for a company. If the consensus expects $100M revenue and the company reports $108M, it "beat" by $8M (8%).
>
> **Why the beat/miss matters:** Stock prices often move on earnings not based on whether results are good or bad in absolute terms, but whether they are better or worse than what analysts were already expecting. A company reporting strong growth that was already expected in the price may see its stock fall if growth came in slightly below consensus — this is called "buy the rumour, sell the news."
>
> **Post-earnings workflow:** (1) Compare actuals vs. consensus on revenue, EBITDA, and EPS. (2) Update the financial model for the new actuals. (3) Revise forward estimates based on management guidance. (4) Update the price target if the valuation model changes. (5) Publish a note summarising the quarter and updated view. This workflow, previously 2-3 hours per company, completes in approximately 45 minutes with the Earnings Analysis Skill.

The Earnings Analysis Skill produces a complete post-earnings update after a company reports quarterly results. It pulls actuals from the connected data provider, compares them to consensus estimates, identifies key beats and misses, updates the financial model, and produces a structured research note ready for distribution.

This is one of the highest-frequency, highest-pressure workflows in equity research. During peak weeks an analyst may need to cover five to eight companies in a single week. The skill compresses what previously took 2-3 hours per company to approximately 45 minutes.

### Example: Post-Earnings Update at 8:30 PM on Report Night

A technology company reports Q3 results at 4:00 PM. The earnings call ends at 5:30 PM. The analyst needs a note in clients' inboxes before markets open.

**She runs:** `/earnings [company] Q3-2025`

Within two minutes, Claude produces the structured analysis:

- **Revenue:** $1.84B reported vs. $1.79B consensus (+2.8% beat). Year-over-year growth accelerating from 12.1% to 14.2%.
- **Gross margin:** 68.4% vs. 67.1% consensus (+130 bps beat). Driven by mix shift toward higher-margin cloud subscription.
- **EBITDA:** $412M vs. $389M consensus (+5.9% beat). Margin 22.4% vs. 21.7% consensus.
- **EPS:** $0.87 vs. $0.82 consensus (+6.1% beat). Adjusted for a one-time tax benefit: core EPS $0.81, a slight miss.
- **Q4 guidance:** Revenue midpoint $1.90B vs. $1.86B consensus — above consensus. EPS midpoint $0.86 vs. $0.85 consensus — in line.
- **Model update:** Full year revenue estimate moves to $7.24B. Price target moves from $142 to $149 based on updated model.

The analyst reviews, adjusts one assumption (she uses a 19x multiple, not 18x, reflecting above-sector growth), adds her qualitative commentary on international expansion, and has the note ready by 9:00 PM. The data processing took minutes. The judgment — which multiple to use, what the international expansion commentary means for the thesis — took the rest of the time.

### Exercise 9: Post-Earnings Analysis (40 min)

**What you need:** Claude in Excel with S&P Capital IQ or FactSet connected. Choose a company that has reported earnings in the last two weeks.

1. Run the Earnings Analysis Skill for the most recent quarter. Review the beats and misses. Were any surprising?

2. Ask Claude: "What does the beat/miss pattern — which lines beat and which missed — suggest about where the business is performing ahead of or behind expectations?"

3. Look at the guidance for the next quarter. Ask: "Is the guidance conservative or aggressive relative to the trend in the last three quarters? What would a company typically need to do to hit or miss this guidance?"

4. Ask: "If I owned this stock at the price before the earnings release and the stock is now up/down X% after-hours, does that movement make sense based on the results? Or does it seem like an overreaction or underreaction?"

5. Ask Claude to draft a two-paragraph client note summarising the quarter and your view. Then edit it: add your own qualitative perspective on one aspect that matters to you.

**The key learning:** Earnings analysis is a data processing task and a judgment task. The Skill handles the data processing — actuals vs. consensus, model updates, price target arithmetic. Your judgment is the qualitative framing: what this quarter means for the long-term thesis, what management credibility looks like, and whether the market's reaction is pricing the right things.

:::tip Fallback: Without a Live Data Connector
Without a live data connector, download the earnings press release from the company's investor relations page and the consensus estimates from Yahoo Finance. Paste them into Excel and ask Claude to compare.
:::

## Skill 10: Initiating Coverage Report

> **What Is an Initiating Coverage Report?**
>
> An initiating coverage report is a comprehensive equity research document — typically 25-50 pages — that introduces an analyst's view on a company to institutional investors. It includes: the investment thesis (why the stock should be bought, held, or sold), business description, industry overview, financial model (DCF, comps), valuation, key risks, and a price target with a rating.
>
> **Why initiating coverage matters:** An analyst cannot publish ongoing earnings updates, price target changes, or buy/sell recommendations on a company without first publishing an initiation. Initiations are how research franchises are built — a high-quality initiation generates significant institutional interest. A weak one gets ignored.
>
> **The analyst's job in an initiation:** The framework and models are standard. What differentiates an initiation is the insight — a non-consensus view on the company's competitive position, a financial analysis that surfaces something the market is not pricing, or a variant view on the industry. Claude handles the standard parts. The analyst supplies the insight.

The Initiating Coverage Skill produces the structural framework and populated data sections for an initiating coverage report. It generates: a company overview (business description, market position, revenue breakdown by segment), a financial summary table (three years of actuals plus two years of estimates), a linked DCF model, a comps table, an investment thesis template with bull and bear case arguments, key risks, and a price target with methodology.

Initiating coverage is the most time-intensive deliverable in equity research. A typical initiation takes 4-8 weeks and produces a 25-50 page document. The skill handles the structural setup and data population — roughly 60% of the elapsed time. The analyst contributes the investment thesis, the qualitative judgments, and the decision on which risks are material.

### Example: Initiating Coverage on a Consumer Technology Company

An equity analyst has been asked to initiate coverage on a consumer technology company that has recently gone public. She has three weeks.

**She runs:** `/initiating-coverage [company]`

Within five minutes, the Skill produces a 12-tab Excel model (three-statement financials, DCF with sensitivity table, comps table with 12 peers from S&P Capital IQ), a Word document framework with all standard sections pre-populated, and an investment thesis template.

**She asks:** "Based on the comps table, is this company expensive or cheap relative to its peer group?"

**Claude:** "On LTM EV/Revenue, the company trades at 8.4x versus the peer median of 6.1x — a 38% premium. On forward EV/Revenue, the premium narrows to 24%. The premium appears justified only if the company can sustain revenue growth above 25% for the next three years. The peer median growth rate is 14%. Of the 12 peers, only two have sustained 25%+ growth for three consecutive years."

That quantitative framing goes directly into the investment thesis section — and it took 30 seconds rather than the hour it would have taken to calculate manually across 12 peers. She then writes the qualitative sections herself: her view on the competitive moat, her assessment of management credibility, and her non-consensus thesis about the addressable market.

### Exercise 10: Initiating Coverage Framework (50 min)

**What you need:** Claude in Excel with S&P Capital IQ connected. Choose any company that has gone public within the last two years.

1. Run the Initiating Coverage Skill. Review the comps table. Are the peer group selections reasonable? Identify one company you would remove and one you would add, with your reasoning.

2. Ask Claude: "Based on the comps table, at what revenue growth rate would this company need to grow to justify its current EV/Revenue multiple, assuming the peer group maintains its current multiples?"

3. Look at the DCF model. Find the WACC assumption. Ask: "Is this WACC appropriate for a company of this size, growth profile, and capital structure? What range would you consider reasonable, and how much does the equity value change across that range?"

4. Draft a three-sentence investment thesis: one sentence describing what the company does, one sentence describing the bull case, one sentence describing the key risk.

5. Ask Claude: "What is the strongest bear case argument against this company that a sceptical investor would make? What would they need to see to be convinced the bull case was right?"

**The key learning:** An initiating coverage report is the hardest thing an equity analyst writes, and the Skill makes the easy half of it fast. The hard half — the non-consensus insight that makes the report worth reading — is entirely the analyst's work. Spend less time building the model and more time developing the view.

:::tip Fallback: Without S&P Capital IQ
Download financial data from SEC EDGAR and peer multiples from Yahoo Finance. Paste the data into Excel and ask Claude to build the comps table and DCF framework from the raw numbers.
:::

## Non-Negotiable Boundaries

Four boundaries apply to every Agent Skill in this lesson and the previous one.

**Claude does not provide investment advice.** It does not tell you whether to buy or sell, whether a valuation is attractive, or whether a deal should proceed. These judgments carry regulatory and fiduciary implications. Claude provides the analytical infrastructure; the professional provides the judgment.

**Claude makes mistakes and must be verified.** Every output — especially the Agent Skills — should be reviewed against the underlying data before it goes to a client or regulator. Cell-level citations make this verification efficient, but the responsibility for accuracy rests with the professional, not the tool.

**Claude does not validate your assumptions.** Revenue growing at 25% for ten years is a model Claude will build. Whether that assumption is reasonable is your professional judgment to apply.

**Claude does not replace an audit.** Outputs are not audited financial statements. Any output filed with a regulator or relied upon in a legal transaction requires the same professional review and sign-off it would without Claude.

These boundaries are not limitations of the current version — they are structural features of what AI-assisted financial analysis is. The skills compress hours of data processing into minutes. The judgment remains yours.

## Try With AI

Use these prompts in Claude or your preferred AI assistant to practise the skills from this lesson.

### Prompt 1: Due Diligence Red Flag Analysis

```
I am reviewing a company for a potential acquisition. Here are the
three-year trends:

- Revenue: $30M → $38M → $45M (growth: 27%, 18%)
- Accounts Receivable: $4M → $7M → $12M (growth: 75%, 71%)
- EBITDA: $6M → $7.5M → $9M (margins: 20%, 20%, 20%)
- Capex: $1.5M → $1.4M → $1.3M
- Depreciation: $2M → $2.5M → $3M
- Top customer: 35% of revenue

Identify the red flags in this data. For each red flag, explain
whether it is likely a genuine risk that requires investigation
or a normal feature of a fast-growing business. Then tell me
the three questions I would most want answered before agreeing
to a price.
```

**What you're learning:** Red flag identification is pattern recognition — receivables growing faster than revenue, capex declining while depreciation rises, and high customer concentration each tell a different story. The professional skill is distinguishing between red flags that kill a deal and red flags that affect price.

### Prompt 2: Earnings Beat/Miss Interpretation

```
A software company just reported quarterly earnings:

- Revenue: $520M reported vs $505M consensus (beat)
- Gross Margin: 71% vs 72% consensus (miss)
- Operating Income: $78M vs $81M consensus (miss)
- EPS: $0.92 vs $0.88 consensus (beat, driven by tax benefit)
- Next quarter guidance: Revenue $530-540M vs $528M consensus

The stock is down 4% after-hours despite the revenue beat.

Explain why the stock might be falling despite beating on
revenue. What is the market likely focused on? If I were
writing a client note, what would be the key message about
this quarter?
```

**What you're learning:** Earnings reactions are about expectations, not absolutes. A revenue beat with margin compression tells a different story than a revenue beat with margin expansion. The market prices the quality of the beat, not just its existence — and guidance matters as much as the quarter itself.

### Prompt 3: Company Teaser Quality Assessment

```
I need to produce a one-page company teaser for a sell-side
mandate. Here is the information I plan to include:

Company: [NAME OR DESCRIBE A COMPANY IN YOUR SECTOR]
- Industry and sub-sector positioning
- Revenue: [AMOUNT], growth rate: [%]
- EBITDA margin: [%]
- Key competitive advantages: [LIST 2-3]
- Management team tenure: [YEARS]

Review my teaser content:
1. Does the teaser tell a clear investment thesis in the
   first two sentences? If not, draft an opening that does.
2. What information is missing that a potential buyer would
   need to decide whether to sign an NDA and proceed?
3. What information should I deliberately EXCLUDE from a
   teaser (and why)?
4. Rate the teaser on a scale of 1-5 for: completeness,
   persuasiveness, and confidentiality protection.
```

**What you're learning:** A company teaser balances two competing objectives: providing enough information to attract serious buyers while withholding enough to protect the seller's identity and competitive position. The skill is not writing a summary — it is making strategic disclosure decisions about what to include, what to omit, and how to frame the opportunity without revealing too much.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 6: From Assistant to Agent →](./06-from-assistant-to-agent.md)
