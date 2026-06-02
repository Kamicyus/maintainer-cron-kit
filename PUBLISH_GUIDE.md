# Publish Guide

This repository is prepared for a clean first public release.

## 1. Create the GitHub repository

Recommended repository name:

```text
maintainer-cron-kit
```

Recommended description:

```text
Read-only GitHub Actions helpers for OSS maintainer triage, release notes, and project health checks.
```

Use MIT license and keep the repository public.

## 2. Push from local checkout

After reviewing the files:

```bash
cd /Users/kamer/Agentlarım/projeler/maintainer-cron-kit
gh repo create Kamicyus/maintainer-cron-kit --public --source . --remote origin --push --description "Read-only GitHub Actions helpers for OSS maintainer triage, release notes, and project health checks."
git tag v0.1.0
git push origin v0.1.0
```

## 3. Create starter issues

Use `docs/STARTER_ISSUES.md` to create 2-3 public issues after publishing:

- Add JSON Output
- Add GitHub Enterprise Support
- Add Codex Prompt Pack

## 4. Fill the OpenAI form

Repository URL:

```text
https://github.com/Kamicyus/maintainer-cron-kit
```

Use the copy in `docs/OPENAI_CODEX_FOR_OSS.md`.

