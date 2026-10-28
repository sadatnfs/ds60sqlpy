"""A bounded local DAG/checkpoint mechanism with actual owned files, not an Airflow service."""

import hashlib
import json
import tempfile
from graphlib import TopologicalSorter
from pathlib import Path

GRAPH = {"validate": set(), "aggregate": {"validate"}, "publish": {"aggregate"}}


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def save(path, value):
    pending = path.with_suffix(".pending")
    pending.write_text(json.dumps(value, sort_keys=True), "utf-8")
    pending.replace(path)


def run_pipeline(root, values, fail_after=None):
    if fail_after not in {None, "validate", "publication-write"}:
        raise ValueError("Unknown deliberate failure boundary")
    identity = digest(
        {
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            ("values"): values,
        }
    )
    path = root / "ledger.json"
    ledger = (
        json.loads(path.read_text("utf-8")) if path.exists() else {"schema_version": 1, "runs": {}}
    )
    if (
        not isinstance(ledger, dict)
        or type(ledger.get("schema_version")) is not int
        or ledger[("schema_version")] != 1
        or not isinstance(ledger.get("runs"), dict)
    ):
        raise ValueError("Unsupported checkpoint schema")
    state = ledger["runs"].setdefault(identity, {"steps": {}, "attempts": {}})
    publication = root / (identity + ".product.json")
    for step in TopologicalSorter(GRAPH).static_order():
        if step in state["steps"]:
            prior = state["steps"][step]
            if digest(prior["value"]) != prior["sha256"]:
                raise ValueError("Checkpoint content differs from its recorded identity")
            continue
        if not GRAPH[step] <= state["steps"].keys():
            raise ValueError("A prerequisite has no accepted checkpoint")
        state["attempts"][step] = state["attempts"].get(step, 0) + 1
        save(path, ledger)
        if step == "validate":
            if (
                not isinstance(values, list)
                or len(values) > 100
                or any(type(value) is not int or value < 1 for value in values)
            ):
                raise ValueError("Expected a bounded complete list of positive counts")
            result = list(values)
        elif step == "aggregate":
            result = {
                "rows": len(state["steps"]["validate"]["value"]),
                "packages": sum(state[("steps")][("validate")][("value")]),
            }
        else:
            result = {"run_identity": identity, **state["steps"]["aggregate"]["value"]}
            if publication.exists():
                if json.loads(publication.read_text("utf-8")) != result:
                    raise ValueError(
                        "An existing publication disagrees with this operation identity"
                    )
            else:
                save(publication, result)
            if fail_after == "publication-write":
                raise RuntimeError(
                    "Deliberate interruption after the effect, before its step checkpoint"
                )
        state["steps"][step] = {"value": result, "sha256": digest(result)}
        save(path, ledger)
        if fail_after == step:
            raise RuntimeError("Deliberate interruption after a completed stage")
    actual = json.loads(publication.read_text("utf-8"))
    if actual != state["steps"]["publish"]["value"]:
        raise ValueError("Published content differs from its accepted checkpoint")
    return {"identity": identity, "product": actual, "attempts": dict(state["attempts"])}


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        try:
            run_pipeline(root, [2, 3, 1], fail_after="validate")
        except RuntimeError:
            pass
        else:
            raise AssertionError("The deliberate interrupted stage must be observed")
        result = run_pipeline(root, [2, 3, 1])
        repeated = run_pipeline(root, [2, 3, 1])
        assert result == repeated and result["product"]["packages"] == 6
        assert result["attempts"] == {"validate": 1, "aggregate": 1, "publish": 1}
        return result


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        try:
            run_pipeline(root, [2, 3, 1], fail_after="publication-write")
        except RuntimeError:
            pass
        else:
            raise AssertionError("The caller must observe the unknown completion boundary")
        existing = next(root.glob("*.product.json"))
        before = existing.read_bytes()
        resumed = run_pipeline(root, [2, 3, 1])
        assert existing.read_bytes() == before and len(list(root.glob("*.product.json"))) == 1
        assert resumed["attempts"]["publish"] == 2 and resumed["product"]["packages"] == 6
        changed = run_pipeline(root, [2, 3, 4])
        assert changed["identity"] != resumed["identity"] and changed["product"]["packages"] == 9
        assert len(list(root.glob("*.product.json"))) == 2
        return {
            "reconciled_publication": resumed,
            "changed_input_product": changed,
            ("old_version_retained"): True,
            "scope": "local mechanism with real files; no distributed scheduler was deployed",
        }


def main():
    print("Resume a completed dependency checkpoint:", example_one())
    print("Reconcile an effect before retrying:", example_two())


if __name__ == "__main__":
    main()
