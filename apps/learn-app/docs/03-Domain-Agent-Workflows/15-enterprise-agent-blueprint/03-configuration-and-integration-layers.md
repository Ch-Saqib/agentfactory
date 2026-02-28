---
sidebar_position: 3
title: "The Plugin Infrastructure"
description: "Understand how plugin.json, .mcp.json, and settings.json form the infrastructure layer of a Cowork plugin — the components that developers and IT maintain so that your SKILL.md has the environment and data connections it needs to operate"
keywords:
  [
    "plugin.json",
    ".mcp.json",
    "MCP connector",
    "settings.json",
    "Cowork plugin",
    "enterprise integration",
    "plugin manifest",
    "infrastructure literacy",
    "plugin architecture",
  ]
chapter: 15
lesson: 3
duration_minutes: 25

# HIDDEN SKILLS METADATA
skills:
  - name: "Read and Interpret Plugin Infrastructure Files"
    proficiency_level: "B1"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can identify the three infrastructure files in a Cowork plugin (plugin.json, .mcp.json, settings.json), explain what each configures, and describe who owns each file"

  - name: "Distinguish MCP Connector States"
    proficiency_level: "A2"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Safety"
    measurable_at_this_level: "Student can describe what a working MCP connector does, what happens when one is unavailable, and why fabricating data is the dangerous failure mode to watch for"

  - name: "Apply Infrastructure Literacy"
    proficiency_level: "A2"
    category: "Applied"
    bloom_level: "Understand"
    digcomp_area: "Information Literacy"
    measurable_at_this_level: "Student can explain the concept of infrastructure literacy — knowing enough to detect and accurately describe an infrastructure problem without needing to fix it themselves"

learning_objectives:
  - objective: "Identify the three infrastructure files in a Cowork plugin and explain what each one configures"
    proficiency_level: "B1"
    bloom_level: "Apply"
    assessment_method: "Given an unfamiliar plugin directory listing, student can name each infrastructure file and describe its purpose in one sentence"

  - objective: "Explain what MCP connectors do at a conceptual level, including the three states a connector can be in"
    proficiency_level: "A2"
    bloom_level: "Understand"
    assessment_method: "Student can describe a working connector, a failed connector showing explicit unavailability, and the dangerous failure mode of fabricated data"

  - objective: "Articulate the knowledge worker's infrastructure literacy requirement — enough to detect a problem, not enough to fix it"
    proficiency_level: "A2"
    bloom_level: "Understand"
    assessment_method: "Student can explain in their own words what infrastructure literacy means and why it matters for productive collaboration with IT"

cognitive_load:
  new_concepts: 4
  concepts_list:
    - "plugin.json manifest (identity and versioning)"
    - ".mcp.json connector declarations (data source access)"
    - "settings.json default plugin behaviour configuration"
    - "connector failure modes (stale, unavailable, fabricated)"
  assessment: "4 concepts at A2-B1 level — within the 7-10 cognitive budget for intermediate content. The plugin directory structure anchors all four concepts concretely."

differentiation:
  extension_for_advanced: "Consider the security implications of the .mcp.json file. If a malicious actor could modify this file, what kinds of data exfiltration or unauthorised access could they enable? Why does this make the plugin review and deployment process a critical security control point?"
  remedial_for_struggling: "Focus on the plugin.json manifest alone. Answer four questions: What is the plugin's name? What does it do? What version is it? Who authored it? Then look at the .mcp.json and list the names of the external systems the plugin connects to. Do not worry about how the connections work — just identify what they connect to."

