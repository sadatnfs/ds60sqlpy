"""Hosted-only, read-only Docker Hub authentication and quota observations.

Only allowlisted booleans, numeric headers and static failure categories leave
this module. Tokens, token claims, IP headers, config contents and response
bodies are never returned or logged. HEAD observations do not download images.
"""

from __future__ import annotations

import base64
import hmac
import os
import platform
import re
import ssl
import stat
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from scripts.docker_registry import ACCEPT, NAMESPACE, NoRedirect, ReleaseError, json_object

MAX_CONFIG = 64 * 1024
HUB_KEYS = frozenset(
    {
        "https://index.docker.io/v1/",
        "https://index.docker.io/v1",
        "index.docker.io",
        "docker.io",
        "registry-1.docker.io",
    }
)
QUOTA = re.compile(r"([0-9]{1,10})(?:\s*;\s*w=([0-9]{1,10}))?\Z")


def command_failure_category(stderr: bytes) -> str:
    """Classify bounded diagnostics without retaining any of their text."""
    text = stderr[:65536].decode("utf-8", "replace").lower()
    if "pull rate limit" in text:
        return "hub-pull-rate-limit"
    if "429" in text or "too many requests" in text or "toomanyrequests" in text:
        return "registry-request-throttled"
    if any(value in text for value in ("unauthorized", "authentication required", "401", "denied")):
        return "registry-authorization-rejected"
    if any(value in text for value in ("manifest unknown", "not found", "404")):
        return "registry-reference-not-found"
    if any(
        value in text
        for value in ("timeout", "timed out", "connection", "tls", "certificate", "no such host")
    ):
        return "registry-transport-error"
    return "metadata-command-failed"


def hosted_guard() -> None:
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or re.fullmatch(r"[1-9][0-9]{0,19}", os.environ.get("GITHUB_RUN_ID", "")) is None
        or platform.system() != "Linux"
    ):
        raise ReleaseError("Registry diagnostics run only in an explicit hosted main dispatch")


def quota_headers(headers: Any) -> dict[str, Any]:
    """Discard every header except bounded numeric quota and retry observations."""
    headers = {
        str(key).lower(): value
        for key, value in (headers.items() if hasattr(headers, "items") else [])
        if str(key).lower() in {"ratelimit-limit", "ratelimit-remaining", "retry-after"}
    }
    result: dict[str, Any] = {
        "quota_known": False,
        "limit": None,
        "remaining": None,
        "window_seconds": None,
        "retry_after_seconds": None,
    }
    for name, key in (("ratelimit-limit", "limit"), ("ratelimit-remaining", "remaining")):
        value = headers.get(name, headers.get(name.title(), ""))
        if not isinstance(value, str) or len(value) > 128:
            continue
        match = QUOTA.fullmatch(value.strip())
        if match:
            result[key] = int(match[1])
            if match[2]:
                result["window_seconds"] = int(match[2])
    result["quota_known"] = result["remaining"] is not None
    value = headers.get("retry-after", headers.get("Retry-After", ""))
    if isinstance(value, str) and re.fullmatch(r"[0-9]{1,6}", value.strip()):
        result["retry_after_seconds"] = int(value.strip())
    return result


