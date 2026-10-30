"""Pure fixture and adapter-routing checks; no Spark or Torch execution claims."""

from __future__ import annotations

import hashlib
import sys
import types
from dataclasses import replace

import pytest
from ds60_torch_training import data
from ds60_torch_training.contracts import TrainingError, canonical_json


def rows(count=6):
    return [
        {
            "id": i,
            "features": [1.0, i / 10],
            "label": float(i % 2),
            "weight": float(i != 3),
        }
        for i in range(count)
    ]


def snapshot(tmp_path, **options):
    return data.prepare_rows(
        rows(),
        tmp_path / "snapshot",
        feature_names=["bias", "x"],
        num_shards=3,
        source_metadata={"purpose": "test", "seed": 7},
        **options,
    )


def rewrite_manifest(path, manifest):
    body = {k: v for k, v in manifest.items() if k != "dataset_digest"}
    manifest["dataset_digest"] = hashlib.sha256(canonical_json(body)).hexdigest()
    path.chmod(0o600)
    path.write_bytes(canonical_json(manifest))


def test_snapshot_assignment_coverage_and_read_only_files(tmp_path):
    path = snapshot(tmp_path)
    manifest = data.load_manifest(path)
    assert manifest["rows"] == 6 and manifest["weight_sum"] == 5
    assert manifest["feature_names"] == ["bias", "x"]
    assert manifest["kind"] == "ds60-torch-row-shards"
    assert not (path.parent / ".staging").exists()
    assignment = data.assign_shards(manifest, 2)
    left = list(data.iter_rank_rows(path, assignment, 0))
    right = list(data.iter_rank_rows(path, assignment, 1))
    assert [r["id"] for r in left] == [0, 3, 2, 5]
    assert [r["id"] for r in right] == [1, 4]
    assert sorted(left + right, key=lambda r: r["id"]) == rows()
    assert not path.stat().st_mode & 0o222
    assert all(not (path.parent / f["path"]).stat().st_mode & 0o222 for f in manifest["files"])
    one = data.assign_shards(manifest, 1)
    assert len(list(data.iter_rank_rows(path, one, 0))) == 6


def test_metadata_load_never_reads_observation_files(tmp_path, monkeypatch):
    path = snapshot(tmp_path)
    original = data._read
    visited = []

    def read(name, limit):
        visited.append(name)
        assert name.name == "manifest.json"
        return original(name, limit)

    monkeypatch.setattr(data, "_read", read)
    manifest = data.load_manifest(path)
    data.assign_shards(manifest, 2)
    assert visited == [path]


def test_all_assigned_files_are_verified_before_first_yield(tmp_path):
    path = snapshot(tmp_path)
    manifest = data.load_manifest(path)
    assignment = data.assign_shards(manifest, 1)
    last = path.parent / manifest["files"][-1]["path"]
    last.chmod(0o600)
    last.write_bytes(last.read_bytes() + b" ")
    iterator = data.iter_rank_rows(path, assignment, 0)
    with pytest.raises(TrainingError, match="identity"):
        next(iterator)


def test_unassigned_payload_is_not_read_by_rank(tmp_path):
    path = snapshot(tmp_path)
    manifest = data.load_manifest(path)
    assignment = data.assign_shards(manifest, 3)
    unassigned = path.parent / manifest["files"][2]["path"]
    unassigned.unlink()
    assert [r["id"] for r in data.iter_rank_rows(path, assignment, 0)] == [0, 3]
    with pytest.raises(TrainingError):
        list(data.iter_rank_rows(path, assignment, 2))


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", True),
        ("id", 2**63),
        ("id", ""),
        ("id", None),
        ("features", [True, 1.0]),
        ("features", [float("nan"), 1.0]),
        ("features", ["1", 2.0]),
        ("features", [2**53 + 1, 2.0]),
        ("features", [1.0]),
        ("label", "1"),
        ("label", False),
        ("weight", -1),
        ("weight", float("inf")),
    ],
)
def test_invalid_rows_refused(tmp_path, field, value):
    record = rows(1)[0]
    record[field] = value
    with pytest.raises(TrainingError):
        data.prepare_rows([record], tmp_path / "bad", feature_names=["bias", "x"])
    assert not (tmp_path / "bad").exists()


