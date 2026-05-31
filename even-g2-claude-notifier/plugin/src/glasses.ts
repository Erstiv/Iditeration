/**
 * Thin wrapper over the Even Hub SDK display calls, tuned for a single
 * full-screen text card on the 576x288 green HUD.
 *
 * Confirmed against the docs: `waitForEvenAppBridge`, `TextContainerProperty`,
 * `CreateStartUpPageContainer` + `bridge.createStartUpPageContainer(...)`,
 * `bridge.rebuildPageContainer(...)`, `bridge.textContainerUpgrade(...)`,
 * and `bridge.onEvenHubEvent(cb)`.
 *
 * NOTE: SDK is v0.0.x and moving fast — if a method name/shape differs in your
 * installed version, the `quickstart`/`glasses-ui` Even Hub Claude Code skills
 * (in even-realities/everything-evenhub) will show the current signatures.
 * Everything funnels through this file so there's one place to adjust.
 */
import {
  waitForEvenAppBridge,
  TextContainerProperty,
  CreateStartUpPageContainer,
} from "@evenrealities/even_hub_sdk";

// The single text container we keep reusing. ID is referenced by the
// partial-update (textContainerUpgrade) path so we avoid full-page flicker.
const MAIN_ID = 1;

// Glyphs the G2 can render (Unicode, 4-bit grayscale). Keep them simple.
const GLYPH: Record<string, string> = {
  attention: "‼",
  done: "✓",
  error: "✕",
  info: "•",
};

export type Note = {
  title: string;
  body: string;
  level: string;
  session_id?: string;
  event?: string;
};

let bridge: Awaited<ReturnType<typeof waitForEvenAppBridge>> | null = null;
let started = false;

function render(note: Note): string {
  const glyph = GLYPH[note.level] ?? GLYPH.info;
  // createStartUpPageContainer caps at 1000 chars; we're well under.
  return `${glyph} ${note.title}\n\n${note.body}`.slice(0, 1000);
}

function mainContainer(text: string): TextContainerProperty {
  return new TextContainerProperty({
    xPosition: 0,
    yPosition: 0,
    width: 576,
    height: 288,
    borderWidth: 0,
    borderColor: 5,
    paddingLength: 8,
    containerID: MAIN_ID,
    containerName: "main",
    content: text,
    isEventCapture: 1, // capture taps so we can dismiss on click
  });
}

/** Connect to the glasses and paint the initial "waiting" screen. */
export async function initGlasses(initialText: string): Promise<void> {
  bridge = await waitForEvenAppBridge();
  await bridge.createStartUpPageContainer(
    new CreateStartUpPageContainer({
      containerTotalNum: 1,
      textObject: [mainContainer(initialText)],
    }),
  );
  started = true;
}

/**
 * Update the HUD text. Prefers the flicker-free partial update
 * (textContainerUpgrade); falls back to a full rebuild if needed.
 */
export async function setText(text: string): Promise<void> {
  if (!bridge || !started) return;
  const clipped = text.slice(0, 2000); // textContainerUpgrade caps at 2000
  try {
    await bridge.textContainerUpgrade({ containerID: MAIN_ID, content: clipped });
  } catch {
    await bridge.rebuildPageContainer(
      new CreateStartUpPageContainer({
        containerTotalNum: 1,
        textObject: [mainContainer(clipped)],
      }),
    );
  }
}

export async function showNote(note: Note): Promise<void> {
  await setText(render(note));
}

/** Register a callback for glasses/ring input + lifecycle events. */
export function onEvent(cb: (event: any) => void): void {
  bridge?.onEvenHubEvent(cb);
}
