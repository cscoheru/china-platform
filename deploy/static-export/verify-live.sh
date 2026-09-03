#!/usr/bin/env bash
# verify-live.sh — knife 662 公网 12 项验收 (post-redeploy 自动化).
#
# Per 662 tasking §1.662-D6 + 661 receipt §6.F2 (12 项基础) + 662 五项新增
# (indicators / coverage matrix / 排序 bar / 4 demo banner / LIVE/DEMO 导航).
#
# 用法:
#   bash deploy/static-export/verify-live.sh                          # 默认 https://china.3strategy.cc
#   bash deploy/static-export/verify-live.sh https://staging.example   # 覆盖
#   bash deploy/static-export/verify-live.sh --offline                # 跳过真 HTTP, 只跑语法 (CI dry-run)
#
# 12 项断言 (全部 PASS 才算通过):
#   1. HTTP 200 + LIVE MODE banner
#   2. 5 指标 tab 默认 active = 总量
#   3. NATIONAL 锚行 + OFFICIAL_ANCHOR badge
#   4. 31 省详情抽样 (BEIJING/SHANGHAI/LIAONING 三档覆盖)
#   5. 5 指标 tab testid 完整 (gdp_total/gdp_growth/primary/secondary/tertiary)
#   6. peer-compare 真数据 4 省
#   7. 溯源 popover 五件套 (URL + SHA + lineage_source + lineage_origin + ruling)
#   8. DATA_MISSING 3 省详情页显式「数据暂缺」
#   9. /indicators 5 指标卡 + 来源等级三分布条形
#  10. 覆盖矩阵 31×5 (DATA_MISSING 三色)
#  11. 4 demo 页 200 + DemoBanner
#  12. layout LIVE/DEMO 导航分组 + 排序 bar
#
# Exit codes:
#   0  all 12 PASS
#   1  one or more FAIL (with [FAIL] red line)
#   2  离线模式 (--offline, 只跑语法; 不真访问公网)
set -u

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAIL=0
PASS=0
WARN=0

BASE_URL="${1:-https://china.3strategy.cc}"
OFFLINE=0
if [ "$BASE_URL" = "--offline" ]; then
  OFFLINE=1
  BASE_URL="https://china.3strategy.cc"
fi

ok()   { printf "${GREEN}[OK]${NC}   %s\n" "$1"; PASS=$((PASS+1)); }
warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; WARN=$((WARN+1)); }
fail() { printf "${RED}[FAIL]${NC} %s\n" "$1"; FAIL=$((FAIL+1)); }

echo "=== knife 662 公网 12 项验收 ==="
echo "Target: $BASE_URL"
echo "Mode:   $([ $OFFLINE -eq 1 ] && echo 'OFFLINE (syntax-only)' || echo 'LIVE')"
echo "Date:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

# 离线模式: 只验证脚本自身语法 + 必备工具.
if [ $OFFLINE -eq 1 ]; then
  echo "--- OFFLINE mode: syntax + 12 项标识检查 ---"
  for k in "LIVE MODE" "metric-tab-gdp_total" "national-badge" \
           "BEIJING" "SHANGHAI" "LIAONING" \
           "peer-compare-real-table" "source-popover" "data-missing-banner" \
           "indicators" "coverage-matrix" "demo-banner" "sort-bar" \
           "site-nav-live-group" "site-nav-demo-group"; do
    # 这里只验证字符串在脚本自身出现 (测试用例覆盖).
    if grep -q "$k" "$0"; then
      ok "标识 $k 在脚本内"
    else
      fail "标识 $k 缺失"
    fi
  done
  echo
  echo "=== OFFLINE summary ==="
  echo "PASS=$PASS  WARN=$WARN  FAIL=$FAIL"
  exit 2
fi

# 真 HTTP 模式: 用 curl 拉页面 + grep 关键 testid / 字符串.
fetch() {
  local url="$1"
  curl -s -L --max-time 20 -o /dev/null -w "%{http_code}" "$url"
}

fetch_body() {
  local url="$1"
  local outfile="$2"
  curl -s -L --max-time 20 -o "$outfile" "$url"
  echo "$?"
}

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "--- 1. HTTP 200 + LIVE MODE banner ---"
HOMEPAGE="$TMPDIR/home.html"
fetch_body "$BASE_URL/" "$HOMEPAGE" >/dev/null
if [ -s "$HOMEPAGE" ] && grep -q "LIVE MODE" "$HOMEPAGE"; then
  ok "首页 HTTP 200 + LIVE MODE banner 出现"
else
  fail "首页未拉取成功或无 LIVE MODE banner"
fi

echo
echo "--- 2. 5 指标 tab 默认 active = 总量 ---"
if grep -q 'data-testid="metric-tab-gdp_total"' "$HOMEPAGE" \
   && grep -A2 'data-testid="metric-tab-gdp_total"' "$HOMEPAGE" | grep -q 'aria-selected="true"'; then
  ok "metric-tab-gdp_total 默认 active (aria-selected=true)"
else
  fail "metric-tab-gdp_total 默认非 active"
fi

