from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from maintainer_cron_kit.analyze import build_digest
from maintainer_cron_kit.models import GitHubItem


def item(
    number: int,
    *,
    title: str | None = None,
    labels=(),
    state="open",
    days_old=1,
    pr=False,
) -> GitHubItem:
    now = datetime.now(timezone.utc)
    return GitHubItem(
        number=number,
        title=title or f"Item {number}",
        state=state,
        html_url=f"https://github.com/example/repo/issues/{number}",
        author="octocat",
        labels=tuple(labels),
        created_at=now - timedelta(days=days_old + 1),
        updated_at=now - timedelta(days=days_old),
        is_pull_request=pr,
    )


class AnalyzeTest(unittest.TestCase):
    def test_build_digest_groups_items(self) -> None:
        items = [
            item(1),
            item(2, labels=("bug",), pr=True),
            item(3, labels=("question",), days_old=30),
            item(4, state="closed", days_old=2, pr=True),
            item(5, labels=("blocked",), days_old=40),
        ]

        digest = build_digest("example/repo", items, days=7, stale_days=14)

        self.assertEqual([i.number for i in digest.needs_triage], [1])
        self.assertEqual([i.number for i in digest.waiting_review], [2])
        self.assertEqual([i.number for i in digest.stale_threads], [3])
        self.assertEqual([i.number for i in digest.recently_closed], [4])


if __name__ == "__main__":
    unittest.main()
