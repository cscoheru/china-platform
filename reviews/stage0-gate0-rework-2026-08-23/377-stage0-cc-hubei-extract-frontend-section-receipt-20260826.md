# 377 — 湖北 REGISTRY_SAMPLE 前端分节 · CC 回执

- 编号：`377-stage0-cc-hubei-extract-frontend-section-receipt-20260826`
- 任务书：`376-stage2-hubei-provincial-sample-extract-frontend-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<待回填>`
- 日期：2026-08-26

---

## §NOW 对照

| 376 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `--from-local-sample --allow-disabled-local-sample --pilot-domain=tjj.hubei.gov.cn --pilot-category=PROVINCIAL_BULLETIN` 写出 extract ≥1 行（期望 ≈21） | ✅ rc=0：21 行 / sha `c5cf5abeb4fdf97a…`（registry 锚吻合）/ WORM `data/public_archives/2026-08/tjj.hubei.gov.cn/hubei_2026_06.xlsx`（幂等未变）/ lineage JSONL `REGISTRY_SAMPLE_INTAKED`（is_demo=true）；`extract_xlsx_tables()` 复用现有 connector 路由（NATIONAL/MUNICIPAL/PROVINCIAL 三类 dispatcher 已覆盖） | 下文证据 |
| (2) `frontend/lib/public_extract_hubei.json` 快照 + `/public-extracts` **第四分节**（显式 REGISTRY_SAMPLE / demo；注明 live `enabled=FALSE` 暂缓，**非** live） | ✅ byte-verbatim 快照（`cp` 后 sha256 双侧一致：`9056001c…`）；第四区块追加在 NBS sample/live + 深圳 sample 三区块之后：`hb-registry-sample` section — h2「湖北月报样本提取 — PROVINCIAL_BULLETIN (REGISTRY_SAMPLE, xlsx)」+ DemoBadge（is_demo="true"，demo_reason 注明 `--from-local-sample --allow-disabled-local-sample; live enabled=FALSE 暂缓; 非 live O1`）+ 免责声明（REGISTRY_SAMPLE / demo / xlsx 提取 / live FALSE 暂缓 / 与 NBS+深圳三轨分轨互不覆盖）+ 8 字段 provenance 表 + 21 行月报统计表（列序 = 首行键序，含空列名 + 前导空格原样保留）+ 尾注（live 仍暂缓 enabled=FALSE / JS-shell tech-blocked / per Cursor 341） | `page.tsx` diff |
| (3) 不覆盖 NBS 三轨既有 fixture | ✅ smoke §12e 配套：HB fixture 在位 + 页面针；NBS 三轨契约（63 行 / `dea13b8a…`、LIVE_CANDIDATE `0b85212f…`、SZ 71 行 / `d5e2c731…`）+ HB 互不覆盖交叉检查 | 自检 + smoke |
| (4) ≥3 pytest（湖北 ≥1 行 + NBS/深圳不回归）+ smoke 针 | ✅ **+3 pytest**（超出 ≥3）；连跑 **103 passed**（100+3）+ smoke **§12e 新 gate** PASS + `next build` rc=0（`/public-extracts` ○ Static 160 B，22/22 页静态生成） | 下文证据 |
| (5) 回执 `377`（`-cc-` 名） | ✅ 本文件名 | — |

## 新增测试 3 case（`tests/test_public_extract_frontend_fixture.py`）

1. `test_hb_fixture_mirrors_extract_and_shape` — fixture 与 extract dict 级相等 + 形状锚（tjj.hubei.gov.cn / PROVINCIAL_BULLETIN / 21 行 / sha `c5cf5abeb4fdf97a…` / WORM 尾段）
2. `test_hb_track_isolated_from_nbs_and_sz` — 分轨不回归 + HB 不冒充 live（NBS 63/`dea13b8a…`、live LIVE_CANDIDATE/`0b85212f…`、SZ `d5e2c731…` 全不变；HB sha/row_count 均与三轨不同；`LIVE_CANDIDATE` 不出现在 HB `intake_status`）
3. `test_page_renders_hb_registry_sample_track` — 页面针：`public_extract_hubei.json` import / `PROVINCIAL_BULLETIN` / 「月报统计表」/「enabled=FALSE」；且不出现 `O1_AUTO_INTAKED`

## smoke §12e 新 gate（`frontend/smoke-check.py`）

- HB fixture 在位：domain `tjj.hubei.gov.cn`、category `PROVINCIAL_BULLETIN`、`row_count==21==len(rows)`、sha 前缀 `c5cf5abeb4fdf97a`
- 页面针（**先剥注释再扫**，per 红线惯例）：`public_extract_hubei.json` / `PROVINCIAL_BULLETIN` / 「月报统计表」/「enabled=FALSE」
- 与 §12c/§12d 共同确保 NBS 双轨 + 深圳 + 湖北四轨互不覆盖