teaching_guide:
  lesson_type: "core"
  session_group: 1
  session_title: "The Three Components"
  key_points:
    - "plugin.json is a simple manifest — name, description, version, author. It identifies the plugin but does not configure its intelligence or behaviour."
    - ".mcp.json declares which external systems the plugin connects to. Each entry names an MCP server and provides its connection configuration. This is where data access is defined."
    - "settings.json configures default plugin behaviour — currently its primary use is the agent key, which activates a custom agent as the main thread. Organisation administrators can override these defaults."
    - "Governance settings (permissions, audit, shadow mode) are configured in Cowork's org admin panel, not in any file within the plugin package."
    - "The dangerous connector failure mode is not unavailability — it is an agent fabricating data when a connector is down. This must be named explicitly."
    - "Infrastructure literacy is a professional skill: enough to detect and describe problems accurately, enabling productive conversation with the people who fix them."
  misconceptions:
    - "Students may think plugin.json contains the agent's instructions or behaviour — it contains only identity metadata (name, description, version, author)"
    - "Students may think governance settings like audit logging and shadow mode are configured inside the plugin — they are configured by organisation administrators in Cowork's admin panel"
    - "Students may think they need to understand how MCP connectors work technically — they need to understand what connectors enable and what to watch for, not how to build or debug them"
    - "Students may think that if a connector fails, the agent will always show an error message — in poorly configured systems, the agent may silently fabricate data instead"
  discussion_prompts:
    - "Look at the .mcp.json example. If the Salesforce MCP server went down, what would you expect a well-configured agent to do? What would a poorly configured agent do?"
    - "If you were a senior analyst and your research agent gave you market data that seemed oddly specific and coherent, but you had not verified that the data connector was working — what would you do?"
  teaching_tips:
    - "Walk through the plugin directory structure first so students have a spatial map of where each file lives. The directory listing is the anchor for the entire lesson."
    - "Emphasise that plugin.json is deliberately minimal. Students may expect it to be the 'main configuration file' — it is not. The intelligence lives in SKILL.md, the connections live in .mcp.json."
    - "Frame infrastructure literacy positively: it is not about knowing less, it is about knowing the right things to be effective and to have productive conversations with IT."
  assessment_checks:
    - question: "What does plugin.json contain, and what does it NOT contain?"
      expected_response: "plugin.json contains only identity metadata: the plugin's name, description, version number, and author. It does not contain the agent's instructions (that is SKILL.md), data connections (that is .mcp.json), or governance settings (those are in the org admin panel)."
    - question: "What are the three states an MCP connector can be in, and which one is dangerous?"
      expected_response: "Working (the connector is running and returning live data), explicitly unavailable (the connector is down and the agent reports it cannot access that data source), and fabricating (the most dangerous state — the connector is unavailable but the agent invents data rather than reporting the gap). The fabricating state is dangerous because it is undetectable without external verification."
    - question: "Where are governance settings like audit logging and shadow mode configured?"
      expected_response: "Governance settings are configured in Cowork's organisation admin panel by administrators, not in any file within the plugin package itself."
---

# The Plugin Infrastructure

In Lesson 2, you examined the SKILL.md — the intelligence layer of a Cowork plugin, written in plain English and owned by the knowledge worker. The SKILL.md tells the agent who it is, what it does, and how it behaves. But a SKILL.md without infrastructure is an expert locked in an empty room. The surrounding files — plugin.json, .mcp.json, and settings.json — provide the identity, data connections, and default configuration that make the agent operational.

These infrastructure components are owned by developers and IT, not by the knowledge worker. This is not a limitation; it is a design choice that reflects where the technical complexity actually sits. Your role with respect to these files is not to author them but to understand them well enough to verify that they match your intentions, and to detect when something is wrong. That combination — sufficient understanding without operational responsibility — is what this lesson will build.

There is a professional skill embedded in this lesson that does not have a widely used name but deserves one: **infrastructure literacy**. It means knowing enough about the systems you depend on to detect problems accurately, describe them precisely, and have productive conversations with the people who fix them. It is not about becoming a systems engineer. It is about being a competent professional user of complex infrastructure.

## The Plugin Directory Structure

Before examining each file individually, it helps to see where they live in relation to each other. A Cowork plugin is a directory with a specific structure:

