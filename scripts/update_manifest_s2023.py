"""Stage 2 / S2.0.2.3 — Update evidence_pack/manifest.json.

Per tasking 165 §NOW: add tests/test_url_health_probe_live.py
(schema_negative_test). scripts/url_health_probe.py is EDITED in place, so
no new artifact there.

Pack invariant after update:
  artifact_count: 511 → 512 (+1)
  role_count.schema_negative_test: 21 → 22 (+1)
  sum(role_count) = ... = 512 == artifact_count ✓
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence_pack" / "manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))

    new_entries = [
        {
            "path": "tests/test_url_health_probe_live.py",
            "role": "schema_negative_test",
            "abs": ROOT / "tests" / "test_url_health_probe_live.py",
        },
    ]

    artifacts = list(m["artifacts"])
    for entry in new_entries:
        artifact = {
            "path": entry["path"],
            "size_bytes": entry["abs"].stat().st_size,
            "sha256": sha256(entry["abs"]),
            "role": entry["role"],
        }
        new_list: list[dict] = []
        placed = False
        for a in artifacts:
            if (
                not placed
                and a["role"] == entry["role"]
                and a["path"] > entry["path"]
            ):
                new_list.append(artifact)
                placed = True
            new_list.append(a)
        if not placed:
            new_list.append(artifact)
        artifacts = new_list

    m["artifacts"] = artifacts
    m["artifact_count"] = len(artifacts)
    for entry in new_entries:
        m["role_count"][entry["role"]] = m["role_count"].get(entry["role"], 0) + 1

    n = len(m["artifacts"])
    ac = m["artifact_count"]
    rc = sum(m["role_count"].values())
    if not (n == ac == rc):
        print(
            f"❌ invariant broken: len(artifacts)={n}, artifact_count={ac}, "
            f"sum(role_count)={rc}",
            file=sys.stderr,
        )
        return 1

    MANIFEST.write_text(
        json.dumps(m, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"✅ pack updated: artifact_count={ac}, sum(role_count)={rc}, invariant: True")
    for entry in new_entries:
        print(f"   - {entry['role']:>22}: +1 {entry['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
