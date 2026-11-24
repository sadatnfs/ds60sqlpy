"""Spark jar overrides: manifest validation, pinned downloads and shaded-library relocation."""

from __future__ import annotations

import hashlib
import io
import json
import struct
import sys
import zipfile
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "docker/workers"), str(ROOT / "docker/workers/spark")]

import apply_jar_overrides as overrides  # noqa: E402
import jar_reshade  # noqa: E402
from jar_reshade import Relocation, Relocator, ReshadeError, Source, reshade  # noqa: E402

SHA = "a" * 64


def class_bytes(*strings: str) -> bytes:
    """Return a minimal class file whose constant pool holds the strings and a long."""
    pool = b"".join(b"\x01" + struct.pack(">H", len(s)) + s.encode() for s in strings)
    pool += b"\x05" + struct.pack(">q", 7)
    count = len(strings) + 3
    return b"\xca\xfe\xba\xbe\x00\x00\x00\x3d" + struct.pack(">H", count) + pool + b"\x00\x21"


def utf8_constants(data: bytes) -> list[str]:
    count = struct.unpack_from(">H", data, 8)[0]
    offset, index, values = 10, 1, []
    while index < count:
        tag = data[offset]
        if tag == 1:
            length = struct.unpack_from(">H", data, offset + 1)[0]
            values.append(data[offset + 3 : offset + 3 + length].decode())
            offset += 3 + length
            index += 1
        else:
            offset += 1 + jar_reshade.FIXED_WIDTH[tag]
            index += 2 if tag in jar_reshade.WIDE else 1
    return values


