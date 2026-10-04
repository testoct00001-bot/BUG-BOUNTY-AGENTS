# Site summary — app.target.com

## Stack
Vanilla JS + webpack bundles. API at `api.app.target.com/v2`.

## Auth flow
1. `/login` sets `window.__CFG` (inline `login.0.js`).
2. `main-abc123.js` exposes `App.refresh` — refresh-token POST to `/auth/refresh`.
3. Refresh token lives in `localStorage` (`rt` key) — XSS anywhere = session theft.

## API surface
- `POST /v2/auth/refresh` — token refresh (see findings/endpoints.jsonl)
- Hash-driven panel render in `732-def456.js` — `location.hash` → `innerHTML`
  (**CONFIRMED** DOM sink, full trace in `../examples/gadgets.json` style)

## Notes for the hunter
- Config is client-visible → probe `/v1/` version-downgrade on the API host.
- `localStorage.rt` + the `innerHTML` sink chain into session theft — lead ladder.