```
financial-research/
├── .claude-plugin/
│   └── plugin.json        # Manifest: name, description, version, author
├── .mcp.json              # MCP server declarations
├── commands/              # Slash commands
├── skills/                # SKILL.md files (your contribution)
├── agents/                # Sub-agents
├── hooks/                 # Event handlers
├── settings.json          # Default settings
└── .lsp.json              # LSP server configs
```

Notice the division of labour built into this structure. The `skills/` directory is where your SKILL.md files live — the intelligence layer you author. Everything else is infrastructure that developers and IT maintain. This lesson covers the three infrastructure files that matter most for your understanding: plugin.json, .mcp.json, and settings.json.

## Component One: The Plugin Manifest (plugin.json)

The plugin.json file lives inside the `.claude-plugin/` directory. It is the plugin's identity card — and it is deliberately minimal. Here is the complete plugin.json for a Financial Research Agent:

```json
{
  "name": "financial-research",
  "description": "Financial research agent for FTSE equity analysis and market data retrieval",
  "version": "1.2.0",
  "author": {
    "name": "Acme Financial"
  }
}
```

That is the entire file. Four fields: `name`, `description`, `version`, and `author`.

This minimalism surprises people. If you expected the manifest to be the "main configuration file" containing the agent's instructions, permissions, and data connections, that expectation is wrong — and the mismatch is worth understanding.

The `name` field is a machine-readable identifier. It determines how the Cowork platform references this plugin internally and how it appears in deployment systems. The `description` field tells the plugin manager — and anyone browsing the marketplace — what this plugin does. It is displayed in discovery interfaces and should clearly state the plugin's purpose. The `version` field matters for change management: when IT updates any file in the plugin, the version number makes it possible to trace which configuration was in effect at any point in time. The `author` field identifies ownership — useful for auditing and for knowing which team to contact when something needs to change.

What plugin.json does _not_ contain is equally important. It does not contain the agent's instructions (that is the SKILL.md). It does not configure data connections (that is .mcp.json). It does not set governance policies like audit logging or shadow mode (those are configured in Cowork's organisation admin panel, not in any file within the plugin). The manifest identifies the plugin. Other components configure it.

## Component Two: MCP Connector Declarations (.mcp.json)

The .mcp.json file is where the plugin's data connections are declared. It specifies which MCP (Model Context Protocol) servers the plugin connects to — and through those servers, which external systems the agent can access.

An MCP server is a small service that acts as a bridge between the agent and an external system. When the Financial Research Agent needs current market data, it does not connect to Bloomberg directly. It communicates with a Bloomberg MCP server, which handles authentication, executes queries, translates data formats, and returns structured results. Each external system the agent connects to has its own MCP server.

The .mcp.json file declares which of these servers the plugin uses. For the Financial Research Agent, it might declare connections to a Bloomberg data server, a Snowflake analytics server, and a SharePoint document server. Each entry names the server and provides its connection configuration — the address, the protocol, and any parameters needed to establish the connection.

This design has several advantages. The agent does not need to know how to authenticate with each external system — that complexity lives in the MCP server. The agent does not need to handle different data formats from different sources — the server normalises them. And when external systems change their APIs or authentication protocols, only the MCP server needs to be updated, not the agent itself.

**Who writes .mcp.json?** Developers and IT. They configure the servers, manage the credentials, and maintain the connections. Your role as the knowledge worker is to understand what the .mcp.json enables — which data sources your agent can reach — and to verify that those connections match the requirements of your workflow.

### The Three Connector States

The practical literacy question is not how MCP servers work internally — that is an IT concern — but what state a connector is in at any given moment. There are three states:

**Working.** The MCP server is running, the authentication is valid, and queries return live data from the external system. When a connector is working, the agent has access to current information. Research reflects today's data, not last week's cached snapshot.