def config_observation(
    username: str, secret: str, child_environment: dict[str, str]
) -> dict[str, Any]:
    """Check only the private config created for this exact hosted operation."""
    raw_directory = os.environ.get("DOCKER_CONFIG", "")
    runner_temp = os.environ.get("RUNNER_TEMP", "")
    result: dict[str, Any] = {
        "config_exported": bool(raw_directory),
        "child_config_matches": bool(raw_directory)
        and child_environment.get("DOCKER_CONFIG") == raw_directory,
        "config_within_runner_temp": False,
        "config_regular": False,
        "config_private": False,
        "hub_entry_present": False,
        "credential_helper_configured": False,
        "inline_auth_matches_environment": None,
    }
    if not raw_directory or not runner_temp:
        return result
    directory = Path(raw_directory)
    temporary = Path(runner_temp)
    if (
        not directory.is_absolute()
        or not temporary.is_absolute()
        or not directory.resolve().is_relative_to(temporary.resolve())
        or directory.resolve() == temporary.resolve()
        or any(parent.is_symlink() for parent in (directory, *directory.parents))
    ):
        return result
    result["config_within_runner_temp"] = True
    path = directory / "config.json"
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_CONFIG:
        return result
    result["config_regular"] = True
    result["config_private"] = stat.S_IMODE(path.stat().st_mode) & 0o077 == 0
    config = json_object(path.read_bytes(), MAX_CONFIG)
    helpers = config.get("credHelpers", {})
    result["credential_helper_configured"] = bool(config.get("credsStore")) or (
        isinstance(helpers, dict) and any(helpers.get(key) for key in HUB_KEYS)
    )
    auths = config.get("auths", {})
    if not isinstance(auths, dict):
        return result
    entries = [value for key, value in auths.items() if key in HUB_KEYS and isinstance(value, dict)]
    result["hub_entry_present"] = bool(entries)
    expected = base64.b64encode((username + ":" + secret).encode("utf-8")).decode("ascii")
    values = [
        entry.get("auth")
        for entry in entries
        if isinstance(entry.get("auth"), str) and entry.get("auth")
    ]
    if values:
        result["inline_auth_matches_environment"] = all(
            value.isascii() and hmac.compare_digest(value, expected) for value in values
        )
    return result


def token_observation(token: str, repository: str) -> dict[str, Any]:
    """Return presence booleans, never claim values or a subscription inference."""
    result: dict[str, Any] = {"subject_present": None, "pull_grant_present": None}
    parts = token.split(".")
    if len(parts) != 3:
        return result
    try:
        data = parts[1].encode("ascii")
        claims = json_object(base64.urlsafe_b64decode(data + b"=" * (-len(data) % 4)), 65536)
    except (ValueError, UnicodeError):
        return result
    result["subject_present"] = isinstance(claims.get("sub"), str) and bool(claims["sub"])
    access = claims.get("access")
    if isinstance(access, list):
        result["pull_grant_present"] = any(
            isinstance(row, dict)
            and row.get("type") == "repository"
            and row.get("name") == repository
            and isinstance(row.get("actions"), list)
            and "pull" in row["actions"]
            for row in access
        )
    return result


def request(
    opener: Any, message: urllib.request.Request, *, body_limit: int = 0
) -> tuple[int | None, dict[str, Any], bytes]:
    try:
        with opener.open(message, timeout=20) as response:
            quota = quota_headers(response.headers)
            raw = response.read(body_limit + 1) if body_limit else b""
            if len(raw) > body_limit:
                raise ReleaseError("Authentication metadata exceeds its bound")
            return int(response.status), quota, raw
    except urllib.error.HTTPError as error:
        status, quota = int(error.code), quota_headers(error.headers)
        error.close()
        return status, quota, b""
    except (OSError, urllib.error.URLError, ReleaseError):
        return None, quota_headers({}), b""


