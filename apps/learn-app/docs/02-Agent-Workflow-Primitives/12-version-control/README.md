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

## Before You Start

You need three things before starting the lessons: a GitHub account, Git installed, and a one-time Git configuration. If you already have all three, skip to Lesson 1.

**Git** and **GitHub** are not the same thing. Git is a tool that runs on your computer and tracks changes to your files. GitHub is a website that stores copies of your Git projects in the cloud — if your laptop breaks, your work survives on GitHub. Git works without GitHub. GitHub doesn't work without Git. You'll use Git locally in Lessons 1-2, then connect it to GitHub in Lesson 3.

<details>
<summary><strong>1. Create a GitHub Account</strong></summary>

You'll use this in [Lesson 3](./03-cloud-backup-portfolio.md), but create it now — you'll need the email address in step 3 below.

1. Visit **github.com** and click "Sign up"
2. Choose a username carefully — this becomes your public portfolio URL: `github.com/yourname`
3. Complete email verification

</details>

<details>
<summary><strong>2. Install Git</strong></summary>

Open your terminal and run:

```bash
git --version
```

If you see something like `git version 2.39.0` — skip to step 3.

**macOS** — run one of these:

```bash
brew install git          # Option 1: Homebrew (recommended)
xcode-select --install    # Option 2: Xcode Command Line Tools
```

**Windows:**

1. Download Git from [git-scm.com/download/win](https://git-scm.com/download/win)
2. Run the installer with default settings (keep clicking "Next")
3. Restart your terminal after installation

**Linux:**

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install git

# Fedora
sudo dnf install git

# Arch Linux
sudo pacman -S git
```

After installing, close and reopen your terminal, then verify with `git --version`.

</details>

<details>
<summary><strong>3. Tell Git Who You Are</strong></summary>

Git labels every commit with your name and email. Use the same email you registered on GitHub — this links your commits to your GitHub profile.

```bash
git config --global user.name "Your Name"
git config --global user.email "your.github.email@example.com"
```

This isn't creating an account. It's a label that appears in your commit history. You only run this once.

</details>

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
| [L04](./04-code-review-pull-requests.md) | Code Review, Pull Requests & Reusable Patterns | Review before you trust, then build lasting habits |
| [Exercises](./05-version-control-exercises.md) | Exercises (Optional) | Hands-on practice |
| [Quiz](./06-chapter-quiz.md) | Chapter Quiz (Optional) | Test your understanding |

## Connection to Building Your First AI Employee

The version control patterns you build here provide the safety infrastructure for [building your own AI Employee](/docs/Agent-Workflow-Primitives/build-first-ai-employee). In that chapter, Git enables:

- Tracking all changes your AI Employee makes to your vault
- Rolling back automated actions that produce unexpected results
- Testing new employee behaviors on a separate branch
- Audit trails showing exactly what your employee did and when

**Version control is what makes autonomous AI operation safe.**
