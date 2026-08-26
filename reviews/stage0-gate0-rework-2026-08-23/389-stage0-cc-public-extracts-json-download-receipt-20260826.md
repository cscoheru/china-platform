# 389 — 四轨 JSON 静态下载 · CC 回执

- 编号：`389-stage0-cc-public-extracts-json-download-receipt-20260826`
- 任务书：`388-stage2-public-extracts-json-download-tasking-20260826`
- 作者：CC（heartbeat 84）
- cc_head：`<待回填>`
- 日期：2026-08-26

---

## §NOW 对照

| 388 §SCHEMA 裁定 | 交付 | 证据 |
|---|---|---|
| (1) 4 个 frontend fixture **字节一致**拷到 `frontend/public/public-extracts/`（`nbs.json` / `nbs-live-candidate.json` / `sz.json` / `hubei.json`） | ✅ `mkdir -p frontend/public/public-extracts` 后 `cp` 4 个 fixture；双侧 sha256 字节完全一致：`nbs.json` 7183B `e30ee811…` ↔ `public_extract_nbs.json`、`nbs-live-candidate.json` 13025B `9232efdb…` ↔ `public_extract_nbs_live_candidate.json`、`sz.json` 24021B `937255a5…` ↔ `public_extract_sz.json`、`hubei.json` 2907B `9056001c…` ↔ `public_extract_hubei.json`；smoke §12g 门 4 字节相等断言；pytest `test_public_json_byte_identical_to_fixture` 4 parametrized cases 字节相等 | 双侧 shasum + smoke + pytest |
| (2) 一览表或各分节加「下载 JSON」链（`/public-extracts/*.json`，`download` 属性可选） | ✅ overview 表增「下载 JSON」列（8 列：轨 / domain / category / 行数 / SHA 前 8 / demo\|candidate 标注 / 分节锚点 / 下载 JSON）；4 行每行 `<a href="/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.json" download="public-extracts-{...}.json">⬇ {name}.json</a>`；smoke §12g 门 9 针（列头 + 4 href + 4 download attr） | diff + 自检 |
| (3) ≥2 pytest（public 文件 sha/字节 == fixture）+ smoke 针 | ✅ 5 pytest case + smoke §12g 门（4 字节相等 + 5 页面针）：<br>• `test_public_json_byte_identical_to_fixture[nbs.json]` + `[nbs-live-candidate.json]` + `[sz.json]` + `[hubei.json]` — 4 parametrized 双侧字节完全相等 + 非空；<br>• `test_page_renders_download_json_column_and_links` — 「下载 JSON」列头 + 4 `href="/public-extracts/*.json"` + 4 `download="public-extracts-*.json"` attr；<br>• `frontend/smoke-check.py §12g` — 4 字节相等断言（4 fixture 字节一致 4 字节相等断言 + 「下载 JSON」列 + 4 download 链 + 4 download attr） | 自检 + pytest + smoke |
| (4) 回执 `389`（`-cc-` 名） | ✅ 本文件名 | — |

## 证据

```
$ for pair in nbs:nbs nbs_live_candidate:nbs-live-candidate sz:sz hubei:hubei; do …; done
MATCH nbs ↔ nbs (e30ee811daef5594…)
MATCH nbs_live_candidate ↔ nbs-live-candidate (9232efdbe1c3798a…)
MATCH sz ↔ sz (937255a5c82b41ec…)
MATCH hubei ↔ hubei (9056001c521c6318…)

$ python3 -m pytest tests/test_public_extract_frontend_fixture.py -q
24 passed in 0.77s                       # knife 63 后 19 → knife 65 +5 (4 parametrized + 1 column)

$ python3 -m pytest tests/test_public_extract_frontend_fixture.py \
                    tests/test_auto_ingest_public_source_s52.py -q
110 passed in 2.10s                      # 24 + 86 = 110 全绿

$ python3 frontend/smoke-check.py
✅ … §12g … public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.json 字节 == fixture (4 字节相等)
✅ public-extracts/page.tsx: 下载 JSON 列 + 4 download 链
=== … smoke: PASS ===

$ (cd frontend && npm run build 2>&1 | grep public-extracts)
├ ○ /public-extracts                     160 B          87.2 kB
                                           # static prerender (○) ✓
 ✓ Compiled successfully
 ✓ Generating static pages (22/22)

$ python3 scripts/_knife65_manifest_bump.py
ADD: frontend/public/public-extracts/nbs.json (…)
ADD: frontend/public/public-extracts/nbs-live-candidate.json (…)
ADD: frontend/public/public-extracts/sz.json (…)
ADD: frontend/public/public-extracts/hubei.json (…)
ADD: scripts/_knife65_manifest_bump.py (…)
ADD: reviews/.../389-…-receipt-20260826.md (…)
UPDATE artifact_count: 694 → 700
INVARIANT: sum(role_count)=700 == artifact_count=700 == len(artifacts)=700
```

