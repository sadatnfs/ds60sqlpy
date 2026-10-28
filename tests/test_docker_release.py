"""Source, image identity and ordered release promotion without registry writes."""

from __future__ import annotations

import copy
import json
import platform
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import pytest

from scripts import docker_release as release
from scripts.docker_registry import (
    OCI_INDEX,
    OCI_MANIFEST,
    Descriptor,
    Head,
    Manifest,
    Registry,
    ReleaseError,
    json_object,
    sha256,
)


@pytest.fixture(autouse=True)
def reject_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.request

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("Release tests must not make real registry/authentication calls")

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", forbidden)


class FakeRegistry(Registry):
    def __init__(self) -> None:
        self.objects: dict[str, Manifest] = {}
        self.tags: dict[str, str] = {}
        self.puts: list[str] = []
        self.gets: list[str] = []
        self.heads: list[str] = []
        self.fail_tag: str | None = None

    def add(self, body: bytes, tag: str | None = None) -> Manifest:
        value = json_object(body)
        manifest = Manifest(Descriptor(value["mediaType"], sha256(body), len(body)), value, body)
        self.objects[manifest.descriptor.digest] = manifest
        if tag is not None:
            self.tags[tag] = manifest.descriptor.digest
        return manifest

    def head(self, reference: str) -> Head | None:
        self.heads.append(reference)
        digest = self.tags.get(reference, reference)
        value = self.objects.get(digest)
        return (
            None
            if value is None
            else Head(value.descriptor.media_type, digest, value.descriptor.size)
        )

    def get(self, reference: str) -> Manifest:
        self.gets.append(reference)
        digest = self.tags.get(reference, reference)
        if digest not in self.objects:
            raise ReleaseError("Missing fake manifest")
        return self.objects[digest]

    def put(self, tag: str, body: bytes, media_type: str = OCI_INDEX) -> Descriptor:
        assert media_type == OCI_INDEX
        self.puts.append(tag)
        if self.fail_tag == tag:
            raise ReleaseError("Injected publication interruption")
        return self.add(body, tag).descriptor


def encoded(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def native(registry: FakeRegistry, name: str) -> tuple[Manifest, str]:
    config = sha256(("config:" + name).encode())
    manifest = registry.add(
        encoded(
            {
                "schemaVersion": 2,
                "mediaType": OCI_MANIFEST,
                "config": {
                    "mediaType": "application/vnd.oci.image.config.v1+json",
                    "digest": config,
                    "size": 128,
                },
                "layers": [],
            }
        )
    )
    return manifest, config


def root_index(
    registry: FakeRegistry, image: Manifest, arch: str, *, attestation: bool = False
) -> Manifest:
    entries = [{**image.descriptor.record(), "platform": {"os": "linux", "architecture": arch}}]
    if attestation:
        attest, _ = native(registry, "attestation:" + image.descriptor.digest)
        entries.append(
            {
                **attest.descriptor.record(),
                "platform": {"os": "unknown", "architecture": "unknown"},
                "annotations": {
                    "vnd.docker.reference.type": "attestation-manifest",
                    "vnd.docker.reference.digest": image.descriptor.digest,
                },
            }
        )
    return registry.add(encoded({"schemaVersion": 2, "mediaType": OCI_INDEX, "manifests": entries}))


@pytest.fixture
def context() -> release.Context:
    return release.Context(
        "exampleuser", "exampleuser/ds60sqlpy", "example/classroom", "1.0.0", "a" * 40, "12345", "1"
    )


@pytest.fixture
def profiles(tmp_path: Path) -> dict[str, release.Profile]:
    (tmp_path / "docker").mkdir()
    (tmp_path / "docker/classroom-images.tsv").write_text(
        "app lab ds60sqlpy-lab lab DS60_LAB_IMAGE app\n"
        "python-core core ds60sqlpy-worker-python-core worker-python-core "
        "DS60_CORE_IMAGE ordinary\n"
        "java21 java ds60sqlpy-worker-java21 worker-java21 DS60_JAVA_IMAGE ordinary\n"
    )
    (tmp_path / "docker/ci-profile-groups.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "groups": [
                    {"id": "python-core", "profiles": ["python-core"]},
                    {"id": "java", "profiles": ["java21"]},
                ],
            }
        )
    )
    return release.catalog(tmp_path)


