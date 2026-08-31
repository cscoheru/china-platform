"""Knife 15 (backfill receipt 236 + UI shell + receipt 239) — bump manifest 553 → 556."""
import json
import hashlib
import pathlib

paths = [
    ('reviews/stage0-gate0-rework-2026-08-23/236-stage0-cc-s28-seven-dim-planning-receipt-20260826.md', 'documentation'),
    ('frontend/lib/types_seven_dim.ts', 'spike_helper'),
    ('frontend/lib/mock_seven_dim.ts', 'spike_helper'),
    ('frontend/app/components/SevenDimGrid.tsx', 'spike_helper'),
    ('frontend/app/seven-dim/page.tsx', 'spike_helper'),
]

new_entries = []
for rel, role in paths:
    p = pathlib.Path(rel)
    size = p.stat().st_size
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    new_entries.append({
        'path': rel, 'size_bytes': size, 'sha256': sha, 'role': role
    })
    print(f"{sha[:12]} {size:>6} {role:25} {rel}")

with open('evidence_pack/manifest.json') as f:
    m = json.load(f)

for entry in new_entries:
    m['artifacts'].append(entry)
m['artifact_count'] = len(m['artifacts'])

assert len(m['artifacts']) == m['artifact_count']
role_count = {}
for a in m['artifacts']:
    role_count[a['role']] = role_count.get(a['role'], 0) + 1
assert sum(role_count.values()) == m['artifact_count']

print(f"\nartifact_count: {m['artifact_count']}")
print(f"documentation: {role_count['documentation']}")
print(f"spike_helper: {role_count['spike_helper']}")
print(f"invariant: {len(m['artifacts'])} == {m['artifact_count']} == {sum(role_count.values())} ✓")

with open('evidence_pack/manifest.json', 'w') as f:
    json.dump(m, f, indent=2, ensure_ascii=False, sort_keys=False)
print("manifest written")