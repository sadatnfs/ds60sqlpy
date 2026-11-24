"""Exercise the disposable lifecycle harness against a fake Docker and git runner."""

from __future__ import annotations

import json
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest

from scripts import check_classroom_lifecycle as lifecycle

ROOT = Path(__file__).resolve().parents[1]
BASE = "1111aaaa" + "0" * 32
TARGET = "2222bbbb" + "0" * 32
TOKEN_DIGEST = "a" * 64
PROGRESS_DIGEST = "c" * 64
LEAKED = "LEAKED-WORKER-TOKEN-value"
SHARED = {
    "ds60sqlpy-lab:1.4.3": "sha256:" + "1" * 64,
    "ds60sqlpy-worker-python-core:1.4.3": "sha256:" + "2" * 64,
}
PROTECTED_VOLUMES = [
    "ds60-classroom_classroom-learning",
    "ds60-classroom_classroom-runtime",
    "ds60-classroom_postgres-data",
]
SERVICES = ("postgres", "classroom-init", "lab", "python-core-worker")


class FakeEngine:
    """A tiny stateful stand-in for git, Docker and the launcher."""

    def __init__(self, root: Path, project: str) -> None:
        self.root = root
        self.project = project
        self.worktree = root / "work" / "p7-worktrees" / project
        self.marker = self.worktree / ".classroom" / project / "p7-owner.json"
        self.calls: list[list[str]] = []
        self.images: dict[str, str] = dict(SHARED)
        self.preexisting: dict[str, str] = {}
        self.compose_projects: list[str] = []
        self.protected_volumes = list(PROTECTED_VOLUMES)
        self.remove_protected_volume_on_up = False
        self.change_shared_on_up = False
        self.token_output = TOKEN_DIGEST
        self.volumes = False
        self.running = False
        self.generation = 0
        self.port = 50000
        self.rebuilt_lab_id = "sha256:" + "9" * 64
        self.lab_image = "sha256:" + "1" * 64
        self.core_image = "sha256:" + "2" * 64
        self.marker_seen_at_down: list[bool] = []
        self.marker_seen_at_launch: list[bool] = []

    def __call__(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str] | None,
        timeout: float,
    ) -> lifecycle.Completed:
        command = list(argv)
        self.calls.append(command)
        return self.answer(command)

    def ok(self, stdout: str = "") -> lifecycle.Completed:
        return lifecycle.Completed(0, stdout, "")

    def answer(self, argv: list[str]) -> lifecycle.Completed:
        if argv[0] == "git":
            return self.git(argv)
        if argv[0] == "./classroom":
            return self.launch(argv)
        if argv[0] == sys.executable:
            return self.ok("PASS")
        if argv[:2] == ["docker", "compose"]:
            return self.compose(argv)
        return self.docker(argv)

    def git(self, argv: list[str]) -> lifecycle.Completed:
        if "rev-parse" in argv:
            return self.ok(BASE if "~1" in argv[-1] else TARGET)
        if "add" in argv:
            self.worktree.mkdir(parents=True)
        if "remove" in argv:
            shutil.rmtree(self.worktree)
        return self.ok()

    def launch(self, argv: list[str]) -> lifecycle.Completed:
        self.marker_seen_at_launch.append(self.marker.is_file())
        if "stop" in argv:
            self.running = False
            return self.ok()
        if "--rebuild" in argv:
            self.generation += 1
            if self.rebuilt_lab_id:
                self.lab_image = self.rebuilt_lab_id
                self.core_image = "sha256:" + "8" * 64
        if "--tag" in argv:
            tag = argv[argv.index("--tag") + 1]
            self.images.setdefault("ds60sqlpy-lab:" + tag, self.lab_image)
            self.images.setdefault("ds60sqlpy-worker-python-core:" + tag, self.core_image)
        if not self.running:
            self.port += 1
        self.running = True
        self.volumes = True
        if self.remove_protected_volume_on_up:
            self.protected_volumes.pop()
        if self.change_shared_on_up:
            self.images["ds60sqlpy-lab:1.4.3"] = "sha256:" + "f" * 64
        state = self.worktree / ".classroom" / self.project
        state.mkdir(parents=True, exist_ok=True)
        (state / "classroom.url").write_text(f"http://127.0.0.1:{self.port}/classroom\n")
        return self.ok()

    def compose(self, argv: list[str]) -> lifecycle.Completed:
        if argv[2:5] == ["ls", "-a", "--format"]:
            return self.ok(json.dumps([{"Name": name} for name in self.compose_projects]))
        if "down" in argv:
            self.marker_seen_at_down.append(self.marker.is_file())
            self.running = False
            self.generation += 1
            if "-v" in argv:
                self.volumes = False
            return self.ok()
        if "ps" in argv:
            rows = [
                {"Service": service, "ID": f"{service}-{self.generation}"} for service in SERVICES
            ]
            return self.ok("\n".join(json.dumps(row) for row in rows))
        if "exec" in argv:
            return self.ok(self.token_output if argv[-1].startswith("DS60_") else PROGRESS_DIGEST)
        return self.ok()

    def docker(self, argv: list[str]) -> lifecycle.Completed:
        joined = " ".join(argv)
        if argv[1] == "info":
            return self.ok("aarch64")
        if argv[1:3] == ["image", "inspect"]:
            if "Labels" in joined:
                return self.ok(TARGET)
            image = self.images.get(argv[-1])
            return self.ok(image) if image else lifecycle.Completed(1, "", "No such image")
        if argv[1:3] == ["image", "tag"]:
            self.images[argv[4]] = self.images[argv[3]]
            return self.ok()
        if argv[1:3] == ["image", "rm"]:
            self.images.pop(argv[3], None)
            return self.ok()
        if argv[1] == "inspect":
            return self.ok(self.lab_image if argv[-1].startswith("lab-") else self.core_image)
        if argv[1:3] == ["volume", "inspect"]:
            return self.ok("2026-11-23T00:00:00Z")
        if argv[1:3] == ["volume", "ls"]:
            if "--filter" in argv:
                found = self.preexisting.get("volume", "") or ("v" if self.volumes else "")
                return self.ok(found)
            return self.ok("\n".join([*self.protected_volumes, "unrelated_data"]))
        if argv[1:3] == ["network", "ls"]:
            return self.ok(self.preexisting.get("network", ""))
        if argv[1] == "ps":
            if "--format" in argv:
                return self.ok("tender_feistel\trunning\t\nds60-p7-other\trunning\tds60-p7-x\n")
            if "-aq" in argv:
                return self.ok(self.preexisting.get("container", ""))
            return self.ok("cid" if self.running else "")
        return self.ok()

    def commands(self, word: str) -> list[list[str]]:
        return [argv for argv in self.calls if word in argv]


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.4.3"\n')
    return tmp_path