def proofs(selected: set[str], group: str) -> list[dict[str, Any]]:
    required = (selected - {"app"}) | ({"python-core"} if "app" in selected else set())
    common = {
        "sha256": sha256(b"report"),
        "profiles": sorted(required),
        "passed": True,
        "complete": True,
    }
    return [
        {**common, "kind": "module-references", "references": 2},
        {
            **common,
            "kind": "ci-summary",
            "group": group,
            "checks": sorted(release.mandatory_ci_checks(group)),
        },
    ]


def receipt(
    registry: FakeRegistry,
    context: release.Context,
    profiles: dict[str, release.Profile],
    arch: str,
    group: str,
    *,
    seed_digests: dict[str, str] | None = None,
    content: str = "first",
) -> dict[str, Any]:
    selected = release.SEEDS if group == "python-core" else {"java21"}
    images = []
    for key in sorted(selected):
        image, config = native(registry, f"{content}:{key}:{arch}")
        root = root_index(registry, image, arch, attestation=True)
        candidate = release.candidate_tag(context, key, arch)
        registry.tags[candidate] = root.descriptor.digest
        images.append(
            {
                "profile": key,
                "local_repository": profiles[key].local_repository,
                "tested_image_id": root.descriptor.digest,
                "candidate_tag": candidate,
                "candidate_root": root.descriptor.record(),
                "native": {
                    **image.descriptor.record(),
                    "platform": {"os": "linux", "architecture": arch},
                },
                "config_digest": config if key in release.SEEDS else None,
                "identity_basis": "root",
            }
        )
    return {
        "schema_version": 1,
        "kind": "ds60-staged-images",
        "context": asdict(context),
        "architecture": arch,
        "group": group,
        "seed_native_digests": seed_digests or {},
        "qualification": proofs(set(selected), group),
        "images": images,
    }


def complete_receipts(
    directory: Path,
    registry: FakeRegistry,
    context: release.Context,
    profiles: dict[str, release.Profile],
) -> dict[str, dict[str, Descriptor]]:
    directory.mkdir()
    expected: dict[str, dict[str, Descriptor]] = {key: {} for key in profiles}
    for arch in release.ARCHITECTURES:
        seed = receipt(registry, context, profiles, arch, "python-core")
        bindings = {image["profile"]: image["native"]["digest"] for image in seed["images"]}
        worker = receipt(registry, context, profiles, arch, "java", seed_digests=bindings)
        for value in (seed, worker):
            folder = directory / f"{value['group']}-{arch}"
            folder.mkdir()
            (folder / "release-receipt.json").write_text(json.dumps(value))
            for image in value["images"]:
                expected[image["profile"]][arch] = release.native_descriptor(image["native"], arch)
    return expected


def test_oci_index_selects_native_and_recognized_attestation_only() -> None:
    registry = FakeRegistry()
    image, _ = native(registry, "native")
    root = root_index(registry, image, "arm64", attestation=True)
    assert release.select_native(root, "arm64") == image.descriptor
    for mutate in (
        "another-native",
        "duplicate-native",
        "unrecognized-attestation",
        "wrong-subject",
    ):
        changed = copy.deepcopy(root.document)
        entries = changed["manifests"]
        if mutate == "another-native":
            entries[1]["platform"] = {"os": "linux", "architecture": "amd64"}
        elif mutate == "duplicate-native":
            entries.append(copy.deepcopy(entries[0]))
        elif mutate == "unrecognized-attestation":
            entries[1]["annotations"].clear()
        else:
            entries[1]["annotations"]["vnd.docker.reference.digest"] = "sha256:" + "0" * 64
        with pytest.raises(ReleaseError):
            release.select_native(registry.add(encoded(changed)), "arm64")


