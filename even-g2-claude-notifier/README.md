# Even G2 — Claude Code Notifier

Surface **Claude Code session events on your Even Realities G2 glasses HUD** —
e.g. "Claude needs you" when a session is waiting for input/permission, and
"Claude is done" when a response finishes.

> Self-contained subproject. It is **not** wired into the parent `Iditeration`
> app and shares none of its code or dependencies.

## How it works

```
┌─────────────────────┐   POST /notify    ┌───────────────┐   WebSocket /ws   ┌──────────────────┐
│  Claude Code         │ ───────────────▶ │  relay server  │ ───────────────▶ │ Even Hub plugin   │
│  (hook on Stop /     │  (bearer token)   │  (FastAPI)     │   (or /poll)      │ (phone WebView)   │
│   Notification /     │                   └───────────────┘                   │   │ bridge → HUD  │
│   SessionEnd)        │                                                       └───┼──────────────┘
└─────────────────────┘                                                            ▼
                                                                              G2 glasses HUD
```

**Why a relay?** Per the Even Hub architecture, plugin logic runs in a WebView
inside the Even Realities phone app — it can make outbound `fetch`/WebSocket
calls (if the origin is whitelisted in `app.json` + CORS is set), but it can't
listen on a port. So Claude Code pushes events to a small relay the phone
connects out to.

**Caveat:** the plugin receives events only while it's the active Even Hub app
in the foreground. There's no general background daemon on the glasses platform.
For lock-screen-style alerts you'd instead rely on OS notification mirroring;
this project covers live glances while you work.

## Components

| Folder        | What it is                                                            |
|---------------|-----------------------------------------------------------------------|
| `relay/`      | FastAPI relay: `POST /notify`, `WS /ws`, `GET /poll`, `GET /health`.  |
| `claude-hook/`| Stdlib Python hook script + a `settings.json` snippet to install it.  |
| `plugin/`     | Vite + TypeScript Even Hub G2 plugin using `@evenrealities/even_hub_sdk`. |

## Setup

### 1. Relay
```bash
cd relay
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set RELAY_TOKEN (and tighten RELAY_ALLOWED_ORIGINS)
export $(grep -v '^#' .env | xargs)
uvicorn server:app --host 0.0.0.0 --port 8787
```
Host it where both your Claude Code machine and your phone can reach it
(VPS / Tailscale / localhost). Put it behind HTTPS — the WebView needs `wss://`.

### 2. Claude Code hook
Merge `claude-hook/settings.example.json` into `~/.claude/settings.json`, fix the
absolute path to `notify_glasses.py`, and set `GLASSES_RELAY_URL` /
`GLASSES_RELAY_TOKEN`. The hook is stdlib-only and exits 0 even if the relay is
down, so it never blocks a session. Test it:
```bash
echo '{"hook_event_name":"Notification","message":"Claude needs your permission","cwd":"/tmp/demo"}' \
  | GLASSES_RELAY_URL=http://localhost:8787 GLASSES_RELAY_TOKEN=yourtoken \
    python3 claude-hook/notify_glasses.py
```

### 3. Plugin
```bash
cd plugin
npm install
# edit src/config.ts (RELAY_WS / RELAY_HTTP / RELAY_TOKEN)
# edit app.json `network` to whitelist your relay's https + wss origins
npm run dev          # or: npm run simulator
npm run build        # then `npm run package` to produce an .ehpk for Even Hub
```

## Verifying the path end-to-end
1. Start the relay; confirm `GET /health` returns `{"ok": true}`.
2. Run the plugin in the Even Hub simulator (or sideload it).
3. Fire the hook test command above → the notification should appear on the HUD.

## API / SDK notes
- HUD is **576×288**, 4-bit grayscale (green). Text via `TextContainerProperty`
  (≤8 per page). `createStartUpPageContainer` once (≤1000 chars), then
  `textContainerUpgrade` for flicker-free updates (≤2000 chars).
- Input/lifecycle via `bridge.onEvenHubEvent` (`CLICK_EVENT`, `FOREGROUND_ENTER`, …).
- SDK is v0.0.x and evolving. All glasses calls are isolated in
  `plugin/src/glasses.ts` — if a signature changed in your installed version,
  adjust there. The official Even Hub Claude Code skills (`quickstart`,
  `glasses-ui`, `build-and-deploy` in `even-realities/everything-evenhub`) track
  current signatures.

## References
- Even Hub docs: https://hub.evenrealities.com/docs
- SDK: https://www.npmjs.com/package/@evenrealities/even_hub_sdk
- Templates: https://github.com/even-realities/evenhub-templates
