from __future__ import annotations

import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from maintainer_cron_kit.github import fetch_recent_items, item_from_api, parse_repo


class GitHubTest(unittest.TestCase):
    def test_api_base_url_is_read_at_call_time(self):
        for base, expected in [
            (None, "https://api.github.com/repos/owner/repo/issues"),
            ("", "https://api.github.com/repos/owner/repo/issues"),
            ("https://github.example.com/api/v3", "https://github.example.com/api/v3/repos/owner/repo/issues"),
            ("https://github.example.com/api/v3/", "https://github.example.com/api/v3/repos/owner/repo/issues"),
        ]:
            env = {} if base is None else {"GITHUB_API_URL": base}
            with self.subTest(base=base), patch.dict("os.environ", env, clear=True), \
                    patch("urllib.request.urlopen") as urlopen:
                urlopen.return_value.__enter__.return_value.read.return_value = b"[]"
                self.assertEqual(fetch_recent_items("owner/repo", days=7, limit=25), [])
                request = urlopen.call_args.args[0]
                url = urlsplit(request.full_url)
                self.assertEqual(f"{url.scheme}://{url.netloc}{url.path}", expected)
                query = parse_qs(url.query)
                self.assertEqual(query["state"], ["all"])
                self.assertEqual(query["sort"], ["updated"])
                self.assertEqual(query["direction"], ["desc"])
                self.assertEqual(query["per_page"], ["25"])
                self.assertTrue(query["since"][0].endswith("Z"))
                self.assertEqual(urlopen.call_args.kwargs, {"timeout": 30})

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

