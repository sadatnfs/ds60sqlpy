"""Registry diagnostics preserve credentials and distinguish observations from inference."""

from __future__ import annotations

import base64
import io
import json
import platform
import urllib.error
from email.message import Message
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest

from scripts import ci_hub_acceptance as hub
from scripts import ci_hub_pull_diagnostics as diagnostic
from scripts.docker_registry import ReleaseError

SECRET = "do-not-export-this-test-credential"
SUBJECT = "do-not-export-this-test-subject"
IP = "192.0.2.211"


@pytest.fixture
def hosted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config = tmp_path / "docker-auth"
    config.mkdir()
    file = config / "config.json"
    file.write_text(
        json.dumps(
            {
                "auths": {
                    "https://index.docker.io/v1/": {
                        "auth": base64.b64encode(("example:" + SECRET).encode()).decode()
                    }
                }
            }
        )
    )
    file.chmod(0o600)
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_RUN_ID": "12345",
        "GITHUB_SHA": "a" * 40,
        "GITHUB_RUN_ATTEMPT": "1",
        "DOCKER_CONFIG": str(config),
        "RUNNER_TEMP": str(tmp_path),
        "DOCKERHUB_USERNAME": "example",
        "DOCKERHUB_TOKEN": SECRET,
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    return config


class Response:
    def __init__(
        self, status: int, headers: dict[str, str], body: bytes, *, head: bool = False
    ) -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self.head = head

    def __enter__(self) -> Response:
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def read(self, maximum: int) -> bytes:
        assert not self.head, "HEAD response bodies must never be read"
        return self.body[:maximum]


class Registry:
    def __init__(
        self,
        *,
        remaining: str | None = "150;w=21600",
        head_status: int = 200,
        subject: bool = True,
        grant: bool = True,
    ) -> None:
        self.remaining = remaining
        self.head_status = head_status
        self.subject = subject
        self.grant = grant
        self.calls: list[tuple[str, str]] = []
        self.tokens: dict[str, bool] = {}

    def open(self, request: Any, timeout: int) -> Response:
        assert timeout == 20
        url = urlsplit(request.full_url)
        self.calls.append((request.get_method(), url.hostname or ""))
        if url.hostname == "auth.docker.io":
            assert request.get_method() == "GET"
            repository = (
                parse_qs(url.query)["scope"][0].removeprefix("repository:").removesuffix(":pull")
            )
            authenticated = request.get_header("Authorization") is not None
            if authenticated:
                assert (
                    request.get_header("Authorization")
                    == "Basic " + base64.b64encode(("example:" + SECRET).encode()).decode()
                )
            claims = {
                "sub": SUBJECT if authenticated and self.subject else "",
                "access": [
                    {
                        "type": "repository",
                        "name": repository,
                        "actions": ["pull"] if self.grant else [],
                    }
                ],
                "private-extra": SECRET,
            }
            payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
            token = "header." + payload + ".signature"
            self.tokens[token] = authenticated
            return Response(200, {}, json.dumps({"token": token}).encode())
        assert url.hostname == "registry-1.docker.io" and request.get_method() == "HEAD"
        token = request.get_header("Authorization").removeprefix("Bearer ")
        authenticated = self.tokens[token]
        headers = {"Docker-RateLimit-Source": IP, "X-Private": SECRET}
        if self.remaining is not None:
            headers.update(
                {
                    "RateLimit-Limit": "200;w=21600" if authenticated else "100;w=21600",
                    "RateLimit-Remaining": self.remaining if authenticated else "0;w=21600",
                }
            )
        if self.head_status != 200:
            headers["Retry-After"] = "60"
            message_headers = Message()
            for key, value in headers.items():
                message_headers[key] = value
            raise urllib.error.HTTPError(
                request.full_url,
                self.head_status,
                SECRET,
                message_headers,
                io.BytesIO(SECRET.encode()),
            )
        return Response(200, headers, b"", head=True)


