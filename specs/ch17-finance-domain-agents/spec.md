# Chapter 17: Finance Domain Agents — Specification

## Status: Implementation In Progress

## Overview

Chapter 17 is the first domain chapter in Part 3 (Domain Agent Workflows). It teaches finance professionals to use Claude in Excel, Cowork finance plugins, and to build enterprise extensions via SKILL.md authoring.

## Source Materials

- **Governing artifact**: `Chapter17_Finance_Domain_Agents.md` (1,780 lines, 3 parts)
- **Research**: `specs/ch17-finance-domain-agents/research/initial-research.md` (verified against 16 primary sources)

## Corrections Applied

1. **Connector narrative**: Rewritten from "two separate ecosystems" to "same MCP connectors, different scope (single-workbook vs multi-app)"
2. **Plan availability**: Pro added to all plan references (Pro, Max, Team, Enterprise)
3. **Model switching**: Sonnet 4.6 / Opus 4.6 selection mentioned
4. **New Lesson 09**: Extracting Finance Domain Knowledge (KEM applied to finance)
5. **Public-data fallback paths**: Added for exercises requiring paid data subscriptions
6. **Security callout**: Prompt injection risks in spreadsheets from untrusted sources

## Lesson Structure (13 lessons)

| #   | File                                                | Title                                           |
| --- | --------------------------------------------------- | ----------------------------------------------- |
| 01  | 01-the-assistant-and-the-agent.md                   | The Assistant and the Agent                     |
| 02  | 02-understanding-workbooks-you-didnt-build.md       | Understanding Workbooks You Didn't Build        |
| 03  | 03-scenarios-errors-and-model-building.md           | Scenarios, Errors, and Model Building           |
| 04  | 04-agent-skills-market-analysis.md                  | The Six Agent Skills: Market Analysis           |
| 05  | 05-agent-skills-deal-and-research.md                | The Six Agent Skills: Deal and Research         |
| 06  | 06-from-assistant-to-agent.md                       | From Assistant to Agent: Cowork Finance Plugins |
| 07  | 07-the-financial-services-plugin-suite.md           | The Financial Services Plugin Suite             |
| 08  | 08-cross-app-orchestration.md                       | Cross-App Orchestration                         |
| 09  | 09-extracting-finance-domain-knowledge.md           | Extracting Finance Domain Knowledge             |
| 10  | 10-enterprise-extensions-risk-and-compliance.md     | Enterprise Extensions: Risk and Compliance      |
| 11  | 11-enterprise-extensions-operations-and-strategy.md | Enterprise Extensions: Operations and Strategy  |
| 12  | 12-your-extension-roadmap.md                        | Your Extension Roadmap and Chapter Summary      |
| 13  | 13-chapter-quiz.md                                  | Chapter Quiz                                    |

## Per-Lesson Deliverables

Each lesson produces 3 files: `.md`, `.summary.md`, `.flashcards.yaml`
Plus chapter-level `README.md`

**Total files: 40** (13 x 3 + 1 README)
