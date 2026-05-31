/**
 * Plugin configuration.
 *
 * For a real, shippable app you'd collect these from a settings page and
 * persist them via the SDK's key-value storage instead of hardcoding. For a
 * sideloaded/personal build, filling these in is fine.
 *
 * RELAY_TOKEN must match the relay's RELAY_TOKEN, and both the https and wss
 * origins below must be listed in app.json's `network` whitelist.
 */
export const RELAY_HTTP = "https://relay.example.com";
export const RELAY_WS = "wss://relay.example.com";
export const RELAY_TOKEN = "change-me-to-match-relay";

/** Fall back to HTTP polling if the WebSocket can't stay open. */
export const POLL_INTERVAL_MS = 5000;
