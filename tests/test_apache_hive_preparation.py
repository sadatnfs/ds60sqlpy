"""Hive preparation policy and canonical identity tests; these do not simulate Hive."""

from __future__ import annotations

import hashlib
import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

BASE = Path(__file__).resolve().parents[1] / "courses/apache-data-platforms/projects/hive"
HIVE = "ds60-apache-hive-upstream:4.2.1"
JAVA = "ds60sqlpy-worker-java21:1.0.0"
HIVE_ID = "sha256:" + "1" * 64
JAVA_ID = "sha256:" + "2" * 64

FAKE_DOCKER = r"""
import json,os,runpy,sys
from pathlib import Path
root=Path(os.environ['FIXTURE_ROOT'])
state_file=root/'docker-state.json'
state=json.loads(state_file.read_text()) if state_file.exists() else {'containers':{},'calls':[]}
a=sys.argv[1:]
state['calls'].append({'args':a,'platform':os.environ.get('DOCKER_DEFAULT_PLATFORM')})
def save(): state_file.write_text(json.dumps(state))
def finish(code=0): save(); raise SystemExit(code)
def value(flag): return a[a.index(flag)+1]
hive='sha256:'+'1'*64
java='sha256:'+'2'*64
mode=os.environ.get('FIXTURE_MODE','normal')
if a[:2]==['context','inspect']: print('unix:///fixture/docker.sock')
elif a[:2]==['info','--format']: print('linux|aarch64')
elif a[:2]==['image','inspect']:
    selected=a[-1]; fmt=value('--format')
    if '.Architecture' in fmt:
        print('linux|amd64' if selected==os.environ.get('WRONG_IMAGE') else 'linux|arm64')
    elif 'Volumes' in fmt: print('null')
    elif '.Id' in fmt: print(hive if 'hive-upstream' in selected else java)
    else: finish(99)
elif a[0]=='create':
    labels=dict(a[i+1].split('=',1) for i,x in enumerate(a) if x=='--label')
    role=labels['org.ds60.workshop.role']
    ident={'classpath':'a','compiler':'b','verifier':'c'}[role]*64
    mounts=[a[i+1] for i,x in enumerate(a) if x=='--mount']
    matches=[x for x in mounts if 'target=/prepared' in x]
    prepared=matches[0].split('source=',1)[1].split(',',1)[0] if matches else ''
    state['containers'][ident]={'role':role,'owner':labels['org.ds60.workshop.owner'],'status':'created','prepared':prepared}
    print(ident)
elif a[0]=='cp':
    if mode=='copy-failure': finish(33)
    Path(a[-1]).mkdir()
elif a[0]=='start':
    item=state['containers'][a[-1]]
    item['status']='running'
    if mode in ['interrupted-compiler','unknown-compiler']:
        if mode=='unknown-compiler': item['status']='removing'
        finish(130)
    scope=runpy.run_path(str(root/'prepare_metadata.py'))
    prepared=Path(item['prepared'])
    if item['role']=='compiler':
        (prepared/'classes').mkdir()
        (prepared/'classes/MetadataProbe.class').write_bytes(b'fixture-class-not-runtime-evidence')
        values={'schema_version':'1','hive_image_id':hive,'java_image_id':java,'source_sha256':scope['checksum'](root/'MetadataProbe.java'),'class_sha256':scope['checksum'](prepared/'classes/MetadataProbe.class')}
        (prepared/'identity.tsv').write_bytes(scope['manifest_bytes'](values))
    try: scope['prepare'](prepared,root/'MetadataProbe.java',hive,java,'verify')
    except ValueError: item['status']='exited'; finish(9)
    item['status']='exited'
elif a[:2]==['ps','-aq']:
    for ident,item in state['containers'].items(): print(ident)
elif a[:2] in [['network','ls'],['volume','ls']]: pass
elif a[0]=='inspect':
    item=state['containers'][a[-1]]
    fmt=value('--format')
    if '.ExitCode' in fmt: print(0)
    else:
        image=hive if item['role']=='classpath' else java
        fields=[item['owner'],'apache-hive-preparation',item['role'],image,item['status']]
        print('|'.join(fields))
elif a[0]=='stop': state['containers'][a[-1]]['status']='exited'
elif a[0]=='rm': del state['containers'][a[-1]]
elif a[0]=='compose':
    keys=['DS60_WORKSHOP_OWNER','DS60_WORKSHOP_PROJECT','DS60_HIVE_IMAGE','DS60_PLATFORM_IMAGE','DS60_POSTGRES_IMAGE','DOCKER_DEFAULT_PLATFORM']
    (root/'compose-env.json').write_text(json.dumps({key:os.environ.get(key) for key in keys}))
else: finish(99)
finish()
"""