def make(
    root: Path,
    project: str = "ds60-p7-unit-1",
    *,
    steps: Sequence[str] = lifecycle.STEPS,
    seed: str | None = None,
    base: str | None = None,
) -> tuple[lifecycle.Lifecycle, FakeEngine]:
    engine = FakeEngine(root, project)
    options = lifecycle.Options(project=project, steps=tuple(steps), seed_images=seed, base=base)
    return lifecycle.Lifecycle(options, runner=engine, root=root), engine


@pytest.mark.parametrize(
    "project",
    [
        "ds60-classroom",
        "ds60-phase1-browser",
        "ds60-p7-",
        "ds60-p7-UPPER",
        "ds60-ci-python-core-1",
        "ds60-p7-ds60-classroom",
        "ds60-p7-tender_feistel",
        "ds60-p7-awesome-copilot",
        "ds60-p7-" + "a" * 42,
        "awesome-copilot",
    ],
)
def test_refuses_non_disposable_or_protected_project_names(root: Path, project: str) -> None:
    engine = FakeEngine(root, project)
    with pytest.raises(lifecycle.HarnessError):
        lifecycle.Lifecycle(lifecycle.Options(project=project), runner=engine, root=root)
    assert engine.calls == []


def test_accepts_a_disposable_name() -> None:
    lifecycle.validate_project("ds60-p7-local-0a1b2c3d")


