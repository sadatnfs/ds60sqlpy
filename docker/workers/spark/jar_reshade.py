"""Replace or remove libraries shaded inside an upstream jar, relocating the new classes.

Spark and Hadoop bundle third-party libraries inside their own jars under relocated
package prefixes (for example ``org/sparkproject/jetty``). A security fix for such a
library therefore needs the fixed upstream jar relocated into the same prefix. This
module does that relocation in pure Python by rewriting the class-file constant pool:
every UTF-8 constant (class names, descriptors, signatures, and string literals) has
the configured package prefixes rewritten in slashed and dotted form, which matches
what the Maven shade plugin produces. Resource paths, ``META-INF/services`` names and
contents, and ``META-INF/versions/N/`` multi-release paths are relocated the same way.

The library's Maven metadata (``META-INF/maven/<group>/<artifact>/``) is replaced with
the fixed jar's own ``pom.properties`` and ``pom.xml`` so scanners see the true version.
"""

from __future__ import annotations

import io
import re
import struct
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

CLASS_MAGIC = b"\xca\xfe\xba\xbe"
VERSIONED = re.compile(r"^(META-INF/versions/\d+/)(.*)$")
SERVICES = "META-INF/services/"
MAVEN = "META-INF/maven/"
# Constant pool tags and the fixed byte width of each non-UTF-8 entry.
CONSTANT_UTF8 = 1
FIXED_WIDTH = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2}
FIXED_WIDTH.update({17: 4, 18: 4, 19: 2, 20: 2})
# A prefix matches at the start of a name or after the "L" of a descriptor element
# (for example "(JLorg/..."), never inside another identifier or path such as
# "__org." or "java/io/". A leading "/" (a classpath resource name) also matches.
BOUNDARY = r"(?:(?<![A-Za-z0-9_$/.])|(?<=^/)|(?<=L))"
WIDE = {5, 6}


class ReshadeError(Exception):
    """A shaded-library replacement could not be applied exactly as configured."""


@dataclass(frozen=True)
class Relocation:
    source: str
    target: str

    def __post_init__(self) -> None:
        for value in (self.source, self.target):
            if not re.fullmatch(r"[A-Za-z0-9_$]+(/[A-Za-z0-9_$]+)*", value):
                raise ReshadeError(f"Relocation prefix must be a slashed package: {value!r}")


class Relocator:
    """Rewrite package prefixes in class files, resource paths, and service files."""

    def __init__(self, relocations: Sequence[Relocation], excludes: Sequence[str] = ()) -> None:
        self.mapping: dict[str, str] = {}
        # An excluded package maps to itself; the longest prefix wins, so it shields
        # names that a broader relocation (for example ``org``) would otherwise move.
        pairs = list(relocations) + [Relocation(item, item) for item in excludes]
        for item in pairs:
            for separator in ("/", "."):
                self.mapping[item.source.replace("/", separator) + separator] = (
                    item.target.replace("/", separator) + separator
                )
        ordered = sorted(self.mapping, key=len, reverse=True)
        # With no relocations the pattern can never match, so content is copied as is.
        alternatives = "|".join(re.escape(key) for key in ordered) or r"(?!)"
        self.pattern = re.compile(f"{BOUNDARY}(?:{alternatives})")
        self.byte_pattern = re.compile(self.pattern.pattern.encode())
        self.byte_mapping = {k.encode(): v.encode() for k, v in self.mapping.items()}

    def text(self, value: str) -> str:
        return self.pattern.sub(lambda match: self.mapping[match.group(0)], value)

    def raw(self, value: bytes) -> bytes:
        # ASCII prefixes never occur inside multi-byte modified UTF-8 sequences.
        return self.byte_pattern.sub(lambda match: self.byte_mapping[match.group(0)], value)

    def relocates(self, value: str) -> bool:
        return self.text(value) != value

    def path(self, name: str) -> str:
        versioned = VERSIONED.match(name)
        if versioned:
            return versioned.group(1) + self.text(versioned.group(2))
        return (
            SERVICES + self.text(name[len(SERVICES) :])
            if name.startswith(SERVICES)
            else self.text(name)
        )

    def class_file(self, data: bytes) -> bytes:
        if data[:4] != CLASS_MAGIC:
            raise ReshadeError("Not a Java class file")
        count = struct.unpack_from(">H", data, 8)[0]
        out = bytearray(data[:10])
        offset, index = 10, 1
        while index < count:
            tag = data[offset]
            if tag == CONSTANT_UTF8:
                length = struct.unpack_from(">H", data, offset + 1)[0]
                value = self.raw(data[offset + 3 : offset + 3 + length])
                if len(value) > 0xFFFF:
                    raise ReshadeError("Relocated constant exceeds the class-file limit")
                out += bytes([tag]) + struct.pack(">H", len(value)) + value
                offset += 3 + length
                index += 1
                continue
            width = FIXED_WIDTH.get(tag)
            if width is None:
                raise ReshadeError(f"Unknown constant pool tag {tag}")
            out += data[offset : offset + 1 + width]
            offset += 1 + width
            index += 2 if tag in WIDE else 1
        out += data[offset:]
        return bytes(out)


