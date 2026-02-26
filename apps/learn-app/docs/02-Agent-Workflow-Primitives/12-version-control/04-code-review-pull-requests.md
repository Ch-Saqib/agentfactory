---
sidebar_position: 4
chapter: 12
lesson: 4
title: "Code Review & Pull Requests"
description: "Review changes before combining them — even your own. Pull requests add an 'are you sure?' step to your workflow."
duration_minutes: 45
keywords: [pull request, code review, diff, merge, github, collaboration]

# HIDDEN SKILLS METADATA
skills:
  - name: "Understand Pull Requests"
    proficiency_level: "A2"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Communication"
    measurable_at_this_level: "Student can explain PRs as a review-before-merge step"

  - name: "Create Pull Request"
    proficiency_level: "A2"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Communication"
    measurable_at_this_level: "Student can create a PR with clear title and description"

  - name: "Review PR Diff"
    proficiency_level: "A2"
    category: "Technical"
    bloom_level: "Analyze"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student can read a diff and verify changes match intent"

  - name: "Document AI Assistance"
    proficiency_level: "A2"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Critical Thinking"
    measurable_at_this_level: "Student includes what AI generated vs what they modified in PR description"

learning_objectives:
  - objective: "Create a pull request from a feature branch to main"
    proficiency_level: "A2"
    bloom_level: "Apply"
    assessment_method: "Student creates a PR on GitHub with clear title and description"

  - objective: "Review a code diff to verify changes match intent"
    proficiency_level: "A2"
    bloom_level: "Analyze"
    assessment_method: "Student reads diff output and identifies what changed and whether it's correct"

  - objective: "Document AI assistance transparently in PR descriptions"
    proficiency_level: "A2"
    bloom_level: "Apply"
    assessment_method: "Student writes PR description that notes which parts AI helped with"

  - objective: "Merge an approved PR into main"
    proficiency_level: "A2"
    bloom_level: "Apply"
    assessment_method: "Student merges PR and verifies changes on main"

cognitive_load:
  new_concepts: 3
  concepts_list:
    - "Pull requests (review before merging)"
    - "Diff review (reading what changed)"
    - "Noting AI assistance in PR descriptions"
  assessment: "3 concepts (within A2 limit) ✓"
teaching_guide:
  lesson_type: "core"
  session_group: 2
  session_title: "GitHub and Collaboration"
  key_points:
    - "Pull requests add a forced pause between 'I made changes' and 'changes are live' — this pause prevents mistakes"
    - "The diff review is where you catch problems — read it like checking your work before turning in an exam"
    - "Noting which parts AI helped with is professional practice, not a confession"
    - "Even solo developers benefit from the review habit"
  misconceptions:
    - "Students think PRs are only for teams — solo developers benefit from the review pause"
    - "Students want to hide AI assistance — transparency is a professional strength"
    - "Students think they can skip review if tests pass — tests catch correctness, not intent mismatches"
  discussion_prompts:
    - "If an employer reads your PR description, what impression do they get about how you work with AI?"
    - "You see a function in the diff you don't understand. What should you do before clicking merge?"
  teaching_tips:
    - "Have students create an actual PR during the lesson — the GitHub interface makes it concrete"
    - "Walk through reading a diff aloud, modeling the internal review dialogue"
  assessment_quick_check:
    - "What three things should a PR description include?"
    - "What should you do if you see code in the diff you don't understand?"
    - "Why is noting AI assistance a professional strength?"

generated_by: "content-implementer v2.0.0"
created: "2025-01-17"
last_modified: "2026-02-26"
version: "2.0.0"
---

# Code Review & Pull Requests

Maya spent the weekend updating the volunteer list while Sarah redesigned the budget. Now they need to combine their work. But Maya renamed some columns, and Sarah moved some rows. If they just copy-paste, they'll lose each other's changes.

Pull requests solve this. They're a "let me see what you changed before we combine" step.