## 证据

```
$ python3 scripts/auto_ingest_public_source.py \
    --pilot-domain=tjj.hubei.gov.cn --pilot-category=PROVINCIAL_BULLETIN \
    --from-local-sample --allow-disabled-local-sample \
    --confirm-live=reviews/.../20260826-local-sample-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.jsonl
OK local-sample pilot matched: tjj.hubei.gov.cn / PROVINCIAL_BULLETIN (enabled=FALSE)
OK archived: data/public_archives/2026-08/tjj.hubei.gov.cn/hubei_2026_06.xlsx
OK extract JSON: data/public_extracts/tjj.hubei.gov.cn/PROVINCIAL_BULLETIN.json
OK lineage: reviews/.../20260826-local-sample-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.jsonl
OK REGISTRY_SAMPLE_INTAKED (is_demo=true; sample ≠ live closure). rc=0

$ python3 -c "..." # 交付产物核验
rows: 21 | sha: c5cf5abeb4fdf97a... | 12 列首行 + 21 行末行覆盖

$ shasum -a 256 data/public_extracts/tjj.hubei.gov.cn/PROVINCIAL_BULLETIN.json \
    frontend/lib/public_extract_hubei.json
9056001c... (双侧一致 — byte-verbatim 快照)

$ python3 -m pytest tests/test_auto_ingest_public_source_s52.py \
    tests/test_public_extract_frontend_fixture.py -q
103 passed in 3.26s         # 100 + 3

$ python3 frontend/smoke-check.py
=== … smoke: PASS ===       # 含新 §12e

$ cd frontend && npm run build
✓ Compiled successfully
✓ Generating static pages (22/22)
├ ○ /public-extracts   160 B   87.2 kB    # 静态预渲染, 无 params.* 分支
build-rc=0
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/lib/public_extract_hubei.json` | NEW（byte-verbatim 快照，21 行 xlsx） | `data_contract_suite` |
| `frontend/app/public-extracts/page.tsx` | MODIFIED（+第四分节；NBS+深圳三区块零改动） | 已入 manifest（SKIP） |
| `frontend/smoke-check.py` | MODIFIED（+§12e gate） | 已入 manifest（SKIP） |
| `tests/test_public_extract_frontend_fixture.py` | MODIFIED + 新增 3 case | 已入 manifest（SKIP） |
| `data/public_extracts/tjj.hubei.gov.cn/PROVINCIAL_BULLETIN.json` | NEW（21 行，git 跟踪） | `data_contract_suite`（**待补登记**） |
| `data/public_archives/2026-08/tjj.hubei.gov.cn/hubei_2026_06.xlsx` | NEW（WORM 幂等归档） | 不入 pack（_knife47/48 先例） |
| `reviews/.../20260826-local-sample-tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.jsonl` | NEW（lineage，git 跟踪） | 不入 pack（_knife47/48 先例） |
| `scripts/_knife61_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../377-stage0-cc-hubei-extract-frontend-section-receipt-20260826.md` | NEW（本文件） | `documentation` |

**已与 knife 58 对齐**：hubei extract JSON 一并登记入 pack（`data_contract_suite`），与 sz extract 同类。

## Pack 不变量

`_knife61_manifest_bump.py`：NEW_ARTIFACTS +4（hubei extract + fixture + bump + receipt）→ **684 → 688**；`sum(role_count) == artifact_count == len(artifacts) == 688`。

## 红线自查

- ❌ 未启用湖北 live（`--allow-disabled-local-sample` 仅放行 local-sample 路径；live 探测 `enabled=FALSE` 仍 FALSE；未改 registry `enabled` 列；未 headless）
- ❌ 未覆盖 NBS+深圳三轨（fixture 契约测试 + smoke §12c/§12d/§12e 交叉检查：63 行 / `dea13b8a…`、LIVE_CANDIDATE / `0b85212f…`、71 行 / `d5e2c731…` 全不变）
- ❌ 未谎称 live（DemoBadge + 免责声明均标 REGISTRY_SAMPLE / demo / live FALSE 暂缓 / 非 live O1；未做湖北 HTTPS 探测，per 376 §不做）
- ❌ 未 Gate/O1 PASS 宣言；未动 `00-CC-CURRENT.md` / `gate_thresholds.json`；未 --force；未索要 PAT
- ✅ 静态路由无 `params.*` 分支（纯 fixture 消费，build 确认 ○ Static）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`git push origin HEAD && git push github HEAD` → `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 378）。