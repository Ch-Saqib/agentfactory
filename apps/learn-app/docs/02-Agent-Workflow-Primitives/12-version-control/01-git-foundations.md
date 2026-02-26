---
sidebar_position: 1
chapter: 12
lesson: 1
title: "Git Foundations"
description: "Understand Git as a snapshot system for your entire project — learn how your agent tracks changes, stages files, and undoes mistakes"
duration_minutes: 55
keywords: [git, version control, commit, staging, undo, restore, diff]

# HIDDEN SKILLS METADATA
skills:
  - name: "Understand Git as Snapshot System"
    proficiency_level: "A1"
    category: "Conceptual"
    bloom_level: "Understand"
    digcomp_area: "Information Literacy"
    measurable_at_this_level: "Student can explain commits as snapshots of an entire project folder"

  - name: "Initialize Git Repository"
    proficiency_level: "A1"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Digital Competence"
    measurable_at_this_level: "Student can execute git init and observe .git directory creation"

  - name: "Stage and Commit Files"
    proficiency_level: "A1"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Digital Competence"
    measurable_at_this_level: "Student can stage specific files and create commits with clear messages"

  - name: "View Changes with git diff"
    proficiency_level: "A1"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Digital Competence"
    measurable_at_this_level: "Student can compare current file state against last commit"

  - name: "Undo Changes Safely"
    proficiency_level: "A1"
    category: "Technical"
    bloom_level: "Apply"
    digcomp_area: "Digital Competence"
    measurable_at_this_level: "Student can restore files, unstage changes, and choose correct undo for each scenario"

learning_objectives:
  - objective: "Explain what a Git commit represents and why it matters"
    proficiency_level: "A1"
    bloom_level: "Understand"
    assessment_method: "Student describes a commit as a snapshot of the entire project at a point in time"

  - objective: "Create a Git repository and make meaningful commits"
    proficiency_level: "A1"
    bloom_level: "Apply"
    assessment_method: "Student executes init, add, commit sequence and verifies with git log"

  - objective: "Use the staging area to control what goes into each commit"
    proficiency_level: "A1"
    bloom_level: "Apply"
    assessment_method: "Student stages specific files while leaving others unstaged"

  - objective: "View changes with git diff and interpret the output"
    proficiency_level: "A1"
    bloom_level: "Apply"
    assessment_method: "Student reads diff output and identifies additions and deletions"

  - objective: "Choose the correct undo command for three different scenarios"
    proficiency_level: "A1"
    bloom_level: "Understand"
    assessment_method: "Student matches restore/reset/revert to the correct situation"

cognitive_load:
  new_concepts: 6
  concepts_list:
    - "Git repository (project folder with history tracking)"
    - "Commits as snapshots (photographing your entire project)"
    - "Staging area (choosing what goes in each snapshot)"
    - "git status (your agent's view of what changed)"
    - "git diff (comparing two snapshots side by side)"
    - "Three levels of undo (unstaged, staged, committed)"
  assessment: "6 concepts (at A1 limit) — merged from two lessons"
teaching_guide:
  lesson_type: "core"
  session_group: 1
  session_title: "Git Foundations"
  key_points:
    - "Git photographs your entire project, not individual files — every commit captures the full state"
    - "The staging area is like packing a suitcase — you choose what goes in before closing it"
    - "Three undo levels cover every mistake: restore for unstaged, restore --staged for staged, reset for committed"
    - "Commands are framed as 'what your agent does' — reader learns to recognize, not memorize"
  misconceptions:
    - "Students think git add saves the file — it only stages it; commit creates the permanent snapshot"
    - "Students fear git restore will delete their file — it only reverts content to the last committed version"
    - "Students confuse git reset HEAD (unstage) with git reset --hard (destroy) — the --hard flag is dangerous"
    - "Students think they need to memorize commands — the agent handles syntax; they need to understand concepts"
  discussion_prompts:
    - "If Git photographs your entire project every time you commit, what happens if you never take a photo?"
    - "Why does Git make you choose which files to include in each snapshot instead of automatically saving everything?"
  teaching_tips:
    - "The Ctrl+Z hook is relatable for everyone — let students feel the gap between single-file undo and project-wide undo"
    - "The deliberate mistake exercise is the lesson's emotional peak — let students break something and feel the relief of recovery"
    - "Frame every command as 'what your agent does' — students learn to direct, not memorize"
  assessment_quick_check:
    - "What is the difference between saving a file and committing in Git?"
    - "You modified a file and want to throw away your changes. What do you tell your agent?"
    - "You staged the wrong file. How do you unstage it without losing the file?"

generated_by: "content-implementer v2.0.0"
created: "2025-01-17"
last_modified: "2026-02-26"
version: "2.0.0"
---