def test_string_and_int_ids_are_distinct_and_unicode_is_preserved(tmp_path):
    records = [
        {"id": value, "features": [1], "label": 0}
        for value in [1, "1", "\u00e9" * 100, -(2**63), 2**63 - 1]
    ]
    path = data.prepare_rows(records, tmp_path / "ids", feature_names=["x"])
    manifest = data.load_manifest(path)
    actual = list(data.iter_rank_rows(path, data.assign_shards(manifest, 1), 0))
    assert [r["id"] for r in actual] == [r["id"] for r in records]


def test_class_index_and_default_weight(tmp_path):
    records = [{"id": "a", "features": [1], "label": 2}]
    path = data.prepare_rows(
        records, tmp_path / "class", feature_names=["x"], label_kind="class_index"
    )
    manifest = data.load_manifest(path)
    actual = list(data.iter_rank_rows(path, data.assign_shards(manifest, 1), 0))[0]
    assert type(actual["label"]) is int and actual["label"] == 2
    assert actual["weight"] == 1.0
    for value in [2.0, -1, True, "2"]:
        with pytest.raises(TrainingError):
            data.prepare_rows(
                [{**records[0], "label": value}],
                tmp_path / str(value),
                feature_names=["x"],
                label_kind="class_index",
            )


def test_duplicate_global_id_refused_before_reservation(tmp_path):
    with pytest.raises(TrainingError, match="Duplicate global"):
        data.prepare_rows(
            [rows(1)[0]] * 2,
            tmp_path / "duplicate",
            feature_names=["bias", "x"],
            num_shards=2,
        )
    assert not (tmp_path / "duplicate").exists()


def test_existing_path_and_failed_staging_refuse_retries(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    sentinel = existing / "sentinel"
    sentinel.write_text("untouched")
    with pytest.raises(TrainingError, match="already exists"):
        data.prepare_rows(rows(), existing, feature_names=["bias", "x"])
    assert sentinel.read_text() == "untouched"
    failed = tmp_path / "failed"
    with pytest.raises(TrainingError, match="byte bound|bounded canonical JSON"):
        data.prepare_rows(
            rows(),
            failed,
            feature_names=["bias", "x"],
            limits=replace(data.DataLimits(), max_shard_bytes=1),
        )
    assert failed.is_dir() and not (failed / "manifest.json").exists()
    with pytest.raises(TrainingError, match="already exists"):
        data.prepare_rows(rows(), failed, feature_names=["bias", "x"])


@pytest.mark.parametrize(
    "limits",
    [
        replace(data.DataLimits(), max_rows=2),
        replace(data.DataLimits(), max_features=1),
        replace(data.DataLimits(), max_source_bytes=1),
        replace(data.DataLimits(), max_rows=True),
        replace(data.DataLimits(), max_rows=32769),
    ],
)
def test_bounds_fail_closed(tmp_path, limits):
    with pytest.raises(TrainingError):
        snapshot(tmp_path, limits=limits)


def test_empty_dataset_and_zero_global_weight_never_commit(tmp_path):
    for name, records in [
        ("empty", []),
        ("zero", [{**r, "weight": 0.0} for r in rows()]),
    ]:
        with pytest.raises(TrainingError):
            data.prepare_rows(records, tmp_path / name, feature_names=["bias", "x"])
        assert not (tmp_path / name / "manifest.json").exists()


@pytest.mark.parametrize(
    "mapping",
    [
        [[], ["shards/part-00000.jsonl"]],
        [["shards/part-00000.jsonl"], ["shards/part-00000.jsonl"]],
        [["shards/part-00000.jsonl"], ["shards/part-00001.jsonl"]],
        [["../escape"], ["shards/part-00001.jsonl"]],
    ],
)
def test_assignment_missing_duplicate_empty_and_unknown_refused(tmp_path, mapping):
    manifest = data.load_manifest(snapshot(tmp_path))
    with pytest.raises(TrainingError):
        data.assign_shards(manifest, 2, rank_files=mapping)


def test_empty_shard_retained_but_empty_rank_refused(tmp_path):
    path = data.prepare_rows(
        rows(1), tmp_path / "empty-shard", feature_names=["bias", "x"], num_shards=2
    )
    manifest = data.load_manifest(path)
    assert manifest["files"][1]["rows"] == 0
    with pytest.raises(TrainingError, match="positive rows"):
        data.assign_shards(manifest, 2)
    assert len(list(data.iter_rank_rows(path, data.assign_shards(manifest, 1), 0))) == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("world_size", True),
        ("world_size", 2.0),
        ("dataset_digest", "0" * 64),
        ("assignment_digest", "0" * 64),
    ],
)
def test_assignment_identity_and_exact_integer_guards(tmp_path, field, value):
    path = snapshot(tmp_path)
    assignment = data.assign_shards(data.load_manifest(path), 2)
    assignment[field] = value
    with pytest.raises(TrainingError):
        next(data.iter_rank_rows(path, assignment, 0))