def _maven_id(name: str) -> str | None:
    parts = name.split("/")
    if len(parts) == 5 and name.startswith(MAVEN) and parts[4] == "pom.properties":
        return f"{parts[2]}/{parts[3]}"
    return None


def _within(name: str, namespaces: Sequence[str]) -> bool:
    logical = VERSIONED.sub(r"\2", name)
    return any(name.startswith(prefix) or logical.startswith(prefix) for prefix in namespaces)


def _is_text(data: bytes) -> bool:
    if b"\0" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _provider_lines(data: bytes) -> list[bytes]:
    lines = []
    for line in data.splitlines():
        entry = line.split(b"#", 1)[0].strip()
        if entry:
            lines.append(entry)
    return lines


@dataclass(frozen=True)
class Source:
    """One fixed upstream jar and the relocator that moves it into the shaded jar."""

    data: bytes
    relocator: Relocator


@dataclass
class SourceEntries:
    entries: dict[str, bytes]
    services: dict[str, list[bytes]]
    maven: dict[str, bytes]
    identifiers: list[str]
    skipped: int


def relocated_entries(source: Source, namespaces: Sequence[str]) -> SourceEntries:
    """Return one fixed jar's relocated entries, service providers, and Maven metadata.

    Only entries that land inside ``namespaces`` are taken. A class that would land
    elsewhere stops the build, since dropping it silently could break the library.
    Text resources inside the namespaces have package names relocated like services.
    """
    relocator = source.relocator
    result = SourceEntries({}, {}, {}, [], 0)
    with zipfile.ZipFile(io.BytesIO(source.data)) as archive:
        for info in archive.infolist():
            name = info.filename
            if info.is_dir():
                continue
            data = archive.read(info)
            if name.startswith(MAVEN):
                identifier = _maven_id(name)
                if identifier:
                    result.identifiers.append(identifier)
                if name.endswith(("/pom.properties", "/pom.xml")):
                    result.maven[name] = data
                continue
            if VERSIONED.sub(r"\2", name).endswith("module-info.class"):
                continue
            target = relocator.path(name)
            if name.startswith(SERVICES):
                lines = _provider_lines(relocator.raw(data))
                if any(_within(_class_path(line), namespaces) for line in lines):
                    result.services[target] = lines
                else:
                    result.skipped += 1
                continue
            if not _within(target, namespaces):
                if name.endswith(".class"):
                    raise ReshadeError(f"Class {name} relocates outside the namespaces: {target}")
                result.skipped += 1
                continue
            if name.endswith(".class"):
                data = relocator.class_file(data)
            elif _is_text(data):
                data = relocator.raw(data)
            result.entries[target] = data
    if not result.identifiers:
        raise ReshadeError("The source jar carries no Maven pom.properties")
    result.identifiers.sort()
    return result


def _class_path(provider: bytes) -> str:
    return provider.decode("utf-8").replace(".", "/") + ".class"