@pytest.mark.parametrize(
    "tag",
    ["1.4.3", "1.4.3-p7abc", "1.4.2-p7deadbeef", "1.4.3-p7DEADBEEF", "1.4.3-p7deadbeef0"],
)
def test_refuses_non_p7_or_wrong_version_tags(tag: str) -> None:
    with pytest.raises(lifecycle.HarnessError):
        lifecycle.validate_tag(tag, "1.4.3")
    lifecycle.validate_tag("1.4.3-p7deadbeef", "1.4.3")


@pytest.mark.parametrize("kind", ["container", "volume", "network", "compose"])
def test_refuses_project_that_already_has_resources(root: Path, kind: str) -> None:
    work, engine = make(root)
    if kind == "compose":
        engine.compose_projects.append("ds60-p7-unit-1")
    else:
        engine.preexisting[kind] = "abc123"
    assert work.run() == 2
    assert engine.commands("worktree") == []
    assert [argv for argv in engine.calls if argv[0] == "./classroom"] == []
    assert engine.commands("down") == []
    report = json.loads(work.report_path.read_text())
    assert report["passed"] is False and "already" in report["error"]


def test_refuses_when_a_p7_tag_already_exists(root: Path) -> None:
    work, engine = make(root)
    engine.images["ds60sqlpy-lab:1.4.3-p7" + BASE[:8]] = "sha256:" + "e" * 64
    assert work.run() == 2
    assert engine.commands("worktree") == []


def test_cleanup_refuses_missing_marker(root: Path) -> None:
    work, engine = make(root)
    with pytest.raises(lifecycle.HarnessError):
        work.cleanup()
    assert engine.commands("down") == []


@pytest.mark.parametrize("field", ["project", "run_id"])
def test_cleanup_refuses_foreign_marker(root: Path, field: str) -> None:
    work, engine = make(root)
    work.marker.parent.mkdir(parents=True)
    identity = {"project": work.project, "run_id": work.run_id}
    identity[field] = "someone-else"
    work.marker.write_text(json.dumps(identity))
    with pytest.raises(lifecycle.HarnessError):
        work.cleanup()
    assert engine.commands("down") == []
    assert engine.commands("rm") == []


def test_cleanup_with_owned_marker_uses_exact_order(root: Path) -> None:
    work, engine = make(root)
    work.worktree.mkdir(parents=True)
    work.marker.parent.mkdir(parents=True)
    work.marker.write_text(json.dumps({"project": work.project, "run_id": work.run_id}))
    work.owned_images = ["ds60sqlpy-lab:1.4.3-p7" + BASE[:8]]
    work.cleanup()
    down = [index for index, argv in enumerate(engine.calls) if "down" in argv]
    rm = [index for index, argv in enumerate(engine.calls) if argv[1:3] == ["image", "rm"]]
    remove = [index for index, argv in enumerate(engine.calls) if "remove" in argv]
    assert len(down) == 1 and len(rm) == 1 and len(remove) == 1
    assert down[0] < rm[0] < remove[0]
    command = engine.calls[down[0]]
    assert command[:2] == ["docker", "compose"]
    assert command[command.index("-p") + 1] == work.project
    assert command[-3:] == ["down", "-v", "--remove-orphans"]
    assert engine.calls[rm[0]] == ["docker", "image", "rm", "ds60sqlpy-lab:1.4.3-p7" + BASE[:8]]
    assert engine.calls[remove[0]][-3:] == ["remove", "--force", str(work.worktree)]


def snapshot(**changes: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "volumes": list(PROTECTED_VOLUMES),
        "images": dict(SHARED),
        "containers": {"tender_feistel": "running", "condescending_kirch": "exited"},
    }
    value.update(changes)
    return value


