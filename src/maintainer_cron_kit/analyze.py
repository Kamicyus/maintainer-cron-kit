from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import Digest, GitHubItem

BLOCKED_LABELS = {"blocked", "wontfix", "invalid", "duplicate"}
REVIEW_LABELS = {"review", "ready", "ready for review", "needs review"}


def build_digest(repo: str, items: list[GitHubItem], days: int, stale_days: int) -> Digest:
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=stale_days)

    open_items = [item for item in items if item.state == "open"]
    closed_items = [item for item in items if item.state == "closed"]

    needs_triage = [
        item
        for item in open_items
        if not item.labels and item.updated_at >= now - timedelta(days=days)
    ]
    waiting_review = [
        item
        for item in open_items
        if item.is_pull_request and not has_any_label(item, BLOCKED_LABELS)
    ]
    stale_threads = [
        item
        for item in open_items
        if item.updated_at < stale_cutoff and not has_any_label(item, BLOCKED_LABELS)
    ]
    recently_closed = sorted(closed_items, key=lambda item: item.updated_at, reverse=True)[:15]
    recent_activity = sorted(items, key=lambda item: item.updated_at, reverse=True)[:20]

    return Digest(
        repo=repo,
        generated_at=now,
        days=days,
        stale_days=stale_days,
        needs_triage=tuple(needs_triage),
        waiting_review=tuple(waiting_review),
        stale_threads=tuple(stale_threads),
        recently_closed=tuple(recently_closed),
        recent_activity=tuple(recent_activity),
    )


def has_any_label(item: GitHubItem, labels: set[str]) -> bool:
    normalized = {label.lower() for label in item.labels}
    return bool(normalized & labels)

