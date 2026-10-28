"""Registry HTTP behavior is tested with scripted responses, never network calls."""

from __future__ import annotations

import base64
import io
import json
import ssl
import urllib.error
import urllib.request
from email.message import Message
from typing import Any

import pytest

from scripts.docker_registry import (
    OCI_INDEX,
    NoRedirect,
    Registry,
    RegistryTransportError,
    ReleaseError,
    sha256,
)

PAT = "synthetic-private-pat"
BEARER = "synthetic-private-bearer"
BODY = b'{"schemaVersion":2,"mediaType":"application/vnd.oci.image.index.v1+json","manifests":[]}'


@pytest.fixture(autouse=True)
def reject_real_network(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.request

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("Release tests must not make real registry/authentication calls")

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", forbidden)


class Response:
    def __init__(
        self, body: bytes, headers: dict[str, str] | None = None, status: int = 200
    ) -> None:
        self.body, self.headers, self.status = io.BytesIO(body), headers or {}, status
        self.read_calls = 0

    def __enter__(self) -> Response:
        return self

    def __exit__(self, *args: Any) -> None:
        self.body.close()

    def read(self, size: int) -> bytes:
        self.read_calls += 1
        return self.body.read(size)


class Opener:
    def __init__(self, *events: Response | Exception) -> None:
        self.events = list(events)
        self.requests: list[urllib.request.Request] = []

    def open(self, request: urllib.request.Request, *, timeout: int) -> Response:
        assert 0 < timeout <= 60
        self.requests.append(request)
        event = self.events.pop(0)
        if isinstance(event, Exception):
            raise event
        return event


def auth(token: str = BEARER) -> Response:
    return Response(json.dumps({"token": token, "expires_in": 300}).encode())


def metadata(body: bytes = BODY, *, status: int = 200) -> Response:
    return Response(
        body,
        {
            "Content-Type": OCI_INDEX,
            "Docker-Content-Digest": sha256(body),
            "Content-Length": str(len(body)),
        },
        status,
    )


def http_error(status: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://registry-1.docker.io/v2/exampleuser/ds60sqlpy/manifests/test",
        status,
        PAT + BEARER,
        Message(),
        io.BytesIO((PAT + BEARER).encode()),
    )


def test_head_reads_no_manifest_body_and_uses_only_scoped_private_headers(
    capsys: pytest.CaptureFixture[str],
) -> None:
    head = metadata()
    opener = Opener(auth(), head)
    result = Registry("exampleuser", PAT, opener=opener).head("1.0.0")
    assert result is not None and result.digest == sha256(BODY)
    assert head.read_calls == 0
    token_request, registry_request = opener.requests
    assert token_request.full_url.startswith("https://auth.docker.io/token?")
    assert "repository%3Aexampleuser%2Fds60sqlpy%3Apull" in token_request.full_url
    assert (
        token_request.get_header("Authorization")
        == "Basic " + base64.b64encode(("exampleuser:" + PAT).encode()).decode()
    )
    assert registry_request.get_method() == "HEAD"
    assert registry_request.get_header("Authorization") == "Bearer " + BEARER
    assert PAT not in registry_request.full_url and BEARER not in registry_request.full_url
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("status", [401, 403, 429, 500])
def test_auth_and_server_errors_are_not_treated_as_missing_or_echoed(status: int) -> None:
    events: list[Response | Exception] = [auth(), http_error(status)]
    if status == 401:
        events += [auth(), http_error(401)]
    opener = Opener(*events)
    with pytest.raises(ReleaseError) as error:
        Registry("exampleuser", PAT, opener=opener).head("1.0.0")
    assert PAT not in str(error.value) and BEARER not in str(error.value)
    assert all(request.get_method() in {"GET", "HEAD"} for request in opener.requests)


def test_only_not_found_means_absent() -> None:
    assert (
        Registry("exampleuser", PAT, opener=Opener(auth(), http_error(404))).head("1.0.0") is None
    )


def test_lost_put_response_is_reconciled_by_head_without_a_second_put() -> None:
    opener = Opener(auth(), urllib.error.URLError(PAT + BEARER), metadata())
    result = Registry("exampleuser", PAT, push=True, opener=opener).put("1.0.0", BODY)
    assert result.digest == sha256(BODY)
    assert [request.get_method() for request in opener.requests] == ["GET", "PUT", "HEAD"]


def test_unknown_put_without_expected_digest_remains_failure() -> None:
    opener = Opener(auth(), urllib.error.URLError(PAT), http_error(404))
    with pytest.raises(RegistryTransportError, match="unverified"):
        Registry("exampleuser", PAT, push=True, opener=opener).put("1.0.0", BODY)
    assert sum(request.get_method() == "PUT" for request in opener.requests) == 1


def test_denied_put_does_not_reconcile_as_success() -> None:
    opener = Opener(auth(), http_error(403))
    with pytest.raises(ReleaseError, match="403"):
        Registry("exampleuser", PAT, push=True, opener=opener).put("1.0.0", BODY)
    assert [request.get_method() for request in opener.requests] == ["GET", "PUT"]


def test_manifest_bytes_must_match_header_and_requested_digest() -> None:
    wrong = metadata()
    wrong.headers["Docker-Content-Digest"] = "sha256:" + "0" * 64
    with pytest.raises(ReleaseError, match="digest"):
        Registry("exampleuser", PAT, opener=Opener(auth(), wrong)).get("1.0.0")
    with pytest.raises(ReleaseError, match="digest"):
        Registry("exampleuser", PAT, opener=Opener(auth(), metadata())).get("sha256:" + "0" * 64)


def test_bearer_expiry_reauthenticates_only_once_and_never_sends_pat_to_registry() -> None:
    opener = Opener(auth("old-bearer"), http_error(401), auth("new-bearer"), metadata())
    result = Registry("exampleuser", PAT, opener=opener).head("latest")
    assert result is not None
    registry_requests = [r for r in opener.requests if r.full_url.startswith("https://registry-1")]
    assert [r.get_header("Authorization") for r in registry_requests] == [
        "Bearer old-bearer",
        "Bearer new-bearer",
    ]
    assert all(PAT not in str(r.header_items()) for r in registry_requests)


def jwt(actions: list[str]) -> str:
    payload = {
        "access": [{"type": "repository", "name": "exampleuser/ds60sqlpy", "actions": actions}]
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    return "header." + encoded + ".signature"


def test_exposed_read_only_token_grant_stops_before_image_build_or_write() -> None:
    opener = Opener(auth(jwt(["pull"])))
    with pytest.raises(ReleaseError, match="read/write"):
        Registry("exampleuser", PAT, push=True, opener=opener).check_push_grant()
    assert len(opener.requests) == 1 and opener.requests[0].full_url.startswith(
        "https://auth.docker.io/"
    )
    permitted = Registry("exampleuser", PAT, push=True, opener=Opener(auth(jwt(["pull", "push"]))))
    assert permitted.check_push_grant() is True
    opaque = Registry("exampleuser", PAT, push=True, opener=Opener(auth()))
    assert opaque.check_push_grant() is False  # No invented proof from an opaque bearer.


def test_tls_verification_and_no_redirect_handler_are_always_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[Any] = []

    def build(*handlers: Any) -> Opener:
        captured.extend(handlers)
        return Opener()

    monkeypatch.setattr(urllib.request, "build_opener", build)
    Registry("exampleuser", PAT)
    assert any(isinstance(handler, NoRedirect) for handler in captured)
    https = next(
        handler for handler in captured if isinstance(handler, urllib.request.HTTPSHandler)
    )
    context = vars(https)["_context"]
    assert isinstance(context, ssl.SSLContext)
    assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname is True
    with pytest.raises(ReleaseError, match="redirect"):
        NoRedirect().redirect_request(
            urllib.request.Request("https://auth.docker.io/token"),
            None,
            302,
            "",
            {},
            "https://elsewhere.invalid/",
        )


@pytest.mark.parametrize(
    "reference", ["../credentials", "https://elsewhere.invalid", "v1?token=secret", "", "a" * 129]
)
def test_invalid_references_fail_before_authentication(reference: str) -> None:
    opener = Opener()
    with pytest.raises(ReleaseError):
        Registry("exampleuser", PAT, opener=opener).head(reference)
    assert not opener.requests
