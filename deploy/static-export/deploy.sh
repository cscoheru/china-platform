#!/usr/bin/env bash
# deploy.sh — knife 660 Track B 公网 redeploy (ops 在 newvps 上跑).
#
# Per 660 tasking §PART 2 + docs/53 §5 第 16 项 🔧 redeploy 命令链:
#   1. cd /opt/china-platform/frontend
#   2. git pull (同步架构师端 660 收口 commit)
#   3. npm ci
#   4. NEXT_PUBLIC_MART_DATA_PATH=./data/mart_province_gdp_2024.json npm run build
#      ⚠️ 关键改动 vs 老 446 命令链:不再传 NEXT_PUBLIC_USE_MOCK=true
#      ⚠️ 新增 NEXT_PUBLIC_MART_DATA_PATH 启用 Track B 静态导出
#   5. sudo systemctl restart china-platform-frontend
#
# SSH 易超时,长命令包 nohup (per docs/53 §5 第 16 项 🔧).
#
# Exit codes:
#   0  success — banner should turn green (LIVE MODE) at https://china.3strategy.cc/
#   1  precheck failed (re-run deploy/static-export/precheck.sh first)
#   2  git pull conflict
#   3  npm ci failed
#   4  npm run build failed
#   5  systemctl restart failed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TARGET="/opt/china-platform/frontend"
LOGFILE="/tmp/china-platform-deploy-$(date -u +%Y%m%dT%H%M%SZ).log"

cd "$TARGET"

echo "=== knife 660 Track B deploy starting at $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "REPO_DIR=$REPO_DIR"
echo "TARGET=$TARGET"
echo "LOGFILE=$LOGFILE"

# 1. precheck (run inline, fail fast)
echo "--- precheck ---"
if ! bash "$REPO_DIR/deploy/static-export/precheck.sh" 2>&1 | tee -a "$LOGFILE"; then
  echo "FATAL: precheck failed. Resolve [FAIL] lines first."
  exit 1
fi

# 2. git pull
echo "--- git pull ---"
git fetch origin 2>&1 | tee -a "$LOGFILE"
if ! git pull --ff-only 2>&1 | tee -a "$LOGFILE"; then
  echo "FATAL: git pull --ff-only failed. Resolve conflicts manually."
  exit 2
fi

# 3. npm ci
echo "--- npm ci ---"
if ! npm ci 2>&1 | tee -a "$LOGFILE"; then
  echo "FATAL: npm ci failed."
  exit 3
fi

# 4.1. Verify mart JSON exists and is current
echo "--- verify mart JSON ---"
MART_JSON="$TARGET/data/mart_province_gdp_2024.json"
if [ ! -f "$MART_JSON" ]; then
  echo "FATAL: $MART_JSON missing. Generate locally with:"
  echo "  python3 $REPO_DIR/deploy/static-export/export-mart-data.py --strict --out $MART_JSON"
  exit 4
fi
TOTAL=$(python3 -c "import json; print(json.load(open('$MART_JSON'))['total_count'])" 2>/dev/null || echo "?")
REAL=$(python3 -c "import json; print(json.load(open('$MART_JSON'))['real_count'])" 2>/dev/null || echo "?")
MISSING=$(python3 -c "import json; print(json.load(open('$MART_JSON'))['missing_count'])" 2>/dev/null || echo "?")
echo "  mart JSON: total=$TOTAL real=$REAL missing=$MISSING"
if [ "$TOTAL" != "31" ] || [ "$REAL" != "28" ] || [ "$MISSING" != "3" ]; then
  echo "WARN: mart JSON row counts unexpected; build may not have 28+3."
fi

# 4.2. Track B build: env=unset MOCK + set MART_DATA_PATH
echo "--- npm run build (Track B 静态导出) ---"
unset NEXT_PUBLIC_USE_MOCK
unset NEXT_PUBLIC_MART_FIXTURE
export NEXT_PUBLIC_MART_DATA_PATH="./data/mart_province_gdp_2024.json"
echo "  NEXT_PUBLIC_USE_MOCK=${NEXT_PUBLIC_USE_MOCK:-(unset)}"
echo "  NEXT_PUBLIC_MART_DATA_PATH=$NEXT_PUBLIC_MART_DATA_PATH"
if ! npm run build 2>&1 | tee -a "$LOGFILE"; then
  echo "FATAL: npm run build failed."
  exit 4
fi

# 5. restart systemd
echo "--- systemctl restart china-platform-frontend ---"
if ! sudo systemctl restart china-platform-frontend 2>&1 | tee -a "$LOGFILE"; then
  echo "FATAL: systemctl restart failed."
  exit 5
fi
sleep 3
sudo systemctl status china-platform-frontend --no-pager 2>&1 | tee -a "$LOGFILE" || true

# 6. localhost sanity check
echo "--- localhost:3000 sanity check ---"
curl -sS -o /tmp/deploy-home.html -w "  HTTP %{http_code} · %{size_download}B · %{time_total}s\n" \
  http://127.0.0.1:3000/ 2>&1 | tee -a "$LOGFILE"

# 7. summary
echo
echo "=== deploy summary ==="
echo "Log: $LOGFILE"
echo "Next: notify CC 端 (架构师) to run public curl verification matrix A-G+H/I/J:"
echo "  https://china.3strategy.cc/ should now show:"
echo "    - 顶部 banner: ✅ LIVE MODE — 28 省 2024 真实数据 + lineage 可溯"
echo "    - 省 GDP 表: 31 行 (28 真实 + 3 缺失)"
echo "    - 3 缺失省: 数据暂缺（公报源缺文）badge"
echo "    - JIANGSU-GDP-INDICATOR-UUID-MOCK 不再出现"
exit 0
