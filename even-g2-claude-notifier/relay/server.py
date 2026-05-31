"""Relay server: bridges Claude Code session events to an Even G2 Hub plugin.

Flow:
    Claude Code hook  --POST /notify-->  this relay  --WebSocket /ws-->  G2 plugin

The relay is deliberately tiny and stateless-ish (in-memory ring buffer only).
Run it somewhere both your Claude Code machine AND your phone can reach
(a small VPS, a Tailscale node, or localhost if everything is on one box).

Auth is a single shared bearer token (RELAY_TOKEN). The glasses plugin must
list this server's origin in its app.json `network` whitelist, and the CORS
config below must allow that origin.
"""

from __future__ import annotations

import asyncio
import os
import time
from collections import deque
from typing import Deque

from fastapi import FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

RELAY_TOKEN = os.environ.get("RELAY_TOKEN", "")
# Comma-separated list of allowed browser origins (the Even Hub WebView origin).
# "*" is convenient for local testing but tighten this for anything real.
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("RELAY_ALLOWED_ORIGINS", "*").split(",") if o.strip()]
RING_SIZE = int(os.environ.get("RELAY_RING_SIZE", "50"))

app = FastAPI(title="Even G2 Claude Notifier Relay", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Notification(BaseModel):
    """One session event headed for the glasses."""

    title: str = Field(..., max_length=40)
    body: str = Field("", max_length=200)
    # "info" | "attention" | "done" | "error" — the plugin maps these to glyphs.
    level: str = Field("info", max_length=16)
    session_id: str = Field("", max_length=80)
    event: str = Field("", max_length=40)  # Claude Code hook event name
    ts: float = Field(default_factory=time.time)


class _Hub:
    """Fans notifications out to every connected WebSocket and keeps a ring
    buffer so the /poll fallback and late-joining clients can catch up."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._ring: Deque[Notification] = deque(maxlen=RING_SIZE)
        self._lock = asyncio.Lock()

    async def register(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.add(ws)
        # Replay the most recent notification so a freshly-opened plugin
        # immediately shows the latest pending state instead of a blank HUD.
        if self._ring:
            await ws.send_json(self._ring[-1].model_dump())

    async def unregister(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def broadcast(self, note: Notification) -> int:
        self._ring.append(note)
        payload = note.model_dump()
        dead: list[WebSocket] = []
        async with self._lock:
            targets = list(self._clients)
        for ws in targets:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.unregister(ws)
        return len(targets) - len(dead)

    def since(self, ts: float) -> list[Notification]:
        return [n for n in self._ring if n.ts > ts]


hub = _Hub()


def _check_token(provided: str | None) -> None:
    if not RELAY_TOKEN:
        raise HTTPException(503, "RELAY_TOKEN is not configured on the relay")
    if provided != RELAY_TOKEN:
        raise HTTPException(401, "bad or missing token")


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "clients": len(hub._clients), "buffered": len(hub._ring)}


@app.post("/notify")
async def notify(note: Notification, authorization: str | None = Header(default=None)) -> dict:
    """Called by the Claude Code hook. `Authorization: Bearer <RELAY_TOKEN>`."""
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    _check_token(token)
    delivered = await hub.broadcast(note)
    return {"ok": True, "delivered_to": delivered}


@app.get("/poll")
async def poll(token: str = Query(...), since: float = Query(0.0)) -> dict:
    """Polling fallback for environments where the WebView can't hold a WS open."""
    _check_token(token)
    return {"notifications": [n.model_dump() for n in hub.since(since)], "now": time.time()}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: str = Query(...)) -> None:
    """The glasses plugin connects here and receives notifications as JSON."""
    if token != RELAY_TOKEN or not RELAY_TOKEN:
        await ws.close(code=4401)
        return
    await ws.accept()
    await hub.register(ws)
    try:
        while True:
            # We don't expect inbound messages; this just keeps the socket
            # alive and detects disconnects. Treat any frame as a ping.
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await hub.unregister(ws)
