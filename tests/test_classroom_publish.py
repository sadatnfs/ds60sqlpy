"""Run the publisher through a fake Docker boundary, never an actual registry."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERSION = "7.8.9"
ROWS = (
    "app lab ds60sqlpy-lab lab DS60_LAB_IMAGE app",
    "python-core python-core-worker ds60sqlpy-worker-python-core worker-python-core "
    "DS60_WORKER_PYTHON_CORE_IMAGE ordinary",
    "java21 java-worker ds60sqlpy-worker-java21 worker-java21 DS60_WORKER_JAVA21_IMAGE ordinary",
    "cuda-python cuda-worker ds60sqlpy-worker-cuda-python worker-cuda-python "
    "DS60_WORKER_CUDA_PYTHON_IMAGE gpu",
)
SOURCES = [f"{row.split()[2]}:{VERSION}" for row in ROWS[:3]]


def image_id(source: str) -> str:
    return "sha256:" + hashlib.sha256(source.encode()).hexdigest()


@dataclass
class Publisher:
    root: Path
    tools: Path
    home: Path
    settings: Path
    log: Path
    environment: dict[str, str]

    def configure(self, **values: Any) -> None:
        self.settings.write_text(json.dumps(values))

    def run(
        self, *arguments: str, legacy: bool = False, environment: dict[str, str] | None = None
    ) -> tuple[subprocess.CompletedProcess[str], list[list[str]]]:
        self.log.unlink(missing_ok=True)
        script = self.root / ("scripts/publish-images" if legacy else "classroom")
        args = list(arguments) if legacy else ["publish", *arguments]
        result = subprocess.run(
            ["/bin/bash", str(script), *args],
            cwd=self.root.parent,
            env={**self.environment, **(environment or {})},
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        calls = (
            [json.loads(line) for line in self.log.read_text().splitlines()]
            if self.log.exists()
            else []
        )
        return result, calls


@pytest.fixture
def publisher(tmp_path: Path) -> Publisher:
    if not Path("/bin/bash").is_file():
        pytest.skip("The supported Bash entrypoint runs on Linux, macOS and WSL 2")
    root = tmp_path / "classroom checkout with spaces"
    (root / "scripts").mkdir(parents=True)
    (root / "docker").mkdir()
    for name in ("classroom", "scripts/classroom.sh", "scripts/publish-images"):
        shutil.copyfile(ROOT / name, root / name)
    # Deliberately omit Compose and classroom_images.sh: publication must dispatch
    # before the startup subsystem is sourced or any project state is inspected.
    (root / "pyproject.toml").write_text(
        '[tool.example]\nversion = "0.0.1"\n\n[project]\nversion = "7.8.9"\n'
    )
    (root / "docker/classroom-images.tsv").write_text("\n".join(ROWS) + "\n")
    home, tools = tmp_path / "publisher home", tmp_path / "tools"
    home.mkdir()
    tools.mkdir()
    settings, log = tmp_path / "settings.json", tmp_path / "docker.jsonl"
    settings.write_text("{}")
    executable = tools / "docker"
    executable.write_text(
        f"#!{sys.executable}\n"
        + """import hashlib,json,os,sys
from pathlib import Path
args=sys.argv[1:]
config=json.loads(Path(os.environ['PUBLICATION_SETTINGS']).read_text())
with Path(os.environ['PUBLICATION_CALLS']).open('a') as stream:
    stream.write(json.dumps(args)+'\\n')
if args[:2]==['image','inspect']:
    source=args[-1]
    if source in config.get('missing',[]):sys.exit(4)
    if source in config.get('raw',{}):print(config['raw'][source]);sys.exit(0)
    os_name,arch=config.get('platforms',{}).get(source,['linux','arm64'])
    identity='sha256:'+hashlib.sha256(source.encode()).hexdigest()
    print(os_name,arch,identity)
elif args[:2]==['image','tag']:
    assert args[2].startswith('sha256:'), 'A source tag is mutable'
    if config.get('fail_tag'):sys.exit(7)
elif args[:2]==['image','push']:
    if config.get('fail_push'):sys.exit(8)
else:
    raise SystemExit('Unexpected Docker operation: '+repr(args))
