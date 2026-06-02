from __future__ import annotations

import unittest

from maintainer_cron_kit.analyze import build_digest
from maintainer_cron_kit.render import render_digest, render_release_notes
from tests.test_analyze import item


class RenderTest(unittest.TestCase):
    def test_render_digest_contains_sections(self) -> None:
        digest = build_digest("example/repo", [item(1), item(2, pr=True)], days=7, stale_days=14)
        markdown = render_digest(digest)

        self.assertIn("# Maintainer Digest - example/repo", markdown)
        self.assertIn("## Needs Triage", markdown)
        self.assertIn("Pull Requests Waiting Review", markdown)

    def test_render_release_notes_groups_prs(self) -> None:
        markdown = render_release_notes(
            "example/repo",
            [
                item(1, title="feat: add digest filters", state="closed", pr=True),
                item(2, title="fix: handle empty labels", state="closed", pr=True),
            ],
            days=30,
        )

        self.assertIn("## Features", markdown)
        self.assertIn("## Fixes", markdown)


if __name__ == "__main__":
    unittest.main()

