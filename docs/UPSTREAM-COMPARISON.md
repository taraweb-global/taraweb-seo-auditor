# Exact comparison with upstream

Upstream baseline: `puneetindersingh/open-seo-crawler` at commit `dcfd8797bf2667f80f6a3d2b427541f26b33ebb6`.

This document describes functional and quality changes in the local TaraWeb edition. It does not use changed-line percentage as a quality measure.

| Area | Upstream behavior | TaraWeb local improvement |
|---|---|---|
| License | MIT license with the original author's required notice. | Notice preserved unchanged; `NOTICE.md` records the source and identifies TaraWeb's modifications. |
| Product identity | Open SEO Crawler branding and upstream update URLs. | TaraWeb SEO Auditor name, TaraWeb visual tokens, new repository references and an explicit modification identity. |
| Default exposure | Flask listened on `0.0.0.0`, exposing the development server to reachable networks. | Listens on `127.0.0.1`; non-loopback listening requires an explicit environment override and logs a warning. |
| State-changing requests | POST endpoints accepted same-origin or cross-site requests without an application token. | A per-process CSRF token is embedded in the page and automatically added to same-origin mutations; missing/invalid tokens return `403`. |
| Crawl-target safety | User-controlled URLs could reach loopback, private, link-local or reserved services when the app was network exposed. | HTTP(S)-only validation rejects embedded credentials and blocks non-global targets by default; private targets require explicit opt-in. |
| Request size | No explicit Flask body-size limit. | A configurable 16 MiB default request limit reduces memory-exhaustion risk from imports and exports. |
| Update controls | HTTP endpoints could fetch Git changes, hard-reset the checkout, install packages and restart the process. | Browser update/restart endpoints are unavailable; installer updates require an explicit command and never hard-reset local files. |
| Cross-origin behavior | Crawl streaming returned `Access-Control-Allow-Origin: *`. | Permissive cross-origin streaming was removed. |
| Browser hardening | No consistent defensive response headers. | Adds `nosniff`, clickjacking protection, no-referrer policy, same-origin isolation headers, no-store caching and a restrictive permissions policy; Chromium keeps its sandbox enabled. |
| Dependency security | `lxml>=5,<6` resolved to a version reported vulnerable by the audit. | `lxml>=6.1,<7` resolves cleanly; the repeatable production dependency audit reports no known vulnerabilities. |
| API validation | Invalid numeric values could raise server errors; several bounds were only partially clamped. | Reusable integer/float validators produce specific `400` responses and enforce page, depth, delay and worker limits. |
| Missing URL response | `/crawl` returned a raw JSON string without a JSON response content type. | Returns a consistent `jsonify` error response. |
| URL entry UX | Empty input only received focus; malformed input could proceed to a server/DNS failure. | Client-side normalization accepts bare domains, rejects whitespace/credentialed URLs, marks invalid fields and gives actionable error copy. |
| Failed crawl UX | Non-2xx `/crawl` responses were read as SSE and could leave the interface in an empty running state. | Non-2xx JSON errors are parsed, displayed in the error banner and return the UI to an idle state. |
| Mobile/tablet UX | Fixed 300 px + 240 px + content columns overflowed narrow screens; no mobile breakpoint existed. | Tablet and phone breakpoints stack the workspace, keep controls touch-sized and preserve table-level scrolling without page-level horizontal overflow. |
| Configuration UX | Every crawler option appeared in one dense, visually flat sidebar. | Uses a clear form hierarchy, grouped crawl limits and a collapsed optional-analysis section while retaining every original control. |
| Loading feedback | Crawl state was communicated mainly by swapping Start and Stop buttons. | Adds a persistent live status line, `aria-busy` state and a visible in-progress stop treatment. |
| Keyboard access | Focus visibility depended on browser defaults and there was no skip link. | Adds a high-contrast `:focus-visible` treatment and a skip link to the crawler workspace. |
| Form accessibility | Several sliders and custom fields had visual text without programmatic label association. | Associates range controls and advanced fields with labels; exposes pressed state for view tabs. |
| Dynamic accessibility | Errors, progress and status updates had no live-region semantics; the page-limit overlay lacked dialog semantics/focus placement. | Adds status/alert regions, dialog labels, initial dialog focus and focus restoration. |
| Motion preferences | No global reduced-motion fallback. | Respects `prefers-reduced-motion` for transitions and animations. |
| Deterministic tests | The supplied script depended on Playwright, live third-party sites and a separately running server. | Adds 16 deterministic tests covering branding, headers, CSRF, redirect safety, download limits, saved-file containment, update removal, validation and crawler parsing; the live harness remains optional. |
| Continuous verification | No repository CI workflow. | Adds least-privilege CI for dependency installation, compilation, tests and vulnerability auditing. |
| Documentation quality | Included unverified performance/comparison claims and automatic-update guidance. | Uses verifiable feature descriptions, clear threat-model limits, configuration details, responsible-use guidance and exact attribution. |
| Publication hygiene | Upstream Git history contained the upstream committer's email metadata. | The local publish plan excludes upstream `.git` history and all local environments/caches; no publication is currently authorized. |

## Why this is materially more than a cosmetic improvement

The change set addresses independent product-quality dimensions: security boundaries, input reliability, failure recovery, mobile usability, keyboard/screen-reader accessibility, dependency safety, deterministic testing and documentation integrity. These improvements alter how the application behaves under misuse, invalid input, small screens, assistive technology and failed network requests; they are not renaming or filler work.
