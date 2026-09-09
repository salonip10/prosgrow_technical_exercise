# Based on the docs at https://staging.prosgrow.ai/docs 

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

import requests

from .exceptions import (
    APIConnectionError,
    APIResponseError,
    AuthenticationError,
    RateLimitError,
)

DEFAULT_BASE_URL = "https://staging.prosgrow.ai/v1"
DEFAULT_TIMEOUT_SECONDS = 30.0


@dataclass
class PromptResult:
    content: str
    status_code: int
    latency_ms: float
    model: str


class ProsGrowClient:
    def __init__(self, api_key, base_url=DEFAULT_BASE_URL, timeout=DEFAULT_TIMEOUT_SECONDS, session=None):
        if not api_key:
            raise ValueError("api_key must not be empty")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        # allow a fake session to be passed in for tests, otherwise use a real one
        self.session = session or requests.Session()

    def send_prompt(self, model, prompt):
        """Send one prompt to `model` and return a PromptResult."""
        url = self.base_url + "/chat/completions"

        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
            "Idempotency-Key": str(uuid.uuid4()),
        }

        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }

        start_time = time.monotonic()
        try:
            response = self.session.post(url, json=body, headers=headers, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise APIConnectionError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise APIConnectionError(f"Could not connect to {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise APIConnectionError(f"Request failed: {e}")
        latency_ms = (time.monotonic() - start_time) * 1000

        # common error cases
        if response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError(
                "API key was rejected",
                status_code=response.status_code,
            )

        if response.status_code == 429:
            raise RateLimitError(
                "Got rate limited by the API",
                status_code=response.status_code,
            )

        if not response.ok:
            raise APIResponseError(
                f"API returned an error: {response.status_code} {response.text[:200]}",
                status_code=response.status_code,
            )

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise APIResponseError(f"Response didn't look like what we expected: {data}")

        return PromptResult(
            content=content,
            status_code=response.status_code,
            latency_ms=latency_ms,
            model=model,
        )
