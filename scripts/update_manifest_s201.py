"""Stage 2 / S2.0.1 — Update evidence_pack/manifest.json.

Per tasking 146 §SCHEMA: "补 docs/34 入 evidence_pack（+1 documentation）；
本刀新文件同步计 role".

Approach for this刀:
  - +1 documentation: docs/34 (Cursor 145 audit explicitly called out this gap)
  - +1 schema_negative_test: tests/test_s201_skeleton_smoke.py (5 pytest cases)
  - Frontend skeleton code files (frontend/*.ts, frontend/app/*.tsx etc.) are
    NOT enumerated in role_count in this刀. Future S2.1 will introduce a
    'frontend_skeleton' role and backfill them.

Resulting pack invariant:
  artifact_count: 504 → 506 (+2)
  role_count.documentation: 36 → 37 (+1)
  role_count.schema_negative_test: 18 → 19 (+1)
  len(artifacts): 504 → 506 (+2)
  sum(role_count): 504 → 506 (+2)
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

    docs34_path = ROOT / "docs" / "34-stage2-s20-kickoff-plan-20260825.md"
    smoke_path = ROOT / "tests" / "test_s201_skeleton_smoke.py"

    docs34_entry = {
        "path": "docs/34-stage2-s20-kickoff-plan-20260825.md",
        "size_bytes": docs34_path.stat().st_size,
        "sha256": sha256(docs34_path),
        "role": "documentation",
    }
    smoke_entry = {
        "path": "tests/test_s201_skeleton_smoke.py",
        "size_bytes": smoke_path.stat().st_size,
        "sha256": sha256(smoke_path),
        "role": "schema_negative_test",
    }

    # Insert at alphabetical position (preserve ordering convention).
    # docs/34 sits after docs/33; tests/test_s201_ sits before tests/test_acceptance.
    new_artifacts: list[dict] = []
    docs34_inserted = False
    smoke_inserted = False
    for a in m["artifacts"]:
        # docs/34 alphabetical ordering: docs/33 < docs/34 < docs/4 ...
        if (
            not docs34_inserted
            and a["path"].startswith("docs/")
            and a["path"] > "docs/34-stage2-s20-kickoff-plan-20260825.md"
            and a["path"] < "docs/35"
        ):
            new_artifacts.append(docs34_entry)
            docs34_inserted = True
        if (
            not smoke_inserted
            and a["path"].startswith("tests/")
            and a["path"] > "tests/test_s201_skeleton_smoke.py"
        ):
            new_artifacts.append(smoke_entry)
            smoke_inserted = True
        new_artifacts.append(a)

    if not docs34_inserted:
        new_artifacts.append(docs34_entry)
    if not smoke_inserted:
        new_artifacts.append(smoke_entry)

    m["artifacts"] = new_artifacts
    m["artifact_count"] = len(new_artifacts)
    m["role_count"]["documentation"] += 1
    m["role_count"]["schema_negative_test"] += 1

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
    print(f"   - documentation: {m['role_count']['documentation']} (+1 docs/34)")
    print(f"   - schema_negative_test: {m['role_count']['schema_negative_test']} (+1 test_s201_skeleton_smoke)")
    return 0


if __name__ == "__main__":
    sys.exit(main())