"""Read-only admission for exact-source wheels and explicit prepared artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import stat
import zipfile
from email.parser import BytesParser
from pathlib import PurePosixPath


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_inventory(root):
    files = [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    if any(path.is_symlink() for path in files):
        raise ValueError("Source and prepared input trees must not contain file symlinks")
    return {str(path.relative_to(root)): digest(path) for path in files}


def wheel_identity(wheel, source, import_name, version):
    if wheel.is_symlink() or not wheel.is_file() or wheel.suffix != ".whl":
        raise ValueError("Supply a regular prepared wheel file")
    if wheel.stat().st_size > 32 * 1024 * 1024:
        raise ValueError("Standalone wheel exceeds the bounded admission size")
    expected = {
        str(path.relative_to(source)): digest(path)
        for path in sorted(source.rglob("*.py"))
        if "__pycache__" not in path.parts
    }
    if any(path.is_symlink() for path in source.rglob("*.py")):
        raise ValueError("Copied Python sources must not be symlinks")
    metadata_prefix = import_name + "-" + version + ".dist-info/"
    try:
        with zipfile.ZipFile(wheel) as archive:
            seen = set()
            total = 0
            for member in archive.infolist():
                path = PurePosixPath(member.filename)
                total += member.file_size
                if (
                    member.filename in seen
                    or path.is_absolute()
                    or ".." in path.parts
                    or "\\" in member.filename
                    or stat.S_ISLNK(member.external_attr >> 16)
                    or not member.filename.startswith((import_name + "/", metadata_prefix))
                    or total > 32 * 1024 * 1024
                ):
                    raise ValueError("Unexpected or duplicate wheel member")
                seen.add(member.filename)
            metadata = BytesParser().parsebytes(archive.read(metadata_prefix + "METADATA"))
            if (
                metadata["Name"].replace("-", "_").lower() != import_name
                or metadata["Version"] != version
            ):
                raise ValueError("Wheel distribution/version differs from the copied package")
            observed = {
                name.removeprefix(import_name + "/"): hashlib.sha256(archive.read(name)).hexdigest()
                for name in archive.namelist()
                if name.startswith(import_name + "/") and name.endswith(".py")
            }
    except (zipfile.BadZipFile, KeyError, AttributeError) as error:
        raise ValueError("Malformed package wheel or distribution metadata") from error
    if not expected or expected != observed:
        raise ValueError("Prepared wheel does not exactly match this copied package source")
    return {"python_source_sha256": observed, "wheel_sha256": digest(wheel), "version": version}


def native_identity(directory, package, architecture, version):
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Supply a regular prepared native installation directory")
    manifest_path = directory / "artifact.json"
    if (
        manifest_path.is_symlink()
        or not manifest_path.is_file()
        or manifest_path.stat().st_size > 4 * 1024 * 1024
    ):
        raise ValueError("Missing or oversized native installation manifest")
    try:
        manifest = json.loads(manifest_path.read_text())
        if (
            manifest["kind"] != "spark-tmbad-artifact"
            or manifest["schema_version"] != 1
            or manifest["protocol"] != 1
            or manifest["package_version"] != version
            or manifest["platform"] != {"os": "linux", "arch": architecture}
        ):
            raise ValueError("Native installation package/platform identity mismatch")
        for key, filename in [("binary", "tmbad-worker"), ("jvm", "spark-tmbad.jar")]:
            path = directory / filename
            if (
                path.is_symlink()
                or not path.is_file()
                or manifest[key]["path"] != "/opt/spark-tmbad/" + filename
                or digest(path) != manifest[key]["sha256"]
            ):
                raise ValueError("Native installation artifact path/hash mismatch")
        native = json.loads((directory / "native-build.json").read_text())
        jvm = json.loads((directory / "jvm-build.json").read_text())
        if (
            native["native_source"] != file_inventory(package / "native")
            or native["build_scripts"] != file_inventory(package / "tooling")
            or native["build_id"] != manifest["build_id"]
            or native["binary_sha256"] != manifest["binary"]["sha256"]
            or jvm["jar_sha256"] != manifest["jvm"]["sha256"]
            or jvm["build_script_sha256"] != digest(package / "jvm/build.py")
        ):
            raise ValueError("Prepared native/JVM receipts differ from the copied source")
        selected = list((package / "jvm/src/main/scala").rglob("*.scala"))
        if jvm["include_tests"]:
            selected += list((package / "jvm/src/test/scala").rglob("*.scala"))
        if {str(path.relative_to(package / "jvm")): digest(path) for path in selected} != jvm[
            "source_sha256"
        ]:
            raise ValueError("Prepared JVM sources differ from the copied package")
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("Malformed native preparation manifest or receipt") from error
    return {
        "artifact_sha256": digest(manifest_path),
        "build_id": manifest["build_id"],
        "binary_sha256": manifest["binary"]["sha256"],
        "jvm_sha256": manifest["jvm"]["sha256"],
    }


def normalized_arch(value):
    return {"aarch64": "arm64", "arm64": "arm64", "x86_64": "amd64", "amd64": "amd64"}.get(value)


def image_identity(image, engine):
    architecture = normalized_arch(engine.get("Architecture"))
    if (
        image.get("Os") != "linux"
        or image.get("Architecture") != architecture
        or architecture is None
    ):
        raise ValueError("Image must match the Linux engine's native architecture; no emulation")
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", image.get("Id", "")):
        raise ValueError("Expected an immutable local image ID")
    if not isinstance(image.get("Config"), dict) or image["Config"].get("Volumes"):
        raise ValueError("Use a prepared image without implicit VOLUME declarations")
    return architecture


def container_identity(values, identifier, project, owner):
    if (
        len(values) != 1
        or values[0].get("Id") != identifier
        or (values[0].get("Config", {}).get("Labels") or {}).get("com.docker.compose.project")
        != project
        or (values[0].get("Config", {}).get("Labels") or {}).get("ds60.owner") != owner
    ):
        raise ValueError("Refusing to operate outside this exact owned Compose project")
    return values[0]