# Git Foundations

Open a Google Doc. Type a paragraph. Delete it. Press Ctrl+Z. It comes back.

Now open a project folder with 47 files. Ask Claude Code to reorganize them. It moves, renames, and rewrites 12 files. The result is wrong. Press Ctrl+Z. Nothing happens. There is no undo for a project folder.

**Unless you have Git.**

> **"Ctrl+Z works for one file. Git works for your entire life's work."**

In 1998, someone at Pixar accidentally ran a delete command on the Toy Story 2 production files. The animation studio lost 90% of two years of work in seconds. Their backup system had silently failed weeks earlier. The entire movie was saved only because one employee, Galyn Susman, had a copy on her home computer — she'd been working remotely while caring for her newborn. Without that stroke of luck, one of the most beloved animated films ever made would have been lost forever. ([Source](https://thenextweb.com/news/how-pixars-toy-story-2-was-deleted-twice-once-by-technology-and-again-for-its-own-good))

Version control exists because of disasters like this.

---

## Before You Start

You need three things before following along: a GitHub account, Git installed, and a one-time Git configuration. If you already have all three, skip to Sarah's Problem.

**Git** and **GitHub** are not the same thing. Git is a tool that runs on your computer and tracks changes to your files. GitHub is a website that stores copies of your Git projects in the cloud — if your laptop breaks, your work survives on GitHub. Git works without GitHub. GitHub doesn't work without Git. You'll use Git locally in Lessons 1-2, then connect it to GitHub as your backup and portfolio in Lesson 3.

### 1. Create a GitHub Account

You'll use this in [Lesson 3](./03-cloud-backup-portfolio.md), but create it now — you'll need the email address in step 3 below.

1. Visit **github.com** and click "Sign up"
2. Choose a username carefully — this becomes your public portfolio URL: `github.com/yourname`
3. Complete email verification

### 2. Install Git

Open your terminal and run:

```bash
git --version
```

If you see something like `git version 2.39.0` — skip to step 3.

<details>
<summary><strong>Git not installed? Click here for installation instructions</strong></summary>

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

### 3. Tell Git Who You Are

Git labels every commit with your name and email. Use the same email you registered on GitHub — this links your commits to your GitHub profile.

```bash
git config --global user.name "Your Name"
git config --global user.email "your.github.email@example.com"
```

This isn't creating an account. It's a label that appears in your commit history. You only run this once.

---

## Sarah's Problem

Sarah is organizing a community fundraiser. She has a folder with budget spreadsheets, flyer designs, and a volunteer list. Last Tuesday she spent two hours updating the budget. Then she tried a new layout and accidentally saved over the old version.

The old budget is gone. No undo. No backup. Two hours of work, lost.

"I wish I could go back to yesterday's version," she says.

Git solves exactly this problem.

---

## The Concept: Snapshots, Not Files

You've used Track Changes in Word or Google Docs. You can see who changed what and when. Git is Track Changes for your entire project folder, not just one document. Every change, every file, with the ability to rewind to any moment in history.

Each snapshot is called a **commit** (a photograph of your entire project at one moment in time). You decide when to take each photo and what to include.

---

## Watch Your Agent Do It

Let's create Sarah's fundraiser project and watch what happens when we tell Claude Code to protect it.

**What you tell your agent**: "Create a new folder called fundraiser-project with a budget file and a volunteer list. Then set up version control."

**What the agent does**:

```bash
mkdir fundraiser-project
cd fundraiser-project
echo "Budget: $500 for venue, $200 for food" > budget.txt
echo "Volunteers: Sarah, Maya, Jordan" > volunteers.txt
git init
```

**What this means**: `git init` creates a hidden `.git` folder inside your project. This folder is Git's brain — it stores your entire project history. Delete `.git` and you lose all your snapshots. Keep it safe.

You can see it yourself:

```bash
ls -la
```

The `.git` directory appears in the listing. Everything Git knows about your project lives there.

---

## What Your Agent Sees

After creating those files, your agent checks what changed:

**What you tell your agent**: "What's the current state of my project?"

**What the agent does**:

```bash
git status
```

**What you see**:

```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        budget.txt
        volunteers.txt
```

Git sees two files it doesn't know about yet. "Untracked" means Git noticed them but hasn't started protecting them. Think of it like a hotel guest who walked in but hasn't checked in yet.

---

## The Staging Area: Packing Your Suitcase

Your agent doesn't photograph everything at once. You choose what goes in each snapshot. This in-between step is called the **staging area**.

Think of it like packing a suitcase. You lay out everything on the bed (your working directory), then decide what goes in the suitcase (staging area), then close the suitcase (commit).

**What you tell your agent**: "Prepare the budget file for saving."

**What the agent does**:

```bash
git add budget.txt
git status
```

