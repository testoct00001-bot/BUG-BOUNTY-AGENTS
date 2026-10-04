# login.0.js (inline, /login)

- Sets `window.__CFG` — global config: API base `https://api.app.target.com/v2`, env `prod`.
- No sinks, no event listeners. Pure config — but note: API base is client-visible,
  so version-downgrade probing (`/v1/...` on the same host) is in scope.
- Cross-ref: `__CFG` consumed by `main-abc123.js` (see `../external/main-abc123.md`).