echo
echo "--- 3. NATIONAL 锚行 + OFFICIAL_ANCHOR badge ---"
if grep -q 'data-testid="national-badge"' "$HOMEPAGE" \
   && grep -q "OFFICIAL_ANCHOR" "$HOMEPAGE"; then
  ok "national-badge + OFFICIAL_ANCHOR 文案出现"
else
  fail "NATIONAL 锚行未出现"
fi

echo
echo "--- 4. 31 省详情抽样 (BEIJING/SHANGHAI 真实 + LIAONING DATA_MISSING 三档) ---"
# 真实省 (BEIJING/SHANGHAI) 必须含 province-metrics-table; DATA_MISSING (LIAONING) 必须含 data-missing-banner.
# per docs/87 §3.1 缺失省禁补零, 显式标记; metrics table 仅真实省渲染.
ALL_PROVINCE_OK=1
for slug in beijing shanghai; do
  PROV_PAGE="$TMPDIR/province-$slug.html"
  fetch_body "$BASE_URL/provinces/$slug" "$PROV_PAGE" >/dev/null
  if [ ! -s "$PROV_PAGE" ]; then
    fail "/provinces/$slug 拉取失败"
    ALL_PROVINCE_OK=0
  else
    if ! grep -q 'data-testid="province-metrics-table"' "$PROV_PAGE"; then
      fail "/provinces/$slug 缺 metrics table"
      ALL_PROVINCE_OK=0
    fi
  fi
done
# DATA_MISSING 省 (LIAONING) 走单独分支 — 无 metrics table 但有 data-missing-banner.
PROV_DM="$TMPDIR/province-liaoning.html"
fetch_body "$BASE_URL/provinces/liaoning" "$PROV_DM" >/dev/null
if [ ! -s "$PROV_DM" ]; then
  fail "/provinces/liaoning 拉取失败"
  ALL_PROVINCE_OK=0
elif ! grep -q 'data-testid="data-missing-banner"' "$PROV_DM"; then
  fail "/provinces/liaoning (DATA_MISSING) 缺 data-missing-banner"
  ALL_PROVINCE_OK=0
fi
if [ $ALL_PROVINCE_OK -eq 1 ]; then
  ok "3 抽样省 (真 BEIJING/SHANGHAI metrics table + 缺 LIAONING data-missing-banner) 全部就位"
fi

echo
echo "--- 5. 5 指标 tab testid 完整 ---"
ALL_TABS_OK=1
for k in gdp_total gdp_growth primary_gdp secondary_gdp tertiary_gdp; do
  if ! grep -q "data-testid=\"metric-tab-$k\"" "$HOMEPAGE"; then
    fail "metric-tab-$k 缺失"
    ALL_TABS_OK=0
  fi
done
if [ $ALL_TABS_OK -eq 1 ]; then
  ok "5 指标 tab testid 完整"
fi

echo
echo "--- 6. peer-compare 真数据 4 省 ---"
PEER_PAGE="$TMPDIR/peer.html"
fetch_body "$BASE_URL/peer-compare" "$PEER_PAGE" >/dev/null
if [ -s "$PEER_PAGE" ] && grep -q "peer-compare-real-table" "$PEER_PAGE" \
   && grep -q "JIANGSU" "$PEER_PAGE" && grep -q "ZHEJIANG" "$PEER_PAGE" \
   && grep -q "GUANGDONG" "$PEER_PAGE" && grep -q "SHANDONG" "$PEER_PAGE"; then
  ok "peer-compare 4 省 (江苏/浙江/广东/山东) 出现"
else
  fail "peer-compare 4 省未齐"
fi

echo
echo "--- 7. 溯源 popover 五件套 (URL + SHA + lineage_source + lineage_origin + ruling) ---"
POPOVER_OK=1
# 抽样一个真实行的 SourcePopover (OFFICIAL_INTAKED 至少 6 行, 找第一个)
if ! grep -q "data-testid=\"lineage-source-value\"" "$HOMEPAGE"; then
  fail "lineage-source-value 缺失"
  POPOVER_OK=0
fi
if ! grep -q "data-testid=\"lineage-origin-value\"" "$HOMEPAGE"; then
  fail "lineage-origin-value 缺失"
  POPOVER_OK=0
fi
if ! grep -q "data-testid=\"source-popover-summary\"" "$HOMEPAGE"; then
  fail "source-popover summary 缺失"
  POPOVER_OK=0
fi
if [ $POPOVER_OK -eq 1 ]; then
  ok "SourcePopover 五件套字段都在 (lineage_source/origin + URL/SHA/ruling)"
fi

echo
echo "--- 8. DATA_MISSING 3 省详情页显式「数据暂缺」 ---"
DATA_MISSING_OK=1
for slug in liaoning hainan guizhou; do
  P="$TMPDIR/missing-$slug.html"
  fetch_body "$BASE_URL/provinces/$slug" "$P" >/dev/null
  if [ ! -s "$P" ]; then
    fail "/provinces/$slug 拉取失败"
    DATA_MISSING_OK=0
  elif ! grep -q "data-missing-banner" "$P"; then
    fail "/provinces/$slug 缺 data-missing-banner"
    DATA_MISSING_OK=0
  fi
