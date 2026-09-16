# Maintainer Cron Kit

Small, dependency-light automation helpers for open-source maintainers who need scheduled project health checks without running a server.

The kit is designed for GitHub Actions cron jobs. It can generate issue/PR triage digests, draft release notes, and run a lightweight workflow doctor from a public repository using only the GitHub API.

## Why this exists

Many open-source maintainers do not need a dashboard or a paid SaaS tool. They need a reliable scheduled job that says:

- Which issues still need triage?
- Which pull requests are waiting for review?
- Which threads are stale?
- What changed since the last release?
- Is the workflow configured safely?

Maintainer Cron Kit turns those questions into Markdown artifacts that can be uploaded by GitHub Actions, posted manually, or passed to Codex for authorized review and maintenance workflows.

## Install

```bash
python3 -m pip install maintainer-cron-kit
```

For local development from a checkout:

```bash
python3 -m pip install -e .
```

## Quick Start

Generate a digest for a public repository:

```bash
mck digest openai/codex --days 7 --output digest.md
```

Use a token for higher GitHub API limits:

```bash
GITHUB_TOKEN="$GITHUB_TOKEN" mck digest owner/repo --days 14
```

Generate release-note draft material from recently closed pull requests:

```bash
mck release-notes owner/repo --days 30 --output RELEASE_DRAFT.md
```

Markdown remains the default. Use JSON for scripts or structured processing:

```bash
mck digest owner/repo --format json
mck release-notes owner/repo --days 30 --format json --output release-notes.json
```

For GitHub Enterprise Server, set the API base URL (including `/api/v3`):

```bash
GITHUB_API_URL=https://github.example.com/api/v3 mck digest owner/repo
```

`GITHUB_API_URL` defaults to `https://api.github.com` when unset or empty.
Use `owner/repo` for Enterprise repositories; trailing slashes are accepted.
Only set this URL to a trusted API host: configured authentication is sent there.

Check workflow environment readiness:

```bash
mck doctor
```

## GitHub Actions

Copy an example workflow from `examples/workflows/` into your repository:

```yaml
name: Maintainer digest

on:
  schedule:
    - cron: "17 8 * * 1"
  workflow_dispatch:

permissions:
  contents: read
  issues: read
  pull-requests: read

jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install maintainer-cron-kit
      - run: mck digest "$GITHUB_REPOSITORY" --output maintainer-digest.md
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: maintainer-digest
          path: maintainer-digest.md
```

The default examples only read repository metadata and upload artifacts. They do not post comments, open issues, send email, or call third-party services.

## Codex and API Credit Use

This project is intentionally useful without AI. Codex can be added on top of the generated Markdown artifacts for authorized maintainer tasks:

- classify issues and pull requests;
- propose small documentation or test fixes;
- review workflow and security-sensitive changes;
- draft release notes from merged pull requests;
- summarize stale threads before maintainer review.

Start with the [read-only Codex prompt pack](docs/prompts/README.md) to review generated Markdown artifacts.

Only run automated review on repositories you own, maintain, or have explicit permission to administer.

## Security Model

- No secrets are stored in this repository.
- `GITHUB_TOKEN` is optional for public repositories and recommended for rate limits.
- Example workflows request read-only permissions by default.
- Write actions are intentionally not included in the default workflow.
- Generated Markdown can be inspected before being posted anywhere.

## More

- Usage guide: `docs/USAGE.md`
- Roadmap: `ROADMAP.md`
- Starter issues: `docs/STARTER_ISSUES.md`
- Codex for OSS notes: `docs/OPENAI_CODEX_FOR_OSS.md`

## Project Status

Alpha. The first release focuses on read-only digest generation and public-safe GitHub Actions examples.

## License

MIT.
