"""A bounded real Arrow Flight service over one immutable owned fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Iterator
from pathlib import Path

import pyarrow as pa
import pyarrow.flight as flight
import pyarrow.parquet as pq

ROWS = [
    {"id": 1, "region": "east", "amount": 4},
    {"id": 2, "region": "west", "amount": 9},
    {"id": 3, "region": "east", "amount": 7},
]
SCHEMA = pa.schema([("id", pa.int64()), ("region", pa.string()), ("amount", pa.int64())])
IDENTITY = hashlib.sha256(
    json.dumps(ROWS, sort_keys=True, separators=(",", ":")).encode()
).hexdigest()


def initialize(state: Path) -> None:
    if state.is_symlink():
        raise ValueError("State must not be a symbolic link")
    state.mkdir(parents=True, exist_ok=True)
    data = state / "events.parquet"
    manifest = state / "manifest.json"
    if data.exists() or manifest.exists():
        read_fixture(state)
        print("Existing fixture verified and retained")
        return
    pq.write_table(pa.Table.from_pylist(ROWS, schema=SCHEMA), data)
    manifest.write_text(
        json.dumps({"schema_version": 1, "logical_sha256": IDENTITY}) + "\n", encoding="utf-8"
    )
    for path in (state, data, manifest):
        path.chmod(0o700 if path.is_dir() else 0o600)
        if os.geteuid() == 0:
            os.chown(path, 1000, 1000)
    print("Created the three-record owned fixture")


def read_fixture(state: Path) -> pa.Table:
    for name in ("events.parquet", "manifest.json"):
        path = state / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("The fixture requires regular data and manifest files")
    if (state / "manifest.json").stat().st_size > 4096 or (
        state / "events.parquet"
    ).stat().st_size > 65536:
        raise ValueError("Fixture files exceed their bounds")
    manifest = json.loads((state / "manifest.json").read_text("utf-8"))
    parquet = pq.ParquetFile(state / "events.parquet")
    if parquet.metadata.num_rows != 3:
        raise ValueError("Fixture must contain exactly three rows")
    table = parquet.read()
    if manifest != {"schema_version": 1, "logical_sha256": IDENTITY}:
        raise ValueError("Fixture manifest identity mismatch")
    if not table.schema.equals(SCHEMA) or table.to_pylist() != ROWS:
        raise ValueError("Fixture content mismatch")
    return table.replace_schema_metadata({b"logical_sha256": IDENTITY.encode()})


# PyArrow's compiled Flight base has no distributed typing declaration.
class FixtureServer(flight.FlightServerBase):  # type: ignore[misc]
    def __init__(self, state: Path, host: str, port: int) -> None:
        super().__init__((host, port))
        self.table = read_fixture(state)

    def information(self) -> flight.FlightInfo:
        descriptor = flight.FlightDescriptor.for_path("events")
        endpoint = flight.FlightEndpoint(flight.Ticket(b"events-v1"), [])
        return flight.FlightInfo(
            self.table.schema, descriptor, [endpoint], self.table.num_rows, self.table.nbytes
        )

    def list_flights(self, context: object, criteria: object) -> Iterator[flight.FlightInfo]:
        yield self.information()

    def get_flight_info(
        self, context: object, descriptor: flight.FlightDescriptor
    ) -> flight.FlightInfo:
        if descriptor.path != [b"events"]:
            raise pa.ArrowInvalid("Unknown fixture descriptor")
        return self.information()

    def do_get(self, context: object, ticket: flight.Ticket) -> flight.RecordBatchStream:
        if ticket.ticket != b"events-v1":
            raise pa.ArrowInvalid("Unknown fixture ticket")
        return flight.RecordBatchStream(self.table)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("init", "serve"))
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8815)
    args = parser.parse_args()
    if args.action == "init":
        initialize(args.state)
    else:
        server = FixtureServer(args.state, args.host, args.port)
        print(f"Arrow Flight fixture ready on port {server.port}", flush=True)
        server.serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
