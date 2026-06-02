from __future__ import annotations

import unittest

from maintainer_cron_kit.github import item_from_api, parse_repo


class GitHubTest(unittest.TestCase):
    def test_parse_repo(self) -> None:
        self.assertEqual(parse_repo("owner/repo"), "owner/repo")
        self.assertEqual(parse_repo("https://github.com/owner/repo"), "owner/repo")
        self.assertEqual(parse_repo("https://github.com/owner/repo.git"), "owner/repo")

    def test_item_from_api_detects_pull_request(self) -> None:
        raw = {
            "number": 7,
            "title": "Fix docs",
            "state": "open",
            "html_url": "https://github.com/owner/repo/pull/7",
            "user": {"login": "dev"},
            "labels": [{"name": "docs"}],
            "created_at": "2026-06-01T10:00:00Z",
            "updated_at": "2026-06-02T10:00:00Z",
            "pull_request": {"url": "https://api.github.com/repos/owner/repo/pulls/7"},
        }

        parsed = item_from_api(raw)

        self.assertTrue(parsed.is_pull_request)
        self.assertEqual(parsed.labels, ("docs",))


if __name__ == "__main__":
    unittest.main()

