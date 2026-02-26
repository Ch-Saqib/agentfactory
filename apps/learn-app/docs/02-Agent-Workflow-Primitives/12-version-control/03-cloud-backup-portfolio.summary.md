### Core Concept
GitHub stores your Git project in the cloud — serving as both catastrophe prevention (if your computer dies, your work survives) and career portfolio (employers see your real projects at `github.com/yourname`). A backup only counts if you've tested that recovery actually works.

### Key Mental Models
- **Git vs GitHub**: Git is the local tool on your computer. GitHub is the cloud service that hosts copies. They work together but are not the same thing.
- **Backup verification**: A backup you've never tested is a backup that doesn't exist. Clone to a separate folder to prove recovery works.
- **Secrets before push**: `.gitignore` must be set up before the first push — once a secret is in Git history, deleting the file doesn't remove it.

### Critical Patterns
- Create `.gitignore` listing sensitive files (API keys, `.env`) before pushing anything to GitHub
- `git remote add origin <URL>` connects your local project to GitHub; `git push` uploads your snapshots
- `git clone <URL>` downloads a complete copy of a project — use this to test that recovery works
- Verify backup by checking GitHub's web interface after every push

### Common Mistakes
- Thinking GitHub IS Git — GitHub is a hosting service; Git is the version control tool that runs locally
- Pushing secrets to a public repository — Sarah pushed her Stripe API key without a `.gitignore`; Maya spotted it on GitHub. Deleting the file doesn't remove it from history; you must revoke the key and generate a new one immediately
- Skipping the clone test — pushing is not proof of backup; only a successful recovery test is proof

### Connections
- **Builds on**: Local commits and branches (Lessons 1-2)
- **Leads to**: Pull requests for reviewing changes before merging (Lesson 4)
