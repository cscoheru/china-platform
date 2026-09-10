// copy-mart-to-public.js — Knife H prebuild/predev 脚本.
//
// 用途: 把 frontend/data/mart_province_timeseries.json (server-side fs read
//   build-time) 复制到 frontend/public/data/mart_province_timeseries.json
//   (client-side fetch from /data/mart_province_timeseries.json).
//
// 触发: 在 frontend/package.json scripts.predev + scripts.prebuild 调用.
//   - predev: `npm run dev` 前执行, dev server 从 public/ serve
//   - prebuild: `npm run build` 前执行, build 把 public/ 复制到 .next/static
//
// 行为:
//   1. 校验源文件存在, 不存在就 throw (fail fast).
//   2. mkdir -p public/data/ (Node fs.mkdirSync recursive).
//   3. fs.copyFileSync 复制.
//   4. console.log 报告 size + path.
//
// 设计意图: 单源 (frontend/data/) 真实数据, public/data/ 是 build artifact.
//   - 源文件更新后, 下次 dev/build 自动重导.
//   - public/data/ 也入 git (便于 verify-live 抓 SSR HTML 后还能 GET client fetch).

const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "data", "mart_province_timeseries.json");
const DST = path.join(ROOT, "public", "data", "mart_province_timeseries.json");

function fail(msg) {
  console.error(`[copy-mart-to-public] FAIL: ${msg}`);
  process.exit(1);
}

if (!fs.existsSync(SRC)) {
  fail(`source not found: ${SRC}. Run dbt export-mart-data.py first.`);
}

fs.mkdirSync(path.dirname(DST), { recursive: true });

try {
  fs.copyFileSync(SRC, DST);
} catch (err) {
  fail(`copyFileSync failed: ${err instanceof Error ? err.message : String(err)}`);
}

const srcSize = fs.statSync(SRC).size;
const dstSize = fs.statSync(DST).size;

if (srcSize !== dstSize) {
  fail(`size mismatch: src=${srcSize} dst=${dstSize}`);
}

console.log(
  `[copy-mart-to-public] OK: ${srcSize} bytes copied to public/data/mart_province_timeseries.json`
);