def test_rank_booleans_and_count_tampering_rejected(tmp_path):
    path = snapshot(tmp_path)
    assignment = data.assign_shards(data.load_manifest(path), 2)
    with pytest.raises(TrainingError):
        next(data.iter_rank_rows(path, assignment, True))
    assignment["ranks"][0]["rank"] = False
    with pytest.raises(TrainingError):
        next(data.iter_rank_rows(path, assignment, 0))


def test_rehashed_manifest_does_not_hide_changed_payload_counts(tmp_path):
    path = snapshot(tmp_path)
    manifest = data.load_manifest(path)
    manifest["files"][0]["ordered_id_sha256"] = "0" * 64
    rewrite_manifest(path, manifest)
    admitted = data.load_manifest(path)
    with pytest.raises(TrainingError, match="ID order"):
        next(data.iter_rank_rows(path, data.assign_shards(admitted, 1), 0))


def test_unsafe_paths_duplicate_json_keys_and_symlinks(tmp_path):
    path = snapshot(tmp_path)
    manifest = data.load_manifest(path)
    manifest["files"][0]["path"] = "../outside.jsonl"
    rewrite_manifest(path, manifest)
    with pytest.raises(TrainingError, match="Unsafe shard"):
        data.load_manifest(path)
    path.write_bytes(b'{"kind":"a","kind":"b"}')
    with pytest.raises(TrainingError, match="JSON"):
        data.load_manifest(path)
    link = tmp_path / "link"
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(TrainingError, match="Symlink"):
        data.prepare_rows(rows(), link / "new", feature_names=["bias", "x"])


def test_manifest_digest_tampering_and_snapshot_source_identity(tmp_path):
    path = snapshot(tmp_path)
    manifest = data.load_manifest(path)
    manifest["source_metadata"]["seed"] = 8
    path.chmod(0o600)
    path.write_bytes(canonical_json(manifest))
    with pytest.raises(TrainingError, match="digest"):
        data.load_manifest(path)


def fake_spark(monkeypatch, records, attempt=0):
    """Routing double only. It supplies no real Spark execution evidence."""
    modules = {
        name: types.ModuleType(name)
        for name in [
            "pyspark",
            "pyspark.sql",
            "pyspark.sql.functions",
            "pyspark.sql.types",
        ]
    }
    type_module = modules["pyspark.sql.types"]
    for name in [
        "ByteType",
        "DoubleType",
        "FloatType",
        "IntegerType",
        "LongType",
        "ShortType",
        "StringType",
    ]:
        setattr(type_module, name, type(name, (), {}))

    class Column:
        def __init__(self, name=None, value=None):
            self.name, self.value, self.output = name, value, name

        def alias(self, name):
            self.output = name
            return self

    functions = modules["pyspark.sql.functions"]
    functions.col = lambda name: Column(name[1:-1].replace("``", "`"))
    functions.lit = lambda value: Column(value=value)
    context = types.SimpleNamespace(index=0)
    context.attemptNumber = lambda: attempt
    context.partitionId = lambda: context.index
    modules["pyspark"].TaskContext = types.SimpleNamespace(get=lambda: context)
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)

    class RDD:
        def __init__(self, partitions):
            self.partitions = partitions

        def getNumPartitions(self):
            return len(self.partitions)

        def mapPartitionsWithIndex(self, function):
            result = []
            for index, partition in enumerate(self.partitions):
                context.index = index
                result.extend(function(index, iter(partition)))
            return RDD([result])

        def collect(self):
            result = [row for part in self.partitions for row in part]
            assert all(
                type(row) is dict
                and set(row)
                == {
                    "path",
                    "bytes",
                    "sha256",
                    "rows",
                    "weight_sum",
                    "ordered_id_sha256",
                }
                for row in result
            ), "Only metadata may reach driver"
            return result

    class Frame:
        _jdf = object()
        isStreaming = False
        columns = ["id", "x", "label", "weight"]
        schema = types.SimpleNamespace(
            fields=[
                types.SimpleNamespace(
                    name=name,
                    dataType=(type_module.LongType() if name == "id" else type_module.DoubleType()),
                )
                for name in columns
            ]
        )

        def select(self, *columns):
            self.projected = [
                tuple(row[col.name] if col.name is not None else col.value for col in columns)
                for row in records
            ]
            return self

        def repartition(self, count, name):
            assert name == "__ds60_id"
            self.partitions = [
                [row for row in self.projected if row[0] % count == index] for index in range(count)
            ]
            return self

        def sortWithinPartitions(self, name):
            self.partitions = [sorted(part, key=lambda row: row[0]) for part in self.partitions]
            return self

        @property
        def rdd(self):
            return RDD(self.partitions)

    return Frame()


