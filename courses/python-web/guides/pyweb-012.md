# pyweb-012: Resource-oriented API design and REST constraints

Tutorial mode. Stage: beginner. Direct prerequisites: `pyweb-011`.

## Starting point and result

A resource-oriented API exposes identifiable things and consistent ways to inspect or change them. This chapter creates tasks, returns a link to each representation and demonstrates that repeating an ordinary POST can create another resource. It is a small design investigation, not a claim to implement every constraint of the REST architectural style.

## Key terms

- **Resource:** An identifiable thing an API exposes, such as one task, addressed by its own URL.
- **Representation:** The data an API chooses to expose about a resource, here an ID and a title, which need not mirror every internal field.
- **Self link:** A URL in a response that identifies the returned resource, generated from the registered read route so a client can follow it.
- **Collection endpoint:** A path such as `/tasks` where POST creates a new member with a server-allocated ID, so repeating the POST creates another resource.
- **REST constraints:** The architectural properties of client/server separation, stateless interactions, cacheability, a uniform interface and layering, which JSON routes do not satisfy automatically.

## Mechanism: identity, representation and transitions

The collection path `/tasks` accepts a bounded title. The server allocates a new ID using a monotonic counter within this disposable application fixture. The response includes the representation and a self link generated from the registered read route. A client can follow that link to retrieve the identified task.

A representation is the data the API chooses to expose about a resource. It need not mirror every internal database field. Here the public fields are ID and title. The input contract accepts only title, so a caller cannot assign an arbitrary owner field through this endpoint. Later authorization chapters derive ownership from trusted authentication state.

REST includes broader constraints such as client/server separation, stateless interactions, cacheability, a uniform interface and layering. JSON plus a set of routes does not automatically satisfy all of them. A practical application should state its choices and tradeoffs clearly rather than treating an architectural label as proof of quality.

## Worked case: create and retrieve a resource

The client posts a title and receives status 201, an ID and a self link. It follows the link and obtains the expected representation. The assertions connect creation to retrieval, which is stronger than testing each handler's return value in isolation.

The route supplies the resource identity on each read request. The server does not require a hidden variable such as “the task this client most recently opened” to decide which task is requested. That makes requests easier to reason about, retry, log and route between workers, subject to the chosen authentication and persistence design.

The counter is a finite fixture mechanism. A deployed application needs an identity strategy appropriate to its database and concurrency model. A process-local counter does not coordinate several workers or survive a restart.

## Worked case: repeat POST and reject unintended fields

The client sends the same POST body twice. Two different IDs are created. That behavior is allowed by this collection-creation contract, so the program explicitly records it. A client retry after an uncertain response could therefore create a duplicate task unless the application provides an additional idempotency mechanism.

A request containing an extra owner field returns 422. An unknown task ID returns 404. These refusals address different concerns: one violates the write schema, while the other identifies a resource the fixture does not have. Neither result should be silently converted into a successful empty object.

Later chapters add idempotency keys, version preconditions, transactions and authorization. They build on the same discipline: define the intended state transition and what a client can observe when it succeeds, repeats, conflicts or fails.

## Worked example: Location headers and a collection resource

```python
from flask import Flask, request, url_for

app = Flask(__name__)
tasks = {}


@app.post("/tasks")
def create():
    task_id = len(tasks) + 1
    tasks[task_id] = {"id": task_id, "title": request.get_json()["title"]}
    return tasks[task_id], 201, {"Location": url_for("read", task_id=task_id)}


@app.get("/tasks/<int:task_id>")
def read(task_id):
    return tasks[task_id]


@app.get("/tasks")
def collection():
    return {"items": list(tasks.values()), "count": len(tasks)}


with app.test_client() as client:
    created = client.post("/tasks", json={"title": "Read RFC 9110"})
    print(created.status_code, created.headers["Location"])
    print(client.get(created.headers["Location"]).json)
    print(client.get("/tasks").json["count"])
```

Expected output:

```text
201 /tasks/1
{'id': 1, 'title': 'Read RFC 9110'}
1
```

The POST targeted the collection `/tasks` and the server, not the client, chose identifier 1. The 201 response advertised the new member's URL in the standard `Location` header, and the client followed that header instead of building `/tasks/1` itself. The lesson puts the same link in a `links.self` body field; both forms let the server change its URL layout without breaking clients. The collection and the member are separate resources with separate representations, which is the core of resource-oriented design. Using `len(tasks) + 1` is only safe in this single-threaded fixture: after a deletion it would reuse an identifier, which is why the lesson keeps a monotonic `count(1)` instead.

## Failure diagnosis

Endpoints that require undocumented call ordering often hide conversational state. APIs that expose database internals can make future migrations unnecessarily difficult. Inconsistent error bodies can force clients to guess which parser to use. Start from concrete client operations and explicit representations, then test their relationships rather than optimizing route syntax first.

A successful local fixture also says nothing about concurrency, storage durability or the behavior of a reverse proxy. The owned workshops add those surfaces with separate acceptance. Keep the confidence supported by each test layer explicit.

## Interview discussion

**Is POST always non-idempotent?** HTTP does not give every POST operation an idempotence guarantee. An application can define a suitable idempotency-key contract, but clients must not assume one exists without documentation.

**Does stateless interaction mean the server stores no data?** No. Resource data can live on the server. The architectural question concerns how much request meaning depends on hidden conversational context rather than information supplied with the request.

## Next step

Choose a framework branch. Flask begins with factories and explicit composition; FastAPI begins with typed request/response contracts; Django begins with a coordinated project and application structure.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite framework-client investigation; no external server is started."""

import json


def run_cases():
    from itertools import count

    from flask import Flask, request, url_for

    app = Flask(__name__)
    records = {}
    identifiers = count(1)

    @app.post("/tasks")
    def create():
        body = request.get_json(silent=True)
        if (
            not isinstance(body, dict)
            or set(body) != {"title"}
            or not isinstance(body["title"], str)
            or not 1 <= len(body["title"]) <= 80
        ):
            return {"error": "one bounded title required"}, 422
        key = next(identifiers)
        records[key] = {"id": key, "title": body["title"]}
        return {**records[key], "links": {"self": url_for("read", task_id=key)}}, 201

    @app.get("/tasks/<int:task_id>")
    def read(task_id):
        if task_id not in records:
            return {"error": "not found"}, 404
        return records[task_id]

    with app.test_client() as client:
        first = client.post("/tasks", json={"title": "Study HTTP"})
        second = client.post("/tasks", json={"title": "Study HTTP"})
        assert first.status_code == second.status_code == 201
        assert first.json["id"] != second.json["id"]
        representation = client.get(first.json["links"]["self"]).json
        assert representation == {"id": 1, "title": "Study HTTP"}
        assert client.get("/tasks/99").status_code == 404
        assert (
            client.post("/tasks", json={"title": "x", "owner": "someone-else"}).status_code == 422
        )
    return {
        "first_representation": representation,
        "repeated_post_created_two_resources": len(records) == 2,
        "resource_url": first.json["links"]["self"],
        "whole_REST_architecture_certified": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
