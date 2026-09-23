#!/usr/bin/env python3
"""versions.lock.json helper for pi-safe-update. Stdlib only.

Subcommands:
    get LOCK pi                 -> current pinned pi version
    get LOCK pkg NAME           -> pinned version of one package
    packages LOCK               -> name=version lines (all packages)
    promote LOCK ACTION PIFROM PITO PKGFROM_JSON PKGTO_JSON
                                merge pi/packages, append a journal entry
    last-promotion LOCK         -> JSON of the last journal entry
"""
from __future__ import annotations

import datetime
import json
import sys


def load(path: str) -> dict:
    return json.load(open(path, encoding="utf-8"))


def save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def cmd_get(path: str, key: str) -> None:
    d = load(path)
    if key == "pi":
        print(d.get("pi", ""))
    else:
        print((d.get("packages") or {}).get(key, ""))


def cmd_packages(path: str) -> None:
    d = load(path)
    for name, ver in (d.get("packages") or {}).items():
        print(f"{name}={ver}")


def cmd_promote(path: str, action: str, pi_from: str, pi_to: str, pkg_from: str, pkg_to: str) -> None:
    d = load(path)
    if pi_to:
        d["pi"] = pi_to
    pkg_from_map = json.loads(pkg_from) if pkg_from else {}
    pkg_to_map = json.loads(pkg_to) if pkg_to else {}
    if pkg_to_map:
        d.setdefault("packages", {})
        d["packages"].update(pkg_to_map)
    d.setdefault("journal", []).append(
        {
            "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "action": action,
            "piFrom": pi_from or d.get("pi", ""),
            "piTo": pi_to or d.get("pi", ""),
            "packagesFrom": pkg_from_map,
            "packagesTo": pkg_to_map,
        }
    )
    save(path, d)


def cmd_last_promotion(path: str) -> None:
    d = load(path)
    for e in reversed(d.get("journal") or []):
        if e.get("action") in ("promote", "rollback"):
            print(json.dumps(e))
            return
    print("")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "get":
        cmd_get(path, sys.argv[3])
    elif cmd == "packages":
        cmd_packages(path)
    elif cmd == "promote":
        cmd_promote(path, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
    elif cmd == "last-promotion":
        cmd_last_promotion(path)
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