def test_snapshot_diff_rules() -> None:
    assert lifecycle.diff_protected(snapshot(), snapshot()) == {"errors": [], "warnings": []}
    removed = lifecycle.diff_protected(snapshot(), snapshot(volumes=PROTECTED_VOLUMES[:2]))
    assert len(removed["errors"]) == 1 and "ds60-classroom_postgres-data" in removed["errors"][0]
    changed = dict(SHARED, **{"ds60sqlpy-worker-python-core:1.4.3": "sha256:" + "3" * 64})
    image = lifecycle.diff_protected(snapshot(), snapshot(images=changed))
    assert len(image["errors"]) == 1 and "worker-python-core" in image["errors"][0]
    state = lifecycle.diff_protected(
        snapshot(),
        snapshot(containers={"tender_feistel": "exited", "condescending_kirch": "exited"}),
    )
    assert state["errors"] == [] and len(state["warnings"]) == 1


def test_source_never_mentions_bulk_removal() -> None:
    source = (ROOT / "scripts" / "check_classroom_lifecycle.py").read_text()
    assert "prune" not in source


def test_full_run_orders_steps_and_cleans_only_owned_resources(root: Path) -> None:
    work, engine = make(root)
    assert work.run() == 0
    report = json.loads(work.report_path.read_text())
    assert [step["name"] for step in report["steps"]] == list(lifecycle.STEPS)
    assert all(step["verdict"] == "passed" for step in report["steps"])
    assert report["passed"] is True and report["protected"]["errors"] == []
    assert all(engine.marker_seen_at_launch)
    assert engine.marker_seen_at_down == [True, True]
    volume_downs = [argv for argv in engine.commands("down") if "-v" in argv]
    assert len(volume_downs) == 1 and engine.calls.index(volume_downs[0]) > max(
        engine.calls.index(argv) for argv in engine.calls if argv[0] == "./classroom"
    )
    removed = sorted(argv[3] for argv in engine.calls if argv[1:3] == ["image", "rm"])
    assert removed == sorted(
        f"{repo}:1.4.3-p7{sha[:8]}"
        for repo in ("ds60sqlpy-lab", "ds60sqlpy-worker-python-core")
        for sha in (BASE, TARGET)
    )
    assert not work.worktree.exists()


def test_launcher_runs_inside_worktree_with_clean_environment(root: Path) -> None:
    calls: list[tuple[list[str], Path, Mapping[str, str] | None]] = []
    work, engine = make(root, steps=("fresh",))

    def recording(
        argv: Sequence[str], *, cwd: Path, env: Mapping[str, str] | None, timeout: float
    ) -> lifecycle.Completed:
        calls.append((list(argv), cwd, env))
        return engine(argv, cwd=cwd, env=env, timeout=timeout)

    work.runner = recording
    assert work.run() == 0
    launches = [(argv, cwd, env) for argv, cwd, env in calls if argv[0] == "./classroom"]
    assert launches and all(cwd == work.worktree for _, cwd, _ in launches)
    fresh = launches[0][0]
    for flag in ("--starter", "--local-build", "--no-browser"):
        assert flag in fresh
    assert fresh[fresh.index("--tag") + 1] == "1.4.3-p7" + BASE[:8]
    assert fresh[fresh.index("--port") + 1] == "0"
    assert fresh[fresh.index("--database-port") + 1] == "0"
    env = launches[0][2]
    assert env is not None and env["COMPOSE_PROJECT_NAME"] == work.project
    assert "GH_TOKEN" not in env


def test_recreate_keeps_volumes(root: Path) -> None:
    work, engine = make(root)
    assert work.run() == 0
    recreate = [argv for argv in engine.commands("down") if "-v" not in argv]
    assert len(recreate) == 1
    assert "--volumes" not in recreate[0] and recreate[0][-2:] == ["down", "--remove-orphans"]
    assert recreate[0][recreate[0].index("-p") + 1] == work.project


def test_rerun_reuses_saved_selection(root: Path) -> None:
    work, engine = make(root)
    assert work.run() == 0
    launches = [argv for argv in engine.calls if argv[0] == "./classroom"]
    reruns = [argv for argv in launches if argv[1:] == ["--project", work.project, "--no-browser"]]
    assert len(reruns) == 4  # rerun, restart, recreate and final-rerun
    resume = [argv for argv in launches if "resume" in argv]
    assert resume == [["./classroom", "resume", "--project", work.project, "--no-browser"]]


