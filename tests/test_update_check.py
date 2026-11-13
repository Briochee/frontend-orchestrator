from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from urllib.error import HTTPError, URLError
from unittest.mock import patch

from frontend_design_director.cli import main
from frontend_design_director.update_check import check_for_update


class UpdateCheckTests(unittest.TestCase):
    def test_newer_github_release_is_reported(self) -> None:
        response = io.BytesIO(b'{"tag_name":"v0.2.0"}')
        with patch("frontend_design_director.update_check.urllib.request.urlopen", return_value=response) as urlopen:
            result = check_for_update("0.1.0")

        self.assertEqual(result["status"], "update_available")
        self.assertEqual(result["latest_version"], "0.2.0")
        self.assertEqual(result["source"], "github_release")
        request = urlopen.call_args.args[0]
        self.assertIn("/repos/Briochee/frontend-orchestrator/releases/latest", request.full_url)

    def test_matching_release_is_reported_as_up_to_date(self) -> None:
        response = io.BytesIO(b'{"tag_name":"v0.1.0"}')
        with patch("frontend_design_director.update_check.urllib.request.urlopen", return_value=response):
            result = check_for_update("0.1.0")

        self.assertEqual(result["status"], "up_to_date")

    def test_main_branch_version_is_used_when_no_release_exists(self) -> None:
        branch_file = io.BytesIO(b'__version__ = "0.2.0"\n')
        release_missing = HTTPError("https://api.github.com/releases/latest", 404, "Not Found", None, None)
        with patch("frontend_design_director.update_check.urllib.request.urlopen", side_effect=[release_missing, branch_file]):
            result = check_for_update("0.1.0")

        self.assertEqual(result["status"], "update_available")
        self.assertEqual(result["source"], "github_main")

    def test_unavailable_network_is_nonfatal(self) -> None:
        with patch("frontend_design_director.update_check.urllib.request.urlopen", side_effect=URLError("offline")):
            result = check_for_update("0.1.0")

        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["latest_version"])

    def test_unrecognized_version_is_not_miscompared(self) -> None:
        response = io.BytesIO(b'{"tag_name":"v0.2.0-rc.1"}')
        with patch("frontend_design_director.update_check.urllib.request.urlopen", return_value=response):
            result = check_for_update("0.1.0")

        self.assertEqual(result["status"], "unavailable")

    def test_cli_checks_by_default_and_keeps_json_stdout_parseable(self) -> None:
        result = {"status": "update_available", "current_version": "0.2.0", "latest_version": "0.3.0", "source": "github_release"}
        with tempfile.TemporaryDirectory() as temporary:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch("frontend_design_director.cli.check_for_update", return_value=result) as check, redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["init", temporary, "--json"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["phase"], "INITIALIZED")
        self.assertIn("0.2.0", stderr.getvalue())
        self.assertIn("0.3.0", stderr.getvalue())
        check.assert_called_once_with()

    def test_cli_update_check_can_be_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            stdout = io.StringIO()
            with patch("frontend_design_director.cli.check_for_update") as check, redirect_stdout(stdout):
                self.assertEqual(main(["--no-update-check", "init", temporary, "--json"]), 0)
        check.assert_not_called()

    def test_cli_version_flag_reports_the_package_version_without_network(self) -> None:
        stdout = io.StringIO()
        with patch("frontend_design_director.cli.check_for_update") as check, redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as exit_result:
                main(["--version"])

        self.assertEqual(exit_result.exception.code, 0)
        self.assertEqual(stdout.getvalue(), "frontend-director 0.2.0\n")
        check.assert_not_called()


if __name__ == "__main__":
    unittest.main()
