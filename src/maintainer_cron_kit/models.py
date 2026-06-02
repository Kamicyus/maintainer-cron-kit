from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class GitHubItem:
    number: int
    title: str
    state: str
    html_url: str
    author: str
    labels: tuple[str, ...]
    created_at: datetime
    updated_at: datetime
    is_pull_request: bool


@dataclass(frozen=True)
class Digest:
    repo: str
    generated_at: datetime
    days: int
    stale_days: int
    needs_triage: tuple[GitHubItem, ...]
    waiting_review: tuple[GitHubItem, ...]
    stale_threads: tuple[GitHubItem, ...]
    recently_closed: tuple[GitHubItem, ...]
    recent_activity: tuple[GitHubItem, ...]