## 交付清单

| 文件 | 变更 | role |
|---|---|---|
| `frontend/public/public-extracts/nbs.json` | NEW (字节一致拷自 `public_extract_nbs.json`) | `data_contract_suite` |
| `frontend/public/public-extracts/nbs-live-candidate.json` | NEW (字节一致拷自 `public_extract_nbs_live_candidate.json`) | `data_contract_suite` |
| `frontend/public/public-extracts/sz.json` | NEW (字节一致拷自 `public_extract_sz.json`) | `data_contract_suite` |
| `frontend/public/public-extracts/hubei.json` | NEW (字节一致拷自 `public_extract_hubei.json`) | `data_contract_suite` |
| `frontend/app/public-extracts/page.tsx` | MODIFIED（header 注释 + overview 表 + 「下载 JSON」列 + 4 download 链） | 已入 manifest（SKIP，SHA REFRESH 不增计数 per knife 44 先例） |
| `frontend/smoke-check.py` | MODIFIED（+ §12g 门，4 字节相等 + 9 页面针） | 已入 manifest（SKIP） |
| `tests/test_public_extract_frontend_fixture.py` | MODIFIED（+ 5 cases，4 parametrized byte-identical + 1 column） | 已入 manifest（SKIP） |
| `scripts/_knife65_manifest_bump.py` | NEW | `spike_helper` |
| `reviews/.../389-stage0-cc-public-extracts-json-download-receipt-20260826.md` | NEW（本文件） | `documentation` |

## Pack 不变量

`_knife65_manifest_bump.py`：NEW_ARTIFACTS +6（4 public 字节拷贝 + bump + receipt）→ **694 → 700**；`sum(role_count) == artifact_count == len(artifacts) == 700`（page.tsx / smoke-check.py / fixture test 皆 SHA REFRESH / 测 / 文案修订 不增计数；4 public 拷贝是 fixture 的字节一致镜像 = 数据合约交付物，按 knife 58/61 precedent 落 pack `data_contract_suite`）。

## 红线自查

- ❌ 未改写 fixture 内容（4 fixture 字节未动；4 public 拷贝与 lib fixture sha 完全一致，pytest 锁定）
- ❌ 未谎称下载 = O1（4 download 链在 demo/candidate 表内，overview 守门未动；下载 JSON 仅供浏览器下载样本数据，非 O1 收口数据）
- ❌ 未覆盖/删减既有四分节正文（仅在 overview 表增列，未动各 section 表格 / 表头 / 字段 / 脚注）
- ❌ 未跑任何 live 探测 / 未改 registry `enabled` 列 / 未动 `00-CC-CURRENT.md` / 未动 `gate_thresholds.json`
- ❌ 未 Gate/O1 PASS 宣告；未 --force；未索要 PAT
- ✅ public 与 lib fixture 字节一致（pytest 4 parametrized + smoke §12g 4 字节相等断言全部锁定）
- ✅ 回执文件名含 `-cc-`；receipt 位于 `reviews/stage0-gate0-rework-2026-08-23/`

## 下一步

`git push origin HEAD && git push github HEAD` → `./scripts/cc_gate_watch.sh --pull` → **84 POLL**（等 Cursor 审计 390）。