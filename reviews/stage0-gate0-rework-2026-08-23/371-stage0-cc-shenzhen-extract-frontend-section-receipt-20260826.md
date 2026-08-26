# 371 — 深圳 REGISTRY_SAMPLE 前端分节 · CC 回执

- 编号：`371-stage0-cc-shenzhen-extract-frontend-section-receipt-20260826`
- 任务书：`370-stage2-shenzhen-extract-frontend-section-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<待回填>`
- 日期：2026-08-26

---

## §NOW 对照

| 370 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) `frontend/lib/public_extract_sz.json` 快照自深圳 MUNICIPAL extract | ✅ byte-verbatim 快照（`cp` 后 sha256 双侧一致：`937255a5…`）；71 行 / sha `d5e2c731…`（registry 锚吻合） | 下文证据 |
| (2) `/public-extracts` 增深圳 REGISTRY_SAMPLE 分节（显式 demo；不覆盖 NBS sample/live） | ✅ 第三区块追加在 NBS live-candidate 之后：`sz-registry-sample` section — h2「深圳公报样本提取 — MUNICIPAL_BULLETIN (REGISTRY_SAMPLE)」+ DemoBadge（is_demo="true"，demo_reason 注明 `--from-local-sample; 2026-08-26 live SSL 暂缓; 非 live O1`）+ 免责声明（REGISTRY_SAMPLE / demo / 散文抽取 / 非 live / 与 NBS 两轨分轨互不覆盖）+ 8 字段 provenance 表（domain/category/intake_status=REGISTRY_SAMPLE_INTAKED/sample 路径/WORM 归档路径/source_sha256/row_count/extracted_at）+ 散文段落表（71 行全量，列序 = 首行键序 `{section, paragraph}`）+ 尾注（SSL BAD_ecPOINT per registry 备注，不构成 live 收口）。NBS sample/live 两区块零改动 | `page.tsx` diff |
| (3) ≥2 pytest + smoke | ✅ **+3 pytest**（超出 ≥2）+ smoke **§12d 新 gate**；连跑 **100 passed**（97+3）+ smoke PASS + `next build` rc=0（`/public-extracts` ○ Static 160 B，22/22 页静态生成） | 下文证据 |
| (4) 回执 `371`（`-cc-` 名） | ✅ 本文件名 | — |

## 新增测试 3 case（`tests/test_public_extract_frontend_fixture.py`）

1. `test_sz_fixture_mirrors_extract_and_shape` — fixture 与交付 extract JSON dict 级相等 + 形状锚（sz.gov.cn / MUNICIPAL_BULLETIN / 71 行 / sha `d5e2c731…` / WORM 尾段）
2. `test_sz_track_isolated_from_nbs` — 分轨不回归：NBS sample 63 行 / `dea13b8a…` 全 sha 不变；live `LIVE_CANDIDATE` + `0b85212f…` 不变；sz 行数与 sha 均与 NBS 两轨不同
3. `test_page_renders_sz_registry_sample_track` — 页面针：`public_extract_sz.json` import / `MUNICIPAL_BULLETIN` / 「散文段落表」/「SSL 暂缓」；且不出现 `O1_AUTO_INTAKED`

## smoke §12d 新 gate（`frontend/smoke-check.py`）

- SZ fixture 在位：domain `sz.gov.cn`、category `MUNICIPAL_BULLETIN`、`row_count==71==len(rows)`、sha 前缀 `d5e2c73196b43cec`
- 页面针（**先剥注释再扫**，per 红线惯例）：`public_extract_sz.json` / `MUNICIPAL_BULLETIN` / 「散文段落表」/「SSL 暂缓」
- NBS 双轨不回归交叉检查：sample 63 行 + `dea13b8a…`（全 sha）+ live `LIVE_CANDIDATE` + `0b85212f…`（前缀）

## 证据

```
$ python3 -m pytest tests/test_auto_ingest_public_source_s52.py \
    tests/test_public_extract_frontend_fixture.py -q
100 passed in 2.09s          # 97 + 3

$ python3 frontend/smoke-check.py
=== … smoke: PASS ===         # 含新 §12d

$ cd frontend && npm run build
✓ Compiled successfully
✓ Generating static pages (22/22)
├ ○ /public-extracts   160 B   87.2 kB    # 静态预渲染, 无 params.* 分支
build-rc=0

$ shasum -a 256 data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json \
    frontend/lib/public_extract_sz.json
937255a5… (双侧一致 — byte-verbatim 快照)
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/lib/public_extract_sz.json` | NEW（byte-verbatim 快照，71 行） | `data_contract_suite` |
| `frontend/app/public-extracts/page.tsx` | MODIFIED（+第三分节；NBS 双轨零改动） | 已入 manifest（SKIP） |
| `frontend/smoke-check.py` | MODIFIED（+§12d gate） | 已入 manifest（SKIP） |
| `tests/test_public_extract_frontend_fixture.py` | MODIFIED + 新增 3 case | 已入 manifest（SKIP） |
| `scripts/_knife59_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../371-stage0-cc-shenzhen-extract-frontend-section-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife59_manifest_bump.py`：NEW_ARTIFACTS +3（sz fixture + bump + receipt）→ **679 → 682**；`sum(role_count) == artifact_count == len(artifacts) == 682`。

## 红线自查

- ❌ 未覆盖 NBS 双轨（fixture 契约测试 + smoke §12d 交叉检查双重锁定：63 行 / `dea13b8a…` / `LIVE_CANDIDATE` / `0b85212f…` 全不变）
- ❌ 未谎称 live（DemoBadge + 免责声明均标 REGISTRY_SAMPLE / demo / SSL 暂缓 / 非 live O1；未做深圳 HTTPS 探测，per 370 §不做）
- ❌ 未 Gate/O1 PASS 宣言；未动 `00-CC-CURRENT.md` / `gate_thresholds.json`；未 --force；未索要 PAT
- ✅ 静态路由无 `params.*` 分支（纯 fixture 消费，build 确认 ○ Static）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 372）。
