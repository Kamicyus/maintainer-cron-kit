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

## Output Formats

Both commands default to Markdown; `--format markdown` selects it explicitly.
Use `--format json` to emit one JSON object:

```bash
mck digest owner/repo --format json
mck release-notes owner/repo --days 30 --format json --output release-notes.json
```

Digest JSON contains `repo`, `generated_at`, `days`, `stale_days`, and arrays
named `needs_triage`, `waiting_review`, `stale_threads`, `recently_closed`, and
`recent_activity`. Empty sections are `[]`.
Release-note JSON contains `repo`, `days`, and `groups`, an object mapping
nonempty heuristic group names to arrays of closed pull requests sorted by number.
With no closed pull requests, `groups` is `{}`. Closed does not mean merged;
verify merge status before claiming a change shipped.
Items include number, title, state, URL (`html_url`), author, labels,
`created_at`, `updated_at`, and `is_pull_request`. Dates use ISO 8601 in UTC.
`--output` writes the selected format as UTF-8 and prints a write confirmation;
without it, the artifact goes to stdout.

## GitHub Enterprise Server

Set `GITHUB_API_URL` to the trusted server's API base URL, including `/api/v3`:

```bash
GITHUB_API_URL=https://github.example.com/api/v3 mck digest owner/repo
GITHUB_API_URL=https://github.example.com/api/v3 mck release-notes owner/repo --format json
```

Both commands read this environment variable at request time. Unset or empty
values use `https://api.github.com`; trailing slashes are stripped.
Use `owner/repo`, not an Enterprise web URL, as the repository argument.
Authentication uses `GITHUB_TOKEN` (or the variable selected by `--token-env`)
and is sent to the configured API host, so only use a trusted HTTPS endpoint.
In GitHub Actions, pass `${{ github.api_url }}` as `GITHUB_API_URL` in the step's
`env` mapping when targeting the workflow's GitHub instance.

## Run in GitHub Actions

Use read-only permissions unless you intentionally add a write step:

```yaml
permissions:
  contents: read
  issues: read
  pull-requests: read
```

Maintainer Cron Kit does not post issues, comments, or releases by default.

