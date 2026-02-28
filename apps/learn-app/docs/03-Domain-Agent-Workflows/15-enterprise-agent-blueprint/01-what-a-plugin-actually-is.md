---
sidebar_position: 1
title: "What a Plugin Actually Is"
description: "Understand the three layers of a Cowork plugin — the generic format, knowledge-work specialisation, and enterprise readiness evaluation — plus the transparency property that makes domain agents deployable in regulated industries"
keywords:
  [
    "Cowork plugin",
    "plugin architecture",
    "SKILL.md",
    "plugin.json",
    ".mcp.json",
    "MCP connectors",
    "transparency",
    "domain agent",
    "enterprise AI",
    "plugin components",
    "inspectable AI",
    "agentskills.io",
    "enterprise readiness",
  ]
chapter: 15
lesson: 1
duration_minutes: 20

# HIDDEN SKILLS METADATA
skills:
  - name: "Define a Cowork Plugin"
    proficiency_level: "A1"
    category: "Conceptual"
    bloom_level: "Remember"
    digcomp_area: "Information Literacy"
    measurable_at_this_level: "Student can distinguish the three layers (generic plugin format, knowledge-work specialisation, enterprise readiness evaluation) and describe the six plugin package components from memory"

  - name: "Identify the Plugin Package Structure"
    proficiency_level: "A2"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Information Literacy"
    measurable_at_this_level: "Student can name the plugin package components (skills, connectors, commands, agents, hooks, manifest), describe what each does at a conceptual level, and explain why the plugin structure separates concerns across different roles"

  - name: "Recognise Transparency as an Architectural Property"
    proficiency_level: "A2"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Safety"
    measurable_at_this_level: "Student can explain why inspectability is not incidental to plugin design but structural, and articulate what this means for deployment in regulated industries"

learning_objectives:
  - objective: "Distinguish the three layers of a Cowork plugin (format, knowledge-work specialisation, enterprise readiness) and describe the plugin package components"
    proficiency_level: "A1"
    bloom_level: "Remember"
    assessment_method: "Student can name the three layers and the six plugin package components from memory without reference to the lesson"

  - objective: "Explain the purpose of the key plugin components and identify which role owns each one"
    proficiency_level: "A2"
    bloom_level: "Understand"
    assessment_method: "Given the name of a component (skills, connectors, commands, agents, hooks, manifest), student can describe its function and name the role responsible for it (knowledge worker, plugin developer/IT)"

  - objective: "Explain why transparency is an architectural property of Cowork plugins and what it enables in regulated environments"
    proficiency_level: "A2"
    bloom_level: "Understand"
    assessment_method: "Student can articulate the difference between incidental transparency and structural transparency, and give an example of what inspectability enables for a compliance or audit function"

cognitive_load:
  new_concepts: 3
  concepts_list:
    - "Three-layer model (generic format → knowledge-work specialisation → enterprise readiness evaluation)"
    - "Plugin package structure (skills, connectors, commands, agents, hooks, manifest)"
    - "Transparency as an architectural property (not incidental)"
  assessment: "3 concepts at A1-A2 level — well within the 5-7 cognitive limit for this tier. Students already know SKILL.md and MCP connectors at surface level from Chapter 14 Lesson 4; this lesson deepens the conceptual model by distinguishing Anthropic's plugin format from knowledge-work specialisation and Panaversity's enterprise readiness evaluation framework."

differentiation:
  extension_for_advanced: "Identify a domain agent you have seen described in industry press or your own organisation. Using the enterprise readiness framework from this lesson, assess how many of the five properties are visible to you. Which properties are opaque? What would need to change for the plugin to be fully inspectable? Document your analysis in a short note."
  remedial_for_struggling: "Focus on the plugin package structure and the ownership question. For each key component (skills/SKILL.md, connectors/.mcp.json, commands, agents, hooks), write one sentence: who creates it and what it contains. If those sentences are accurate, the foundational model is understood."

