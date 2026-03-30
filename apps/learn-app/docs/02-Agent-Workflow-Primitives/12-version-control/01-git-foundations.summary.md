### Core Concept
Git takes snapshots of your entire project folder — not individual files. Each snapshot (called a commit) captures everything at one moment in time, so you can rewind to any previous state when something goes wrong. Your AI agent already uses Git; this lesson teaches you to understand and direct what it does.

### Key Mental Models
- **Snapshots, not saves**: A commit photographs your whole project. Unlike Ctrl+Z (which works on one file), Git lets you undo changes across every file in the folder at once.
- **Staging = packing a suitcase**: You choose which files go into each snapshot before committing. This gives you control over what's protected and what's left out.
- **Three levels of undo**: Every mistake has a matching fix — restore for bad edits, restore --staged for accidental staging, reset for bad commits.

### Critical Patterns
- `git init` creates the `.git` folder — Git's brain that stores all project history
- `git add` then `git commit` is the two-step snapshot cycle: stage what you want, then photograph it
- `git diff` compares your current files against the last snapshot — red lines removed, green lines added
- `git restore <file>` instantly reverts a file to the last committed version without deleting it

### Common Mistakes
- Thinking `git add` saves a file — it only stages it; `git commit` creates the actual snapshot
- Fearing `git restore` will delete a file — it only reverts the content, the file still exists
- Confusing `git reset HEAD~1` (safe, keeps files) with `git reset --hard` (destructive, erases everything)
- Reaching for `git reset --hard` as a first instinct — Sarah lost her uncommitted volunteer list this way. Always use the smallest undo tool for the job

### Connections
- **Builds on**: Terminal basics and file operations (Chapters 8-11)
- **Leads to**: Branches for testing multiple approaches simultaneously (Lesson 2)
