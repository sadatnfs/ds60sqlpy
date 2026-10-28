"""Bounded actual Delta Sharing Parquet-protocol client, not a reference server."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

EXPECTED = [
    {"id": 1, "region": "east", "amount": 4},
    {"id": 2, "region": "west", "amount": 9},
    {"id": 3, "region": "east", "amount": 7},
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Redirect rejected before credential or signed-URL forwarding")


def fetch(url, *, token=None, payload=None, allow=()):
    if (
        not isinstance(url, str)
        or len(url) > 16384
        or any(not 33 <= ord(char) <= 126 for char in url)
    ):
        raise ValueError("Sharing/data URL has an unsupported format; values withheld")
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        raise ValueError("Sharing/data URL has an unsupported format; values withheld") from None
    if token is not None and (
        not isinstance(token, str)
        or re.fullmatch(r"[A-Za-z0-9._~+/-]{1,4096}={0,8}", token, flags=re.ASCII) is None
    ):
        raise ValueError("Recipient bearer credential has an unsupported format; value withheld")
    if parts.scheme != "https" or parts.username or parts.password or parts.fragment:
        raise ValueError("Use verified HTTPS without embedded credentials")
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = "Bearer " + token
    data = None if payload is None else json.dumps(payload).encode()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(
            urllib.request.Request(url, data=data, headers=headers), timeout=20
        ) as response:
            raw = response.read(4000001)
            if len(raw) > 4000000:
                raise ValueError("Response exceeds the bounded sharing client limit")
            return response.status, dict(response.headers), raw
    except urllib.error.HTTPError as error:
        if error.code in allow:
            return error.code, {}, b""
        raise ValueError(
            "Sharing/data HTTP failure " + str(error.code) + "; URLs and credentials withheld"
        ) from None
    except urllib.error.URLError:
        raise ValueError(
            "Sharing/data transport unavailable; URLs and credentials withheld"
        ) from None


def read_profile():
    path = Path("/project/.workshop/recipient.share")
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 32768:
        raise ValueError("Use one regular bounded untracked recipient profile")
    try:
        profile = json.loads(path.read_text())
    except (ValueError, UnicodeError):
        raise ValueError("Invalid recipient profile; contents withheld") from None
    if type(profile) is not dict:
        raise ValueError("Recipient profile must be an object; contents withheld")
    if (
        profile.get("shareCredentialsVersion") != 1
        or not isinstance(profile.get("bearerToken"), str)
        or not profile["bearerToken"]
    ):
        raise ValueError("Unsupported or incomplete recipient profile")
    if (
        re.fullmatch(r"[A-Za-z0-9._~+/-]{1,4096}={0,8}", profile["bearerToken"], flags=re.ASCII)
        is None
    ):
        raise ValueError("Recipient bearer credential has an unsupported format; value withheld")
    endpoint = profile.get("endpoint", "")
    if (
        not isinstance(endpoint, str)
        or len(endpoint) > 16384
        or any(not 33 <= ord(char) <= 126 for char in endpoint)
    ):
        raise ValueError("Recipient endpoint has an unsupported format; value withheld")
    try:
        parts = urllib.parse.urlsplit(endpoint)
    except ValueError:
        raise ValueError("Recipient endpoint has an unsupported format; value withheld") from None
    if parts.query or parts.fragment or parts.username or parts.password or parts.scheme != "https":
        raise ValueError("Recipient endpoint must use verified HTTPS without query/credentials")
    return profile


def check():
    profile = read_profile()
    endpoint = profile["endpoint"].rstrip("/")
    token = profile["bearerToken"]
    contract = json.loads(Path("/project/fixture-contract.json").read_text())
    share, schema, table = [contract[key] for key in ["share", "schema", "table"]]
    path = (
        "/shares/"
        + urllib.parse.quote(share, safe="")
        + "/schemas/"
        + urllib.parse.quote(schema, safe="")
        + "/tables/"
        + urllib.parse.quote(table, safe="")
    )

    def control(suffix, payload=None):
        return fetch(endpoint + suffix, token=token, payload=payload)

    code, _, body = control("/shares?maxResults=100")
    if share not in {row["name"] for row in json.loads(body).get("items", [])}:
        raise ValueError("Expected owned share absent from bounded listing")
    _, _, body = control(
        "/shares/" + urllib.parse.quote(share, safe="") + "/schemas?maxResults=100"
    )
    if schema not in {row["name"] for row in json.loads(body).get("items", [])}:
        raise ValueError("Expected owned schema absent")
    _, _, body = control(path.rsplit("/", 1)[0] + "?maxResults=100")
    if table not in {row["name"] for row in json.loads(body).get("items", [])}:
        raise ValueError("Expected owned table absent")
    _, metadata_headers, metadata_body = control(path + "/metadata")
    _, headers, body = control(
        path + "/query", {"version": contract["version"], "predicateHints": []}
    )
    rows = [json.loads(line) for line in body.splitlines() if line.strip()]
    protocols = [row["protocol"] for row in rows if "protocol" in row]
    if (
        len(protocols) != 1
        or protocols[0].get("minReaderVersion") != 1
        or protocols[0].get("readerFeatures")
    ):
        raise ValueError("Unsupported protocol/features; no data files fetched")
    if headers.get("delta-table-version", headers.get("Delta-Table-Version")) != str(
        contract["version"]
    ):
        raise ValueError("Pinned table version was not confirmed")
    files = [row["file"] for row in rows if "file" in row]
    if not 1 <= len(files) <= 10 or any(
        row.get("deletionVectorFile") or row.get("add") for row in rows
    ):
        raise ValueError("This portable route accepts only bounded basic Parquet responses")
    allowed = set(os.environ.get("DS60_SHARING_DATA_HOSTS", "").split(",")) - {""}
    tables = []
    total = 0
    uncompressed_total = 0
    materialized_rows = 0
    for file in files:
        if file.get("partitionValues"):
            raise ValueError("Portable route requires an unpartitioned table; no data fetched")
        url = file["url"]
        if urllib.parse.urlsplit(url).hostname not in allowed:
            raise ValueError("Data host not explicitly allowed; signed URL withheld")
        # Recipient bearer credentials are never forwarded to object storage.
        _, _, raw = fetch(url)
        total += len(raw)
        if total > 8000000:
            raise ValueError("Combined data budget exceeded")
        parquet = pq.ParquetFile(pa.BufferReader(raw))
        metadata = parquet.metadata
        if (
            metadata.num_rows > 1000
            or metadata.num_columns != 3
            or metadata.num_row_groups > 16
            or metadata.serialized_size > 262144
        ):
            raise ValueError("Parquet footer exceeds row/column/group/metadata bounds")
        schema = parquet.schema_arrow
        if set(schema.names) != {"id", "region", "amount"} or not (
            pa.types.is_integer(schema.field("id").type)
            and pa.types.is_string(schema.field("region").type)
            and pa.types.is_integer(schema.field("amount").type)
        ):
            raise ValueError("Portable fixture requires the exact primitive unpartitioned schema")
        uncompressed = sum(
            metadata.row_group(group).column(column).total_uncompressed_size
            for group in range(metadata.num_row_groups)
            for column in range(metadata.num_columns)
        )
        uncompressed_total += uncompressed
        materialized_rows += metadata.num_rows
        if uncompressed < 0 or uncompressed_total > 16000000 or materialized_rows > 1000:
            raise ValueError(
                "Uncompressed data/combined row budget exceeded before materialization"
            )
        parsed = parquet.read(columns=["id", "region", "amount"])
        tables.append(parsed)
    result = sorted(pa.concat_tables(tables).to_pylist(), key=lambda row: row["id"])
    if result != EXPECTED:
        raise ValueError("Shared rows differ from the independent exact oracle")
    rejected, _, _ = fetch(
        endpoint + "/shares?maxResults=1", token="deliberately-invalid-fixture", allow=(401, 403)
    )
    if rejected not in {401, 403}:
        raise ValueError("Invalid recipient credential was not rejected")
    return {
        "passed": True,
        "actual_delta_sharing_protocol": True,
        "version": contract["version"],
        "rows": result,
        "metadata_response_bytes": len(metadata_body),
        "file_count": len(files),
        "data_bytes": total,
        "invalid_recipient_rejected": True,
        "basic_parquet_reader_version": 1,
        "delta_format_cdf_or_new_features_qualified": False,
        "credentials_or_signed_urls_saved": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "check"])
    args = parser.parse_args()
    print(
        json.dumps(
            {
                "expected_rows": EXPECTED,
                "supported_protocol": "basic Parquet/minReaderVersion1",
                "server_contacted": False,
            }
            if args.action == "plan"
            else check(),
            sort_keys=True,
        )
    )