def test_head_only_diagnostic_preserves_child_config_and_never_exports_secrets(
    hosted: Path,
) -> None:
    registry = Registry()
    report = diagnostic.inspect_hub("example", "1.1.0", hub.environment(), opener=registry)
    assert report["pulls_allowed"] is True
    assert report["config"]["inline_auth_matches_environment"] is True
    assert report["config"]["child_config_matches"] is True
    assert report["flows"]["authenticated_quota"]["quota"]["remaining"] == 150
    assert report["flows"]["anonymous_quota_control"]["quota"]["remaining"] == 0
    assert report["requests"] == {
        "token_exchanges": 3,
        "manifest_heads": 3,
        "manifest_gets": 0,
        "image_pulls": 0,
    }
    assert registry.calls.count(("GET", "auth.docker.io")) == 3
    assert registry.calls.count(("HEAD", "registry-1.docker.io")) == 3
    serialized = json.dumps(report)
    for private in (
        SECRET,
        SUBJECT,
        IP,
        "signature",
        base64.b64encode(("example:" + SECRET).encode()).decode(),
    ):
        assert private not in serialized
    assert str(hosted) not in serialized


@pytest.mark.parametrize(
    "remaining,status",
    [("0;w=21600", 200), ("150;w=21600", 429), (None, 429), ("150;w=21600", 401)],
)
def test_exhaustion_or_request_rejection_blocks_pulls_without_subscription_inference(
    hosted: Path, remaining: str | None, status: int
) -> None:
    report = diagnostic.inspect_hub(
        "example",
        "1.1.0",
        hub.environment(),
        opener=Registry(remaining=remaining, head_status=status),
    )
    assert report["pulls_allowed"] is False and report["block_reasons"]
    assert report["requests"]["image_pulls"] == 0
    assert SECRET not in json.dumps(report) and IP not in json.dumps(report)
    assert "subscription" not in report


def test_absent_headers_remain_unknown_and_do_not_imply_unlimited(hosted: Path) -> None:
    report = diagnostic.inspect_hub(
        "example", "1.1.0", hub.environment(), opener=Registry(remaining=None)
    )
    assert report["quota_interpretation"] == "unknown-not-unlimited"
    assert report["flows"]["authenticated_quota"]["quota"]["remaining"] is None
    assert report["flows"]["authenticated_quota"]["quota"]["quota_known"] is False


@pytest.mark.parametrize("subject,grant", [(False, True), (True, False)])
def test_authentication_and_scope_cannot_be_assumed_from_http_success(
    hosted: Path, subject: bool, grant: bool
) -> None:
    report = diagnostic.inspect_hub(
        "example", "1.1.0", hub.environment(), opener=Registry(subject=subject, grant=grant)
    )
    assert not report["pulls_allowed"]


def test_missing_child_config_or_different_stored_auth_is_visible_and_blocks(hosted: Path) -> None:
    report = diagnostic.inspect_hub("example", "1.1.0", {}, opener=Registry())
    assert not report["config"]["child_config_matches"] and not report["pulls_allowed"]
    (hosted / "config.json").write_text(
        json.dumps({"auths": {"https://index.docker.io/v1/": {"auth": "wrong"}}})
    )
    report = diagnostic.inspect_hub("example", "1.1.0", hub.environment(), opener=Registry())
    assert report["config"]["inline_auth_matches_environment"] is False
    assert not report["pulls_allowed"]


