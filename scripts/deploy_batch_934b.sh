#!/usr/bin/env bash
# Knife 934b — deploy seeds + marts to newvps postgres
# ============================================================================
# Pipeline:
#   1. Generate deploy SQL (locally)             [Python: scripts/deploy_batch_934b.py]
#   2. Upload SQL + 5 CSV seeds to newvps        [scp]
#   3. docker cp CSVs into china-platform-pg     [/tmp/934b_seeds/]
#   4. Apply SQL via docker exec psql            [pipe via -i]
#   5. Verify mart row counts                    [psql -c]
#
# Standalone run:  bash scripts/deploy_batch_934b.sh
# Pre-flight check (no apply):  bash scripts/deploy_batch_934b.sh --check
set -euo pipefail

PROJECT_ROOT="/Users/kjonekong/projects/china platform"
NEWVPS_HOST="newvps"
PG_CONTAINER="china-platform-pg"
PG_USER="postgres"
PG_DB="cegr_test"
SQL_LOCAL="/tmp/934b/deploy_batch_934b.sql"
SQL_REMOTE="/tmp/934b/deploy_batch_934b.sql"
SEED_DIR_LOCAL="$PROJECT_ROOT/dbt/seeds"
SEED_DIR_REMOTE="/tmp/934b_seeds"

CHECK_ONLY=0
if [ "${1:-}" = "--check" ]; then
  CHECK_ONLY=1
fi

echo "=== knife 934b deploy (newvps postgres) ==="
echo "  newvps host:  $NEWVPS_HOST"
echo "  pg container: $PG_CONTAINER"
echo "  pg db:        $PG_DB"
echo "  sql:          $SQL_LOCAL"
echo "  seed dir:     $SEED_DIR_LOCAL → container:$SEED_DIR_REMOTE"
echo

# ---- Step 1: Generate SQL ----
echo "[1/5] Generate deploy SQL locally"
python3 "$PROJECT_ROOT/scripts/deploy_batch_934b.py" > /dev/null
ls -la "$SQL_LOCAL"
echo

# ---- Step 2: Upload SQL + CSVs to newvps ----
echo "[2/5] Upload SQL + 5 seed CSVs to newvps"
ssh "$NEWVPS_HOST" "mkdir -p /tmp/934b"
scp "$SQL_LOCAL" "$NEWVPS_HOST:$SQL_REMOTE"
for year in 2021 2022 2023 2024 2025; do
  scp "$SEED_DIR_LOCAL/seed_hongheiku_timeseries_${year}.csv" "$NEWVPS_HOST:/tmp/seed_hongheiku_timeseries_${year}.csv"
done
ssh "$NEWVPS_HOST" "ls -la $SQL_REMOTE /tmp/seed_hongheiku_timeseries_*.csv"
echo

# ---- Step 3: docker cp CSVs into pg container ----
echo "[3/5] docker cp 5 CSVs into pg container at $SEED_DIR_REMOTE/"
ssh "$NEWVPS_HOST" "
  docker exec $PG_CONTAINER mkdir -p $SEED_DIR_REMOTE
  for year in 2021 2022 2023 2024 2025; do
    docker cp /tmp/seed_hongheiku_timeseries_\${year}.csv $PG_CONTAINER:$SEED_DIR_REMOTE/seed_hongheiku_timeseries_\${year}.csv
  done
  docker exec $PG_CONTAINER ls -la $SEED_DIR_REMOTE/
"
echo

if [ $CHECK_ONLY -eq 1 ]; then
  echo "[check mode] stopping before SQL apply"
  exit 0
fi

# ---- Step 4: Apply SQL via docker exec psql ----
echo "[4/5] Apply SQL via docker exec -i psql"
ssh "$NEWVPS_HOST" "docker exec -i $PG_CONTAINER psql -U $PG_USER -d $PG_DB -v ON_ERROR_STOP=1" < "$SQL_LOCAL" 2>&1 | tail -50
echo

# ---- Step 5: Verify mart row counts ----
echo "[5/5] Verify mart row counts on newvps"
ssh "$NEWVPS_HOST" "docker exec $PG_CONTAINER psql -U $PG_USER -d $PG_DB -c \"
SELECT 'mart_province_timeseries' AS mart,
       COUNT(*) AS total_rows,
       COUNT(*) FILTER (WHERE value IS NOT NULL) AS real_cells,
       COUNT(DISTINCT year) AS years,
       COUNT(DISTINCT province_code) AS provinces
  FROM cegr_mart.mart_province_timeseries
UNION ALL
SELECT 'mart_city_timeseries' AS mart,
       COUNT(*) AS total_rows,
       COUNT(*) FILTER (WHERE value IS NOT NULL) AS real_cells,
       COUNT(DISTINCT year) AS years,
       COUNT(DISTINCT city_code) AS provinces
  FROM cegr_mart.mart_city_timeseries
ORDER BY mart;
\""
echo
ssh "$NEWVPS_HOST" "docker exec $PG_CONTAINER psql -U $PG_USER -d $PG_DB -c \"
SELECT year, COUNT(*) FILTER (WHERE value IS NOT NULL) AS real
  FROM cegr_mart.mart_province_timeseries
 GROUP BY year ORDER BY year;
\""
echo

echo "=== knife 934b deploy: ALL DONE ==="
