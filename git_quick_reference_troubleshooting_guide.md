# Git Quick Reference & Troubleshooting Guide

A concise reference for common Git commands, workflows, and errors.

---

# 1. Initialize a Repository

## Start Git in a project
```bash
git init
```
- Creates a `.git/` folder
- Enables version control in the project

---

# 2. Staging Changes

## Add files to staging
```bash
git add .
```

### Variations
```bash
git add file.txt   # specific file
git add -A         # all changes including deletions
git add -p         # interactively choose changes
```

- Staging = preparing changes for commit

---

# 3. Committing Changes

```bash
git commit -m "message"
```

- Saves a snapshot of staged changes
- `-m` adds commit message inline

---

# 4. Connect to GitHub Remote

```bash
git remote add origin https://github.com/user/repo.git
```

- `origin` = name for remote repo
- Links local repo to GitHub

---

# 5. Rename Branch to main

```bash
git branch -M main
```

- `-M` forces rename
- Standardizes default branch name

---

# 6. Push to GitHub

```bash
git push -u origin main
```

### Flags
- `-u` sets upstream tracking

After this:
```bash
git push
git pull
```
work without specifying branch

---

# 7. Clone a Repository

```bash
git clone https://github.com/user/repo.git
```

- Downloads repo
- Sets up remote automatically
- Best starting method for collaboration

---

# 8. Branching Workflow

## Create and switch branch
```bash
git checkout -b feature-name
```

- `-b` = create + switch

## Push branch
```bash
git push origin feature-name
```

---

# 9. Updating Code from Remote

```bash
git pull origin main
```

- Downloads + merges remote changes

Internally:
```bash
git fetch origin main
git merge origin/main
```

---

# 10. Merging Branches

```bash
git merge main
```

- Combines branches into current branch

---

# 11. Rebase (Cleaner History)

```bash
git rebase main
```

- Moves your commits on top of latest main
- Produces linear history

---

# 12. Common Errors & Fixes

---

## ❌ Error: "Updates were rejected because tip of your branch is behind"

### Meaning:
Remote has commits you don't have locally

### Fix:
```bash
git pull origin main
git push origin main
```

Or cleaner:
```bash
git pull --rebase origin main
git push
```

---

## ❌ Error: "refusing to merge unrelated histories"

### Meaning:
Local and remote repos have completely different histories

### Fix:
```bash
git pull origin main --allow-unrelated-histories
```

Then resolve conflicts and:
```bash
git push
```

---

## ⚠️ Merge Conflicts

### Example:
```
<<<<<<< HEAD
your code
=======
their code
>>>>>>> branch
```

### Fix steps:
1. Manually edit file
2. Remove conflict markers
3. Stage changes
```bash
git add .
```
4. Commit
```bash
git commit
```

---

## ⚠️ Force Push (Dangerous)

```bash
git push --force
```

### What it does:
- Overwrites remote history

### Use only when:
- Working alone
- You understand consequences

---

# 13. Git Mental Model

## Three states:

### 1. Working Directory
Your actual files

### 2. Staging Area
Prepared changes (`git add`)

### 3. Repository
Committed history (`git commit`)

---

# 14. Core Workflow Summary

```bash
git add .
git commit -m "message"
git pull origin main
git push origin main
```

---

# 15. Collaboration Best Practice

- Always use branches for features
- Pull before pushing
- Use pull requests for merging
- Avoid force push on shared repos

---

# 16. Key Idea Summary

- Git tracks snapshots, not files
- GitHub stores shared remote history
- Branches = parallel work streams
- Pull requests = controlled merging system

