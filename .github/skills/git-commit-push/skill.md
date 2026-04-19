---
name: git-commit-push
description: "Commit and push repository changes with fixed message prefixes: [feat] or [fix]."
user-invocable: true
---

# Git Commit Push Skill

Use this skill whenever the task is to commit and push code.

## Required commit title format

- `[feat]your description`
- `[fix]your description`

No extra prefixes. No alternate styles.

## Workflow

1. Determine commit type (`feat` or `fix`) and description.
2. Ensure the description is short, meaningful, and not empty.
3. Run:
   - `python .\scripts\git_commit_push_agent.py --type <feat|fix> --description "<description>" --all`
4. If a branch is explicitly requested, add:
   - `--branch <branch-name>`
5. If a remote is explicitly requested, add:
   - `--remote <remote-name>`
6. If command fails, report the exact git/script error and do not claim success.

## Notes

- The script enforces the final title as `[type]description`.
- `--all` stages current changes before commit.
