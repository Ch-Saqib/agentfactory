### Core Concept
Pull requests add a forced pause between "I made changes" and "changes are live." They're an "are you sure?" dialog for your entire project — you review what changed before merging into main. This lesson also names the three patterns you've been following all chapter, turning instinct into repeatable habits.

### Key Mental Models
- **Writing vs proofreading**: Commits save your work (writing). Pull requests force you to evaluate it before merging (proofreading). Skipping review is like submitting a paper you never re-read.
- **Diff as evidence**: The diff shows exactly what changed — red lines removed, green lines added. If you can't read and understand every change, don't merge.
- **AI transparency as strength**: Noting which parts AI helped with in your PR description is professional practice, not a confession. It shows ownership and builds trust.
- **Three patterns, not commands**: Professionals don't memorize Git commands. They follow three patterns — Commit-Before-Experiment, Branch-Test-Merge, Push-for-Backup — and let the agent handle syntax.

### Critical Patterns
- Push a feature branch to GitHub, then create a PR comparing it to main
- Every PR description answers three questions: what changed, how it was tested, what role AI played
- Review the diff before merging: check intent match, unexpected changes, and understanding
- After merging on GitHub, run `git pull` locally and delete the merged branch
- **Pattern 1 — Commit Before Experimenting**: Always snapshot before letting AI try anything risky
- **Pattern 2 — Branch-Test-Merge**: Isolate risky work on a branch; merge winners, delete losers
- **Pattern 3 — Push for Backup**: Push to GitHub after meaningful work, not just at end of day

### Common Mistakes
- Thinking PRs are only for teams — solo developers catch mistakes and build good habits with self-review
- Merging code you don't understand — if AI generated something unfamiliar, ask it to explain before merging
- Hiding AI assistance — transparency about AI usage is a professional strength that employers respect
- Treating patterns as theory — they map directly to the Seven Principles you've been practicing all chapter

### Connections
- **Builds on**: Branches (Lesson 2) and GitHub push (Lesson 3)
- **Leads to**: Exercises for hands-on practice and the chapter quiz
