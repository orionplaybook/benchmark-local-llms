"""Chart.js is downloaded on first use (pinned version, SHA-256 checked), never committed.
Run from benchmark-local-llms/:  python3 -m unittest discover -s tests"""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from benchlm import vendor  # noqa: E402

GOOD = b"!function(){/* chart */}();"


class ChartjsDownload(unittest.TestCase):
    def setUp(self):
        vendor._failed = False
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "vendor" / "chart.umd.min.js"
        self.sha = mock.patch.object(vendor, "CHARTJS_SHA256", hashlib.sha256(GOOD).hexdigest())
        self.sha.start()

    def tearDown(self):
        self.sha.stop()
        self.tmp.cleanup()
        vendor._failed = False

    def test_downloads_once_and_checks_the_hash(self):
        with mock.patch.object(vendor.http, "get_bytes", return_value=GOOD) as get:
            self.assertTrue(vendor.ensure_chartjs(quiet=True, path=self.path))
            self.assertTrue(vendor.ensure_chartjs(quiet=True, path=self.path))
        self.assertEqual(get.call_count, 1)
        self.assertEqual(self.path.read_bytes(), GOOD)

    def test_rejects_a_file_with_the_wrong_hash(self):
        with mock.patch.object(vendor.http, "get_bytes", return_value=b"tampered"), mock.patch("builtins.print"):
            self.assertFalse(vendor.ensure_chartjs(quiet=True, path=self.path))
        self.assertFalse(self.path.exists())

    def test_replaces_a_modified_local_copy(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"old")
        with mock.patch.object(vendor.http, "get_bytes", return_value=GOOD):
            self.assertTrue(vendor.ensure_chartjs(quiet=True, path=self.path))
        self.assertEqual(self.path.read_bytes(), GOOD)

    def test_offline_tries_once_per_process_and_never_raises(self):
        with mock.patch.object(vendor.http, "get_bytes", side_effect=OSError("offline")) as get, \
                mock.patch("builtins.print"):
            self.assertFalse(vendor.ensure_chartjs(quiet=True, path=self.path))
            self.assertFalse(vendor.ensure_chartjs(quiet=True, path=self.path))
        self.assertEqual(get.call_count, 1)

    def test_a_rejected_copy_is_removed_even_when_offline(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"corrupted")
        with mock.patch.object(vendor.http, "get_bytes", side_effect=OSError("offline")), mock.patch("builtins.print"):
            self.assertFalse(vendor.ensure_chartjs(quiet=True, path=self.path))
        self.assertFalse(self.path.exists())

    def test_a_write_error_doesnt_raise_or_leave_a_temp_file(self):
        with mock.patch.object(vendor.http, "get_bytes", return_value=GOOD), \
                mock.patch.object(vendor.os, "replace", side_effect=OSError("read-only")), mock.patch("builtins.print"):
            self.assertFalse(vendor.ensure_chartjs(quiet=True, path=self.path))
        self.assertEqual(list(self.path.parent.iterdir()), [])

    def test_pinned_hash_matches_the_real_file_when_present(self):
        if not vendor.CHARTJS_PATH.exists():
            self.skipTest("Chart.js not downloaded yet")
        self.sha.stop()
        try:
            self.assertEqual(hashlib.sha256(vendor.CHARTJS_PATH.read_bytes()).hexdigest(), vendor.CHARTJS_SHA256)
        finally:
            self.sha.start()


if __name__ == "__main__":
    unittest.main()
