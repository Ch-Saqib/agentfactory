### Core Concept
Branches create parallel versions of your entire project that can't interfere with each other. You test ideas on a branch, and if they work you merge them into main. If they fail, you delete the branch. Main stays untouched either way.

### Key Mental Models
- **Branches as photocopies**: Creating a branch is like photocopying your whole project folder. You edit the copy freely — the original is untouched until you choose to merge.
- **Branch vs commit decision**: If you're thinking "this might go wrong," create a branch. If you're confident the change is small and correct, commit directly.
- **Create-test-merge-delete cycle**: The full workflow is: create a branch, make changes, test them, merge the winner into main, delete all branches. Always clean up.

### Critical Patterns
- `git branch <name>` creates a new branch; `git switch <name>` moves to it
- Files created on a branch disappear when you switch back to main — this is isolation working correctly
- `git merge <branch>` brings branch work into main; "Fast-forward" means main hadn't changed since branching, so Git just moves the pointer forward
- `git branch -d <branch>` cleans up afterward — deletes the branch name, not the merged commits
- Use descriptive branch names with prefixes: `feature/`, `experiment/`, `bugfix/` — names like `branch1` tell you nothing in a week

### Common Mistakes
- Thinking a branch copies all your files — it only creates a lightweight pointer to the current commit
- Panicking when files disappear after switching branches — they're safe on their branch, not deleted
- Forgetting to clean up branches after merging — old branches clutter the project

### Connections
- **Builds on**: Commits and snapshots (Lesson 1)
- **Leads to**: Pushing branches to GitHub for cloud backup (Lesson 3)
