---
sidebar_position: 5
chapter: 12
lesson: 5
title: "Reusable Git Patterns"
description: "Three patterns professionals follow every day — commit before experimenting, branch for testing, push for backup"
duration_minutes: 45
keywords: [git patterns, workflow, commit before experiment, branch test merge, push backup]

# HIDDEN SKILLS METADATA
skills:
  - name: "Recognize Recurring Patterns"
    proficiency_level: "A2"
    category: "Conceptual"
    bloom_level: "Analyze"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student identifies 3 recurring patterns from L01-L04"

  - name: "Document Reusable Workflows"
    proficiency_level: "A2"
    category: "Technical"
    bloom_level: "Create"
    digcomp_area: "Digital Literacy"
    measurable_at_this_level: "Student creates a personal git-workflow.md reference"

  - name: "Apply Patterns to New Scenarios"
    proficiency_level: "A2"
    category: "Applied"
    bloom_level: "Apply"
    digcomp_area: "Problem-Solving"
    measurable_at_this_level: "Student applies documented patterns without looking at lesson text"

learning_objectives:
  - objective: "Identify three recurring Git patterns from lessons 1-4"
    proficiency_level: "A2"
    bloom_level: "Analyze"
    assessment_method: "Student names all three patterns and when to use each"

  - objective: "Create a personal workflow reference document"
    proficiency_level: "A2"
    bloom_level: "Create"
    assessment_method: "Student writes git-workflow.md in their own words"

  - objective: "Apply documented patterns to a new scenario"
    proficiency_level: "A2"
    bloom_level: "Apply"
    assessment_method: "Student completes new scenario using only their documentation"

cognitive_load:
  new_concepts: 3
  concepts_list:
    - "Commit-Before-Experiment pattern"
    - "Branch-Test-Merge pattern"
    - "Push-for-Backup pattern"
  assessment: "3 concepts (no new Git commands — synthesis of existing knowledge) ✓"
teaching_guide:
  lesson_type: "core"
  session_group: 2
  session_title: "GitHub and Collaboration"
  key_points:
    - "Three patterns cover 90% of daily Git use — students already do them, now they name them"
    - "Writing patterns down is more valuable than memorizing commands — a reference works under pressure"
    - "The test is applying patterns to a new scenario using only the documentation"
    - "Professionals don't memorize Git commands — they follow patterns and look up syntax"
  misconceptions:
    - "Students think this lesson teaches new commands — it teaches zero new commands; value is in pattern recognition"
    - "Students treat the workflow document as an assignment — it's a personal reference they should actually use"
    - "Students think professionals memorize all Git commands — they rely on patterns and references"
  discussion_prompts:
    - "When you applied patterns to the new scenario, did you need to look back at earlier lessons?"
    - "If a teammate joins next week, could they follow your documentation without asking you questions?"
  teaching_tips:
    - "Give students quiet time for the reflection — genuinely thinking about patterns before documenting them"
    - "Have students complete the new scenario using ONLY their workflow document"
  assessment_quick_check:
    - "Name the three Git patterns without looking at your notes"
    - "In a new scenario, which pattern do you apply first and why?"
    - "If your documentation wasn't enough for the scenario, what should you do?"

generated_by: "content-implementer v2.0.0"
created: "2025-11-17"
last_modified: "2026-02-26"
version: "2.0.0"
---

# Reusable Git Patterns

Sarah notices something. Every time she works on the fundraiser project, she does the same three things: saves before trying anything risky, tests changes on a separate branch, and backs up to the cloud. She's been doing this instinctively since Lesson 1. Now she writes it down — so she never has to think about it again.

> **"Professionals don't memorize Git commands. They follow three patterns."**

This lesson teaches zero new commands. Everything here is something you've already done. The value is in recognizing the patterns and writing them down so you can follow them on autopilot.

---

## The Three Patterns

### Pattern 1: Commit Before Experimenting

Before you let your agent try anything risky, take a snapshot first.

**When to use it:**
- Before asking AI to make changes
- Before trying something you're not sure about
- Anytime you think "this might go wrong"

**What you tell your agent**: "Save the current state before we try anything risky."

**What the agent does**:

```bash
git add .
git commit -m "Before refactoring: working state"
```

**Why it matters**: If the experiment fails, you can get back to this exact state with `git restore` or `git reset`. Without this snapshot, there's nothing to go back to.

---

### Pattern 2: Branch-Test-Merge

When you're testing something that might break your project, do it on a separate branch.

**When to use it:**
- Testing multiple approaches
- Making changes that could break things
- Working on something while keeping `main` stable

**The workflow:**

```bash
# 1. Create a branch for your experiment
git checkout -b experiment/new-approach

# 2. Make changes, test them
# ... work happens here ...
git add .
git commit -m "Test new approach"

# 3. If it works → merge into main
git switch main
git merge experiment/new-approach
git branch -d experiment/new-approach

# 3. If it fails → delete the branch
git switch main
git branch -D experiment/new-approach
```

