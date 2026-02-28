---
sidebar_position: 1
title: "What a Plugin Actually Is"
description: "Define a Cowork plugin precisely, understand its plugin package structure, and understand why transparency is the architectural property that makes domain agents deployable in regulated industries"
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
    measurable_at_this_level: "Student can state the definition of a Cowork plugin and list its five structural properties (identity, instructions, connections, governance, performance record) from memory"

  - name: "Identify the Plugin Package Structure"
    proficiency_level: "A2"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Information Literacy"
    measurable_at_this_level: "Student can name the key components of a plugin package (skills, connectors, commands, sub-agents, manifest), describe what each does at a conceptual level, and explain why the plugin structure separates concerns across different roles"

  - name: "Recognise Transparency as an Architectural Property"
    proficiency_level: "A2"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Safety"
    measurable_at_this_level: "Student can explain why inspectability is not incidental to plugin design but structural, and articulate what this means for deployment in regulated industries"

learning_objectives:
  - objective: "State the definition of a Cowork plugin and list its five structural properties"
    proficiency_level: "A1"
    bloom_level: "Remember"
    assessment_method: "Student can reproduce the plugin definition and the five properties from memory without reference to the lesson"

  - objective: "Explain the purpose of the key plugin components and identify which role owns each one"
    proficiency_level: "A2"
    bloom_level: "Understand"
    assessment_method: "Given the name of a component (skills, connectors, commands, sub-agents, manifest), student can describe its function and name the role responsible for it (knowledge worker, plugin developer/IT)"

  - objective: "Explain why transparency is an architectural property of Cowork plugins and what it enables in regulated environments"
    proficiency_level: "A2"
    bloom_level: "Understand"
    assessment_method: "Student can articulate the difference between incidental transparency and structural transparency, and give an example of what inspectability enables for a compliance or audit function"

cognitive_load:
  new_concepts: 3
  concepts_list:
    - "Cowork plugin as a defined entity (five structural properties)"
    - "Plugin package structure (skills, connectors, commands, sub-agents, manifest)"
    - "Transparency as an architectural property (not incidental)"
  assessment: "3 concepts at A1-A2 level — well within the 5-7 cognitive limit for this tier. Students already know SKILL.md and MCP connectors at surface level from Chapter 14 Lesson 4; this lesson deepens the conceptual model by introducing the full plugin package structure."

differentiation:
  extension_for_advanced: "Identify a domain agent you have seen described in industry press or your own organisation. Using the five-property framework from this lesson, assess how many of the five properties are visible to you. Which properties are opaque? What would need to change for the plugin to be fully inspectable? Document your analysis in a short note."
  remedial_for_struggling: "Focus on the plugin package structure and the ownership question. For each key component (skills/SKILL.md, connectors/.mcp.json, commands, sub-agents), write one sentence: who creates it and what it contains. If those sentences are accurate, the foundational model is understood."

teaching_guide:
  lesson_type: "core"
  session_group: 1
  session_title: "Defining the Unit of Work"
  key_points:
    - "A Cowork plugin is not a vague concept — it has a precise definition with five structural properties. Students should be able to reproduce the definition, not just paraphrase it."
    - "The plugin package structure maps cleanly to two primary roles: knowledge worker (skills) and plugin developer/IT (connectors, commands, sub-agents, manifest). This ownership clarity is a feature, not an incidental detail."
    - "Transparency is architectural, not incidental. Every plugin property is inspectable by design. This is what makes plugins deployable in regulated industries — not trust, but verifiability."
    - "Students have already encountered SKILL.md and connectors in Chapter 14 Lesson 4 (which introduced the full plugin package). This lesson moves from surface recognition to conceptual understanding of what each component actually does."
  misconceptions:
    - "Students may think a 'plugin' is just a chatbot add-on. Correct this early: a Cowork plugin is a domain-specific agent with a complete governance and performance infrastructure, not a UI widget."
    - "Students may assume transparency means 'visible to everyone'. Clarify: transparency means every property is inspectable by the right role (knowledge worker reads SKILL.md, IT reads .mcp.json and plugin.json, admin sees audit logs). The point is that no property is a black box."
    - "Students may treat the plugin components as interchangeable. The division of ownership is the key insight — each component has a defined owner and a defined scope. Mixing them creates governance problems."
  discussion_prompts:
    - "Think of a workflow in your organisation that is currently done by a person. Which of the five plugin properties (identity, instructions, connections, governance, performance record) does that person's role already have, informally? Which are missing?"
    - "If your organisation audited an AI agent tomorrow, which plugin properties would they need to inspect? Could they inspect them in an agent your organisation has already deployed?"
  teaching_tips:
    - "Open with the five-property definition before introducing the components. Students who can articulate the five properties have a conceptual hook for everything in the chapter."
    - "When introducing the plugin package, use the ownership framing immediately: SKILL.md belongs to the knowledge worker, everything else (connectors, commands, sub-agents, manifest) belongs to the developer or IT. This prevents the components from feeling like arbitrary technical divisions."
    - "On transparency: use the analogy of a licensed professional. A doctor's practice is inspectable (credentials, records, outcomes) not because someone added a transparency feature, but because the framework of the profession requires it. A Cowork plugin is designed the same way."
  assessment_checks:
    - question: "What is a Cowork plugin?"
      expected_response: "A domain-specific agent deployed inside the Cowork environment with a defined identity, explicit instructions, connections to external systems via MCP, a governance framework, and a performance record"
    - question: "Name the key components of a Cowork plugin package."
      expected_response: "Skills (SKILL.md files — the intelligence layer, owned by the knowledge worker), connectors (.mcp.json — MCP server declarations for enterprise system integration), commands (slash commands for explicit invocation), sub-agents (specialised assistants for complex workflows), and a manifest (plugin.json declaring name, version, and author)"
    - question: "Why does transparency matter as an architectural property?"
      expected_response: "Because every aspect of a plugin is inspectable, modifiable, and testable by the right role. In regulated industries, this verifiability replaces trust as the basis for deployment — you do not have to trust the agent, you can inspect it."
