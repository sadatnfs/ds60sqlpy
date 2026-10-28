"""Bounded Docker Hub Registry v2 metadata client with verified TLS and private auth.

Only manifests and bearer-token exchange are handled here. Layer transport stays
with Docker. See https://distribution.github.io/distribution/spec/api/ and the
OCI image index specification. No credential or server response body is logged.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, NoReturn

OCI_INDEX = "application/vnd.oci.image.index.v1+json"
DOCKER_INDEX = "application/vnd.docker.distribution.manifest.list.v2+json"
OCI_MANIFEST = "application/vnd.oci.image.manifest.v1+json"
DOCKER_MANIFEST = "application/vnd.docker.distribution.manifest.v2+json"
INDEX_TYPES = frozenset({OCI_INDEX, DOCKER_INDEX})
IMAGE_TYPES = frozenset({OCI_MANIFEST, DOCKER_MANIFEST})
MANIFEST_TYPES = INDEX_TYPES | IMAGE_TYPES
ACCEPT = ", ".join(sorted(MANIFEST_TYPES))
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
DIGEST = re.compile(r"sha256:[a-f0-9]{64}\Z")
NAMESPACE = re.compile(r"[a-z0-9][a-z0-9_-]{1,38}\Z")
TAG = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}\Z")


class ReleaseError(ValueError):
    """A controlled diagnostic that contains no remote body or credential."""


class RegistryTransportError(ReleaseError):
    """A request may have reached the registry, but transport lost its outcome."""


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def require_digest(value: Any) -> str:
    if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
        raise ReleaseError("Expected a SHA-256 content digest")
    return value


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReleaseError("Duplicate JSON metadata field")
        result[key] = value
    return result


def _invalid_constant(value: str) -> NoReturn:
    raise ReleaseError("JSON metadata must use finite standard values")


def json_object(data: bytes, maximum: int = MAX_MANIFEST_BYTES) -> dict[str, Any]:
    if len(data) > maximum:
        raise ReleaseError("JSON metadata exceeds its size limit")
    try:
        value = json.loads(
            data.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_invalid_constant
        )
    except (ValueError, UnicodeError, RecursionError):
        raise ReleaseError("Invalid bounded JSON metadata") from None
    if not isinstance(value, dict):
        raise ReleaseError("JSON metadata must be an object")
    return value


@dataclass(frozen=True)
class Descriptor:
    media_type: str
    digest: str
    size: int

    def record(self) -> dict[str, Any]:
        return {"mediaType": self.media_type, "digest": self.digest, "size": self.size}


@dataclass(frozen=True)
class Head:
    media_type: str
    digest: str
    size: int | None


@dataclass(frozen=True)
class Manifest:
    descriptor: Descriptor
    document: dict[str, Any]
    body: bytes


def descriptor(value: Any, *, image_only: bool = False) -> Descriptor:
    if not isinstance(value, dict):
        raise ReleaseError("Invalid manifest descriptor")
    media_type = value.get("mediaType")
    if not isinstance(media_type, str) or media_type not in (
        IMAGE_TYPES if image_only else MANIFEST_TYPES
    ):
        raise ReleaseError("Unsupported manifest media type")
    digest = require_digest(value.get("digest"))
    size = value.get("size")
    if type(size) is not int or not 1 <= size <= MAX_MANIFEST_BYTES:
        raise ReleaseError("Invalid manifest descriptor size")
    return Descriptor(str(media_type), digest, size)


def same_head(head: Head | None, expected: Descriptor) -> bool:
    return (
        head is not None
        and head.digest == expected.digest
        and head.media_type == expected.media_type
        and (head.size is None or head.size == expected.size)
    )


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self, req: urllib.request.Request, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        raise ReleaseError("Registry metadata redirects are not permitted")


class Registry:
    """Use a short-lived in-memory bearer, scoped to one fixed Docker Hub repository."""

    def __init__(
        self, username: str, token: str, *, push: bool = False, opener: Any = None
    ) -> None:
        if NAMESPACE.fullmatch(username) is None:
            raise ReleaseError("Invalid Docker Hub username")
        if not token or len(token) > 4096 or any(char in token for char in "\r\n"):
            raise ReleaseError("Docker Hub token is missing or malformed")
        self.repository = username + "/ds60sqlpy"
        self._username = username
        self._pat = token
        self._scope = "pull,push" if push else "pull"
        self._bearer = ""
        self._expires = 0.0
        self._opener = opener or urllib.request.build_opener(
            NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context())
        )

    def _authenticate(self) -> None:
        query = urllib.parse.urlencode(
            {
                "service": "registry.docker.io",
                "scope": f"repository:{self.repository}:{self._scope}",
            }
        )
        basic = base64.b64encode((self._username + ":" + self._pat).encode()).decode("ascii")
        request = urllib.request.Request(
            "https://auth.docker.io/token?" + query,
            headers={"Authorization": "Basic " + basic, "Accept": "application/json"},
        )
        try:
            with self._opener.open(request, timeout=30) as response:
                if response.status != 200:
                    raise ReleaseError("Docker Hub authentication was rejected")
                payload = json_object(response.read(65_537), 65_536)
        except ReleaseError:
            raise
        except (OSError, urllib.error.HTTPError, urllib.error.URLError):
            raise ReleaseError("Docker Hub authentication could not complete") from None
        bearer = payload.get("token", payload.get("access_token"))
        if (
            not isinstance(bearer, str)
            or not 1 <= len(bearer) <= 16_384
            or any(not 32 < ord(char) < 127 for char in bearer)
            or (
                "token" in payload
                and "access_token" in payload
                and payload["token"] != payload["access_token"]
            )
        ):
            raise ReleaseError("Docker Hub returned malformed authentication metadata")
        lifetime = payload.get("expires_in", 60)
        if type(lifetime) is not int or not 1 <= lifetime <= 86_400:
            raise ReleaseError("Docker Hub returned an invalid token lifetime")
        self._bearer = bearer
        self._expires = time.monotonic() + max(1, lifetime - 15)

    def check_push_grant(self) -> bool:
        if self._scope != "pull,push":
            raise ReleaseError("Gate must request the repository pull,push scope")
        self._authenticate()
        parts = self._bearer.split(".")
        if len(parts) != 3:
            return False
        try:
            encoded = parts[1].encode("ascii")
            payload = json_object(
                base64.urlsafe_b64decode(encoded + b"=" * (-len(encoded) % 4)), 65_536
            )
        except (ValueError, UnicodeError):
            raise ReleaseError("Authentication grant metadata is invalid") from None
        access = payload.get("access")
        if not isinstance(access, list):
            return False
        permitted = any(
            isinstance(item, dict)
            and item.get("type") == "repository"
            and item.get("name") == self.repository
            and isinstance(item.get("actions"), list)
            and all(isinstance(action, str) for action in item["actions"])
            and {"pull", "push"} <= set(item["actions"])
            for item in access
        )
        if not permitted:
            raise ReleaseError("Docker Hub token did not grant repository read/write access")
        return True

    def _request(
        self,
        method: str,
        reference: str,
        *,
        body: bytes | None = None,
        media_type: str | None = None,
    ) -> tuple[dict[str, str], bytes] | None:
        if TAG.fullmatch(reference) is None and DIGEST.fullmatch(reference) is None:
            raise ReleaseError("Invalid registry tag or digest")
        if method not in {"HEAD", "GET", "PUT"}:
            raise ReleaseError("Unsupported registry metadata operation")
        if method == "PUT" and (self._scope != "pull,push" or media_type not in MANIFEST_TYPES):
            raise ReleaseError("Registry writes were not authorized for this client")
        url = "https://registry-1.docker.io/v2/" + self.repository + "/manifests/" + reference
        for attempt in range(2):
            if not self._bearer or time.monotonic() >= self._expires:
                self._authenticate()
            headers = {"Accept": ACCEPT, "Authorization": "Bearer " + self._bearer}
            if media_type is not None:
                headers["Content-Type"] = media_type
            request = urllib.request.Request(url, data=body, method=method, headers=headers)
            try:
                with self._opener.open(request, timeout=60) as response:
                    expected_status = 201 if method == "PUT" else 200
                    if response.status != expected_status:
                        raise ReleaseError("Unexpected registry metadata response status")
                    result_headers = {key.lower(): value for key, value in response.headers.items()}
                    data = b"" if method == "HEAD" else response.read(MAX_MANIFEST_BYTES + 1)
                    if len(data) > MAX_MANIFEST_BYTES:
                        raise ReleaseError("Registry metadata exceeds its size limit")
                    return result_headers, data
            except urllib.error.HTTPError as error:
                status = error.code
                error.close()
                if status == 401 and attempt == 0:
                    self._bearer = ""
                    continue
                if status == 404 and method in {"HEAD", "GET"}:
                    return None
                raise ReleaseError(f"Registry {method} rejected with HTTP {status}") from None
            except ReleaseError:
                raise
            except (OSError, urllib.error.URLError):
                raise RegistryTransportError(
                    f"Registry {method} outcome could not be verified"
                ) from None
        raise ReleaseError("Registry authentication retry was exhausted")

    def head(self, reference: str) -> Head | None:
        response = self._request("HEAD", reference)
        if response is None:
            return None
        headers, _ = response
        digest = require_digest(headers.get("docker-content-digest"))
        media = headers.get("content-type", "").split(";", 1)[0].strip()
        if media not in MANIFEST_TYPES:
            raise ReleaseError("Registry returned an unsupported manifest type")
        length = headers.get("content-length")
        if length is not None and (
            not length.isdecimal() or not 1 <= int(length) <= MAX_MANIFEST_BYTES
        ):
            raise ReleaseError("Registry returned an invalid manifest length")
        return Head(media, digest, int(length) if length is not None else None)

    def get(self, reference: str) -> Manifest:
        response = self._request("GET", reference)
        if response is None:
            raise ReleaseError("Required registry manifest is missing")
        headers, body = response
        expected = require_digest(headers.get("docker-content-digest"))
        actual = sha256(body)
        if actual != expected or (DIGEST.fullmatch(reference) and actual != reference):
            raise ReleaseError("Registry manifest digest does not match its bytes")
        document = json_object(body)
        media = headers.get("content-type", "").split(";", 1)[0].strip()
        if (
            media not in MANIFEST_TYPES
            or document.get("mediaType") != media
            or type(document.get("schemaVersion")) is not int
            or document["schemaVersion"] != 2
        ):
            raise ReleaseError("Registry manifest schema or media type is inconsistent")
        return Manifest(Descriptor(media, actual, len(body)), document, body)

    def put(self, tag: str, body: bytes, media_type: str = OCI_INDEX) -> Descriptor:
        if TAG.fullmatch(tag) is None or len(body) > MAX_MANIFEST_BYTES:
            raise ReleaseError("Invalid manifest publication")
        expected = Descriptor(media_type, sha256(body), len(body))
        try:
            self._request("PUT", tag, body=body, media_type=media_type)
        except RegistryTransportError:
            # A lost response is not permission to PUT again. Reconcile the exact
            # expected digest using HEAD; authorization failures remain failures.
            if same_head(self.head(tag), expected):
                return expected
            raise RegistryTransportError("Manifest PUT outcome remains unverified") from None
        if not same_head(self.head(tag), expected):
            raise ReleaseError("Published manifest failed digest readback")
        return expected