In 2012, a financial company called Knight Capital deployed code changes to their trading system without review. A single server out of eight received the wrong version. In 45 minutes, the system made millions of unintended trades. They lost $440 million — nearly destroying a company that took 17 years to build. A pause to review before deploying would have caught the error. ([Source](https://www.henricodolfing.ch/en/case-study-4-the-440-million-software-error-at-knight-capital/))

> **"Never merge what you don't understand — even if you wrote it yesterday."**

---

## From Solo to Review

So far, everything you've done has been solo — just you and your agent. Pull requests add one more step: a pause to review before changes become permanent. Think of it as an "are you sure?" dialog for your entire project.

Even if you're working alone, this habit matters. You'll catch mistakes. You'll write better descriptions of your work. And when you start collaborating with others, you'll already know the workflow.

---

## What Is a Pull Request?

A **pull request** (PR) is a GitHub feature that says: "Here are my changes. Review them before merging into main."

The workflow:

1. You push a feature branch to GitHub
2. You create a PR on GitHub (comparing feature branch to main)
3. GitHub shows a **diff** — what changed
4. You review the changes
5. You merge when satisfied

![PR lifecycle showing creation, review phase, and merge decision](https://pub-80f166e40b854371ac7b05053b435162.r2.dev/books/ai-native-dev/static/images/part-2/chapter-09/pull-request-lifecycle-workflow.png)

**Why PRs matter**: Commits save snapshots. PRs force you to *evaluate* those snapshots before they reach `main`. It's the difference between writing and proofreading.

---

## Create Your First PR

First, create a feature branch with changes and push it to GitHub.

**What you tell your agent**: "Create a branch for updating the volunteer list, add a change, and push it to GitHub."

**What the agent does**:

```bash
git checkout -b feature/update-volunteers
echo "Volunteers: Sarah, Maya, Jordan, Alex" > volunteers.txt
git add volunteers.txt
git commit -m "Add Alex to volunteer list"
git push -u origin feature/update-volunteers
```

Now create the PR on GitHub:

1. Go to your repository on github.com
2. You'll see a banner: "feature/update-volunteers had recent pushes"
3. Click "Compare & pull request"
4. Fill in the title: `Add Alex to volunteer list`
5. Write the description (see below)
6. Click "Create pull request"

---

## Write a Clear PR Description

A good PR description answers three questions:

1. **What changed?** — A brief summary
2. **How was it tested?** — What you verified
3. **What role did AI play?** — Which parts your agent helped with

Here's what a professional PR description looks like:

```markdown
## Summary

Added Alex to the volunteer list for the fundraiser.

## Changes

- Updated volunteers.txt with new volunteer name

## AI Assistance

- Claude Code helped draft the commit message
- I verified the file contents manually

## Testing

- Confirmed file contents with `cat volunteers.txt`
- Verified no other files were changed with `git status`
```

Noting which parts AI helped with isn't a confession. It's professional practice. Employers see someone who works transparently and takes ownership of the final result.

---

## Review the Diff

Before merging, read the diff. On the GitHub PR page, click "Files changed."

```diff
- Volunteers: Sarah, Maya, Jordan
+ Volunteers: Sarah, Maya, Jordan, Alex
```

Red lines show what was removed. Green lines show what was added. Ask yourself:

1. **Does it match my intent?** — "I wanted to add Alex... yes, I see Alex added."
2. **Is anything unexpected?** — "No other files changed. Good."
3. **Do I understand every change?** — "Yes, it's one line."

If you see something you don't understand — especially AI-generated code — don't merge. Ask your agent to explain it first.

Can you read it? Do you understand what changed? If yes, merge. If not, ask questions first.

---

## Merge and Clean Up

On the GitHub PR page, click "Merge pull request." Then "Confirm merge."

Back in your terminal, update your local project:

```bash
git switch main
git pull
```

Your main branch now includes the changes. The feature branch can be deleted on GitHub (it offers a button after merging) and locally:

```bash
git branch -d feature/update-volunteers
```

---

## A Review Checklist

Use this checklist every time you review a PR, whether it's yours or someone else's:

- Does the change match the stated intent?
- Are there unexpected files or changes?
- Do I understand every line in the diff?
- Are there sensitive files (secrets, keys) included by accident?
- Is the PR description clear enough that future-you will understand it?

---

You've learned the pieces. Now let's turn them into patterns you'll use for the rest of your career.

---

## Try With AI

**Write your PR description:**

> "I just created a pull request where I updated my project with help from my AI agent. Help me write a professional PR description that explains what changed, how I tested it, and what my agent helped with. Make it clear and honest."

**Practice reviewing a diff:**

> "Show me an example code diff and walk me through how to review it step by step. What questions should I ask myself? What red flags should I watch for? Help me build a mental checklist for code review."

**Handle review feedback:**

> "Someone reviewed my PR and left comments asking me to change something. How should I respond? What if I disagree with their suggestion? Give me a framework for productive code review conversations."

**Create a self-review habit:**

> "Before I submit PRs for review, I want to catch my own mistakes. Walk me through a self-review checklist: what to check in the code diff, in the PR description, in my commit messages, and in my test coverage."
