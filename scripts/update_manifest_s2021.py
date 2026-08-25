"""Stage 2 / S2.0.2.1 — Update evidence_pack/manifest.json.

Per tasking 157 §SCHEMA.3: + docs/35 + this刀测试（及脚本若入库）.

3 new artifacts:
  - docs/35-stage2-s202-real-sha-probe-plan-20260825.md   → documentation
  - scripts/compute_file_sha.py                           → spike_helper
       (matches existing scripts/seed_jiangsu_gdp_demo.py convention)
  - tests/test_compute_file_sha.py                        → schema_negative_test

Pack invariant after update:
  artifact_count: 506 → 509 (+3)
  role_count.documentation: 37 → 38 (+1)
  role_count.schema_negative_test: 19 → 20 (+1)
  role_count.spike_helper: 7 → 8 (+1)
  sum(role_count) = 38+20+8+... = 509 == artifact_count ✓
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
            "path": "docs/35-stage2-s202-real-sha-probe-plan-20260825.md",
            "role": "documentation",
            "abs": ROOT / "docs/35-stage2-s202-real-sha-probe-plan-20260825.md",
        },
        {
            "path": "scripts/compute_file_sha.py",
            "role": "spike_helper",
            "abs": ROOT / "scripts/compute_file_sha.py",
        },
        {
            "path": "tests/test_compute_file_sha.py",
            "role": "schema_negative_test",
            "abs": ROOT / "tests/test_compute_file_sha.py",
        },
    ]

    artifacts = list(m["artifacts"])
    inserted: set[str] = set()
    for entry in new_entries:
        artifact = {
            "path": entry["path"],
            "size_bytes": entry["abs"].stat().st_size,
            "sha256": sha256(entry["abs"]),
            "role": entry["role"],
        }
        # Insert at alphabetical position relative to existing entries.
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
                inserted.add(entry["path"])
            new_list.append(a)
        if not placed:
            new_list.append(artifact)
            inserted.add(entry["path"])
        artifacts = new_list

    m["artifacts"] = artifacts
    m["artifact_count"] = len(artifacts)
    for entry in new_entries:
        m["role_count"][entry["role"]] = m["role_count"].get(entry["role"], 0) + 1

    # Verify invariant
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