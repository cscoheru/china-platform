#!/usr/bin/env python3
"""Gen /public-extracts four-track CSV downloads (tasking 403 / knife 70).

Deterministically renders the 4 existing frontend fixtures as CSV into
frontend/public/public-extracts/ (committed static products):

  nbs.csv               <- frontend/lib/public_extract_nbs.json
  nbs-live-candidate.csv<- frontend/lib/public_extract_nbs_live_candidate.json
  sz.csv                <- frontend/lib/public_extract_sz.json
  hubei.csv             <- frontend/lib/public_extract_hubei.json

Contract (per 403 §SCHEMA-1 + §红线):
  - 列序 = fixture 首行键序 (json.load 保序 == page Object.keys(rows[0]));
    不重命名、不重排、不 reinterpret; 空键 (湖北未命名列) 原样保留.
  - 行数 = fixture row_count (CSV 数据行与 fixture rows 一一对应).
  - 单元格值 = row.get(key, "") (与页面 {row[key] ?? ""} 同语义).
  - UTF-8 无 BOM, 换行 \n, csv.QUOTE_MINIMAL — 字节确定性 (重跑同字节).
  - 只读 fixture; 不改 fixture JSON 字节; 无服务端动态导出 (静态文件).

Demo gate: CSV 与 JSON 一样是 fixture 快照导出 (demo/candidate),
非权威库、非 O1 收口.
"""
from __future__ import annotations

import csv
import io
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIB_DIR = ROOT / "frontend" / "lib"
OUT_DIR = ROOT / "frontend" / "public" / "public-extracts"

# name -> lib fixture path (与 knife 65 public JSON 命名一致)
FIXTURES: dict[str, pathlib.Path] = {
    "nbs": LIB_DIR / "public_extract_nbs.json",
    "nbs-live-candidate": LIB_DIR / "public_extract_nbs_live_candidate.json",
    "sz": LIB_DIR / "public_extract_sz.json",
    "hubei": LIB_DIR / "public_extract_hubei.json",
}


def render_csv_bytes(fixture: dict) -> bytes:
    """Pure: fixture dict -> deterministic CSV bytes (UTF-8, \\n, QUOTE_MINIMAL)."""
    rows = fixture["rows"]
    keys = list(rows[0].keys()) if rows else []
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(keys)
    for row in rows:
        writer.writerow([row.get(key, "") for key in keys])
    return buf.getvalue().encode("utf-8")


def main() -> int:
    wrote = 0
    for name, fixture_path in sorted(FIXTURES.items()):
        if not fixture_path.is_file():
            print(f"ERR: fixture missing: {fixture_path}", file=sys.stderr)
            return 1
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        data = render_csv_bytes(fixture)
        out_path = OUT_DIR / f"{name}.csv"
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)
        n_rows = len(fixture["rows"])
        print(
            f"WROTE {out_path.relative_to(ROOT)} "
            f"({len(data)} bytes, {n_rows} data rows + header)"
        )
        wrote += 1
    print(f"OK wrote {wrote} CSVs (deterministic; rerun yields identical bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
