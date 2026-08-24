#!/usr/bin/env python3
"""Build truth_p24.json for spike 04 (page 24, France trade table, 1843-1872).

The cell values below are HUMAN READINGS from the rendered page (three vision
transcription passes + zoomed single-cell re-reads + pixel component analysis),
cross-validated against five arithmetic identities that the printed table
satisfies exactly:

    excess = exports - imports          (5 column groups per row)
    gs_leaf = gold_leaf + silver_leaf   (3 leaves per row)

Any reading that broke an identity was re-verified at 600 dpi with connected
-component width analysis; the surviving reading is what is recorded here.
This script re-runs the identity verification on every row before writing the
file, so the JSON is machine-verified at build time.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent

# column keys in printed order (after YEAR)
COLS = [
    "gt_imports", "gt_exports", "gt_excess",          # Merchandise / General trade
    "st_imports", "st_exports", "st_excess",          # Merchandise / Special trade
    "gold_imports", "gold_exports", "gold_excess",    # Precious metals / Gold
    "silver_imports", "silver_exports", "silver_excess",  # Precious metals / Silver
    "gs_imports", "gs_exports", "gs_excess",          # Precious metals / Gold and silver
]

# Human readings. Sign convention: excess = exports - imports
# (negative = excess of imports, positive = excess of exports).
ROWS: list[tuple[int, list[int]]] = [
    (1843, [229100, 191500, -37600, 163200, 132600, -30600, 1900, 9800, 7900, 30200, 10300, -19900, 32100, 20100, -12000]),
    (1844, [230200, 221300, -8900, 167400, 152500, -14900, 1000, 2000, 1000, 29200, 13300, -15900, 30200, 15300, -14900]),
    (1845, [239300, 229200, -10100, 165200, 163700, -1500, 1000, 3600, 2600, 34600, 13300, -21300, 35600, 16900, -18700]),
    (1846, [242500, 227700, -14800, 177600, 164500, -13100, 1500, 3200, 1700, 20600, 11600, -9000, 22100, 14800, -7300]),
    (1847, [249000, 202500, -46500, 184500, 138900, -45600, 4100, 6500, 2400, 26700, 16300, -10400, 30800, 22800, -8000]),
    (1848, [136700, 180700, 44000, 91500, 133200, 41700, 8500, 1100, -7400, 45000, 3700, -41300, 53500, 4800, -48700]),
    (1849, [197100, 245000, 47900, 139800, 181000, 41200, 2300, 1100, -1200, 56200, 9000, -47200, 58500, 10100, -48400]),
    (1850, [216100, 277000, 60900, 152600, 206100, 53500, 11800, 8500, -3300, 29900, 15900, -14000, 41700, 24400, -17300]),
    (1851, [211100, 293400, 82300, 147700, 223500, 75800, 22300, 6000, -16300, 34500, 19400, -15100, 56800, 25400, -31400]),
    (1852, [268700, 324300, 55600, 191000, 212600, 21600, 11400, 8200, -3200, 34700, 35200, 500, 46100, 43400, -2700]),
    (1853, [327300, 396300, 69000, 230800, 297600, 66800, 61500, 5700, -55800, 21700, 34300, 12600, 83200, 40000, -43200]),
    (1854, [348400, 376800, 28400, 249300, 272800, 23500, 92800, 12400, -80400, 19300, 50900, 31600, 112100, 63300, -48800]),
    (1855, [416800, 418300, 1500, 307700, 300700, -7000, 73500, 31400, -42100, 23300, 61400, 38100, 96800, 92800, -4000]),
    (1856, [528900, 513200, -15700, 384000, 365300, -18700, 89700, 17300, -72400, 19500, 75900, 56400, 109200, 93200, -16000]),
    (1857, [519000, 509400, -9600, 351500, 350100, -1400, 109800, 23700, -86100, 19000, 88400, 69400, 128800, 112100, -16700]),
    (1858, [417700, 494300, 76600, 301600, 364200, 62600, 106800, 12800, -94000, 31000, 33900, 2900, 137800, 46700, -91100]),
    (1859, [454500, 590000, 135500, 316700, 437400, 120700, 140300, 36200, -104100, 38800, 73700, 34900, 179100, 109900, -69200]),
    (1860, [512900, 607500, 94600, 366200, 439500, 73300, 90800, 30600, -60200, 25200, 55500, 30300, 116000, 86100, -29900]),
    (1861, [595500, 513400, -82100, 471100, 371500, -99600, 47100, 51700, 4600, 33200, 45200, 12000, 80300, 96900, 16600]),
    (1862, [559500, 588600, 29100, 424300, 432800, 8500, 77500, 45700, -31800, 25400, 42000, 16600, 102900, 87700, -15200]),
    (1863, [624600, 680600, 56000, 468300, 510000, 41700, 71400, 69000, -2400, 31100, 44300, 13200, 102500, 113300, 10800]),
    (1864, [657600, 756800, 99200, 487000, 563500, 76500, 89600, 65400, -24200, 51700, 59900, 8200, 141300, 125300, -16000]),
    (1865, [680800, 788700, 107900, 509900, 596100, 86200, 80900, 51800, -29100, 45600, 31600, -14000, 126500, 83400, -43100]),
    (1866, [742100, 826200, 84100, 539100, 613900, 74800, 157000, 67200, -89800, 48300, 39600, -8700, 205300, 106800, -98500]),
    (1867, [777900, 759300, -18600, 584100, 545400, -38700, 114571, 35697, -78874, 49096, 12493, -36603, 163667, 48190, -115477]),
    (1868, [821800, 718100, -103700, 637600, 538500, -99100, 95235, 54152, -41083, 37260, 16170, -21090, 132495, 70322, -62173]),
    (1869, [773700, 770800, -2900, 608500, 593500, -15000, 87737, 34791, -52946, 37213, 15708, -21505, 124950, 50499, -74451]),
    (1870, [675000, 667000, -8000, 553400, 540800, -12600, 59896, 36781, -23115, 20466, 13621, -6845, 80362, 50402, -29960]),
    (1871, [763000, 632700, -130300, 688400, 554400, -134000, 27765, 69031, 41266, 30338, 27343, -2995, 58103, 96374, 38271]),
    (1872, [868800, 918000, 49200, 689100, 726000, 36900, 27379, 37588, 10209, 46489, 26754, -19735, 73868, 64342, -9526]),
]

# Cells whose print is degraded or whose reading required arbitration beyond a
# plain transcription pass. adopted == value recorded above.
CONTESTED = [
    {"cell": "1847 gt_imports", "adopted": 249000, "alternatives": [249700],
     "evidence": "component glyph sequence at 600 dpi = 2,4,9,0,0,0 (no 7th digit); identity 202500-249000=-46500 matches printed excess"},
    {"cell": "1847 st_imports", "adopted": 184500, "alternatives": [181500],
     "evidence": "third glyph nearly inkless (dropout at binarization); identity 138900-184500=-45600 matches printed excess; zoom reads favored 181500 — flagged print_degraded"},
    {"cell": "1852 silver_imports", "adopted": 34700, "alternatives": [31700],
     "evidence": "gs decomposition 46100-11400=34700 and excess 35200-34700=+500 both match printed values; zoom read 31700 (4 read as 1)"},
    {"cell": "1853 gold_imports", "adopted": 61500, "alternatives": [91500],
     "evidence": "gs decomposition 83200-21700=61500 and excess 5700-61500=-55800 both match printed values"},
    {"cell": "1853 silver_exports", "adopted": 34300, "alternatives": [31300],
     "evidence": "gs decomposition 40000-5700=34300 and excess 34300-21700=+12600 both match printed values"},
    {"cell": "1857 st_imports", "adopted": 351500, "alternatives": [361500],
     "evidence": "digit-2 component width 14px matches 5 (13-16) not 6; identity 350100-351500=-1400 matches printed excess"},
    {"cell": "1857 st_excess", "adopted": -1400, "alternatives": [-11400],
     "evidence": "right-alignment: value starts one digit-slot right of 5-digit rows (start x 2041 vs 2012); 4 digit glyphs = 1,4,0,0"},
    {"cell": "1861 st_exports", "adopted": 371500, "alternatives": [371800],
     "evidence": "digit-4 component width 21px matches 5 (17-23) not 8 (12-15); identity 471100-371500=-99600 matches printed excess"},
    {"cell": "1861 st_excess", "adopted": -99600, "alternatives": [-99300],
     "evidence": "two independent zoom reads -99,600; closes identity with 371500 partner"},
    {"cell": "1864 st_exports", "adopted": 563500, "alternatives": [561400, 564400],
     "evidence": "verified-band component sequence 5,6,3,5,0(+faint 0); identity 487000+76500=563500"},
    {"cell": "1864 st_excess", "adopted": 76500, "alternatives": [74400],
     "evidence": "two independent zoom reads +76,500; identity with 563500 partner closes"},
    {"cell": "1863 gold_imports", "adopted": 71400, "alternatives": [74400],
     "evidence": "gs decomposition 102500-31100=71400 and excess 69000-71400=-2400 both match printed values"},
    {"cell": "1852 st_excess", "adopted": 21600, "alternatives": [51600],
     "evidence": "6x zoom: leading digit shows flat bottom bar of 2, second glyph plain stem = 1; identity 212600-191000=21600"},
    {"cell": "1866 gt_excess", "adopted": 84100, "alternatives": [81100],
     "evidence": "two independent contact-sheet reads show open-top 4 after the 8; identity 826200-742100=84100"},
    {"cell": "1871 st_excess", "adopted": -134000, "alternatives": [-131000],
     "evidence": "digit-3 component width 11px matches open-4 (9-12) not serif-1 (15-21); trailing zero split into two arcs (w10+w12) same pattern as neighboring rows; identity 554400-688400=-134000; st_imports 688400 read at 6x zoom (double-loop 8)"},
]

# Measured page geometry (600 dpi rotated canvas, page 24) used to re-locate
# rows/columns on re-render; x windows are interior to each column's rules.
GEOMETRY_600DPI = {
    "year_band_x": [130, 270],
    "column_x_windows": {
        "gt_imports": [560, 845], "gt_exports": [855, 1125], "gt_excess": [1140, 1410],
        "st_imports": [1425, 1670], "st_exports": [1685, 1930], "st_excess": [1975, 2250],
        "gold_imports": [2270, 2515], "gold_exports": [2530, 2790], "gold_excess": [2825, 3090],
        "silver_imports": [3110, 3335], "silver_exports": [3355, 3640], "silver_excess": [3660, 3935],
        "gs_imports": [3955, 4200], "gs_exports": [4215, 4460], "gs_excess": [4475, 4750],
    },
    "row_ink_peaks_y": {str(y): p for y, p in zip(
        range(1843, 1873),
        [1316, 1367, 1417, 1467, 1517, 1568, 1618, 1669, 1718, 1769, 1819, 1869, 1919, 1969,
         2020, 2070, 2120, 2170, 2220, 2270, 2321, 2371, 2421, 2471, 2521, 2571, 2621, 2671, 2720, 2771])},
    "glyph_band_offset_from_peak": [-38, 2],
    "note": "300 dpi values = divide by 2; peaks measured on year-column ink profile; bands verified against GT-column ink rows",
}


def verify_identities() -> list[str]:
    errors = []
    for year, vals in ROWS:
        d = dict(zip(COLS, vals))
        for g in ("gt", "st", "gold", "silver", "gs"):
            if d[f"{g}_exports"] - d[f"{g}_imports"] != d[f"{g}_excess"]:
                errors.append(f"{year} {g}: {d[f'{g}_exports']}-{d[f'{g}_imports']} != {d[f'{g}_excess']}")
        for leaf in ("imports", "exports", "excess"):
            if d[f"gold_{leaf}"] + d[f"silver_{leaf}"] != d[f"gs_{leaf}"]:
                errors.append(f"{year} gs_{leaf}: gold+silver != gs")
    return errors


def main() -> int:
    if len(ROWS) != 30:
        print(f"FATAL: expected 30 rows, got {len(ROWS)}")
        return 1
    for y, vals in ROWS:
        if len(vals) != 15:
            print(f"FATAL: {y} has {len(vals)} values, expected 15")
            return 1
    errs = verify_identities()
    if errs:
        print(f"FATAL: {len(errs)} identity violations:")
        for e in errs:
            print("  ", e)
        return 1
    print("identity check: 30 rows x 5 excess identities + 30 x 3 gs identities — ALL PASS")

    truth = {
        "truth_id": "safc1909_p24_france_trade_1843_1872",
        "table": "Total imports and exports of merchandise, and imports and exports of gold and silver (FRANCE, continued)",
        "page_pdf_1indexed": 24,
        "rows": 30,
        "years": [1843, 1872],
        "sign_convention": "excess = exports - imports; negative = excess of imports, positive = excess of exports; printed as - or + beside the excess value",
        "unit_all_columns": "1,000 dollars (printed '1,000 dollars.' beneath every numeric column header)",
        "columns": [
            {"key": "year", "group_l1": None, "group_l2": None, "leaf": "YEAR."},
            {"key": "gt_imports", "group_l1": "MERCHANDISE", "group_l2": "General trade", "leaf": "Imports"},
            {"key": "gt_exports", "group_l1": "MERCHANDISE", "group_l2": "General trade", "leaf": "Exports"},
            {"key": "gt_excess", "group_l1": "MERCHANDISE", "group_l2": "General trade", "leaf": "Excess of imports (-) or exports (+)"},
            {"key": "st_imports", "group_l1": "MERCHANDISE", "group_l2": "Special trade", "leaf": "Imports"},
            {"key": "st_exports", "group_l1": "MERCHANDISE", "group_l2": "Special trade", "leaf": "Exports"},
            {"key": "st_excess", "group_l1": "MERCHANDISE", "group_l2": "Special trade", "leaf": "Excess of imports (-) or exports (+)"},
            {"key": "gold_imports", "group_l1": "PRECIOUS METALS", "group_l2": "Gold", "leaf": "Imports"},
            {"key": "gold_exports", "group_l1": "PRECIOUS METALS", "group_l2": "Gold", "leaf": "Exports"},
            {"key": "gold_excess", "group_l1": "PRECIOUS METALS", "group_l2": "Gold", "leaf": "Excess of imports (-) or exports (+)"},
            {"key": "silver_imports", "group_l1": "PRECIOUS METALS", "group_l2": "Silver", "leaf": "Imports"},
            {"key": "silver_exports", "group_l1": "PRECIOUS METALS", "group_l2": "Silver", "leaf": "Exports"},
            {"key": "silver_excess", "group_l1": "PRECIOUS METALS", "group_l2": "Silver", "leaf": "Excess of imports (-) or exports (+)"},
            {"key": "gs_imports", "group_l1": "PRECIOUS METALS", "group_l2": "Gold and silver", "leaf": "Imports"},
            {"key": "gs_exports", "group_l1": "PRECIOUS METALS", "group_l2": "Gold and silver", "leaf": "Exports"},
            {"key": "gs_excess", "group_l1": "PRECIOUS METALS", "group_l2": "Gold and silver", "leaf": "Excess of imports (-) or exports (+)"},
        ],
        "construction": {
            "method": "human transcription from rendered page (300 dpi full-page pass, 600 dpi row-band passes, zoomed single-cell re-reads)",
            "arbitration": "connected-component glyph analysis at 600 dpi (font metrics: serif-1 width 15-21px, open-4 width 9-12px) plus right-alignment digit counting",
            "verification": "five printed-table identities hold exactly (excess=exports-imports for 5 groups; gold+silver=gs for 3 leaves); all 30 rows verified programmatically at build time",
            "contested_cells": CONTESTED,
            "contested_count": len(CONTESTED),
            "contested_excluded_from_scoring": False,
            "note_contested": "contested cells carry the adopted reading and documented alternatives; the evaluator additionally reports metrics excluding contested cells as a sensitivity check",
        },
        "geometry_600dpi": GEOMETRY_600DPI,
        "rows_data": [{"year": y, **dict(zip(COLS, vals))} for y, vals in ROWS],
    }
    out = HERE / "truth_p24.json"
    out.write_text(json.dumps(truth, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes): 30 rows x 15 columns = {30*15} numeric cells + 30 year labels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
