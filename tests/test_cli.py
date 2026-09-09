"""Tests for the CLI: env var wiring, missing-config handling, no credential leakage."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from prosgrow_validator import cli
from prosgrow_validator.client import PromptResult


class CliMissingConfigTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key_is_reported_and_does_not_crash(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = cli.main(["hello"])

        self.assertEqual(exit_code, 1)
        self.assertIn("PROSGROW_API_KEY", stderr.getvalue())

    @patch.dict("os.environ", {"PROSGROW_API_KEY": "secret-key"}, clear=True)
    def test_missing_model_is_reported(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = cli.main(["hello"])

        self.assertEqual(exit_code, 1)
        self.assertIn("--model", stderr.getvalue())


class CliSuccessTests(unittest.TestCase):
    @patch.dict("os.environ", {"PROSGROW_API_KEY": "super-secret-key"}, clear=True)
    @patch("prosgrow_validator.cli.ProsGrowClient")
    def test_output_never_contains_the_api_key(self, mock_client_cls) -> None:
        mock_client_cls.return_value.send_prompt.return_value = PromptResult(
            content="42", status_code=200, latency_ms=12.3, model="test-model"
        )

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = cli.main(["What is the answer?", "--model", "test-model"])

        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("Status:   200", output)
        self.assertIn("Latency:", output)
        self.assertIn("42", output)
        self.assertNotIn("super-secret-key", output)


if __name__ == "__main__":
    unittest.main()
