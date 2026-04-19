import argparse
import subprocess
import sys

COAUTHOR_TRAILER = "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def ensure_clean_message(message: str) -> str:
    cleaned = " ".join(message.strip().split())
    if not cleaned:
        raise ValueError("Commit description must not be empty.")
    return cleaned


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Commit and push changes with standardized message format.",
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["feat", "fix"],
        help="Commit type prefix.",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Commit description (after the prefix).",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Git remote name (default: origin).",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Branch name. If omitted, uses current branch.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Stage all changes with git add -A before commit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print actions without committing/pushing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    description = ensure_clean_message(args.description)
    commit_title = f"[{args.type}]{description}"

    branch = args.branch
    if not branch:
        branch_result = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        if branch_result.returncode != 0:
            print(branch_result.stderr.strip() or "Failed to resolve current branch.", file=sys.stderr)
            raise SystemExit(1)
        branch = branch_result.stdout.strip()

    if args.all:
        add_result = run_git(["add", "-A"])
        if add_result.returncode != 0:
            print(add_result.stderr.strip() or "git add -A failed.", file=sys.stderr)
            raise SystemExit(1)

    staged_check = run_git(["diff", "--cached", "--quiet"])
    if staged_check.returncode == 0:
        print("No staged changes found. Stage files first or use --all.", file=sys.stderr)
        raise SystemExit(1)

    if args.dry_run:
        print(f"Dry run OK. Commit title: {commit_title}")
        print(f"Would push to: {args.remote}/{branch}")
        return

    commit_result = run_git(["commit", "-m", commit_title, "-m", COAUTHOR_TRAILER])
    if commit_result.returncode != 0:
        print(commit_result.stderr.strip() or commit_result.stdout.strip() or "git commit failed.", file=sys.stderr)
        raise SystemExit(1)

    push_result = run_git(["push", args.remote, branch])
    if push_result.returncode != 0:
        print(push_result.stderr.strip() or push_result.stdout.strip() or "git push failed.", file=sys.stderr)
        raise SystemExit(1)

    print(f"Committed and pushed successfully: {commit_title}")


if __name__ == "__main__":
    main()
