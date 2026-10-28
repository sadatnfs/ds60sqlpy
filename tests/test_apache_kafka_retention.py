"""Real pure-JDK compaction invariants and side-effect-free CLI policy guards."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "courses/apache-data-platforms/projects/streaming"
HARNESS = ROOT / "tests/fixtures/apache-retention/RetentionSemanticsCheck.java"


@pytest.fixture(scope="module")
def run_semantics(
    tmp_path_factory: pytest.TempPathFactory,
) -> Callable[[Path], subprocess.CompletedProcess[str]]:
    image = os.environ.get("DS60_RETENTION_JAVA_IMAGE")
    if image:
        assert re.fullmatch(
            r"ds60(?:-apache-kafka-binary|sqlpy-worker-java21):[0-9]+\.[0-9]+\.[0-9]+", image
        )
        docker = shutil.which("docker") or str(Path.home() / ".rd/bin/docker")
        inspect = subprocess.run(
            [docker, "image", "inspect", "--format", "{{.Os}}|{{.Architecture}}", image],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        ).stdout.strip()
        engine = subprocess.run(
            [docker, "info", "--format", "{{.OSType}}|{{.Architecture}}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        ).stdout.strip()
        engine = {"linux|aarch64": "linux|arm64", "linux|x86_64": "linux|amd64"}.get(engine, engine)
        assert inspect == engine and engine in {"linux|arm64", "linux|amd64"}

        def execute(source: Path) -> subprocess.CompletedProcess[str]:
            source.chmod(0o644)
            return subprocess.run(
                [
                    docker,
                    "run",
                    "--rm",
                    "--pull=never",
                    "--network",
                    "none",
                    "--read-only",
                    "--tmpfs",
                    "/tmp:rw,nosuid,size=128m",
                    "--user",
                    "1000:1000",
                    "--memory",
                    "256m",
                    "--cpus",
                    "1",
                    "--pids-limit",
                    "128",
                    "-v",
                    str(PROJECT) + ":/project:ro",
                    "-v",
                    str(HARNESS.parent) + ":/checks:ro",
                    "-v",
                    str(source) + ":/input/source.txt:ro",
                    "--entrypoint",
                    "bash",
                    image,
                    "-c",
                    "mkdir -p /tmp/classes && "
                    "javac -proc:none -d /tmp/classes /project/RetentionSemantics.java "
                    "/checks/RetentionSemanticsCheck.java && "
                    "java -Xms16m -Xmx64m -cp /tmp/classes "
                    "RetentionSemanticsCheck /input/source.txt",
                ],
                capture_output=True,
                text=True,
                timeout=45,
            )

        return execute
    javac, java = shutil.which("javac"), shutil.which("java")
    if platform.system() == "Darwin" and not os.environ.get("JAVA_HOME"):
        pytest.skip("Use a prepared native Java image or an explicitly configured local JDK")
    if javac is None or java is None:
        pytest.skip("Optional JDK17+ or explicit prepared native image is required")
    version = subprocess.run([javac, "-version"], capture_output=True, text=True, timeout=10)
    match = re.search(r"javac (\d+)", version.stdout + version.stderr)
    if version.returncode or match is None or int(match.group(1)) < 17:
        pytest.skip("Optional JDK17+ is not available")
    output = tmp_path_factory.mktemp("retention-classes")
    subprocess.run(
        [
            javac,
            "--release",
            "17",
            "-d",
            str(output),
            str(PROJECT / "RetentionSemantics.java"),
            str(HARNESS),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )

    def execute_local(source: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [java, "-cp", str(output), "RetentionSemanticsCheck", str(source)],
            capture_output=True,
            text=True,
            timeout=20,
        )

    return execute_local


def test_real_java_validator_accepts_two_histories_and_rejects_twelve_corruptions(
    run_semantics: Callable[[Path], subprocess.CompletedProcess[str]],
) -> None:
    source = PROJECT / "retention-events.txt"
    result = run_semantics(source)
    assert result.returncode == 0, result.stdout + result.stderr
    observation = json.loads(result.stdout)
    assert observation == {
        "passed": True,
        "semantic_only": True,
        "valid_cases": 2,
        "rejected_cases": 12,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }


def test_real_java_validator_rejects_changed_source_bytes(
    tmp_path: Path, run_semantics: Callable[[Path], subprocess.CompletedProcess[str]]
) -> None:
    changed = tmp_path / "changed.txt"
    changed.write_bytes((PROJECT / "retention-events.txt").read_bytes().replace(b"v2", b"v9"))
    result = run_semantics(changed)
    assert result.returncode != 0 and "Source fixture differs" in result.stderr


def shell_function(name: str, file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            "-c",
            'source "$1"; "$2" "$3"',
            "retention-test",
            str(PROJECT / "check-kafka.sh"),
            name,
            str(file),
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )


@pytest.mark.parametrize(
    "replacement",
    [None, "retention.ms=604800000", "retention.bytes=1000000", "cleanup.policy=compact,delete"],
)
def test_effective_noncompacted_policy_is_verified_without_broker_calls(
    tmp_path: Path, replacement: str | None
) -> None:
    lines = [
        "  cleanup.policy=delete sensitive=false",
        "  retention.ms=-1 sensitive=false",
        "  retention.bytes=-1 sensitive=false",
    ]
    if replacement:
        key = replacement.split("=")[0]
        lines = [
            replacement + " sensitive=false" if line.strip().startswith(key + "=") else line
            for line in lines
        ]
    fixture = tmp_path / "policy.txt"
    fixture.write_text("All configs for topic classroom-events are:\n" + "\n".join(lines) + "\n")
    result = shell_function("verify_study_policy", fixture)
    assert (result.returncode == 0) is (replacement is None)


@pytest.mark.parametrize(
    "body,expected",
    [
        ("classroom-events:0:2\nclassroom-events:1:1\n", "2 1 3"),
        ("classroom-events:1:0\nclassroom-events:0:0\n", "0 0 0"),
        ("classroom-events:0:3\nclassroom-events:1:0\n", "3 0 3"),
        ("classroom-events:0:2\n", None),
        ("classroom-events:0:1\nclassroom-events:0:2\n", None),
        ("classroom-events:0:4\nclassroom-events:1:0\n", None),
        ("other:0:2\nclassroom-events:1:1\n", None),
    ],
)
def test_partition_positions_are_exact_and_bounded(
    tmp_path: Path, body: str, expected: str | None
) -> None:
    fixture = tmp_path / "offsets.txt"
    fixture.write_text(body)
    result = shell_function("parse_study_offsets", fixture)
    if expected is None:
        assert result.returncode != 0
    else:
        assert result.returncode == 0 and result.stdout.strip() == expected


@pytest.mark.parametrize(
    "partitions,replicas,valid", [(2, "1", True), (1, "1", False), (2, "1,2", False)]
)
def test_actual_partition_and_replica_metadata_is_required(
    tmp_path: Path, partitions: int, replicas: str, valid: bool
) -> None:
    fixture = tmp_path / "metadata.txt"
    fixture.write_text(
        f"Topic: classroom-events PartitionCount: {partitions} ReplicationFactor: 1\n"
        + "\n".join(
            f"Topic: classroom-events Partition: {i} Leader: 1 Replicas: {replicas} Isr: 1"
            for i in range(partitions)
        )
        + "\n"
    )
    result = shell_function("verify_study_topology", fixture)
    assert (result.returncode == 0) is valid