def test_docker29_worker_index_id_is_verified_without_refetching_children(
    context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    image, _ = native(registry, "java")
    root = root_index(registry, image, "amd64", attestation=True)
    registry.tags[release.candidate_tag(context, "java21", "amd64")] = root.descriptor.digest
    local = {
        "profile": "java21",
        "local_repository": profiles["java21"].local_repository,
        "tested_image_id": root.descriptor.digest,
        "local_descriptor": root.descriptor.record(),
    }
    result = release.verify_candidate(registry, context, local, "amd64")
    assert result["identity_basis"] == "root" and result["config_digest"] is None
    assert result["native"]["digest"] == image.descriptor.digest
    assert registry.gets == [root.descriptor.digest]


def test_old_config_id_fallback_and_changed_root_are_not_confused(
    context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    image, config = native(registry, "legacy")
    root = root_index(registry, image, "amd64")
    registry.tags[release.candidate_tag(context, "java21", "amd64")] = root.descriptor.digest
    local = {
        "profile": "java21",
        "local_repository": profiles["java21"].local_repository,
        "tested_image_id": config,
        "local_descriptor": None,
    }
    result = release.verify_candidate(registry, context, local, "amd64")
    assert result["identity_basis"] == "config" and result["config_digest"] == config
    with pytest.raises(ReleaseError, match="root descriptor"):
        release.verify_candidate(
            registry,
            context,
            {
                **local,
                "local_descriptor": {**root.descriptor.record(), "digest": "sha256:" + "0" * 64},
            },
            "amd64",
        )
    with pytest.raises(ReleaseError, match="neither"):
        release.verify_candidate(
            registry, context, {**local, "tested_image_id": "sha256:" + "0" * 64}, "amd64"
        )


def test_complete_promotion_orders_workers_before_each_app_pointer(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    expected = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    inputs = release.promotion_inputs(tmp_path / "receipts", context, profiles, registry, tmp_path)
    assert inputs == expected
    report = release.promote_release(
        context, profiles, registry, natives=inputs, output=tmp_path / "promotion.json"
    )
    assert registry.puts == [
        "1.0.0-worker-python-core",
        "1.0.0-worker-java21",
        "1.0.0",
        "latest-worker-python-core",
        "latest-worker-java21",
        "latest",
    ]
    assert report["status"] == "published"
    assert len(report["version_tags"]) == len(report["latest_tags"]) == 3
    assert registry.gets == []  # Descriptor HEAD verification and direct index PUT only.
    release.promote_release(
        context, profiles, registry, natives=inputs, output=tmp_path / "repeat.json"
    )
    assert len(registry.puts) == 6  # Exact repeat never rewrites immutable or matching aliases.
    assert release.gate_release(context, profiles, registry)["mode"] == "noop"


def add_unselected_group(root: Path) -> dict[str, release.Profile]:
    image_catalog = root / "docker/classroom-images.tsv"
    image_catalog.write_text(
        image_catalog.read_text()
        + "cpp20 cpp ds60sqlpy-worker-cpp20 worker-cpp20 DS60_CPP_IMAGE ordinary\n"
    )
    group_catalog = root / "docker/ci-profile-groups.json"
    groups = json.loads(group_catalog.read_text())
    groups["groups"].append({"id": "cpp", "profiles": ["cpp20"]})
    group_catalog.write_text(json.dumps(groups))
    return release.catalog(root)


def test_targeted_publication_binds_exact_group_and_only_moves_selected_aliases(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    profiles = add_unselected_group(tmp_path)
    registry = FakeRegistry()
    gate = release.gate_release(context, profiles, registry, target_group="java", root=tmp_path)
    assert gate["mode"] == "build"
    assert gate["selection"] == {"group": "java", "profiles": ["app", "java21", "python-core"]}
    complete_receipts(tmp_path / "receipts", registry, context, profiles)
    inputs = release.promotion_inputs(
        tmp_path / "receipts", context, profiles, registry, tmp_path, target_group="java"
    )
    assert set(inputs) == {"app", "python-core", "java21"}
    report = release.promote_release(
        context,
        profiles,
        registry,
        natives=inputs,
        output=tmp_path / "partial.json",
        target_group="java",
        root=tmp_path,
    )
    assert report["scope"] == "partial" and report["group"] == "java"
    assert report["profiles"] == ["app", "java21", "python-core"]
    assert registry.puts == [
        "1.0.0-worker-python-core",
        "1.0.0-worker-java21",
        "1.0.0",
        "latest-worker-python-core",
        "latest-worker-java21",
        "latest",
    ]
    assert not any("cpp20" in tag for tag in registry.tags)
    for key in ("app", "python-core", "java21"):
        manifest = registry.get(release.version_tag(profiles[key], context.version))
        assert manifest.document["annotations"][release.SCOPE] == "partial"
        assert manifest.document["annotations"][release.GROUP] == "java"
    assert (
        release.gate_release(context, profiles, registry, target_group="java", root=tmp_path)[
            "mode"
        ]
        == "noop"
    )
    with pytest.raises(ReleaseError, match="partial version tag"):
        release.gate_release(context, profiles, registry, root=tmp_path)
    newer = replace(context, version="1.0.1", revision="b" * 40)
    assert release.gate_release(newer, profiles, registry, root=tmp_path)["mode"] == "build"
    full = complete_receipts(tmp_path / "new-receipts", registry, newer, profiles)
    for architecture in release.ARCHITECTURES:
        cpp, _ = native(registry, "new-cpp-" + architecture)
        full["cpp20"][architecture] = cpp.descriptor
    complete = release.promote_release(
        newer,
        profiles,
        registry,
        natives=full,
        output=tmp_path / "complete.json",
    )
    assert complete["status"] == "published"
    assert registry.puts[-1] == "latest"
    assert "latest-worker-cpp20" in registry.puts


def test_targeted_publication_rejects_other_source_version_before_any_write(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    profiles = add_unselected_group(tmp_path)
    registry = FakeRegistry()
    complete_receipts(tmp_path / "receipts", registry, context, profiles)
    inputs = release.promotion_inputs(
        tmp_path / "receipts", context, profiles, registry, tmp_path, target_group="java"
    )
    other = replace(context, revision="b" * 40)
    amd64, _ = native(registry, "occupied-cpp-amd64")
    arm64, _ = native(registry, "occupied-cpp-arm64")
    registry.add(
        release.index_body(other, "cpp20", {"amd64": amd64.descriptor, "arm64": arm64.descriptor}),
        release.version_tag(profiles["cpp20"], context.version),
    )
    with pytest.raises(ReleaseError, match="occupied by another revision"):
        release.promote_release(
            context,
            profiles,
            registry,
            natives=inputs,
            output=tmp_path / "denied.json",
            target_group="java",
            root=tmp_path,
        )
    assert registry.puts == []


def test_targeted_promotion_requires_only_selected_but_both_native_receipts(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    profiles = add_unselected_group(tmp_path)
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    complete_receipts(folder, registry, context, profiles)
    (folder / "java-arm64/release-receipt.json").unlink()
    with pytest.raises(ReleaseError, match="selected native qualification group"):
        release.promotion_inputs(folder, context, profiles, registry, tmp_path, target_group="java")


def test_core_only_targeted_publication_needs_no_worker_receipts(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    folder.mkdir()
    for architecture in release.ARCHITECTURES:
        seed = receipt(registry, context, profiles, architecture, "python-core")
        child = folder / f"seed-{architecture}"
        child.mkdir()
        (child / "release-receipt.json").write_text(json.dumps(seed))
    inputs = release.promotion_inputs(
        folder, context, profiles, registry, tmp_path, target_group="python-core"
    )
    assert set(inputs) == {"app", "python-core"}
    release.promote_release(
        context,
        profiles,
        registry,
        natives=inputs,
        output=tmp_path / "core-only.json",
        target_group="python-core",
        root=tmp_path,
    )
    assert registry.puts == [
        "1.0.0-worker-python-core",
        "1.0.0",
        "latest-worker-python-core",
        "latest",
    ]


def test_partial_version_failure_keeps_app_and_latest_unpublished_then_resumes_exact_digests(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    registry.fail_tag = "1.0.0-worker-java21"
    with pytest.raises(ReleaseError, match="interruption"):
        release.promote_release(
            context, profiles, registry, natives=natives, output=tmp_path / "partial.json"
        )
    assert "1.0.0" not in registry.tags and not any(
        tag.startswith("latest") for tag in registry.tags
    )
    with pytest.raises(ReleaseError, match="original failed promotion"):
        release.gate_release(context, profiles, registry)
    registry.fail_tag = None
    before = len(registry.puts)
    release.promote_release(
        replace(context, run_attempt="2"),
        profiles,
        registry,
        natives=natives,
        output=tmp_path / "recovered.json",
    )
    assert "1.0.0-worker-python-core" not in registry.puts[before:]
    assert registry.puts[-1] == "latest"


def test_conflicting_version_descriptors_fail_before_any_canonical_write(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    other, _ = native(registry, "different-worker")
    changed = {**natives["java21"], "amd64": other.descriptor}
    registry.add(release.index_body(context, "java21", changed), "1.0.0-worker-java21")
    with pytest.raises(ReleaseError, match="Immutable version descriptors"):
        release.promote_release(
            context, profiles, registry, natives=natives, output=tmp_path / "denied.json"
        )
    assert registry.puts == []


def test_an_older_rerun_never_moves_latest_backward(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    newer = replace(context, version="1.1.0", revision="b" * 40)
    for key, profile in profiles.items():
        registry.add(release.index_body(newer, key, natives[key]), release.latest_tag(profile))
    old_latest = dict(registry.tags)
    report = release.promote_release(
        context, profiles, registry, natives=natives, output=tmp_path / "old.json"
    )
    assert report["latest_skipped_newer_release"] is True and report["latest_tags"] == []
    assert all(registry.tags[tag] == digest for tag, digest in old_latest.items())
    assert release.gate_release(context, profiles, registry)["mode"] == "noop"


def test_same_revision_complete_versions_can_finish_missing_aliases(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    for key, profile in profiles.items():
        registry.add(
            release.index_body(context, key, natives[key]),
            release.version_tag(profile, context.version),
        )
    assert release.gate_release(context, profiles, registry)["mode"] == "promote-existing"
    release.promote_release(
        context, profiles, registry, natives=None, output=tmp_path / "aliases.json"
    )
    assert registry.puts == ["latest-worker-python-core", "latest-worker-java21", "latest"]


def test_latest_unique_same_run_worker_receipts_reuse_exact_selected_seeds(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    expected = complete_receipts(folder, registry, context, profiles)
    current = replace(context, run_attempt="3")
    old = json.loads((folder / "java-amd64/release-receipt.json").read_text())
    newer = receipt(
        registry,
        replace(context, run_attempt="2"),
        profiles,
        "amd64",
        "java",
        seed_digests=old["seed_native_digests"],
        content="retry",
    )
    (folder / "java-retry.json").write_text(json.dumps(newer))
    actual = release.promotion_inputs(folder, current, profiles, registry, tmp_path)
    assert actual["python-core"] == expected["python-core"]
    assert actual["java21"]["amd64"].digest == newer["images"][0]["native"]["digest"]
    assert actual["java21"]["arm64"] == expected["java21"]["arm64"]


def test_old_workers_cannot_be_combined_with_rebuilt_seed_digests(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    complete_receipts(folder, registry, context, profiles)
    newer = receipt(
        registry,
        replace(context, run_attempt="2"),
        profiles,
        "amd64",
        "python-core",
        content="rebuilt",
    )
    (folder / "seed-new.json").write_text(json.dumps(newer))
    with pytest.raises(ReleaseError, match="different seeds"):
        release.promotion_inputs(
            folder, replace(context, run_attempt="2"), profiles, registry, tmp_path
        )
    assert registry.puts == []


@pytest.mark.parametrize(
    "change", [{"run_id": "99999"}, {"revision": "b" * 40}, {"run_attempt": "4"}]
)
def test_receipts_cannot_cross_runs_revisions_or_future_attempts(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    change: dict[str, str],
) -> None:
    registry = FakeRegistry()
    value = receipt(registry, context, profiles, "amd64", "python-core")
    value["context"].update(change)
    with pytest.raises(ReleaseError):
        release.staged_receipt(value, replace(context, run_attempt="3"), profiles, root=tmp_path)


def test_duplicate_attempt_artifacts_are_ambiguous_even_if_bytes_match(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    folder = tmp_path / "receipts"
    complete_receipts(folder, registry, context, profiles)
    original = folder / "java-amd64/release-receipt.json"
    (folder / "duplicate.json").write_bytes(original.read_bytes())
    with pytest.raises(ReleaseError, match="Ambiguous duplicate"):
        release.promotion_inputs(folder, context, profiles, registry, tmp_path)


def test_receipt_artifacts_never_accept_image_archives_or_links(tmp_path: Path) -> None:
    folder = tmp_path / "receipts"
    folder.mkdir()
    (folder / "image.tar").write_bytes(b"not a receipt")
    with pytest.raises(ReleaseError, match="small JSON"):
        release.receipt_files(folder)
    (folder / "image.tar").unlink()
    (folder / "linked.json").symlink_to(tmp_path / "private.json")
    with pytest.raises(ReleaseError, match="links"):
        release.receipt_files(folder)


class FakeDocker(release.Docker):
    def __init__(self, registry: FakeRegistry) -> None:
        self.registry = registry
        self.images: dict[str, dict[str, Any]] = {}
        self.by_id: dict[str, Manifest] = {}
        self.tagged: dict[str, str] = {}
        self.operations: list[tuple[str, ...]] = []
        self.pulled: dict[str, dict[str, Any]] = {}

    def native(self, architecture: str) -> None:
        assert architecture in release.ARCHITECTURES
        self.operations.append(("native", architecture))

    def inspect(self, reference: str) -> dict[str, Any]:
        self.operations.append(("inspect", reference))
        return copy.deepcopy(self.images[reference])

    def tag(self, identity: str, target: str) -> None:
        self.operations.append(("tag", identity, target))
        self.tagged[target] = identity

    def push(self, target: str) -> None:
        self.operations.append(("push", target))
        image = self.by_id[self.tagged[target]]
        self.registry.tags[target.split(":", 1)[1]] = image.descriptor.digest

    def pull(self, repository: str, digest: str, architecture: str) -> dict[str, Any]:
        self.operations.append(("pull", repository, digest, architecture))
        return copy.deepcopy(self.pulled[digest])


def local_images(
    registry: FakeRegistry,
    context: release.Context,
    profiles: dict[str, release.Profile],
    arch: str,
) -> FakeDocker:
    docker = FakeDocker(registry)
    for key, profile in profiles.items():
        image, _ = native(registry, key + arch)
        root = root_index(registry, image, arch)
        docker.images[profile.local_repository + ":" + context.version] = {
            "Id": root.descriptor.digest,
            "Os": "linux",
            "Architecture": arch,
            "Descriptor": root.descriptor.record(),
            "Config": {"Labels": {release.RELEASE_VERSION: context.version}},
        }
        docker.by_id[root.descriptor.digest] = root
    return docker


def test_stage_rejects_changed_tested_images_before_any_candidate_tag_or_push(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    docker = local_images(registry, context, profiles, "amd64")
    snapshot = release.inspect_images(
        context, profiles, ["app", "python-core"], "amd64", docker, root=tmp_path
    )
    docker.images[profiles["python-core"].local_repository + ":" + context.version]["Id"] = (
        "sha256:" + "0" * 64
    )
    with pytest.raises(ReleaseError, match="changed after qualification"):
        release.stage_images(
            context,
            profiles,
            snapshot,
            proofs(set(release.SEEDS), "python-core"),
            registry,
            docker,
            tmp_path,
        )
    assert not [op for op in docker.operations if op[0] in {"tag", "push"}]


def test_successful_seed_stage_binds_pushed_root_native_config_and_qualification(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    docker = local_images(registry, context, profiles, "arm64")
    snapshot = release.inspect_images(
        context, profiles, ["app", "python-core"], "arm64", docker, root=tmp_path
    )
    result = release.stage_images(
        context,
        profiles,
        snapshot,
        proofs(set(release.SEEDS), "python-core"),
        registry,
        docker,
        tmp_path,
    )
    assert release.staged_receipt(result, context, profiles, root=tmp_path) == result
    assert all(
        image["identity_basis"] == "root" and image["config_digest"] for image in result["images"]
    )
    assert [op[1] for op in docker.operations if op[0] == "tag"] == [
        image["tested_image_id"] for image in snapshot["images"]
    ]
    assert not any(tag in registry.tags for tag in ("1.0.0", "latest"))


def test_seed_import_reuses_earlier_attempt_by_native_digest_and_pins_restored_tags(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    seed = receipt(registry, context, profiles, "arm64", "python-core")
    docker = FakeDocker(registry)
    for image in seed["images"]:
        native_image = release.native_descriptor(image["native"], "arm64")
        docker.pulled[native_image.digest] = {
            "Id": image["config_digest"],
            "Os": "linux",
            "Architecture": "arm64",
            "Config": {"Labels": {release.RELEASE_VERSION: context.version}},
        }
    release.import_seed(
        replace(context, run_attempt="2"), profiles, seed, "arm64", registry, docker, tmp_path
    )
    pulls = [op for op in docker.operations if op[0] == "pull"]
    assert {op[2] for op in pulls} == {image["native"]["digest"] for image in seed["images"]}
    tags = [op for op in docker.operations if op[0] == "tag"]
    assert {op[1] for op in tags} == {image["config_digest"] for image in seed["images"]}
    assert all(op[2].startswith("ds60sqlpy-") for op in tags)
    assert not registry.gets and not registry.puts


def test_worker_inspection_requires_the_selected_native_seed_receipt(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    docker = local_images(registry, context, profiles, "amd64")
    with pytest.raises(ReleaseError, match="seed-receipt"):
        release.inspect_images(context, profiles, ["java21"], "amd64", docker, root=tmp_path)


def qualification_files(
    tmp_path: Path, context: release.Context, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    from scripts.check_module_references import ReferenceCase

    folder = tmp_path / "courses/example"
    folder.mkdir(parents=True)
    cases = {}
    rows = []
    for number in (1, 2):
        source = f"class Main {{ int value = {number}; }}\n"
        relative = f"courses/example/case-{number}.java"
        (tmp_path / relative).write_text(source)
        case = ReferenceCase(
            f"example-{number:03}", "example", "java21", "java", "practice", None, relative, source
        )
        cases[case.lesson_id] = case
        rows.append(
            {
                **case.metadata(),
                "status": "passed",
                "worker_status": "succeeded",
                "returncode": 0,
                "truncated": False,
                "job_id": str(number) * 32,
            }
        )
    monkeypatch.setattr(release, "expected_references", lambda root, required: cases)
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "passed": True,
                "complete": True,
                "profiles": ["java21"],
                "selected_cases": 2,
                "results": rows,
            }
        )
    )
    summary = tmp_path / "ci.json"
    summary.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "passed": True,
                "complete": True,
                "profiles": ["java21"],
                "group": "java",
                "architecture": "amd64",
                "version": context.version,
                "revision": context.revision,
                "run_id": context.run_id,
                "run_attempt": context.run_attempt,
                "checks": [
                    {"name": name, "passed": True}
                    for name in sorted(release.mandatory_ci_checks("java"))
                ],
            }
        )
    )
    return corpus, summary


def test_shortened_self_consistent_corpus_cannot_claim_complete_qualification(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus, summary = qualification_files(tmp_path, context, monkeypatch)
    assert (
        len(
            release.qualification_records([corpus, summary], context, "amd64", {"java21"}, tmp_path)
        )
        == 2
    )
    value = json.loads(corpus.read_text())
    value["results"].pop()
    value["selected_cases"] = 1
    corpus.write_text(json.dumps(value))
    with pytest.raises(ReleaseError, match="omitted admitted"):
        release.qualification_records([corpus, summary], context, "amd64", {"java21"}, tmp_path)


@pytest.mark.parametrize("change", ["source", "mandatory-check", "context", "failed", "duplicate"])
def test_qualification_rejects_changed_source_incomplete_checks_and_wrong_context(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
    change: str,
) -> None:
    corpus, summary = qualification_files(tmp_path, context, monkeypatch)
    if change == "source":
        (tmp_path / "courses/example/case-1.java").write_text("changed source")
    else:
        path = corpus if change in {"failed", "duplicate"} else summary
        value = json.loads(path.read_text())
        if change == "mandatory-check":
            value["checks"].pop()
        elif change == "context":
            value["run_id"] = "98765"
        elif change == "failed":
            value["results"][0]["worker_status"] = "failed"
        else:
            value["results"][1] = value["results"][0]
        path.write_text(json.dumps(value))
    with pytest.raises(ReleaseError):
        release.qualification_records([corpus, summary], context, "amd64", {"java21"}, tmp_path)


def github_environment(
    tmp_path: Path, context: release.Context, monkeypatch: pytest.MonkeyPatch
) -> Path:
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.0"\n')
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps(
            {
                "ref": "refs/heads/main",
                "deleted": False,
                "head_commit": {"id": context.revision, "message": "Release [publish-docker]"},
                "repository": {"full_name": context.source_repository},
            }
        )
    )
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REPOSITORY": context.source_repository,
        "GITHUB_SHA": context.revision,
        "GITHUB_RUN_ID": context.run_id,
        "GITHUB_RUN_ATTEMPT": context.run_attempt,
        "GITHUB_EVENT_PATH": str(event),
    }.items():
        monkeypatch.setenv(key, value)

    def git(root: Path, args: list[str]) -> str:
        if args[:1] == ["status"]:
            return ""
        if args[:1] == ["log"]:
            return "Release [publish-docker]"
        return context.revision

    monkeypatch.setattr(release, "git_output", git)
    return event


@pytest.mark.parametrize(
    "change",
    ["pull-request", "branch", "head-message", "mixed-marker", "head-id", "deleted", "dirty"],
)
def test_gate_requires_the_actual_main_push_head_marker_before_auth(
    tmp_path: Path, context: release.Context, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    event = github_environment(tmp_path, context, monkeypatch)
    if change == "pull-request":
        monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    elif change == "branch":
        monkeypatch.setenv("GITHUB_REF", "refs/heads/feature")
    elif change == "dirty":
        monkeypatch.setattr(
            release,
            "git_output",
            lambda root, args: (
                "changed"
                if args[:1] == ["status"]
                else context.revision
                if args[:1] == ["rev-parse"]
                else "[publish-docker]"
            ),
        )
    else:
        value = json.loads(event.read_text())
        if change == "head-message":
            value["head_commit"]["message"] = "ordinary change"
            value["commits"] = [{"message": "old [publish-docker]"}]
        elif change == "mixed-marker":
            value["head_commit"]["message"] = "Release [publish-docker] [publish-js]"
        elif change == "head-id":
            value["head_commit"]["id"] = "b" * 40
        else:
            value["deleted"] = True
        event.write_text(json.dumps(value))
    with pytest.raises(ReleaseError):
        release.github_context(tmp_path, context.namespace)


def test_earlier_same_run_gate_returns_current_context_for_fresh_job_receipts(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = replace(context, run_attempt="2")
    github_environment(tmp_path, current, monkeypatch)
    gate = release.gate_release(context, profiles, FakeRegistry())
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(gate))
    loaded, found, mode = release.load_gate(path, tmp_path)
    assert loaded == current and found == profiles and mode == "build"


def test_targeted_gate_revalidates_group_and_selected_profiles(
    tmp_path: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = replace(context, run_attempt="2")
    event = github_environment(tmp_path, current, monkeypatch)
    payload = json.loads(event.read_text())
    payload["head_commit"]["message"] = "Release [publish-java]"
    event.write_text(json.dumps(payload))
    monkeypatch.setattr(
        release,
        "git_output",
        lambda root, args: (
            ""
            if args[:1] == ["status"]
            else "Release [publish-java]"
            if args[:1] == ["log"]
            else current.revision
        ),
    )
    gate = release.gate_release(
        context, profiles, FakeRegistry(), target_group="java", root=tmp_path
    )
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(gate))
    loaded, found, mode = release.load_gate(path, tmp_path)
    assert loaded == current and found == profiles and mode == "build"
    gate["selection"]["profiles"].remove("python-core")
    path.write_text(json.dumps(gate))
    with pytest.raises(ReleaseError, match="Invalid targeted release group"):
        release.load_gate(path, tmp_path)


def test_docker_layer_transfers_do_not_buffer_or_limit_progress_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess

    calls = []

    def run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append(args)
        assert kwargs["stdout"] == subprocess.DEVNULL and kwargs["stderr"] == subprocess.DEVNULL
        assert "capture_output" not in kwargs
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(subprocess, "run", run)
    release.Docker().push("exampleuser/ds60sqlpy:ci-example")
    assert calls == [["docker", "image", "push", "--quiet", "exampleuser/ds60sqlpy:ci-example"]]


def test_existing_release_with_missing_native_content_cannot_noop(
    tmp_path: Path, context: release.Context, profiles: dict[str, release.Profile]
) -> None:
    registry = FakeRegistry()
    natives = complete_receipts(tmp_path / "receipts", registry, context, profiles)
    for key, profile in profiles.items():
        body = release.index_body(context, key, natives[key])
        registry.add(body, release.version_tag(profile, context.version))
        registry.add(body, release.latest_tag(profile))
    del registry.objects[natives["java21"]["arm64"].digest]
    with pytest.raises(ReleaseError, match="missing native"):
        release.gate_release(context, profiles, registry)
    assert not registry.puts


@pytest.mark.parametrize(
    "system,machine,engine",
    [
        ("Darwin", "arm64", "linux arm64"),
        ("Linux", "x86_64", "linux arm64"),
        ("Linux", "aarch64", "windows arm64"),
    ],
)
def test_native_qualification_never_accepts_host_or_engine_emulation_mismatch(
    monkeypatch: pytest.MonkeyPatch, system: str, machine: str, engine: str
) -> None:
    monkeypatch.setattr(platform, "system", lambda: system)
    monkeypatch.setattr(platform, "machine", lambda: machine)
    monkeypatch.setattr(release.Docker, "output", lambda self, args, **kwargs: engine)
    with pytest.raises(ReleaseError):
        release.Docker().native("arm64")


def test_opaque_registry_secret_is_never_printed_for_invalid_cli(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DOCKERHUB_TOKEN", "synthetic-secret-never-print")
    assert release.main(["gate", "--token", "synthetic-secret-never-print"]) == 2
    captured = capsys.readouterr()
    assert "synthetic-secret-never-print" not in captured.out + captured.err


def test_metadata_output_is_bounded_while_reading_and_its_process_is_reaped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess
    import sys

    original = subprocess.Popen
    children: list[subprocess.Popen[bytes]] = []

    def launch(args: list[str], **kwargs: Any) -> subprocess.Popen[bytes]:
        assert args == ["docker", "info"]
        child = original(
            [
                sys.executable,
                "-c",
                "import sys,time; sys.stdout.buffer.write(b'x'*(9*1024*1024)); "
                "sys.stdout.flush(); time.sleep(30)",
            ],
            **kwargs,
        )
        children.append(child)
        return child

    monkeypatch.setattr(subprocess, "Popen", launch)
    with pytest.raises(ReleaseError, match="exceeds limits"):
        release.Docker().output(["info"], timeout=5)
    assert len(children) == 1 and children[0].poll() is not None
