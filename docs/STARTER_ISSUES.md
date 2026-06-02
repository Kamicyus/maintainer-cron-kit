# Starter Issues

These are good first public issues after the repository is published.

## Add JSON Output

Expose `--format json` for `digest` and `release-notes`, while keeping Markdown as the default.

Acceptance criteria:

- `mck digest owner/repo --format json` prints valid JSON.
- Existing Markdown output stays unchanged.
- Unit tests cover empty and populated output.

## Add GitHub Enterprise Support

Allow maintainers to pass a custom GitHub API base URL.

Acceptance criteria:

- `GITHUB_API_URL` is documented.
- URL parsing still works for public GitHub.
- Tests cover custom API URL construction.

## Add Codex Prompt Pack

Create safe prompt templates that consume generated Markdown artifacts for authorized maintainer review.

Acceptance criteria:

- Prompts include an authorization boundary.
- Prompts ask for findings before suggestions.
- No prompt asks Codex to post or merge automatically.