def reshade(
    jar: bytes,
    namespaces: Sequence[str],
    metadata: Iterable[str],
    sources: Iterable[Source],
) -> tuple[bytes, list[str]]:
    """Return ``jar`` with the shaded ``namespaces`` replaced by relocated ``sources``.

    ``metadata`` names the ``group/artifact`` Maven directories of the libraries being
    replaced or removed; the sources supply their own metadata in its place. With no
    sources the namespaces are simply removed. Service provider files lose the lines
    that name removed classes and gain the sources' providers. Every namespace and
    metadata directory must match something, so a manifest written for a different
    upstream jar fails instead of silently doing nothing.
    """
    if not namespaces:
        raise ReshadeError("At least one namespace is required")
    with zipfile.ZipFile(io.BytesIO(jar)) as archive:
        infos = archive.infolist()
        original = {info.filename: archive.read(info) for info in infos}
    removed_metadata = [f"{MAVEN}{item}/" for item in metadata]
    for prefix in removed_metadata:
        if not any(name.startswith(prefix) for name in original):
            raise ReshadeError(f"Missing Maven metadata to replace: {prefix}")
    doomed = list(namespaces) + removed_metadata
    kept: dict[str, bytes] = {}
    services: dict[str, list[bytes]] = {}
    dropped_providers = 0
    for name, data in original.items():
        if any(name.startswith(prefix) for prefix in doomed):
            continue
        if name.startswith(SERVICES) and name != SERVICES:
            lines = _provider_lines(data)
            remaining = [line for line in lines if not _within(_class_path(line), namespaces)]
            dropped_providers += len(lines) - len(remaining)
            if remaining != lines:
                services[name] = remaining
                continue
        kept[name] = data
    removed = _files(original) - _files(kept) - len(services)
    report = [f"removed {removed} entries and {dropped_providers} service providers"]
    added: dict[str, bytes] = {}
    for source in sources:
        result = relocated_entries(source, namespaces)
        for name, data in result.entries.items():
            if name in added:
                raise ReshadeError(f"Two source jars provide {name}")
            added[name] = data
        for name, lines in result.services.items():
            current = services.get(name)
            if current is None and name in kept:
                current = _provider_lines(kept.pop(name))
            merged = list(current or [])
            merged += [line for line in lines if line not in merged]
            services[name] = merged
        notes = []
        for name, data in result.maven.items():
            existing = added.get(name, kept.get(name))
            if existing is None:
                added[name] = data
            elif existing != data and name in added:
                raise ReshadeError(f"Two source jars disagree on {name}")
            elif existing != data:
                notes.append(name.split("/")[3])
        note = f", skipped {result.skipped} unrelocated resources" if result.skipped else ""
        if notes:
            note += f", kept the existing metadata of {', '.join(sorted(set(notes)))}"
        entries = len(result.entries) + len(result.maven)
        report.append(f"added {', '.join(result.identifiers)} ({entries} entries{note})")
    for prefix in namespaces:
        if not any(name.startswith(prefix) for name in list(original) + list(added)):
            raise ReshadeError(f"Namespace matches nothing: {prefix}")
    for name in added:
        if name in kept:
            raise ReshadeError(f"Relocated entry collides with a kept entry: {name}")
    for name, lines in services.items():
        if lines:
            added[name] = b"".join(line + b"\n" for line in lines)
    # Class loaders resolve a resource directory (Spark serves its UI from
    # org/apache/spark/ui/static) only through an explicit directory entry.
    for name in list(added):
        parts = name.split("/")[:-1]
        for depth in range(1, len(parts) + 1):
            directory = "/".join(parts[:depth]) + "/"
            if directory not in kept and directory not in added:
                added[directory] = b""
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for info in infos:
            if info.filename in kept:
                archive.writestr(_entry(info.filename), kept[info.filename])
        for name in sorted(added):
            archive.writestr(_entry(name), added[name])
    return output.getvalue(), report


def _files(entries: Iterable[str]) -> int:
    return sum(not name.endswith("/") for name in entries)


def _entry(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    if name.endswith("/"):
        info.external_attr = (0o40755 << 16) | 0x10
    else:
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
    return info
