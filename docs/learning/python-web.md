# Python web development learning route

A Python web application receives an HTTP request, validates its inputs, decides
which work is allowed, calls application or database code, and returns a response.
FastAPI, Flask and Django provide different tools for those steps. HTML, CSS and
browser JavaScript still run on the browser side; a Python API can serve a website,
a data product, a mobile client or another service.

The [Python web course](../../courses/python-web/README.md) contains 72 self-paced
chapters. Begin after Python functions and modules, then follow the shared HTTP
foundations. The framework branches are independent: studying FastAPI does not
require completing Flask or Django first. Existing Python lesson IDs and saved
work remain unchanged. There is no day-count limit or completion deadline.

## Choose a framework branch

| Route                       | Start                                                     | What you learn                                                                                                                                                       |
| --------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shared foundations          | [pyweb-001](../../courses/python-web/guides/pyweb-001.md) | Requests, URLs, methods, status codes, JSON, validation, templates, forms, cookies, WSGI/ASGI, tests and REST constraints                                            |
| Flask                       | [pyweb-013](../../courses/python-web/guides/pyweb-013.md) | Application factories, blueprints, contexts, SQLAlchemy, transactions, forms, login, ownership, file boundaries, caching, migrations and outbound clients            |
| FastAPI                     | [pyweb-027](../../courses/python-web/guides/pyweb-027.md) | Typed contracts, Pydantic, dependencies, lifespan, async work, database sessions, concurrency, authentication, authorization, streaming, WebSockets, SSE and OpenAPI |
| Django                      | [pyweb-045](../../courses/python-web/guides/pyweb-045.md) | Settings, middleware, templates, ORM, migrations, query costs, forms, authentication, permissions, admin, Django REST Framework and deployment checks                |
| Cross-framework engineering | [pyweb-063](../../courses/python-web/guides/pyweb-063.md) | Time budgets, cancellation, retries, outboxes, indexes, contention, distributed rate limits, observability, proxies, deployment, recovery and failure testing        |

For a data scientist starting with FastAPI, take 001 through 012, then 027 through 044.
Continue to the cross-framework engineering chapters before treating a model
endpoint as a complete service. A successful prediction does not establish input
validation, ownership, load behavior or recovery. Connect this route to the
[ML engineering service project](../../courses/ml-engineering/projects/local-system/README.md)
and the [LLM inference lifecycle](../../courses/data-ml-engineering/projects/inference-service/README.md).

Flask makes request and application boundaries visible with a small core. Django
brings an integrated ORM, migrations, forms, authentication and administrative
interface. FastAPI emphasizes typed API contracts and the ASGI ecosystem. None
of these choices removes the need to understand HTTP, database transactions,
authorization or deployment. The course demonstrates those shared requirements
with contrasting examples rather than ranking frameworks by one benchmark.

## Run the coding-pad examples

From a current repository checkout with Docker running:

```sh
./classroom --profile python-web
```

Open **Python web development: HTTP, Flask, FastAPI and Django** in the classroom
subject chooser. Each of the 69 executable examples runs in a fresh prepared
Python process and terminates. They use real framework test clients and bounded
temporary data. Code, notes and saved output use the same lesson-specific storage
as the other subjects. Temporary files created by a program are discarded when
that run ends.

Return to the same classroom project with:

```sh
./classroom resume
```

If you chose a named project, pass the same `--project NAME` on both commands.
Resume does not build or pull. Apply source changes deliberately through the
[documented update route](../one-command-classroom.md), preserving the project
and its volumes.

## Run actual web servers

The [owned web service lab](../../courses/python-web/projects/web-lab/README.md)
provides Flask/Gunicorn, FastAPI/Uvicorn and Django/Gunicorn servers, PostgreSQL,
and a separate worker for durable streaming jobs. It uses loopback ports and
its own saved settings and database volume. Authentication, per-user notes,
CSRF, WebSocket messages and SSE are real browser/server exchanges there.
FastAPI's API explorer and Django's admin assets are served locally after image
preparation; opening a page does not need a public asset CDN.

The lab has separate prepare, start, stop, resume, replace, check and verify
commands. Follow its README for the exact prerequisites and optional port choices.
Stopping or replacing application containers preserves database state. The 69
pad examples and the three project-reading chapters 068, 070 and 072 explain which
surface supplies each observation. An in-process client assertion, a browser
observation and a database recovery check answer different questions.

If you use a published Hub release, the worker keeps its registry-qualified
image name. After the full 1.1.0 release is available, this prepares the same
web-lab source layer from the pulled worker without rebuilding its dependencies:

```sh
./classroom pull --profile python-web --from-hub YOUR_DOCKERHUB_USER --tag 1.1.0
docker pull mirror.gcr.io/library/postgres:17
cd courses/python-web/projects/web-lab
WORKSHOP_BASE_IMAGE=YOUR_DOCKERHUB_USER/ds60sqlpy:1.1.0-worker-python-web ./workshop prepare
./workshop start
```

Replace `YOUR_DOCKERHUB_USER` with the publisher's namespace. Select this base
before the lab's first preparation; later stop/resume actions keep its saved
image and ports. The current source checkout must match the selected classroom
release, as required by the [Hub guide](../dockerhub.md).

## Continue into browser and systems work

Use [HTML/CSS/PHP](../../courses/web-development/README.md) for page structure and
styling, [JavaScript/TypeScript](../../courses/javascript-typescript/README.md)
for browser interaction, and [Docker](../../courses/docker/README.md) for image,
network and volume behavior. The current web lab is a local teaching deployment.
Public hosting, TLS termination, managed identity and multi-node operations need
their own environment-specific setup and acceptance; the chapters identify those
boundaries explicitly.
