# ProsGrow API — Developer Integration Note

A practical guide for developers integrating with the ProsGrow API using this validation tool.

---

## 1. Environment Setup

**Requirements**
- Python 3.9+
- `pip` (comes with Python)

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Configure credentials**

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env`:

```
PROSGROW_API_KEY=sk-your-key-here
# optional overrides — leave commented out unless you need to change them
# PROSGROW_API_BASE_URL=https://staging.prosgrow.ai/v1
# PROSGROW_DEFAULT_MODEL=your-model-name
```

The tool uses `python-dotenv` to load `.env` automatically — no manual `export` needed.

> `.env` is git-ignored. Never commit a real API key.

---

## 2. Authentication

The API uses **Bearer token** authentication. Every request must include:

```
Authorization: Bearer <your-api-key>
```

Obtain your API key from the ProsGrow staging console at `https://staging.prosgrow.ai/`. Navigate to your account settings or the API Keys section to generate one.

The validation tool reads the key from `PROSGROW_API_KEY` and injects it into the `Authorization` header automatically. The key is never printed, logged, or included in error messages.

---

## 3. API Endpoint

| Field | Value |
|-------|-------|
| Base URL (staging) | `https://staging.prosgrow.ai/v1` |
| Chat completions endpoint | `POST /v1/chat/completions` |
| Content-Type | `application/json` |

> **Docs vs. actual behavior:** The written documentation references `https://api.prosgrow.ai` as the base URL, but the docs' own example `curl` command targets `https://staging.prosgrow.ai`. This tool defaults to the staging host per the exercise's staging-only instruction. This discrepancy should be clarified in the official docs.

---

## 4. Required Parameters

**Request body (JSON)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | The model identifier to use |
| `messages` | array | Yes | Array of message objects |
| `messages[].role` | string | Yes | `"user"`, `"assistant"`, or `"system"` |
| `messages[].content` | string | Yes | The message text |

**Recommended headers**

| Header | Description |
|--------|-------------|
| `Authorization` | `Bearer <api-key>` |
| `Content-Type` | `application/json` |
| `Idempotency-Key` | A UUID per request; prevents duplicate processing on retries |

**Minimal request example**

```json
{
  "model": "your-model-name",
  "messages": [
    { "role": "user", "content": "Hello, how are you?" }
  ]
}
```

**Response shape**

```json
{
  "choices": [
    {
      "message": {
        "content": "I'm doing well, thanks for asking!"
      }
    }
  ]
}
```

The tool reads the response from `choices[0].message.content`.

---

## 5. How to Run the Validation Tool

**Basic usage**

```bash
python -m prosgrow_validator "Your prompt here" --model deepseek-v4-pro
```

**With a default model set via env var** (set `PROSGROW_DEFAULT_MODEL` in `.env`)

```bash
python -m prosgrow_validator "Your prompt here"
```

**Override request timeout (default: 30s)**

```bash
python -m prosgrow_validator "Your prompt here" --model your-model-name --timeout 60
```

**Run the unit test suite (no API key or network needed)**

```bash
python -m unittest discover -s tests -v
```

---

## 6. Working Example

```bash
# with PROSGROW_API_KEY set in .env
python -m prosgrow_validator "Say hello in one sentence." --model deepseek-v4-pro
```

Actual output captured during testing:

```
Model:    deepseek-v4-pro
Status:   200
Latency:  1158.4 ms
Response:
Hello! How can I help you today?
```

---

## 7. Errors Encountered

The following errors were observed during testing. See `validation_results.md` for the full test matrix.

| Scenario | HTTP Status | Error Type | Tool Output |
|----------|-------------|------------|-------------|
| Missing `PROSGROW_API_KEY` env var | N/A (no request sent) | `MissingAPIKeyError` | `Configuration error: PROSGROW_API_KEY is not set.` |
| Invalid API key (`sk-invalid-test-key`) | 401 | `AuthenticationError` | `Authentication failed (status 401): API key was rejected` |
| Invalid model name (`this-model-does-not-exist`) | 404 | `APIResponseError` | `API error (status 404): ... "message":"The requested model was not found.","type":"not_found_error","code":"model_not_found"` |
| Empty prompt (`""`) | 400 | `APIResponseError` | `API error (status 400): ... "'messages[0].content' must be a non-empty string or a non-empty array of content parts."` |
| Network unavailable / timeout | N/A | `APIConnectionError` | `Connection error: Could not connect to https://staging.prosgrow.ai/v1` |
| Rate limit exceeded | 429 | `RateLimitError` | `Rate limited (status 429): Got rate limited by the API` |

> Full raw terminal output for each scenario is in `TEST_RESULTS.md`.

---

## 8. Docs vs. Actual API Behavior

| Area | Documentation Says | Actual Behavior |
|------|-------------------|-----------------|
| Base URL | `https://api.prosgrow.ai` (prose) | Docs' own example `curl` targets `https://staging.prosgrow.ai`; this tool defaults to staging per the exercise |
| Chat SKU availability | Docs say chat SKUs are "catalog-only during preview and not callable without onboarding" | Requests succeeded with the test key as-is — that restriction appears outdated or misscoped |
| Model discovery | No mention of a model catalog endpoint | `GET /v1/models` works and returns available models (e.g. `deepseek-v4-pro`); undocumented |
| Empty-content validation | Not documented | API returns 400 with `"'messages[0].content' must be a non-empty string"` — constraint should be listed in the request schema |
| 401 response body | No example provided | Tool masks the raw body; docs should publish an example 401 response so client authors know what to parse |

---

## Quick Reference

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env  # then edit .env with your key (dotenv loads it automatically)

# Run
python -m prosgrow_validator "Your prompt" --model deepseek-v4-pro

# Test (no API key or network needed)
python -m unittest discover -s tests -v
```