""",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    environment = {
        k: v for k, v in os.environ.items() if not k.startswith(("DOCKER_", "COMPOSE_", "DS60_"))
    }
    environment.update(
        PATH=str(tools) + os.pathsep + environment.get("PATH", ""),
        HOME=str(home),
        PUBLICATION_SETTINGS=str(settings),
        PUBLICATION_CALLS=str(log),
    )
    return Publisher(root, tools, home, settings, log, environment)


def mutations(calls: list[list[str]]) -> list[list[str]]:
    return [call for call in calls if call[:2] in (["image", "tag"], ["image", "push"])]


def test_default_public_command_previews_complete_catalog_and_leaves_state_untouched(
    publisher: Publisher,
) -> None:
    state = publisher.root / ".classroom/study/images.env"
    state.parent.mkdir(parents=True)
    state.write_text("INVALID_STARTUP_CONFIG_THAT_PUBLISH_MUST_NOT_READ\n")
    (publisher.root / ".env").write_text("INVALID_COMPOSE_SETTING\n")
    before = state.read_bytes()
    result, calls = publisher.run("--to-hub", "exampleuser")
    assert result.returncode == 0, result.stderr
    assert [call[-1] for call in calls] == SOURCES
    assert all(call[:2] == ["image", "inspect"] for call in calls)
    assert "Preview only. 3 Linux arm64 images" in result.stdout
    assert f"exampleuser/ds60sqlpy:{VERSION}-lab-arm64" in result.stdout
    assert "0.0.1" not in result.stdout and "cuda" not in result.stdout
    assert state.read_bytes() == before
    assert not (publisher.root / "injected").exists()
    assert not mutations(calls)


def test_explicit_all_is_the_same_preview_and_version_aliases_remain_compatible(
    publisher: Publisher,
) -> None:
    modern, modern_calls = publisher.run("--to-hub", "exampleuser", "--tag", VERSION, "--all")
    legacy, legacy_calls = publisher.run(
        "--namespace", "exampleuser", "--version", VERSION, legacy=True
    )
    assert modern.returncode == legacy.returncode == 0
    assert modern.stdout == legacy.stdout
    assert modern_calls == legacy_calls


def test_repeated_exact_profiles_are_deduplicated_in_catalog_order(publisher: Publisher) -> None:
    result, calls = publisher.run(
        "--to-hub", "exampleuser", "--profile", "java21", "--profile", "app", "--profile", "java21"
    )
    assert result.returncode == 0
    assert [call[-1] for call in calls] == [SOURCES[0], SOURCES[2]]
    assert "Preview only. 2" in result.stdout
    assert "worker-python-core" not in result.stdout


@pytest.mark.parametrize("index", [0, 1, 2])
def test_any_missing_selected_image_prevents_all_tags_and_pushes(
    publisher: Publisher, index: int
) -> None:
    publisher.configure(missing=[SOURCES[index]])
    result, calls = publisher.run("--to-hub", "exampleuser", "--push")
    assert result.returncode != 0
    assert "Nothing has been pushed or tagged" in result.stderr
    assert not mutations(calls)
    assert " -> " not in result.stdout  # Never present a partial plan as a complete preview.


@pytest.mark.parametrize("platform", [("windows", "arm64"), ("linux", "amd64"), ("linux", "arm")])
def test_wrong_or_mixed_platform_fails_complete_preflight(
    publisher: Publisher, platform: tuple[str, str]
) -> None:
    publisher.configure(platforms={SOURCES[-1]: platform})
    result, calls = publisher.run("--to-hub", "exampleuser", "--push")
    assert result.returncode != 0 and not mutations(calls)
    assert len(calls) == 3


@pytest.mark.parametrize(
    "output",
    [
        "linux arm64 mutable-name",
        "linux arm64 sha256:" + "a" * 64 + " extra",
        "linux arm64 sha256:" + "a" * 64 + "\nlinux amd64 sha256:" + "b" * 64,
    ],
)
def test_malformed_inspection_never_reaches_tagging(publisher: Publisher, output: str) -> None:
    publisher.configure(raw={SOURCES[-1]: output})
    result, calls = publisher.run("--to-hub", "exampleuser", "--push")
    assert result.returncode != 0 and not mutations(calls)


def test_push_uses_only_inspected_ids_after_every_selected_image_passes(
    publisher: Publisher,
) -> None:
    result, calls = publisher.run("--to-hub", "exampleuser", "--push")
    assert result.returncode == 0, result.stderr
    assert all(call[:2] == ["image", "inspect"] for call in calls[:3])
    assert [call[:2] for call in calls[3:]] == [["image", "tag"], ["image", "push"]] * 3
    tags = calls[3::2]
    assert [call[2] for call in tags] == [image_id(source) for source in SOURCES]
    assert [call[3] for call in tags] == [
        f"exampleuser/ds60sqlpy:{VERSION}-lab-arm64",
        f"exampleuser/ds60sqlpy:{VERSION}-worker-python-core-arm64",
        f"exampleuser/ds60sqlpy:{VERSION}-worker-java21-arm64",
    ]
    assert (
        f"./classroom --all --from-hub exampleuser --tag {VERSION} --architecture-tags"
        in result.stdout
    )


def test_push_failure_stops_without_retrying_or_claiming_no_upload(publisher: Publisher) -> None:
    publisher.configure(fail_push=True)
    result, calls = publisher.run("--to-hub", "exampleuser", "--push")
    assert result.returncode != 0
    assert [call[:2] for call in mutations(calls)] == [["image", "tag"], ["image", "push"]]
    assert "Uploads may have completed" in result.stderr
    assert "Published the checked" not in result.stdout


def test_partial_publication_does_not_claim_a_complete_release_is_available(
    publisher: Publisher,
) -> None:
    result, calls = publisher.run("--to-hub", "exampleuser", "--profile", "java21", "--push")
    assert result.returncode == 0
    assert len(mutations(calls)) == 2
    assert "selected subset" in result.stdout
    assert "Install the complete release" not in result.stdout


@pytest.mark.parametrize(
    "arguments",
    [
        ("--all", "--profile", "app"),
        ("--profile", "app", "--all"),
        ("--tag", VERSION, "--version", VERSION),
        ("--namespace", "anotheruser"),
        ("--tag", "1.0.0"),
        ("--tag", "latest"),
        ("--profile", "cuda-python"),
        ("--profile", "unknown"),
        ("--profile",),
        ("--tag", "--push"),
        ("--from-hub", "exampleuser"),
        ("--no-build",),
        ("--rebuild",),
        ("--login",),
        ("--password=DO_NOT_ECHO_THIS_VALUE",),
    ],
)
def test_invalid_or_conflicting_publication_flags_fail_before_docker(
    publisher: Publisher, arguments: tuple[str, ...]
) -> None:
    result, calls = publisher.run("--to-hub", "exampleuser", *arguments, "--push")
    assert result.returncode != 0
    assert not calls
    assert "DO_NOT_ECHO_THIS_VALUE" not in result.stdout + result.stderr
    assert not (publisher.root / ".classroom").exists()


@pytest.mark.parametrize(
    "catalog",
    [
        "\n".join(ROWS + (ROWS[1],)),
        "\n".join(ROWS).replace(
            "worker-java21 DS60_WORKER_JAVA21_IMAGE", "lab DS60_WORKER_JAVA21_IMAGE"
        ),
        "\n".join(ROWS).replace(" ordinary", " unregistered", 1),
        "\n".join(ROWS) + "\nbroken row\n",
        "\n".join(ROWS[1:]),
    ],
)
def test_catalog_ambiguity_or_missing_app_fails_before_docker(
    publisher: Publisher, catalog: str
) -> None:
    (publisher.root / "docker/classroom-images.tsv").write_text(catalog)
    result, calls = publisher.run("--to-hub", "exampleuser", "--push")
    assert result.returncode != 0 and not calls


def test_release_is_derived_from_project_table_not_a_literal_or_other_section(
    publisher: Publisher,
) -> None:
    path = publisher.root / "pyproject.toml"
    path.write_text("[tool.unrelated]\nversion = '0.0.1'\n[project]\nversion = '8.9.10'\n")
    result, calls = publisher.run("--to-hub", "exampleuser", "--profile", "app")
    assert result.returncode == 0, result.stderr
    assert calls[0][-1] == "ds60sqlpy-lab:8.9.10"
    assert "8.9.10-lab-arm64" in result.stdout


def test_help_does_not_need_docker_or_checkout_configuration(publisher: Publisher) -> None:
    (publisher.root / "pyproject.toml").unlink()
    result, calls = publisher.run("--help")
    assert result.returncode == 0 and not calls
    assert "--to-hub" in result.stdout and "--namespace" in result.stdout
    assert "--all" in result.stdout and "--profile" in result.stdout


def test_rancher_fallback_works_without_docker_in_path(publisher: Publisher) -> None:
    local_tools = publisher.root.parent / "minimal path"
    local_tools.mkdir()
    for name in ("bash", "dirname", "awk"):
        found = shutil.which(name)
        assert found is not None
        (local_tools / name).symlink_to(found)
    fallback = publisher.home / ".rd/bin/docker"
    fallback.parent.mkdir(parents=True)
    shutil.copyfile(publisher.tools / "docker", fallback)
    fallback.chmod(0o755)
    result, calls = publisher.run(
        "--to-hub", "exampleuser", "--profile", "app", environment={"PATH": str(local_tools)}
    )
    assert result.returncode == 0, result.stderr
    assert len(calls) == 1 and calls[0][-1] == SOURCES[0]


def test_overlong_destination_tag_is_rejected_before_any_publication(publisher: Publisher) -> None:
    version = "7.8.9-" + "a" * 103
    (publisher.root / "pyproject.toml").write_text(f'[project]\nversion = "{version}"\n')
    result, calls = publisher.run("--to-hub", "exampleuser", "--push")
    assert result.returncode != 0
    assert "tag exceeds Docker limits" in result.stderr
    assert not mutations(calls)


@pytest.mark.parametrize("relative", ["pyproject.toml", "docker/classroom-images.tsv"])
def test_release_metadata_and_catalog_symlinks_are_not_followed(
    publisher: Publisher, relative: str
) -> None:
    path = publisher.root / relative
    retained = publisher.root.parent / "retained-publication-input"
    original = path.read_bytes()
    path.rename(retained)
    path.symlink_to(retained)
    result, calls = publisher.run("--to-hub", "exampleuser", "--push")
    assert result.returncode != 0 and not calls
    assert retained.read_bytes() == original