**What you see**:

```
Changes to be committed:
    new file:   budget.txt

Untracked files:
    volunteers.txt
```

`budget.txt` moved from "untracked" to "ready to commit" (shown in green). `volunteers.txt` is still waiting. You control what goes in each snapshot.

**Why not add everything?** Sometimes you have personal notes, temporary files, or half-finished work you don't want in the snapshot. The staging area gives you control.

Let's stage everything and take our first snapshot:

```bash
git add volunteers.txt
git commit -m "Initial fundraiser files: budget and volunteer list"
```

**What happened**: Git took a photograph of your entire project. Both files are protected. The message describes what this snapshot contains.

Verify it:

```bash
git log
```

You see your commit with a unique ID, your name, the date, and the message. This is your first restore point.

---

## When Things Go Wrong

Sarah edits the budget. She accidentally deletes the food line and types nonsense over the venue costs.

Let's simulate this. Make a bad edit:

**What you tell your agent**: "Replace the budget contents with this broken version."

**What the agent does**:

```bash
echo "Budget: XXXXX broken data" > budget.txt
```

Sarah panics. The file is ruined. But she committed earlier. Git has her back.

---

## Seeing What Changed

Before undoing anything, look at what changed.

**What you tell your agent**: "Show me what's different from the last snapshot."

**What the agent does**:

```bash
git diff budget.txt
```

**What you see**:

```diff
--- a/budget.txt
+++ b/budget.txt
@@ -1 +1 @@
-Budget: $500 for venue, $200 for food
+Budget: XXXXX broken data
```

The `-` line shows what was there before. The `+` line shows what's there now. Red means removed. Green means added. This is like comparing two photographs side by side.

---

## Three Levels of Undo

Here's the decision tree for what to tell your agent. Every mistake falls into one of three categories.

### Scenario 1: You edited a file but haven't staged it yet

Sarah just made a bad edit. She hasn't run `git add`. The fix is simple.

**What you tell your agent**: "Throw away my changes to budget.txt. Go back to the last saved version."

**What the agent does**:

```bash
git restore budget.txt
```

Check the file:

```bash
cat budget.txt
```

The original budget is back. The bad edit is gone. The file still exists — Git just rewound it to the last committed version.

### Scenario 2: You staged the wrong file

You accidentally told Git to include a file you didn't want in the next snapshot.

**What you tell your agent**: "I staged the wrong file. Remove it from the staging area but keep the file."

**What the agent does**:

```bash
git restore --staged budget.txt
```

The file leaves the staging area. It goes back to "modified" or "untracked." Nothing is deleted. The file is exactly as you left it.

### Scenario 3: You already committed the mistake

You took a snapshot that includes bad changes. You need to undo the whole commit.

**What you tell your agent**: "Undo my last commit but keep the files so I can fix them."

**What the agent does**:

```bash
git reset HEAD~1
```

The commit disappears from history. Your files stay in the working directory. You can fix them and commit again.

:::caution

`git reset --hard HEAD~1` deletes the commit **and** throws away all file changes. This is the nuclear option. Only use it when you're certain you want to erase everything.

:::

### Quick Reference: Which Undo Do I Need?

| Situation | What to tell your agent | What it runs |
| --- | --- | --- |
| Bad edit, not staged | "Throw away my changes to this file" | `git restore <file>` |
| Staged the wrong file | "Unstage this file" | `git restore --staged <file>` |
| Bad commit, keep files | "Undo my last commit" | `git reset HEAD~1` |
| Bad commit, erase everything | "Erase my last commit completely" | `git reset --hard HEAD~1` |

---

Your project is safe on your computer. But what if you want to try two completely different approaches at once? What if Sarah wants a formal flyer *and* a casual flyer, and she wants to work on both without losing either?

That's what branches solve — and that's the next lesson.

---

## Try With AI

**Understand the snapshot concept:**

> "I just learned that Git commits are snapshots of my entire project folder, not just individual files. Explain how this is different from saving a single file. Use a real-world analogy that doesn't involve video games."

**Explore the staging area:**

> "Why does Git make me choose which files to include in each commit? Why not just save everything automatically? Give me three real scenarios where selective staging is useful."

**Break something on purpose:**

> "Help me practice Git recovery. Create a small project with three files, then walk me through deliberately breaking one file and recovering it with git restore. Then walk me through staging the wrong file and unstaging it. I want to feel the panic and the relief so I'm not scared when it happens for real."

**Write better commit messages:**

> "Here are five bad commit messages: 'update', 'fix stuff', 'changes', 'WIP', 'asdf'. For each one, rewrite it as a clear message that explains WHY the change was made, not just WHAT changed. Then give me a template I can follow: what should the first line say? When should I add more detail?"