@pytest.fixture
def owned(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    project = tmp_path / "project"
    shutil.copytree(
        BASE, project, ignore=shutil.ignore_patterns(".env", ".workshop*", "__pycache__")
    )
    tools = tmp_path / "tools"
    tools.mkdir()
    docker = tools / "docker"
    docker.write_text(f"#!{sys.executable}\n" + FAKE_DOCKER)
    docker.chmod(0o755)
    env = os.environ | {
        "PATH": str(tools) + os.pathsep + os.environ["PATH"],
        "FIXTURE_ROOT": str(project),
        "DOCKER_CONTEXT": "",
        "DOCKER_HOST": "unix:///fixture/docker.sock",
        "DOCKER_DEFAULT_PLATFORM": "linux/amd64",
    }
    return project, env


def helper(owned: tuple[Path, dict[str, str]], **extra: str) -> subprocess.CompletedProcess[str]:
    root, env = owned
    return subprocess.run(
        ["bash", "prepare-metadata.sh", HIVE, JAVA],
        cwd=root,
        env=env | extra,
        capture_output=True,
        text=True,
        timeout=15,
    )


def state(root: Path) -> dict[str, Any]:
    result: dict[str, Any] = json.loads((root / "docker-state.json").read_text())
    return result


def test_hive_preparation_serializes_against_normal_workshop_actions(owned: Any) -> None:
    root, env = owned
    lock = root / ".workshop-lock"
    lock.mkdir()
    (lock / "pid").write_text("retained-owner")
    result = subprocess.run(
        ["bash", "run.sh", "prepare"], cwd=root, env=env, capture_output=True, text=True, timeout=5
    )
    assert result.returncode == 2 and "Another workshop action" in result.stderr
    assert (lock / "pid").read_text() == "retained-owner"
    assert not (root / "docker-state.json").exists()


def test_hive_metadata_second_preparation_cannot_steal_lock(owned: Any) -> None:
    root, _ = owned
    lock = root / ".workshop/preparation-lock"
    lock.mkdir(parents=True)
    (lock / "pid").write_text("retained-owner")
    result = helper(owned)
    assert result.returncode == 2 and "already locked" in result.stderr
    assert (lock / "pid").read_text() == "retained-owner"
    assert not any(call["args"][0] == "create" for call in state(root)["calls"])


def test_accepted_hive_class_cannot_hide_uncertain_preparation(owned: Any) -> None:
    root, _ = owned
    (root / ".workshop/metadata-client").mkdir(parents=True)
    marker = root / ".workshop/preparation.owner"
    marker.write_text("retained-unknown-owner")
    result = helper(owned)
    assert result.returncode == 2 and "reconciliation" in result.stderr
    assert marker.read_text() == "retained-unknown-owner"
    assert not any(call["args"][0] == "create" for call in state(root)["calls"])


@pytest.mark.parametrize("wrong", [HIVE, JAVA])
def test_hive_native_helper_rejects_wrong_architecture_before_state(owned: Any, wrong: str) -> None:
    root, _ = owned
    result = helper(owned, WRONG_IMAGE=wrong)
    assert result.returncode == 2 and "emulation is disabled" in result.stderr
    assert not (root / ".workshop").exists()
    assert not any(call["args"][0] == "create" for call in state(root)["calls"])


def test_hive_completed_preparation_reuses_verified_class_without_compiling(owned: Any) -> None:
    root, _ = owned
    assert helper(owned).returncode == 0
    accepted = root / ".workshop/metadata-client"
    before = {
        str(p.relative_to(accepted)): p.read_bytes() for p in accepted.rglob("*") if p.is_file()
    }
    assert set(before) == {"identity.tsv", "classes/MetadataProbe.class"}
    assert helper(owned).returncode == 0
    assert before == {
        str(p.relative_to(accepted)): p.read_bytes() for p in accepted.rglob("*") if p.is_file()
    }
    calls = state(root)["calls"]
    assert sum("org.ds60.workshop.role=compiler" in c["args"] for c in calls) == 1
    assert sum("org.ds60.workshop.role=verifier" in c["args"] for c in calls) == 1
    assert not state(root)["containers"]
    assert not (root / ".workshop/preparation.owner").exists()
    assert not (root / ".workshop/preparation-lock").exists()
    assert all(c["platform"] is None for c in calls)
    for call in calls:
        if call["args"][0] == "create" and "--user" in call["args"]:
            assert call["args"][call["args"].index("--user") + 1] == f"{os.getuid()}:{os.getgid()}"


@pytest.mark.parametrize("mode", ["copy-failure", "interrupted-compiler"])
def test_hive_known_failed_preparation_reaps_only_owned_resources(owned: Any, mode: str) -> None:
    root, _ = owned
    result = helper(owned, FIXTURE_MODE=mode)
    assert result.returncode != 0
    assert not state(root)["containers"]
    assert not (root / ".workshop/preparation.owner").exists()
    assert not list((root / ".workshop").glob("metadata-build-*"))
    assert not (root / ".workshop/metadata-client").exists()
    if mode == "interrupted-compiler":
        assert any(c["args"][:3] == ["stop", "--time", "10"] for c in state(root)["calls"])


def test_hive_unknown_compiler_state_retains_owner_and_never_replays(owned: Any) -> None:
    root, _ = owned
    result = helper(owned, FIXTURE_MODE="unknown-compiler")
    assert result.returncode == 2 and "uncertain" in result.stderr
    marker = root / ".workshop/preparation.owner"
    original = marker.read_bytes()
    assert state(root)["containers"] and list((root / ".workshop").glob("metadata-build-*"))
    creates = sum(c["args"][0] == "create" for c in state(root)["calls"])
    retry = helper(owned)
    assert retry.returncode == 2 and marker.read_bytes() == original
    assert sum(c["args"][0] == "create" for c in state(root)["calls"]) == creates


def test_hive_verification_rejects_changed_canonical_identity_without_replacement(
    owned: Any,
) -> None:
    root, _ = owned
    assert helper(owned).returncode == 0
    manifest = root / ".workshop/metadata-client/identity.tsv"
    altered = manifest.read_bytes().replace(HIVE_ID.encode(), ("sha256:" + "9" * 64).encode())
    manifest.write_bytes(altered)
    result = helper(owned)
    assert result.returncode != 0 and manifest.read_bytes() == altered
    assert not state(root)["containers"]
    assert sum("org.ds60.workshop.role=compiler" in c["args"] for c in state(root)["calls"]) == 1


def test_hive_compilation_uses_release21_and_refuses_extra_classes(
    tmp_path: Path, monkeypatch: Any
) -> None:
    scope = runpy.run_path(str(BASE / "prepare_metadata.py"))
    root = tmp_path / "prepared"
    root.mkdir()
    source = tmp_path / "MetadataProbe.java"
    source.write_text("fixture")

    for name in scope["SDK_JARS"]:
        jar = root / name
        jar.parent.mkdir(parents=True, exist_ok=True)
        jar.write_bytes(b"bounded-sdk-fixture")

    def compile_fixture(args: list[str], **kwargs: Any) -> None:
        assert args[:3] == ["javac", "--release", "21"] and kwargs["timeout"] == 90
        assert "-proc:none" in args and "*" not in args[args.index("-cp") + 1]
        (root / "classes/MetadataProbe.class").write_bytes(b"bounded-test-class")

    monkeypatch.setattr(scope["subprocess"], "run", compile_fixture)
    result = scope["prepare"](root, source, HIVE_ID, JAVA_ID, "compile")
    assert result["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    (root / "classes/Unexpected.class").write_bytes(b"other")
    with pytest.raises(ValueError, match="inventory"):
        scope["verify"](root, source, HIVE_ID, JAVA_ID)


def test_hive_runtime_uses_canonical_manifest_and_rejects_changed_source(
    owned: Any, tmp_path: Path
) -> None:
    root, env = owned
    assert helper(owned).returncode == 0
    sha = tmp_path / "tools/sha256sum"
    sha.write_text(
        f"#!{sys.executable}\n"
        "import sys,hashlib\nfrom pathlib import Path\n"
        "p=Path(sys.argv[1])\n"
        'print(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+str(p))\n'
    )
    sha.chmod(0o755)
    command = ["bash", "verify-metadata.sh", str(root), HIVE_ID]
    assert (
        subprocess.run(command, cwd=root, env=env, capture_output=True, timeout=5).returncode == 0
    )
    (root / "MetadataProbe.java").write_text("changed source")
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, timeout=5)
    assert result.returncode != 0 and "identity differs" in result.stderr


def test_hive_compose_pins_saved_values_and_clears_platform_override(owned: Any) -> None:
    root, env = owned
    owner = "f" * 32
    saved = {
        "DS60_WORKSHOP_OWNER": owner,
        "DS60_WORKSHOP_PROJECT": "ds60-apache-hive-" + owner[:12],
        "DS60_HIVE_IMAGE": HIVE,
        "DS60_PLATFORM_IMAGE": "ds60sqlpy-worker-data-platforms-python:1.0.0",
        "DS60_POSTGRES_IMAGE": "ds60-apache-hive-postgres:17.6",
    }
    (root / ".env").write_text("".join(f"{key}={value}\n" for key, value in saved.items()))
    before = (root / ".env").read_bytes()
    result = subprocess.run(
        ["bash", "run.sh", "status"],
        cwd=root,
        env=env | dict.fromkeys(saved, "ambient-wrong"),
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads((root / "compose-env.json").read_text()) == saved | {
        "DOCKER_DEFAULT_PLATFORM": None
    }
    assert (root / ".env").read_bytes() == before
