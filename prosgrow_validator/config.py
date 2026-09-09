# Environment-based configuration for the ProsGrow validation tool.

from __future__ import annotations

import os

from .client import DEFAULT_BASE_URL

API_KEY_ENV_VAR = "PROSGROW_API_KEY"
BASE_URL_ENV_VAR = "PROSGROW_API_BASE_URL"
DEFAULT_MODEL_ENV_VAR = "PROSGROW_DEFAULT_MODEL"


class MissingAPIKeyError(RuntimeError):
    """Raised when PROSGROW_API_KEY is not set in the environment."""


def get_api_key() -> str:
    api_key = os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        raise MissingAPIKeyError(
            f"{API_KEY_ENV_VAR} is not set."
        )
    return api_key


def get_base_url() -> str:
    return os.environ.get(BASE_URL_ENV_VAR, DEFAULT_BASE_URL)


def get_default_model() -> str | None:
    return os.environ.get(DEFAULT_MODEL_ENV_VAR)
