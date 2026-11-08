#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

FAIL_TYPES = {"Delete", "Ignore", "Unsupported", "Deploy"}
ALLOW_TYPES = {"Create", "Modify", "NoChange"}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: evaluate_whatif.py <whatif-json-path>")
        return 2

    path = Path(sys.argv[1]).resolve()
    if not path.exists():
        print(f"what-if output not found: {path}")
        return 1

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Cannot read what-if output: {exc}", file=sys.stderr)
        return 1
    if (not isinstance(data, dict) or not isinstance(data.get("changes"), list)
            or data.get("error") or data.get("status", "Succeeded") != "Succeeded"):
        print("Expected a successful what-if result with a changes array.", file=sys.stderr)
        return 1
    changes = data["changes"]

    fail = []
    for change in changes:
        if not isinstance(change, dict):
            print("Invalid what-if change entry.", file=sys.stderr)
            return 1
        change_type = change.get("changeType")
        resource_id = change.get("resourceId")
        if not isinstance(resource_id, str) or not resource_id:
            print("What-if change is missing a resourceId.", file=sys.stderr)
            return 1
        if change_type in FAIL_TYPES or change_type not in ALLOW_TYPES:
            fail.append({"resourceId": resource_id, "changeType": change_type})

    print(json.dumps({"fail": fail, "count": len(changes)}, indent=2))

    if fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