def test_dataframe_adapter_collects_metadata_only_with_deterministic_shards(tmp_path, monkeypatch):
    records = [
        {"id": i, "x": i * 0.25, "label": float(i % 2), "weight": 1.0} for i in reversed(range(6))
    ]
    frame = fake_spark(monkeypatch, records)
    path = data.prepare_dataframe(
        frame,
        tmp_path / "df",
        feature_names=["x"],
        label_col="label",
        id_col="id",
        weight_col="weight",
        source_metadata={"adapter_test_double": True},
    )
    manifest = data.load_manifest(path)
    assignment = data.assign_shards(manifest, 2)
    assert [r["id"] for r in data.iter_rank_rows(path, assignment, 0)] == [0, 2, 4]
    assert [r["id"] for r in data.iter_rank_rows(path, assignment, 1)] == [1, 3, 5]


def test_dataframe_writer_retry_refused_and_no_manifest(tmp_path, monkeypatch):
    frame = fake_spark(monkeypatch, [{"id": 0, "x": 1.0, "label": 1.0, "weight": 1.0}], attempt=1)
    with pytest.raises(TrainingError, match="retry"):
        data.prepare_dataframe(
            frame,
            tmp_path / "retry",
            feature_names=["x"],
            label_col="label",
            id_col="id",
        )
    assert not (tmp_path / "retry" / "manifest.json").exists()


def test_dataframe_duplicate_ids_fail_before_commit(tmp_path, monkeypatch):
    row = {"id": 0, "x": 1.0, "label": 1.0, "weight": 1.0}
    frame = fake_spark(monkeypatch, [row, row])
    with pytest.raises(TrainingError, match="Duplicate row ID"):
        data.prepare_dataframe(
            frame,
            tmp_path / "duplicate",
            feature_names=["x"],
            label_col="label",
            id_col="id",
        )
    assert not (tmp_path / "duplicate" / "manifest.json").exists()


def test_dataframe_empty_partition_does_not_become_empty_training_rank(tmp_path, monkeypatch):
    frame = fake_spark(monkeypatch, [{"id": 0, "x": 1.0, "label": 0.0, "weight": 1.0}])
    path = data.prepare_dataframe(
        frame,
        tmp_path / "empty-partition",
        feature_names=["x"],
        label_col="label",
        id_col="id",
    )
    manifest = data.load_manifest(path)
    assert [item["rows"] for item in manifest["files"]] == [1, 0]
    with pytest.raises(TrainingError, match="positive rows"):
        data.assign_shards(manifest, 2)
    assert len(list(data.iter_rank_rows(path, data.assign_shards(manifest, 1), 0))) == 1


def test_dataframe_preserves_integer_feature_until_exact_float64_guard(tmp_path, monkeypatch):
    frame = fake_spark(monkeypatch, [{"id": 0, "x": 2**53 + 1, "label": 0.0, "weight": 1.0}])
    with pytest.raises(TrainingError, match="exactly representable"):
        data.prepare_dataframe(
            frame,
            tmp_path / "precision",
            feature_names=["x"],
            label_col="label",
            id_col="id",
        )


