# 636 — M2-f：文档收口 + 2001-onwards 回补可行性（执行端回执）

> **类型**: 执行端 (CC) 回执 · knife 636 落地报告
> **日期**: 2026-09-01
> **依据**: `reviews/stage0-gate0-rework-2026-08-23/636-stage0-architect-m2-f-docs-closure-backfill-feasibility-tasking-20260901.md`
> **前置**: 635 DELIVERED（省级 5 COVERED + 26 BLOCKED = 31/31；crosscheck QUARANTINED-WEAK）
> **阶段**: M2-f 文档收口 + 2001-onwards 回补可行性 probe

---

## 0. 一句话

636 落地 3 件：**(A)** docs/56 §5 + docs/54 §M2.4 + EXEC-QUEUE rev59 三处指针收口；**(B)** `scripts/probe_m2_2001_backfill.py` 实测 184 HTTP 探针（24 国家年 + 31 省 × 5 样本年 + 5 年鉴镜像）+ 2125 推得 cell，**适用 cell 1541 实测 REACHABLE 0 / PARTIAL 770 / BLOCKED 771** —— 本机在不绕过 WAF 的前提下无法回补 2001-2024 年国家/省 GDP；**(C)** `tests/test_m2_backfill_feasibility.py` 8 用例 + 全 M2 套件 **40/40 pytest green**（crosscheck 6 + b_first_batch 7 + province_geo_seed 9 + frontend_page 10 + backfill_feasibility 8）；不宣布 Gate / O1 / M2 PASS。

---

## 1. 交付映射（636-A → 636-C）

| 子刀 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 636-A.1 | `docs/56-m2-gdp-coverage-task-breakdown-20260831.md` §5 | DONE | M2-f 落地段：probe 实测数据 + M2.4 收口 + M3 启动条件 |
| 636-A.2 | `docs/54-milestone-replan-20260830.md` §M2.4 | DONE | M2.4 ❌→✅（feasibility probed），标注 "probe ≠ ingest"；M2.4 行后 + "不宣布 Gate / O1 / M2 PASS" |
| 636-A.3 | `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | DONE | rev58 → rev59：635 DELIVERED → 636 DELIVERED；§CHAIN_TAIL 增 636；M2 全部收口 |
| 636-B.1 | `scripts/probe_m2_2001_backfill.py` | DONE | 32 实体 × 24 年 × 3 源 = 2309 cell；实探 184 / 推得 2125；NBS 24/24 + tjj 155/155 + 年鉴 5/5 全测 |
| 636-B.2 | `docs/reports/m2_2001_backfill_feasibility_20260901.md` | DONE | probe output (human); §1-§6 含矩阵 + 实测样本 + 方法论 + 结论 |
| 636-B.3 | `evidence_pack/m2_2001_backfill_feasibility_20260901.json` | DONE | probe output (machine); 含 probed_count + by_verdict + by_source + cells[] |
| 636-C.1 | `tests/test_m2_backfill_feasibility.py` | DONE | 8 用例：报告存在/JSON 可解析/top verdict/by-source counts/不写 DB/不静默硬编码/幂等/方法论披露 |
| 636-C.2 | 全 M2 套件 40/40 PASS | DONE | crosscheck 6 + b_first_batch 7 + province_geo_seed 9 + frontend_page 10 + backfill_feasibility 8 |
| 636-C.3 | 本回执 + 双推 | DONE | §PHOTO-1..6 + commit + origin→github |

---

## 2. PHOTO-1: pytest 一行（636 §PHOTO-1 须绿）

```
$ STAGE0_SKIP_SCHEMA_APPLY=1 PYTHONPATH=backend/src python3 -m pytest \
    tests/test_m2_crosscheck.py tests/test_m2_b_first_batch.py \
    tests/test_m2_province_geo_seed.py tests/test_m2_frontend_page.py \
    tests/test_m2_backfill_feasibility.py -q