teaching_guide:
  lesson_type: "core"
  session_group: 1
  session_title: "Defining the Unit of Work"
  key_points:
    - "A Cowork plugin has three layers students must keep distinct: the generic format (a directory of components), the knowledge-work specialisation (domain expertise + enterprise connectors), and enterprise readiness evaluation (Panaversity's five-property framework). Conflating these layers leads to misattribution."
    - "The plugin package structure maps cleanly to two primary roles: knowledge worker (skills) and plugin developer/IT (connectors, commands, agents, hooks, manifest). This ownership clarity is a feature, not an incidental detail."
    - "Transparency is architectural, not incidental. Every plugin property is inspectable by design. This is what makes plugins deployable in regulated industries — not trust, but verifiability."
    - "Students have already encountered SKILL.md and connectors in Chapter 14 Lesson 4 (which introduced the full plugin package). This lesson moves from surface recognition to conceptual understanding of what each component actually does."
  misconceptions:
    - "Students may think a 'plugin' is just a chatbot add-on. Correct this early: the plugin format is a general-purpose extension system, but knowledge-work plugins use it to create domain-specialist agents with real enterprise connections — not UI widgets."
    - "Students may assume transparency means 'visible to everyone'. Clarify: transparency means every property is inspectable by the right role (knowledge worker reads SKILL.md, IT reads .mcp.json and plugin.json, admin sees audit logs). The point is that no property is a black box."
    - "Students may treat the plugin components as interchangeable. The division of ownership is the key insight — each component (skills, connectors, commands, agents, hooks, manifest) has a defined owner and a defined scope. Mixing them creates governance problems."
  discussion_prompts:
    - "Think of a workflow in your organisation that is currently done by a person. Which of the five plugin properties (identity, instructions, connections, governance, performance record) does that person's role already have, informally? Which are missing?"
    - "If your organisation audited an AI agent tomorrow, which plugin properties would they need to inspect? Could they inspect them in an agent your organisation has already deployed?"
  teaching_tips:
    - "Open with the three-layer distinction. Students who understand that the format is generic, the knowledge-work specialisation is Anthropic's use of it, and the enterprise readiness model is Panaversity's evaluation lens will avoid conflating them throughout the chapter."
    - "When introducing the plugin package, use the ownership framing immediately: SKILL.md belongs to the knowledge worker, everything else (connectors, commands, agents, hooks, manifest) belongs to the developer or IT. This prevents the components from feeling like arbitrary technical divisions."
    - "On transparency: use the analogy of a licensed professional. A doctor's practice is inspectable (credentials, records, outcomes) not because someone added a transparency feature, but because the framework of the profession requires it. A Cowork plugin is designed the same way."
  assessment_checks:
    - question: "What is a Cowork plugin?"
      expected_response: "At its base, a self-contained directory of components that extends Claude Code. Knowledge-work plugins use this format to turn a general-purpose agent into a domain specialist. Panaversity's enterprise readiness model then evaluates whether the result is production-ready via five properties: identity, instructions, connections, governance, and performance record."
    - question: "Name the key components of a Cowork plugin package."
      expected_response: "Skills (SKILL.md files — the intelligence layer, owned by the knowledge worker), connectors (.mcp.json — MCP server declarations for enterprise system integration), commands (slash commands for explicit invocation), agents (specialised assistants for complex workflows), hooks (event handlers for lifecycle automation), and a manifest (plugin.json declaring name, version, and author)"
    - question: "Why does transparency matter as an architectural property?"
      expected_response: "Because every aspect of a plugin is inspectable, modifiable, and testable by the right role. In regulated industries, this verifiability replaces trust as the basis for deployment — you do not have to trust the agent, you can inspect it."
---

# What a Plugin Actually Is

> _"The black box is not a technical problem — it is a governance problem. Once you can inspect everything the agent does, you can deploy it anywhere an auditor can follow."_

In Chapter 14, you established that the knowledge worker, not the developer, is the central figure in enterprise AI deployment. You identified the knowledge transfer gap — the structural barrier between domain expertise and deployed agents — and recognised the platform that closes it. Now the question becomes concrete: what, precisely, is the thing you are going to build?

The word "plugin" carries baggage from its previous life in software. Browser plugins, email plugins, productivity suite plugins — add-ons that bolt a feature onto a product someone else built. A Cowork plugin is something more capable than that, but to understand what it actually is, you need to separate three things that are easy to conflate: the plugin format itself, what knowledge-work plugins do with it, and how enterprises evaluate whether the result is production-ready.

This lesson gives you all three layers, plus the architectural property that makes the whole thing deployable in environments that do not tolerate black boxes.

## Layer 1: What a Plugin Is

Anthropic's [plugin reference](https://code.claude.com/docs/en/plugins-reference) defines a plugin precisely: **a self-contained directory of components that extends Claude Code with custom functionality.** A plugin is a packaging format. It bundles skills, agents, hooks, MCP server declarations, and a manifest into a directory that Claude Code can discover, load, and use. That is all the format requires. It does not prescribe what the plugin is _about_, any more than a ZIP file prescribes its contents.

## Layer 2: What Knowledge-Work Plugins Do With It

Anthropic's [knowledge-work plugins](https://github.com/anthropics/knowledge-work-plugins) use this generic format for a specific purpose: turning a general-purpose coding agent into a domain specialist. A general-purpose agent knows how to reason, write, and use tools. A knowledge-work plugin gives it specific knowledge — what your organisation's contracts look like, how your compliance reviews work, what your financial analysis conventions require. The SKILL.md files encode that domain expertise. The MCP connectors wire it to the systems where the work actually lives. The result is an agent that operates within a defined professional field — compliance review, financial analysis, contract triage — rather than as a generalist.

