"""Initialize missing metadata/pool, then let upstream own its components."""

from __future__ import annotations

import os
import subprocess


def main() -> None:
    subprocess.run(["airflow", "db", "migrate"], check=True, timeout=120)
    from airflow.models.pool import Pool
    from airflow.utils.session import create_session

    with create_session() as session:
        exists = session.query(Pool).filter(Pool.pool == "classroom_io").one_or_none() is not None
    if not exists:
        subprocess.run(
            ["airflow", "pools", "set", "classroom_io", "1", "Bounded classroom fixture I/O"],
            check=True,
            timeout=30,
        )
    else:
        print("Existing classroom pool configuration retained", flush=True)
    os.execvp("airflow", ["airflow", "standalone"])


if __name__ == "__main__":
    main()
