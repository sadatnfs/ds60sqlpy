"""Output declarations retain old formats without masking missing or unrelated evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts import check_module_references as references
from scripts.declared_outputs import load_contracts, verify_contract

ROOT = Path(__file__).resolve().parents[1]


def write_contract(root: Path, units: list[Any], **fields: Any) -> Path:
    path = root / "courses/example/figure-contracts.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "units": units, **fields}), encoding="utf-8")
    return path


def load_unit(tmp_path: Path, **fields: Any) -> dict[str, Any]:
    write_contract(tmp_path, [{"id": "example-001", **fields}])
    return load_contracts(tmp_path, "example", {"example-001"})["example-001"]


def chart(rows: list[list[Any]] | None = None) -> dict[str, Any]:
    metadata: dict[str, Any] = {"description": "Observed synthetic values"}
    if rows is not None:
        metadata["table"] = {"columns": ["Value"], "rows": rows}
    return {
        "kind": "plotly",
        "figure": {
            "data": [{"type": "scatter", "x": [0], "y": [1]}],
            "layout": {"meta": metadata},
        },
    }


def table(rows: list[list[Any]]) -> dict[str, Any]:
    return {
        "kind": "table",
        "description": "Observed values",
        "table": {"columns": ["Value"], "rows": rows},
    }


@pytest.mark.parametrize(
    "subject", ["applied-science", "bayesian-computing", "julia", "llm-evaluation"]
)
def test_existing_course_output_declarations_remain_admitted(subject: str) -> None:
    raw = json.loads((ROOT / f"courses/{subject}/lessons.json").read_text())
    identities = {
        name
        for lesson in raw["lessons"]
        for name in [
            lesson["id"],
            *(f"{lesson['id']}@{variant['id']}" for variant in lesson.get("variants", [])),
        ]
    }
    contracts = load_contracts(ROOT, subject, identities)
    assert contracts and set(contracts) <= identities
    if subject == "bayesian-computing":
        assert contracts["bayes-009"]["kinds"] == ["png"]
        assert contracts["bayes-024"]["kinds"] == ["table", "plotly"]
        assert contracts["bayes-024"]["count"] == 2
        assert "short traces" in contracts["bayes-024"]["limits"]


def test_heterogeneous_kind_list_accepts_only_a_matching_optional_count(tmp_path: Path) -> None:
    contract = load_unit(
        tmp_path,
        kinds=["table", "plotly"],
        count=2,
        origin="Observed sampler CSV",
        limits="Short runs do not establish convergence.",
        description_required=True,
    )
    verify_contract(contract, [table([[42]]), chart()])
    assert contract["origin"] == "Observed sampler CSV"
    for artifacts in ([chart()], [table([[42]]), table([[43]])]):
        with pytest.raises(ValueError, match="missing or changed kind"):
            verify_contract(contract, artifacts)


def test_homogeneous_count_preserves_duplicate_output_expectations(tmp_path: Path) -> None:
    contract = load_unit(tmp_path, kind="plotly", count=2)
    verify_contract(contract, [chart(), chart()])
    with pytest.raises(ValueError, match="missing or changed kind"):
        verify_contract(contract, [chart()])


@pytest.mark.parametrize(
    "fields",
    [
        {},
        {"kind": "png"},
        {"kind": "png", "count": True},
        {"kind": "png", "count": 0},
        {"kind": "png", "count": 3},
        {"kinds": []},
        {"kinds": "plotly"},
        {"kinds": [["plotly"]]},
        {"kinds": ["plotly", "table", "json"]},
        {"kinds": ["html"]},
        {"kinds": ["png"], "kind": "png"},
        {"kinds": ["png"], "count": 2},
        {"kinds": ["png"], "count": 1.0},
        {"kinds": ["png"], "count": True},
        {"kinds": ["plotly"], "description_required": "true"},
        {"kinds": ["plotly"], "table_required": 1},
        {"kinds": ["plotly"], "origin": []},
        {"kinds": ["plotly"], "origin": "  "},
        {"kinds": ["plotly"], "limits": "x" * 2001},
        {"kinds": ["plotly"], "optional": True},
        {"kinds": ["plotly"], "source_sha256": "0" * 64},
        {"kinds": ["plotly"], "table_rows": True},
        {"kinds": ["plotly"], "table_rows": -1},
        {"kinds": ["plotly"], "table_rows": 101},
        {"kinds": ["plotly"], "table_rows": 1, "table_required": False},
        {"kinds": ["json"], "table_required": True},
        {"kinds": ["png"], "table_rows": 1},
    ],
)
def test_malformed_or_contradictory_unit_contracts_fail_closed(
    tmp_path: Path, fields: dict[str, Any]
) -> None:
    with pytest.raises(ValueError):
        load_unit(tmp_path, **fields)


@pytest.mark.parametrize(
    "fields",
    [
        {"schema_version": True},
        {"schema_version": 1.0},
        {"schema_version": 2},
        {"unrecognized": "ignored rules would be unsafe"},
    ],
)
def test_top_level_contract_schema_is_strict(tmp_path: Path, fields: dict[str, Any]) -> None:
    write_contract(tmp_path, [], **fields)
    with pytest.raises(ValueError, match="Invalid reference"):
        load_contracts(tmp_path, "example", set())


@pytest.mark.parametrize("unit", [None, [], "example-001"])
def test_unit_records_must_be_objects(tmp_path: Path, unit: Any) -> None:
    write_contract(tmp_path, [unit])
    with pytest.raises(ValueError, match="expectation fields"):
        load_contracts(tmp_path, "example", {"example-001"})


def test_duplicate_json_fields_cannot_override_a_rule(tmp_path: Path) -> None:
    path = write_contract(tmp_path, [])
    path.write_text(
        '{"schema_version":1,"units":[{"id":"example-001","kind":"plotly","count":1,"count":2}]}',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate"):
        load_contracts(tmp_path, "example", {"example-001"})


def test_contracts_bind_exact_admitted_variants_and_reject_duplicate_ids(tmp_path: Path) -> None:
    unit = {"id": "example-001@plotly", "kind": "plotly", "count": 1}
    write_contract(tmp_path, [unit])
    with pytest.raises(ValueError, match="authored unit"):
        load_contracts(tmp_path, "example", {"example-001"})
    assert set(load_contracts(tmp_path, "example", {"example-001@plotly"})) == {
        "example-001@plotly"
    }
    write_contract(tmp_path, [unit, unit])
    with pytest.raises(ValueError, match="unique authored"):
        load_contracts(tmp_path, "example", {"example-001@plotly"})


@pytest.mark.parametrize("subject", ["../other", "nested/subject", "", "Example"])
def test_subject_identity_is_validated_even_when_contract_file_is_absent(
    tmp_path: Path, subject: str
) -> None:
    with pytest.raises(ValueError, match="subject"):
        load_contracts(tmp_path, subject, set())


def test_absent_contract_is_optional_but_an_oversized_file_is_not(tmp_path: Path) -> None:
    assert load_contracts(tmp_path, "example", {"example-001"}) == {}
    path = write_contract(tmp_path, [])
    path.write_bytes(b" " * 64_001)
    with pytest.raises(ValueError, match="metadata limit"):
        load_contracts(tmp_path, "example", {"example-001"})


def test_contract_source_cannot_be_replaced_by_a_symlink(tmp_path: Path) -> None:
    path = write_contract(tmp_path, [])
    retained = tmp_path / "retained.json"
    path.rename(retained)
    path.symlink_to(retained)
    with pytest.raises(ValueError, match="symbolic link"):
        load_contracts(tmp_path, "example", set())
    assert json.loads(retained.read_text())["units"] == []


@pytest.mark.parametrize("kind", ["table", "plotly"])
@pytest.mark.parametrize("rows", [[], [[None], [0], [False], ["9007199254740993"]]])
def test_row_count_is_enforced_without_a_separate_table_flag(
    tmp_path: Path, kind: str, rows: list[list[Any]]
) -> None:
    contract = load_unit(tmp_path, kinds=[kind], table_rows=len(rows))
    make = table if kind == "table" else chart
    verify_contract(contract, [make(rows)])
    with pytest.raises(ValueError, match="row count changed"):
        verify_contract(contract, [make([*rows, [7]])])
    if kind == "plotly":
        with pytest.raises(ValueError, match="accessible output table"):
            verify_contract(contract, [chart()])


def test_required_description_is_not_inferred_from_an_unrelated_plot_title(tmp_path: Path) -> None:
    contract = load_unit(tmp_path, kinds=["plotly"], description_required=True)
    artifact = chart()
    artifact["figure"]["layout"] = {"title": {"text": "A title is not a description"}}
    with pytest.raises(ValueError, match="description is missing"):
        verify_contract(contract, [artifact])


@pytest.mark.parametrize("kind", ["table", "plotly", "json"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), 9_007_199_254_740_993])
def test_expected_output_kinds_do_not_bypass_value_fidelity_validation(
    tmp_path: Path, kind: str, value: float | int
) -> None:
    contract = load_unit(tmp_path, kinds=[kind])
    artifact = (
        {"kind": "json", "description": "Observed value", "data": {"value": value}}
        if kind == "json"
        else (table([[value]]) if kind == "table" else chart([[value]]))
    )
    with pytest.raises(ValueError):
        verify_contract(contract, [artifact])


@pytest.mark.parametrize(
    "changed",
    [
        {"source_sha256": "0" * 64},
        {"lesson_id": "example-001@plotly"},
        {"profile": "another-profile"},
        {"job_id": "another-job"},
    ],
)
def test_matching_outputs_cannot_substitute_for_the_selected_source_receipt(
    tmp_path: Path, changed: dict[str, str]
) -> None:
    contract = load_unit(tmp_path, kinds=["table", "json"], count=2)
    case = references.ReferenceCase(
        "example-001",
        "example",
        "python-core",
        "python",
        "practice",
        None,
        "courses/example/solutions/reference.py",
        "print(42)\n",
        contract,
    )
    job = {
        "job_id": "job",
        "lesson_id": case.lesson_id,
        "profile": case.profile,
        "source_sha256": case.source_sha256,
        "status": "succeeded",
        "returncode": 0,
        "checks": [],
        "truncated": False,
        "artifacts": [table([[42]]), {"kind": "json", "description": "Model", "data": {}}],
    }
    references.verify_result(case, "job", job)
    with pytest.raises(ValueError, match="source-bound receipt"):
        references.verify_result(case, "job", {**job, **changed})
