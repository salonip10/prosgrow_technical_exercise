"""Tests for ProsGrowClient: success path, error handling, and latency/status capture."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

import requests

from prosgrow_validator.client import ProsGrowClient
from prosgrow_validator.exceptions import (
    APIConnectionError,
    APIResponseError,
    AuthenticationError,
    RateLimitError,
)


def make_response(status_code: int, json_data: dict | None = None, ok: bool = True, text: str = ""):
    response = MagicMock()
    response.status_code = status_code
    response.ok = ok
    response.text = text
    response.json.return_value = json_data or {}
    return response


class ProsGrowClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = MagicMock()
        self.client = ProsGrowClient(api_key="test-key", session=self.session)

    def test_send_prompt_success(self) -> None:
        self.session.post.return_value = make_response(
            200, json_data={"choices": [{"message": {"content": "hello"}}]}
        )

        result = self.client.send_prompt(model="test-model", prompt="hi")

        self.assertEqual(result.content, "hello")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.model, "test-model")
        self.assertGreaterEqual(result.latency_ms, 0)

    def test_send_prompt_sets_idempotency_key_header(self) -> None:
        self.session.post.return_value = make_response(
            200, json_data={"choices": [{"message": {"content": "hello"}}]}
        )

        self.client.send_prompt(model="test-model", prompt="hi")

        _, kwargs = self.session.post.call_args
        self.assertIn("Idempotency-Key", kwargs["headers"])
        self.assertTrue(kwargs["headers"]["Idempotency-Key"])

    def test_authentication_error(self) -> None:
        self.session.post.return_value = make_response(401, ok=False, text="unauthorized")

        with self.assertRaises(AuthenticationError) as ctx:
            self.client.send_prompt(model="test-model", prompt="hi")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_rate_limit_error(self) -> None:
        self.session.post.return_value = make_response(429, ok=False, text="too many requests")

        with self.assertRaises(RateLimitError) as ctx:
            self.client.send_prompt(model="test-model", prompt="hi")
        self.assertEqual(ctx.exception.status_code, 429)

    def test_generic_api_error(self) -> None:
        self.session.post.return_value = make_response(500, ok=False, text="server error")

        with self.assertRaises(APIResponseError) as ctx:
            self.client.send_prompt(model="test-model", prompt="hi")
        self.assertEqual(ctx.exception.status_code, 500)

    def test_connection_error(self) -> None:
        self.session.post.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(APIConnectionError):
            self.client.send_prompt(model="test-model", prompt="hi")

    def test_timeout_error(self) -> None:
        self.session.post.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(APIConnectionError):
            self.client.send_prompt(model="test-model", prompt="hi")

    def test_malformed_response_shape(self) -> None:
        self.session.post.return_value = make_response(200, json_data={"unexpected": "shape"})

        with self.assertRaises(APIResponseError):
            self.client.send_prompt(model="test-model", prompt="hi")

    def test_api_key_never_appears_in_request_body(self) -> None:
        self.session.post.return_value = make_response(
            200, json_data={"choices": [{"message": {"content": "ok"}}]}
        )

        self.client.send_prompt(model="test-model", prompt="hi")

        _, kwargs = self.session.post.call_args
        self.assertIn("Authorization", kwargs["headers"])
        self.assertNotIn("test-key", str(kwargs["json"]))


if __name__ == "__main__":
    unittest.main()