def test_update_fails_when_image_ids_do_not_change(root: Path) -> None:
    work, engine = make(root)
    engine.rebuilt_lab_id = ""
    assert work.run() == 1
    report = json.loads(work.report_path.read_text())
    update = next(step for step in report["steps"] if step["name"] == "update")
    assert update["verdict"] == "failed"
    assert any(
        key.startswith("image-changed")
        for key, value in update["checks"].items()
        if value != "pass"
    )
    assert engine.marker_seen_at_down[-1] is True
    assert not work.worktree.exists()


def test_update_checks_out_target_and_rebuilds_with_target_tag(root: Path) -> None:
    work, engine = make(root)
    assert work.run() == 0
    checkout = [argv for argv in engine.calls if "checkout" in argv]
    assert checkout and checkout[0][-1] == TARGET
    rebuild = [argv for argv in engine.calls if "--rebuild" in argv]
    assert (
        len(rebuild) == 1 and rebuild[0][rebuild[0].index("--tag") + 1] == "1.4.3-p7" + TARGET[:8]
    )
    report = json.loads(work.report_path.read_text())
    update = next(step for step in report["steps"] if step["name"] == "update")
    assert update["revision_label"] == TARGET


def test_seeded_mode_tags_existing_images_and_skips_rebuild(root: Path) -> None:
    work, engine = make(root, seed="1.4.3")
    assert work.run() == 0
    tags = [argv for argv in engine.calls if argv[1:3] == ["image", "tag"]]
    assert sorted(argv[4] for argv in tags) == sorted(
        f"{repo}:1.4.3-p7{BASE[:8]}" for repo in ("ds60sqlpy-lab", "ds60sqlpy-worker-python-core")
    )
    assert [argv for argv in engine.calls if "--rebuild" in argv] == []
    report = json.loads(work.report_path.read_text())
    update = next(step for step in report["steps"] if step["name"] == "update")
    assert update["verdict"] == "skipped"
    assert {ref: engine.images[ref] for ref in SHARED} == SHARED


def test_report_has_digests_only(root: Path) -> None:
    work, engine = make(root)
    engine.token_output = LEAKED
    assert work.run() == 1
    text = work.report_path.read_text()
    assert LEAKED not in text
    assert work.sentinel_token not in text
    report = json.loads(text)
    assert report["sentinel"]["name"] == work.sentinel_name
    assert len(report["sentinel"]["token_sha256"]) == 64
    execs = engine.commands("exec")
    assert execs and all(argv[argv.index("-u") + 1] == "1000:1000" for argv in execs)
    probes = [argv for argv in engine.calls if argv[0] == sys.executable]
    assert probes and all("--sql-sentinel" in argv for argv in probes)
    assert "--check-persistence" not in probes[0]
    assert all("--check-persistence" in argv for argv in probes[1:])


def test_learner_files_accept_absent_progress_but_require_coaching(root: Path) -> None:
    work, _ = make(root)
    assert work.learner_readable({"progress.json": "absent", "coaching.json": "c" * 64})
    assert work.learner_readable({"progress.json": "d" * 64, "coaching.json": "c" * 64})
    assert not work.learner_readable({"progress.json": "d" * 64, "coaching.json": "absent"})
    assert not work.learner_readable({"progress.json": "invalid", "coaching.json": "c" * 64})


def test_protected_volume_loss_fails_the_run(root: Path) -> None:
    work, engine = make(root, steps=("fresh",))
    engine.remove_protected_volume_on_up = True
    assert work.run() == 1
    report = json.loads(work.report_path.read_text())
    assert report["protected"]["errors"]


def test_shared_image_change_fails_the_run(root: Path) -> None:
    work, engine = make(root, steps=("fresh",))
    engine.change_shared_on_up = True
    assert work.run() == 1


def test_steps_must_start_with_fresh_and_follow_order(root: Path) -> None:
    for steps in (("stop",), ("fresh", "resume", "stop"), ("fresh", "bogus")):
        with pytest.raises(lifecycle.HarnessError):
            make(root, steps=steps)