**Why it matters**: Main stays clean. If the experiment is terrible, you delete the branch and nothing happened. If it's great, you merge it in.

---

### Pattern 3: Push for Backup

After meaningful work, push to GitHub. Don't wait until end of day.

**When to use it:**
- After completing a feature
- After merging a branch
- Before closing your laptop
- Before doing anything risky

**What you tell your agent**: "Push everything to GitHub."

**What the agent does**:

```bash
git push
```

Then verify on GitHub that your commits appear.

**Why it matters**: Your laptop can break, get stolen, or run out of battery at the worst moment. If your code is on GitHub, you lose nothing.

---

## How the Patterns Work Together

Here's what a typical work session looks like:

```
1. Start: git status          (Where did I leave off?)
2. Before AI: commit          (Pattern 1 — save current state)
3. Risky change: branch       (Pattern 2 — isolate the experiment)
4. Test the changes           (Does it work?)
5. Decision: merge or delete  (Keep the good, discard the bad)
6. Push to GitHub             (Pattern 3 — backup)
```

Sarah follows this every time she works on the fundraiser. She doesn't think about which Git command to run. She thinks about which pattern to apply. The agent handles the commands.

---

## Write It Down

Create a file called `git-workflow.md` in your project. Write the three patterns in your own words. Include:

- **When** you use each pattern
- **What** you tell your agent
- **Why** it matters

The best reference is one written in your own language. Don't copy this lesson — describe the patterns as you understand them.

---

## Apply Your Patterns: Sarah's Final Challenge

Sarah's fundraiser is next month. A new volunteer, Alex, wants to help with the project website. Sarah needs to:

1. Save the current state of the project (it's working)
2. Create a branch for Alex's website work
3. Let Alex make changes on the branch
4. Review the changes before merging
5. Push everything to GitHub

Using **only your `git-workflow.md`**, work through each step. Don't look back at Lessons 1-4. If your documentation is clear enough, you won't need to.

**Step 1**: Which pattern applies? What do you tell your agent?

**Step 2**: Which pattern applies? What branch name would you use?

**Step 3**: Alex works on the branch. How do you check what changed?

**Step 4**: How do you review before merging? (Hint: you learned this last lesson.)

**Step 5**: Which pattern applies?

If you got stuck, your documentation needs work. Revise it and try again. The goal is a reference you can follow under pressure without thinking.

---

## Reflection

Answer these questions:

1. **Did you need to look at earlier lessons?** If yes, your documentation needs more detail in that area.
2. **What would you add to your workflow document?** Maybe a troubleshooting section, or notes about common mistakes.
3. **How confident are you?** Rate yourself 1-5. If you're below 4, revise your documentation.

---

You started this chapter pressing Ctrl+Z and hoping. You're ending it with a system that professionals use to protect million-dollar projects. The same system your AI agent uses every time you ask it to help. Now you understand what it's doing — and why.

---

## The Bigger Picture: Seven Principles in Action

These three patterns aren't just Git habits. They're the [Seven Principles of General Agent Problem Solving](/docs/General-Agents-Foundations/seven-principles) applied to version control. You've been practicing them all chapter without labeling them.

| Git Pattern | Principle It Applies | What You Did |
| --- | --- | --- |
| **Commit Before Experiment** | Small, Reversible Decomposition | Made atomic save points so any change can be undone |
| **Branch-Test-Merge** | Constraints and Safety | Isolated risky work so it can't damage main |
| **Push for Backup** | Persisting State in Files | Saved your project outside your computer so it survives failures |
| `git status` before every action | Verification as Core Step | Checked the current state before making changes |
| Clear commit messages and PR descriptions | Observability | Made your history readable so anyone can see what happened and why |

Five of seven principles, embedded in your daily workflow. You didn't memorize them as theory — you practiced them as habits. That's the difference between knowing principles and living them.

---

## Try With AI

**Validate your workflow document:**

> "I created a personal Git workflow guide with three patterns: Commit-Before-Experiment, Branch-Test-Merge, and Push-for-Backup. [Paste your git-workflow.md]. Review it for clarity, completeness, and practicality. Could someone else follow it? What scenarios did I miss?"

**Add error recovery:**

> "My workflow covers the happy path. What happens when things go wrong? Help me add an error recovery section for: merge conflicts, accidental commits to the wrong branch, and pushing secrets to GitHub. For each, give me the symptom, the fix, and how to prevent it."

**Customize for AI development:**

> "I work with AI agents that generate code frequently. Help me extend my workflow for this: How often should I commit AI-generated code? How do I track what AI did vs what I did? What safety checks should I add? Write an 'AI development' section for my workflow."

**Build a quick reference card:**

> "Convert my workflow into a one-page cheat sheet. For the 10 most common Git operations, give me: a one-line description, the command, when to use it, and one safety tip. Format it so I can keep it at my desk."