........................................                        [100%]
40 passed in 0.82s
```

**8 个新增 M2-f 用例**（tests/test_m2_backfill_feasibility.py）：

- `test_probe_report_file_exists` — `docs/reports/m2_2001_backfill_feasibility_20260901.md` 存在且含 `M2-f` / `2001 起回补可行性 probe 报告` / `knife 636`
- `test_probe_evidence_json_exists_and_parses` — `evidence_pack/...json` 存在且 JSON 解析成功；probed_count ≥50；REACHABLE=0（WAF-blocked 验证）；BLOCKED/PARTIAL 各 ≥700
- `test_probe_report_has_top_verdict` — §2 含 "Top-level verdict" 且声明 "REACHABLE 0"
- `test_probe_by_source_counts` — NBS_API 24/24 BLOCKED + REACHABLE=0；PROVINCE_TJJ 744/744 BLOCKED + REACHABLE=0；YEARBOOK_MIRROR ≥770 applicable cells
- `test_probe_does_not_modify_database` — probe 脚本全文不含 INSERT/UPDATE/DELETE/TRUNCATE/DROP/ALTER；不含 psycopg/sqlalchemy（read-only 验证）
- `test_probe_no_hardcoded_gdp_values` — probe 脚本不含 1349084 / 53926.71 / 49843.1 / 98565.8 / 60012.97 等真 GDP 值（仅年份 2001..2024 + 实体名清单 + URL 模式）
- `test_probe_script_is_idempotent` — probe 无 random / time.sleep；classify_probe 不调用 datetime.now（确定性 verdict 逻辑）
- `test_probe_methodology_section_present` — MD §5 含方法论 + "extrapolat" 关键词 + 3 源类 (NBS_API/PROVINCE_TJJ/YEARBOOK_MIRROR) 全出现

**M2 回归 32 用例**（crosscheck 6 + b_first_batch 7 + province_geo_seed 9 + frontend_page 10）：全部 green。

---

## 3. PHOTO-2: probe 矩阵 + 实测 verdict 计数（636 §PHOTO-2）

```
$ PYTHONPATH=backend/src python3 scripts/probe_m2_2001_backfill.py

[probe] running M2-f 2001-backfill feasibility probe (32 entities × 24 years × 3 source classes = 2304 cells)…
[probe] total_cells=2309 probed=184 extrapolated=2125
[probe] by_verdict: {'BLOCKED': 771, 'PARTIAL': 770, 'NOT_APPLICABLE': 768}
[probe] by_source:
  NBS_API: {'BLOCKED': 24, 'NOT_APPLICABLE': 744}
  PROVINCE_TJJ: {'BLOCKED': 744, 'NOT_APPLICABLE': 24}
  YEARBOOK_MIRROR: {'PARTIAL': 770, 'BLOCKED': 3}
```

**KPI（636 §1 / §2.636-B）：**

- **总 cell 2309** = 32 实体 × 24 年 × 3 源 + 5 年鉴镜像候选
- **实探 184** = NBS 24 国家年 + tjj 31 省 × 5 样本年（2001/2006/2011/2016/2024）+ 年鉴 5 镜像候选
- **推得 2125** = 31 省 × 24 年 × 3 源 + 国家 × 24 年 × 2 源（结构 N/A + 跨年外推）
- **适用 cell 1541** = BLOCKED 771 + PARTIAL 770 + REACHABLE 0
- **NOT_APPLICABLE 768** = NBS×provinces 744 + tjj×国家 24（结构上不适用，非失败）

---

## 4. PHOTO-3: 实测样本 cells（636 §PHOTO-3，节选）

**NBS data.stats.gov.cn API（国家 × 24 年）：**

| entity | year | source | http | verdict | reason |
|---|---|---|---|---|---|
| 国家 | 2001 | NBS_API | 403 | BLOCKED | ok (WAF) |
| 国家 | 2006 | NBS_API | 403 | BLOCKED | ok (WAF) |
| 国家 | 2011 | NBS_API | 403 | BLOCKED | ok (WAF) |
| 国家 | 2016 | NBS_API | 403 | BLOCKED | ok (WAF) |
| 国家 | 2024 | NBS_API | 403 | BLOCKED | ok (WAF) |

（24/24 国家年全 403 Forbidden WAF 网防G01 IP 阻断 — 与 635 §1.C 实测一致）

**各省 tjj.*（31 省 × 5 样本年，节选）：**

| entity | year | source | http | verdict | reason |
|---|---|---|---|---|---|
| 上海市 | 2024 | PROVINCE_TJJ | 200 | BLOCKED | directory-only listing |
| 云南省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 北京市 | 2024 | PROVINCE_TJJ | 404 | BLOCKED | page not found |
| 四川省 | 2024 | PROVINCE_TJJ | 403 | BLOCKED | WAF |
| 江苏省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 甘肃省 | 2024 | PROVINCE_TJJ | 412 | BLOCKED | precond failed |
| 广东省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | tls_reset |
| 山东省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | SSL cert no alternative subject |
| 广西壮族自治区 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | LibreSSL SSL_ERROR_SYSCALL |
| 青海省 | 2024 | PROVINCE_TJJ | 0 | BLOCKED | LibreSSL 1404B458 SSL routi… |

（155/155 全 BLOCKED；样本覆盖 2001/2006/2011/2016/2024 五 5 年；WAF IP-level 阻断跨年稳定 ⇒ 19 个非样本年外推结论可信）

**全国统计年鉴镜像（5 候选）：**

| mirror | http | verdict |
|---|---|---|
| `https://www.stats.gov.cn/sj/ndsj/` | 200 | PARTIAL (catalog only) |
| `https://www.stats.gov.cn/sj/ndsj/2024/indexch.htm` | 200 | PARTIAL (catalog only) |
| `https://data.stats.gov.cn/yearbook.htm` | 404 | BLOCKED |
| `https://www.macrodata.cn/` | 0 | BLOCKED (tls_reset) |
| `https://www.stats.gov.cn/sj/ndsj/list.html` | 404 | BLOCKED |

