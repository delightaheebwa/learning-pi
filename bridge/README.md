# pi-bridge

An OpenAI-compatible endpoint in front of the pinned pi runtime, so **Open WebUI
can be the face while pi stays the brain** (the learning-gate, subagents, and
skills run unchanged; Open WebUI holds only chat transcripts).

```
Open WebUI (Docker, this machine)
      │  OpenAI API  (http://127.0.0.1:8790/v1)
   pi-bridge  ── one `pi --mode rpc` process per chat
      │
   pi runtime (learning-gate withholds turns before emission)
      │
   the real machine: state repo, files, shell
```

## Why it is shaped this way (Phase 0 spike findings)

* Assistant text is taken **only** from `message_end`. `message_update` deltas
  carry the raw, *pre-verification* draft — the spike watched a withheld teaching
  draft stream in full before the gate replaced it. The bridge never forwards
  deltas, so unverified content cannot leak to the learner.
* A withheld turn already arrives as a `⛔ WITHHELD (…)` banner inside the
  `message_end` text, so the learner sees the gate's verdict with no extra wiring.
* Sessions run with `--bash-guard-disabled` (only when bash-guard is installed):
  routine commands (including `git status`) pass, while the catastrophic floor
  (`rm -r/-rf`, `sudo`, `curl|sh`, `mkfs*`, `dd of=/dev/…`, disk/power tools,
  `git reset --hard`, …) stays blocked — bash-guard's default in a headless
  session blocks even read-only `git`, which would make computer use unusable.
* One pi session per chat; only the **newest** user message is forwarded (pi owns
  its context). A resend of the same message is treated as a regenerate and forks
  the session back to that user message first.

## Run

```sh
# key: --api-key, $PI_BRIDGE_API_KEY, or ~/.pi-bridge-key
python3 -m bridge --port 8790 --state-repo ~/learning-system
```

In Open WebUI: **Settings → Connections → +** (OpenAI API). The Base URL must be
one a container can reach — for the default Docker bridge network bind the
bridge to that interface and use `http://172.17.0.1:8790/v1`, or run Open WebUI
with `--network host` and use `http://127.0.0.1:8790/v1`. (A bridge bound to
`127.0.0.1` is **not** reachable from a normal container via
`host.docker.internal` on Linux.) Set the API key to your bridge key, then pick
the `learning` model.

Options: `--host/--port`, `--models a,b,c`, `--timeout`, `--max-sessions`,
`--agent-dir`, `--session-dir`, `--ledger-dir`, `--allow-bash-guard` (do **not**
pass `--bash-guard-disabled`; not recommended headless).

## Single-writer policy

The learning system forbids two concurrent writers on the state repo. The bridge
holds a learning lock for the duration of each learning turn and releases it when
the turn ends, so concurrent learning turns — including two from the same chat —
cannot overlap; a second chat that starts a learning turn meanwhile is told to
wait. General (non-learning) chats are exempt. Idle pi sessions are evicted LRU
(`--max-sessions`).

## Limits

* Tool activity is buffered with the turn (no live status lines yet) — the turn
  arrives whole, which matches "generated then verified then emitted".
* Regenerate uses `fork`; if pi cannot fork, the bridge falls back to appending
  the prompt.
* Interactive extension UI (approval dialogs) is declined, not surfaced.

## Tests

`python3 -m unittest discover -s test/bridge` — deterministic, uses a fake pi
(`test/bridge/fake_pi.py`); no models or network.
