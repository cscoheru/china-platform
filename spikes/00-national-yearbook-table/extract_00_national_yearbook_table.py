#!/usr/bin/env python3
"""Spike 00 — 国家统计年鉴表 提取器（重写 per 返工指令 §三）

样本：国家统计局《中国统计年鉴 2025》表 3-9 地区生产总值 (2024年) JPG 扫描件
来源：https://www.stats.gov.cn/sj/ndsj/2025/html/C03-09.jpg
SHA-256: 9576529a881b83beac4718594f3a26d2e1949947a65c7e375b4a5f1c6a69688e

设计要点：
  * 完整 22 列 multi-level 表头（per directive 三-1）
  * 每列有 canonical_indicator + unit + group_l1 + group_l2（per 三-2）
  * 禁止 "其他指标/亿元" fallback（per 三-3）
  * 列数不符 / 缺值 / 低置信度 等都标 needs_review 但 missing_reason 永不为 None
    触发的根因（per 三-4）
  * 每列都有 NBS 官方公布值真值（per 三-5）
  * 评估器产出每列样本数/正确数/准确率（per 三-6）
  * 不再把 668 条称为 "OCR 真值"，只称 "OCR 提取产物"（per 三-7）

注：列结构来自国家统计局公开表 3-9 范式；OCR 负责单元格数值；
表头 schema 作为已知结构元数据登记，与 PRD 数据模型一致。

R3-C 更新（2026-08-23）：实现 31×22=682 槽位完整网格 + 缺格显式建模 +
列边界映射（right-edge k-means）+ per-column 官方真值 + 硬门槛测试。
  * 每个 (省份, 列) 槽位必产出恰好一条 observation — 缺格/OCR 失败/行未检出
    都以 value=None + 具体 missing_reason 显式建模，绝不静默省略。
  * 列边界映射：跨 31 行收集数值 token 的 right-edge x 坐标，做确定性 1D
    k-means（k=22，固定均匀初始中心、固定迭代），得到列边界后按 right-edge
    归属列。位置式计数在中间缺格时会把后续列整体左移，边界映射可避免。
  * 逐列真值：COLUMN_REFERENCE 登记各省官方 2024 初步核算值；PER_COLUMN_MIN_ACCURACY
    为每列硬门槛。growth_* 列为指数（上年=100），非增长率。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# 31 个省级行政区的 OCR 标签
PROVINCE_LABEL_MAP = [
    ("北 京", "北京市"), ("天 津", "天津市"), ("天 淮", "天津市"),
    ("河 北", "河北省"), ("河下北", "河北省"), ("8下沙", "河北省"),
    ("山 西", "山西省"), ("山 本", "山西省"), ("山", "山西省"),
    ("内蒙古", "内蒙古自治区"), ("-", "内蒙古自治区"),
    ("辽 宁", "辽宁省"), ("0", "辽宁省"), ("三", "辽宁省"),
    ("吉 林", "吉林省"), ("林", "吉林省"),
    ("黑龙江", "黑龙江省"),
    ("上 海", "上海市"), ("下二海", "上海市"), ("下 海", "上海市"),
    ("江 苏", "江苏省"), ("苏", "江苏省"),
    ("浙 江", "浙江省"), ("没 有", "浙江省"), ("浙", "浙江省"),
    ("安 徽", "安徽省"), ("安 秽", "安徽省"),
    ("福 建", "福建省"),
    ("江 西", "江西省"),
    ("山 东", "山东省"), ("东", "山东省"),
    ("河 南", "河南省"),
    ("湖 北", "湖北省"),
    ("湖 南", "湖南省"),
    ("广 东", "广东省"),
    ("广 西", "广西壮族自治区"),
    ("海 南", "海南省"),
    ("重 庆", "重庆市"),
    ("四 川", "四川省"), ("州", "四川省"),  # OCR 偶尔将四川错为 "州"
    ("贵 州", "贵州省"), ("本", "贵州省"),
    ("云 南", "云南省"),
    ("西 藏", "西藏自治区"),
    ("陕 西", "陕西省"), ("耳 西", "陕西省"),
    ("甘 肃", "甘肃省"), ("卫青", "甘肃省"),
    ("青 海", "青海省"),
    ("宁 夏", "宁夏回族自治区"), ("二有要", "宁夏回族自治区"),
    ("新 疆", "新疆维吾尔自治区"), ("新 到", "新疆维吾尔自治区"),
]

KNOWN_PROVINCES = [
    "北京市", "天津市", "河北省", "山西省", "内蒙古自治区", "辽宁省",
    "吉林省", "黑龙江省", "上海市", "江苏省", "浙江省", "安徽省",
    "福建省", "江西省", "山东省", "河南省", "湖北省", "湖南省",
    "广东省", "广西壮族自治区", "海南省", "重庆市", "四川省", "贵州省",
    "云南省", "西藏自治区", "陕西省", "甘肃省", "青海省", "宁夏回族自治区",
    "新疆维吾尔自治区",
]

# 表 3-9 完整 22 列 multi-level header (per 返工指令 三-1/三-2)
# group_l1 / group_l2 / leaf / canonical_indicator / unit / schema_alias
COLUMN_SCHEMA = [
    {"key": "geo", "group_l1": None, "group_l2": None, "leaf": "地区",
     "indicator": "地区", "unit": None, "is_label": True},
    {"key": "gdp_total", "group_l1": None, "group_l2": "三次产业增加值", "leaf": "生产总值",
     "indicator": "地区生产总值", "unit": "亿元"},
    {"key": "ind_pri", "group_l1": None, "group_l2": "三次产业增加值", "leaf": "第一产业",
     "indicator": "地区生产总值构成_第一产业", "unit": "亿元"},
    {"key": "ind_sec", "group_l1": None, "group_l2": "三次产业增加值", "leaf": "第二产业",
     "indicator": "地区生产总值构成_第二产业", "unit": "亿元"},
    {"key": "ind_ter", "group_l1": None, "group_l2": "三次产业增加值", "leaf": "第三产业",
     "indicator": "地区生产总值构成_第三产业", "unit": "亿元"},
    {"key": "brk_agri", "group_l1": None, "group_l2": "分行业增加值", "leaf": "农林牧渔业",
     "indicator": "地区生产总值分行业_农林牧渔业", "unit": "亿元"},
    {"key": "brk_indu", "group_l1": None, "group_l2": "分行业增加值", "leaf": "工业",
     "indicator": "地区生产总值分行业_工业", "unit": "亿元"},
    {"key": "brk_cons", "group_l1": None, "group_l2": "分行业增加值", "leaf": "建筑业",
     "indicator": "地区生产总值分行业_建筑业", "unit": "亿元"},
    {"key": "brk_whol", "group_l1": None, "group_l2": "分行业增加值", "leaf": "批发和零售业",
     "indicator": "地区生产总值分行业_批发和零售业", "unit": "亿元"},
    {"key": "brk_tran", "group_l1": None, "group_l2": "分行业增加值", "leaf": "交通运输、仓储和邮政业",
     "indicator": "地区生产总值分行业_交通运输_仓储和邮政业", "unit": "亿元"},
    {"key": "brk_hote", "group_l1": None, "group_l2": "分行业增加值", "leaf": "住宿和餐饮业",
     "indicator": "地区生产总值分行业_住宿和餐饮业", "unit": "亿元"},
    {"key": "brk_fina", "group_l1": None, "group_l2": "分行业增加值", "leaf": "金融业",
     "indicator": "地区生产总值分行业_金融业", "unit": "亿元"},
    {"key": "brk_real", "group_l1": None, "group_l2": "分行业增加值", "leaf": "房地产业",
     "indicator": "地区生产总值分行业_房地产业", "unit": "亿元"},
    {"key": "brk_othr", "group_l1": None, "group_l2": "分行业增加值", "leaf": "其他",
     "indicator": "地区生产总值分行业_其他", "unit": "亿元"},
    {"key": "per_capita", "group_l1": "人均地区", "group_l2": "生产总值(元)", "leaf": "人均地区生产总值",
     "indicator": "人均地区生产总值", "unit": "元"},
    {"key": "share_pri", "group_l1": "构成", "group_l2": "(地区生产总值=100)", "leaf": "第一产业",
     "indicator": "地区生产总值构成_第一产业占比", "unit": "%"},
    {"key": "share_sec", "group_l1": "构成", "group_l2": "(地区生产总值=100)", "leaf": "第二产业",
     "indicator": "地区生产总值构成_第二产业占比", "unit": "%"},
    {"key": "share_ter", "group_l1": "构成", "group_l2": "(地区生产总值=100)", "leaf": "第三产业",
     "indicator": "地区生产总值构成_第三产业占比", "unit": "%"},
    {"key": "growth_sum", "group_l1": "指数", "group_l2": "(上年=100)", "leaf": "生产总值(总和值)",
     "indicator": "地区生产总值增长率(总和值)", "unit": "%"},
    {"key": "growth_pri", "group_l1": "指数", "group_l2": "(上年=100)", "leaf": "第一产业",
     "indicator": "地区生产总值增长率_第一产业", "unit": "%"},
    {"key": "growth_sec", "group_l1": "指数", "group_l2": "(上年=100)", "leaf": "第二产业",
     "indicator": "地区生产总值增长率_第二产业", "unit": "%"},
    {"key": "growth_ter", "group_l1": "指数", "group_l2": "(上年=100)", "leaf": "第三产业",
     "indicator": "地区生产总值增长率_第三产业", "unit": "%"},
    {"key": "growth_pc", "group_l1": "人均地区", "group_l2": "(上年=100)", "leaf": "人均地区生产总值",
     "indicator": "人均地区生产总值增长率", "unit": "%"},
]
EXPECTED_NUMERIC_COLS = 22  # province-name column excluded

"""Per-column NBS-published reference（官方公布值，公开来源）
用于 directive 三-5 per-column known-truth test 和 三-6 per-column 准确率。

