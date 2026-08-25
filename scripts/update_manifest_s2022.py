"""Stage 2 / S2.0.2.2 — Update evidence_pack/manifest.json.

Per tasking 162 §NOW: add scripts/replace_demo_with_real.py (spike_helper)
+ tests/test_replace_demo_with_real_s2022.py (schema_negative_test).

Pack invariant after update:
  artifact_count: 509 → 511 (+2)
  role_count.spike_helper: 8 → 9 (+1)
  role_count.schema_negative_test: 20 → 21 (+1)
  sum(role_count) = ... = 511 == artifact_count ✓
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
            "path": "scripts/replace_demo_with_real.py",
            "role": "spike_helper",
            "abs": ROOT / "scripts" / "replace_demo_with_real.py",
        },
        {
            "path": "tests/test_replace_demo_with_real_s2022.py",
            "role": "schema_negative_test",
            "abs": ROOT / "tests" / "test_replace_demo_with_real_s2022.py",
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
        # Insert at alphabetical position relative to existing same-role entries.
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
