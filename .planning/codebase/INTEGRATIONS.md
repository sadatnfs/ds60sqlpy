---
last_mapped_commit: a7b9bee89d73119a71319d41d2bf7ec2fefffc8e
last_mapped_at: 2026-11-23
---
<!-- refreshed: 2026-11-23 -->
# External Integrations

**Analysis Date:** 2026-11-23

## APIs & External Services

| System | Type | Purpose | Auth model | Criticality | Evidence |
|--------|------|---------|------------|-------------|----------|
| PostgreSQL | Database | Local course SQL database used for SQL lessons, notebooks, and training fixtures | Environment-configured course login; target validation restricts the course runner to the disposable training database | High for SQL lessons; not needed for non-SQL reading | `src/ds60sqlpy/sql_runner.py`, `src/ds60sqlpy/sql_notebook.py`, `.env.example` |
| Private runtime workers | Internal HTTP services | Execute profile-bound module jobs in separately selected worker containers | Per-session token loaded from a local token file and sent in `X-DS60-Worker-Token`; endpoint hostnames are restricted to private service names or loopback | High for runnable module profiles; optional by selection | `src/ds60sqlpy/module_jobs.py`, `docker/workers/` |
| Docker Engine / Compose | Local container runtime | Start the classroom, database, and selected language workers | Local engine access; no classroom Docker socket is exposed to lesson code | High for supported learner delivery | `README.md`, `scripts/classroom.sh`, `compose.classroom.yaml`, `compose.modules.yaml` |
| Docker Hub Registry v2 | Image registry API | Optional image metadata, release publication, and pull acceptance; Docker transports image layers | Docker Hub username/token for authorized registry operations; GitHub Actions references `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as repository secrets | Medium; only required for Hub distribution, not local image builds | `scripts/docker_registry.py`, `.github/workflows/publish-images.yml`, `.github/workflows/verify-published-images.yml` |
| GitHub Actions | CI/CD | Runs source, test, image qualification, and gated publication workflows | GitHub workflow permissions; Docker Hub secrets are used only by registry jobs | Medium for maintained checks and published images | `.github/workflows/ci.yml`, `.github/workflows/publish-images.yml` |
| Python/package and artifact repositories | Build-time package sources | Resolve dependencies and fetch pinned tools when building selected images; not required for ordinary classroom use after images and fixtures are prepared | Public HTTPS package/artifact endpoints; optional mirror variables are configuration-only | Medium during setup/build; not an app request dependency | `Dockerfile`, `docker/workers/`, `src/ds60sqlpy/docker_profiles.py`, `scripts/prepare_kubernetes.py` |
| MCP host | Local protocol adapter | Optional tutor tooling reads catalog and lesson content through the local stdio adapter | Host launches the local `ds60-mcp` command; progress writes are opt-in | Low/optional | `pyproject.toml`, `src/ds60sqlpy/mcp_server.py` |

The browser UI calls the classroom's same-origin `/api/` routes; no third-party browser API is required for the main classroom flow (`src/ds60sqlpy/assets/classroom.js`, `src/ds60sqlpy/classroom_http.py`). Optional course projects may separately document service dependencies; they are not app-wide integrations.

## Data Storage

**Databases:**
- PostgreSQL stores the course training database for SQL lessons. The host runner reads `DS60_DATABASE_URL`; container runtime configuration can use `DS60_LAB_DATABASE_URL` (`src/ds60sqlpy/sql_runner.py`, `src/ds60sqlpy/container_runtime.py`).
- SQL execution validates that the target is the designated local training database; connection details are not printed in this map (`src/ds60sqlpy/sql_notebook.py`, `src/ds60sqlpy/sql_runner.py`).

**File Storage:**
- Learner work and private runtime data persist in project-scoped Docker named volumes (`README.md`, `.env.example`).
- Contributor-mode progress, module jobs, and run receipts are stored as local files beneath their configured state directories (`src/ds60sqlpy/classroom_http.py`, `src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/state_files.py`).
- No external object-storage service is detected in the root runtime configuration.

**Caching:**
- No external cache service is detected in the root runtime manifests.

## Authentication & Identity

**Auth Provider:**
- No external user identity provider or SSO integration is detected. The local browser API uses a per-session random token and validates Host/Origin for state-changing requests (`src/ds60sqlpy/classroom_http.py`).
- Internal workers require a bounded token read from a local file; requests are restricted to configured private/loopback endpoints (`src/ds60sqlpy/module_jobs.py`).
- Docker Hub access uses registry token exchange. Workflow secret *names* are referenced in GitHub Actions; no secret values are included here (`scripts/docker_registry.py`, `.github/workflows/publish-images.yml`).

**Secrets and Credentials:**
- `.env.example` documents local configuration variable names. A local `.env` file is present, but its contents were not read or reproduced.
- Docker Hub credentials are supplied through GitHub Actions repository secrets for publishing and acceptance workflows. Worker session tokens are kept in a local runtime token file (`.github/workflows/publish-images.yml`, `src/ds60sqlpy/module_jobs.py`).
- Credential rotation policy is not detected in repository configuration.

## Reliability and Failure Behavior

- Worker HTTP calls use a four-second timeout, disable proxy use and redirects, validate response shape/size, and report readiness failures without automatically resubmitting a job (`src/ds60sqlpy/module_jobs.py`).
- The Docker Hub metadata client verifies TLS, rejects redirects, bounds response sizes, applies request timeouts, retries an expired bearer once, and checks visibility after registry writes (`scripts/docker_registry.py`).
- SQL helpers configure connection and statement/lock limits for supported execution paths (`src/ds60sqlpy/sql_runner.py`, `src/ds60sqlpy/execution.py`).

## Monitoring & Observability

**Error Tracking:** Not detected in the root runtime configuration.

**Logs and Metrics:**
- The local classroom emits concise request logs and avoids logging session tokens (`src/ds60sqlpy/classroom_http.py`).
- CI and release job output is available through GitHub Actions (`.github/workflows/ci.yml`).
- No external APM, metrics exporter, or hosted log integration is detected in the root runtime dependencies/configuration.

## CI/CD & Deployment

**Hosting:**
- Local Docker Engine/Compose is the supported application deployment target (`README.md`, `compose.classroom.yaml`).
- Docker Hub is an optional image distribution target; published-image workflows are gated and use registry credentials from GitHub Actions secrets (`.github/workflows/publish-images.yml`).

**CI Pipeline:**
- GitHub Actions covers validation, image builds, and specialized release verification (`.github/workflows/ci.yml`, `.github/workflows/verify-native-package.yml`, `.github/workflows/verify-published-images.yml`).

## Environment Configuration

**Relevant variable names:**
- Local app/database configuration: `DS60_POSTGRES_PORT`, `DS60_LAB_PORT`, `DS60_COURSE_USER`, `DS60_COURSE_PASSWORD`, `DS60_DATABASE_URL`, and `DS60_LAB_DATABASE_URL` (`.env.example`, `src/ds60sqlpy/container_runtime.py`).
- Optional module workers: `DS60_MODULE_ENDPOINTS` and `DS60_MODULE_TOKEN_FILE` (`src/ds60sqlpy/module_jobs.py`).
- Optional build mirror: `DS60_PYTHON_INDEX_URL` (`src/ds60sqlpy/docker_profiles.py`).
- Registry workflow secrets: `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (`.github/workflows/publish-images.yml`).

**Secrets location:**
- Local configuration is supplied through environment/`.env` without publishing values; release credentials are GitHub Actions repository secrets. No secret values are included in this document.

## Webhooks & Callbacks

**Incoming:** No third-party webhook receiver is detected; `/api/` routes serve the local classroom UI (`src/ds60sqlpy/classroom_http.py`).

**Outgoing:** The optional registry client contacts Docker Hub for image metadata and auth; selected build and Kubernetes preparation workflows fetch pinned artifacts from their configured upstreams (`scripts/docker_registry.py`, `scripts/prepare_kubernetes.py`).

## Evidence

- `src/ds60sqlpy/sql_runner.py`
- `src/ds60sqlpy/sql_notebook.py`
- `src/ds60sqlpy/module_jobs.py`
- `src/ds60sqlpy/classroom_http.py`
- `scripts/docker_registry.py`
- `scripts/prepare_kubernetes.py`
- `.env.example`
- `.github/workflows/publish-images.yml`
- `compose.classroom.yaml`

---

*Integration audit: 2026-11-23*
