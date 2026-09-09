# AI Usage and Verification Note

## AI Tools Used
- Claude (Anthropic) — via Claude Code CLI

## What AI Helped Generate
- Initial structure and boilerplate for `prosgrow_validator/client.py`, `cli.py`, `config.py`, and `exceptions.py`
- Unit test scaffolding in `tests/test_client.py` and `tests/test_cli.py`
- `integration_note.md` — full draft of the developer integration guide
- `.env.example` template
- `submission/team_contributions.md` and this file

## One Error, Weakness, or Unsupported Assumption Produced by AI
The AI assumed the ProsGrow API's response shape exactly matches the OpenAI chat completions format (`choices[0].message.content`) based on the staging docs, and it assumed the error response bodies would be standard. It also generated example outputs in `integration_note.md` with placeholder model names and fabricated latency numbers, since it had no access to the live staging environment. The AI did not discover that the API exposes an undocumented `GET /v1/models` catalog endpoint, and it could not predict that the docs' statement about "chat SKUs being catalog-only during preview" was outdated.

## How the Team Tested and Corrected the Output
- Student B ran all four test scenarios against the real staging API and recorded actual HTTP status codes, response bodies, and latency in `TEST_RESULTS.md`
- Discovered the real working model (`deepseek-v4-pro`) via the undocumented `GET /v1/models` endpoint — AI had no knowledge of valid model names
- The integration note's working example and errors table were updated with real captured output after live testing
- The docs-vs-actual table in `integration_note.md` Section 8 was filled in from B's real findings, not AI guesses
- The unit test suite (`python -m unittest discover -s tests -v`) was run locally to verify all 12 tests pass before submission

## What the Team Would Improve with Two Additional Hours
- Add a `--batch` mode that runs all four validation scenarios automatically and prints a formatted results table — currently each scenario must be run by hand
- Write a more detailed retry-with-backoff mechanism for transient errors (currently the tool exits immediately on any failure)
- Expand the test suite with integration tests that hit a locally mocked HTTP server rather than relying only on `unittest.mock`
- Add output format options (`--json`, `--csv`) so validation results can be piped into other tools
