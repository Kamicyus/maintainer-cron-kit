from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from .models import GitHubItem

GITHUB_API = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")


def parse_repo(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("repository is required")
    if value.startswith("https://github.com/"):
        parsed = urllib.parse.urlparse(value)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1].removesuffix('.git')}"
    if value.count("/") == 1:
        owner, repo = value.split("/")
        if owner and repo:
            return f"{owner}/{repo.removesuffix('.git')}"
    raise ValueError("repository must be owner/repo or a GitHub repository URL")


def isoformat_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_github_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def fetch_json(url: str, token: str | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "maintainer-cron-kit/0.1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_recent_items(repo: str, days: int, limit: int = 100, token: str | None = None) -> list[GitHubItem]:
    repo = parse_repo(repo)
    since = isoformat_z(datetime.now(timezone.utc) - timedelta(days=days))
    query = urllib.parse.urlencode(
        {
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "since": since,
            "per_page": min(max(limit, 1), 100),
        }
    )
    data = fetch_json(f"{GITHUB_API}/repos/{repo}/issues?{query}", token=token)
    return [item_from_api(raw) for raw in data[:limit]]


def item_from_api(raw: dict[str, Any]) -> GitHubItem:
    labels = tuple(sorted(label.get("name", "") for label in raw.get("labels", []) if label.get("name")))
    user = raw.get("user") or {}
    return GitHubItem(
        number=int(raw["number"]),
        title=str(raw.get("title") or "").strip(),
        state=str(raw.get("state") or "unknown"),
        html_url=str(raw.get("html_url") or ""),
        author=str(user.get("login") or "unknown"),
        labels=labels,
        created_at=parse_github_datetime(raw["created_at"]),
        updated_at=parse_github_datetime(raw["updated_at"]),
        is_pull_request="pull_request" in raw,
    )

