"""Learner state survives multiple application/MCP writers and failed writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from ds60sqlpy.catalog import Catalog
from ds60sqlpy.coaching import CoachingService
from ds60sqlpy.progress import ProgressStore
from ds60sqlpy.state_files import atomic_json_write, locked_update

ROOT = Path(__file__).resolve().parents[1]
WORKER = """
import sys,time
from pathlib import Path
from ds60sqlpy.catalog import Catalog
from ds60sqlpy.coaching import CoachingService
from ds60sqlpy.progress import ProgressStore
root, folder, mode, identity = sys.argv[1:]
folder=Path(folder)
catalog=Catalog.load(Path(root))
progress=ProgressStore(catalog,folder/'progress.json')
service=CoachingService(catalog,progress)
for index in range(20):
    if mode=='coaching':
        service.save('python-01',identity,f'{identity}:{index}')
    else:
        progress.mark_complete(identity,f'{identity}:{index}')
    time.sleep(0.001)
"""


def test_state_reads_do_not_create_a_workspace_or_locks(tmp_path: Path) -> None:
    catalog = Catalog.load()
    folder = tmp_path / "not-created"
    store = ProgressStore(catalog, folder / "progress.json")
    service = CoachingService(catalog, store)
    assert store.completions() == ()
    assert service.session("python-01") == {}
    service.paths()
    service.lesson("python-01")
    assert not folder.exists()


@pytest.mark.parametrize(
    ("mode", "identities"),
    [
        ("coaching", ("predict", "attempt", "compare", "explain")),
        ("progress", ("python-01", "python-02", "sql-01", "sql-02")),
    ],
)
def test_independent_processes_preserve_each_others_state(
    tmp_path: Path, mode: str, identities: tuple[str, ...]
) -> None:
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", WORKER, str(ROOT), str(tmp_path), mode, identity],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for identity in identities
    ]
    try:
        for process in processes:
            stdout, stderr = process.communicate(timeout=30)
            assert process.returncode == 0, stdout + stderr
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=10)
    if mode == "coaching":
        payload = json.loads((tmp_path / "coaching.json").read_text(encoding="utf-8"))
        notes = payload["lessons"]["python-01"]
        for identity in identities:
            assert notes[identity] == f"{identity}:19"
    else:
        records = ProgressStore(Catalog.load(), tmp_path / "progress.json").completions()
        assert {record.lesson_id: record.notes for record in records} == {
            identity: f"{identity}:19" for identity in identities
        }
    assert not list(tmp_path.glob("*.tmp"))


def test_failed_serialization_preserves_previous_bytes_and_cleans_only_own_temp(
    tmp_path: Path,
) -> None:
    path = tmp_path / "progress.json"
    path.write_text('{"original":true}\n', encoding="utf-8")
    unrelated = tmp_path / "my-notes.tmp"
    unrelated.write_text("keep", encoding="utf-8")
    before = path.read_bytes()
    with (
        locked_update(path),
        patch("ds60sqlpy.state_files.json.dump", side_effect=ValueError("invalid new content")),
        pytest.raises(ValueError, match="invalid new"),
    ):
        atomic_json_write(path, {"new": "content"})
    assert path.read_bytes() == before
    assert unrelated.read_text(encoding="utf-8") == "keep"
    assert sorted(item.name for item in tmp_path.iterdir()) == [
        "my-notes.tmp",
        "progress.json",
        "progress.json.lock",
    ]


def test_process_exit_releases_lock_and_preserves_previous_state(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    with locked_update(path):
        atomic_json_write(path, {"before": True})
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import os,sys; from pathlib import Path; "
            "from ds60sqlpy.state_files import locked_update; "
            "context=locked_update(Path(sys.argv[1])); context.__enter__(); os._exit(7)",
            str(path),
        ],
        cwd=ROOT,
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 7
    assert json.loads(path.read_text(encoding="utf-8")) == {"before": True}
    with locked_update(path):
        atomic_json_write(path, {"after": True})
    assert json.loads(path.read_text(encoding="utf-8")) == {"after": True}


def test_progress_reset_keeps_coaching_and_the_stable_lock_anchor(tmp_path: Path) -> None:
    progress = ProgressStore(Catalog.load(), tmp_path / "progress.json")
    progress.mark_complete("python-01", "retain until explicit reset")
    service = CoachingService(progress.catalog, progress)
    service.save("python-01", "predict", "keep my evidence")
    progress.reset()
    assert not progress.path.exists()
    assert progress.path.with_name("progress.json.lock").is_file()
    assert service.session("python-01")["predict"] == "keep my evidence"
    progress.mark_complete("python-01", "new completion")
    assert progress.completions()[0].notes == "new completion"
