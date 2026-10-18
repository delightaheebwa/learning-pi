# Phase 0 — spike findings

Status: **spikes done at source level; one live click-test blocked (needs an
Open WebUI API key).** Recorded 2026-10-18.

Environment probed:

- Open WebUI **v0.12.2**, live at `http://127.0.0.1:3000` (GET `/api/version` +
  `/api/config` both answered unauthenticated).
- Source read at tag `v0.12.2`, commit
  `6a18585ff4c2e5f6805f682222cfbc46dc669ef8` (2026-10-14). All `path:line`
  refs below are from that tag, not `main`.
- This host: `docker` needs `sudo` (password), so I could not inspect the
  container directly. `pi-bridge.service` is not installed here.
- **`~/.openwebui_key` does not exist on this host**, so authenticated REST
  calls (chat create/update, the embed event, reading it back) could not be run.
  `POST /api/v1/chats/cid/messages/mid/event` does answer `401 Not
  authenticated` (route exists) rather than `404`.

Every claim below is verified against v0.12.2 source unless marked *(live)* or
*(blocked)*.

---

## Spike 1 — Artifacts trigger on a ` ```html ` fence

**CONFIRMED.** No `message.artifacts` field and no backend detector exist in
v0.12.2; artifacts are derived **client-side** from message markdown and the
side panel is opened by `ContentRenderer.svelte`.

