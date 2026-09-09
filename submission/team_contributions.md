# Team Contribution Summary

## Student A — [Saloni Patel]
Built the API validation tool (Task 1).
- Designed and implemented the full Python CLI package (`prosgrow_validator/`)
- Wrote `client.py` with HTTP request logic, latency tracking, and four distinct error types (auth, rate limit, connection, malformed response)
- Wrote `cli.py` with argument parsing, env-var wiring, and per-error exit codes
- Wrote `config.py` and `exceptions.py`
- Wrote 12 unit tests in `tests/` covering all error paths, credential leakage, and idempotency key injection
- Wrote the initial `README.md` with setup and usage instructions

## Student B — [Prerana Anand]
Tested API behavior and documented results (Task 2).
- Obtained the API key from the staging console
- Ran four real scenarios against `https://staging.prosgrow.ai/v1`: valid request, invalid API key, invalid model, and one additional scenario
- Recorded HTTP status codes, actual response bodies, and latency
- Wrote `validation_results.md` with pass/fail verdicts and recommended API/documentation improvements

## Student C — [Aadesh Thoppae]
Created developer documentation, the bonus feature, and submission materials (Tasks 3 & 4).
- Wrote `integration_note.md` covering environment setup, authentication, API endpoint, required parameters, how to run the tool, a working example, errors encountered, and docs-vs-actual discrepancies
- Created `.env.example` so developers can configure credentials safely
- Implemented the bonus feature: [describe here after it's built]
- Wrote `submission/team_contributions.md` and `submission/ai_usage_note.md`
