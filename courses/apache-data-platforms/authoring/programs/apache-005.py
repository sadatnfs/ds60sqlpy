import hashlib
from collections import Counter, defaultdict


def bucket(key, partitions=4):
    encoded = str(key).encode("utf-8")
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big") % partitions


balanced = [(f"customer-{i}", i % 7) for i in range(200)]
hot = [("hot", 1)] * 180 + [(f"other-{i}", 1) for i in range(20)]
for name, records in [("balanced", balanced), ("hot", hot)]:
    partitions = defaultdict(list)
    for key, value in records:
        partitions[bucket(key)].append((key, value))
    counts = Counter({p: len(rows) for p, rows in partitions.items()})
    assert sum(counts.values()) == len(records)
    assert sum(v for rows in partitions.values() for _, v in rows) == sum(v for _, v in records)
    if name == "hot":
        assert max(counts.values()) >= 180
    print(name, sorted(counts.items()))
assert [bucket(k) for k, _ in balanced] == [bucket(k) for k, _ in balanced]
partials = defaultdict(int)
for index, (key, value) in enumerate(hot):
    salt = index % 4 if key == "hot" else 0
    partials[(key, salt)] += value
merged = defaultdict(int)
for (key, _), value in partials.items():
    merged[key] += value
assert merged["hot"] == 180 and sum(merged.values()) == 200
print("Salted partials for hot key:", [partials[("hot", s)] for s in range(4)])
