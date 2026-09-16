from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from maintainer_cron_kit.cli import main
from tests.test_analyze import item


NOW = datetime(2026, 1, 20, 12, 0, tzinfo=timezone.utc)


def sample_items():
    return [
        replace(item(number, title=title, state=state, labels=labels, pr=pr),
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc), updated_at=NOW)
        for number, title, state, labels, pr in [
            (1, 'Question "quoted" — café', 'open', (), False),
            (2, 'feat: add export', 'closed', ('feature',), True),
            (3, 'fix: empty input', 'closed', ('bug',), True),
            (4, 'Open PR', 'open', ('review',), True),
            (5, 'Closed issue', 'closed', (), False),
        ]
    ]


class CliTest(unittest.TestCase):
    def run_cli(self, command, items, *args):
        output = io.StringIO()
        with patch('maintainer_cron_kit.cli.fetch_recent_items', return_value=items), \
                patch('maintainer_cron_kit.analyze.datetime') as clock, \
                patch('urllib.request.urlopen', side_effect=AssertionError('Network forbidden')), \
                redirect_stdout(output):
            clock.now.return_value = NOW
            code = main([command, 'example/repo', *args])
        self.assertEqual(code, 0)
        return output.getvalue()

    def test_markdown_matches_pre_change_snapshots(self):
        for command in ('digest', 'release-notes'):
            for name, items in (('empty', []), ('full', sample_items())):
                expected = (Path(__file__).parent / 'fixtures' / f'{command}-{name}.md').read_text(encoding='utf-8')
                for flags in ((), ('--format', 'markdown')):
                    with self.subTest(command=command, data=name, flags=flags):
                        self.assertEqual(self.run_cli(command, items, *flags), expected + '\n')
                with TemporaryDirectory() as directory:
                    target = Path(directory) / 'output.md'
                    self.run_cli(command, items, '--output', str(target))
                    self.assertEqual(target.read_bytes(), expected.encode())

    def test_digest_json_empty_and_full(self):
        for items in ([], sample_items()):
            with self.subTest(empty=not items):
                data = json.loads(self.run_cli('digest', items, '--format', 'json'))
                self.assertEqual(set(data), {'repo', 'generated_at', 'days', 'stale_days',
                    'needs_triage', 'waiting_review', 'stale_threads', 'recently_closed', 'recent_activity'})
                self.assertEqual(data['repo'], 'example/repo')
                self.assertEqual(data['generated_at'], '2026-01-20T12:00:00Z')
                self.assertEqual((data['days'], data['stale_days']), (7, 14))
                for key, numbers in [('needs_triage', [1]), ('waiting_review', [4]),
                                     ('stale_threads', []), ('recently_closed', [2, 3, 5]),
                                     ('recent_activity', [1, 2, 3, 4, 5])]:
                    self.assertEqual([entry['number'] for entry in data[key]], numbers if items else [])
                if items:
                    self.assertEqual(data['needs_triage'][0], {
                        'number': 1, 'title': 'Question "quoted" — café', 'state': 'open',
                        'html_url': 'https://github.com/example/repo/issues/1', 'author': 'octocat',
                        'labels': [], 'created_at': '2026-01-01T00:00:00Z',
                        'updated_at': '2026-01-20T12:00:00Z', 'is_pull_request': False,
                    })

    def test_release_notes_json_empty_and_full(self):
        for items in ([], [replace(sample_items()[1], number=6), *reversed(sample_items())]):
            with self.subTest(empty=not items):
                data = json.loads(self.run_cli('release-notes', items, '--format', 'json', '--days', '30'))
                self.assertEqual(set(data), {'repo', 'days', 'groups'})
                self.assertEqual((data['repo'], data['days']), ('example/repo', 30))
                self.assertEqual({key: [entry['number'] for entry in entries]
                                  for key, entries in data['groups'].items()},
                                 {'Features': [2, 6], 'Fixes': [3]} if items else {})

    def test_json_file_output(self):
        for command in ('digest', 'release-notes'):
            with self.subTest(command=command), TemporaryDirectory() as directory:
                target = Path(directory) / 'output.json'
                expected = json.loads(self.run_cli(command, sample_items(), '--format', 'json'))
                output = self.run_cli(command, sample_items(), '--format', 'json', '-o', str(target))
                self.assertEqual(json.loads(target.read_text(encoding='utf-8')), expected)
                self.assertEqual(output, f'wrote {target}\n')

    def test_invalid_format_rejected_before_fetch(self):
        for command in ('digest', 'release-notes'):
            with self.subTest(command=command), \
                    patch('maintainer_cron_kit.cli.fetch_recent_items') as fetch, \
                    patch('sys.stderr', new_callable=io.StringIO), \
                    self.assertRaises(SystemExit) as error:
                main([command, 'example/repo', '--format', 'xml'])
            self.assertEqual(error.exception.code, 2)
            fetch.assert_not_called()