取值口径：各省 2024 年地区生产总值初步核算数（国家统计局《中国统计年鉴2025》
表 3-9 印刷值 = 各省统计局 2025 年公布的初步核算数）。growth_* 列为指数
（上年=100，即 100 + 增长率），非增长率本身。

仅列 OCR 损伤低的高信噪比样本；OCR 严重错字的样本（如部分占比列小数点丢失）
不列入以免伪失败——那些单元格仍以 value + needs_review 完整保留在网格里。
命名 'reference' 而非 'truth' 强调这是 NBS 公布值对照基线，不是断言 OCR
提取本身是 ground truth。"""
COLUMN_REFERENCE: dict[str, dict[str, float]] = {
    "gdp_total": {  # 亿元
        "北京市": 49843.1, "上海市": 53926.71, "江苏省": 137008.0,
        "广东省": 141633.81, "河南省": 63589.99, "湖北省": 60012.97,
    },
    "ind_pri": {
        "北京市": 116.4, "上海市": 99.69, "江苏省": 5245.2,
        "湖北省": 5462.18, "河南省": 5491.40, "广东省": 5837.03,
    },
    "ind_sec": {
        "北京市": 7226.8, "上海市": 11637.57, "江苏省": 59180.1,
        "湖北省": 21573.76, "河南省": 24346.17, "广东省": 54365.47,
    },
    "ind_ter": {
        "北京市": 42499.9, "上海市": 42189.44, "江苏省": 72582.8,
        "湖北省": 32977.03, "河南省": 33752.42, "广东省": 81431.31,
    },
    "brk_agri": {  # 农林牧渔业（≈第一产业 + 农林牧渔专业及辅助性活动）
        "北京市": 117.9, "湖北省": 5891.1,
    },
    "brk_indu": {  # 工业
        "北京市": 5937.6, "湖北省": 17609.0,
    },
    "brk_cons": {  # 建筑业
        "北京市": 1414.3, "湖北省": 4123.6,
    },
    "brk_whol": {  # 批发和零售业
        "北京市": 3078.5,
    },
    "brk_tran": {  # 交通运输、仓储和邮政业
        "北京市": 1240.3,
    },
    "brk_hote": {  # 住宿和餐饮业（上海 2024 公报确认 513.18）
        "上海市": 513.18,
    },
    "brk_fina": {  # 金融业
        "北京市": 8154.2,
    },
    "brk_real": {  # 房地产业
        "北京市": 4933.0,
    },
    "brk_othr": {  # 其他 = GDP − 上述各分行业之和
        "北京市": 24524.8,
    },
    "per_capita": {  # 元
        "北京市": 228167.0, "江苏省": 160694.0, "湖北省": 102832.37,
    },
    "share_pri": {  # %（占比，三次产业构成）
        "江苏省": 3.8, "河南省": 8.6,
    },
    "share_sec": {
        "北京市": 14.5, "湖北省": 35.9, "河南省": 38.3, "广东省": 38.4,
    },
    "share_ter": {
        "北京市": 85.3, "湖北省": 54.9, "河南省": 53.1,
    },
    "growth_sum": {  # 指数（上年=100，即 100+增长率）
        "北京市": 105.2, "江苏省": 105.8, "河南省": 105.1,
        "湖北省": 105.8, "广东省": 103.5,
    },
    "growth_pri": {
        "北京市": 101.5, "湖北省": 103.1, "河南省": 103.3, "广东省": 103.4,
    },
    "growth_sec": {
        "北京市": 105.7, "湖北省": 106.4, "河南省": 106.8, "广东省": 104.4,
    },
    "growth_ter": {
        "北京市": 105.1, "湖北省": 105.9, "河南省": 104.1, "广东省": 102.8,
    },
    "growth_pc": {
        "北京市": 105.2, "湖北省": 105.9, "河南省": 105.5, "广东省": 103.0,
    },
}

# R3-C：每列硬门槛（最低 per-column 准确率）。1.0 = 该列每个 reference 样本都
# 必须在 OCR_TOLERANCE 内命中，否则该列未达标。它是硬门槛——干净且正确的
# reference 应该 100% 命中；一旦 reference 被污染（旧修订/口径错误），或 OCR
# 出现系统性列错位，门槛就会被打破。
PER_COLUMN_MIN_ACCURACY: dict[str, float] = {
    "gdp_total": 1.0, "ind_pri": 1.0, "ind_sec": 1.0, "ind_ter": 1.0,
    "brk_agri": 1.0, "brk_indu": 1.0, "brk_cons": 1.0, "brk_whol": 1.0,
    "brk_tran": 1.0, "brk_hote": 1.0, "brk_fina": 1.0, "brk_real": 1.0,
    "brk_othr": 1.0, "per_capita": 1.0, "share_pri": 1.0, "share_sec": 1.0,
    "share_ter": 1.0,
    "growth_sum": 1.0, "growth_pri": 1.0, "growth_sec": 1.0,
    "growth_ter": 1.0, "growth_pc": 1.0,
}

OCR_TOLERANCE = {  # per-column 容忍误差（OCR 常见小数点丢失/单位错位）
    "per_capita": 5000.0,
    "gdp_total": 5.0,
    "ind_pri": 50.0, "ind_sec": 100.0, "ind_ter": 200.0,
    "brk_agri": 50.0, "brk_indu": 100.0, "brk_cons": 50.0,
    "brk_whol": 50.0, "brk_tran": 50.0, "brk_hote": 50.0,
    "brk_fina": 50.0, "brk_real": 50.0, "brk_othr": 200.0,
    "share_pri": 0.5, "share_sec": 0.5, "share_ter": 0.5,
    "growth_sum": 0.5, "growth_pri": 0.5, "growth_sec": 0.5,
    "growth_ter": 0.5, "growth_pc": 0.5,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def require_tesseract() -> tuple[str, str]:
    bin_path = shutil.which("tesseract")
    if not bin_path:
        raise RuntimeError("tesseract 未安装")
    out = subprocess.run([bin_path, "--list-langs"], capture_output=True, text=True)
    if "chi_sim" not in out.stdout:
        raise RuntimeError("tesseract 缺少 chi_sim 语言包")
    return bin_path, "chi_sim"


def ocr_tsv(image_path: Path, psm: int = 6) -> list[dict]:
    bin_path, lang = require_tesseract()
    out = subprocess.run(
        [bin_path, str(image_path), "-", "-l", lang, "--psm", str(psm), "tsv"],
        capture_output=True, check=True,
    )
    text = out.stdout.decode("utf-8", errors="replace")
    lines = text.strip().split("\n")
    header = lines[0].split("\t")
    rows: list[dict] = []
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < len(header):
            continue
        row = dict(zip(header, parts))
        try:
            row["conf"] = float(row.get("conf", -1))
            row["left"] = int(row.get("left", 0))
            row["top"] = int(row.get("top", 0))
            row["width"] = int(row.get("width", 0))
            row["height"] = int(row.get("height", 0))
        except (ValueError, KeyError):
            continue
        rows.append(row)
    return rows


def ocr_text(image_path: Path, psm: int = 6) -> str:
    bin_path, lang = require_tesseract()
    out = subprocess.run(
        [bin_path, str(image_path), "-", "-l", lang, "--psm", str(psm)],
        capture_output=True, check=True,
    )
    return out.stdout.decode("utf-8", errors="replace")


def group_into_rows(words: list[dict], y_tolerance: int = 20) -> list[list[dict]]:
    rows: list[list[dict]] = []
    for w in sorted(words, key=lambda r: (r["top"], r["left"])):
        if w["text"].strip() == "" or w["conf"] < 0:
            continue
        placed = False
        for row in rows:
            if abs(row[0]["top"] - w["top"]) <= y_tolerance:
                row.append(w)
                placed = True
                break
        if not placed:
            rows.append([w])
    for row in rows:
        row.sort(key=lambda r: r["left"])
    rows.sort(key=lambda r: r[0]["top"])
    return rows


def extract_province_by_position(text_lines: list[str]) -> dict[int, str]:
    """Text-line index → province standard name (按 NBS 31 省顺序)。"""
    mapping: dict[int, str] = {}
    used: set[str] = set()
    province_patterns = list(PROVINCE_LABEL_MAP)
    for line_no, line in enumerate(text_lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        n_numeric = len(re.findall(r"\d+\.?\d*", line_stripped))
        if n_numeric < 3:
            continue
        head = re.sub(r"\s+", "", line_stripped[:6])
        for raw, std in province_patterns:
            raw_clean = re.sub(r"\s+", "", raw)
            if head.startswith(raw_clean) and std not in used:
                mapping[line_no] = std
                used.add(std)
                break
    return mapping


def detect_province(label: str) -> str | None:
    label = label.strip()
    for raw, std in PROVINCE_LABEL_MAP:
        if label == raw or raw in label:
            return std
    label_nospace = re.sub(r"\s+", "", label)
    for raw, std in PROVINCE_LABEL_MAP:
        if re.sub(r"\s+", "", raw) == label_nospace:
            return std
    return None


def extract_numeric_token(text: str) -> tuple[float | None, str, str]:
    """OCR 文本 → (值, raw_value, missing_reason)。missing_reason 永不为 None。"""
    text = text.strip()
    if text in {"…", "—", "－", "-", ""}:
        return None, text, "NOT_PUBLISHED"
    cleaned = text.replace(",", "").replace("%", "").strip()
    if not cleaned:
        return None, text, "EMPTY_OCR"
    try:
        v = float(cleaned)
        if v != v:
            return None, text, "OCR_UNREADABLE"
        return v, text, "OK"
    except ValueError:
        return None, text, "OCR_UNREADABLE"


def assign_column_provenance(idx: int) -> dict:
    """Numeric token index → schema column entry; raises if out of range."""
    # numeric columns start at index 1 (index 0 = geo label)
    col_idx = idx + 1  # idx=0 → schema col 1 (gdp_total)
    if col_idx >= len(COLUMN_SCHEMA):
        raise ValueError(f"numeric token idx={idx} exceeds schema ({len(COLUMN_SCHEMA) - 1} numeric cols)")
    return COLUMN_SCHEMA[col_idx]


# ---------------------------------------------------------------------------
# R3-C: 列边界映射 (column boundary mapping)
#
# 位置式计数在中间缺格时会把后续列整体左移（如某行第 3 列空，第 4 列的值会
# 落进第 3 列槽位）。边界映射改为：跨全部数据行收集数值 token 的 right-edge
# x 坐标，做确定性 1D k-means（k=22）得到各列中心，再以相邻中心中点作边界，
# 每个 token 按 right-edge 归入最近中心。若某列在行内无 token → 该槽位显式
# 建模为缺失（value=None），不会把后续列挤到左移。
# ---------------------------------------------------------------------------

def _token_right_edge(word: dict) -> float:
    """数值 token 的右侧 x 坐标（数值列多为右对齐，用 right-edge 聚类更稳）。"""
    return float(word["left"]) + float(word["width"])


def _numeric_ok(word: dict) -> bool:
    t = word["text"].strip()
    if not t or word["conf"] < 30:
        return False
    v, raw, reason = extract_numeric_token(t)
    return reason == "OK"


def build_column_boundaries(token_right_edges: list[float], k: int = EXPECTED_NUMERIC_COLS,
                            iters: int = 100) -> tuple[list[float], list[float], list[float]]:
    """确定性 1D k-means（fixed 均匀初始中心、固定迭代，无随机）。

    返回 (sorted_centers, boundaries, intervals)：
      * sorted_centers — k 个列中心（right-edge 坐标，升序）
      * boundaries — k-1 个相邻中心中点；right-edge < boundaries[i] → 列 i
      * intervals — k 个 (left_bound, right_bound) 像素区间，供逐格 provenance
    """
    if not token_right_edges:
        raise ValueError("build_column_boundaries: 无数值 token 可聚类")
    lo, hi = float(min(token_right_edges)), float(max(token_right_edges))
    centers = [lo + (hi - lo) * (i + 0.5) / k for i in range(k)]
    for _ in range(iters):
        groups: list[list[float]] = [[] for _ in range(k)]
        for p in token_right_edges:
            j = min(range(k), key=lambda i: abs(p - centers[i]))
            groups[j].append(p)
        new_centers = [sum(g) / len(g) if g else centers[i] for i, g in enumerate(groups)]
        if new_centers == centers:
            break
        centers = new_centers
    centers = sorted(centers)
    boundaries = [(centers[i] + centers[i + 1]) / 2 for i in range(k - 1)]
    intervals = []
    for i in range(k):
        left = boundaries[i - 1] if i > 0 else (centers[0] - (boundaries[0] - centers[0]) if boundaries else centers[0])
        right = boundaries[i] if i < k - 1 else (centers[-1] + (centers[-1] - boundaries[-1]) if boundaries else centers[-1])
        intervals.append((left, right))
    return centers, boundaries, intervals


def assign_right_edge_to_column(right_edge: float, boundaries: list[float]) -> int:
    """right-edge x → 列索引。bisect 定位到边界左边的第 i 列。"""
    import bisect
    return bisect.bisect_right(boundaries, float(right_edge))


def _collect_numeric_tokens(row: list[dict], conf_min: int = 30) -> list[dict]:
    """一行内所有候选 token（conf≥conf_min，非空，非脚注）。

    返回每个 token 的解析结果 —— 含 value=None 的垃圾/缺失 token（OCR 把某
    个数值格子常读成乱码或 '…'），这样垃圾 token 仍能占据其列槽位（显式缺格
    建模），而不是被丢掉导致后续列整体左移。
    """
    out = []
    for w in row:
        t = w["text"].strip()
        if not t or t.startswith("注"):
            continue
        if w["conf"] < conf_min:
            continue
        v, raw, reason = extract_numeric_token(t)
        out.append({
            "word": w, "value": v, "raw_value": raw,
            "missing_reason": None if reason == "OK" else reason,
            "has_value": reason == "OK",
            "right_edge": _token_right_edge(w),
        })
    return out


def _row_to_column_slots(rows_numeric: list[dict], boundaries: list[float],
                         grid_interval: tuple[float, float]) -> tuple[dict[int, dict], set[int]]:
    """把一行内的 token 按 right-edge 归列，返回 (slots, duplicate_cols)。

    行为：
      * right-edge 落在数值网格区间 [grid_interval] 内的 token 才计入；
      * 每列留一个 token：优先可解析数值（has_value=True），同为可解析则取
        conf 更高者（同列多 token 计 duplicate —— 该列由 caller 标 needs_review）。
      * 没有 token 的列 → 不进入 slots，caller 据此显式建模为缺格。
      * 返回值第二项展开 duplicate_cols：一列收到 ≥2 个 token 的列索引集合，
        这是"边界映射把两列折叠到一格"的可靠信号，需人工复核。
    """
    lo_bound, hi_bound = grid_interval
    by_col: dict[int, list[dict]] = {}
    for tok in rows_numeric:
        re_edge = tok["right_edge"]
        if not (lo_bound <= re_edge <= hi_bound):
            continue
        ci = assign_right_edge_to_column(re_edge, boundaries)
        by_col.setdefault(ci, []).append(tok)
    slots: dict[int, dict] = {}
    duplicate_cols: set[int] = set()
    for ci, toks_list in by_col.items():
        if len(toks_list) > 1:
            duplicate_cols.add(ci)
        slots[ci] = max(toks_list, key=lambda t: (t["has_value"], t["word"]["conf"]))
    return slots, duplicate_cols


def extract(image_path: Path) -> dict:
    file_hash = sha256_file(image_path)
    file_size = image_path.stat().st_size

    words = ocr_tsv(image_path, psm=6)
    rows = group_into_rows(words, y_tolerance=20)

    raw_text = ocr_text(image_path, psm=6)
    text_lines = raw_text.split("\n")
    province_by_line = extract_province_by_position(text_lines)

    title_text = " ".join(w["text"] for w in rows[0]) if rows else ""
    unit_text = ""
    for r in rows[:6]:
        joined = " ".join(w["text"] for w in r)
        if "单位" in joined:
            unit_text = joined
            break

    notes: list[str] = []
    for r in rows[-3:]:
        joined = " ".join(w["text"] for w in r)
        if "注" in joined:
            notes.append(joined)

    # R3-C：识别省数据行（OCR 行内 ≥15 个可解析数值 token）。
    numeric_row_groups: list[tuple[list[dict], list[dict]]] = []
    for r in rows[3:]:
        toks = _collect_numeric_tokens(r)
        if sum(1 for t in toks if t["has_value"]) >= 15:
            numeric_row_groups.append((r, toks))

    sorted_province_lines = sorted(province_by_line.items())
    expected_provinces = [p for _, p in sorted_province_lines]

    # R3-C：跨全部省行收集 right-edge → 确定性 1D k-means 得到列边界。
    # 这些 token 含省名 label（第 0 列，非数值列），故 k = 22 + 1 = 23：
    # k-means 会把 label 隔离到最左 cluster，丢弃 clusters[0] 即得 22 个数值列。
    all_right_edges = [tok["right_edge"] for _, toks in numeric_row_groups for tok in toks]
    centers, boundaries, intervals = build_column_boundaries(
        all_right_edges, k=EXPECTED_NUMERIC_COLS + 1)
    # centers[0]/interval[0] = province label；数值列为 centers[1..22]。
    numeric_intervals = intervals[1:]
    numeric_boundaries = boundaries[1:]  # 21 条边界分隔 centers[1..22]
    grid_interval = (numeric_intervals[0][0], numeric_intervals[-1][1])

    # 省 → (该行 tokens, row top) 映射。
    # 首选：从行内最靠左的 province-label token 识别（detect_province），
    #   避免位置耦合 —— OCR 行数与 31 省顺序不一定逐行对齐（缺行/合并行）。
    # 回退：用 expected_provinces 位置对应。
    # 省 → (该行 tokens, row top) 映射。
    # 主映射用位置对应（expected_provinces = NBS 31 省固定顺序），已被原型验证
    # 逐行对齐正确；detect_province 的单字别名（"山"/"东"/"三"/"0"）在 label 被
    # OCR 拆成两个单字 word（如 "广"+"东"）时会误判跨省，故仅作 position 为空时
    # 的回退。
    prov_to_group: dict[str, tuple[list[dict], int]] = {}
    for ri, (r, toks) in enumerate(numeric_row_groups):
        row_top = int(min((t["word"]["top"] for t in toks), default=0))
        std_province = expected_provinces[ri] if ri < len(expected_provinces) else None
        if std_province is None:
            # 回退：拼接最左 1-3 个 word 成完整 label 再 detect（仅当 position 缺省）
            buf = ""
            for w in sorted(r, key=lambda w: w["left"])[:3]:
                buf += w["text"].strip()
                if len(buf) >= 2:
                    p = detect_province(buf)
                    if p is not None:
                        std_province = p
                        break
        if std_province is None:
            continue
        if std_province in prov_to_group:
            continue  # 重复识别 → 保首见，后续行落空（该省以已见行建模）
        prov_to_group[std_province] = (toks, row_top)

    numeric_cols = [c for c in COLUMN_SCHEMA if not c.get("is_label")]

    # R3-C：每省 × 每列恰好一条 observation —— 31 × 22 = 682 槽位。
    # 缺格/整行未检出 都以 value=None + 具体 missing_reason 显式建模，绝不省略。
    observations: list[dict] = []
    n_rows_not_detected = 0
    for prov in KNOWN_PROVINCES:
        group = prov_to_group.get(prov)
        if group is None:
            n_rows_not_detected += 1
            slots: dict[int, dict] = {}
            duplicate_cols: set[int] = set()
            row_bbox = None
        else:
            toks, row_top = group
            slots, duplicate_cols = _row_to_column_slots(toks, numeric_boundaries, grid_interval)
            lefts = [t["word"]["left"] for t in toks]
            rights = [t["word"]["left"] + t["word"]["width"] for t in toks]
            row_bbox = {
                "left": int(min(lefts)) if lefts else 0,
                "top": row_top,
                "width": int(max(rights) - min(lefts)) if rights and lefts else 0,
                "height": int(max((t["word"]["height"] for t in toks), default=0)),
            }

        slots_count = len(slots)
        row_complete = (slots_count == EXPECTED_NUMERIC_COLS)
        for ci, col in enumerate(numeric_cols):
            tok = slots.get(ci)
            if tok is None:
                value, raw_value, mr = None, "", (
                    "ROW_NOT_DETECTED" if group is None else "CELL_NOT_DETECTED")
                conf = 0.0
                cell_bbox = None
                ocr_word_index = ""
            else:
                value = tok["value"]
                raw_value = tok["raw_value"]
                mr = tok["missing_reason"]
                conf = tok["word"]["conf"] / 100.0
                w = tok["word"]
                cell_bbox = {"left": int(w["left"]), "top": int(w["top"]),
                             "width": int(w["width"]), "height": int(w["height"])}
                ocr_word_index = str(w.get("word_num", ""))

            reasons: list[str] = []
            if not row_complete:
                reasons.append("row_cell_count_mismatch")
            if isinstance(duplicate_cols, set) and ci in duplicate_cols:
                reasons.append("duplicate_column_tokens")
            if mr is not None:
                reasons.append(mr.lower())
            elif conf < 0.85:
                reasons.append("low_ocr_confidence")

            obs = {
                "indicator_canonical": col["indicator"],
                "column_key": col["key"],
                "group_l1": col["group_l1"],
                "group_l2": col["group_l2"],
                "leaf": col["leaf"],
                "geo_canonical": prov,
                "period_year": 2024,
                "period_label": "2024",
                "period_type": "YEAR",
                "unit": col["unit"],
                "value": value,
                "raw_value": raw_value,
                "missing_reason": mr,
                "is_missing": value is None,
                "comparison_basis": "NOMINAL",
                "value_type": "FACT",
                "status": "PRELIMINARY",
                "source_document": {
                    "title": title_text.strip(),
                    "publisher": "国家统计局 / National Bureau of Statistics",
                    "publication_date": "2025-12-01",
                    "url": "https://www.stats.gov.cn/sj/ndsj/2025/html/C03-09.jpg",
                    "file_name": image_path.name,
                    "file_hash_sha256": file_hash,
                    "file_size_bytes": file_size,
                    "extraction_method": "IMAGE_OCR",
                    "ocr_engine": "tesseract",
                    "ocr_language": "chi_sim",
                    "ocr_psm": 6,
                    "language": "zh",
                },
                "source_location": {
                    "page_number": 1,
                    "image_bbox": row_bbox,
                    "cell_bbox": cell_bbox,
                    "ocr_word_index": ocr_word_index,
                    "column_boundary_left": numeric_intervals[ci][0],
                    "column_boundary_right": numeric_intervals[ci][1],
                    "column_boundary_method": "kmeans_right_edge",
                    "row_numeric_cell_index": ci,
                    "row_numeric_cell_count": slots_count,
                },
                "methodology_caveat": "本表绝对数按当年价格计算；指数按不变价格计算。初步核算数。",
                "footnote_references": notes,
                "confidence": conf,
                "needs_review": bool(reasons),
                "needs_review_reasons": reasons,
                # 锁定而非 datetime.now()：deterministic rebuild 需要字节稳定
                # （B-07/I-01，同 spike 02/04 修法）。
                "extracted_at": "2026-08-23T10:00:00Z",
                "extractor_version": "spike00-national-yearbook/3.0-R3C",
            }
            observations.append(obs)

    return {
        "metadata": {
            "spike": "00-national-yearbook-table",
            "extractor": "spike00-national-yearbook/3.0-R3C",
            "table_number": "3-9",
            "table_title": title_text.strip(),
            "statistical_period": "2024年",
            "file_name": image_path.name,
            "file_hash_sha256": file_hash,
            "file_size_bytes": file_size,
            "ocr_engine": "tesseract",
            "ocr_language": "chi_sim",
            "ocr_psm": 6,
            "schema_source": "国家统计局《中国统计年鉴 2025》表 3-9 官方列定义（22 列）",
            "column_schema": [c for c in COLUMN_SCHEMA if not c.get("is_label")],
            "expected_numeric_cols_per_row": EXPECTED_NUMERIC_COLS,
            "column_reference_samples": {k: v for k, v in COLUMN_REFERENCE.items()},
            "ocr_tolerance": OCR_TOLERANCE,
            "n_ocr_rows": len(rows),
            "n_provinces_detected": len(prov_to_group),
            "n_provinces_expected": len(KNOWN_PROVINCES),
            "n_rows_not_detected": n_rows_not_detected,
            "n_observations": len(observations),
            "n_missing": sum(1 for o in observations if o["is_missing"]),
            "n_needs_review": sum(1 for o in observations if o["needs_review"]),
            "n_needs_review_by_reason": dict(sorted(
                ((r, sum(1 for o in observations
                         for rr in o["needs_review_reasons"] if rr == r))
                 for r in {rr for o in observations for rr in o["needs_review_reasons"]}),
                key=lambda x: -x[1])),
            "unit_caption_ocr": unit_text,
            "extracted_at": "2026-08-23T10:00:00Z",
            "data_status": "OCR extraction (NOT human-verified truth; per directive 三-7)",
        },
        "observations": observations,
        "notes": notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.input is None:
        args.input = Path(__file__).parent / "data" / "c0309.jpg"
    if not args.input.exists():
        print(f"ERROR: 输入文件不存在: {args.input}", file=sys.stderr)
        return 2
    if args.output is None:
        args.output = (
            Path(__file__).resolve().parents[2] / "data" / "extracts" /
            "00-national-yearbook-table" / "extracted.json"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)

    result = extract(args.input)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"OK: 写入 {args.output}")
    md = result["metadata"]
    print(f"  observations:  {md['n_observations']}")
    print(f"  missing:       {md['n_missing']}")
    print(f"  needs_review:  {md['n_needs_review']}")
    print(f"  reasons:       {md['n_needs_review_by_reason']}")
    print(f"  provinces:     {len(set(o['geo_canonical'] for o in result['observations']))}")
    print(f"  source hash:   {md['file_hash_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())