---
sidebar_position: 12
title: "Chapter 12: Version Control & Safe Experimentation"
---

# Chapter 12: Version Control & Safe Experimentation

Every Claude Code session runs `git` commands behind the scenes. When you told it to "fix my authentication logic" last chapter, it ran `git add`, `git commit`, and `git diff` — commands you've never seen. It was protecting you without your knowledge.

**What happens when it can't protect you?** When you're working outside Claude Code — editing files manually, moving folders, collaborating with someone — there's no safety net. One bad change overwrites an hour of work. One accidental delete loses a week of progress.

This chapter teaches you the system your agent already uses. Not to memorize commands — your agent handles those. To understand the *concepts* so you can direct your agent's safety features intentionally, not accidentally.

> **"Your agent already uses version control. This chapter teaches you to direct it intentionally instead of accidentally."**

### Meet Sarah

Throughout this chapter, you'll follow Sarah. She's organizing a community fundraiser with her friend Maya. They share a project folder with budget spreadsheets, flyer designs, and volunteer lists. Sarah has never used version control. By the end of this chapter, she'll wonder how she ever worked without it.

## Principles Applied

In [The Seven Principles of General Agent Problem Solving](/docs/General-Agents-Foundations/seven-principles), you learned the operational patterns that make AI collaboration reliable. This chapter puts four of them into practice — Git is where those principles become muscle memory.

| Principle | How It Applies in Git |
| --- | --- |
| **Small, Reversible Decomposition** | Commit small changes you can undo; branch for experiments |
| **Verification as Core Step** | Check status before and after every operation |
| **Constraints and Safety** | Branches isolate experiments; never push untested code |
| **Observability** | Git log shows exactly what changed, when, and why |

## What You'll Learn

By the end of this chapter, you'll be able to:

- Create project folders that track every change automatically
- Undo mistakes at any level — from a single edit to an entire experiment
- Test two ideas at once without risking your working project
- Back up your work to the cloud so a dead laptop doesn't mean lost work
- Review changes before combining them — even your own
- Follow three reusable patterns that professionals use daily

## Lessons

| Lesson | Title | Focus |
| --- | --- | --- |
| [L01](./01-git-foundations.md) | Git Foundations | Snapshots, staging, undo — the core concepts |
| [L02](./02-testing-ai-safely-with-branches.md) | Testing AI Safely with Branches | Parallel timelines for safe experimentation |
| [L03](./03-cloud-backup-portfolio.md) | Cloud Backup & Portfolio | GitHub as your safety net and career showcase |
| [L04](./04-code-review-pull-requests.md) | Code Review & Pull Requests | Review before you trust — even your own work |
| [L05](./05-reusable-git-patterns.md) | Reusable Git Patterns | Three patterns you'll use for the rest of your career |
| [Exercises](./06-version-control-exercises.md) | Exercises | Hands-on practice |
| [Quiz](./07-chapter-quiz.md) | Chapter Quiz | Test your understanding |

## Connection to Building Your First AI Employee

The version control patterns you build here provide the safety infrastructure for [building your own AI Employee](/docs/Agent-Workflow-Primitives/build-first-ai-employee). In that chapter, Git enables:

- Tracking all changes your AI Employee makes to your vault
- Rolling back automated actions that produce unexpected results
- Testing new employee behaviors on a separate branch
- Audit trails showing exactly what your employee did and when

**Version control is what makes autonomous AI operation safe.**
