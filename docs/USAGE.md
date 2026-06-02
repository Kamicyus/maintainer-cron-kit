# Usage

## Generate a Digest

```bash
mck digest owner/repo --days 7 --output maintainer-digest.md
```

The digest includes:

- unlabeled open issues that need triage;
- open pull requests waiting for review;
- stale open threads;
- recently closed issues and pull requests;
- recent activity.

## Draft Release Notes

```bash
mck release-notes owner/repo --days 30 --output RELEASE_DRAFT.md
```

Release-note groups are heuristic and based on pull request titles and labels. Review the draft before publishing it.

## Run in GitHub Actions

Use read-only permissions unless you intentionally add a write step:

```yaml
permissions:
  contents: read
  issues: read
  pull-requests: read
```

Maintainer Cron Kit does not post issues, comments, or releases by default.