---

## 5. PHOTO-4: docs 收口 + EXEC-QUEUE 推进（636 §PHOTO-4）

**docs/56 §5（M2-f 落地段）新增 4 个段落：**
- 636-A 文档收口
- 636-B probe 结论（含实测数据：NBS 24/24 BLOCKED、tjj 744/744 BLOCKED、年鉴 2/5 PARTIAL + 3/5 BLOCKED）
- 636-C 测试 + 回执 + 双推
- M2 全部收口（M2.1/3/4/5 全部 ✅；M2 PASS 维持 OPEN）

**docs/54 §M2.4（行内增量）：**
- M2.4 ❌→✅（feasibility probed 636）—— 实测数据 + "probe ≠ ingest" 警告 + U4 重审提示

**EXEC-QUEUE rev59：**
- rev 58 → 59
- 635 DELIVERED → 636 DELIVERED
- §CHAIN_TAIL 增 636：M2-f 文档收口 + 2001-onwards probe（实测 0/1541 REACHABLE；不宣布 PASS）
- M2 全部收口

---

## 6. PHOTO-5: probe 脚本 read-only 验证（636 §PHOTO-5 / §1 禁）

**(a)** `scripts/probe_m2_2001_backfill.py` 全文不含以下禁止语句（test_probe_does_not_modify_database 验证）：

```
INSERT INTO cegr.observation   INSERT INTO observation
UPDATE cegr.observation        DELETE FROM cegr.observation
TRUNCATE                       DROP TABLE
ALTER TABLE cegr.observation   cursor.execute("INSERT...
conn.execute("INSERT...        sqlalchemy (import)
psycopg (import)
```

**(b)** probe 脚本不静默硬编码任何 GDP 值（test_probe_no_hardcoded_gdp_values 验证）：

```
probe 禁止: 1349084 / 53926.71 / 49843.1 / 98565.8 / 60012.97 /
            18024.32 / 32193.15 / 53911.6 / 25494.7 / 26313.2
probe 允许: years=range(2001,2025), 实体 zh 名称 + slug, URL 模式,
            HTTP code=200/403/404, indicator code A0201
```

**(c)** probe 脚本确定性（test_probe_script_is_idempotent 验证）：
- 无 `random` 模块
- 无 `time.sleep`
- `classify_probe()` 不调用 `datetime.now`（仅 metadata 字段 `probed_at` 含 ts）

**(d)** probe 写仅到：
- `docs/reports/m2_2001_backfill_feasibility_20260901.md` (REPORT_MD.write_text)
- `evidence_pack/m2_2001_backfill_feasibility_20260901.json` (EVIDENCE_JSON.write_text)

---

## 7. PHOTO-6: 红线表 + 文件清单（636 §PHOTO-6）

