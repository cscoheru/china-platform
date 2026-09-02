#!/usr/bin/env bash
# precheck.sh — knife 660 Track B 公网 redeploy 前置环境探测 (ops 跑).
#
# Per 660 tasking §PART 2 + docs/53 §5 第 16 项 📍 运维登记:
#   newvps (207.57.134.99:16921 via ssh puer-hk host alias ONLY — never
#   aliyun -p 16921, that's mail.rana.asia) 上 ops 跑这个 precheck,
#   全部 PASS 才进 deploy.sh。任何 FAIL 必须先解决,否则 build 必败。
#
# Exit codes:
#   0  all checks PASS
#   1  one or more checks FAIL (退出前打印红色 [FAIL] 行)
set -u

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAIL=0
WARN=0

ok()   { printf "${GREEN}[OK]${NC}   %s\n" "$1"; }
warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; WARN=$((WARN+1)); }
fail() { printf "${RED}[FAIL]${NC} %s\n" "$1"; FAIL=$((FAIL+1)); }

echo "=== knife 660 Track B 公网 redeploy precheck ==="
echo "Host: $(hostname)"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

echo "--- 1. Node.js / npm ---"
if command -v node >/dev/null 2>&1; then
  NODE_VER=$(node -v | sed 's/^v//')
  NODE_MAJOR=$(echo "$NODE_VER" | cut -d. -f1)
  if [ "$NODE_MAJOR" -ge 18 ]; then
    ok "node $NODE_VER (>= 18 required)"
  else
    fail "node $NODE_VER (< 18; Next.js 14+ requires >= 18 LTS)"
  fi
else
  fail "node not found in PATH"
fi

if command -v npm >/dev/null 2>&1; then
  ok "npm $(npm -v)"
else
  fail "npm not found in PATH"
fi

echo
echo "--- 2. systemd + china-platform-frontend service ---"
if command -v systemctl >/dev/null 2>&1; then
  ok "systemctl available"
  if systemctl list-unit-files 2>/dev/null | grep -q "^china-platform-frontend.service"; then
    ok "china-platform-frontend.service is registered"
    STATE=$(systemctl is-active china-platform-frontend 2>/dev/null || echo "unknown")
    if [ "$STATE" = "active" ] || [ "$STATE" = "inactive" ] || [ "$STATE" = "failed" ]; then
      ok "current state: $STATE (will be restarted by deploy.sh)"
    else
      warn "unexpected state: $STATE"
    fi
  else
    fail "china-platform-frontend.service NOT registered; deploy.sh will not work. See docs/53 §5 第 16 项 📍"
  fi
else
  fail "systemctl not found"
fi

echo
echo "--- 3. nginx + china.3strategy.cc.conf ---"
if command -v nginx >/dev/null 2>&1; then
  ok "nginx $(nginx -v 2>&1 | awk -F/ '{print $2}')"
  if [ -f /etc/nginx/sites-enabled/china.3strategy.cc.conf ]; then
    ok "china.3strategy.cc.conf is enabled"
    if nginx -t 2>/dev/null | grep -q "syntax is ok"; then
      ok "nginx config syntax OK"
    else
      fail "nginx config has syntax error; run 'sudo nginx -t' for details"
    fi
  else
    fail "/etc/nginx/sites-enabled/china.3strategy.cc.conf missing; see docs/53 §5 第 16 项"
  fi
else
  fail "nginx not found"
fi

echo
echo "--- 4. /opt/china-platform/frontend writable ---"
TARGET="/opt/china-platform/frontend"
if [ -d "$TARGET" ]; then
  ok "$TARGET exists"
  if [ -w "$TARGET" ]; then
    ok "$TARGET writable"
  else
    fail "$TARGET not writable by $(whoami); need sudo or correct ownership"
  fi
else
  fail "$TARGET missing; expected per docs/53 §5 第 16 项"
fi

echo
echo "--- 5. .env / NEXT_PUBLIC_USE_MOCK leakage check ---"
ENV_FILES=$(find "$TARGET" -maxdepth 2 -name ".env*" -type f 2>/dev/null)
if [ -z "$ENV_FILES" ]; then
  ok "no .env* files (env should be set inline at build time)"
else
  warn ".env* files present: $ENV_FILES (verify NEXT_PUBLIC_USE_MOCK is NOT set to 'true')"
  for f in $ENV_FILES; do
    if grep -q "NEXT_PUBLIC_USE_MOCK=true" "$f" 2>/dev/null; then
      fail "$f contains NEXT_PUBLIC_USE_MOCK=true; deploy.sh will override but warn user"
    fi
  done
fi

echo
echo "=== precheck summary ==="
if [ "$FAIL" -eq 0 ] && [ "$WARN" -eq 0 ]; then
  echo -e "${GREEN}ALL PASS${NC} — proceed to deploy.sh"
  exit 0
elif [ "$FAIL" -eq 0 ]; then
  echo -e "${YELLOW}PASS WITH WARNINGS${NC} ($WARN warnings) — review before deploy.sh"
  exit 0
else
  echo -e "${RED}FAIL${NC} ($FAIL failures, $WARN warnings) — DO NOT proceed to deploy.sh"
  echo "Resolve each [FAIL] line, then re-run precheck.sh"
  exit 1
fi
