# pyweb-043: OpenAPI, compatibility and generated clients

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-042`.

## Starting point and result

An OpenAPI document describes an HTTP API's paths, operations, schemas and responses. FastAPI derives much of it from route declarations and Pydantic models. This chapter checks that generated contract directly and examines a small breaking request change without depending on an external documentation CDN.

## Key terms

- **OpenAPI document:** A machine-readable description of an API's paths, operations, parameters, schemas and responses, which FastAPI derives from route declarations.
- **operationId:** A stable name for one operation, here `createNote`, that generated clients and documentation use to identify it.
- **Breaking change:** A contract change that makes requests valid under the old schema fail, such as adding a new required request field.
- **Generated client:** Code produced from an OpenAPI document that faithfully follows the contract, including any mistakes the contract contains.

## Mechanism: generated documentation still needs review

The route declares a stable operationId, a request model and a response model. The generated schema includes a successful 201 response and the framework's validation response. Required fields and forbidden extra properties come from the request model.

A schema is a representation of declarations, not proof that every runtime behavior is correct. Authorization, transactional side effects and domain rules may need descriptions and separate tests. A generated client can faithfully implement a mistaken contract, so generation does not remove API design responsibility.

The example disables FastAPI's default Swagger and ReDoc HTML routes because their standard pages reference external assets. It still serves the local OpenAPI JSON. The owned workshop provides an original local explorer using prepared local JavaScript and CSS, with no runtime CDN requirement.

## Worked case: inspect the actual generated operation

The client fetches openapi.json and locates the notes POST operation. It checks the stable operationId, 201 and 422 responses, the required title field and additionalProperties false. It then sends a valid request and verifies the public response.

These assertions connect declarations with real application behavior. They catch a renamed operation or weakened schema that might otherwise break generated clients silently. Stable operation IDs are useful because many generators derive method names from them.

The example also checks that the default documentation routes are absent. That is a deployment choice for an offline product, not a claim that OpenAPI itself requires internet access. The JSON schema and locally prepared documentation UI can work entirely within the owned server.

## Worked case: adding a required field breaks old callers

The program compares an earlier request's required-field set with a proposed set that adds category. Existing callers sending only title would now fail validation. The added required property is therefore a breaking request change even if the endpoint path and response remain unchanged.

Compatibility is directional. Adding an optional response field may be tolerated by some clients but rejected by strict ones. Removing a response field can break consumers. Tightening an enum, changing units or altering pagination semantics can break callers without a dramatic structural difference.

A useful compatibility review combines schema comparison with representative client requests and documented semantics. The small set comparison here explains one mechanism; it is not advertised as a complete OpenAPI compatibility checker.

## Worked example: spotting breaking changes in a request schema

```python
from pydantic import BaseModel, ConfigDict, Field


class CreateV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=60)


class CreateV2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=40)
    category: str
    pinned: bool = False


def breaking(old, new):
    old_schema, new_schema = old.model_json_schema(), new.model_json_schema()
    added = set(new_schema.get("required", [])) - set(old_schema.get("required", []))
    problems = [f"new required field {name}" for name in sorted(added)]
    for name, spec in old_schema["properties"].items():
        limit = new_schema["properties"].get(name, {}).get("maxLength")
        if limit is not None and limit < spec.get("maxLength", limit):
            problems.append(f"{name} maxLength {spec['maxLength']} to {limit}")
    return problems


print(CreateV1.model_json_schema()["properties"]["title"])
print(breaking(CreateV1, CreateV2))
```

Expected output:

```text
{'maxLength': 60, 'minLength': 1, 'title': 'Title', 'type': 'string'}
['new required field category', 'title maxLength 60 to 40']
```

FastAPI builds each request body entry in `/openapi.json` from `model_json_schema`, so comparing two versions of that output is a cheap contract test you can run before a release. Version 2 makes three changes and the checker flags two of them. Adding the required `category` field breaks every existing client that does not send it, and shrinking `maxLength` from 60 to 40 rejects titles that used to be accepted. The new `pinned` field has a default, so old requests still validate and it is correctly left off the list. Notice that the rule runs the other way for response models: adding a field to a response is usually safe, while removing one breaks readers. A real compatibility tool also compares types, enums, paths and status codes, but the principle is the one the lesson's `previous_required` and `proposed_required` sets demonstrate: diff the published contract rather than relying on memory of what changed.

## Failure diagnosis and discussion

**Does changing only a Python type annotation affect clients?** It can change validation and generated schema, so it may be an API change. Review it as part of the public contract.

**Why not fetch documentation assets when the page opens?** The classroom must remain usable offline and should not make hidden external requests. Asset preparation belongs to a deliberate build step or original local implementation.

If a generated client changes method names unexpectedly, inspect operation IDs. If an old caller starts receiving 422, compare required fields, coercion and bounds before debugging transport. Continue with the integrated application walkthrough, where contract, authentication, persistence and ownership are exercised together.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, ConfigDict, Field

    class Create(BaseModel):
        model_config = ConfigDict(extra="forbid")
        title: str = Field(min_length=1, max_length=60)

    class Note(BaseModel):
        identifier: int
        title: str

    app = FastAPI(title="Notes contract", version="1.0.0", docs_url=None, redoc_url=None)

    @app.post("/notes", response_model=Note, status_code=201, operation_id="createNote")
    def create(payload: Create):
        return {"identifier": 1, "title": payload.title}

    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        operation = schema["paths"]["/notes"]["post"]
        assert operation["operationId"] == "createNote"
        assert "201" in operation["responses"] and "422" in operation["responses"]
        assert schema["components"]["schemas"]["Create"]["required"] == ["title"]
        assert schema["components"]["schemas"]["Create"]["additionalProperties"] is False
        assert client.get("/docs").status_code == 404 and client.get("/redoc").status_code == 404
        assert client.post("/notes", json={"title": "Contract"}).json() == {
            "identifier": 1,
            "title": "Contract",
        }
        assert (
            client.post("/notes", json={"title": "Contract", "owner": "other"}).status_code == 422
        )
    previous_required = {"title"}
    proposed_required = {"title", "category"}
    assert proposed_required - previous_required == {"category"}
    return {
        "operation_id": "createNote",
        "required_request_addition_is_breaking": ["category"],
        "offline_docs": "workshop serves its own local explorer; no default CDN UI",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