**Explicitly unavailable.** The MCP server is not running or cannot authenticate. In a well-configured system, the agent detects this state and tells the user it cannot access that data source. "I was unable to retrieve current Bloomberg data for this analysis. Please verify the connector status with your IT team." This is the correct failure mode — it is transparent about the limitation.

**Fabricating data.** This is the dangerous failure mode, and it must be named explicitly. In a poorly designed or misconfigured system, when a connector is unavailable, the agent may draw on its training data or internal knowledge to produce responses that appear to be live data but are not. The output looks like a real market data response. The numbers are plausible. The format is correct. But the information is invented.

The reason this is categorically different from the second state is that it is undetectable without external verification. An agent that says "I cannot access Bloomberg" gives you accurate information about its limitations. An agent that generates a plausible-looking market data table without access to Bloomberg has produced a hallucination presented as fact — and in a financial context, acting on fabricated data can have serious consequences.

Cowork's architecture is designed to make the third state unlikely. The platform and connector design enforce explicit failure reporting rather than silent substitution. But no architecture eliminates the risk entirely, which is why infrastructure literacy includes knowing this risk exists and building the habit of verifying data provenance when stakes are high.

## Component Three: Default Settings (settings.json)

The settings.json file configures default plugin behaviour. Its current primary use is the `agent` key, which activates a custom agent definition as the plugin's main conversation thread. When a plugin includes a settings.json with an `agent` key pointing to an agent file, that agent becomes the entry point when a user starts a session with the plugin.

This scope is deliberately narrow today — settings.json may support additional configuration keys as the platform evolves — but even a single key carries architectural significance. It means the plugin developer decides which agent a user interacts with by default, while the organisation retains the ability to override that choice through the admin panel.

The distinction between settings.json and governance controls is important. Settings.json lives inside the plugin package and configures developer-chosen defaults for plugin behaviour. Governance controls — audit logging, output review requirements, shadow mode, escalation routing — are configured by organisation administrators in Cowork's admin panel. They sit above the plugin, applying organisation-wide policies that no individual plugin can override.

This separation is a security design: the people who build plugins cannot weaken the governance controls that the organisation applies to them.

## A Note on Governance

If you are wondering where audit logging, permission scopes, shadow mode, and escalation routing are configured — the answer is: not inside the plugin. These governance settings live in Cowork's organisation admin panel, managed by administrators who set policies that apply across all plugins in the organisation.

This means governance is not something a plugin author decides. It is something the organisation enforces. A plugin author cannot disable audit logging for their plugin, and a knowledge worker cannot bypass review requirements. The governance layer wraps around the plugin from the outside, which is precisely how enterprise security should work.

You will examine governance in detail in Lesson 7 when the chapter covers shadow mode and compliance frameworks. For now, the key point is architectural: governance is organisational, not per-plugin.

## The Relationship Between Infrastructure and Intelligence

With all three infrastructure files in view, the division of labour becomes clear:

| Component               | What It Does                                                          | Who Owns It        |
| ----------------------- | --------------------------------------------------------------------- | ------------------ |
| **plugin.json**         | Identifies the plugin (name, description, version, author)            | Developers         |
| **.mcp.json**           | Declares data connections to external systems                         | Developers / IT    |
| **settings.json**       | Configures default plugin behaviour (e.g., activating a custom agent) | Developers         |
| **SKILL.md**            | Defines the agent's expertise and behaviour                           | Knowledge worker   |
| **Governance settings** | Enforces organisational policies (audit, review, shadow mode)         | Org administrators |

Your contribution — the SKILL.md — sits at the centre. It is the intelligence that makes the agent useful. But it operates within the environment that the infrastructure files create. A SKILL.md that instructs the agent to analyse Bloomberg data only works if the .mcp.json declares a Bloomberg MCP server and IT has configured that server to be available. A SKILL.md that describes careful, audited research behaviour only matters if the organisation's governance settings actually enforce audit logging.

