"""Real local artifact lineage with explicit recipe and content identities."""

import csv
import hashlib
import json
import tempfile
from graphlib import TopologicalSorter
from pathlib import Path

GRAPH = {
    "raw": set(),
    "calendar": set(),
    "clean": {"raw"},
    "totals": {"clean"},
    "report": {"totals"},
    "calendar_report": {"calendar"},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")), "utf-8")


def build(root):
    (root / "raw.csv").write_text("id,route,packages\nA,north,2\nB,north,3\nC,south,1\n")
    (root / "calendar.txt").write_text("2024-01-01\n")
    paths = {"raw": root / "raw.csv", "calendar": root / "calendar.txt"}
    recipes = {
        "clean": {"kind": "typed-csv"},
        "totals": {"kind": "group-sum", "key": "route", "value": "packages"},
        "report": {"kind": "total"},
        "calendar_report": {"kind": "line-count"},
    }
    ledger = {}
    for node in TopologicalSorter(GRAPH).static_order():
        if node not in paths:
            recipe_path = root / (node + ".recipe.json")
            save(recipe_path, recipes[node])
            recipe = json.loads(recipe_path.read_text())
            if recipe["kind"] == "typed-csv":
                with paths["raw"].open(newline="") as handle:
                    value = [
                        {**row, "packages": int(row["packages"])} for row in csv.DictReader(handle)
                    ]
            elif recipe["kind"] == "group-sum":
                value = {}
                for row in json.loads(paths["clean"].read_text()):
                    key = row[recipe["key"]]
                    value[key] = value.get(key, 0) + row[recipe["value"]]
            elif recipe["kind"] == "total":
                value = {"packages": sum(json.loads(paths["totals"].read_text()).values())}
            else:
                value = {"days": len(paths["calendar"].read_text().splitlines())}
            paths[node] = root / (node + ".json")
            save(paths[node], value)
        ledger[node] = {
            "file": paths[node].name,
            "sha256": sha(paths[node]),
            "parents": {parent: ledger[parent]["sha256"] for parent in sorted(GRAPH[node])},
        }
        if node in recipes:
            ledger[node]["recipe"] = {
                "file": node + ".recipe.json",
                "sha256": sha(root / (node + ".recipe.json")),
                "implementation_sha256": sha(Path(__file__)),
            }
    save(root / "lineage.json", ledger)
    return ledger


def invalidated(root, ledger):
    direct = set()
    affected = set()
    for node in TopologicalSorter(GRAPH).static_order():
        item = ledger[node]
        if sha(root / item["file"]) != item["sha256"]:
            direct.add(node)
        if "recipe" in item and sha(root / item["recipe"]["file"]) != item["recipe"]["sha256"]:
            direct.add(node)
        if "recipe" in item and item["recipe"]["implementation_sha256"] != sha(Path(__file__)):
            direct.add(node)
        if any(item["parents"].get(parent) != ledger[parent]["sha256"] for parent in GRAPH[node]):
            direct.add(node)
        if node in direct or GRAPH[node] & affected:
            affected.add(node)
    return {
        "direct": sorted(direct),
        "affected": sorted(affected),
        "unaffected": sorted(set(GRAPH) - affected),
    }


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        ledger = build(root)
        assert invalidated(root, ledger)["affected"] == []
        assert json.loads((root / "report.json").read_text()) == {"packages": 6}
        (root / "raw.csv").write_text("id,route,packages\nA,north,4\nB,north,3\nC,south,1\n")
        result = invalidated(root, ledger)
        assert result == {
            "direct": ["raw"],
            "affected": ["clean", "raw", "report", "totals"],
            "unaffected": ["calendar", "calendar_report"],
        }
        return {
            "changed_input_invalidation": result,
            "stored_report_is_now_stale": 6,
            "expected_rebuild_total": 8,
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        ledger = build(root)
        save(root / "totals.recipe.json", {"kind": "group-sum", "key": "id", "value": "packages"})
        result = invalidated(root, ledger)
        assert result["direct"] == ["totals"] and result["affected"] == ["report", "totals"]
        assert "clean" in result["unaffected"]
        return {
            "changed_recipe_invalidation": result,
            "earliest_rebuild_node": "totals",
            "hashes_establish_consistency_not_authorization": True,
        }


def main():
    print("Trace a changed source through actual artifacts:", example_one())
    print("A recipe change has a different impact boundary:", example_two())


if __name__ == "__main__":
    main()