---

# What a Plugin Actually Is

> _"The black box is not a technical problem — it is a governance problem. Once you can inspect everything the agent does, you can deploy it anywhere an auditor can follow."_

In Chapter 14, you established that the knowledge worker, not the developer, is the central figure in enterprise AI deployment. You identified the knowledge transfer gap — the structural barrier between domain expertise and deployed agents — and recognised the platform that closes it. Now the question becomes concrete: what, precisely, is the thing you are going to build?

The word "plugin" carries baggage from its previous life in software. Browser plugins, email plugins, productivity suite plugins — add-ons that bolt a feature onto a product someone else built. A Cowork plugin is something architecturally different. Before the chapter goes any further, it is worth spending the time to define it precisely, because the definition will do a great deal of work in everything that follows.

This lesson gives you the definition, the plugin package structure, and the architectural property that makes the whole thing deployable in environments that do not tolerate black boxes.

## The Definition

A Cowork plugin is a **domain-specific agent deployed inside the Cowork environment**. That sentence contains six words that each carry weight.

_Domain-specific_ means the agent knows something particular. Not general knowledge from a large language model, but the specific conventions, standards, thresholds, and edge cases of a defined professional field — compliance review in a particular jurisdiction, financial analysis within a specific investment mandate, contract triage against a firm's established risk criteria.

_Agent_ means the system acts, not just responds. It monitors, analyses, sequences multi-step workflows, and produces outputs. It does not wait to be asked the same question twice.

_Deployed_ means it is running in production, not in a demonstration. It is connected to real systems, operating against real data, with real outputs being used by real people.

_Inside the Cowork environment_ means it operates within an infrastructure that handles authentication, governance, audit, and platform-level constraints — not as a standalone script, but as a managed component of an enterprise platform.

Beyond this core definition, every Cowork plugin has five structural properties:

| Property               | What It Is                                                                     |
| ---------------------- | ------------------------------------------------------------------------------ |
| **Identity**           | A defined name, persona, and set of declared capabilities                      |
| **Instructions**       | Explicit guidance governing the agent's behaviour across all scenarios         |
| **Connections**        | Links to external data sources and enterprise systems via MCP                  |
| **Governance**         | Rules defining who can use it, what it can do, and what happens to its outputs |
| **Performance record** | A log of every interaction, output, and escalation, maintained automatically   |

These five properties are not optional features you configure later. They are the structural requirements for anything that qualifies as a plugin. An agent without a governance framework is not a plugin — it is a prototype. An agent without a performance record is not deployable in an audited environment — it is a risk.

## The Plugin Package

The five structural properties are delivered through a **plugin package** — a bundled directory that contains everything a domain agent needs to operate. You have encountered this structure before — Chapter 14 Lesson 4 introduced the components at the level of the architecture. This chapter goes deeper, but first you need the structural model clearly in mind.

| Component                   | What It Contains                                                                                                                   | Who Owns It            |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **Skills** (SKILL.md files) | The agent's persona, operating principles, domain constraints, and response behaviours — structured Markdown with YAML frontmatter | Knowledge worker (you) |
| **Connectors** (.mcp.json)  | MCP server declarations that wire the agent to enterprise systems (CRM, email, project tools)                                      | Plugin developer or IT |
| **Commands**                | Slash commands you invoke explicitly (e.g., `/sales:call-prep`)                                                                    | Plugin developer       |
| **Sub-agents**              | Specialised assistants for complex multi-step workflows                                                                            | Plugin developer       |
| **Manifest** (plugin.json)  | Plugin identity: name, version, and author, inside `.claude-plugin/`                                                               | Plugin developer       |

A plugin also carries optional components: `hooks/` for event handlers, `settings.json` for default settings, and `.lsp.json` for language server configurations. But the five components above are the ones that matter for understanding how a plugin works.

