#!/usr/bin/env python3
"""Spike 00 — 省级统计年鉴表 提取器（R3-D 重写）

样本：湖北省统计局《湖北统计年鉴 2025》ZIP 原件 → 第 01 章 综合 / 0109-地区生产总值.xls

R3-D 约束（per Codex Gate 0 决定）：
  1. tracked ZIP 为唯一默认输入；不得依赖 gitignored 预解压 XLS
  2. 解压使用 TemporaryDirectory；写入磁盘位置 = tempfile 系统临时目录
  3. 防 zip-slip：解压时检查 resolve() 是否在临时目录内；禁止绝对路径 / 越界
  4. 自动定位 0109-*.xls：按章节前缀+文件名前缀在 ZIP 内递归搜索
  5. clean clone 缺 ZIP 时 fail（exit != 0），不得 skip

设计要点（per PRD §3 + Stage 0 评审 B-08）：
  * 逐行血缘：sheet / row / col 定位；行范围；脚注引用
  * 保留原始单元格文本（raw_value）
  * 缺失值用 null + missing_reason，绝不补零
  * 包含 methodology caveat 与单位
  * confidence=1.0（机器可读 xls），但缺失行 / 跳过行 confidence 强制进复核队列
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import xlrd  # 仅 .xls；.xlsx 走 openpyxl

MISSING_CHARS = {"…", "—", "－", "-", ""}  # 包含半角/全角破折号、省略号、空串


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_extract_member(zf: zipfile.ZipFile, member: zipfile.ZipInfo, target_dir: Path) -> Path:
    """R3-D-3: 防 zip-slip 解压。

    校验：
      - 解压目标绝对路径必须仍在 target_dir 内（resolve() 后字符串前缀匹配）
      - 不允许 absolute path / .. / 驱动器字母
    """
    raw_name = member.filename
    # 禁止绝对路径 / 越界 / 反斜杠
    if raw_name.startswith("/") or raw_name.startswith("\\"):
        raise ValueError(f"zip-slip: absolute path entry {raw_name!r}")
    if ".." in raw_name.split("/"):
        raise ValueError(f"zip-slip: relative-parent entry {raw_name!r}")
    if re.match(r"^[A-Za-z]:", raw_name):
        raise ValueError(f"zip-slip: drive-letter entry {raw_name!r}")

    target_path = (target_dir / raw_name).resolve()
    target_dir_resolved = target_dir.resolve()
    # 确保 target_path 仍在 target_dir 内
    try:
        target_path.relative_to(target_dir_resolved)
    except ValueError:
        raise ValueError(f"zip-slip: {raw_name!r} escapes {target_dir_resolved}")

    if member.is_dir():
        target_path.mkdir(parents=True, exist_ok=True)
        return target_path

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(member) as src, open(target_path, "wb") as dst:
        while True:
            chunk = src.read(65536)
            if not chunk:
                break
            dst.write(chunk)
    return target_path


def locate_0109_in_zip(zip_path: Path, target_dir: Path) -> tuple[Path, dict]:
    """R3-D-4: 在 ZIP 内自动定位 0109-*.xls。

    匹配规则（按优先级）：
      1. 文件名以 "0109-" 开头 + 以 ".xls" 结尾
      2. 文件名以 "0109" 开头（无连字符）+ 以 ".xls" 结尾
    返回：解压后的路径 + 解压统计信息
    """
    with zipfile.ZipFile(zip_path) as zf:
        # 遍历 namelist，先全匹配后宽松匹配
        candidates_strict = [m for m in zf.infolist()
                             if not m.is_dir()
                             and Path(m.filename).name.startswith("0109-")
                             and m.filename.lower().endswith(".xls")]
        candidates_loose = [m for m in zf.infolist()
                            if not m.is_dir()
                            and Path(m.filename).name.startswith("0109")
                            and m.filename.lower().endswith(".xls")]
        candidates = candidates_strict or candidates_loose

        if not candidates:
            raise FileNotFoundError(
                f"未在 {zip_path.name} 内找到 0109*.xls "
                f"(checked {len(zf.namelist())} entries)"
            )
        # 选第一个匹配（确定性：按文件名排序）
        candidates.sort(key=lambda m: m.filename)
        chosen = candidates[0]

        # 解压（防 zip-slip）
        extracted_path = safe_extract_member(zf, chosen, target_dir)
        return extracted_path, {
            "zip_entry_name": chosen.filename,
            "zip_entry_size": chosen.file_size,
            "zip_entry_compressed_size": chosen.compress_size,
            "zip_entry_crc": chosen.CRC,
            "n_candidates": len(candidates),
        }


def classify_cell(raw: Any) -> dict:
    """把 xlrd 单元格值归类为 value/missing 或脚注/标题。
    返回：{value: float|None, raw_value: str, is_missing: bool, missing_reason: str|None}"""
    if isinstance(raw, str):
        text = raw.strip()
        if text in MISSING_CHARS:
            return {
                "value": None,
                "raw_value": raw,
                "is_missing": True,
                "missing_reason": "NOT_PUBLISHED",
            }
    try:
        v = float(raw)
        if v != v:  # NaN
            return {
                "value": None,
                "raw_value": str(raw),
                "is_missing": True,
                "missing_reason": "NOT_PUBLISHED",
            }
        return {"value": v, "raw_value": str(raw), "is_missing": False, "missing_reason": None}
    except (TypeError, ValueError):
        return {
            "value": None,
            "raw_value": str(raw),
            "is_missing": True,
            "missing_reason": "TEXT_OR_NOTE",
        }


def detect_methodology_caveat(rows: list[list]) -> str | None:
    """寻找 R3 之类位置的单位/价格口径说明。"""
    for r in rows[:6]:
        for cell in r:
            if isinstance(cell, str) and "价格" in cell:
                return cell.strip()
    return None


def extract_year_rows(
    path: Path,
    data_start_row: int,
    year_col: int = 0,
    column_definitions: dict | None = None,
) -> list[dict]:
    """从指定行开始提取 (year, value_dict) 列表。"""
    wb = xlrd.open_workbook(str(path))
    sh = wb.sheet_by_index(0)
    out = []
    for r in range(data_start_row, sh.nrows):
        year_cell = sh.cell_value(r, year_col)
        # 注释行（包含 "注："）
        if isinstance(year_cell, str) and ("注" in year_cell or "Note" in year_cell):
            break
        # 列名/合计行（年单元格非数字且非纯整数）
        if not _looks_like_year(year_cell):
            continue
        try:
            year = int(float(year_cell))
        except (TypeError, ValueError):
            continue
        row_data: dict[str, Any] = {
            "row_locator": f"A{r + 1}",
            "year": year,
            "columns": {},
        }
        for c in range(year_col + 1, sh.ncols):
            cls = classify_cell(sh.cell_value(r, c))
            col_label = xlrd.colname(c)
            cell_key = f"{col_label}{r + 1}"
            col_def = column_definitions.get(col_label, {})
            row_data["columns"][cell_key] = {
                **cls,
                "cell_locator": cell_key,
                "indicator_alias": col_def.get("indicator_alias", cell_key),
                "unit": col_def.get("unit", ""),
            }
        out.append(row_data)
    return out


def _looks_like_year(v: Any) -> bool:
    if isinstance(v, (int, float)):
        return 1900 <= float(v) <= 2100
    if isinstance(v, str):
        s = v.strip()
        if s.isdigit():
            return 1900 <= int(s) <= 2100
    return False


def extract_notes(path: Path, after_row: int) -> list[str]:
    wb = xlrd.open_workbook(str(path))
    sh = wb.sheet_by_index(0)
    notes = []
    for r in range(after_row, sh.nrows):
        text = sh.cell_value(r, 0)
        if isinstance(text, str) and text.strip():
            notes.append(text.strip())
    return notes


def extract(xls_path: Path, source_zip_info: dict | None = None) -> dict:
    """主提取函数。

    source_zip_info: 若传入，则记录 ZIP entry 信息（用于 provenance）。
    """
    file_hash = sha256_file(xls_path)
    file_size = xls_path.stat().st_size
    wb = xlrd.open_workbook(str(xls_path))
    sh = wb.sheet_by_index(0)

    # 头部行（前 9 行）
    header_rows = []
    for r in range(min(10, sh.nrows)):
        header_rows.append([sh.cell_value(r, c) for c in range(sh.ncols)])

    title_row = header_rows[0][0] if header_rows else ""
    en_title = header_rows[1][0] if len(header_rows) > 1 else ""
    methodology = detect_methodology_caveat(header_rows)

    # 列定义（用 rows 4-9 推断）—— 必须在 extract_year_rows 之前
    column_definitions = _build_column_definitions(header_rows)

    year_rows = extract_year_rows(
        xls_path,
        data_start_row=10,
        year_col=0,
        column_definitions=column_definitions,
    )
    notes = extract_notes(xls_path, after_row=sh.nrows - 3)

    # 构建 provenance（R3-D：包含 ZIP 原件 + entry 信息）
    source_doc = {
        "title": title_row.strip(),
        "english_title": en_title.strip() if isinstance(en_title, str) else "",
        "publisher": "湖北省统计局 / Hubei Provincial Bureau of Statistics",
        "publication_date": "2025-12-31",
        "url": "http://tjj.hubei.gov.cn/tjsj/sjkscx/tjnj/qstjnj/",
        "file_name": xls_path.name,
        "file_hash_sha256": file_hash,
        "file_size_bytes": file_size,
        "extraction_method": "EXCEL_PARSE",
        "language": "zh+en",
    }
    if source_zip_info:
        source_doc["zip_entry"] = source_zip_info

    # observation 列表（含缺失值）
    observations = []
    for row in year_rows:
        year = row["year"]
        for cell_key, cell in row["columns"].items():
            col_letter = cell_key[0]
            col_def = column_definitions.get(col_letter, {})
            obs = {
                "indicator_canonical": col_def.get("canonical_indicator", "地区生产总值"),
                "indicator_alias": col_def.get("indicator_alias", cell_key),
                "period_year": year,
                "period_label": f"{year}",
                "period_type": "YEAR",
                "unit": cell.get("unit") or col_def.get("unit", "亿元"),
                "value": cell["value"],
                "raw_value": cell["raw_value"],
                "is_missing": cell["is_missing"],
                "missing_reason": cell["missing_reason"],
                "comparison_basis": "NOMINAL",
                "value_type": "FACT",
                "status": "PRELIMINARY" if year >= 2024 else "FINAL",
                "source_document": source_doc,
                "source_location": {
                    "sheet_name": "Sheet1",
                    "row_locator": row["row_locator"],
                    "cell_locator": cell["cell_locator"],
                },
                "methodology_caveat": methodology,
                "footnote_references": [n[:60] + ("…" if len(n) > 60 else "") for n in notes],
                "confidence": 1.0,  # 机器可读
                "needs_review": cell["is_missing"],
                # 锁定而非 datetime.now()：deterministic rebuild 需要字节稳定
                # （B-07/I-01，同 spike 02/04 修法）。
                "extracted_at": "2026-08-23T10:30:00Z",
                "extractor_version": "spike00-provincial-yearbook/2.0-R3D",
            }
            observations.append(obs)

    return {
        "metadata": {
            "spike": "00-provincial-yearbook-table",
            "extractor": "spike00-provincial-yearbook/2.0-R3D",
            "sample": {
                "title": title_row.strip(),
                "publisher": "湖北省统计局 / Hubei Provincial Bureau of Statistics",
                "yearbook_year": 2025,
                "file_name": xls_path.name,
                "file_hash_sha256": file_hash,
                "file_size_bytes": file_size,
                "sheet_name": sh.name,
                "n_rows": sh.nrows,
                "n_cols": sh.ncols,
            },
            "headers_rows_0_to_9": header_rows,
            "methodology_caveat": methodology,
            "column_definitions": column_definitions,
            "n_observations": len(observations),
            "n_missing": sum(1 for o in observations if o["is_missing"]),
            "extracted_at": "2026-08-23T10:30:00Z",
        },
        "observations": observations,
        "notes": notes,
    }


def _build_column_definitions(header_rows: list[list]) -> dict:
    """基于湖北年鉴 1-9 表的实际列结构生成列定义（按列字母 B/C/...）。
    列：B=GDP(亿元) / C=Primary / D=Secondary / E=Industry / F=Construction /
        G=Tertiary / H=Banking / I=Real Estate / J=Per Capita GDP(yuan) / K=Per Capita GDP(USD)
    """
    return {
        "B": {"canonical_indicator": "地区生产总值", "indicator_alias": "GDP", "unit": "亿元"},
        "C": {"canonical_indicator": "地区生产总值构成", "indicator_alias": "第一产业", "unit": "亿元"},
        "D": {"canonical_indicator": "地区生产总值构成", "indicator_alias": "第二产业", "unit": "亿元"},
        "E": {"canonical_indicator": "地区生产总值构成", "indicator_alias": "工业", "unit": "亿元"},
        "F": {"canonical_indicator": "地区生产总值构成", "indicator_alias": "建筑业", "unit": "亿元"},
        "G": {"canonical_indicator": "地区生产总值构成", "indicator_alias": "第三产业", "unit": "亿元"},
        "H": {"canonical_indicator": "地区生产总值构成", "indicator_alias": "金融业", "unit": "亿元"},
        "I": {"canonical_indicator": "地区生产总值构成", "indicator_alias": "房地产业", "unit": "亿元"},
        "J": {"canonical_indicator": "人均地区生产总值", "indicator_alias": "Per Capita GDP CNY", "unit": "元"},
        "K": {"canonical_indicator": "人均地区生产总值", "indicator_alias": "Per Capita GDP USD", "unit": "美元"},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--zip",
        type=Path,
        default=None,
        help="ZIP 原件路径（不传则用内置默认 data/hubei_2025_yearbook.zip）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="输出 JSON 路径（默认 data/extracts/00-provincial-yearbook-table/extracted.json）",
    )
    args = parser.parse_args()

    # R3-D-1: tracked ZIP 为唯一默认输入
    if args.zip is None:
        args.zip = Path(__file__).parent / "data" / "hubei_2025_yearbook.zip"

    # R3-D-5: clean clone 缺 ZIP 时 fail
    if not args.zip.exists():
        print(f"ERROR: ZIP 原件不存在: {args.zip}", file=sys.stderr)
        print("  R3-D 要求 clean clone 时 tracked ZIP 必须存在。", file=sys.stderr)
        print("  若 ZIP 缺失，本脚本必须 fail 而非 skip。", file=sys.stderr)
        return 2

    zip_hash = sha256_file(args.zip)
    zip_size = args.zip.stat().st_size

    # R3-D-2/3: TemporaryDirectory + 防 zip-slip 解压
    with tempfile.TemporaryDirectory(prefix="spike00_zip_") as tmp:
        tmp_dir = Path(tmp)
        try:
            xls_path, zip_entry_info = locate_0109_in_zip(args.zip, tmp_dir)
        except (FileNotFoundError, ValueError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 3

        # 在临时目录解压后提取
        result = extract(xls_path, source_zip_info=zip_entry_info)

    # 添加入口 provenance
    result["metadata"]["source_zip"] = {
        "zip_file_name": args.zip.name,
        "zip_sha256": zip_hash,
        "zip_size_bytes": zip_size,
    }

    if args.output is None:
        args.output = (
            Path(__file__).resolve().parents[2] / "data" / "extracts" /
            "00-provincial-yearbook-table" / "extracted.json"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"OK: 写入 {args.output}")
    print(f"  observations: {result['metadata']['n_observations']}")
    print(f"  missing:      {result['metadata']['n_missing']}")
    print(f"  source zip:   {args.zip.name} (sha256={zip_hash[:16]}…)")
    print(f"  zip entry:    {result['metadata']['source_zip']['zip_file_name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())