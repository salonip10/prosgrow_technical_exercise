# API Validation Results

Tested against the ProsGrow **staging** API (`https://staging.prosgrow.ai/v1`) using the
`prosgrow_validator` CLI, run from a local terminal (this sandbox's outbound network is
restricted by org policy, so tests were executed directly on a team member's machine).
Model used: `deepseek-v4-pro` (found via the unauthenticated `GET /v1/models` catalog
endpoint). Tested: 2026-09-09.

## Summary table

| # | Test scenario | Expected result | Actual result | Pass/Fail | Recommended API / docs improvement |
|---|---|---|---|---|---|
| 1 | Valid request (valid key, valid model, non-empty prompt) | HTTP 200, model response returned, status + latency reported | `Status: 200`, latency 1158.4 ms, coherent response returned (`"Hello! How can I help you today?"`) | **Pass** | Docs state chat SKUs are "catalog-only during preview and not callable without onboarding," but this request succeeded with the test key as-is. That line in the docs is misleading/outdated and should be corrected or scoped to specific models. |
| 2 | Invalid API key (`sk-invalid-test-key`, real model) | Request rejected with a 401/403 and a clear, non-crashing error; no key leaked in output | `Authentication failed (status 401): API key was rejected`, exit code 1, key never appears in output | **Pass** | The tool intentionally doesn't surface the raw 401 response body (only its own generic message), so we can't confirm the API's actual error JSON shape for auth failures. Recommend the docs publish an example 401 response body (same as they do for other error types) so client authors know what to parse. |
| 3 | Invalid/missing model (`this-model-does-not-exist`, real key) | Non-2xx response with a clear error, non-zero exit code | `API error (status 404): ... "message":"The requested model was not found.","type":"not_found_error","code":"model_not_found"` | **Pass** | The `/v1/models` catalog endpoint and the model-not-found error are undocumented on the docs page — worth adding both to the API reference so integrators know how to discover valid model ids and what a bad one returns. |
| 4 | Empty prompt (`""`, real key, real model) | Either a validation error before the request is sent, or a clear 4xx from the API | `API error (status 400): ... "'messages[0].content' must be a non-empty string or a non-empty array of content parts.","type":"invalid_request_error","code":"invalid_request"` | **Pass** | This validation rule (non-empty message content) isn't documented anywhere. Recommend the docs list required-field constraints (e.g. minimum content length) alongside the request schema. The client library could also add optional client-side pre-validation to save a round trip, though surfacing the server's real behavior as-is is arguably more useful for an integration-testing tool like this one. |

## Overall

All 4 scenarios behaved as expected — the API's actual behavior matched what a well-formed
OpenAI-compatible chat-completions API should do, and the validator tool correctly classified
and reported every case (right status code, right exception type, right exit code, no
credential leakage in any output). No functional bugs found in either the API or the tool.
The main gaps are in the **documentation**, not the API itself (see recommendations above,
plus the base-URL discrepancy already noted in the README: docs' prose names
`https://api.prosgrow.ai` while the docs' own example curl targets
`https://staging.prosgrow.ai`).

## Raw output (evidence)

```
$ python3 -m prosgrow_validator "Say hello in one sentence." --model deepseek-v4-pro ; echo "exit: $?"
Model:    deepseek-v4-pro
Status:   200
Latency:  1158.4 ms
Response:
Hello! How can I help you today?
exit: 0

$ PROSGROW_API_KEY=sk-invalid-test-key python3 -m prosgrow_validator "Say hello" --model deepseek-v4-pro ; echo "exit: $?"
Authentication failed (status 401): API key was rejected
exit: 1

$ python3 -m prosgrow_validator "Say hello" --model this-model-does-not-exist ; echo "exit: $?"
API error (status 404): API returned an error: 404 {"error":{"message":"The requested model was not found.","type":"not_found_error","param":"model","code":"model_not_found"}}
exit: 1

$ python3 -m prosgrow_validator "" --model deepseek-v4-pro ; echo "exit: $?"
API error (status 400): API returned an error: 400 {"error":{"message":"'messages[0].content' must be a non-empty string or a non-empty array of content parts.","type":"invalid_request_error","param":"messages","code":"invalid_request", ...}
exit: 1
```
