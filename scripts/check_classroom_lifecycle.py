#!/usr/bin/env python3
"""Qualify classroom lifecycle transitions on a disposable ds60-p7- Compose project.

The harness drives the real ./classroom launcher from its own clean git worktree
through fresh setup, stop, resume, rerun, restart, recreate (no volume removal),
update with --rebuild and a final rerun. After every start it proves that the
learner's progress, saved pad, run receipt, worker token and a learner-created
SQL table survived, and that the project volumes are the same volumes. It never
touches protected projects, and cleanup removes only what its ownership marker
proves this run created. The JSON report holds digests, IDs and verdicts only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import string
import subprocess
import sys
import time
import tomllib
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.ci_classroom import clean_environment  # noqa: E402

PROJECT_RE = re.compile(r"^ds60-p7-[a-z0-9-]+$")
PROJECT_LIMIT = 49
TAG_RE = re.compile(r"^(\d+\.\d+\.\d+)-p7[0-9a-f]{8}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
PROTECTED_NAMES = (
    "ds60-classroom",
    "ds60-phase1-browser",
    "ds60-livetest-pg",
    "tender_feistel",
    "condescending_kirch",
    "awesome-copilot",
)
PROTECTED_VOLUME_PREFIXES = ("ds60-classroom_", "ds60-phase1-browser_")
SHARED_IMAGES = ("ds60sqlpy-lab:2.1.0", "ds60sqlpy-worker-python-core:2.1.0")
IMAGE_REPOSITORIES = {"lab": "ds60sqlpy-lab", "python-core-worker": "ds60sqlpy-worker-python-core"}
VOLUMES = ("classroom-learning", "classroom-runtime", "postgres-data")
STEPS = ("fresh", "stop", "resume", "rerun", "restart", "recreate", "update", "final-rerun")
BUILD_TIMEOUT = 2700
STEP_TIMEOUT = 600
PROBE_TIMEOUT = 300
QUERY_TIMEOUT = 120
REVISION_LABEL = "org.opencontainers.image.revision"
PROGRESS_FILE = "/workspace/.learning/progress.json"
# The lab saves evidence notes here; progress.json appears only after a completion.
COACHING_FILE = "/workspace/.learning/coaching.json"
LEARNER_FILES = {"progress.json": PROGRESS_FILE, "coaching.json": COACHING_FILE}
# The lab drops every capability, so root cannot read learner-owned files; use the learner.
LEARNER_USER = "1000:1000"
TOKEN_VARIABLE = "DS60_MODULE_TOKEN_FILE"
# Runs inside the lab container; only a sha256 hex digest (or "absent") leaves it.
DIGEST_CODE = (
    "import hashlib, os, pathlib, sys\n"
    "name = sys.argv[1]\n"
    "path = pathlib.Path(os.environ.get(name, '') if name.startswith('DS60_') else name)\n"
    "print(hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'absent')\n"
)


class HarnessError(RuntimeError):
    """A refusal or failed precondition; the message never contains secrets."""


@dataclass
class Completed:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class Runner(Protocol):
    def __call__(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str] | None,
        timeout: float,
    ) -> Completed: ...


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value


def run_command(
    argv: Sequence[str], *, cwd: Path, env: Mapping[str, str] | None, timeout: float
) -> Completed:
    try:
        result = subprocess.run(
            list(argv),
            cwd=cwd,
            env=None if env is None else dict(env),
            timeout=timeout,
            capture_output=True,
            text=True,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return Completed(124, _text(exc.stdout), _text(exc.stderr) + "\nTimed out.")
    except OSError as exc:
        return Completed(127, "", str(exc))
    return Completed(result.returncode, result.stdout, result.stderr)


def validate_project(project: str) -> None:
    if (
        len(project) > PROJECT_LIMIT
        or PROJECT_RE.fullmatch(project) is None
        or any(name in project for name in PROTECTED_NAMES)
    ):
        raise HarnessError(
            f"Refusing project {project!r}: use a fresh ds60-p7-[a-z0-9-] name of at most "
            f"{PROJECT_LIMIT} characters that names no protected resource."
        )


def validate_tag(tag: str, version: str) -> None:
    match = TAG_RE.fullmatch(tag)
    if match is None or match.group(1) != version:
        raise HarnessError(f"Refusing image tag {tag!r}: use {version}-p7<sha8>.")


def p7_tag(version: str, commit: str) -> str:
    return f"{version}-p7{commit[:8]}"


def pyproject_version(root: Path) -> str:
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    if not isinstance(version, str) or VERSION_RE.fullmatch(version) is None:
        raise HarnessError("pyproject.toml has no plain release version.")
    return version


def parse_json(text: str) -> list[dict[str, Any]]:
    """Read Docker JSON output, which is either one array or one object per line."""
    text = text.strip()
    if not text:
        return []
    if text.startswith("["):
        loaded = json.loads(text)
        return [item for item in loaded if isinstance(item, dict)]
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def protected_container(name: str, project: str) -> bool:
    return any(item in name for item in PROTECTED_NAMES) or any(
        project.startswith(item) for item in PROTECTED_NAMES
    )


def diff_protected(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for volume in sorted(set(before["volumes"]) - set(after["volumes"])):
        errors.append(f"protected volume removed: {volume}")
    for reference, image in sorted(before["images"].items()):
        if after["images"].get(reference) != image:
            errors.append(f"shared image changed: {reference}")
    for name, state in sorted(before["containers"].items()):
        now = after["containers"].get(name)
        if now != state:
            warnings.append(f"protected container {name}: {state} -> {now or 'absent'}")
    return {"errors": errors, "warnings": warnings}


def ordered_steps(requested: Sequence[str]) -> tuple[str, ...]:
    unknown = [step for step in requested if step not in STEPS]
    if unknown or not requested or requested[0] != "fresh":
        raise HarnessError(f"Steps must start with fresh and come from: {', '.join(STEPS)}.")
    positions = [STEPS.index(step) for step in requested]
    if positions != sorted(set(positions)):
        raise HarnessError("Steps must be unique and in the canonical order.")
    return tuple(requested)


@dataclass
class Options:
    project: str
    target: str = "HEAD"
    base: str | None = None
    steps: tuple[str, ...] = STEPS
    report: Path | None = None
    keep: bool = False
    seed_images: str | None = None
    profiles: tuple[str, ...] = ()
    architecture: str | None = None


@dataclass
class Step:
    name: str
    verdict: str = "passed"
    commands: list[dict[str, Any]] = field(default_factory=list)
    checks: dict[str, str] = field(default_factory=dict)
    observed: dict[str, Any] = field(default_factory=dict)

    def expect(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks[name] = "pass" if ok else "fail" + (f": {detail}" if detail else "")
        if not ok:
            self.verdict = "failed"

    def report(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "verdict": self.verdict,
            "commands": self.commands,
            "checks": self.checks,
            **self.observed,
        }


class Lifecycle:
    def __init__(self, options: Options, *, runner: Runner = run_command, root: Path = ROOT):
        validate_project(options.project)
        self.steps_selected = ordered_steps(options.steps)
        if options.seed_images is not None and VERSION_RE.fullmatch(options.seed_images) is None:
            raise HarnessError("--seed-images takes a plain release version such as 2.1.0.")
        self.options = options
        self.runner: Runner = runner
        self.root = root
        self.project = options.project
        self.worktree = root / "work" / "p7-worktrees" / self.project
        self.state_dir = self.worktree / ".classroom" / self.project
        self.marker = self.state_dir / "p7-owner.json"
        self.logs = root / "work" / "p7-logs" / self.project
        self.report_path = options.report or root / "work" / f"p7-lifecycle-{self.project}.json"
        self.env = clean_environment(self.project)
        self.version = pyproject_version(root)
        self.run_id = uuid.uuid4().hex
        alphabet = string.ascii_letters + string.digits
        self.sentinel_name = f"p7_{self.run_id[:12]}"
        self.sentinel_token = "".join(secrets.choice(alphabet) for _ in range(24))
        self.base = ""
        self.target = ""
        self.tags: dict[str, str] = {}
        self.owned_images: list[str] = []
        self.created_worktree = False
        self.marker_written = False
        self.steps: list[Step] = []
        self.sequence = 0
        self.report: dict[str, Any] = {
            "schema_version": 1,
            "project": self.project,
            "run_id": self.run_id,
            "mode": "seeded" if options.seed_images else "build",
            "profiles": list(options.profiles) or ["starter"],
            "sentinel": {
                "name": self.sentinel_name,
                "token_sha256": hashlib.sha256(self.sentinel_token.encode()).hexdigest(),
            },
            "passed": False,
        }

    # Command helpers -----------------------------------------------------------

    def display(self, argv: Sequence[str]) -> list[str]:
        return [
            item.replace(self.sentinel_token, "<redacted>") if self.sentinel_token in item else item
            for item in argv
        ]

    def call(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float = QUERY_TIMEOUT,
    ) -> Completed:
        return self.runner(argv, cwd=cwd or self.root, env=env, timeout=timeout)

    def output(self, argv: Sequence[str], **kwargs: Any) -> str:
        result = self.call(argv, **kwargs)
        if result.returncode:
            raise HarnessError(
                f"{' '.join(self.display(argv)[:4])} failed with exit {result.returncode}."
            )
        return result.stdout.strip()

    def compose(self, *args: str) -> list[str]:
        return [
            "docker",
            "compose",
            "--project-directory",
            str(self.worktree),
            "--env-file",
            str(self.worktree / "docker" / "registry-mirrors.env.txt"),
            "-f",
            str(self.worktree / "compose.classroom.yaml"),
            "-p",
            self.project,
            "--profile",
            "*",
            *args,
        ]

    def compose_output(self, *args: str) -> str:
        return self.output(self.compose(*args), cwd=self.worktree, env=self.env)

    def logged(self, step: Step, label: str, argv: Sequence[str], **kwargs: Any) -> Completed:
        started = time.monotonic()
        result = self.call(argv, **kwargs)
        seconds = round(time.monotonic() - started, 1)
        self.sequence += 1
        self.logs.mkdir(parents=True, exist_ok=True)
        log = self.logs / f"{self.sequence:02d}-{step.name}-{label}.log"
        text = (result.stdout + "\n" + result.stderr).replace(self.sentinel_token, "<redacted>")
        log.write_text(text)
        step.commands.append(
            {"argv": self.display(argv), "exit_code": result.returncode, "seconds": seconds}
        )
        print(
            f"[p7] {step.name}: {label} exit {result.returncode} in {seconds}s",
            file=sys.stderr,
            flush=True,
        )
        return result

    def launch(self, step: Step, label: str, args: Sequence[str], timeout: float) -> bool:
        result = self.logged(
            step,
            label,
            ["./classroom", *args],
            cwd=self.worktree,
            env=self.env,
            timeout=timeout,
        )
        step.expect(f"{label} exit 0", result.returncode == 0, f"exit {result.returncode}")
        return result.returncode == 0

    # Guards and snapshots ----------------------------------------------------

    def resolve(self, revision: str) -> str:
        commit = self.output(["git", "-C", str(self.root), "rev-parse", "--verify", revision])
        commit = commit.split()[-1] if commit else ""
        if COMMIT_RE.fullmatch(commit) is None:
            raise HarnessError(f"Could not resolve {revision!r} to a commit.")
        return commit

    def image_id(self, reference: str) -> str | None:
        result = self.call(["docker", "image", "inspect", "--format", "{{.Id}}", reference])
        return result.stdout.strip() if result.returncode == 0 else None

    def guard(self) -> None:
        validate_project(self.project)
        self.target = self.resolve(self.options.target + "^{commit}")
        base = self.options.base or f"{self.target}~1"
        self.base = self.resolve(base + "^{commit}")
        self.tags = {
            "base": p7_tag(self.version, self.base),
            "target": p7_tag(self.version, self.target),
        }
        for tag in self.tags.values():
            validate_tag(tag, self.version)
        engine = self.output(["docker", "info", "--format", "{{.Architecture}}"])
        aliases = {"x86_64": "amd64", "aarch64": "arm64", "amd64": "amd64", "arm64": "arm64"}
        architecture = aliases.get(engine, engine)
        if self.options.architecture and self.options.architecture != architecture:
            raise HarnessError("The Docker engine architecture differs from --architecture.")
        self.report.update(
            base=self.base, target=self.target, tags=self.tags, architecture=architecture
        )
        projects = parse_json(self.output(["docker", "compose", "ls", "-a", "--format", "json"]))
        if any(item.get("Name") == self.project for item in projects):
            raise HarnessError(f"{self.project} already exists as a Compose project.")
        label = f"label=com.docker.compose.project={self.project}"
        for argv in (
            ["docker", "ps", "-aq", "--filter", label],
            ["docker", "volume", "ls", "-q", "--filter", label],
            ["docker", "network", "ls", "-q", "--filter", label],
        ):
            if self.output(argv):
                raise HarnessError(f"{self.project} already has Docker resources; pick a new name.")
        if self.worktree.exists() or self.worktree.is_symlink():
            raise HarnessError(f"{self.worktree} already exists; pick a new project name.")
        for tag in sorted(set(self.tags.values())):
            for repository in IMAGE_REPOSITORIES.values():
                if self.image_id(f"{repository}:{tag}") is not None:
                    raise HarnessError(
                        f"{repository}:{tag} already exists; this run would not own it."
                    )
        if self.options.seed_images:
            for repository in IMAGE_REPOSITORIES.values():
                if self.image_id(f"{repository}:{self.options.seed_images}") is None:
                    raise HarnessError(
                        f"Seed image {repository}:{self.options.seed_images} is missing."
                    )

    def snapshot_protected(self) -> dict[str, Any]:
        names = self.output(["docker", "volume", "ls", "--format", "{{.Name}}"]).splitlines()
        volumes = sorted(name for name in names if name.startswith(PROTECTED_VOLUME_PREFIXES))
        images = {reference: self.image_id(reference) for reference in SHARED_IMAGES}
        listing = self.output(
            [
                "docker",
                "ps",
                "-a",
                "--format",
                '{{.Names}}\t{{.State}}\t{{.Label "com.docker.compose.project"}}',
            ]
        )
        containers: dict[str, str] = {}
        for line in listing.splitlines():
            name, state, project = ([*line.split("\t"), "", ""])[:3]
            if name and protected_container(name, project):
                containers[name] = state
        return {"volumes": volumes, "images": images, "containers": containers}

    # Ownership ------------------------------------------------------------------

    def create_worktree(self) -> None:
        self.worktree.parent.mkdir(parents=True, exist_ok=True)
        result = self.call(
            [
                "git",
                "-C",
                str(self.root),
                "worktree",
                "add",
                "--detach",
                str(self.worktree),
                self.base,
            ],
            timeout=STEP_TIMEOUT,
        )
        self.created_worktree = self.worktree.exists()
        if result.returncode:
            raise HarnessError("git worktree add failed.")

    def write_marker(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if self.marker.exists() or self.marker.is_symlink():
            raise HarnessError("An ownership marker already exists for this project.")
        identity = {
            "project": self.project,
            "run_id": self.run_id,
            "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "base": self.base,
            "target": self.target,
            "tags": sorted(set(self.tags.values())),
        }
        self.marker.write_text(json.dumps(identity, sort_keys=True) + "\n")
        self.marker_written = True

    def check_owned(self) -> None:
        if self.marker.is_symlink() or not self.marker.is_file():
            raise HarnessError("No ownership marker for this project; refusing to remove anything.")
        try:
            identity = json.loads(self.marker.read_text())
        except json.JSONDecodeError as exc:
            raise HarnessError("The ownership marker is unreadable; refusing cleanup.") from exc
        if (
            not isinstance(identity, dict)
            or identity.get("project") != self.project
            or identity.get("run_id") != self.run_id
        ):
            raise HarnessError("The ownership marker belongs to another run; refusing cleanup.")

    def own_tag(self, tag: str) -> None:
        for repository in IMAGE_REPOSITORIES.values():
            reference = f"{repository}:{tag}"
            if reference not in self.owned_images:
                self.owned_images.append(reference)

    def cleanup(self) -> dict[str, Any]:
        self.check_owned()
        summary: dict[str, Any] = {}
        down = self.call(
            self.compose("down", "-v", "--remove-orphans"),
            cwd=self.worktree,
            env=self.env,
            timeout=STEP_TIMEOUT,
        )
        summary["down_exit_code"] = down.returncode
        removed: list[str] = []
        for reference in self.owned_images:
            if self.call(["docker", "image", "rm", reference]).returncode == 0:
                removed.append(reference)
        summary["images_removed"] = removed
        remove = self.call(
            ["git", "-C", str(self.root), "worktree", "remove", "--force", str(self.worktree)],
            timeout=STEP_TIMEOUT,
        )
        summary["worktree_removed"] = remove.returncode == 0 and not self.worktree.exists()
        return summary

    def residue(self) -> dict[str, bool]:
        label = f"label=com.docker.compose.project={self.project}"
        return {
            kind: bool(self.output(["docker", *argv, "--filter", label]))
            for kind, argv in (
                ("containers", ["ps", "-aq"]),
                ("volumes", ["volume", "ls", "-q"]),
                ("networks", ["network", "ls", "-q"]),
            )
        }

    # Observation ----------------------------------------------------------------

    def url(self) -> str:
        path = self.state_dir / "classroom.url"
        value = path.read_text().strip() if path.is_file() else ""
        if not value.startswith("http://127.0.0.1:"):
            raise HarnessError("The launcher did not record a loopback classroom URL.")
        return value

    def digest(self, target: str) -> str:
        result = self.call(
            self.compose(
                "exec", "-T", "-u", LEARNER_USER, "lab", "python", "-c", DIGEST_CODE, target
            ),
            cwd=self.worktree,
            env=self.env,
        )
        if result.returncode:
            return "unavailable"
        value = result.stdout.strip()
        return value if value == "absent" or DIGEST_RE.fullmatch(value) else "invalid"

    def containers(self) -> dict[str, str]:
        rows = parse_json(self.compose_output("ps", "-a", "--format", "json"))
        return {str(row.get("Service")): str(row.get("ID")) for row in rows if row.get("Service")}

    def volumes(self) -> dict[str, str | None]:
        found: dict[str, str | None] = {}
        for volume in VOLUMES:
            result = self.call(
                [
                    "docker",
                    "volume",
                    "inspect",
                    "--format",
                    "{{.CreatedAt}}",
                    f"{self.project}_{volume}",
                ]
            )
            found[volume] = result.stdout.strip() if result.returncode == 0 else None
        return found

    def observe(self) -> dict[str, Any]:
        containers = self.containers()
        images = {
            service: self.output(
                ["docker", "inspect", "--format", "{{.Image}}", containers[service]]
            )
            for service in IMAGE_REPOSITORIES
            if service in containers
        }
        return {
            "url_port": self.url().rsplit(":", 1)[-1].split("/", 1)[0],
            "containers": containers,
            "images": images,
            "volumes": self.volumes(),
            "token_sha256": self.digest(TOKEN_VARIABLE),
            "learner_sha256_before_probe": self.learner_digests(),
        }

    def learner_digests(self) -> dict[str, str]:
        return {name: self.digest(path) for name, path in LEARNER_FILES.items()}

    def learner_readable(self, digests: Mapping[str, str]) -> bool:
        progress = digests.get("progress.json", "")
        return DIGEST_RE.fullmatch(digests.get("coaching.json", "")) is not None and (
            progress == "absent" or DIGEST_RE.fullmatch(progress) is not None
        )

    def probe(self, step: Step, *, persistence: bool) -> bool:
        argv = [
            sys.executable,
            str(self.root / "scripts" / "check_lab_http.py"),
            "--url",
            self.url(),
            "--confirm-disposable",
        ]
        if persistence:
            argv.append("--check-persistence")
        argv.extend(["--sql-sentinel", f"{self.sentinel_name}:{self.sentinel_token}"])
        label = "persistence-probe" if persistence else "seed-probe"
        result = self.logged(step, label, argv, env=self.env, timeout=PROBE_TIMEOUT)
        step.expect(label, result.returncode == 0, f"exit {result.returncode}")
        return result.returncode == 0

    # Transitions ----------------------------------------------------------------

    def start_args(self, tag: str) -> list[str]:
        args = ["--project", self.project]
        if self.options.profiles:
            for profile in self.options.profiles:
                args.extend(["--profile", profile])
        else:
            args.append("--starter")
        return [
            *args,
            "--local-build",
            "--tag",
            tag,
            "--port",
            "0",
            "--database-port",
            "0",
            "--no-browser",
            "--registry",
            "mirrors",
        ]

    def rerun_args(self) -> list[str]:
        return ["--project", self.project, "--no-browser"]

    def seed_tags(self, step: Step) -> bool:
        seed = self.options.seed_images or ""
        self.own_tag(self.tags["base"])
        for repository in IMAGE_REPOSITORIES.values():
            result = self.logged(
                step,
                "seed-tag",
                [
                    "docker",
                    "image",
                    "tag",
                    f"{repository}:{seed}",
                    f"{repository}:{self.tags['base']}",
                ],
            )
            step.expect(f"seed {repository}", result.returncode == 0)
        return step.verdict == "passed"

    def fresh(self, step: Step) -> bool:
        if self.options.seed_images and not self.seed_tags(step):
            return False
        self.own_tag(self.tags["base"])
        return self.launch(step, "up", ["up", *self.start_args(self.tags["base"])], BUILD_TIMEOUT)

    def stop(self, step: Step) -> bool:
        if not self.launch(step, "stop", ["stop", "--project", self.project], STEP_TIMEOUT):
            return False
        label = f"label=com.docker.compose.project={self.project}"
        running = self.output(["docker", "ps", "-q", "--filter", label])
        step.expect("no running containers", not running)
        volumes = self.volumes()
        step.expect("volumes retained", volumes == self.baseline["volumes"])
        step.observed["volumes"] = volumes
        return step.verdict == "passed"

    def resume(self, step: Step) -> bool:
        return self.launch(step, "resume", ["resume", *self.rerun_args()], STEP_TIMEOUT)

    def rerun(self, step: Step) -> bool:
        return self.launch(step, "rerun", self.rerun_args(), STEP_TIMEOUT)

    def restart(self, step: Step) -> bool:
        if not self.launch(step, "stop", ["stop", "--project", self.project], STEP_TIMEOUT):
            return False
        return self.launch(step, "start", self.rerun_args(), STEP_TIMEOUT)

    def recreate(self, step: Step) -> bool:
        self.check_owned()
        down = self.logged(
            step,
            "down",
            self.compose("down", "--remove-orphans"),
            cwd=self.worktree,
            env=self.env,
            timeout=STEP_TIMEOUT,
        )
        step.expect("down exit 0", down.returncode == 0)
        if down.returncode:
            return False
        return self.launch(step, "start", self.rerun_args(), STEP_TIMEOUT)

    def update(self, step: Step) -> bool:
        if self.options.seed_images:
            step.verdict = "skipped"
            step.observed["reason"] = (
                "Seeded images: an update needs a local --rebuild image build, "
                "which this run was asked not to perform."
            )
            return True
        checkout = self.logged(
            step,
            "checkout",
            ["git", "-C", str(self.worktree), "checkout", "--detach", self.target],
            timeout=STEP_TIMEOUT,
        )
        step.expect("checkout target", checkout.returncode == 0)
        if checkout.returncode:
            return False
        self.own_tag(self.tags["target"])
        args = ["--rebuild", *self.start_args(self.tags["target"])]
        return self.launch(step, "rebuild", args, BUILD_TIMEOUT)

    def verify(self, step: Step, previous: dict[str, Any] | None) -> None:
        state = self.observe()
        step.observed.update(state)
        if previous is None:
            self.baseline = state
        baseline = self.baseline
        step.expect(
            "token digest stable",
            DIGEST_RE.fullmatch(state["token_sha256"]) is not None
            and state["token_sha256"] == baseline["token_sha256"],
            "worker token digest missing or changed",
        )
        step.expect(
            "volumes retained",
            all(state["volumes"].values()) and state["volumes"] == baseline["volumes"],
            "a project volume is missing or was recreated",
        )
        if previous is not None:
            step.expect(
                "learner files unchanged by transition",
                state["learner_sha256_before_probe"] == previous["learner_sha256_after_probe"],
            )
            self.compare_containers(step, state, previous)
        if self.probe(step, persistence=previous is not None):
            step.observed["learner_sha256_after_probe"] = self.learner_digests()
            step.expect(
                "learner files readable",
                self.learner_readable(step.observed["learner_sha256_after_probe"]),
            )

    def compare_containers(
        self, step: Step, state: dict[str, Any], previous: dict[str, Any]
    ) -> None:
        if step.name == "recreate":
            step.expect(
                "containers recreated",
                state["containers"].get("postgres") != previous["containers"].get("postgres"),
            )
            return
        if step.name == "update":
            self.compare_images(step, state)
            return
        port_changed = state["url_port"] != previous["url_port"]
        for service, container in previous["containers"].items():
            if service == "classroom-init" or (service == "lab" and port_changed):
                continue
            step.expect(f"{service} container kept", state["containers"].get(service) == container)
        step.observed["lab_recreated_for_port"] = port_changed and (
            state["containers"].get("lab") != previous["containers"].get("lab")
        )

    def compare_images(self, step: Step, state: dict[str, Any]) -> None:
        fresh = self.baseline["images"]
        for service in IMAGE_REPOSITORIES:
            if self.base != self.target:
                step.expect(
                    f"image-changed {service}",
                    bool(state["images"].get(service))
                    and state["images"].get(service) != fresh.get(service),
                )
        label = self.call(
            [
                "docker",
                "image",
                "inspect",
                "--format",
                f'{{{{index .Config.Labels "{REVISION_LABEL}"}}}}',
                str(state["images"].get("lab", "")),
            ]
        )
        value = label.stdout.strip() if label.returncode == 0 else ""
        step.observed["revision_label"] = value if value and value != "<no value>" else "unlabeled"
        if step.observed["revision_label"] != "unlabeled":
            step.expect("revision label is target", value == self.target)

    def transitions(self) -> None:
        actions: dict[str, Callable[[Step], bool]] = {
            "fresh": self.fresh,
            "stop": self.stop,
            "resume": self.resume,
            "rerun": self.rerun,
            "restart": self.restart,
            "recreate": self.recreate,
            "update": self.update,
            "final-rerun": self.rerun,
        }
        previous: dict[str, Any] | None = None
        for name in self.steps_selected:
            step = Step(name)
            self.steps.append(step)
            try:
                if actions[name](step) and name != "stop" and step.verdict == "passed":
                    self.verify(step, previous)
                    previous = step.observed
            except HarnessError as exc:
                step.expect("harness", False, str(exc))
            if step.verdict == "failed":
                break

    # Entry point ----------------------------------------------------------------

    baseline: dict[str, Any]

    def write_report(self) -> None:
        self.report["steps"] = [step.report() for step in self.steps]
        text = json.dumps(self.report, indent=2, sort_keys=True) + "\n"
        if self.sentinel_token in text:
            raise HarnessError("Refusing to write a report containing the sentinel token.")
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(text)

    def run(self) -> int:
        try:
            self.guard()
        except HarnessError as exc:
            self.report["error"] = str(exc)
            self.write_report()
            print(f"Refused: {exc}", file=sys.stderr)
            return 2
        before = self.snapshot_protected()
        try:
            self.create_worktree()
            self.write_marker()
            self.transitions()
        except HarnessError as exc:
            self.report["error"] = str(exc)
        finally:
            if self.options.keep:
                self.report["cleanup"] = {"skipped": "--keep"}
            elif self.marker_written:
                try:
                    self.report["cleanup"] = self.cleanup()
                    self.report["residue"] = self.residue()
                except HarnessError as exc:
                    self.report["cleanup_error"] = str(exc)
            elif self.created_worktree:
                self.call(
                    [
                        "git",
                        "-C",
                        str(self.root),
                        "worktree",
                        "remove",
                        "--force",
                        str(self.worktree),
                    ]
                )
            after = self.snapshot_protected()
            self.report["protected"] = {
                "before": before,
                "after": after,
                **diff_protected(before, after),
            }
            self.finish()
        return 0 if self.report["passed"] else 1

    def finish(self) -> None:
        verdicts = [step.verdict for step in self.steps]
        cleanup = self.report.get("cleanup", {})
        clean = self.options.keep or (
            cleanup.get("worktree_removed") is True
            and not any(self.report.get("residue", {"left": True}).values())
        )
        self.report["passed"] = bool(
            verdicts
            and len(verdicts) == len(self.steps_selected)
            and all(verdict in {"passed", "skipped"} for verdict in verdicts)
            and "error" not in self.report
            and "cleanup_error" not in self.report
            and not self.report["protected"]["errors"]
            and clean
        )
        self.report["skipped_steps"] = [s.name for s in self.steps if s.verdict == "skipped"]
        self.write_report()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="A fresh ds60-p7-... Compose project.")
    parser.add_argument("--target", default="HEAD", help="Revision the update step moves to.")
    parser.add_argument("--base", help="Revision for the fresh setup (default: target~1).")
    parser.add_argument("--steps", default=",".join(STEPS), help="Comma list in canonical order.")
    parser.add_argument("--report", type=Path, help="JSON report path (default under work/).")
    parser.add_argument(
        "--profile", action="append", default=[], help="Repeatable; default starter."
    )
    parser.add_argument("--architecture", choices=("amd64", "arm64"))
    parser.add_argument("--keep", action="store_true", help="Skip cleanup for debugging.")
    parser.add_argument(
        "--seed-images",
        metavar="VERSION",
        help=(
            "Tag the existing local lab and python-core VERSION images as the base p7 tag "
            "instead of building; the update step is then skipped."
        ),
    )
    args = parser.parse_args(argv)
    options = Options(
        project=args.project,
        target=args.target,
        base=args.base,
        steps=tuple(item.strip() for item in args.steps.split(",") if item.strip()),
        report=args.report,
        keep=args.keep,
        seed_images=args.seed_images,
        profiles=tuple(args.profile),
        architecture=args.architecture,
    )
    try:
        harness = Lifecycle(options)
    except HarnessError as exc:
        print(f"Refused: {exc}", file=sys.stderr)
        return 2
    return harness.run()


if __name__ == "__main__":
    raise SystemExit(main())