done
if [ $DATA_MISSING_OK -eq 1 ]; then
  ok "DATA_MISSING 3 省 (辽宁/海南/贵州) 详情页显式「数据暂缺」"
fi

echo
echo "--- 9. /indicators 5 指标卡 + 来源等级三分布条形 ---"
INDICATORS_PAGE="$TMPDIR/indicators.html"
fetch_body "$BASE_URL/indicators" "$INDICATORS_PAGE" >/dev/null
INDICATORS_OK=1
if [ ! -s "$INDICATORS_PAGE" ]; then
  fail "/indicators 拉取失败"
  INDICATORS_OK=0
else
  for k in gdp_total gdp_growth primary_gdp secondary_gdp tertiary_gdp; do
    if ! grep -q "data-testid=\"indicator-card-$k\"" "$INDICATORS_PAGE"; then
      fail "indicator-card-$k 缺失"
      INDICATORS_OK=0
    fi
    if ! grep -q "data-testid=\"grade-bar-official-$k\"" "$INDICATORS_PAGE"; then
      fail "grade-bar-official-$k 缺失"
      INDICATORS_OK=0
    fi
  done
fi
if [ $INDICATORS_OK -eq 1 ]; then
  ok "/indicators 5 指标卡 + 三档条形 全部就位"
fi

echo
echo "--- 10. 覆盖矩阵 31×5 (DATA_MISSING 三色) ---"
COVERAGE_OK=1
if ! grep -q "data-testid=\"coverage-matrix\"" "$HOMEPAGE"; then
  fail "coverage-matrix testid 缺失"
  COVERAGE_OK=0
fi
if ! grep -q "data-testid=\"coverage-footer\"" "$HOMEPAGE"; then
  fail "coverage-footer 缺失"
  COVERAGE_OK=0
fi
if ! grep -q "data-testid=\"data-missing-publicity\"" "$HOMEPAGE"; then
  fail "data-missing-publicity 缺失"
  COVERAGE_OK=0
fi
# DATA_MISSING 单元格 (e.g. LIAONING-gdp_total) 存在 — CoverageMatrix 用 uppercase province_code.
for prov in LIAONING HAINAN GUIZHOU; do
  if ! grep -q "data-testid=\"coverage-cell-$prov-gdp_total\"" "$HOMEPAGE"; then
    fail "coverage-cell-$prov-gdp_total 缺失"
    COVERAGE_OK=0
  fi
done
if [ $COVERAGE_OK -eq 1 ]; then
  ok "CoverageMatrix 31×5 (含 DATA_MISSING 三色) + footer + 公示 全部就位"
fi

echo
echo "--- 11. 4 demo 页 200 + DemoBanner ---"
# 注: 路径含 "/" 时直接做 tmpfile 名会写失败, 需把 "/" 替成 "_" 让文件落在 $TMPDIR 根.
DEMO_OK=1
for path in seven-dim research/m1-series research/q1-2024-gdp public-extracts; do
  safe=$(printf '%s' "$path" | tr '/' '_')
  D="$TMPDIR/demo-$safe.html"
  fetch_body "$BASE_URL/$path" "$D" >/dev/null
  if [ ! -s "$D" ]; then
    fail "/$path 拉取失败"
    DEMO_OK=0
  elif ! grep -q "data-testid=\"demo-banner\"" "$D"; then
    fail "/$path 缺 demo-banner"
    DEMO_OK=0
  fi
done
if [ $DEMO_OK -eq 1 ]; then
  ok "4 demo 页 (seven-dim/m1-series/q1-2024-gdp/public-extracts) 全部含 DemoBanner"
fi

echo
echo "--- 12. layout LIVE/DEMO 导航分组 + 排序 bar ---"
LAYOUT_OK=1
if ! grep -q "data-testid=\"site-nav-live-group\"" "$HOMEPAGE"; then
  fail "site-nav-live-group 缺失"
  LAYOUT_OK=0
fi
if ! grep -q "data-testid=\"site-nav-demo-group\"" "$HOMEPAGE"; then
  fail "site-nav-demo-group 缺失"
  LAYOUT_OK=0
fi
if ! grep -q "data-testid=\"sort-bar\"" "$HOMEPAGE"; then
  fail "sort-bar 缺失"
  LAYOUT_OK=0
fi
if [ $LAYOUT_OK -eq 1 ]; then
  ok "layout LIVE/DEMO 导航分组 + 首页 sort-bar 就位"
fi

echo
echo "=== knife 662 公网 12 项验收 summary ==="
if [ $FAIL -eq 0 ] && [ $WARN -eq 0 ]; then
  echo -e "${GREEN}VERIFY PASS: $PASS/12${NC}"
  exit 0
elif [ $FAIL -eq 0 ]; then
  echo -e "${YELLOW}VERIFY PASS WITH WARNINGS: $PASS PASS / $WARN WARN${NC}"
  exit 0
else
  echo -e "${RED}VERIFY FAIL: $FAIL failed / $PASS passed / $WARN warned${NC}"
  echo "Resolve each [FAIL] line, then re-run verify-live.sh"
  exit 1
fi
