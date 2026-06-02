from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .analyze import build_digest
from .github import fetch_recent_items, parse_repo
from .render import render_digest, render_release_notes


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"mck: error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mck",
        description="GitHub Actions helpers for open-source maintainer automation.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    digest = subparsers.add_parser("digest", help="Generate an issue and PR maintainer digest.")
    add_repo_args(digest)
    digest.add_argument("--stale-days", type=int, default=14, help="Open thread stale threshold.")
    digest.set_defaults(func=cmd_digest)

    notes = subparsers.add_parser("release-notes", help="Draft release notes from recently closed pull requests.")
    add_repo_args(notes)
    notes.set_defaults(func=cmd_release_notes)

    doctor = subparsers.add_parser("doctor", help="Check local or GitHub Actions environment readiness.")
    doctor.set_defaults(func=cmd_doctor)

    return parser


def add_repo_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("repo", help="Repository as owner/repo or https://github.com/owner/repo")
    parser.add_argument("--days", type=int, default=7, help="Activity window in days.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum GitHub items to fetch.")
    parser.add_argument("--output", "-o", help="Write Markdown to this file instead of stdout.")
    parser.add_argument(
        "--token-env",
        default="GITHUB_TOKEN",
        help="Environment variable containing a GitHub token.",
    )


def cmd_digest(args: argparse.Namespace) -> int:
    repo = parse_repo(args.repo)
    token = os.environ.get(args.token_env)
    items = fetch_recent_items(repo, days=args.days, limit=args.limit, token=token)
    digest = build_digest(repo, items, days=args.days, stale_days=args.stale_days)
    write_output(render_digest(digest), args.output)
    return 0


def cmd_release_notes(args: argparse.Namespace) -> int:
    repo = parse_repo(args.repo)
    token = os.environ.get(args.token_env)
    items = fetch_recent_items(repo, days=args.days, limit=args.limit, token=token)
    write_output(render_release_notes(repo, items, days=args.days), args.output)
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    lines = [
        "# Maintainer Cron Kit Doctor",
        "",
        f"- GitHub Actions: {'yes' if os.environ.get('GITHUB_ACTIONS') == 'true' else 'no'}",
        f"- GITHUB_REPOSITORY: {os.environ.get('GITHUB_REPOSITORY', 'not set')}",
        f"- GITHUB_TOKEN present: {'yes' if os.environ.get('GITHUB_TOKEN') else 'no'}",
        "",
        "Recommended workflow permissions:",
        "",
        "```yaml",
        "permissions:",
        "  contents: read",
        "  issues: read",
        "  pull-requests: read",
        "```",
        "",
        "Default commands are read-only and write Markdown to stdout or a file.",
        "",
    ]
    print("\n".join(lines))
    return 0


def write_output(markdown: str, output: str | None) -> None:
    if not output:
        print(markdown)
        return
    path = Path(output)
    path.write_text(markdown, encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    raise SystemExit(main())

