#!/usr/bin/env bash
# Stage 1 / S1.11 — Great Expectations runner wrapper.
# Per docs/25 §8 + reviews/86 §NOW.
#
# Usage:
#   ./ge/scripts/ge_run.sh                     # all 5 suites (CI default)
#   ./ge/scripts/ge_run.sh --suite d4         # single suite (dev)
#   ./ge/scripts/ge_run.sh --docs             # build Data Docs HTML
#
# DSN chain (env var only):
#   CEGR_GE_DSN → CEGR_API_DSN → CEGR_DSN → DATABASE_URL → dev default

set -euo pipefail

# Resolve paths relative to repo root.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${GE_DIR}/.." && pwd)"

# Resolve Python venv (prefer /tmp/ge_venv per docs/25 §8.1).
if [ -x "/tmp/ge_venv/bin/python" ]; then
  PY="/tmp/ge_venv/bin/python"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "${VIRTUAL_ENV}/bin/python" ]; then
  PY="${VIRTUAL_ENV}/bin/python"
else
  PY="$(command -v python3)"
fi

# DSN chain.
DSN="${CEGR_GE_DSN:-${CEGR_API_DSN:-${CEGR_DSN:-${DATABASE_URL:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}}}}"
export CEGR_GE_DSN="${DSN}"

cd "${GE_DIR}"

case "${1:-check}" in
  --suite)
    SUITE="${2:?usage: ge_run.sh --suite <name>}"
    exec "${PY}" -m great_expectations checkpoint run dev_checkpoint \
      --name "${SUITE}"
    ;;
  --docs)
    exec "${PY}" -m great_expectations docs build
    ;;
  check|"")
    exec "${PY}" -m great_expectations checkpoint run ci_checkpoint
    ;;
  *)
    echo "usage: ge_run.sh [--suite <name>|--docs|check]" >&2
    exit 2
    ;;
esac
