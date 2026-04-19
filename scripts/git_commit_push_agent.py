import argparse
import subprocess
import sys

def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
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
    parser.add_argument(
        "--tag",
        default=None,
        help="Create and push an annotated tag for the new commit (example: v0.2.0).",
    )
    parser.add_argument(
        "--tag-message",
        default=None,
        help="Annotated tag message. Defaults to commit title.",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Create a GitHub release for the tag using GitHub CLI (gh). Requires --tag.",
    )
    parser.add_argument(
        "--release-title",
        default=None,
        help="Release title. Defaults to the tag name.",
    )
    parser.add_argument(
        "--release-notes",
        default=None,
        help="Release notes body text. If omitted, uses --generate-notes in gh release create.",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create the GitHub release as draft.",
    )
    parser.add_argument(
        "--prerelease",
        action="store_true",
        help="Mark the GitHub release as prerelease.",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Target branch or commit for release metadata (optional gh --target value).",
    )
    args = parser.parse_args()
    if args.release and not args.tag:
        parser.error("--release requires --tag.")
    return args


def ensure_tag_absent(tag: str) -> None:
    tag_check = run_git(["show-ref", "--verify", "--quiet", f"refs/tags/{tag}"])
    if tag_check.returncode == 0:
        print(f"Tag already exists locally: {tag}", file=sys.stderr)
        raise SystemExit(1)


def create_and_push_tag(tag: str, message: str, remote: str) -> None:
    tag_result = run_git(["tag", "-a", tag, "-m", message])
    if tag_result.returncode != 0:
        print(tag_result.stderr.strip() or tag_result.stdout.strip() or "git tag failed.", file=sys.stderr)
        raise SystemExit(1)

    push_tag_result = run_git(["push", remote, tag])
    if push_tag_result.returncode != 0:
        print(push_tag_result.stderr.strip() or push_tag_result.stdout.strip() or "git push tag failed.", file=sys.stderr)
        raise SystemExit(1)


def create_release(
    tag: str,
    title: str | None,
    notes: str | None,
    draft: bool,
    prerelease: bool,
    target: str | None,
) -> None:
    gh_check = run_gh(["--version"])
    if gh_check.returncode != 0:
        print(gh_check.stderr.strip() or "GitHub CLI (gh) is required for --release.", file=sys.stderr)
        raise SystemExit(1)

    args = ["release", "create", tag]
    if title:
        args.extend(["--title", title])
    if notes:
        args.extend(["--notes", notes])
    else:
        args.append("--generate-notes")
    if draft:
        args.append("--draft")
    if prerelease:
        args.append("--prerelease")
    if target:
        args.extend(["--target", target])

    release_result = run_gh(args)
    if release_result.returncode != 0:
        print(release_result.stderr.strip() or release_result.stdout.strip() or "gh release create failed.", file=sys.stderr)
        raise SystemExit(1)

    output = release_result.stdout.strip()
    if output:
        print(output)


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
        if args.tag:
            print(f"Would create and push tag: {args.tag}")
        if args.release:
            print(f"Would create GitHub release for tag: {args.tag}")
        return

    commit_result = run_git(["commit", "-m", commit_title])
    if commit_result.returncode != 0:
        print(commit_result.stderr.strip() or commit_result.stdout.strip() or "git commit failed.", file=sys.stderr)
        raise SystemExit(1)

    push_result = run_git(["push", args.remote, branch])
    if push_result.returncode != 0:
        print(push_result.stderr.strip() or push_result.stdout.strip() or "git push failed.", file=sys.stderr)
        raise SystemExit(1)

    if args.tag:
        ensure_tag_absent(args.tag)
        tag_message = args.tag_message or commit_title
        create_and_push_tag(tag=args.tag, message=tag_message, remote=args.remote)

    if args.release:
        create_release(
            tag=args.tag,
            title=args.release_title or args.tag,
            notes=args.release_notes,
            draft=args.draft,
            prerelease=args.prerelease,
            target=args.target or branch,
        )

    print(f"Committed and pushed successfully: {commit_title}")


if __name__ == "__main__":
    main()
