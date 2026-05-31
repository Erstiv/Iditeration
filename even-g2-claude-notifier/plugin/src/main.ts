/**
 * Claude Notifier — Even G2 Hub plugin entry point.
 *
 * Lifecycle:
 *   1. Connect to the glasses, show a "waiting" card.
 *   2. Open a WebSocket to the relay; on each notification, paint it on the HUD.
 *   3. If the socket drops (or never opens), fall back to HTTP polling.
 *   4. A tap on the glasses dismisses the current notification.
 */
import { RELAY_WS, RELAY_HTTP, RELAY_TOKEN, POLL_INTERVAL_MS } from "./config";
import { initGlasses, showNote, setText, onEvent, type Note } from "./glasses";

const WAITING = "• Claude Notifier\n\nWaiting for session events…";
let lastTs = 0;
let socket: WebSocket | null = null;
let pollTimer: ReturnType<typeof setInterval> | null = null;

async function handleNote(note: Note & { ts?: number }) {
  if (typeof note.ts === "number") lastTs = Math.max(lastTs, note.ts);
  await showNote(note);
}

function startPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(async () => {
    try {
      const url = `${RELAY_HTTP}/poll?token=${encodeURIComponent(RELAY_TOKEN)}&since=${lastTs}`;
      const res = await fetch(url);
      if (!res.ok) return;
      const data = await res.json();
      for (const note of data.notifications ?? []) await handleNote(note);
    } catch {
      /* relay unreachable; try again next tick */
    }
  }, POLL_INTERVAL_MS);
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

function connectWs() {
  try {
    socket = new WebSocket(`${RELAY_WS}/ws?token=${encodeURIComponent(RELAY_TOKEN)}`);
  } catch {
    startPolling();
    return;
  }

  socket.onopen = () => stopPolling(); // WS is live, no need to poll
  socket.onmessage = (ev) => {
    try {
      handleNote(JSON.parse(ev.data));
    } catch {
      /* ignore malformed frames */
    }
  };
  socket.onclose = () => {
    socket = null;
    startPolling(); // keep receiving while we retry the socket
    setTimeout(connectWs, 3000);
  };
  socket.onerror = () => socket?.close();
}

async function main() {
  await initGlasses(WAITING);

  onEvent((event) => {
    // Tap (either temple or the R1 ring) dismisses the current card.
    const click = event?.textEvent === "CLICK_EVENT" || event?.sysEvent === "CLICK_EVENT";
    if (click) {
      void setText(WAITING);
      return;
    }
    // Re-establish the stream when the plugin returns to the foreground.
    if (event?.sysEvent === "FOREGROUND_ENTER" && !socket) connectWs();
  });

  connectWs();
}

void main();