- A ` ```html ` fence triggers both the artifact-group extraction and the
  auto-open. Recognized for auto-open: `html`, `svg`, and `xml` **only when the
  code contains `<svg`**. `mermaid` is **not** an artifact — it renders inline.
- Triggering is **per code block** and the fallback scan is global
  (`/```[\s\S]*?```/g`), so surrounding prose in a long pi-style message is
  **irrelevant**.
- **No length/size threshold.** Gates are only: `detectArtifacts` setting
  (default true), not `compactPreview`, a closing fence exists, not already
  auto-opened, not mobile, and a current chat id exists.

Evidence:

- `src/lib/components/chat/Messages/ContentRenderer.svelte:144-171` —
  `isArtifact = ['html','svg'].includes(lang) || (lang === 'xml' && code.includes('<svg'))`
  and the auto-open condition (`showArtifacts.set(true)`).
- `src/lib/utils/index.ts:2380-2385` — `getCodeBlockContents` global fence scan.
- `src/lib/utils/index.ts:2409-2421` — `html` opens a group; `css` / `js` attach.
- `src/lib/components/chat/Messages/CodeBlock.svelte:371` — `mermaid` inline render.
- `backend/open_webui/models/users.py:75` — `detectArtifacts` default.

**Decision:** the ` ```html ` free-form path is viable and prose-independent.
` ```mermaid ` is confirmed as an inline (non-artifact) render. No fallback
("emit the artifact on its own turn") is needed for the trigger.

---

## Spike 2 — embeds delivery + placement

### 2a. Delivery: REST (pi-bridge is not a Filter)

The bridge is an OpenAI-compatible endpoint, **not** an Open WebUI Filter/Pipe,
so the Filter-`outlet` `__event_emitter__` path is unavailable. The bridge must
use the REST route:

`POST /api/v1/chats/{chat_id}/messages/{message_id}/event` with
`{"type":"embeds","data":{"embeds":["<url>"]}}` (optional `"replace": true`).

- **CONFIRMED (source).** `backend/open_webui/routers/chats.py:1604-1649`
  (`class EventForm`, `send_chat_message_event_by_id`), mounted at
  `/api/v1/chats` (`main.py:895`). It builds an event emitter and forwards the
  event; **no `session_id` is passed** (so the "shared" socket emit does not
  skip the originating client).
- **CONFIRMED (live).** Route exists and is auth-guarded (`401`, not `404`).
- Persistence happens inside `get_event_emitter` (`socket/main.py:1324`,
  `:1444-1459`): an `embeds` event calls
  `Chats.upsert_message_to_chat_by_id_and_message_id(..., {'embeds': embeds})`,
  which writes `chat_messages.embeds` (`models/chat_messages.py:152`). New
  embeds are **prepended** to existing ones unless `data.replace` is true.
  There is no `add_embeds` function in v0.12.2.

### 2b. Placement: embeds render ABOVE the message's own text

**CONFIRMED (source).** The embeds block is emitted **before**
`<ContentRenderer>` in the same assistant message:

- `src/lib/components/chat/Messages/ResponseMessage.svelte:735-755` renders
  `{#if message?.embeds ...}`; `<ContentRenderer ... />` is at `:849` (after).
- `src/lib/components/chat/Chat.svelte:1584-1592` handles the socket event
  (`'chat:message:embeds' || 'embeds'`): sets `message.embeds = data.embeds`,
  then auto-scrolls to `#${message_id}-embeds-container`.

### 2c. Two-message arrangement for "below prose" — FEASIBLE, exact recipe

To put a widget **below** the prose, append a **second assistant message** and
attach the embed to it:

1. `GET /api/v1/chats/{id}` → read `chat.history`; `PARENT_ID =
   history.currentId` (the prose assistant message).
2. `NEW_ID = uuid4()`. `POST /api/v1/chats/{id}` (`ChatForm`, i.e. body
   `{"chat": { "history": { "messages": { "<NEW_ID>": {...} }, "currentId":
   "<NEW_ID>" }, "models": [...] }}`). The synthetic assistant node needs:
   `id`, `parentId=PARENT_ID`, `role:"assistant"`, `content:""` (or a short
   caption), `model`, and **`done:true`**; `childrenIds` is rebuilt by
   `merge_history` and `timestamp` is optional.
   - `models/chats.py:254-257` (`ChatForm.chat: dict` — unvalidated),
     `:803-855` (`update_chat_by_id` merges history and upserts every incoming
     message with a truthy `role`), `:1008-1031` (`merge_history` rebuilds
     `childrenIds`).
   - Frontend builds the same node shape: `Chat.svelte:3290-3305`.
3. `POST /api/v1/chats/{id}/messages/{NEW_ID}/event` with the embeds payload.

Caveats confirmed in source: `role` is mandatory (`chat_message.role` NOT NULL,
`models/chat_messages.py:139`); `done:true` avoids the unfinished-assistant
path (`models/chats.py:824-831`, `chat_messages.py:326`); `model` avoids a
nameless header (`ResponseMessage.svelte:190-191`); `POST /{id}` is
**owner-only** (`routers/chats.py:1454`); there is **no single-message append
endpoint** — `POST /{id}/messages/{message_id}` only edits an existing message
(`routers/chats.py:1490-1497`). `Chats.update_chat_by_id` swallows exceptions
and can return `None`, so the client must verify the new message is present in
the response.

**Risk from PLAN.md is resolved:** two-message placement **is** feasible via
the public REST API. No custom frontend reorder needed.

### 2d. `input:prompt:submit` from message-level embeds

**CONFIRMED (source).** `Chat.svelte` registers `window.addEventListener('message',
onMessageHandler)` (`:1843-1846`); the handler (`:1732`) treats
`input:prompt:submit` as trusted when `isSameOrigin || isEmbedWindow(event.source)
|| settings.iframeSandboxAllowSameOrigin` (`:1737-1755`).

- Same-origin → immediate `submitHandler(text)`.
- **Own cross-origin embed** (any `FullHeightIframe`, which is what message
  embeds use) → shows the **"Confirm Prompt from Embed"** dialog, then submits
  on confirm (`:1790-1808`). `FullHeightIframe` registers its `contentWindow`
  in a `Set` (`FullHeightIframe.svelte:2-5,185-192`), default `allowSameOrigin
  = false` (opaque origin).
- Untrusted external cross-origin window → **silently dropped**, no dialog.
- `input:prompt:insert` and `input:message:submit` **do not exist** in
  v0.12.2; only `input:prompt` (insert-only) and `input:prompt:submit`.
- **Bug #26912 is fixed in v0.12.2**: the `isEmbedWindow` identity trust path
  is present, so OWUI's own opaque-origin embeds reach the confirm dialog.

The PLAN.md assumption ("`input:prompt:submit` from cross-origin embeds shows a
confirm dialog ... message-level embeds must be verified in Phase 0") is
**confirmed at source**. Live verification (persistence across reload in the
browser + the confirm-dialog click-through) is *(blocked)* on
`~/.openwebui_key`, because the embed setup itself requires authenticated REST
calls; without the key no embed can be created to observe.

### Open question surfaced for Phase 2 — where does the wrapper HTML live? (resolved Phase 3)

Embeds are **iframe `src` URLs**, not inline HTML. The bridge must serve the
OpenUI wrapper document at a URL the browser can frame. Candidates: a `data:`
URL (self-contained; allowed by the Phase 3 CSP `data: blob:`), an Open
WebUI-served static asset (installer-only write via `setup_openwebui.py`), or a
bridge URL (note: `default-src 'self'` in `IFRAME_CSP` would **not** allow
`172.17.0.1:8790`). **Resolved in Phase 3:** the wrapper is an Open WebUI static
asset (same-origin, no new port, no CDN), generated by `setup_openwebui.py`.
Discovery during Phase 3: Open WebUI's `FullHeightIframe` only treats
`http(s)://` / `//` as a URL, so a `data:` embed renders as literal text — the
static asset is required, not just preferred. The payload rides in the URL
fragment (`widget.html#<base64url payload>`); the pinned bundle is self-hosted
beside it.

---

## Spike 3 — bundle pinning and hosting

**Decision: pin and self-host** (repo network posture: loopback-only, no CDN).

- `@openuidev/browser-bundle` latest is **0.2.1** (published 2026-10-15),
  **MIT** (© Thesys Inc.). Dist is two static files: `dist/openui-bundle.min.js`
  (measured from dist @0.2.1: ~3.23 MB raw / **~873 KB gzip**; the package
  README rounds to ~900 KB) and `dist/openui-styles.css` (~397 KB raw / **~38 KB
  gzip**; README rounds to ~35 KB), IIFE exposing `window.__OpenUI`.
- It is **trivially self-hostable**: both files can be dropped into Open WebUI
  static storage; no runtime fetches beyond those two files.
- The thesys plugin defaults to **`@latest`** (`tool.py:125`), which can
  auto-upgrade to a breaking `0.3+`. The package README recommends pinning
  **`@0.2`**. We pin the exact **0.2.1**.
- The plan's "~650KB gzipped" estimate was low; the real JS gzip is ~873 KB
  (first load, browser-cached after).

**Decision:** self-host `openui-bundle.min.js` + `openui-styles.css` at a
pinned version (0.2.1) via the installer, not jsDelivr. No `IFRAME_CSP`
allowlist for a CDN origin is needed.

---

## Spike 4 — license of thesysdev/openwebui-plugin

**BLOCKER for the plan as written.** `thesysdev/openwebui-plugin` has **no
LICENSE** file and GitHub reports `license: null`; `tool.py` carries no
license/copyright header. With no grant, redistribution/modification is **not
permitted** — we **must not vendor** `tool.py` as PLAN.md Phase 2 proposed.

Everything it depends on is MIT: `@openuidev/browser-bundle`,
`@openuidev/react-ui` / `react-lang` / `lang-core` / `react-headless`, and the
canonical `thesysdev/openui` spec repo (MIT © Thesys Inc.).

**Decision (plan delta):** write our **own** thin wrapper against the OpenUI
Lang spec (MIT) and the MIT bundle. We may still *read* the plugin to learn the
rendering contract (bundle global shape, `iframe:height` reporting,
`sendPrompt` → `{type:'input:prompt:submit', text}`), but the code must be ours.
Attribution is welcome but the license problem is not solvable by attribution
alone. PLAN.md Phase 2 wording ("vendored thesys `tool.py` HTML shell
(attributed)") must change to "our own wrapper, inspired by the plugin's
rendering contract".

---

## Spike outcome vs PLAN.md "done criteria"

| Criterion | Result |
|---|---|
| Placement below via two-message | **Confirmed feasible** at source; live write test *(blocked)* on `~/.openwebui_key` |
| Persistence across reload | **Confirmed** at source (`chat_messages.embeds` column) |
| Follow-up submit from message-level embeds | **Confirmed** at source (own-embed trust → confirm dialog); #26912 fixed |
| Artifact trigger on ` ```html ` in a long message | **Confirmed**, no threshold, prose-independent |
| Bundle pinned / no CDN | **Resolved** — self-host 0.2.1 |
| License check | **Resolved** — do NOT vendor the plugin; write our own wrapper |

## Plan deltas required

1. **Phase 2 license:** replace "vendored thesys `tool.py` HTML shell
   (attributed)" with an original wrapper built against the OpenUI Lang spec +
   MIT bundle. No code copied from the unlicensed plugin.
2. **Phase 2/3 hosting:** embeds are URLs → define where the wrapper HTML is
   served (recommend an Open WebUI static asset written by
   `setup_openwebui.py`); record it in `infra/VERSIONS.md`.
3. **Phase 3 bundle size:** update the anticipated first-load size (~873 KB
   gzip JS + ~38 KB gzip CSS at 0.2.1), and pin 0.2.1 rather than `@latest`.
4. **Phase 2 REST client:** the bridge needs an Open WebUI API key; add
   provisioning of `~/.openwebui_key` to the deploy docs/`setup_openwebui.py`
   flow. (`~/.openwebui_key` does not exist on this host today.)

## To finish the live spike

Provide an Open WebUI API key at `~/.openwebui_key` (Settings → Account → API
Keys), host the example wrapper document, and run (a `data:` embed renders as
text in v0.12.2, so the document must be served):

```sh
python3 docs/plans/intelligent-ui/spike_embeds_live.py --print-html > embed.html
python3 docs/plans/intelligent-ui/spike_embeds_live.py \
  --base-url http://127.0.0.1:3000 --widget-url http://127.0.0.1:3000/static/embed.html
```

It creates a synthetic chat with two assistant messages, attaches an embed to
the second, verifies persistence via `GET`, and prints the chat URL plus a
widget containing a follow-up button to click. See the script's `--help`.
