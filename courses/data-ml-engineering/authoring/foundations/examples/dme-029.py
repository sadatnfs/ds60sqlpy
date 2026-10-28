"""Query-shape and replica-intersection models, not a Cassandra server or client."""

from collections import Counter
from itertools import combinations


def fixture():
    return [("busy", day, event, 1) for day in (1, 2, 3) for event in range(4)] + [
        ("small", 1, 0, 2),
        ("small", 2, 0, 3),
    ]


def latest(versions):
    present = [version for version in versions if version is not None]
    if not present:
        return None
    timestamp = max(version[0] for version in present)
    candidates = {version for version in present if version[0] == timestamp}
    if len(candidates) != 1:
        raise ValueError("This teaching model rejects ambiguous equal-clock writes")
    return candidates.pop()


def example_one():
    rows = fixture()
    unbounded = Counter(tenant for tenant, _, _, _ in rows)
    bucketed = Counter((tenant, day) for tenant, day, _, _ in rows)
    query = [row for row in rows if row[0] == "busy" and row[1] == 2]
    assert unbounded["busy"] == 12 and max(bucketed.values()) == 4
    assert sum(row[3] for row in query) == 4
    tenant_partitions = sorted(key for key in bucketed if key[0] == "busy")
    assert len(tenant_partitions) == 3
    return {
        "tenant_only_largest_partition_rows": 12,
        "tenant_day_largest_rows": 4,
        "one_day_result": query,
        "all_days_query_partition_fanout": len(tenant_partitions),
        "scope": "query-model arithmetic; no CQL or replica network executed",
    }


def example_two():
    live = (1, "live", 2)
    deleted = (2, "deleted", None)
    replicas = [deleted, deleted, live]
    one_replica = [latest([replicas[index]])[1] for index in range(3)]
    quorum_reads = [
        latest([replicas[index] for index in pair])[1] for pair in combinations(range(3), 2)
    ]
    assert one_replica == ["deleted", "deleted", "live"] and quorum_reads == ["deleted"] * 3
    premature_purge = [None, None, live]
    resurrected = latest(premature_purge)
    assert resurrected == live
    return {
        "read_one_outcomes": one_replica,
        "read_two_outcomes": quorum_reads,
        "intersection_inequality": "2 + 2 > 3",
        "after_unsafe_tombstone_purge": list(resurrected),
        "assumptions": (
            "same replica set, completed writes, comparable clocks; not a proof of linearizability"
        ),
    }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("Partition design follows the required query:", first)
    print("Replica intersection and deletion retention:", second)
    counts = Counter((tenant, day) for tenant, day, _, _ in fixture())
    publish_table(
        ["tenant", "day", "rows"],
        [[tenant, day, count] for (tenant, day), count in sorted(counts.items())],
        description=(
            "Synthetic query-shape model: each busy tenant-day has four rows; "
            "no Cassandra server was run."
        ),
    )
    publish_report(
        second,
        description=(
            "Explicit three-replica model assumptions and deletion outcomes, "
            "not cluster qualification."
        ),
    )


if __name__ == "__main__":
    main()