def jar(entries: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return output.getvalue()


def read(data: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def pom(group: str, artifact: str, version: str) -> dict[str, bytes]:
    base = f"META-INF/maven/{group}/{artifact}/"
    return {
        base
        + "pom.properties": f"groupId={group}\nartifactId={artifact}\nversion={version}\n".encode(),
        base + "pom.xml": f"<version>{version}</version>".encode(),
    }


SHADE = Relocator([Relocation("com/google", "org/sparkproject/guava")])


def shaded_host() -> bytes:
    return jar(
        {
            "org/apache/spark/ui/static/": b"",
            "org/sparkproject/guava/": b"",
            "org/apache/spark/Uses.class": class_bytes("org/sparkproject/guava/common/Old"),
            "org/sparkproject/guava/common/Old.class": class_bytes("old"),
            "META-INF/services/java.nio.file.spi.FileSystemProvider": (
                b"org.sparkproject.guava.common.OldProvider\norg.apache.spark.Kept\n"
            ),
            **pom("com.google.guava", "guava", "33.4.0-jre"),
            **pom("org.apache.spark", "spark-network-common_2.13", "4.3.0"),
        }
    )


def fixed_guava() -> bytes:
    return jar(
        {
            "com/google/common/New.class": class_bytes(
                "com/google/common/New", "Lcom/google/common/Base;", "java/lang/Object"
            ),
            "com/google/common/messages.txt": b"see com.google.common.New",
            "META-INF/services/java.nio.file.spi.FileSystemProvider": (
                b"# comment\ncom.google.common.NewProvider\n"
            ),
            "META-INF/versions/9/module-info.class": class_bytes("module"),
            **pom("com.google.guava", "guava", "33.8.0-jre"),
        }
    )


def test_relocator_rewrites_class_constants_paths_and_dotted_names() -> None:
    relocator = Relocator(
        [Relocation("com/google", "org/sparkproject/guava")], excludes=["com/google/errorprone"]
    )
    moved = relocator.class_file(class_bytes("com/google/common/A", "[Lcom/google/common/B;"))
    assert utf8_constants(moved) == [
        "org/sparkproject/guava/common/A",
        "[Lorg/sparkproject/guava/common/B;",
    ]
    assert relocator.text("com.google.common.A") == "org.sparkproject.guava.common.A"
    assert relocator.text("xcom/google/common/A") == "xcom/google/common/A"
    assert relocator.text("com/google/errorprone/X") == "com/google/errorprone/X"
    assert relocator.path("META-INF/versions/11/com/google/A.class") == (
        "META-INF/versions/11/org/sparkproject/guava/A.class"
    )
    assert relocator.path("META-INF/services/com.google.Spi") == (
        "META-INF/services/org.sparkproject.guava.Spi"
    )
    with pytest.raises(ReshadeError, match="slashed package"):
        Relocation("com.google", "x")
    with pytest.raises(ReshadeError, match="Not a Java class file"):
        relocator.class_file(b"nope")


def test_reshade_replaces_namespace_metadata_and_service_providers() -> None:
    output, report = reshade(
        shaded_host(),
        ["org/sparkproject/guava/"],
        ["com.google.guava/guava"],
        [Source(fixed_guava(), SHADE)],
    )
    entries = read(output)
    assert "org/sparkproject/guava/common/Old.class" not in entries
    assert utf8_constants(entries["org/sparkproject/guava/common/New.class"])[:2] == [
        "org/sparkproject/guava/common/New",
        "Lorg/sparkproject/guava/common/Base;",
    ]
    assert entries["org/sparkproject/guava/common/messages.txt"] == (
        b"see org.sparkproject.guava.common.New"
    )
    assert b"version=33.8.0-jre" in entries["META-INF/maven/com.google.guava/guava/pom.properties"]
    assert (
        b"version=4.3.0"
        in entries["META-INF/maven/org.apache.spark/spark-network-common_2.13/pom.properties"]
    )
    assert entries["META-INF/services/java.nio.file.spi.FileSystemProvider"] == (
        b"org.apache.spark.Kept\norg.sparkproject.guava.common.NewProvider\n"
    )
    assert (
        entries["org/apache/spark/Uses.class"] == read(shaded_host())["org/apache/spark/Uses.class"]
    )
    assert not any("module-info" in name for name in entries)
    # Directory entries survive and are synthesized, so getResource can find folders.
    assert {"org/apache/spark/ui/static/", "org/sparkproject/guava/common/"} <= set(entries)
    assert report[0] == "removed 3 entries and 1 service providers"
    assert report[1].startswith("added com.google.guava/guava (")


def test_reshade_without_sources_removes_namespace_and_metadata() -> None:
    output, _ = reshade(shaded_host(), ["org/sparkproject/guava/"], ["com.google.guava/guava"], [])
    entries = read(output)
    assert not any(name.startswith("org/sparkproject/guava/") for name in entries)
    assert "org/apache/spark/ui/static/" in entries
    assert not any(name.startswith("META-INF/maven/com.google.guava/") for name in entries)
    assert entries["META-INF/services/java.nio.file.spi.FileSystemProvider"] == (
        b"org.apache.spark.Kept\n"
    )


@pytest.mark.parametrize(
    ("namespaces", "metadata", "sources", "message"),
    [
        ([], [], [], "At least one namespace"),
        (["org/missing/"], [], [], "Namespace matches nothing"),
        (["org/sparkproject/guava/"], ["com.example/absent"], [], "Missing Maven metadata"),
        (
            ["org/sparkproject/guava/"],
            [],
            [Source(fixed_guava(), Relocator([Relocation("com/google", "elsewhere")]))],
            "relocates outside the namespaces",
        ),
        (
            ["org/sparkproject/guava/"],
            [],
            [Source(fixed_guava(), SHADE), Source(fixed_guava(), SHADE)],
            "Two source jars provide",
        ),
        (
            ["org/sparkproject/guava/"],
            [],
            [Source(jar({"com/google/X.class": class_bytes("x")}), SHADE)],
            "no Maven pom.properties",
        ),
    ],
)
def test_reshade_fails_closed(
    namespaces: list[str], metadata: list[str], sources: list[Source], message: str
) -> None:
    with pytest.raises(ReshadeError, match=message):
        reshade(shaded_host(), namespaces, metadata, sources)


def test_reshade_refuses_collision_with_kept_entry() -> None:
    host = jar(
        {
            "org/sparkproject/guava/common/Old.class": class_bytes("old"),
            "META-INF/versions/9/org/sparkproject/guava/common/V.class": class_bytes("kept"),
        }
    )
    source = jar(
        {
            "META-INF/versions/9/com/google/common/V.class": class_bytes("new"),
            **pom("com.google.guava", "guava", "33.8.0-jre"),
        }
    )
    with pytest.raises(ReshadeError, match="collides with a kept entry"):
        reshade(host, ["org/sparkproject/guava/"], [], [Source(source, SHADE)])


def manifest(**changes: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema": 1,
        "spark_version": "4.3.0",
        "reshade_jars": [
            {
                "jar": "spark-network-common_2.13-4.3.0.jar",
                "relocations": [{"from": "com/google", "to": "org/sparkproject/guava"}],
                "items": [
                    {
                        "namespaces": ["org/sparkproject/guava/"],
                        "metadata": ["com.google.guava/guava"],
                        "sources": [
                            {"url": "https://example.test/g.jar", "sha256": SHA, "jar": "g"}
                        ],
                    }
                ],
            }
        ],
    }
    base["reshade_jars"][0].update(changes)
    return base


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"relocations": []}, "relocations must be a non-empty list"),
        ({"relocations": [{"from": "a"}]}, "exactly from and to"),
        ({"items": []}, "items must be a non-empty list"),
        ({"items": [{"namespaces": []}]}, "namespaces must not be empty"),
        (
            {
                "items": [
                    {
                        "namespaces": ["x/"],
                        "sources": [{"url": "http://x", "sha256": SHA, "jar": "j"}],
                    }
                ]
            },
            "must use HTTPS",
        ),
        (
            {
                "items": [
                    {
                        "namespaces": ["x/"],
                        "sources": [{"url": "https://x", "sha256": "AB", "jar": "j"}],
                    }
                ]
            },
            "64 lowercase hex",
        ),
        (
            {
                "items": [
                    {
                        "namespaces": ["x/"],
                        "sources": [{"url": "https://x", "sha256": SHA, "jar": "j", "relocate": 1}],
                    }
                ]
            },
            "relocate must be a boolean",
        ),
    ],
)
def test_validate_manifest_rejects_malformed_reshade(changes: dict[str, Any], message: str) -> None:
    with pytest.raises(SystemExit, match=message):
        overrides.validate_manifest(manifest(**changes))


