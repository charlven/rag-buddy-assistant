---
name: git-commit-push
description: "Commit and push repository changes with fixed prefixes, with optional tag and GitHub release creation."
user-invocable: true
---

# Git Commit Push + Release Skill

Use this skill whenever the task is to commit/push code, and optionally publish a version tag and release.

## Required commit title format

- `[feat]your description`
- `[fix]your description`

No extra prefixes. No alternate styles.

## Supported automation

- Commit + push
- Commit + push + annotated tag
- Commit + push + annotated tag + GitHub release

## Workflow

1. Determine commit type (`feat` or `fix`) and description.
2. Ensure the description is short, meaningful, and not empty.
3. Run:
   - `python .\scripts\git_commit_push_agent.py --type <feat|fix> --description "<description>" --all`
4. If a branch is explicitly requested, add:
   - `--branch <branch-name>`
5. If a remote is explicitly requested, add:
   - `--remote <remote-name>`
6. If a tag is required, add:
   - `--tag <tag-name>`
   - optional `--tag-message "<annotated tag message>"`
7. If a GitHub release is required, add:
   - `--release`
   - optional `--release-title "<title>"`
   - optional `--release-notes "<notes>"`
   - optional `--draft`
   - optional `--prerelease`
8. If command fails, report the exact git/script error and do not claim success.

## Notes

- The script enforces the final title as `[type]description`.
- `--all` stages current changes before commit.
- `--release` requires `gh` CLI authentication and `--tag`.