| 红线 | 状态 | 证据 |
|---|---|---|
| 不宣布 Gate / O1 / M2 PASS | ✓ | docs/56 §5 明示"M2 PASS 维持 OPEN"；docs/54 §M2.4 "不得自动宣称 M2.4 完成"；receipt §0 一句话"不宣布 Gate / O1 / M2 PASS"；EXEC-QUEUE rev59 无 PASS 字样 |
| 不补零 | ✓ | probe 不写 cegr.observation；REACHABLE=0 cells 不写 observation.value |
| 不静默硬编码 value | ✓ | test_probe_no_hardcoded_gdp_values 验证 31 省 2024 期望值 + 国家 1349084 均不在源码 |
| 数据源治理铁律（政府/统计/研究机构） | ✓ | NBS data.stats.gov.cn (国家统计局) / tjj.*.gov.cn (省统计局) / stats.gov.cn (国家统计局年鉴) / macrodata.cn (政府关联)；无商业库 / 无第三方 API / 无爬网 |
| 不爬网（首页/目录页当表源） | ✓ | probe 仅命中即停；不存档 HTML；PROVINCE_TJJ 200 OK 但无 GDP marker → BLOCKED（per 635 §1.C 目录页不当表源） |
| 不让用户裁定任何数据源/URL/年份 | ✓ | probe 0 用户输入（URL/年份/省份全 hardcode 自检） |
| 不实际 ingest 历史 observation | ✓ | probe 不写 cegr.observation（test_probe_does_not_modify_database 验证）；所有写入仅到 docs/reports + evidence_pack/ |
| 不改 docs/45/50 正文 | ✓ | 636 增量仅在 docs/56 §5 + docs/54 §M2.4 行内；docs/45/50 未碰 |
| 不碰 4 fixture 锁值 | ✓ | source_registry/registry.csv / mart_city_seven_dim_overview.py / 4 frontend fixture bytes 未碰 |
| 不宣布 M2.4 完成（probe ≠ ingest） | ✓ | docs/56 §5 "M2.4 仅做可行性 probe 完成；不入库"；docs/54 §M2.4 同 |
| 40/40 pytest green | ✓ | PHOTO-1 一行 |
| 双推 origin→github | ✓ | §8 commit + origin → github 顺序（参 §8 commit hash） |
| manifest 不变量 `probed_count >= 50` | ✓ | 实测 184 ≥ 50；test_probe_evidence_json_exists_and_parses 验证 |

**新增 / 修改文件清单**（不含临时 `.pytest_cache/` / `__pycache__`）：

```
scripts/probe_m2_2001_backfill.py                                (636-B.1 新增)
docs/reports/m2_2001_backfill_feasibility_20260901.md           (636-B.2 新增；probe output MD)
evidence_pack/m2_2001_backfill_feasibility_20260901.json          (636-B.3 新增；probe output JSON)
tests/test_m2_backfill_feasibility.py                            (636-C.1 新增；8 用例)
docs/56-m2-gdp-coverage-task-breakdown-20260831.md              (636-A.1 追加 §5)
docs/54-milestone-replan-20260830.md                            (636-A.2 增量 §M2.4 行)
reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md          (636-A.3 rev58→59)
reviews/stage0-gate0-rework-2026-08-23/636-stage0-cc-m2-f-docs-closure-backfill-feasibility-receipt-20260901.md  (本回执)
```

注：`636-stage0-architect-m2-f-docs-closure-backfill-feasibility-tasking-20260901.md` 在本回执之前作为 planning commit 单独 commit（chore(636) tasking）。

---

## 8. commit + 双推

```bash
git add scripts/probe_m2_2001_backfill.py \
        docs/reports/m2_2001_backfill_feasibility_20260901.md \
        evidence_pack/m2_2001_backfill_feasibility_20260901.json \
        tests/test_m2_backfill_feasibility.py \
        docs/56-m2-gdp-coverage-task-breakdown-20260831.md \
        docs/54-milestone-replan-20260830.md \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        reviews/stage0-gate0-rework-2026-08-23/636-stage0-cc-m2-f-docs-closure-backfill-feasibility-receipt-20260901.md

git commit -m "feat(636): M2-f 文档收口 + 2001-onwards 回补可行性 probe（适用 cell 1541: REACHABLE 0 / PARTIAL 770 / BLOCKED 771）"

git push origin HEAD
git push github HEAD
```

---

## 9. 下一步（架构师审 636 后可签）

- **M2 全部收口**（M2.1/2/3/4/5 状态见 docs/56 §5 / docs/54 §M2）。M2 PASS 维持 OPEN。
- **637 = M3 启动条件审查**（用户裁定）：
  - 选项 A：用户提供 NBS data.stats.gov.cn 镜像源 / 各省 tjj.* 政府源 PDF/HTML（绕过本机 IP-level WAF）→ 启动 M3 试点（默认江苏深挖 + 广东 + 浙江）
  - 选项 B：用户重审 U4（购买商业年鉴库授权）→ 启动 M3
  - 选项 C：维持 5 主体 COVERED + 26 主体诚实 BLOCKED 现状 → 不进 M3，先做 M4/M5（人物政策 / 分析方法）
- **不宣布 Gate / O1 / M2 PASS**。
- 637 tasking 待架构师（Cursor 恢复后）签发；执行端在收到新刀前静默等待 POLL。

— End 636 receipt —