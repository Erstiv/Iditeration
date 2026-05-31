#!/usr/bin/env python3
"""Claude Code hook -> Even G2 relay.

Claude Code invokes this with the hook payload on stdin (JSON). We translate
the event into a short glasses-sized notification and POST it to the relay.

Stdlib only (urllib) so it has zero install footprint and runs from any hook.

Configure via env (set them in your shell profile or the hook command):
    GLASSES_RELAY_URL    e.g. https://relay.example.com   (no trailing /notify)
    GLASSES_RELAY_TOKEN  must match the relay's RELAY_TOKEN

Wire it up in settings.json — see settings.example.json in this folder.
Exit code is always 0: a notifier must never block or fail your session.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

RELAY_URL = os.environ.get("GLASSES_RELAY_URL", "").rstrip("/")
RELAY_TOKEN = os.environ.get("GLASSES_RELAY_TOKEN", "")
TIMEOUT_S = 4


def _short(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def build_notification(payload: dict) -> dict:
    """Map a Claude Code hook payload to a {title, body, level, ...} notification.

    Recognised hook events: Notification, Stop, SubagentStop, SessionEnd.
    Unknown events still pass through with a generic title.
    """
    event = payload.get("hook_event_name", "")
    session_id = payload.get("session_id", "")
    cwd = os.path.basename(payload.get("cwd", "")) or "session"

    if event == "Notification":
        # message is e.g. "Claude needs your permission to use Bash" or
        # "Claude is waiting for your input".
        msg = payload.get("message", "Needs your attention")
        level = "attention"
        title = "Claude needs you"
        body = msg
    elif event in ("Stop", "SubagentStop"):
        level = "done"
        title = "Claude is done"
        body = f"Finished in {cwd}. Tap to dismiss."
    elif event == "SessionEnd":
        level = "info"
        title = "Session ended"
        body = cwd
    else:
        level = "info"
        title = event or "Claude"
        body = payload.get("message", "")

    return {
        "title": _short(title, 40),
        "body": _short(body, 200),
        "level": level,
        "session_id": session_id,
        "event": event,
    }


def main() -> int:
    if not RELAY_URL or not RELAY_TOKEN:
        # Not configured — silently no-op so the hook is safe to leave installed.
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, ValueError):
        payload = {}

    note = build_notification(payload)

    req = urllib.request.Request(
        f"{RELAY_URL}/notify",
        data=json.dumps(note).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RELAY_TOKEN}",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=TIMEOUT_S)
    except (urllib.error.URLError, TimeoutError) as exc:
        # Don't break the user's session over a flaky notifier; log to stderr.
        print(f"[notify_glasses] relay unreachable: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
