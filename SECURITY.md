# Security policy

Please report suspected vulnerabilities privately through TaraWeb's contact page: <https://taraweb.tech/contact/>. Do not include live credentials, customer information or exploit data from systems you do not own. Provide a minimal reproduction against a local test target where possible.

## Supported security boundary

TaraWeb SEO Auditor is a local, single-user development application. It binds to `127.0.0.1` by default and has no user authentication. Do not expose it directly to the public internet or a shared network. A shared deployment needs authentication, authorization, request throttling, a production WSGI server and a trusted reverse proxy.

The crawler deliberately connects to websites selected by its operator and processes untrusted HTML, headers and URLs. Its default controls:

- permit only HTTP and HTTPS targets without embedded credentials;
- block loopback, private, link-local and reserved destinations on the initial request and every redirect;
- apply the same destination policy to optional Playwright requests;
- cap request bodies and downloaded response bodies;
- ignore ambient proxy and `.netrc` credentials during crawler requests;
- require a per-process CSRF token for state-changing routes;
- prevent permissive cross-origin access and add defensive same-origin response headers;
- constrain saved-crawl reads and deletes to regular JSON files inside approved folders;
- keep browser sandboxing enabled; and
- provide no browser endpoint that can update source code or restart a process.

Private targets and invalid TLS certificates require separate, explicit environment opt-ins. Use either setting only for a target you control on a trusted machine.

## Secrets and local data

Never commit production credentials. Copy `.env.example` only for local configuration; `.env*` files are ignored except for the example itself. The application does not need TaraWeb production credentials and does not include telemetry.

Saved crawls and exports may contain page text, URLs, metadata and the requester's local IP address. Treat these artifacts as potentially confidential and inspect them before sharing.

## Known limitations

- Hostname validation and the eventual socket connection are separate operations, leaving a residual DNS-rebinding/time-of-check-to-time-of-use window. Keep the application local; destination-IP pinning is required before treating it as a multi-user service.
- The legacy client renders many escaped HTML templates and still uses inline event handlers, so a strict Content Security Policy is not yet enabled. URL links are restricted to HTTP(S), but a DOM-safe rendering migration remains recommended.
- Enabling JavaScript rendering executes untrusted website code inside Chromium. Keep Playwright and Chromium patched and run the application as an unprivileged OS user.
- Disabling TLS verification or allowing private targets materially weakens the default protections.
