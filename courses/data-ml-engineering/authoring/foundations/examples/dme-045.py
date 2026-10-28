"""Synthetic resource authorization and actual bounded POSIX file reads inside owned fixtures."""

import json
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Principal:
    name: str
    tenant: str
    roles: frozenset[str]


RESOURCES = {
    "report-a": {"tenant": "north", "file": "a.json"},
    "report-b": {"tenant": "south", "file": "b.json"},
}


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicated JSON field is ambiguous")
        result[key] = value
    return result


def read_report(root, principal, resource_id):
    resource = RESOURCES.get(resource_id)
    if (
        resource is None
        or principal.tenant != resource["tenant"]
        or "analyst" not in principal.roles
    ):
        raise PermissionError("Resource action is not authorized")
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        descriptor = os.open(resource["file"], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            information = os.fstat(descriptor)
            if not stat.S_ISREG(information.st_mode) or information.st_size > 4096:
                raise ValueError("Expected a bounded regular report file")
            content = os.read(descriptor, 4097)
            if len(content) > 4096:
                raise ValueError("Report grew beyond its byte budget")
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)
    value = json.loads(content, object_pairs_hook=unique_fields)
    if (
        not isinstance(value, dict)
        or set(value) != {"packages"}
        or type(value["packages"]) is not int
        or value["packages"] < 0
    ):
        raise ValueError("Report content violates the reviewed numeric schema")
    return value


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "a.json").write_text('{"packages":6}')
        (root / "b.json").write_text('{"packages":9}')
        principal = Principal("synthetic-reader", "north", frozenset({"analyst"}))
        assert read_report(root, principal, "report-a") == {"packages": 6}
        denied = []
        for resource in ["report-b", "../b.json", "unlisted"]:
            try:
                read_report(root, principal, resource)
            except PermissionError:
                denied.append(resource)
            else:
                raise AssertionError("Unauthorized resource was returned")
        return {
            "own_resource": {"packages": 6},
            "denied_request_count": len(denied),
            "principal_is_a_trusted_fixture_not_user_supplied_authentication": True,
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        parent = Path(directory)
        root = parent / "reports"
        root.mkdir()
        outside = parent / "other-fixture.json"
        outside.write_text('{"packages":999}')
        (root / "a.json").symlink_to(outside)
        principal = Principal("synthetic-reader", "north", frozenset({"analyst"}))
        try:
            read_report(root, principal, "report-a")
        except OSError:
            linked = True
        else:
            raise AssertionError("A report symlink escaped the fixed file boundary")
        (root / "a.json").unlink()
        (root / "a.json").write_text('{"packages":true}')
        try:
            read_report(root, principal, "report-a")
        except ValueError:
            typed = True
        else:
            raise AssertionError("A Boolean was accepted as a package count")
        return {
            "symlink_rejected": linked,
            "boolean_count_rejected": typed,
            "outside_owned_fixture_unchanged": json.loads(outside.read_text()) == {"packages": 999},
        }


def main():
    print("Authorization precedes resource access:", example_one())
    print("File and payload validation enforce a separate boundary:", example_two())


if __name__ == "__main__":
    main()
