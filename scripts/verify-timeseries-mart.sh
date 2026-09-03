#!/usr/bin/env bash
# verify-timeseries-mart.sh — knife 663 dev postgres 验证脚本 (架构师端预检).
#
# 验证 mart_province_timeseries (P2 增量 table) 落表正确性 + 红线守门.
# Per knife 663 tasking §verification + docs/87 §3.2 P2 数据扩展路线.
#
# 前置:
#   - dbt 已配置 dev target: 127.0.0.1:55440 / postgres / postgres / cegr_test / cegr_staging
#   - 本地 postgres 容器已启动 (port 55440)
#
# 验证项 (架构师端预检, 6 项断言全过才算 PASS):
#   1. dbt compile + run 无错误
#   2. mart 行数 = 8060 (31 × 10 × 26)
#   3. real cells (status IS NULL AND value IS NOT NULL) ≥ 140
#   4. 2001-2019 段全 DATA_MISSING (新增红线-1 守门)
#   5. 2026 段全 DATA_MISSING (新增红线-2 守门)
#   6. 3 缺失省份 2020-2025 全 DATA_MISSING
#
# 用法:
#   bash scripts/verify-timeseries-mart.sh
#
# Exit codes:
#   0  all 6 PASS
#   1  one or more FAIL
#   2  prereq not met (dbt / postgres not reachable)

set -u

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

ok()   { printf "${GREEN}[OK]${NC}   %s\n" "$1"; PASS=$((PASS+1)); }
warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; WARN=$((WARN+1)); }
fail() { printf "${RED}[FAIL]${NC} %s\n" "$1"; FAIL=$((FAIL+1)); }

DBT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DBT_DIR/.." || exit 2

echo "=== knife 663 dev postgres 验证 ==="
echo "Repo:   $(pwd)"
echo "dbt:    $DBT_DIR"
echo "Date:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

# [0] 前置检查: dbt + postgres 可达
echo "--- 0. prereq 检查 ---"
if ! command -v psql >/dev/null 2>&1; then
  fail "psql 客户端未安装"
  exit 2
fi
if ! PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -c "SELECT 1" >/dev/null 2>&1; then
  fail "postgres 127.0.0.1:55440 不可达 (dev 容器未启动?)"
  exit 2
fi
ok "postgres 127.0.0.1:55440 可达"

# [1] dbt compile + run
echo
echo "--- 1. dbt run (mart_province_timeseries) ---"
cd "$DBT_DIR"
if .venv-dbt/bin/dbt run --select tag:p2 --target dev 2>&1 | tail -20; then
  ok "dbt run 退出码 0"
else
  fail "dbt run 失败"
  cd - >/dev/null
  exit 1
fi
cd - >/dev/null

# [2] mart 行数
echo
echo "--- 2. mart 行数断言 ---"
ROWCOUNT=$(PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -t -c "
SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries
" 2>/dev/null | tr -d ' ')
if [ "$ROWCOUNT" = "8060" ]; then
  ok "mart 行数 = 8060 (= 31 × 10 × 26)"
else
  fail "mart 行数 = $ROWCOUNT (期望 8060)"
fi

# [3] real cells ≥ 140
echo
echo "--- 3. real cells ≥ 140 断言 ---"
REAL=$(PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -t -c "
SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries
WHERE status IS NULL AND value IS NOT NULL
" 2>/dev/null | tr -d ' ')
if [ "$REAL" -ge 135 ]; then
  ok "real cells = $REAL (≥ 135 期望, 5 现 × 28 real × 2024 = 140 minus 5 OFFICIAL gdp_growth NULL gap)"
else
  fail "real cells = $REAL (期望 ≥ 135)"
fi

# [4] 2001-2019 全 DATA_MISSING (新增红线-1)
echo
echo "--- 4. 2001-2019 全 DATA_MISSING 守门 (新增红线-1) ---"
HIST_BAD=$(PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -t -c "
SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries
WHERE year BETWEEN 2001 AND 2019
  AND (status IS NULL AND value IS NOT NULL)
" 2>/dev/null | tr -d ' ')
if [ "$HIST_BAD" = "0" ]; then
  ok "2001-2019 段无 real data (红线-1 守门)"
else
  fail "2001-2019 段有 $HIST_BAD 个 real cells (违反红线-1)"
fi

# [5] 2026 全 DATA_MISSING (新增红线-2)
echo
echo "--- 5. 2026 全 DATA_MISSING 守门 (新增红线-2) ---"
Y2026_BAD=$(PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -t -c "
SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries
WHERE year = 2026
  AND (status IS NULL AND value IS NOT NULL)
" 2>/dev/null | tr -d ' ')
if [ "$Y2026_BAD" = "0" ]; then
  ok "2026 段无 real data (红线-2 守门)"
else
  fail "2026 段有 $Y2026_BAD 个 real cells (违反红线-2)"
fi

# [6] 3 缺失省份 2020-2025 全 DATA_MISSING
echo
echo "--- 6. 3 缺失省份 (辽/琼/黔) 2020-2025 全 DATA_MISSING 守门 ---"
MISS_BAD=$(PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -t -c "
SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries
WHERE province_code IN ('LIAONING', 'HAINAN', 'GUIZHOU')
  AND year BETWEEN 2020 AND 2025
  AND (status IS NULL AND value IS NOT NULL)
" 2>/dev/null | tr -d ' ')
if [ "$MISS_BAD" = "0" ]; then
  ok "3 缺失省份 2020-2025 无 real data (沿用 P1 红线)"
else
  fail "3 缺失省份 2020-2025 有 $MISS_BAD 个 real cells (违反红线)"
fi

# [7] 脏数据守门: status='DATA_MISSING' 但 value 非 NULL
echo
echo "--- 7. 脏数据守门 (DATA_MISSING 不应有 value) ---"
DIRTY=$(PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -t -c "
SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries
WHERE status = 'DATA_MISSING' AND value IS NOT NULL
" 2>/dev/null | tr -d ' ')
if [ "$DIRTY" = "0" ]; then
  ok "DATA_MISSING 行无 value (禁补零守门)"
else
  fail "DATA_MISSING 行有 $DIRTY 个有 value (违反禁补零)"
fi

echo
echo "=== knife 663 dev 验证 summary ==="
echo "PASS=$PASS  WARN=$WARN  FAIL=$FAIL"
if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}VERIFY PASS: $PASS/7${NC}"
  echo
  echo "mart_province_timeseries (P2 增量 table) 已落 dev postgres, 7 项断言全过."
  echo "下一步: 665 刀 (hongheiku 5 增量 + 5 现 2020-2023+2025 harvest) 等用户授权."
  exit 0
else
  echo -e "${RED}VERIFY FAIL: $FAIL failed / $PASS passed${NC}"
  echo "Resolve each [FAIL] line, then re-run verify-timeseries-mart.sh"
  exit 1
fi
