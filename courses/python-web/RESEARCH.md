# Python web framework sources and runtime boundaries

Reviewed 2026-10-29. Framework version selection uses official package metadata
and project documentation, followed by an actual compatibility probe. Course
prose and examples are original; external examples are references, not copied
application source.

| Component | Selected initial version | Primary evidence |
| --- | --- | --- |
| FastAPI | 0.162.0 | [Release package](https://pypi.org/project/fastapi/0.162.0/) and [testing guide](https://fastapi.tiangolo.com/tutorial/testing/) |
| Starlette | 1.10.0 | [Release package](https://pypi.org/project/starlette/1.10.0/) and [TestClient documentation](https://www.starlette.io/testclient/) |
| Pydantic | 2.14.1 | [Package metadata](https://pypi.org/project/pydantic/2.14.1/) and [validation concepts](https://docs.pydantic.dev/latest/concepts/models/) |
| Flask | 3.1.3 | [Release package](https://pypi.org/project/Flask/3.1.3/) and [testing guide](https://flask.palletsprojects.com/en/stable/testing/) |
| Django | 6.1.2 | [Release package](https://pypi.org/project/Django/6.1.2/), [6.1 testing tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/) and [6.1 release notes](https://docs.djangoproject.com/en/6.1/releases/6.1/) |
| HTTPX2 | 2.16.0 | [Release package](https://pypi.org/project/httpx2/2.16.0/) and [maintained source](https://github.com/pydantic/httpx2) |

Django 6.1 requires Python 3.12 or newer. Author-written lesson syntax remains
parseable by Python 3.11 contributor checks; execution uses the separate prepared
Python 3.12 web profile.

The first actual probe used HTTPX 0.28.1 and passed, but Starlette emitted its
explicit deprecation warning recommending HTTPX2. Starlette's official TestClient
page now documents HTTPX2, and its distribution metadata includes that client in
the full extra. Repeating the real probe with HTTPX2 2.16.0 removed the warning
and preserved all results. The separate web profile avoids changing another
already-qualified framework's HTTP dependency stack.

`runtime_probe.py` checks the exact six versions, a real Flask client, FastAPI
request/response validation, ASGI lifespan startup/shutdown, a finite WebSocket
exchange through TestClient, and a Django client backed by a temporary SQLite
table. It completed on host Python 3.12.13 with a clean pip dependency check.
That is in-process compatibility evidence. It does not establish a Linux image,
TCP server, browser, TLS proxy, PostgreSQL or deployed WebSocket/SSE behavior.
Those require their separately retained native and workshop checks.

The complete finite route also uses the exact pins in
`runtime-extra-requirements.in`, including SQLAlchemy/Alembic, DRF, JWT/Argon2,
async/server libraries, observability clients and WhiteNoise. Real host probes
exercise the selected APIs and dependency resolution is checked before native
worker preparation. Celery eager mode and in-memory telemetry/email are labeled
as such; they are not durable worker, SMTP or external collector acceptance.

[WhiteNoise's Django integration](https://whitenoise.readthedocs.io/en/stable/django.html)
documents the explicit collectstatic and middleware boundary used by the owned
workshop. [FastAPI's local documentation asset guidance](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)
explains why default documentation HTML needs deliberate offline preparation.
This workshop instead serves an original limited local OpenAPI explorer, with
Swagger/ReDoc disabled and no external bundle, font or validator dependency.
It uses the local OpenAPI schema and fixed same-origin interactive examples.

All 72 authored chapters have complete original cases. The 69 finite Python
references have actual framework-client/library execution coverage; the 3
reading/project units point to the real owned service lifecycle. Source checks,
host execution, native nonroot worker execution, TCP/WS/SSE acceptance, browser
asset observations and retained-state readback are separate evidence tiers.
Do not infer a completed service run from the existence of its acceptance script.

See [current qualification boundaries](QUALIFICATION.md) for the completed
native worker, real service/browser and retained-state observations.