def test_non_hosted_or_non_dispatch_execution_never_makes_network_requests(
    hosted: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = Registry()
    monkeypatch.setenv("GITHUB_ACTIONS", "false")
    with pytest.raises(ReleaseError, match="hosted main dispatch"):
        diagnostic.inspect_hub("example", "1.1.0", hub.environment(), opener=registry)
    assert registry.calls == []


def test_config_outside_the_owned_runner_temp_is_not_read(
    hosted: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RUNNER_TEMP", str(hosted / "other"))
    report = diagnostic.config_observation("example", SECRET, hub.environment())
    assert report["config_within_runner_temp"] is False and not report["config_regular"]


@pytest.mark.parametrize(
    "message,category",
    [
        ("unauthenticated pull rate limit " + SECRET, "hub-pull-rate-limit"),
        ("HTTP429 Too Many Requests " + SECRET, "registry-request-throttled"),
        ("HTTP401 unauthorized " + SECRET, "registry-authorization-rejected"),
        ("manifest unknown " + SECRET, "registry-reference-not-found"),
        ("TLS handshake timeout " + SECRET, "registry-transport-error"),
        ("unknown diagnostic " + SECRET, "metadata-command-failed"),
    ],
)
def test_metadata_failure_categories_do_not_retain_server_text(message: str, category: str) -> None:
    assert diagnostic.command_failure_category(message.encode()) == category
    assert SECRET not in diagnostic.command_failure_category(message.encode())


def test_quota_header_allowlist_rejects_unexpected_strings_and_private_headers() -> None:
    result = diagnostic.quota_headers(
        {
            "RateLimit-Limit": SECRET,
            "RateLimit-Remaining": "7;w=21600",
            "Retry-After": "60",
            "Docker-RateLimit-Source": IP,
            "Authorization": SECRET,
        }
    )
    assert result == {
        "quota_known": True,
        "limit": None,
        "remaining": 7,
        "window_seconds": 21600,
        "retry_after_seconds": 60,
    }


def test_shared_metadata_error_returns_only_static_category(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    def rejected(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            args, 1, stdout=b"", stderr=("HTTP429 pull rate limit " + SECRET + " " + IP).encode()
        )

    monkeypatch.setattr(subprocess, "run", rejected)
    with pytest.raises(ReleaseError) as caught:
        hub.run_output(
            ["docker", "buildx", "imagetools", "inspect", "example/ds60sqlpy:1.1.0"], root=tmp_path
        )
    assert "hub-pull-rate-limit" in str(caught.value)
    assert SECRET not in str(caught.value) and IP not in str(caught.value)


def test_operational_cli_records_observations_without_claiming_acceptance(
    hosted: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    root = tmp_path / "source"
    monkeypatch.setattr(diagnostic, "__file__", str(root / "scripts/diagnostic.py"))
    monkeypatch.setattr(
        diagnostic,
        "inspect_hub",
        lambda *args: {
            "pulls_allowed": False,
            "quota_interpretation": "unknown-not-unlimited",
            "requests": {"image_pulls": 0, "manifest_gets": 0},
        },
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(
            args, 0, stdout=b"false true 2\n", stderr=SECRET.encode()
        ),
    )
    assert diagnostic.main(["--version", "1.1.0", "--report", "work/observation.json"]) == 0
    report = json.loads((root / "work/observation.json").read_text())
    assert report["scope"] == "registry-metadata-only-no-classroom-or-source-acceptance"
    assert report["status"] == "blocked"
    assert report["engine_transport"] == {
        "http_proxy_configured": False,
        "https_proxy_configured": True,
        "registry_mirror_count": 2,
    }
    assert SECRET not in json.dumps(report)


def test_metadata_workflow_is_separate_from_full_source_and_pull_acceptance() -> None:
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/inspect-registry-metadata.yml").read_text()
    assert "workflow_dispatch:" in workflow and "  push:" not in workflow
    assert "needs: diagnostic-tests" in workflow and "max-parallel: 1" in workflow
    assert "--require-hashes" in workflow and "--only-binary=:all:" in workflow
    assert "ci_hub_pull_diagnostics.py --version" in workflow
    assert "docker pull" not in workflow and "docker push" not in workflow
    assert "docker build" not in workflow and "ci_hub_release_audit.py accept" not in workflow
    assert "contents: read" in workflow and "actions: read" in workflow
    full = (root / "scripts/ci_hub_release_audit.py").read_text()
    assert "source_ci = recovery.current_source_jobs(request)" in full


def test_minimal_diagnostic_tools_match_the_existing_uv_lock() -> None:
    import tomllib

    root = Path(__file__).resolve().parents[1]
    packages = {
        row["name"]: row for row in tomllib.loads((root / "uv.lock").read_text())["package"]
    }
    requirements = (root / "requirements/registry-diagnostic-tests.lock").read_text().splitlines()
    checked = set()
    for line in requirements:
        if not line or line.startswith("#"):
            continue
        requirement, digest = line.split(" --hash=")
        name, version = requirement.split("==")
        assert packages[name]["version"] == version
        assert digest in {wheel["hash"] for wheel in packages[name]["wheels"]}
        checked.add(name)
    assert checked == {"pytest", "iniconfig", "packaging", "pluggy", "pygments"}
