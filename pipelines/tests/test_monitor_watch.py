"""A1 (spec seguranca-doacoes, sections 3 and 14): the monitor watched from the main repository. The newest run of the monitor's chain
check (every 15 minutes) older than 45 minutes, three of its intervals, fails the hourly job; no run at all fails it too."""
import datetime
import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("monitor_watch", Path(__file__).resolve().parents[2] / ".github" / "scripts" / "monitor_watch.py")
mw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mw)
NOW = datetime.datetime(2026, 11, 4, 12, 0, tzinfo=datetime.timezone.utc)


class MonitorWatchTest(unittest.TestCase):
    def test_a1_a_run_older_than_45_minutes_fails(self):
        self.assertTrue(mw.stale("2026-11-04T11:14:00Z", NOW))

    def test_control_a_recent_run_passes(self):
        self.assertFalse(mw.stale("2026-11-04T11:56:00Z", NOW))

    def test_no_run_at_all_fails(self):
        self.assertTrue(mw.stale(None, NOW))


if __name__ == "__main__":
    unittest.main()
