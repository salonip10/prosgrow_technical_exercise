# ProsGrow API Validation Tool

A minimal CLI that sends a prompt to a model via the ProsGrow API, prints the
response, and reports the HTTP status and round-trip latency.

## Design

- [`prosgrow_validator/client.py`](prosgrow_validator/client.py) — `ProsGrowClient`, the only place that
  knows the HTTP request/response schema. Per the docs published at
  `https://staging.prosgrow.ai/docs`, ProsGrow is an OpenAI-compatible
  chat-completion API: `POST /v1/chat/completions` with
  `{"model", "messages"}` plus an `Idempotency-Key` header, response read
  from `choices[0].message.content`. If actual behavior turns out to differ
  from the docs, `send_prompt` is the only place that needs to change.

  **Docs vs. behavior note:** the docs' prose names `https://api.prosgrow.ai`
  as the base URL, but the docs' own example `curl` command targets
  `https://staging.prosgrow.ai`. This tool defaults to the staging host
  (`PROSGROW_API_BASE_URL`, see `.env.example`) per the exercise's
  staging-only instruction — worth flagging as a documentation fix.
- [`prosgrow_validator/config.py`](prosgrow_validator/config.py) — reads configuration from environment
  variables. Nothing else in the package touches `os.environ` directly.
- [`prosgrow_validator/exceptions.py`](prosgrow_validator/exceptions.py) — a small exception hierarchy
  (`AuthenticationError`, `RateLimitError`, `APIConnectionError`,
  `APIResponseError`) so callers can handle specific failure modes instead of
  parsing error strings.
- [`prosgrow_validator/cli.py`](prosgrow_validator/cli.py) — argument parsing and orchestration; maps
  each exception type to a clear message and a non-zero exit code.

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, fill in your real key, and export the
variables (or load them however you normally manage env vars):

```bash
export PROSGROW_API_KEY=sk-...
export PROSGROW_API_BASE_URL=https://api.prosgrow.ai/v1   # optional, has a default
export PROSGROW_DEFAULT_MODEL=your-default-model          # optional
```

`.env` is git-ignored — never commit a real API key.

## Usage

```bash
python -m prosgrow_validator "Summarize this exercise in one sentence" --model your-model
```

Output:

```
Model:    your-model
Status:   200
Latency:  842.3 ms
Response:
<model's response text>
```

`--model` can be omitted if `PROSGROW_DEFAULT_MODEL` is set. `--timeout`
overrides the default 30s request timeout.

## Error handling

The client distinguishes several failure modes and the CLI reports each with
a specific message and exit code 1:

- **Missing/invalid API key** — `PROSGROW_API_KEY` unset, or the API returns
  401/403 (`AuthenticationError`).
- **Rate limiting** — API returns 429 (`RateLimitError`).
- **Network failure / timeout** — the request never got a response
  (`APIConnectionError`).
- **Other API errors** — any other non-2xx status, or a response body that
  doesn't match the expected shape (`APIResponseError`).

## Credentials

The API key is read once from `PROSGROW_API_KEY` and used only to build the
`Authorization` header for the ProsGrow request. It is never printed, logged,
or included in any exception message.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests mock the HTTP layer (`requests.Session`), so no network access or real
API key is needed to run them.