This is the kind of plugin this chapter teaches you to build. When the rest of this chapter says "plugin," it means a knowledge-work plugin: one that encodes domain expertise and connects to enterprise systems. But it is worth remembering that the underlying format is general-purpose, and Anthropic designed it that way deliberately.

## The Plugin Package

The two layers above tell you what a plugin _is_ and what knowledge-work plugins _do_. The plugin package tells you what one _contains_. The official structure, as documented at [code.claude.com](https://code.claude.com/docs/en/plugins-reference), includes:

| Component                   | What It Contains                                                                                                               | Who Owns It            |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------- |
| **Skills** (SKILL.md files) | The agent's domain knowledge — structured Markdown with YAML frontmatter, following the Agent Skills standard (agentskills.io) | Knowledge worker (you) |
| **Connectors** (.mcp.json)  | MCP server declarations that wire the agent to enterprise systems (CRM, email, project tools)                                  | Plugin developer or IT |
| **Commands**                | Slash commands you invoke explicitly (e.g., `/sales:call-prep`)                                                                | Plugin developer       |
| **Agents**                  | Specialised assistants for complex multi-step workflows (in the `agents/` directory)                                           | Plugin developer       |
| **Hooks**                   | Event handlers that automate lifecycle actions — triggered on events like tool calls or notifications                          | Plugin developer       |
| **Manifest** (plugin.json)  | Plugin identity: name, version, and author, inside `.claude-plugin/`                                                           | Plugin developer       |

Additional optional components include `settings.json` for default configuration and `.lsp.json` for language server integration. Anthropic designed these as plain Markdown and JSON files so that anyone can contribute — but in enterprise environments, clear ownership of each component prevents governance gaps.

The division of labour here is intentional and significant. The knowledge worker writes the intelligence — the SKILL.md files that encode domain expertise — but does not build the integration infrastructure. The plugin developer or IT builds and maintains the connectors, commands, agents, hooks, and manifest. Plugins arrive from the marketplace as ready-made packages. Your contribution is the part no one else can write: the SKILL.md that encodes how _your_ organisation actually works.

This separation is not bureaucratic overhead. It is what makes a plugin governable. When something goes wrong — and in production, something eventually goes wrong — the ownership model tells you immediately which layer is responsible and who can fix it. This chapter and Chapter 16 will go deep on each component in turn. What matters here is the model: the knowledge worker owns the intelligence layer, everyone else owns the infrastructure.

## Layer 3: Evaluating Enterprise Readiness

The plugin format gives you a packaging standard. Knowledge-work plugins give you domain specialisation. But neither tells you whether the result is ready for production in an enterprise that answers to regulators, auditors, and compliance officers. That requires a different lens. At Panaversity, we use five properties as an enterprise readiness evaluation model:

| Property               | What It Evaluates                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------------- |
| **Identity**           | Does the agent have a defined name, persona, and set of declared capabilities?            |
| **Instructions**       | Are there explicit instructions governing the agent's behaviour?                          |
| **Connections**        | Are its data sources and system integrations declared and scoped via MCP?                 |
| **Governance**         | Are there rules defining who can use it, what it can do, and what happens to its outputs? |
| **Performance record** | Is there a log of interactions, outputs, and escalations?                                 |

This is our analytical framework for assessing whether a plugin deployment meets enterprise standards. A Cowork plugin's architecture naturally supports all five — skills encode instructions, .mcp.json declares connections, Anthropic's enterprise admin controls handle governance, and the platform maintains interaction logs. But the framework itself is a lens we apply to evaluate readiness, not a feature list from the platform documentation.

An agent that lacks clear governance is not ready for production. An agent without a performance record is not deployable in an audited environment. These are enterprise deployment standards, and the five-property framework gives you a structured way to assess them.

## Transparency as an Architectural Property

There is a phrase that appears consistently in conversations about enterprise AI adoption: "the black box problem." The concern is legitimate. If an agent makes a decision — approves a contract clause, flags a transaction as suspicious, recommends a clinical protocol — but no one can explain why, the decision cannot be audited, challenged, or trusted by the people who are accountable for it.

A Cowork plugin is designed to be inspectable. Every aspect of its architecture is readable, modifiable, and testable by the appropriate role:

| What Is Inspectable     | How                                                                                                |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| **Agent identity**      | plugin.json declares what the agent is and what it claims to be capable of                         |
| **Domain instructions** | SKILL.md files contain the exact text that governs behaviour — every word of it                    |
| **System connections**  | .mcp.json declares which systems the agent can access, with what scope                             |
| **Governance controls** | Anthropic's enterprise admin controls manage authorisation, constraints, and escalation thresholds |
| **Interaction history** | Platform logs capture queries, outputs, and escalations                                            |

This is not transparency in the sense of "we could probably find this out if we looked hard enough." It is transparency as a structural property of the design. The SKILL.md file is readable by the knowledge worker who authored it. The plugin.json manifest and .mcp.json connector declarations are readable by IT. The audit log is accessible to compliance and governance functions. The connector permissions are documented in the deployment record. There is no property of a Cowork plugin that is inaccessible to the right role.

This property is what makes plugins deployable in regulated industries. Financial services firms, healthcare organisations, legal practices — these environments do not deploy systems they cannot audit. The historic barrier to enterprise AI was not model capability — by mid-2024, the models were capable enough. The barrier was the governance gap: organisations could not inspect, verify, or audit what their AI systems were actually doing. A Cowork plugin's architecture — plain-text skills, declared connections, platform-managed logs — provides the structural affordance that makes this kind of inspection possible.

Consider the practical implication. A compliance officer reviewing a contract analysis agent does not have to trust that the agent applies the firm's standards correctly. She can read the SKILL.md, which specifies the agent's operating principles for high-risk language. She can check the .mcp.json to verify which document repositories the agent can access. She can review the audit log to confirm that every flagged clause was reviewed by a qualified lawyer before the contract was executed. The agent becomes evaluable in the same way that a licensed professional's practice is evaluable — not because someone added a transparency feature, but because the architecture provides the affordance for inspection.

This is the architectural property that everything in the rest of this chapter rests on. The plugin package structure, the context hierarchy, the governance mechanisms — all of them derive their enterprise deployability from the same foundational fact: there is nothing in a Cowork plugin that cannot be inspected.

## What Comes Next

This lesson has established the definition and the foundational model. The lessons that follow build the architecture from the inside out. Lesson 2 goes deep on the SKILL.md — the intelligence layer you, as a knowledge worker, will author. Lesson 3 covers the configuration and integration layers. Lessons 4 and 5 introduce the context hierarchy and show a complete, annotated plugin example. Lessons 6 and 7 cover the connector ecosystem and the governance layer in detail.

By the end of this chapter, you will be able to define, understand, and describe every layer of the architecture. Chapter 16 will then teach you how to extract and encode your domain expertise into the first layer — the one that is yours to write.

## Try With AI

Use these prompts in Anthropic Cowork or your preferred AI assistant to deepen your understanding of this lesson's concepts.

### Prompt 1: Personal Application

```
I work as [YOUR ROLE] in [YOUR INDUSTRY]. I want to understand whether my
current AI tools qualify as Cowork plugins or not. Help me assess them against
these five enterprise readiness properties: defined identity, explicit instructions, connections to
enterprise systems via MCP, a governance framework, and a performance record.

For each property, ask me one diagnostic question, then assess whether the tool
I describe meets the standard or falls short.
```

**What you're learning:** The enterprise readiness framework is analytical, not just descriptive. By applying it to tools you already use, you are practising the diagnostic skill that Chapter 15 is building toward — the ability to assess whether an agent deployment is a genuine plugin or a prototype dressed as one.

### Prompt 2: Framework Analysis

```
The lesson describes transparency as an "architectural property" rather than an
"incidental feature." Analyse the difference between these two framings for three
specific regulated industries: financial services, healthcare, and legal.

For each industry:
1. What would an auditor need to inspect in an AI agent deployment?
2. Which of the five enterprise readiness properties would they examine?
3. What happens operationally when a property is opaque rather than inspectable?

Present your analysis as a comparison table.
```

**What you're learning:** Transparency as an architectural property has concrete operational consequences that vary by industry. This exercise trains you to see the governance implications of plugin design choices — the same perspective you will need when configuring your own plugin's governance layer in Lesson 7.

### Prompt 3: Domain Research

```
Research one high-profile case in [YOUR INDUSTRY] where an AI system was deployed
but later faced regulatory scrutiny, public challenge, or internal audit failure.

Assess that case against the five enterprise readiness properties. Which properties were
present in the deployed system? Which were absent or opaque? Based on this analysis,
would the system have passed inspection under a Cowork-style governance framework?
What would have needed to be different?
```

**What you're learning:** Historical cases of AI governance failures are the clearest evidence for why transparency is an architectural requirement rather than a nice-to-have. Applying the enterprise readiness framework to a real case builds the analytical vocabulary you will use to justify governance design decisions to colleagues and senior stakeholders.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 2: The Intelligence Layer — SKILL.md →](./02-the-intelligence-layer-skill-md.md)
