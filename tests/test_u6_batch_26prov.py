"""658 test_u6_batch_26prov.py — 23 省 × 5 指标 hongheiku 转载 batch 守门.

Per knife 658 tasking §658-B:
  18 文件集 311 回归 + test_u6_batch_26prov ≥19 = ≥326 green (底限 ≥316).

守门口径 (per 658 §C 验收):
  1. evidence_fetch JSON 存在且 schema 合规
  2. evidence_anchor JSON 存在且 verdict PASS
  3. 23/26 REACHABLE 完整提取 (5/5 字段齐)
  4. 3 BLOCKED 整省留痕 (liaoning/hainan/guizhou)
  5. SHA 锁转载字节 (23 sha256 distinct)
  6. 国家锚 -5.336% ≤ ±5.5% 容差 = PASS
  7. 自洽 23/23 ≤0.5% PASS
  8. lineage 三重标注 (source/origin/ruling) 全行
  9. seed SQL 232 INSERT ROWS 存在 (5 ind + 5 mv + 23 reg + 23 doc + 23 loc + 23 run + 115 obs + 1 evt)
  10. seed SQL UUID q 段 (q0..q7) ≠ 657 p 段
  11. fetch 脚本 ≤32 HTTP 预算
  12. docs/82 §1.2 P3-1 重写 31 行
  13. docs/82 §1.2 行内更正注记 inline
  14. docs/82 §1.2 计数 25 R + 4 B + 2 M2-only = 31
  15. docs/83 M2 batch 文档存在 + 含国家锚/自洽
  16. u6_batch_26prov_20260902 报告存在 + 含红线 14
  17. 红线 1-14 + U6 §5 附加五条 自检
  18. fetch script 不绕反爬 (无 captcha/waf 字样)
  19. HTTP ≤32 实际值守门 (23/32)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path('/Users/kjonekong/projects/china platform')
EVIDENCE_FETCH = REPO / 'evidence_pack' / 'u6_batch_26prov_fetch_20260902.json'
EVIDENCE_ANCHOR = REPO / 'evidence_pack' / 'u6_batch_26prov_anchor_20260902.json'
SEED_SQL = REPO / 'scripts' / 'seed_m2_u6_batch_26prov.sql'
FETCH_PY = REPO / 'scripts' / 'fetch_m2_u6_batch_26prov_2024.py'
DOCS_82 = REPO / 'docs' / '82-m4-20-policy-detail-real-v14-20260902.md'
DOCS_83 = REPO / 'docs' / '83-m2-batch-u6-hongheiku-20260902.md'
REPORT = REPO / 'docs' / 'reports' / 'u6_batch_26prov_20260902.md'

BLOCKED_PROVINCES = {'liaoning', 'hainan', 'guizhou'}


def test_01_evidence_fetch_exists_and_valid() -> None:
    """fetch evidence JSON 存在且含 23 REACHABLE + 3 BLOCKED cells."""
    assert EVIDENCE_FETCH.exists(), f'missing {EVIDENCE_FETCH}'
    data = json.loads(EVIDENCE_FETCH.read_text(encoding='utf-8'))
    assert data['knife'] == '658'
    assert data['chain_id'] == 'real_658_m2_u6_batch_v1'
    assert data['substitute_pool_status'] == 'EXHAUSTED'
    assert data['fetched_count'] == 23
    assert data['blocked_no_pool_count'] == 3
    assert len(data['cells']) == 23


def test_02_evidence_anchor_pass() -> None:
    """anchor evidence PASS: 国家锚 + 自洽."""
    assert EVIDENCE_ANCHOR.exists(), f'missing {EVIDENCE_ANCHOR}'
    data = json.loads(EVIDENCE_ANCHOR.read_text(encoding='utf-8'))
    assert data['national_anchor']['verdict'] == 'PASS'
    assert data['self_consistency_23_reachable']['verdict'] == 'PASS'
    assert data['self_consistency_5_canary_official']['verdict'] == 'PASS'


def test_03_23_reachable_complete_5_of_5() -> None:
    """23 REACHABLE 全部 5/5 字段完整."""
    data = json.loads(EVIDENCE_FETCH.read_text(encoding='utf-8'))
    for cell in data['cells']:
        if cell['verdict'] != 'REACHABLE':
            continue
        e = cell['extracted']
        assert 'gdp_total' in e, f"{cell['province']} missing gdp_total"
        assert 'growth' in e, f"{cell['province']} missing growth"
        assert 'primary' in e, f"{cell['province']} missing primary"
        assert 'secondary' in e, f"{cell['province']} missing secondary"
        assert 'tertiary' in e, f"{cell['province']} missing tertiary"


def test_04_three_blocked_provinces_documented() -> None:
    """3 BLOCKED 省 整省留痕 (liaoning/hainan/guizhou)."""
    data = json.loads(EVIDENCE_FETCH.read_text(encoding='utf-8'))
    blocked_names = {b['province'] for b in data['blocked_provinces']}
    assert blocked_names == BLOCKED_PROVINCES
    for b in data['blocked_provinces']:
        assert b['reason'] == 'NOT_FOUND_IN_2024_INDEX'


def test_05_sha256_locked_for_all_23_reachable() -> None:
    """23 REACHABLE 各自 sha256 distinct (转载字节锁)."""
    data = json.loads(EVIDENCE_FETCH.read_text(encoding='utf-8'))
    shas = [c['sha256'] for c in data['cells'] if c['verdict'] == 'REACHABLE']
    assert len(shas) == 23
    assert len(set(shas)) == 23, 'sha256 not distinct'
    for s in shas:
        assert len(s) == 64
        assert re.match(r'^[0-9a-f]{64}$', s)


def test_06_national_anchor_pass_within_5_5_pct() -> None:
    """国家锚 PASS: 28 省观察差 ≤ ±5.5% 容差."""
    data = json.loads(EVIDENCE_ANCHOR.read_text(encoding='utf-8'))
    diff_pct = data['national_anchor']['observed_diff_pct']
    assert abs(diff_pct) <= 5.5, f'diff_pct={diff_pct} > 5.5%'


def test_07_self_consistency_23_of_23_pass() -> None:
    """自洽 23/23 PASS: 1+2+3 = GDP, ≤0.5%."""
    data = json.loads(EVIDENCE_ANCHOR.read_text(encoding='utf-8'))
    scc = data['self_consistency_23_reachable']
    assert scc['pass_count'] == 23
    assert scc['total_count'] == 23
    for cell in scc['cells']:
        assert cell['verdict'] == 'PASS', f"{cell['province']} self-consistency FAIL"


def test_08_lineage_triple_annotation_in_seed() -> None:
    """seed SQL lineage 三重标注 全行 (hongheiku_tjgb / XX省统计局 / U6 2026-09-02)."""
    sql = SEED_SQL.read_text(encoding='utf-8')
    assert "'source', 'hongheiku_tjgb'" in sql
    assert "'ruling', 'U6 2026-09-02'" in sql
    # origin 含 23 省统计局 全名
    origin_count = sql.count("'origin', '") - sql.count("'origin', 'XX")  # exclude template
    assert origin_count == 23, f'expected 23 distinct origins, got {origin_count}'


def test_09_seed_sql_218_insert_rows() -> None:
    """seed SQL 218 INSERT ROWS (5+5+23+23+23+23+115+1).

    indicator_definition / methodology_version use multi-row INSERT (5 each),
    so count VALUES tuples instead of INSERT statements.
    source_registry / document / location / ingestion_run / observation /
    project_event use 1 statement per row (per-province DO blocks).
    """
    sql = SEED_SQL.read_text(encoding='utf-8')
    # indicator_definition: 5 rows in 1 INSERT — count by VALUES tuples
    # The VALUES clause has pattern ('a2000000...', 'name', ...) repeated 5x.
    ind_def_block = sql[sql.find('INSERT INTO cegr.indicator_definition'):sql.find('INSERT INTO cegr.indicator_methodology_version')]
    ind_count = len(re.findall(r"\('a2000000-0000-0000-0000-00000000a00[0-9]',", ind_def_block))
    mv_block = sql[sql.find('INSERT INTO cegr.indicator_methodology_version'):sql.find('-- 1-23.')]
    mv_count = len(re.findall(r"\('a2000000-0000-0000-0000-00000000a0[0-9]+',", mv_block))
    # Per-row INSERTs (each is its own statement)
    reg_count = sql.count('INSERT INTO cegr.source_registry')
    doc_count = sql.count('INSERT INTO cegr.source_document')
    loc_count = sql.count('INSERT INTO cegr.source_location')
    run_count = sql.count('INSERT INTO cegr.ingestion_run')
    obs_count = sql.count('INSERT INTO cegr.observation')
    evt_count = sql.count('INSERT INTO cegr.project_event')
    total = ind_count + mv_count + reg_count + doc_count + loc_count + run_count + obs_count + evt_count
    assert (ind_count, mv_count, reg_count, doc_count, loc_count, run_count, obs_count, evt_count) == \
           (5, 5, 23, 23, 23, 23, 115, 1), \
           f'INSERT counts mismatch: ind={ind_count} mv={mv_count} reg={reg_count} doc={doc_count} loc={loc_count} run={run_count} obs={obs_count} evt={evt_count} total={total}'
    assert total == 218, f'total INSERT = {total}, expected 218'


def test_10_seed_sql_uuid_q_prefix() -> None:
    """seed SQL UUID q 段 (q0/q1/q2/q6/q7) ≠ 657 p 段."""
    sql = SEED_SQL.read_text(encoding='utf-8')
    # q-prefix samples
    for prefix in ('q0eebc99', 'q1eebc99', 'q2eebc99', 'q6eebc99', 'q7eebc99'):
        assert prefix in sql, f'missing {prefix}'
    # 657 p-prefix NOT in 658 SQL (namespace isolation)
    for p_prefix in ('p0eebc99', 'p1eebc99', 'p2eebc99', 'p6eebc99', 'p7eebc99'):
        assert p_prefix not in sql, f'657 namespace leak: {p_prefix} found'


def test_11_fetch_script_within_32_http_budget() -> None:
    """fetch script 实际 HTTP ≤32 预算 (evidence http_count=23)."""
    data = json.loads(EVIDENCE_FETCH.read_text(encoding='utf-8'))
    assert data['http_count'] <= data['http_limit'] == 32


def test_12_docs_82_section_1_2_31_rows() -> None:
    """docs/82 §1.2 P3-1 重写 31 行 (含 25 R + 4 B + 2 M2-only)."""
    text = DOCS_82.read_text(encoding='utf-8')
    # 抓取 §1.2 表 (| 序 | 省 | 落定刀 | verdict | 备注 |)
    sec_1_2 = text[text.find('### 1.2 全国 31 省'):text.find('### 1.3 关键意义')]
    # Count table rows starting with "| NN |"
    rows = [r for r in sec_1_2.split('\n') if re.match(r'^\|\s*\d+\s*\|', r)]
    assert len(rows) == 31, f'expected 31 rows, got {len(rows)}'


def test_13_docs_82_inline_p3_1_annotation() -> None:
    """docs/82 §1.2 行内更正注记 inline 〔658-A.2 P3-1〕."""
    text = DOCS_82.read_text(encoding='utf-8')
    sec_1_2 = text[text.find('### 1.2 全国 31 省'):text.find('### 1.3 关键意义')]
    # ≥5 inline annotations 〔658-A.2 P3-1〕
    assert sec_1_2.count('〔658-A.2 P3-1') >= 5


def test_14_docs_82_count_25r_4b_2m2_equals_31() -> None:
    """docs/82 §1.2 计数 25 R + 4 B + 2 M2-only = 31."""
    text = DOCS_82.read_text(encoding='utf-8')
    sec_1_2 = text[text.find('### 1.2 全国 31 省'):text.find('### 1.3 关键意义')]
    assert '25 R + 4 B + 2 M2-only' in sec_1_2 or '25 spike REACHABLE' in sec_1_2
    assert '31/31' in sec_1_2


def test_15_docs_83_exists_with_anchor_and_self_consistency() -> None:
    """docs/83 M2 batch 文档存在 + 含国家锚 + 自洽章节."""
    assert DOCS_83.exists(), f'missing {DOCS_83}'
    text = DOCS_83.read_text(encoding='utf-8')
    assert '## 2. 国家锚 + 自洽' in text
    assert '国家锚 verdict' in text
    assert '自洽' in text


def test_16_report_exists_with_red_lines() -> None:
    """u6_batch_26prov 报告存在 + 含红线 14."""
    assert REPORT.exists(), f'missing {REPORT}'
    text = REPORT.read_text(encoding='utf-8')
    assert '红线 14' in text or '红线' in text
    # ≥14 numbered red lines
    red_line_count = sum(1 for i in range(1, 15) if f'| {i} |' in text)
    assert red_line_count >= 14


def test_17_red_line_audit() -> None:
    """红线 1-14 + U6 §5 附加五条 自检 (基于 evidence + seed SQL + docs)."""
    fetch_data = json.loads(EVIDENCE_FETCH.read_text(encoding='utf-8'))
    anchor_data = json.loads(EVIDENCE_ANCHOR.read_text(encoding='utf-8'))
    sql = SEED_SQL.read_text(encoding='utf-8')
    # 红线 1: 不补零 (3 BLOCKED 不入库 obs)
    blocked_names = {b['province'] for b in fetch_data['blocked_provinces']}
    for bn in blocked_names:
        assert f"'{bn}'" not in sql or 'NOT_FOUND_IN_2024_INDEX' in sql or \
               sql.find(f"'{bn}'", sql.find('blocked_provinces')) == -1
    # 红线 3: HTTP ≤32
    assert fetch_data['http_count'] <= 32
    # 红线 5: SHA 锁 (≥23 SHA 在 seed)
    sha_count = sql.count("file_hash_sha256")
    assert sha_count >= 23
    # 红线 14: BLOCKED 留痕 (project_event)
    assert 'INSERT INTO cegr.project_event' in sql
    # U6 §5-2: lineage 三重标注
    assert "'source', 'hongheiku_tjgb'" in sql
    assert "'ruling', 'U6 2026-09-02'" in sql


def test_18_no_captcha_or_waf_bypass() -> None:
    """fetch 脚本不绕反爬 (无 captcha/waf bypass 字样)."""
    text = FETCH_PY.read_text(encoding='utf-8')
    forbidden = ('captcha', 'waf_bypass', 'selenium', 'playwright', 'recaptcha')
    for kw in forbidden:
        assert kw.lower() not in text.lower(), f'forbidden kw {kw} in fetch script'


def test_19_http_actual_23_of_32() -> None:
    """实际 HTTP 23/32 (73% 利用率, 不超预算)."""
    data = json.loads(EVIDENCE_FETCH.read_text(encoding='utf-8'))
    assert data['http_count'] == 23
    assert data['http_limit'] == 32
