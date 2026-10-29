# Python web qualification and evidence boundaries

The admitted route contains 72 detailed tutorial chapters: 69 complete finite
Python programs and three explicit project-reading units. The route extends the
original Python curriculum without replacing its IDs or saved work. Framework
branches can follow the shared HTTP foundations independently.

The finite runtime is the separately prepared `python-web` profile. Its Python
3.12 environment supplies the exact framework and supporting-library pins in
`runtime-requirements.in`, `runtime-extra-requirements.in` and the native worker
locks. Author-written source remains parseable by Python 3.11 contributor tools.
Dependencies and browser assets are prepared deliberately, never downloaded by
opening a lesson or running its source.

## What has actually been exercised

| Surface | Observed evidence | Boundary |
| --- | --- | --- |
| Finite references | Every one of the 69 programs executed through the actual bounded nonroot Linux ARM64 worker. Extended compatibility and deliberate nonzero-exit reporting also passed. | In-process framework clients and local fixtures do not establish TCP or browser delivery. |
| Host source and behavior checks | Complete authoring projection, prerequisites, Python syntax, real finite references, body-byte limits, owned lifecycle and offline-asset contracts passed focused tests. | Source checks and host execution remain distinct from native container execution. |
| Real server application | Flask/Gunicorn, FastAPI/Uvicorn and Django/Gunicorn served actual HTTP against an owned PostgreSQL database, with authentication, CSRF, origin/host refusal and owner-scoped notes. | Local loopback HTTP only; no public TLS or remote identity provider is claimed. |
| Streaming and work ownership | A real WebSocket exchange passed. SSE bytes arrived before a held job was released; disconnect/resume used persistent event IDs. An actually stopped worker later reconciled its released job with one committed completion. | A bounded local fixture is not a multi-host queue or throughput benchmark. |
| Browser and assets | Chromium exercised all three applications, local API explorer GET/POST, Django admin assets, note reload/owner switching, WebSocket and SSE reconnect. No external requests or page errors were observed. | Desktop light/dark observations were retained. A separate mobile viewport qualification was not performed. |
| Saved data and lifecycle | Stop/resume retained the exact five container/image identities. Application/worker replacement retained PostgreSQL and successfully read the earlier receipt's note/job identities. | Readback did not recreate lost records or switch projects. |
| Source/image provenance | The maintained checker matched the native Linux architecture and every shipped public-project source hash, exported receipts, and removed only its newly owned containers/network. | Synthetic database volumes and evidence were retained; learner resources were not used. |

The browser pass exposed a real asynchronous form bug that HTTP tests alone did
not catch. The handler now retains its form before awaiting a response. An actual
JavaScript regression rejects the earlier handler and checks that the repaired
handler resets the form and refreshes the committed data. A local API explorer
label association was also corrected before final sealed acceptance.

## Reproduce the appropriate layer

From the course directory, regenerate only the owned curriculum and check it:

```sh
python authoring/build.py
python authoring/build.py --check
```

The focused contributor tests are `tests/test_python_web_curriculum.py`,
`tests/test_python_web_workshop.py` and `tests/test_python_web_project_checker.py`.
`DS60_PYTHON_WEB_INTERPRETER` selects an explicitly prepared interpreter for the
69 real finite-program tests. If it is absent, those runtime tests report skips;
a skip must not be described as successful execution. Native worker qualification
and the ordinary publication matrix supply their own runtime evidence.

Follow [the web-lab README](projects/web-lab/README.md) for Docker-only learner
startup, stop/resume and saved-state readback. Its maintained `check_project.py`
accepts a fresh workspace, prepared native image, prepared browser interpreter,
new report path and explicit disposable confirmation. It runs the actual service,
worker, browser and lifecycle checks and retains source-bound receipts before
cleaning its synthetic containers. It does not publish images or delete volumes.

The complete project gate intentionally refuses inherited emulation/project
settings and registry tokens, preserves a browser virtual environment's lexical
interpreter path, rejects unsupported or mismatched native architectures, and
applies the same cache exclusions when inventorying and copying public source.
Those refusal paths have focused negative tests.

## Release and platform boundaries

Local native runtime acceptance was performed on ARM64. Native AMD64 qualification
belongs to the hosted Linux runner and must pass before claiming that release
architecture accepted. The source supports Linux Docker delivery on Linux/macOS
and Windows through WSL 2, but this local run is not a Windows host observation.

Course admission, generated-reader rendering, unified classroom navigation and
saved editor work are shared application integration gates. They remain distinct
from the standalone project and from completed Docker Hub promotion/fresh pulls.
A prepared image, configured workflow or staged upload is not a published release.
Preserve immutable released tags and use the repository's coordinated publication
path for a new version.