def test_writer_duplicate_attempt_cannot_overwrite_staged_bytes(tmp_path):
    root = data._reserve(tmp_path / "attempt")
    limits = data.DataLimits()
    first = data._write_partition(rows(1), root, 0, ["bias", "x"], "float", limits)
    original = (root / ".staging" / "part-00000.jsonl").read_bytes()
    with pytest.raises(TrainingError, match="retry"):
        data._write_partition(rows(2), root, 0, ["bias", "x"], "float", limits)
    assert (root / ".staging" / "part-00000.jsonl").read_bytes() == original
    assert hashlib.sha256(original).hexdigest() == first["sha256"]


def test_existing_commit_marker_cannot_be_overwritten(tmp_path):
    root = data._reserve(tmp_path / "commit-collision")
    limits = data.DataLimits()
    record = data._write_partition(rows(1), root, 0, ["bias", "x"], "float", limits)
    (root / "manifest.json").write_bytes(b"existing owner")
    with pytest.raises(FileExistsError):
        data._commit(root, [record], ["bias", "x"], "float", {}, limits)
    assert (root / "manifest.json").read_bytes() == b"existing owner"


def test_noncanonical_payload_and_duplicate_json_are_refused_even_with_new_hash(
    tmp_path,
):
    for name, raw in [
        ("noncanonical", b'{"id":0,"features":[1.0,0.0],"label":0.0,"weight":1.0}\n'),
        (
            "duplicate",
            b'{"id":0,"id":0,"features":[1.0,0.0],"label":0.0,"weight":1.0}\n',
        ),
    ]:
        path = data.prepare_rows(rows(1), tmp_path / name, feature_names=["bias", "x"])
        manifest = data.load_manifest(path)
        file = path.parent / manifest["files"][0]["path"]
        file.chmod(0o600)
        file.write_bytes(raw)
        manifest["files"][0]["bytes"] = len(raw)
        manifest["files"][0]["sha256"] = hashlib.sha256(raw).hexdigest()
        rewrite_manifest(path, manifest)
        admitted = data.load_manifest(path)
        with pytest.raises(TrainingError):
            next(data.iter_rank_rows(path, data.assign_shards(admitted, 1), 0))


def test_dataframe_streaming_and_connect_refuse_before_writing(tmp_path, monkeypatch):
    for name in ["streaming", "connect"]:
        frame = fake_spark(monkeypatch, [])
        if name == "streaming":
            frame.isStreaming = True
        else:
            frame._jdf = None
        with pytest.raises(TrainingError):
            data.prepare_dataframe(
                frame,
                tmp_path / name,
                feature_names=["x"],
                label_col="label",
                id_col="id",
            )
        assert not (tmp_path / name).exists()


def test_dataframe_total_staged_byte_budget_is_divided_before_writers(tmp_path, monkeypatch):
    frame = fake_spark(monkeypatch, [{"id": 0, "x": 1.0, "label": 1.0, "weight": 1.0}])
    with pytest.raises(TrainingError):
        data.prepare_dataframe(
            frame,
            tmp_path / "bounded",
            feature_names=["x"],
            label_col="label",
            id_col="id",
            limits=replace(data.DataLimits(), max_total_bytes=2),
        )
    assert not (tmp_path / "bounded" / "manifest.json").exists()
    assert sum(p.stat().st_size for p in (tmp_path / "bounded" / ".staging").iterdir()) <= 2


def test_numeric_shard_metadata_never_accepts_booleans(tmp_path):
    path = snapshot(tmp_path)
    manifest = data.load_manifest(path)
    manifest["files"][0]["rows"] = True
    rewrite_manifest(path, manifest)
    with pytest.raises(TrainingError, match="exact integer"):
        data.load_manifest(path)


def test_shard_symlink_refused_before_any_row(tmp_path):
    path = snapshot(tmp_path)
    manifest = data.load_manifest(path)
    file = path.parent / manifest["files"][0]["path"]
    elsewhere = tmp_path / "outside.jsonl"
    elsewhere.write_bytes(file.read_bytes())
    file.unlink()
    file.symlink_to(elsewhere)
    with pytest.raises(TrainingError, match="Symlink"):
        next(data.iter_rank_rows(path, data.assign_shards(manifest, 1), 0))
