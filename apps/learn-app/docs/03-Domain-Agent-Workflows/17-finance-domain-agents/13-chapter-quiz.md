---
sidebar_position: 13
title: "Chapter 17: Finance Domain Agents Quiz"
---

# Chapter 17: Finance Domain Agents Quiz

Test your understanding of finance domain agents — from Claude in Excel as an embedded assistant through Cowork as an orchestrating agent to enterprise extensions that encode your institution's specific knowledge.

<Quiz
title="Chapter 17: Finance Domain Agents Assessment"
questions={[
{
question: "A junior analyst asks: 'What is the difference between Claude in Excel and Cowork? They both use AI for finance.' A senior colleague who has completed Chapter 17 gives a precise architectural answer. Which response is correct?",
options: [
"Claude in Excel is an embedded assistant operating within a single workbook; Cowork is an orchestrating agent operating across multiple applications — they share the same MCP connector ecosystem but operate at different scope",
"Claude in Excel is a free tool while Cowork is a paid enterprise product with different underlying technology",
"Claude in Excel handles spreadsheets and Cowork handles presentations — they are separate products with separate connectors",
"Cowork is a newer version of Claude in Excel that replaces it with more features"
],
correctOption: 0,
explanation: "Lesson 1 establishes the core architectural distinction: Claude in Excel is an embedded assistant that works within a single workbook, while Cowork is an orchestrating agent that works across multiple applications. The critical insight is that they share the same MCP connector ecosystem — the difference is scope, not infrastructure. Option B is wrong because the distinction is architectural, not pricing-based. Option C incorrectly separates them into different product categories. Option D is wrong because Cowork does not replace Claude in Excel; they are complementary layers.",
source: "Lesson 1: The Assistant and the Agent"
},
{
question: "A finance team is evaluating which Claude plans support Claude in Excel. A team member claims: 'You need at least a Max plan to use Claude in Excel.' Is this correct, and what is the accurate plan availability?",
options: [
"Incorrect — Claude in Excel is available on Pro, Max, Team, and Enterprise (beta) plans",
"Correct — Claude in Excel requires Max or higher because of the computational demands of financial modelling",
"Incorrect — Claude in Excel is available on all plans including the free tier",
"Correct — only Enterprise plans include Claude in Excel because it requires MCP connectors"
],
correctOption: 0,
explanation: "Lesson 1 explicitly states that Claude in Excel is available on Pro, Max, Team, and Enterprise (beta) plans. The team member's claim is incorrect because Pro is sufficient. Option B invents a computational requirement that does not exist. Option C is wrong because the free tier is not listed. Option D incorrectly restricts availability to Enterprise only.",
source: "Lesson 1: The Assistant and the Agent"
},
{
question: "A portfolio manager opens a colleague's complex financial model for the first time and asks Claude to help understand it. Claude responds with dependency traces showing cell-level citations. What is the professional value of these citations?",
options: [
"They allow the portfolio manager to click through to the exact cells Claude references, verifying each claim against the actual workbook data rather than trusting the AI's interpretation",
"They make the output look more professional for client presentations",
"They help Claude process the spreadsheet faster by indexing cell locations",
"They are required by regulatory compliance for all AI-assisted financial analysis"
],
correctOption: 0,
explanation: "Lesson 2 emphasises that cell-level citations are clickable references that allow the user to verify each claim Claude makes against the actual workbook data. This establishes verification as a professional discipline — the citations exist so you never need to trust the AI's interpretation without checking. Option B confuses verification with presentation. Option C misidentifies the purpose as performance optimisation. Option D invents a regulatory requirement.",
source: "Lesson 2: Understanding Workbooks You Didn't Build"
},
{
question: "An analyst asks Claude to identify the type of financial model in a workbook. Claude responds that it is a three-statement model. The analyst wants to verify this classification. According to the chapter, what are the four financial model types Claude can identify?",
options: [
"Three-statement model, discounted cash flow (DCF), comparable company analysis (comps), and leveraged buyout (LBO)",
"Balance sheet, income statement, cash flow statement, and equity model",
"Revenue model, cost model, profitability model, and valuation model",
"Static model, dynamic model, scenario model, and Monte Carlo simulation"
],
correctOption: 0,
explanation: "Lesson 2 identifies the four financial model types as three-statement, DCF, comps, and LBO. These represent the standard categories of financial models that Claude can recognise and work with. Option B lists financial statements, not model types. Option C and D invent categories not covered in the chapter.",
source: "Lesson 2: Understanding Workbooks You Didn't Build"
},
{
question: "An analyst runs a scenario test where revenue drops 15% and COGS increases 8%. Claude shows that the combined EBITDA impact is worse than the sum of the two individual impacts. The analyst is confused. What explains this?",
options: [
"Combined scenario impacts are non-additive — they compound because each change affects the base on which the other operates, so the combined effect exceeds the arithmetic sum of individual effects",
"Claude made a calculation error when combining the two scenarios",
"The model has a circular reference that amplifies the combined effect",
"The analyst forgot to reset the first scenario before applying the second one"
],
correctOption: 0,
explanation: "Lesson 3 explains that combined impacts are non-additive because the changes compound. When revenue drops 15% and COGS rises 8%, the COGS increase applies to a different revenue base than in isolation, producing a combined effect that exceeds the sum of the individual effects. Option B incorrectly attributes the result to an error. Option C invents a circular reference problem. Option D describes a procedural mistake, not the mathematical principle at work.",
source: "Lesson 3: Scenarios, Errors, and Model Building"
},
{
question: "A financial analyst notices that a SUM formula in a workbook returns a number that seems too low. The cells in the range appear to contain numbers, but some are left-aligned. What is the most likely cause?",
options: [
"Some cells contain numbers formatted as text — they appear numeric but SUM ignores them because they are stored as text strings, and the left-alignment is the visual indicator",
"The SUM formula has a syntax error in its range reference",
"The workbook is corrupted and needs to be repaired",
"Excel's SUM function has a known bug with certain number formats"
],
correctOption: 0,
explanation: "Lesson 3 identifies the text-number formatting mismatch as one of the most dangerous invisible errors in spreadsheets. Numbers stored as text are left-aligned (genuine numbers are right-aligned), and SUM silently ignores them. There is no error message — the formula returns a result that is simply wrong. This is why Claude flags left-aligned numbers in a SUM range as a potential problem. Option B, C, and D invent causes that do not match the described symptom.",
source: "Lesson 3: Scenarios, Errors, and Model Building"
},
{
question: "When asking Claude to build a financial model from a description, the chapter emphasises that one factor determines the quality of the resulting model more than any other. What is it?",
options: [
"The quality of the specification — a vague description produces a generic model, while a precise specification with assumptions, time horizon, and key drivers produces a model that reflects the analyst's professional judgement",
"The size of the Claude model used — Opus 4.6 produces better models than Sonnet 4.6",
"The complexity of the Excel workbook — simpler workbooks produce more accurate models",
"The number of data sources connected through MCP connectors"
],
correctOption: 0,
explanation: "Lesson 3 establishes that specification quality equals model quality. A vague request like 'build me a DCF' produces a generic template, while a detailed specification that includes assumptions, time horizons, key drivers, and output requirements produces a model aligned to the analyst's professional judgement. Option B oversimplifies model selection. Option C confuses workbook complexity with specification quality. Option D conflates data connectivity with model design.",
source: "Lesson 3: Scenarios, Errors, and Model Building"
},
{
question: "The Comparable Company Analysis Agent Skill generates a comps table. An analyst reviewing the output notices the peer group includes a company from a different industry. What does the chapter say is the professional skill the analyst must apply?",
options: [
"Peer group evaluation — the analyst must assess whether each company in the peer group is genuinely comparable, because the Agent Skill selects peers algorithmically but cannot apply the analyst's contextual judgement about business model similarity",
"The analyst should remove the company and re-run the skill without changing any parameters",
"The analyst should switch to the DCF Agent Skill instead, which does not require peer selection",
"The analyst should report the error to Anthropic's support team for correction"
],
correctOption: 0,
explanation: "Lesson 4 identifies peer group evaluation as a professional skill that the analyst must apply to any comps output. The Agent Skill selects peers based on available data, but the analyst's contextual knowledge — understanding business models, competitive dynamics, and market positioning — is what determines whether a peer is genuinely comparable. Option B skips the professional judgement step. Option C avoids the issue. Option D treats a judgement call as a software bug.",
source: "Lesson 4: Agent Skills — Market Analysis"
},
{
question: "A junior analyst asks: 'What is enterprise value and how does it differ from market capitalisation?' According to the chapter's concept explanation, which formula is correct?",
options: [
"Enterprise Value = Market Capitalisation + Total Debt − Cash and Cash Equivalents — it represents the total price to acquire a company, including the obligation to assume its debt offset by the cash you would receive",
"Enterprise Value = Market Capitalisation − Total Debt + Cash — it represents the equity value adjusted for leverage",
"Enterprise Value = Market Capitalisation × Price-to-Earnings ratio — it represents the market's valuation of future earnings",
"Enterprise Value = Total Assets − Total Liabilities — it represents the book value of the company"
],
correctOption: 0,
explanation: "Lesson 4 defines enterprise value as Market Cap + Debt − Cash. The intuition is that if you buy a company, you pay the market cap (equity price), assume its debt obligations (adding debt), but receive its cash (subtracting cash). Option B reverses the debt and cash signs. Option C confuses enterprise value with a P/E-based metric. Option D describes book value, which is an accounting concept, not a market valuation.",
source: "Lesson 4: Agent Skills — Market Analysis"
},
{
question: "The DCF Agent Skill produces a valuation with a sensitivity table. The chapter describes this table as the most important output of the entire DCF analysis. Why?",
options: [
"Because a single DCF value implies false precision — the sensitivity table shows how the valuation changes across ranges of WACC and terminal growth rate assumptions, revealing which assumptions the valuation is most sensitive to",
"Because regulators require sensitivity tables for all DCF valuations submitted in official filings",
"Because the sensitivity table is the only output that clients understand without financial training",
"Because Claude cannot produce a single valuation number accurately enough to be useful"
],
correctOption: 0,
explanation: "Lesson 4 explains that a single DCF number implies a precision that does not exist. The sensitivity table varies WACC and terminal growth rate across plausible ranges, showing how the valuation changes with different assumptions. This reveals which assumptions drive the most value variation, allowing the analyst to focus diligence on those inputs. Option B invents a regulatory requirement. Option C underestimates client sophistication. Option D mischaracterises Claude's capabilities.",
source: "Lesson 4: Agent Skills — Market Analysis"
},
{
question: "During a due diligence review, the Due Diligence Data Pack Agent Skill flags three red flags in a target company's financials. Which of the following is identified in the chapter as a genuine due diligence red flag?",
options: [
"Days Sales Outstanding (DSO) expanding quarter over quarter — suggesting the company is booking revenue but struggling to collect cash, which may indicate revenue quality issues",
"Revenue growing faster than the industry average — suggesting the company is gaining market share too quickly",
"The company's headquarters being located in a different country from its primary market",
"The company having more than five board members, which suggests excessive governance overhead"
],
correctOption: 0,
explanation: "Lesson 5 identifies expanding DSO as a red flag because it suggests the company is recognising revenue but having difficulty collecting the associated cash. This pattern can indicate aggressive revenue recognition or deteriorating customer creditworthiness. Option B misidentifies growth as a red flag. Option C and D are not financial red flags relevant to due diligence.",
source: "Lesson 5: Agent Skills — Deal and Research"
},
{
question: "The chapter identifies four non-negotiable boundaries when using Claude's finance Agent Skills. A colleague says: 'Claude validated our investment thesis, so we can proceed with the acquisition.' Which boundary does this violate?",
options: [
"Claude does not provide investment advice — it generates analysis that supports human decision-making, but the investment decision and its consequences remain entirely with the human professional",
"Claude cannot process acquisition documents because they exceed the context window",
"Claude requires a second AI model to validate investment theses before they can be acted upon",
"Claude's analysis is only valid for public companies, not private acquisition targets"
],
correctOption: 0,
explanation: "Lesson 5 establishes four non-negotiable boundaries, the first being that Claude does not provide investment advice. Treating Claude's output as validation of an investment thesis conflates analysis with advice. Claude generates structured analysis; the professional applies judgement and bears responsibility for the decision. Option B invents a technical limitation. Option C invents a validation requirement. Option D incorrectly restricts Claude's scope.",
source: "Lesson 5: Agent Skills — Deal and Research"
},
{
question: "A security-conscious IT manager asks about risks of using Claude in Excel with spreadsheets from external sources. The chapter includes a specific security warning. What does it say?",
options: [
"Spreadsheets from untrusted sources could contain prompt injection attacks — malicious instructions hidden in cell values, named ranges, or conditional formatting rules that attempt to manipulate Claude's behaviour when it reads the workbook",
"External spreadsheets may contain macros that conflict with Claude's MCP connectors",
"Claude cannot read spreadsheets from external sources due to file format compatibility issues",
"The only risk is data leakage — Claude might send the spreadsheet contents to external servers"
],
correctOption: 0,
explanation: "Lesson 1 includes an explicit security warning about prompt injection in spreadsheets. Malicious actors can embed instructions in cell values, named ranges, or conditional formatting that attempt to manipulate Claude when it processes the workbook. This is a real attack vector because Claude reads all workbook content as context. Option B confuses macros with prompt injection. Option C incorrectly claims a compatibility limitation. Option D identifies only one risk and mischaracterises it.",
source: "Lesson 1: The Assistant and the Agent"
},
{
question: "A finance team adopts Cowork and notices that some capabilities activate automatically while others must be explicitly requested. What is the architectural distinction the chapter draws between these two types?",
options: [
"Skills are passive capabilities that activate automatically when relevant context is detected; commands are active capabilities that must be explicitly invoked by the user — this distinction determines how the agent integrates into workflows",
"Skills are for junior analysts and commands are for senior analysts, reflecting different permission levels",
"Skills handle text processing and commands handle numerical calculations, reflecting different computational requirements",
"Skills are free features and commands are premium features that require additional licensing"
],
correctOption: 0,
explanation: "Lesson 6 establishes the architectural distinction between skills (passive, auto-triggered by context) and commands (active, explicitly invoked). Skills activate when Cowork detects relevant context — for example, audit-support activating when compliance-related content is being processed. Commands must be explicitly called — for example, /journal-entry to generate a specific deliverable. Option B invents a permission hierarchy. Option C invents a processing distinction. Option D invents a pricing model.",
source: "Lesson 6: From Assistant to Agent"
},
{
question: "The knowledge-work-plugins/finance plugin includes category placeholders like ~~erp and ~~data warehouse in its MCP configuration. A new Cowork user asks what these placeholders mean. What is the correct explanation?",
options: [
"They are connection points where an organisation's IT team configures the specific systems — ~~erp becomes SAP, Oracle, or NetSuite depending on the institution; ~~data warehouse becomes Snowflake, BigQuery, or Redshift — making the plugin architecture-agnostic",
"They are error codes indicating that the MCP connectors failed to load properly",
"They are placeholder names for future features that Anthropic has not yet developed",
"They are security classifications that restrict which users can access each connector"
],
correctOption: 0,
explanation: "Lesson 6 explains that category placeholders like ~~erp and ~~data warehouse are architecture-agnostic connection points. The plugin defines what data it needs (ERP transactions, warehouse queries), and the IT team maps these to the organisation's specific systems during deployment. This allows the same plugin to work across different technology stacks. Option B misidentifies them as error codes. Option C treats them as future features. Option D confuses data connectivity with security classification.",
source: "Lesson 6: From Assistant to Agent"
},
{
question: "A corporate finance team uses the knowledge-work-plugins/finance plugin for month-end close. The chapter describes a six-day workflow. On Day 1, the team runs /journal-entry. What happens on Day 2?",
options: [
"Reconciliation — the reconciliation skill activates to match posted entries against source systems, and the team runs /reconciliation for any items that need formal investigation",
"The team runs /income-statement to generate the final income statement for the period",
"The team conducts the SOX compliance testing using /sox-testing",
"The team prepares the variance analysis comparing actuals to budget"
],
correctOption: 0,
explanation: "Lesson 6 describes the month-end close workflow sequentially: Day 1 is journal entries, Day 2 is reconciliation. The reconciliation skill activates passively to match entries against source systems, and the /reconciliation command is used for items requiring formal investigation. Option B (income statement) occurs on Day 3. Option C (SOX testing) occurs on Day 5. Option D (variance analysis) occurs on Day 4.",
source: "Lesson 6: From Assistant to Agent"
},
{
question: "The financial-services-plugins suite is described as having a specific scale. How many skills, commands, and MCP connector families does the full suite include?",
options: [
"41 skills, 38 commands, and 11 MCP connector families",
"6 skills, 5 commands, and 3 MCP connector families",
"100 skills, 50 commands, and 20 MCP connector families",
"15 skills, 15 commands, and 5 MCP connector families"
],
correctOption: 0,
explanation: "Lesson 7 states that the financial-services-plugins suite includes 41 skills, 38 commands, and 11 MCP connector families across the core plugin and its add-ons. This represents a substantial professional toolkit. Option B describes the smaller knowledge-work-plugins/finance plugin. Option C and D invent numbers not stated in the chapter.",
source: "Lesson 7: The Financial-Services Plugin Suite"
},
{
question: "A new Cowork deployment team installs the investment-banking add-on plugin before installing the core financial-analysis plugin. The system does not function correctly. Why?",
options: [
"The chapter specifies a mandatory install order: the core financial-analysis plugin must be installed first because add-on plugins depend on its base skills, commands, and MCP connectors — installing add-ons first creates unresolved dependencies",
"The investment-banking plugin is incompatible with Cowork and can only be used in Claude in Excel",
"The team's Cowork licence does not include investment banking features",
"Add-on plugins must be installed alphabetically to avoid naming conflicts"
],
correctOption: 0,
explanation: "Lesson 7 explicitly states that the core financial-analysis plugin must be installed first (mandatory install order). Add-on plugins (investment-banking, equity-research, private-equity, wealth-management) depend on the base skills, commands, and MCP connectors provided by the core. Installing add-ons without the core creates unresolved dependencies. Option B invents a platform restriction. Option C invents a licence limitation. Option D invents an alphabetical requirement.",
source: "Lesson 7: The Financial-Services Plugin Suite"
},
{
question: "A leveraged buyout (LBO) model is described in the chapter. What is the core question an LBO model answers?",
options: [
"Whether a private equity firm can acquire a company using a combination of debt and equity, operate it for a defined period, and sell it at a return that justifies the investment — the model tests the viability of the debt structure against projected cash flows",
"Whether a company's stock price will increase or decrease over the next twelve months",
"Whether a company should issue new shares to fund an expansion project",
"Whether a company's existing debt should be refinanced at current market rates"
],
correctOption: 0,
explanation: "Lesson 7 explains that an LBO model tests whether a leveraged acquisition is financially viable. The model structures the acquisition with a combination of debt and equity, projects the company's cash flows to service the debt, and calculates the return at exit. The core question is whether the debt can be serviced and the return justifies the risk. Option B describes stock analysis. Option C describes equity issuance. Option D describes debt refinancing.",
source: "Lesson 7: The Financial-Services Plugin Suite"
},
{
question: "A deal team uses Cowork to build a client presentation. The agent pulls analysis from Excel, structures it in PowerPoint, and produces a complete deck in a single workflow. The chapter identifies a key advantage of this approach over manual deck-building. What is it?",
options: [
"Structural consistency — because a single agent pass ensures that every number, chart, and commentary in the presentation reflects the same analytical snapshot, eliminating the disconnection risk of manual copy-paste between applications",
"The presentation is automatically formatted with the firm's brand guidelines",
"The agent produces presentations faster than any human analyst could",
"The presentation includes interactive elements that static PowerPoint cannot"
],
correctOption: 0,
explanation: "Lesson 8 identifies structural consistency as the key advantage of cross-app orchestration. When an agent carries context from Excel analysis through to PowerPoint presentation in a single pass, every element reflects the same data state. Manual deck-building introduces disconnection risk — numbers can change in the model after they have been pasted into slides, creating inconsistencies. Option B is about formatting, not consistency. Option C focuses on speed rather than the architectural advantage. Option D invents interactive capabilities.",
source: "Lesson 8: Cross-App Orchestration"
},
{
question: "The chapter warns about 'disconnection risk' in manually built presentations. What exactly is this risk?",
options: [
"Data in the Excel model changes after numbers have been copied into the PowerPoint deck, creating a presentation where some figures reflect the current model and others reflect an earlier version — but the inconsistency is invisible to the audience",
"The PowerPoint file becomes disconnected from the network drive and cannot be saved",
"The presenter loses their internet connection during the client meeting",
"The Excel model and PowerPoint file are stored in different folders, making version control difficult"
],
correctOption: 0,
explanation: "Lesson 8 defines disconnection risk as the specific danger that arises when model data is manually copied into a presentation: if the model is updated after the copy, the presentation contains stale data that the audience cannot distinguish from current data. The risk is invisible — the numbers look authoritative but may be wrong. Option B, C, and D describe IT infrastructure issues, not the analytical consistency problem the chapter addresses.",
source: "Lesson 8: Cross-App Orchestration"
},
{
question: "An investment bank wants to use Cowork's cross-app orchestration capabilities. According to the chapter, what plan level is required and what is the current availability status?",
options: [
"Cowork Team or Enterprise plans, currently in research preview — meaning the feature is available but may evolve before general release",
"Any Cowork plan including the free tier, fully released and production-ready",
"Only Cowork Enterprise plans with a minimum seat count of 50 users",
"Cross-app orchestration is a future roadmap feature not yet available on any plan"
],
correctOption: 0,
explanation: "Lesson 8 states that cross-app orchestration is available on Cowork Team and Enterprise plans and is currently in research preview. This means the feature works but may change before general availability. Option B incorrectly claims free-tier availability and full release. Option C invents a minimum seat requirement. Option D incorrectly states the feature is not yet available.",
source: "Lesson 8: Cross-App Orchestration"
},
{
question: "A consulting firm wants to apply the Knowledge Extraction Method (KEM) to their finance practice. Lesson 9 adapts the Five Questions from Chapter 16 to a finance context. What is the first question, and why is it adapted differently for finance?",
options: [
"'Walk me through your most recent monthly close from start to finish' — it is adapted to finance because monthly close is the recurring, high-stakes workflow that surfaces the most tacit knowledge about an institution's specific accounting practices",
"'What financial software do you use?' — technology inventory comes first because the SKILL.md needs to reference specific tools",
"'What are the biggest risks in your portfolio?' — risk identification is the primary concern in finance",
"'How many people are on your finance team?' — headcount determines the scope of the extraction"
],
correctOption: 0,
explanation: "Lesson 9 adapts Question 1 to 'Walk me through your most recent monthly close' because the monthly close is the most recurring, comprehensive financial workflow. It touches every aspect of the accounting process and surfaces tacit knowledge about how the institution handles its specific complexities. Option B focuses on tools rather than knowledge. Option C jumps to risk without establishing the workflow context. Option D is an operational question irrelevant to knowledge extraction.",
source: "Lesson 9: Extracting Finance Domain Knowledge"
},
{
question: "During a KEM interview with a CFO, the interviewer asks about variance analysis. The CFO explains that a 3% variance on a $500,000 line item is immaterial but a 3% variance on a $50 million line item triggers investigation. What type of knowledge does this illustrate?",
options: [
"Firm-specific knowledge — the materiality thresholds, escalation rules, and contextual judgements that distinguish this institution's practices from generic accounting principles and cannot be obtained from textbooks or general training",
"Generic accounting knowledge that any qualified accountant would know",
"Regulatory requirements imposed by external auditors that apply to all companies",
"Statistical knowledge about variance analysis that could be found in any finance textbook"
],
correctOption: 0,
explanation: "Lesson 9 uses variance analysis as the primary example of firm-specific versus generic knowledge. Generic knowledge says 'investigate material variances.' Firm-specific knowledge says 'a 3% variance on this line item is immaterial but the same percentage on that line item requires CFO review.' These thresholds and escalation rules are institutional knowledge that the KEM extracts. Option B misidentifies firm-specific thresholds as generic. Option C attributes institutional practice to regulation. Option D confuses applied judgement with textbook theory.",
source: "Lesson 9: Extracting Finance Domain Knowledge"
},
{
question: "The KEM interview produces a draft SKILL.md for a finance domain agent. The chapter shows the structure of this draft. What are the three main sections of the SKILL.md that the extraction produces?",
options: [
"Persona (who the agent is and its expertise boundaries), Questions (what it asks and what is out of scope), and Principles (the specific rules encoding the expert's tacit knowledge)",
"Introduction, Body, and Conclusion — following standard document structure",
"Data Sources, Calculations, and Outputs — following the data processing pipeline",
"Setup, Execution, and Validation — following the software deployment lifecycle"
],
correctOption: 0,
explanation: "Lesson 9 shows that the KEM extraction produces a SKILL.md with three sections: Persona (defining the agent's identity and expertise boundaries), Questions (defining what the agent asks about and what falls outside its scope), and Principles (encoding the specific rules that capture the expert's tacit knowledge). Option B applies generic document structure. Option C describes a data pipeline. Option D describes software deployment.",
source: "Lesson 9: Extracting Finance Domain Knowledge"
},
{
question: "One of the Principles extracted during the KEM interview states: 'If a subsidiary closes its books more than two business days after the group deadline, escalate to the Group Controller before adjusting the consolidation.' What makes this a well-formed Principle?",
options: [
"It is testable — it specifies a concrete condition (two business days late), a specific action (escalate to Group Controller), and a sequence constraint (before adjusting) that an agent can evaluate against data without ambiguity",
"It is written in formal language appropriate for a legal document",
"It covers a common scenario that occurs in most organisations",
"It references a specific person by name rather than by role"
],
correctOption: 0,
explanation: "Lesson 9 emphasises that SKILL.md Principles must be testable. This Principle succeeds because it has a concrete trigger condition (subsidiary more than two business days late), a specific required action (escalate to Group Controller), and a sequence constraint (escalation before adjustment). An agent can evaluate each element against available data. Option B confuses quality with formality. Option C misidentifies firm-specificity as universality. Option D is incorrect — the Principle uses a role (Group Controller), which is appropriate.",
source: "Lesson 9: Extracting Finance Domain Knowledge"
},
{
question: "Enterprise extensions in the chapter follow a three-step pattern. A compliance officer wants to build a regulatory reporting extension. What are the three steps?",
options: [
"Identify the gap between generic plugin output and institutional requirements, write specific SKILL.md instructions that encode the institution's practices, and add governance gates that enforce compliance boundaries",
"Purchase the enterprise licence, install the compliance module, and configure the reporting templates",
"Interview the regulator, draft a compliance policy, and submit it for board approval",
"Build the data warehouse, train the machine learning model, and deploy to production"
],
correctOption: 0,
explanation: "Lessons 10 and 11 establish a three-step pattern for enterprise extensions: (1) identify the specific gap between generic plugin output and what the institution needs, (2) write SKILL.md instructions that encode the institution's specific practices and knowledge, and (3) add governance gates that enforce boundaries and escalation rules. Option B describes software procurement, not knowledge encoding. Option C describes regulatory engagement. Option D describes a data engineering pipeline.",
source: "Lesson 10: Enterprise Extensions — Risk and Compliance"
},
{
question: "The credit risk classification extension addresses a specific problem with generic credit risk plugins. What is that problem?",
options: [
"Generic plugins classify credits using standard external rating methodologies, but each institution has its own internal rating model with proprietary criteria, thresholds, and override rules — the extension encodes the institution's specific classification logic",
"Generic plugins cannot perform any credit risk analysis at all",
"Generic plugins are too slow to process large credit portfolios in real time",
"Generic plugins produce credit ratings that conflict with regulatory requirements"
],
correctOption: 0,
explanation: "Lesson 10 explains that generic credit risk plugins apply standard external rating methodologies, but institutions develop proprietary internal rating models with specific criteria, thresholds, and override rules. The enterprise extension encodes these institution-specific elements so the agent classifies credits the way the institution's credit committee does. Option B incorrectly claims generic plugins cannot do credit analysis. Option C focuses on performance. Option D conflates internal and regulatory rating systems.",
source: "Lesson 10: Enterprise Extensions — Risk and Compliance"
},
{
question: "The IPS compliance extension uses a specific verification sequence when checking whether a portfolio complies with an Investment Policy Statement. What is the correct order?",
options: [
"Hard caps first (absolute limits that cannot be exceeded), then concentration targets, then screening exclusions, then liquidity constraints — this sequence prevents the agent from optimising within a soft constraint while violating a hard one",
"Liquidity first, then screening exclusions, then concentration targets, then hard caps — checking the easiest constraints first saves time",
"All constraints are checked simultaneously using parallel processing for maximum efficiency",
"The order depends on the size of the portfolio — larger portfolios start with liquidity, smaller ones start with hard caps"
],
correctOption: 0,
explanation: "Lesson 10 specifies the IPS verification sequence: hard caps → concentration targets → screening exclusions → liquidity. The sequence matters because hard caps are absolute constraints — if a portfolio violates a hard cap, no amount of compliance on other dimensions makes it acceptable. Checking hard caps first prevents wasted effort and ensures the most critical constraints are satisfied before moving to softer ones. Option B inverts the priority. Option C loses the sequential logic. Option D invents a portfolio-size dependency.",
source: "Lesson 10: Enterprise Extensions — Risk and Compliance"
},
{
question: "The portfolio attribution extension uses the Brinson model. What are the three effects that the Brinson attribution decomposes performance into?",
options: [
"Allocation effect (being in the right sectors), selection effect (picking the right securities within sectors), and interaction effect (the combined impact of both decisions)",
"Alpha, beta, and gamma — the three components of risk-adjusted return",
"Revenue growth, margin expansion, and multiple expansion — the three drivers of equity returns",
"Market effect, currency effect, and timing effect — the three external factors affecting portfolio returns"
],
correctOption: 0,
explanation: "Lesson 10 explains the Brinson attribution model as decomposing portfolio performance into three effects: allocation (the impact of sector weight decisions), selection (the impact of security choices within sectors), and interaction (the combined effect that is not captured by either allocation or selection alone). Option B uses risk terminology, not attribution terminology. Option C describes equity return drivers. Option D lists external factors, not the Brinson decomposition.",
source: "Lesson 10: Enterprise Extensions — Risk and Compliance"
},
{
question: "The treasury management extension described in Lesson 11 addresses cash flow forecasting. What approach does the chapter identify as distinguishing firm-specific treasury management from generic cash management?",
options: [
"Encoding the institution's specific cash flow patterns, counterparty relationships, and liquidity buffer requirements — generic tools forecast based on historical averages, while the extension incorporates the treasurer's knowledge of seasonal patterns, covenant constraints, and counterparty risk thresholds",
"Using a more powerful AI model for treasury calculations",
"Connecting to more bank accounts through additional MCP connectors",
"Automating all treasury decisions without human oversight"
],
correctOption: 0,
explanation: "Lesson 11 explains that the treasury extension encodes institution-specific knowledge: the treasurer's understanding of seasonal cash flow patterns, covenant constraints, counterparty risk thresholds, and liquidity buffer requirements. Generic tools produce forecasts based on historical averages; the extension adds the contextual judgement that makes forecasts actionable for a specific institution. Option B conflates model capability with domain knowledge. Option C focuses on connectivity rather than knowledge. Option D removes the human oversight that the chapter emphasises.",
source: "Lesson 11: Enterprise Extensions — Operations and Strategy"
},
{
question: "The FP&A (Financial Planning and Analysis) extension uses a specific forecasting methodology that the chapter distinguishes from simple trend extrapolation. What is this methodology?",
options: [
"Driver-based forecasting — decomposing financial projections into volume, price, and mix components rather than extrapolating aggregate trends, because driver-based models allow the FP&A team to test specific operational assumptions",
"Monte Carlo simulation — running thousands of random scenarios to produce a probability distribution",
"Moving average forecasting — smoothing historical data to project future trends",
"Zero-based budgeting — rebuilding every budget from scratch each period"
],
correctOption: 0,
explanation: "Lesson 11 identifies driver-based forecasting (volume, price, mix decomposition) as the methodology that the FP&A extension uses. This approach decomposes projections into operational drivers rather than extrapolating aggregate trends, allowing the team to test specific assumptions about what is driving financial performance. Option B describes a statistical technique, not the chapter's methodology. Option C is the generic approach the chapter contrasts against. Option D is a budgeting methodology, not a forecasting one.",
source: "Lesson 11: Enterprise Extensions — Operations and Strategy"
},
{
question: "The M&A integration PMO extension addresses post-merger integration. What specific problem does this extension solve that generic project management tools cannot?",
options: [
"It encodes the institution's integration playbook — the specific sequencing of system migrations, organisational restructuring milestones, and synergy realisation targets that reflect lessons learned from prior acquisitions, not generic project management templates",
"It provides Gantt charts that are more visually appealing than standard project management tools",
"It automates all post-merger decisions to reduce the need for human project managers",
"It generates regulatory filings required for merger completion"
],
correctOption: 0,
explanation: "Lesson 11 explains that the M&A integration PMO extension encodes institutional knowledge from prior acquisitions: specific integration sequencing, system migration dependencies, and synergy realisation milestones that are learned through experience. Generic project management tools provide templates; the extension provides the institution's specific playbook. Option B focuses on aesthetics. Option C removes human oversight. Option D confuses post-merger integration with regulatory filing.",
source: "Lesson 11: Enterprise Extensions — Operations and Strategy"
},
{
question: "The ESG reporting extension must handle two specific regulatory frameworks mentioned in the chapter. What are they?",
options: [
"CSRD (Corporate Sustainability Reporting Directive) and ISSB (International Sustainability Standards Board) — the extension must map ESG data to each framework's specific disclosure requirements",
"GDPR and SOX — data privacy and internal controls frameworks",
"Basel III and Solvency II — banking and insurance capital requirements",
"IFRS and US GAAP — accounting standards for financial reporting"
],
correctOption: 0,
explanation: "Lesson 11 identifies CSRD and ISSB as the two ESG regulatory frameworks the extension must handle. Each framework has different disclosure requirements, and the extension must map the institution's ESG data to each framework's specific format. Option B lists unrelated regulatory frameworks. Option C lists capital adequacy frameworks. Option D lists accounting standards, not ESG frameworks.",
source: "Lesson 11: Enterprise Extensions — Operations and Strategy"
},
{
question: "The extension prioritisation framework in Lesson 12 uses four criteria to rank extension candidates. A team scores an extension as: Frequency: High, Pain: High, Data Availability: Low, Expertise Availability: High. Should this extension be prioritised for immediate implementation?",
options: [
"No — despite high frequency, pain, and expertise scores, the low data availability means the extension cannot function until the data prerequisite is resolved; data availability is a blocking constraint regardless of how appealing the other scores are",
"Yes — three out of four criteria are high, giving it a strong composite score",
"Yes — high pain level should always override other criteria because it represents the greatest immediate benefit",
"It depends on whether the extension has regulatory exposure, which overrides all other criteria"
],
correctOption: 0,
explanation: "Lesson 12 emphasises that data availability is a blocking constraint. An extension without accessible data sources cannot be built regardless of how high it scores on other criteria. The team should resolve the data prerequisite first, then sequence the extension based on its composite score. Option B ignores the blocking nature of data availability. Option C incorrectly prioritises pain alone. Option D, while partially correct about regulatory override, does not address the data availability blocker.",
source: "Lesson 12: Your Extension Roadmap and Chapter Summary"
},
{
question: "The prioritisation framework includes an override rule that supersedes the composite scoring. What is this rule?",
options: [
"Regulatory exposure takes precedence — an extension addressing compliance requirements moves to the front of the queue regardless of its composite score, because the cost of non-compliance is a risk cost, not merely a friction cost",
"The extension requested by the most senior executive always takes priority",
"The extension with the lowest implementation cost should be built first to demonstrate quick wins",
"Extensions that encode knowledge from retiring employees always take precedence"
],
correctOption: 0,
explanation: "Lesson 12 states that regulatory exposure overrides the arithmetic of the composite score. Extensions addressing compliance requirements (regulatory reporting, IPS compliance, credit risk classification) move to the front because non-compliance carries risk costs — potential fines, sanctions, or operational restrictions — that exceed the friction costs measured by the other criteria. Option B prioritises by authority rather than risk. Option C prioritises by cost rather than risk. Option D, while knowledge risk is important, is not identified as an override rule.",
source: "Lesson 12: Your Extension Roadmap and Chapter Summary"
},
{
question: "Lesson 12 recommends running three extensions in parallel during the first quarter rather than sequencing them one at a time. What is the rationale?",
options: [
"The three extensions target different concerns — highest-volume workflow, highest-risk compliance area, and most at-risk knowledge — so they do not compete for the same resources and running them in parallel produces institutional value faster than sequential execution",
"Three extensions is the maximum number the Cowork platform can support simultaneously",
"Running extensions in parallel is always faster than sequential execution regardless of resource constraints",
"The regulatory deadline requires all three to be completed within the same quarter"
],
correctOption: 0,
explanation: "Lesson 12 explains that the three recommended parallel extensions address different concerns (volume, compliance risk, knowledge risk) and therefore draw on different resources. Because they do not compete, parallel execution is feasible and produces value faster. Option B invents a platform limitation. Option C ignores the resource-dependency reasoning. Option D invents a regulatory deadline.",
source: "Lesson 12: Your Extension Roadmap and Chapter Summary"
},
{
question: "The chapter summary describes a 'unifying architecture' across the three parts of Chapter 17. A colleague says: 'Claude in Excel, Cowork, and enterprise extensions are three separate products.' How does the chapter correct this?",
options: [
"They are three layers of the same architecture sharing the same MCP connector ecosystem — Claude in Excel uses connectors at workbook scope, Cowork uses the same connectors at multi-application scope, and enterprise extensions add institutional knowledge on top of both layers through SKILL.md files",
"They are three separate products that happen to be made by the same company",
"They share the same user interface but have different backend architectures",
"They are three versions of the same product released in chronological order"
],
correctOption: 0,
explanation: "Lesson 12's chapter summary explicitly corrects the misconception that the three parts are separate systems. They are layers of the same architecture sharing the same MCP connector ecosystem. The difference is scope: Claude in Excel operates within one workbook, Cowork operates across applications, and enterprise extensions add organisational knowledge on top of both through SKILL.md files. Option B is the exact misconception being corrected. Option C invents a shared-UI claim. Option D incorrectly implies versioning.",
source: "Lesson 12: Your Extension Roadmap and Chapter Summary"
},
{
question: "The chapter's concluding architectural insight is captured in a three-part phrase. What is it?",
options: [
"'Same connectors. Different scope. Your knowledge on top.' — expressing that MCP connectors are shared across environments, scope differentiates Claude in Excel from Cowork, and enterprise extensions add institutional knowledge",
"'Build once. Deploy everywhere. Scale infinitely.' — expressing the platform's technical scalability",
"'Learn. Apply. Extend.' — expressing the chapter's pedagogical structure",
"'Data in. Analysis out. Decision made.' — expressing the workflow from input to output"
],
correctOption: 0,
explanation: "Lesson 12 concludes with the phrase 'Same connectors. Different scope. Your knowledge on top.' This captures the chapter's architectural insight: the MCP connector ecosystem is shared (same connectors), what changes is whether you operate within one workbook or across applications (different scope), and enterprise extensions add your organisation's specific knowledge (your knowledge on top). Option B, C, and D are invented phrases not from the chapter.",
source: "Lesson 12: Your Extension Roadmap and Chapter Summary"
},
{
question: "The chapter lists six pre-built Agent Skills for Claude in Excel. A new user asks which Agent Skills are available. Which list is correct?",
options: [
"Comparable Company Analysis, Discounted Cash Flow Model, Due Diligence Data Pack, Company Teaser, Earnings Analysis, and Initiating Coverage Report",
"Balance Sheet Analysis, Income Statement Review, Cash Flow Forecast, Ratio Calculator, Trend Analysis, and Benchmark Comparison",
"Credit Risk Assessment, Regulatory Compliance Check, Portfolio Optimisation, Risk Scoring, Stress Testing, and Capital Adequacy",
"Market Research, Competitive Analysis, Industry Overview, SWOT Analysis, Porter's Five Forces, and PESTEL Analysis"
],
correctOption: 0,
explanation: "Lesson 1 lists the six pre-built Agent Skills as Comparable Company Analysis, Discounted Cash Flow Model, Due Diligence Data Pack, Company Teaser, Earnings Analysis, and Initiating Coverage Report. These represent Layer 2 capabilities that connect to live market data through MCP connectors. Option B, C, and D list plausible but incorrect skill sets not described in the chapter.",
source: "Lesson 1: The Assistant and the Agent"
},
{
question: "WACC (Weighted Average Cost of Capital) is used as the discount rate in DCF analysis. The chapter explains that one component of WACC uses the CAPM (Capital Asset Pricing Model). What does CAPM calculate?",
options: [
"The cost of equity — the return that equity investors require, calculated as the risk-free rate plus a premium for the company's systematic risk (beta) relative to the market",
"The cost of debt — the interest rate the company pays on its borrowings",
"The optimal capital structure — the ideal ratio of debt to equity",
"The terminal value — the value of the company beyond the explicit forecast period"
],
correctOption: 0,
explanation: "Lesson 4 explains that CAPM calculates the cost of equity component of WACC. The formula adds a risk premium (beta times the market risk premium) to the risk-free rate, producing the return that equity investors require to compensate for the company's systematic risk. Option B describes a different WACC component. Option C describes capital structure optimisation. Option D describes a different DCF element.",
source: "Lesson 4: Agent Skills — Market Analysis"
},
{
question: "An analyst uses the Earnings Analysis Agent Skill to review a company's quarterly results. The skill compares reported earnings to consensus estimates. What does the chapter identify as the key analytical output beyond the simple beat/miss determination?",
options: [
"The pattern of beats and misses over multiple quarters — whether the company consistently beats by a small margin (suggesting conservative guidance), consistently misses (suggesting deteriorating fundamentals), or shows erratic variance (suggesting unpredictable business dynamics)",
"The exact dollar amount by which earnings exceeded or fell short of estimates",
"A recommendation to buy, sell, or hold the stock based on the earnings result",
"A comparison of the company's earnings to every competitor in its industry"
],
correctOption: 0,
explanation: "Lesson 5 explains that the Earnings Analysis skill goes beyond simple beat/miss to analyse the pattern over multiple quarters. Consistent small beats may indicate conservative guidance management; consistent misses may signal fundamental deterioration. The pattern provides more analytical value than any single quarter's result. Option B focuses on a single data point. Option C violates the chapter's boundary against investment advice. Option D overstates the comparative scope.",
source: "Lesson 5: Agent Skills — Deal and Research"
},
{
question: "A private equity firm is evaluating which add-on plugin to install for their Cowork deployment. They primarily build LBO models, conduct portfolio company monitoring, and prepare fund reports. Which add-on plugin is most relevant?",
options: [
"The private-equity add-on plugin — it provides commands and skills specifically designed for leveraged buyout analysis, portfolio company monitoring, and fund-level reporting that align with PE workflows",
"The investment-banking add-on plugin — because investment banks also do LBO models",
"The equity-research add-on plugin — because it covers all types of financial analysis",
"The wealth-management add-on plugin — because PE firms manage assets on behalf of limited partners"
],
correctOption: 0,
explanation: "Lesson 7 describes four add-on plugins, each targeting a specific segment: investment-banking, equity-research, private-equity, and wealth-management. The private-equity add-on is designed for the workflows described — LBO analysis, portfolio monitoring, and fund reporting. Option B is relevant for advisory work but not PE-specific workflows. Option C focuses on research coverage. Option D targets individual wealth management, not institutional PE.",
source: "Lesson 7: The Financial-Services Plugin Suite"
},
{
question: "During a KEM interview, the CFO describes how dormant accounts are handled: 'If an account shows no activity for 90 days, reclassify it as dormant and move the balance to a suspense ledger.' This is translated into a SKILL.md Principle. Why is the 90-day threshold important?",
options: [
"Because it is the institution's specific threshold — other institutions may use 60 days or 120 days, and encoding the exact number ensures the agent applies this institution's rule rather than a generic assumption",
"Because 90 days is the universally accepted accounting standard for dormancy",
"Because Claude cannot process transactions older than 90 days due to context window limitations",
"Because the CFO personally prefers 90 days and the number has no institutional significance"
],
correctOption: 0,
explanation: "Lesson 9 uses the dormant account example to illustrate firm-specific knowledge. The 90-day threshold is this institution's specific rule — not a universal standard. Other institutions may use different thresholds. Encoding the exact number in the SKILL.md ensures the agent applies the correct institutional rule rather than a generic assumption. Option B incorrectly claims universality. Option C invents a technical limitation. Option D dismisses institutional significance.",
source: "Lesson 9: Extracting Finance Domain Knowledge"
},
{
question: "Claude in Excel offers two model options: Sonnet 4.6 and Opus 4.6. The chapter provides guidance on when to use each. What is the recommended approach?",
options: [
"Start with Sonnet 4.6 for routine tasks like formula explanation and error identification; switch to Opus 4.6 for complex reasoning tasks like multi-step scenario analysis or model building where deeper analytical capability is required",
"Always use Opus 4.6 because it produces higher-quality financial analysis",
"Use Sonnet 4.6 for text and Opus 4.6 for numbers — each model specialises in different data types",
"The models are identical in capability; the choice is purely a cost consideration"
],
correctOption: 0,
explanation: "Lesson 1 recommends starting with Sonnet 4.6 for routine tasks and switching to Opus 4.6 when the task requires deeper reasoning. This is practical guidance — Sonnet handles straightforward tasks efficiently, while Opus provides stronger performance on complex analytical challenges. Option B ignores the efficiency trade-off. Option C invents a data-type specialisation that does not exist. Option D incorrectly claims the models are identical.",
source: "Lesson 1: The Assistant and the Agent"
},
{
question: "The tax provision extension described in Lesson 11 must handle a specific accounting standard. Which standard governs tax provision accounting in the chapter's discussion?",
options: [
"ASC 740 — the US accounting standard for income taxes that governs how companies calculate, recognise, and disclose tax provisions in their financial statements",
"IFRS 16 — the international standard for lease accounting",
"ASC 606 — the revenue recognition standard",
"SOX Section 404 — the internal controls over financial reporting requirement"
],
correctOption: 0,
explanation: "Lesson 11 identifies ASC 740 as the accounting standard governing tax provision calculations. The tax provision extension must encode institution-specific application of ASC 740, including how the company calculates deferred tax assets and liabilities, applies valuation allowances, and handles uncertain tax positions. Option B governs leases. Option C governs revenue recognition. Option D governs internal controls, not tax accounting.",
source: "Lesson 11: Enterprise Extensions — Operations and Strategy"
},
{
question: "The fund administration extension mentioned in Lesson 11 centres on a specific calculation. What is this calculation, and why does it require firm-specific knowledge?",
options: [
"NAV (Net Asset Value) calculation — each fund has specific rules for valuing illiquid positions, allocating expenses, and handling side pockets that generic tools cannot apply without institutional knowledge",
"IRR (Internal Rate of Return) calculation — a standard formula that any financial calculator can perform",
"P&L (Profit and Loss) calculation — a basic accounting function that does not require specialisation",
"AUM (Assets Under Management) calculation — a simple aggregation of portfolio values"
],
correctOption: 0,
explanation: "Lesson 11 describes NAV calculation as the core of the fund administration extension. NAV requires firm-specific knowledge because each fund has specific rules for valuing illiquid positions, allocating expenses across share classes, and handling side pockets or special situations. Generic tools apply standard valuation methods; the extension encodes the fund's specific NAV policies. Option B is a standard calculation. Option C and D do not require the same level of institutional specificity.",
source: "Lesson 11: Enterprise Extensions — Operations and Strategy"
},
{
question: "Lesson 11 introduces three prioritisation dimensions for selecting enterprise extensions before the formal four-criteria framework in Lesson 12. What are these three dimensions?",
options: [
"Operational pain (which workflows cause the most friction), knowledge risk (which expertise might leave the organisation), and regulatory exposure (which areas carry compliance consequences)",
"Cost (cheapest to build), speed (fastest to deploy), and visibility (most impressive to management)",
"Revenue impact, customer satisfaction, and employee retention",
"Technical complexity, data volume, and integration difficulty"
],
correctOption: 0,
explanation: "Lesson 11 introduces operational pain, knowledge risk, and regulatory exposure as the three dimensions for initial prioritisation before Lesson 12's full four-criteria framework. These dimensions reflect different types of institutional value: reducing friction, preserving expertise, and managing compliance risk. Option B prioritises by convenience rather than value. Option C and D use dimensions not identified in the chapter.",
source: "Lesson 11: Enterprise Extensions — Operations and Strategy"
},
{
question: "A credit analyst's SKILL.md Principle states: 'If the aging distribution shows more than 15% of receivables past 90 days, flag the credit for enhanced monitoring regardless of the overall DSO.' Why is this Principle valuable?",
options: [
"Because it encodes a specific threshold (15% past 90 days) and a specific action (enhanced monitoring) that reflect the institution's credit policy — a generic tool would look at overall DSO without examining the aging distribution, potentially missing concentrated risk in the tail",
"Because 15% is the universally accepted threshold for credit risk across all industries",
"Because the Principle prevents Claude from looking at any other credit metrics",
"Because aging distributions are only available in the institution's proprietary system"
],
correctOption: 0,
explanation: "Lesson 9 uses this type of Principle to illustrate how firm-specific knowledge creates value. The 15% threshold and the aging distribution focus are institutional decisions — other institutions may use different thresholds or different metrics. A generic tool would rely on overall DSO, potentially missing that a small number of large, old receivables create concentrated risk even when the average looks acceptable. Option B incorrectly claims universality. Option C misidentifies the Principle as exclusive. Option D confuses data availability with analytical specificity.",
source: "Lesson 9: Extracting Finance Domain Knowledge"
},
{
question: "The chapter describes the Knowledge Extraction Method as transferring directly to subsequent domain chapters. According to Lesson 12, what transfers and what changes?",
options: [
"The methodology transfers — the same five interview questions, document extraction framework, and validation loop apply in every domain — but the professional context changes, surfacing different tacit knowledge, different governance requirements, and different domain-specific judgements",
"Nothing transfers — each domain chapter introduces a completely new methodology",
"Only the SKILL.md format transfers — the interview questions must be redesigned for each domain",
"The methodology transfers but requires a different AI model for each domain"
],
correctOption: 0,
explanation: "Lesson 12 explicitly states that the KEM methodology is domain-agnostic: the same five questions, the same document extraction, and the same validation loop transfer to every domain chapter. What changes is the professional knowledge the method surfaces — legal domain agents require different expertise than finance domain agents, but the extraction process is identical. Option B incorrectly claims no transfer. Option C partially transfers. Option D invents a model requirement.",
source: "Lesson 12: Your Extension Roadmap and Chapter Summary"
}
]}
/>

---

Return to [Chapter Overview](./README.md)
