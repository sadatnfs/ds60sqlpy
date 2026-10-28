"""Read actual Flight batches and verify rejected requests with bounded calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import socket
from pathlib import Path
from typing import TypedDict

import pyarrow as pa
import pyarrow.flight as flight


class Row(TypedDict):
    id: int
    region: str
    amount: int


def check(endpoint: str, *, health_only: bool = False) -> dict[str, object]:
    client = flight.FlightClient(
        endpoint, generic_options=[("grpc.max_receive_message_length", 131072)]
    )
    options = flight.FlightCallOptions(timeout=5)
    try:
        flights = []
        for information in client.list_flights(options=options):
            flights.append(information)
            if len(flights) > 1:
                raise AssertionError("More than one fixture flight")
        if len(flights) != 1 or flights[0].descriptor.path != [b"events"]:
            raise AssertionError("Expected exactly one fixture flight")
        if health_only:
            return {"healthy": True}
        information = client.get_flight_info(flight.FlightDescriptor.for_path("events"), options)
        if information.total_records != 3 or len(information.endpoints) != 1:
            raise AssertionError("Unexpected fixture size or endpoints")
        reader = client.do_get(information.endpoints[0].ticket, options)
        batches = []
        try:
            for index, chunk in enumerate(reader):
                if index > 8 or chunk.data is None:
                    raise AssertionError("Unexpected stream structure")
                batches.append(chunk.data)
                if (
                    sum(batch.num_rows for batch in batches) > 3
                    or sum(batch.nbytes for batch in batches) > 65536
                ):
                    raise AssertionError("Fixture stream exceeds its declared bound")
            table = pa.Table.from_batches(batches, schema=reader.schema)
        finally:
            reader.cancel()
        expected: list[Row] = [
            {"id": 1, "region": "east", "amount": 4},
            {"id": 2, "region": "west", "amount": 9},
            {"id": 3, "region": "east", "amount": 7},
        ]
        if table.to_pylist() != expected:
            raise AssertionError("Received rows differ from the independent fixture oracle")
        digest = hashlib.sha256(
            json.dumps(expected, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if table.schema.metadata != {b"logical_sha256": digest.encode()}:
            raise AssertionError("Source identity metadata mismatch")
        rejected = []
        for ticket in (b"missing", b"../manifest.json", b"events-v1\x00"):
            try:
                client.do_get(flight.Ticket(ticket), options).read_all()
            except pa.ArrowInvalid:
                rejected.append(True)
            else:
                raise AssertionError("Unknown tickets must not select files or data")
        try:
            client.get_flight_info(flight.FlightDescriptor.for_path("missing"), options)
        except pa.ArrowInvalid:
            pass
        else:
            raise AssertionError("Unknown descriptor was accepted")
        return {
            "schema_version": 1,
            "passed": True,
            "transport": "actual-arrow-flight",
            "rows": len(expected),
            "east_total": sum(row["amount"] for row in expected if row["region"] == "east"),
            "logical_sha256": digest,
            "invalid_tickets_rejected": len(rejected),
        }
    finally:
        client.close()


def network_check() -> dict[str, object]:
    """Observe the real client namespace, not a network simulation."""
    addresses = sorted(
        {entry[4][0] for entry in socket.getaddrinfo("server", 8815, type=socket.SOCK_STREAM)}
    )
    if not addresses or len(addresses) > 8:
        raise AssertionError("Unexpected private service DNS result")
    valid = check("grpc://server:8815")
    client = flight.FlightClient("grpc://127.0.0.1:8815")
    try:
        try:
            list(client.list_flights(options=flight.FlightCallOptions(timeout=1)))
        except (flight.FlightUnavailableError, flight.FlightTimedOutError):
            pass
        else:
            raise AssertionError("Client loopback unexpectedly reached the separate server")
    finally:
        client.close()
    return {
        "passed": True,
        "namespace": "actual-client-container",
        "service_addresses": addresses,
        "service_dns_read_passed": valid["passed"],
        "client_loopback_rejected": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default="grpc://server:8815")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--network", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = network_check() if args.network else check(args.endpoint, health_only=args.health)
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
