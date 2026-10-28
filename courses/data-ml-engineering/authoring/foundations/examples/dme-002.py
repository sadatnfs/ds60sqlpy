"""Actual owned file operations and child processes, without a shell or network."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        data = root / "incoming" / "deliveries.json"
        data.parent.mkdir()
        data.write_text(
            json.dumps({"route": "café", "packages": 6}, ensure_ascii=False), encoding="utf-8"
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import json,pathlib,sys; "
                "print(json.loads(pathlib.Path(sys.argv[1]).read_text("
                "encoding='utf-8'))['packages'])",
                str(data),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        assert result.stdout.strip() == "6" and result.stderr == ""
        assert json.loads(data.read_text("utf-8"))["route"] == "café"
        return {
            "absolute_path_read_from_explicit_working_directory": True,
            "child_output": result.stdout.strip(),
            "exit_code": result.returncode,
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; print('candidate rows: 3'); "
                "print('contract rejected', file=sys.stderr); sys.exit(3)",
            ],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        assert result.returncode == 3 and result.stdout.strip() == "candidate rows: 3"
        assert result.stderr.strip() == "contract rejected"
        try:
            result.check_returncode()
        except subprocess.CalledProcessError as error:
            assert error.returncode == 3
        else:
            raise AssertionError("A nonzero process must not be reported as success")
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
            "publishable": False,
        }


def main():
    print("Owned files and a successful child:", example_one())
    print("Output is not a success signal:", example_two())


if __name__ == "__main__":
    main()
