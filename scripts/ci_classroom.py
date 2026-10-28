"""Qualify an explicitly disposable ordinary classroom with reusable native CI phases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.ci_profiles import RUNNERS, selected  # noqa: E402

SCIENTIFIC = {"python-core", "data-engineering", "dbt-duckdb", "stan-cpu", "julia"}
CORE_BROWSER = (
    ("scripts/check_classroom_browser.py", "browser-receipts.json"),
    ("courses/web-development/authoring/check_browser.py", "web-browser-receipts.json"),
    ("courses/web-development/authoring/check_live_preview.py", "live-preview-receipts.json"),
    ("scripts/check_d3_browser.py", "d3-browser-receipts.json"),
    ("scripts/check_plotly_browser.py", "plotly-browser-receipts.json"),
)


def required_checks(group: str) -> frozenset[str]:
    """Mandatory named evidence for a complete ordinary qualification group."""
    profiles = selected(group)
    names = {
        "read-only launcher doctor",
        "scripts/check_lab_http.py",
        "scripts/check_classroom_profiles.py",
        "scripts/check_classroom_failures.py",
        "scripts/check_module_references.py",
        "scripts/check_lab_http.py:persistence",
        "scripts/check_classroom_profiles.py:persistence",
    }
    if group == "python-core":
        names.add("complete SQL lessons and executable solutions")
    if group in {"python-core", "r"}:
        names.update(
            {
                "scripts/check_scientific_artifacts.py",
                "scripts/check_scientific_artifacts.py:persistence",
            }
        )
    if group == "data-engineering":
        names.add("owned ML service HTTP and rollback")
        names.add("owned data product HTTP, publication and recovery")
    if group == "pytorch":
        names.add("owned inference lifecycle, SSE and persistent history")
    if group == "data-platforms":
        names.add("owned Arrow Flight, Rust IPC and persistent data")
    if group == "java":
        names.add("owned Kafka transactions, offsets and persistent data")
    if set(profiles) & SCIENTIFIC:
        names.update(
            {"scripts/check_scientist_browser.py", "scripts/check_scientist_browser.py:persistence"}
        )
        if group == "python-core":
            names.update(script for script, _ in CORE_BROWSER)
            names.update(script + ":persistence" for script, _ in CORE_BROWSER[-2:])
    return frozenset(names)


def clean_environment(project: str) -> dict[str, str]:
    secret_keys = {
        "DOCKERHUB_USERNAME",
        "DOCKERHUB_TOKEN",
        "HUB_USER",
        "HUB_TOKEN",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "DOCKER_CONFIG",
        "DOCKER_DEFAULT_PLATFORM",
    }
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in secret_keys and not key.startswith(("DS60_", "COMPOSE_"))
    }
    env.update(
        COMPOSE_PROJECT_NAME=project,
        DS60_CLASSROOM_PORT="0",
        DS60_POSTGRES_PORT="0",
        COMPOSE_BAKE="false",
        PYTHONUTF8="1",
    )
    return env


def compose(project: str) -> list[str]:
    return [
        "docker",
        "compose",
        "--env-file",
        "docker/registry-mirrors.env.txt",
        "-f",
        "compose.classroom.yaml",
        "-p",
        project,
        "--profile",
        "*",
    ]


def launcher(project: str, version: str, profiles: list[str], *, resume: bool = False) -> list[str]:
    command = [
        "bash",
        "classroom",
        "--project",
        project,
        "--registry",
        "mirrors",
        "--local-build",
        "--tag",
        version,
        "--no-browser",
    ]
    if resume:
        command.append("--no-build")
    for profile in profiles:
        command.extend(["--profile", profile])
    return command


def browser_lock(architecture: str) -> str:
    if architecture not in RUNNERS:
        raise ValueError("Unsupported native architecture")
    return (
        "requirements/ci-browser.arm64.lock"
        if architecture == "arm64"
        else "requirements/ci-browser.lock"
    )


class ClassroomCI:
    def __init__(self, group: str, project: str, version: str, architecture: str) -> None:
        if re.fullmatch(r"ds60-(?:ci|pub)-[a-z0-9][a-z0-9-]{0,80}", project) is None:
            raise ValueError("Use a distinct ds60-ci- or ds60-pub- project")
        current = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
        if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version) is None or version != current:
            raise ValueError("CI image version must match the source release")
        if architecture not in RUNNERS:
            raise ValueError("Unsupported native architecture")
        self.group, self.project, self.version, self.architecture = (
            group,
            project,
            version,
            architecture,
        )
        self.profiles = selected(group)
        self.env = clean_environment(project)
        self.marker = ROOT / ".classroom" / project / "ci-owner.json"
        self.identity = {
            "project": project,
            "group": group,
            "version": version,
            "architecture": architecture,
        }
        self.completed: list[str] = []

    def run(self, command: list[str]) -> None:
        subprocess.run(command, cwd=ROOT, env=self.env, check=True)

    def output(self, command: list[str]) -> str:
        return subprocess.check_output(command, cwd=ROOT, env=self.env, text=True).strip()

    def owned(self) -> None:
        if (
            self.marker.is_symlink()
            or not self.marker.is_file()
            or json.loads(self.marker.read_text()) != self.identity
        ):
            raise ValueError("This CI project has no matching ownership marker")

    def prepare(self) -> None:
        engine = self.output(["docker", "info", "--format", "{{.Architecture}}"])
        aliases = {"x86_64": "amd64", "aarch64": "arm64", "amd64": "amd64", "arm64": "arm64"}
        if aliases.get(engine) != self.architecture:
            raise ValueError(
                "Use the declared native Docker architecture; emulation is not qualification"
            )
        for command in (
            ["docker", "ps", "-aq"],
            ["docker", "network", "ls", "-q"],
            ["docker", "volume", "ls", "-q"],
        ):
            if self.output(
                [*command, "--filter", "label=com.docker.compose.project=" + self.project]
            ):
                raise ValueError(
                    "Choose a fresh CI project; existing resources will not be modified"
                )
        if self.marker.exists() or self.marker.is_symlink():
            raise ValueError("Choose a fresh CI ownership marker")
        doctor = launcher(self.project, self.version, self.profiles)
        doctor.insert(2, "doctor")
        existed = self.marker.parent.exists()
        self.run(doctor)
        if self.marker.parent.exists() != existed:
            raise ValueError("Read-only doctor unexpectedly created project state")
        self.marker.parent.mkdir(parents=True, exist_ok=True)
        self.marker.write_text(json.dumps(self.identity, sort_keys=True) + "\n")
        self.run(launcher(self.project, self.version, self.profiles))

    def url(self) -> str:
        return (self.marker.parent / "classroom.url").read_text().strip()

    def check(
        self,
        script: str,
        report: str | None = None,
        *,
        browser: bool = False,
        extra: list[str] | None = None,
        persistence: bool = False,
    ) -> None:
        python = str(ROOT / "work/browser-env/bin/python") if browser else sys.executable
        command = [python, script, "--url", self.url(), "--confirm-disposable"]
        if report:
            command.extend(["--report", "work/" + report])
        command.extend(extra or [])
        if persistence:
            command.append("--check-persistence")
        self.run(command)
        self.completed.append(script + (":persistence" if persistence else ""))

    def replace(self) -> None:
        self.run([*compose(self.project), "down"])
        self.run(launcher(self.project, self.version, self.profiles, resume=True))

    def qualify(self) -> None:
        self.owned()
        doctor = launcher(self.project, self.version, self.profiles)
        doctor.insert(2, "doctor")
        marker_before = self.marker.read_bytes()
        self.run(doctor)
        if self.marker.read_bytes() != marker_before:
            raise ValueError("Read-only doctor changed the ownership marker")
        self.completed.append("read-only launcher doctor")
        (ROOT / "work").mkdir(exist_ok=True)
        smoke_profiles = " ".join(dict.fromkeys(["python-core", *self.profiles]))
        self.check("scripts/check_lab_http.py", extra=["--reset-sql"])
        self.check(
            "scripts/check_classroom_profiles.py",
            "runtime-receipts.json",
            extra=["--profiles", smoke_profiles],
        )
        self.check(
            "scripts/check_classroom_failures.py",
            "runtime-failures.json",
            extra=["--profiles", smoke_profiles]
            + (["--check-timeout"] if self.group == "python-core" else []),
        )
        self.check(
            "scripts/check_module_references.py",
            "module-reference-results.json",
            extra=["--profiles", " ".join(self.profiles)],
        )
        if self.group == "python-core":
            for scope in ("all", "solutions"):
                self.run(
                    [
                        *compose(self.project),
                        "exec",
                        "-T",
                        "lab",
                        "python",
                        "scripts/course.py",
                        "sql",
                        "--quiet",
                        scope,
                        "--reset",
                    ]
                )
            self.completed.append("complete SQL lessons and executable solutions")
        figures = self.group in {"python-core", "r"}
        if figures:
            self.check(
                "scripts/check_scientific_artifacts.py",
                "scientific-artifact-receipts.json",
                extra=["--profiles", " ".join(self.profiles)],
            )
        if self.group == "data-engineering":
            self.run(
                [
                    sys.executable,
                    "courses/ml-engineering/projects/local-system/check.py",
                    "--project",
                    (
                        "ds60-mle-ci-"
                        + os.environ.get("GITHUB_RUN_ID", "local")
                        + "-"
                        + os.environ.get("GITHUB_RUN_ATTEMPT", "1")
                        + "-"
                        + self.architecture
                    ),
                    "--image",
                    "ds60sqlpy-worker-data-engineering:" + self.version,
                    "--confirm-disposable",
                    "--report",
                    "work/ml-service-receipts.json",
                ]
            )
            self.completed.append("owned ML service HTTP and rollback")
            self.run(
                [
                    sys.executable,
                    "courses/data-ml-engineering/projects/data-product/check_project.py",
                    "--workspace",
                    "work/data-product-ci-workspace",
                    "--image",
                    "ds60sqlpy-worker-data-engineering:" + self.version,
                    "--report",
                    "work/data-product-receipts.json",
                    "--confirm-disposable",
                ]
            )
            self.completed.append("owned data product HTTP, publication and recovery")
        self.replace()
        self.check("scripts/check_lab_http.py", persistence=True)
        self.check(
            "scripts/check_classroom_profiles.py",
            "runtime-receipts.json",
            extra=["--profiles", smoke_profiles],
            persistence=True,
        )
        if figures:
            self.check(
                "scripts/check_scientific_artifacts.py",
                "scientific-artifact-receipts.json",
                extra=["--profiles", " ".join(self.profiles)],
                persistence=True,
            )
        scientific = [profile for profile in self.profiles if profile in SCIENTIFIC]
        if scientific or self.group == "pytorch":
            self.run([sys.executable, "-m", "venv", "work/browser-env"])
            browser = str(ROOT / "work/browser-env/bin/python")
            self.run(
                [
                    browser,
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    "--require-hashes",
                    "--only-binary=:all:",
                    "-r",
                    browser_lock(self.architecture),
                ]
            )
            self.run([browser, "-m", "playwright", "install", "--with-deps", "chromium"])
            if self.group == "python-core":
                for script, report in CORE_BROWSER:
                    self.check(script, report, browser=True)
            if scientific:
                self.check(
                    "scripts/check_scientist_browser.py",
                    "scientist-browser.json",
                    browser=True,
                    extra=["--profiles", *scientific],
                )
                self.replace()
                if self.group == "python-core":
                    for script, report in CORE_BROWSER[-2:]:
                        self.check(script, report, browser=True, persistence=True)
                self.check(
                    "scripts/check_scientist_browser.py",
                    "scientist-browser.json",
                    browser=True,
                    extra=["--profiles", *scientific],
                    persistence=True,
                )
            if self.group == "pytorch":
                identity = hashlib.sha256(self.project.encode()).hexdigest()[:20]
                self.run(
                    [
                        sys.executable,
                        "scripts/check_inference_project.py",
                        "--project",
                        "ds60-infer-ci-" + identity,
                        "--image",
                        "ds60sqlpy-worker-llm-torch-cpu:" + self.version,
                        "--browser-python",
                        browser,
                        "--confirm-disposable",
                        "--report",
                        "work/inference-project-receipts.json",
                    ]
                )
                self.completed.append("owned inference lifecycle, SSE and persistent history")
        if self.group in {"data-platforms", "java"}:
            workshop = "arrow-flight" if self.group == "data-platforms" else "streaming"
            variable = (
                "DS60_PLATFORM_IMAGE" if self.group == "data-platforms" else "DS60_JAVA_IMAGE"
            )
            image_profile = "data-platforms-python" if self.group == "data-platforms" else "java21"
            self.run(
                [
                    "env",
                    f"{variable}=ds60sqlpy-worker-{image_profile}:{self.version}",
                    sys.executable,
                    "courses/apache-data-platforms/authoring/qualify_workshop.py",
                    workshop,
                    "--workspace",
                    "work/apache-service-workspace",
                    "--evidence",
                    "work/apache-service-receipts.json",
                    "--require-ipc" if self.group == "data-platforms" else "--prepare",
                ]
            )
            self.completed.append(
                "owned Arrow Flight, Rust IPC and persistent data"
                if self.group == "data-platforms"
                else "owned Kafka transactions, offsets and persistent data"
            )
        self.run(["git", "diff", "--exit-code"])
        if set(self.completed) != required_checks(self.group) or len(self.completed) != len(
            set(self.completed)
        ):
            raise ValueError("Qualification did not produce the exact required check set")
        summary = {
            "schema_version": 1,
            "complete": True,
            "passed": True,
            **self.identity,
            "profiles": self.profiles,
            "revision": self.output(["git", "rev-parse", "HEAD"]),
            "run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
            "checks": [{"name": name, "passed": True} for name in self.completed],
        }
        (ROOT / "work/ci-qualification.json").write_text(json.dumps(summary, indent=2) + "\n")

    def cleanup(self) -> None:
        if not self.marker.exists():
            print("No owned CI project was prepared; nothing to remove.")
            return
        self.owned()
        self.run([*compose(self.project), "down", "--volumes", "--remove-orphans"])

    def diagnostics(self) -> None:
        if self.marker.exists():
            self.owned()
            self.run([*compose(self.project), "logs", "--no-color", "--tail", "100"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("prepare", "qualify", "cleanup", "diagnostics"))
    parser.add_argument("--group", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--architecture", choices=tuple(RUNNERS), default="amd64")
    parser.add_argument("--confirm-disposable", action="store_true")
    args = parser.parse_args()
    if not args.confirm_disposable:
        parser.error("Use --confirm-disposable for explicitly owned CI state")
    work = ClassroomCI(args.group, args.project, args.version, args.architecture)
    getattr(work, args.phase)()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