The division of labour here is intentional and significant. The knowledge worker writes the intelligence — the SKILL.md files that encode domain expertise — but does not build the integration infrastructure. The plugin developer or IT builds and maintains the connectors, commands, sub-agents, and manifest. Plugins arrive from the marketplace as ready-made packages. Your contribution is the part no one else can write: the SKILL.md that encodes how _your_ organisation actually works.

This separation is not bureaucratic overhead. It is what makes a plugin governable. When something goes wrong — and in production, something eventually goes wrong — the ownership model tells you immediately which layer is responsible and who can fix it. This chapter and Chapter 16 will go deep on each component in turn. What matters here is the model: the knowledge worker owns the intelligence layer, everyone else owns the infrastructure.

## Transparency as an Architectural Property

There is a phrase that appears consistently in conversations about enterprise AI adoption: "the black box problem." The concern is legitimate. If an agent makes a decision — approves a contract clause, flags a transaction as suspicious, recommends a clinical protocol — but no one can explain why, the decision cannot be audited, challenged, or trusted by the people who are accountable for it.

A Cowork plugin is not a black box. Every aspect of its design is inspectable, modifiable, and testable:

| Property               | What Is Inspectable                                                              |
| ---------------------- | -------------------------------------------------------------------------------- |
| **Identity**           | What the agent claims to be and what it claims to be capable of                  |
| **Instructions**       | The exact text that governs its behaviour — every word of it                     |
| **Connections**        | Which systems it can access, with what permissions, and with what scope          |
| **Governance**         | Who authorised it, what constraints apply, what the escalation thresholds are    |
| **Performance record** | Every query it received, every output it produced, every escalation it triggered |

This is not transparency in the sense of "we could probably find this out if we looked hard enough." It is transparency as a structural property of the design. The SKILL.md file is readable by the knowledge worker who authored it. The plugin.json manifest and .mcp.json connector declarations are readable by IT. The audit log is accessible to compliance and governance functions. The connector permissions are documented in the deployment record. There is no property of a Cowork plugin that is inaccessible to the right role.

This property is what makes plugins deployable in regulated industries. Financial services firms, healthcare organisations, legal practices — these environments do not deploy systems they cannot audit. The historic barrier to enterprise AI was not model capability. By mid-2024, the models were capable enough. The barrier was the governance gap: organisations could not inspect, verify, or audit what their AI systems were actually doing. A Cowork plugin closes that gap by design, not by aspiration.

Consider the practical implication. A compliance officer reviewing a contract analysis agent does not have to trust that the agent applies the firm's standards correctly. She can read the SKILL.md, which specifies exactly what the agent treats as high-risk language and under what conditions it escalates. She can check the .mcp.json to verify which document repositories the agent can access. She can review the audit log to confirm that every flagged clause was reviewed by a qualified lawyer before the contract was executed. The agent becomes auditable in the same way that a licensed professional's practice is auditable — not because someone added a transparency feature, but because the framework of deployment requires it.

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
these five properties: defined identity, explicit instructions, connections to
enterprise systems via MCP, a governance framework, and a performance record.

For each property, ask me one diagnostic question, then assess whether the tool
I describe meets the standard or falls short.
```

**What you're learning:** The five-property framework is analytical, not just descriptive. By applying it to tools you already use, you are practising the diagnostic skill that Chapter 15 is building toward — the ability to assess whether an agent deployment is a genuine plugin or a prototype dressed as one.

### Prompt 2: Framework Analysis

```
The lesson describes transparency as an "architectural property" rather than an
"incidental feature." Analyse the difference between these two framings for three
specific regulated industries: financial services, healthcare, and legal.

For each industry:
1. What would an auditor need to inspect in an AI agent deployment?
2. Which of the five plugin properties would they examine?
3. What happens operationally when a property is opaque rather than inspectable?

Present your analysis as a comparison table.
```

**What you're learning:** Transparency as an architectural property has concrete operational consequences that vary by industry. This exercise trains you to see the governance implications of plugin design choices — the same perspective you will need when configuring your own plugin's governance layer in Lesson 7.

### Prompt 3: Domain Research

```
Research one high-profile case in [YOUR INDUSTRY] where an AI system was deployed
but later faced regulatory scrutiny, public challenge, or internal audit failure.

Assess that case against the five Cowork plugin properties. Which properties were
present in the deployed system? Which were absent or opaque? Based on this analysis,
would the system have passed inspection under a Cowork-style governance framework?
What would have needed to be different?
```

**What you're learning:** Historical cases of AI governance failures are the clearest evidence for why transparency is an architectural requirement rather than a nice-to-have. Applying the five-property framework to a real case builds the analytical vocabulary you will use to justify governance design decisions to colleagues and senior stakeholders.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 2: The Intelligence Layer — SKILL.md →](./02-the-intelligence-layer-skill-md.md)
