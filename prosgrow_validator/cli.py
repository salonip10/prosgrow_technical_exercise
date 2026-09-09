"""Command-line interface for the ProsGrow API validation tool."""

from __future__ import annotations

import argparse
import sys

from .client import ProsGrowClient
from .config import (
    DEFAULT_MODEL_ENV_VAR,
    MissingAPIKeyError,
    get_api_key,
    get_base_url,
    get_default_model,
)
from .exceptions import (
    APIConnectionError,
    APIResponseError,
    AuthenticationError,
    RateLimitError,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="prosgrow-validator",
        description="Send a prompt to the ProsGrow API and report the response, status, and latency.",
    )
    parser.add_argument("prompt", help="Prompt text to send to the model")
    parser.add_argument(
        "--model",
        default=None,
        help=f"Model name to use (falls back to the {DEFAULT_MODEL_ENV_VAR} env var if omitted)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        api_key = get_api_key()
    except MissingAPIKeyError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    model = args.model or get_default_model()
    if not model:
        print(
            f"Error: no model specified. Pass --model or set {DEFAULT_MODEL_ENV_VAR}.",
            file=sys.stderr,
        )
        return 1

    client = ProsGrowClient(api_key=api_key, base_url=get_base_url(), timeout=args.timeout)

    try:
        result = client.send_prompt(model=model, prompt=args.prompt)
    except AuthenticationError as exc:
        print(f"Authentication failed (status {exc.status_code}): {exc}", file=sys.stderr)
        return 1
    except RateLimitError as exc:
        print(f"Rate limited (status {exc.status_code}): {exc}", file=sys.stderr)
        return 1
    except APIConnectionError as exc:
        print(f"Connection error: {exc}", file=sys.stderr)
        return 1
    except APIResponseError as exc:
        print(f"API error (status {exc.status_code}): {exc}", file=sys.stderr)
        return 1

    print(f"Model:    {result.model}")
    print(f"Status:   {result.status_code}")
    print(f"Latency:  {result.latency_ms:.1f} ms")
    print("Response:")
    print(result.content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