Understanding this relationship is what makes you an effective collaborator rather than someone who writes instructions in isolation and hopes the infrastructure team gets the rest right.

### What the Knowledge Worker Needs to Know

You do not need to build MCP servers, write plugin.json files, or manage settings.json. That work belongs to developers and IT. What you need is enough understanding to operate as a competent professional user of the infrastructure.

| Capability                      | What It Looks Like in Practice                                                                                                                                                                  |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Verify connector alignment**  | Confirm that the MCP servers declared in .mcp.json match the data sources your workflow actually requires                                                                                       |
| **Detect data quality issues**  | Recognise when an agent's output may be based on unavailable or stale data                                                                                                                      |
| **Report problems accurately**  | Describe an infrastructure problem in terms IT can act on — "the Bloomberg connector appears to be returning stale data, last updated three days ago" is more useful than "the agent seems off" |
| **Understand the architecture** | Know which file controls what, so you can direct questions to the right people                                                                                                                  |

This is infrastructure literacy: not operational depth, but sufficient awareness to be a capable professional user and an effective collaborator with the people who maintain the infrastructure you depend on.

## Try With AI

Use these prompts in Anthropic Cowork or your preferred AI assistant to practise reasoning about plugin infrastructure.

### Prompt 1: Plugin Structure Annotation

```
I'm going to describe a Cowork plugin directory structure. For each
infrastructure file (plugin.json, .mcp.json, settings.json), explain:
(1) what it configures, (2) who owns it, and (3) what would happen if
it were missing or misconfigured.

Then tell me: where do the governance settings like audit logging and
shadow mode live? Why don't they live inside the plugin?

The plugin is called "legal-contract-reviewer" and it connects to
a LexisNexis database, a SharePoint document library, and a DocuSign
signing service.
```

**What you're learning:** Understanding the plugin directory structure requires more than memorising file names — it requires knowing what each file controls and who is responsible for it. This prompt practises treating the infrastructure as a map of responsibilities, not just a list of files.

### Prompt 2: Connector Failure Diagnosis

```
I'm using a Financial Research Agent that connects to Bloomberg,
Snowflake, and SharePoint through MCP servers declared in its
.mcp.json file. The agent has produced a report with detailed market
data and company financials for three competitors. I haven't verified
whether the Bloomberg MCP server was running when the report was
generated.

Help me think through: (1) what questions I should ask before trusting
this data, (2) how I would verify whether the data is live or
fabricated, and (3) what I should tell IT if I suspect a connector
problem. Be specific about what "fabricated data" looks like versus
"live data with genuine uncertainties."
```

**What you're learning:** Infrastructure literacy includes knowing how to verify data provenance — not just trusting that the agent has access to what it is supposed to have access to. This prompt practises the reasoning process for high-stakes data verification, which is a core professional skill when working with AI-powered research tools.

### Prompt 3: Infrastructure Requirements Conversation

```
I'm a senior analyst preparing to work with IT to set up a new Cowork
plugin for our research team. I need to explain what MCP server
connections the plugin requires so that IT can write the .mcp.json file
and configure the servers.

Our workflow requires: live market data from Bloomberg, access to our
internal analytics database in Snowflake (specifically the models and
deal history tables, not HR data), and read access to approved research
templates in SharePoint.

Help me draft a clear, specific request to IT that describes what
connections I need, what data each connection should provide access to,
and any access restrictions I want to emphasise. Frame this as a
knowledge worker communicating requirements to a technical team.
```

**What you're learning:** Even though IT writes the .mcp.json and configures the MCP servers, the knowledge worker specifies the requirements. This prompt practises the communication skill of translating workflow needs into infrastructure requirements — clearly enough that IT can implement them correctly on the first pass.

## Flashcards Study Aid

<Flashcards />

---

Continue to [Lesson 4: The Three-Level Context System →](./04-three-level-context-system.md)
