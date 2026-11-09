# Security Policy

## Supported versions

This is a personal, continuously evolving project. Only the latest commit on
`main` is supported. There are no maintained release branches.

## Reporting a vulnerability

Please **do not** report security vulnerabilities through public issues or
discussions.

Use GitHub's private vulnerability reporting:

1. Go to the **Security** tab of
   [`delightaheebwa/learning-system`](https://github.com/delightaheebwa/learning-system/security).
2. Click **Report a vulnerability**.
3. Describe the issue, the impact, and a reproduction if you have one.

If private reporting is unavailable, contact the maintainer via their GitHub
profile ([@delightaheebwa](https://github.com/delightaheebwa)).

## What to include

- Affected component (installer, gate Filter, `ops.py`, a skill, the pi layer).
- Reproduction steps or a proof of concept.
- Impact — what an attacker gains.
- Any suggested fix.

## Scope

In scope:

- The Python installer and gate Filter (`scripts/`, `Skills/learning-review/openwebui/`).
- `scripts/ops.py` and the pi-layer scripts.

Out of scope:

- Vulnerabilities in third-party dependencies or in upstream
  [Open WebUI](https://github.com/open-webui/open-webui) itself — report those
  upstream.
- The public, non-sensitive contents of this repo (skills, docs, learning notes).

## Disclosure

Please give a reasonable window to investigate and ship a fix before public
disclosure. You will be credited unless you ask otherwise.