def test_committed_manifest_is_valid_and_pins_the_image_spark() -> None:
    data = overrides.load_manifest(ROOT / "docker/workers/spark/jar-overrides.json")
    assert data["spark_version"] == "4.3.0"
    assert {item["jar"] for item in data["reshade_jars"]} == {
        "spark-core_2.13-4.3.0.jar",
        "spark-network-common_2.13-4.3.0.jar",
        "hadoop-client-runtime-3.5.0.jar",
    }
    dockerfile = (ROOT / "docker/workers/Dockerfile.spark").read_text()
    assert "spark:4.3.0-scala2.13-java17-python3-ubuntu@sha256:" in dockerfile
    assert json.dumps(data).count("https://repo1.maven.org/maven2/") > 0


class FakeResponse(io.BytesIO):
    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def test_download_fails_closed_on_checksum_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = b"jar bytes"
    monkeypatch.setattr(overrides, "open_download", lambda url, timeout: FakeResponse(payload))
    good = {"url": "https://x/j.jar", "sha256": hashlib.sha256(payload).hexdigest()}
    assert overrides.download(good) == payload
    with pytest.raises(SystemExit, match="SHA-256 mismatch"):
        overrides.download({"url": "https://x/j.jar", "sha256": SHA})


def test_reshade_jar_rewrites_the_jar_on_disk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "spark-network-common_2.13-4.3.0.jar"
    target.write_bytes(shaded_host())
    source = fixed_guava()
    monkeypatch.setattr(overrides, "download", lambda item: source)
    entry = manifest()["reshade_jars"][0]
    actions = overrides.reshade_jar(target, entry)
    assert actions[0].startswith("reshaded spark-network-common_2.13-4.3.0.jar: removed")
    assert "org/sparkproject/guava/common/New.class" in read(target.read_bytes())
    with pytest.raises(SystemExit, match="Reshade of .* failed: Namespace matches nothing"):
        overrides.reshade_jar(target, entry | {"items": [{"namespaces": ["org/gone/"]}]})
