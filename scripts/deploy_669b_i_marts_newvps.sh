#!/usr/bin/env bash
# knife batch8-deploy step 1b — apply 18 in-place UPSERT/INSERT-ONLY mart scripts to newvps postgres
# Order: dongguan → batch2-8 → 669j-1-6 (DONGGUAN seeds 10-indicator dimension; 669j anchor query patched to use any 2024 city)
set -euo pipefail

API="china-platform-api"
CONTAINER_SCRIPTS_DIR="/app/scripts"
CONTAINER_CACHE_DIR="/tmp/669b_i_cache"

echo "=== Step 0: Copy cache files from host → container ==="
for f in dalian dongguan qingdao suzhou wuxi xiamen; do
  if [ -f "/tmp/669b_i_cache/seed_${f}_full.csv" ]; then
    docker cp "/tmp/669b_i_cache/seed_${f}_full.csv" "$API:$CONTAINER_CACHE_DIR/seed_${f}_full.csv"
    echo "  ✓ /tmp/669b_i_cache/seed_${f}_full.csv"
  fi
done
for b in batch2 batch3 batch4 batch5 batch6 batch7 batch8; do
  docker exec "$API" mkdir -p "$CONTAINER_CACHE_DIR/tag/$b"
  if [ -f "/tmp/669b_i_cache/tag/$b/eid_map_$b.json" ]; then
    docker cp "/tmp/669b_i_cache/tag/$b/eid_map_$b.json" \
      "$API:$CONTAINER_CACHE_DIR/tag/$b/eid_map_$b.json"
    echo "  ✓ /tmp/669b_i_cache/tag/$b/eid_map_$b.json"
  fi
done
docker exec "$API" mkdir -p /app/source_registry
for b in 2 3 4 5 6 7 8; do
  f="source_registry/seed_hongheiku_city_timeseries_669b_i_batch${b}.csv"
  if [ -f "$f" ]; then
    docker cp "$f" "$API:/app/source_registry/seed_hongheiku_city_timeseries_669b_i_batch${b}.csv"
    echo "  ✓ /app/source_registry/seed_hongheiku_city_timeseries_669b_i_batch${b}.csv"
  fi
done

echo ""
echo "=== Step 1: Apply scripts (dongguan first → batch2-8 → 669j-1-6) ==="
SCRIPTS=(
  apply_mart_city_669b_i_dongguan.py
  apply_mart_city_669b_i_dalian.py
  apply_mart_city_669b_i_qingdao.py
  apply_mart_city_669b_i_wuxi.py
  apply_mart_city_669b_i_suzhou.py
  apply_mart_city_669b_i_xiamen.py
  apply_mart_city_669b_i_batch2.py
  apply_mart_city_669b_i_batch3.py
  apply_mart_city_669b_i_batch4.py
  apply_mart_city_669b_i_batch5.py
  apply_mart_city_669b_i_batch6.py
  apply_mart_city_669b_i_batch7.py
  apply_mart_city_669b_i_batch8.py
  apply_mart_city_669j_1.py
  apply_mart_city_669j_2.py
  apply_mart_city_669j_3.py
  apply_mart_city_669j_4.py
  apply_mart_city_669j_5.py
  apply_mart_city_669j_6.py
)

OK=0; FAIL=0
for s in "${SCRIPTS[@]}"; do
  echo ""
  echo "=== $s ==="
  docker cp "scripts/$s" "$API:$CONTAINER_SCRIPTS_DIR/$s"
  docker exec -u root "$API" sed -i 's/DB_HOST = "127.0.0.1"/DB_HOST = "china-platform-pg"/' "$CONTAINER_SCRIPTS_DIR/$s"
  docker exec -u root "$API" sed -i 's/DB_PORT = 55440/DB_PORT = 5432/' "$CONTAINER_SCRIPTS_DIR/$s"
  docker exec -u root "$API" sed -i 's|/Users/kjonekong/projects/china platform/source_registry/|/app/source_registry/|g' "$CONTAINER_SCRIPTS_DIR/$s"
  # Patch 669j-* anchor query: replace DONGGUAN-specific with any-2024-city
  if [[ "$s" == apply_mart_city_669j_* ]]; then
    docker exec -u root "$API" sed -i \
      "s|WHERE city_code = 'GUANGDONG_DONGGUAN' AND year = 2024|WHERE year = 2024 AND value IS NOT NULL AND indicator_label IS NOT NULL|" \
      "$CONTAINER_SCRIPTS_DIR/$s"
  fi
  if docker exec "$API" python3 "$CONTAINER_SCRIPTS_DIR/$s" 2>&1 | tail -10; then
    OK=$((OK+1))
  else
    FAIL=$((FAIL+1))
    echo "  ✗ $s FAILED"
  fi
done

echo ""
echo "============================================="
echo "Total: $((OK+FAIL)) scripts — OK=$OK FAIL=$FAIL"
