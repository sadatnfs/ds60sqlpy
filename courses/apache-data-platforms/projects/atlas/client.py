"""Actual bounded Atlas v2 API client for an explicitly prepared owned server."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

OWNER = os.environ.get("DS60_ATLAS_OWNER", "")
if not re.fullmatch(r"[a-f0-9]{32}", OWNER):
    raise ValueError("Use the copied workshop launcher to establish ownership")
PREFIX = "ds60_" + OWNER[:12]
DATASET = PREFIX + "_dataset"
PROCESS = PREFIX + "_process"
LABEL = PREFIX + "_reviewed"
NAMES = {
    key: "ds60://" + OWNER + "/" + key for key in ["raw", "curated", "unrecorded", "transform"]
}


def payloads():
    types = {
        "entityDefs": [
            {"name": DATASET, "superTypes": ["DataSet"], "typeVersion": "1.0", "attributeDefs": []},
            {"name": PROCESS, "superTypes": ["Process"], "typeVersion": "1.0", "attributeDefs": []},
        ],
        "classificationDefs": [
            {"name": LABEL, "superTypes": [], "typeVersion": "1.0", "attributeDefs": []}
        ],
    }
    entities = []
    for number, key in enumerate(["raw", "curated", "unrecorded"], 1):
        entity = {
            "guid": str(-number),
            "typeName": DATASET,
            "attributes": {
                "qualifiedName": NAMES[key],
                "name": key,
                "description": "Synthetic owned Atlas tutorial asset",
            },
        }
        if key == "curated":
            entity["classifications"] = [{"typeName": LABEL}]
        entities.append(entity)
    entities.append(
        {
            "guid": "-4",
            "typeName": PROCESS,
            "attributes": {
                "qualifiedName": NAMES["transform"],
                "name": "transform",
                "inputs": [{"guid": "-1", "typeName": DATASET}],
                "outputs": [{"guid": "-2", "typeName": DATASET}],
            },
        }
    )
    return {"types": types, "entities": {"entities": entities}}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Atlas redirect rejected before credential forwarding")


class Client:
    def __init__(self, *, invalid: bool = False):
        endpoint = os.environ.get("DS60_ATLAS_ENDPOINT", "")
        parts = urllib.parse.urlsplit(endpoint)
        if (
            parts.username
            or parts.password
            or parts.query
            or parts.fragment
            or parts.path not in ["", "/"]
        ):
            raise ValueError("Use a credential-free Atlas origin without path/query")
        local = parts.hostname in {"localhost", "127.0.0.1", "host.docker.internal"}
        if parts.scheme != "https" and not (parts.scheme == "http" and local):
            raise ValueError("Use verified HTTPS, or an explicit local fixture HTTP origin")
        user = os.environ.get("DS60_ATLAS_USERNAME", "")
        password = os.environ.get("DS60_ATLAS_PASSWORD", "")
        if not user or not password:
            raise ValueError("Provide fixture-only credentials in the untracked environment file")
        self.endpoint = endpoint.rstrip("/") + "/api/atlas/v2"
        self.authorization = (
            "Basic "
            + base64.b64encode(
                (user + ":" + ("deliberately-invalid-fixture" if invalid else password)).encode()
            ).decode()
        )

    def request(self, path, *, payload=None, method=None, allow=()):
        data = None if payload is None else json.dumps(payload).encode()
        req = urllib.request.Request(
            self.endpoint + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json", "Authorization": self.authorization},
        )
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
            with opener.open(req, timeout=15) as response:
                raw = response.read(200001)
                if len(raw) > 200000:
                    raise ValueError("Atlas response exceeds the bounded client contract")
                return response.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            if error.code in allow:
                return error.code, None
            raise ValueError(
                "Atlas HTTP failure " + str(error.code) + "; response/credentials not logged"
            ) from None
        except urllib.error.URLError:
            raise ValueError("Atlas transport unavailable; endpoint credentials withheld") from None

    def entity(self, key):
        kind = PROCESS if key == "transform" else DATASET
        path = (
            "/entity/uniqueAttribute/type/"
            + kind
            + "?"
            + urllib.parse.urlencode({"attr:qualifiedName": NAMES[key]})
        )
        return self.request(path)[1]["entity"]


def apply():
    client = Client()
    data = payloads()
    missing = {"entityDefs": [], "classificationDefs": []}
    for collection in missing:
        for definition in data["types"][collection]:
            code, existing = client.request(
                "/types/typedef/name/" + definition["name"], allow=(404,)
            )
            if code == 404:
                missing[collection].append(definition)
            elif existing.get("name") != definition["name"] or set(
                existing.get("superTypes", [])
            ) != set(definition["superTypes"]):
                raise ValueError("Existing owned type differs; no automatic migration occurred")
    if any(missing.values()):
        client.request("/types/typedefs", payload=missing)
    client.request("/entity/bulk", payload=data["entities"])
    return check()


def check():
    client = Client()
    entities = {key: client.entity(key) for key in NAMES}
    for key, entity in entities.items():
        if entity["attributes"]["qualifiedName"] != NAMES[key] or entity.get("status") != "ACTIVE":
            raise ValueError("Owned entity identity/status differs")
    guid = entities["curated"]["guid"]
    lineage = client.request("/lineage/" + guid + "?direction=BOTH&depth=3")[1]
    relations = lineage.get("relations", [])
    pairs = {(row["fromEntityId"], row["toEntityId"]) for row in relations}
    expected = {
        (entities["raw"]["guid"], entities["transform"]["guid"]),
        (entities["transform"]["guid"], guid),
    }
    if not expected <= pairs or any(entities["unrecorded"]["guid"] in pair for pair in pairs):
        raise ValueError("Recorded lineage does not match the owned expected edges")
    if LABEL not in {row["typeName"] for row in entities["curated"].get("classifications", [])}:
        raise ValueError("Owned classification missing")
    bad, _ = Client(invalid=True).request("/types/typedef/name/" + DATASET, allow=(401, 403))
    if bad not in {401, 403}:
        raise ValueError("Invalid-credential request was not rejected")
    return {
        "passed": True,
        "actual_atlas_rest": True,
        "owner": OWNER,
        "entity_guids": {key: row["guid"] for key, row in entities.items()},
        "expected_edges_present": True,
        "unrecorded_edge_absent": True,
        "classification_present": True,
        "invalid_credentials_rejected": True,
        "read_only_no_initialization": True,
        "hook_or_data_engine_enforcement_demonstrated": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "apply", "check"])
    args = parser.parse_args()
    result = (
        payloads() if args.action == "plan" else {"apply": apply, "check": check}[args.action]()
    )
    print(json.dumps(result, sort_keys=True))
