# main-abc123.js (external)

- Defines `window.App.refresh` — POSTs `localStorage` refresh token to `/auth/refresh`.
- API base comes from `window.__CFG.api` (set in `login.0.js` inline).
- No dangerous sinks in this file. No hardcoded secrets.
- Cross-ref: auth flow continues in `732-def456.js` note (hash-driven panel render —
  see gadgets: `innerHTML` sink, CONFIRMED with trace).