def head_flow(
    opener: Any,
    repository: str,
    reference: str,
    *,
    username: str | None = None,
    secret: str | None = None,
) -> dict[str, Any]:
    """One fixed-scope token exchange followed by one HEAD, with no retries."""
    query = urllib.parse.urlencode(
        {"service": "registry.docker.io", "scope": "repository:" + repository + ":pull"}
    )
    headers = {"Accept": "application/json", "User-Agent": "ds60-hub-readonly-diagnostic"}
    if username is not None and secret is not None:
        headers["Authorization"] = (
            "Basic " + base64.b64encode((username + ":" + secret).encode()).decode()
        )
    message = urllib.request.Request("https://auth.docker.io/token?" + query, headers=headers)
    status, token_quota, raw = request(opener, message, body_limit=65536)
    result: dict[str, Any] = {
        "token_http_status": status,
        "head_http_status": None,
        "head_attempted": False,
        "token_metadata_observation": {"subject_present": None, "pull_grant_present": None},
        "quota": token_quota,
        "error": None,
    }
    if status != 200:
        result["error"] = "token-exchange-not-accepted"
        return result
    try:
        payload = json_object(raw, 65536)
        token = payload.get("token", payload.get("access_token"))
        if (
            not isinstance(token, str)
            or not 1 <= len(token) <= 16384
            or any(not 32 < ord(char) < 127 for char in token)
        ):
            raise ReleaseError("Invalid token envelope")
    except (ValueError, UnicodeError):
        result["error"] = "invalid-token-envelope"
        return result
    result["token_metadata_observation"] = token_observation(token, repository)
    message = urllib.request.Request(
        "https://registry-1.docker.io/v2/" + repository + "/manifests/" + reference,
        method="HEAD",
        headers={
            "Accept": ACCEPT,
            "Authorization": "Bearer " + token,
            "User-Agent": "ds60-hub-readonly-diagnostic",
        },
    )
    result["head_attempted"] = True
    status, quota, _ = request(opener, message)
    result["head_http_status"] = status
    result["quota"] = quota
    if status != 200:
        result["error"] = "manifest-head-not-accepted"
    return result


def inspect_hub(
    namespace: str, version: str, child_environment: dict[str, str], *, opener: Any = None
) -> dict[str, Any]:
    hosted_guard()
    username = os.environ.get("DOCKERHUB_USERNAME", "")
    secret = os.environ.get("DOCKERHUB_TOKEN", "")
    if (
        NAMESPACE.fullmatch(namespace) is None
        or username != namespace
        or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None
        or not secret
        or len(secret) > 4096
        or any(char in secret for char in "\r\n")
    ):
        raise ReleaseError("Hosted read credentials or release version are unavailable")
    client = opener or urllib.request.build_opener(
        NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context())
    )
    config = config_observation(username, secret, child_environment)
    flows = {
        "authenticated_quota": head_flow(
            client, "ratelimitpreview/test", "latest", username=username, secret=secret
        ),
        "anonymous_quota_control": head_flow(client, "ratelimitpreview/test", "latest"),
        "authenticated_release": head_flow(
            client, namespace + "/ds60sqlpy", version, username=username, secret=secret
        ),
    }
    blocked = []
    if not all(
        config[key]
        for key in (
            "config_exported",
            "child_config_matches",
            "config_within_runner_temp",
            "config_regular",
        )
    ):
        blocked.append("docker-config-not-bound-to-child")
    if config["inline_auth_matches_environment"] is not True:
        blocked.append("docker-config-auth-not-confirmed")
    for name in ("authenticated_quota", "authenticated_release"):
        flow = flows[name]
        if flow["token_http_status"] != 200 or flow["head_http_status"] != 200:
            blocked.append(name + "-request-not-accepted")
        if flow["token_metadata_observation"]["subject_present"] is not True:
            blocked.append(name + "-authenticated-subject-not-observed")
        if flow["token_metadata_observation"]["pull_grant_present"] is not True:
            blocked.append(name + "-pull-grant-not-observed")
        if flow["quota"]["remaining"] == 0:
            blocked.append(name + "-quota-exhausted")
    known = flows["authenticated_quota"]["quota"]["quota_known"]
    return {
        "schema_version": 1,
        "kind": "ds60-hub-head-diagnostic",
        "config": config,
        "flows": flows,
        "pulls_allowed": not blocked,
        "block_reasons": blocked,
        "quota_interpretation": "server-reported-remaining" if known else "unknown-not-unlimited",
        "requests": {
            "token_exchanges": 3,
            "manifest_heads": sum(flow["head_attempted"] for flow in flows.values()),
            "manifest_gets": 0,
            "image_pulls": 0,
        },
        "limitations": [
            "Configuration and token-presence observations do not prove a Docker CLI "
            "request carried credentials.",
            "Absent quota headers do not establish unlimited pulls or any account subscription.",
            "Authenticated requests can still meet shared-IP abuse throttling; "
            "no IP headers are retained.",
        ],
    }
