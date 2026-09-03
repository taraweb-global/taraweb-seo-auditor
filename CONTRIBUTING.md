# Contributing

Thank you for helping improve TaraWeb SEO Auditor.

1. Open an issue describing the bug or proposed change.
2. Keep changes focused and include tests for behavior changes.
3. Run `python -m compileall -q app.py challenge_browser.py` and `pytest -q`.
4. Run `python -m pip_audit -r requirements.txt` before submitting.
5. Explain user-facing, security and compatibility effects in the pull request.

Never commit tokens, credentials, `.env` files, customer data, saved crawl files, private URLs or exported audit reports containing sensitive information.
