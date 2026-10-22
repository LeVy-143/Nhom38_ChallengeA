import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch
from memory_store import load_conventions, save_convention, render_memory
from main import execute_tool


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'nested' / 'memory.json'
        self.env = patch.dict(os.environ, {'AGENT_MEMORY_FILE': str(self.path)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_update_keeps_history_but_injects_only_current(self):
        self.assertTrue(save_convention('authentication', 'JWT')['ok'])
        self.assertTrue(save_convention('authentication', 'session cookie')['updated'])
        self.assertEqual(load_conventions()['authentication']['history'][0]['value'], 'JWT')
        self.assertEqual(json.loads(render_memory()), {'authentication': 'session cookie'})

    def test_fresh_process_reads_latest_value(self):
        save_convention('authentication', 'JWT')
        command = [sys.executable, '-c', 'from memory_store import render_memory; print(render_memory())']
        first = subprocess.check_output(command, text=True)
        self.assertEqual(json.loads(first), {'authentication': 'JWT'})
        save_convention('authentication', 'session cookie')
        second = subprocess.check_output(command, text=True)
        self.assertEqual(json.loads(second), {'authentication': 'session cookie'})

    def test_identical_save_is_idempotent(self):
        save_convention('style', 'snake_case')
        before = self.path.read_bytes()
        save_convention('style', 'snake_case')
        self.assertEqual(before, self.path.read_bytes())

    def test_corruption_is_not_overwritten(self):
        self.path.parent.mkdir()
        self.path.write_text('{invalid')
        with self.assertRaises(ValueError):
            save_convention('style', 'snake_case')
        self.assertEqual(self.path.read_text(), '{invalid')

    def test_invalid_tool_arguments(self):
        for args in ('invalid', '[]', '{}', '{"key": 1, "value": "x"}'):
            self.assertFalse(execute_tool('remember_convention', args)['ok'])
        self.assertFalse(self.path.exists())

    def test_failed_atomic_replace_preserves_old_memory(self):
        save_convention('authentication', 'JWT')
        before = self.path.read_bytes()
        with patch('memory_store.os.replace', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                save_convention('authentication', 'session cookie')
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])


if __name__ == '__main__':
    unittest.main()
