# Engineering audit

Audit date: 2026-09-01

## Original application

The selected source was a single-process Python Flask application with a large server module, one large JavaScript client, one HTML template and CSS. It crawled websites concurrently, streamed results over SSE, inspected common technical SEO signals, saved crawl data locally and exported reports. Optional Playwright integration supported JavaScript-rendered pages and challenge handling.

## Strengths

- Broad technical SEO coverage with useful sitemap, duplicate-content and crawl-budget reports.
- Local-first operation with no account requirement.
- Per-host crawl delay, worker limits and robots.txt support.
- Saved-crawl comparison and structured exports.
- Straightforward Python and browser technology stack.

## Weaknesses and risks found

- The development server listened on every network interface by default.
- State-changing routes had no anti-CSRF control or authentication boundary.
- Arbitrary crawl targets created an SSRF path to loopback and private-network services when network-exposed.
- Self-update could fetch and hard-reset the checkout, reinstall packages and restart the process through an HTTP request.
- The crawl stream allowed any origin.
- The `lxml<6` dependency constraint resolved to a release flagged by the vulnerability audit.
- The frontend relies heavily on inline event handlers and HTML-string rendering, which makes a strict Content Security Policy and comprehensive XSS assurance difficult.
- Core code is concentrated in very large files, increasing regression and review risk.
- The original automated test was a live-network browser harness rather than a deterministic unit suite.
- Documentation contained performance and comparison claims that were not reproducible in this audit.
- Original Git history exposed the upstream author's public commit email metadata. No credential-pattern or sensitive-filename candidates were found in the scanned history.

## Improvements applied

- Rebranded the public application and documentation as TaraWeb SEO Auditor.
- Preserved the required upstream MIT copyright and added a clear modification notice.
- Changed the default bind address to loopback and made host/port configurable.
- Added per-process CSRF protection to state-changing routes.
- Added URL validation that blocks credentials and non-public target addresses by default.
- Removed browser-triggered self-update/restart and made installer updates manual-only.
- Added redirect-by-redirect SSRF checks, browser request guards, bounded downloads and isolation from ambient proxy/`.netrc` credentials.
- Removed permissive cross-origin streaming and added defensive response and cache headers.
- Constrained saved-crawl reads/deletes to non-symlink JSON files within approved folders.
- Removed destructive installer rollback commands and kept the Chromium sandbox enabled.
- Updated the vulnerable dependency constraint and added a repeatable dependency audit.
- Added deterministic security/regression tests and a least-privilege CI workflow.
- Replaced unsupported marketing claims with verifiable feature and safety documentation.
- Added responsive tablet/phone layouts, consistent keyboard focus and reduced-motion support.
- Added programmatic form labels, live error/progress semantics and accessible dialog focus behavior.
- Reorganized the crowded configuration rail into clear target, crawl-limit and optional advanced-analysis groups.
- Standardized native inputs, selects, sliders and action buttons on the TaraWeb design tokens.
- Added a visible idle/running status indicator, an animated stop state that respects reduced-motion preferences and keyboard operation for legacy report controls.
- Added client-side URL normalization plus clear server-side numeric validation errors.
- Fixed the failed-request path that previously treated non-2xx JSON as an SSE stream and left the UI in a misleading running state.

## Remaining engineering opportunities

- Split `app.py` into route, crawl, storage and export modules.
- Replace inline event handlers and HTML-string UI construction with DOM-safe rendering, then introduce a strict CSP.
- Add deterministic fixture sites for end-to-end crawl testing without third-party network dependencies.
- Add authentication before supporting shared-network deployments.
- Add rate limits and destination-IP pinning to close the residual DNS-rebinding window before any future multi-user deployment.
