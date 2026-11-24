ARG DS60_BASE_IMAGE=python:3.12.16-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
ARG DS60_TEX_NODE_IMAGE=node:24.22.3-trixie-slim@sha256:af02d57b57719b9657a45199a79264a9437940cd55b3c7b3fc99615654f124a0
FROM ${DS60_TEX_NODE_IMAGE} AS lesson-tex
WORKDIR /compile
COPY scripts/compile_lesson_tex.mjs scripts/compile_lesson_tex.mjs
COPY src/ds60sqlpy/assets/vendor/textbook/katex.js src/ds60sqlpy/assets/vendor/textbook/katex.js
COPY curriculum/tex-inputs.json /compile/tex-inputs.json
RUN node scripts/compile_lesson_tex.mjs <tex-inputs.json >compiled-tex.json

FROM ${DS60_BASE_IMAGE}

LABEL org.opencontainers.image.title="DS60 Learning Lab" \
    org.opencontainers.image.version="1.4.3" \
    org.opencontainers.image.description="Local classroom for programming, data science and machine learning" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy" \
    org.opencontainers.image.url="https://github.com/sadatnfs/ds60sqlpy" \
    org.opencontainers.image.licenses="Apache-2.0" \
    org.opencontainers.image.created=""

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_CONTAINER=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never \
    _PIP_USE_IMPORTLIB_METADATA=1
# Apply Debian security updates newer than the pinned base image.
# hadolint ignore=DL3005
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    curl ca-certificates gosu libgomp1 \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl --fail --silent --show-error --location --retry 3 \
        https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
    && . /etc/os-release \
    && printf 'Types: deb\nURIs: https://apt.postgresql.org/pub/repos/apt\nSuites: %s-pgdg\nArchitectures: %s\nComponents: main\nSigned-By: /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc\n' \
        "$VERSION_CODENAME" "$(dpkg --print-architecture)" \
        >/etc/apt/sources.list.d/pgdg.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-17 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 learner
WORKDIR /opt/course
ARG DS60_DOCKER_PROFILES=core
ENV DS60_DOCKER_PROFILES=${DS60_DOCKER_PROFILES}
ENV PATH="/opt/course/.venv/bin:$PATH"
COPY requirements/bootstrap-pip.lock /tmp/bootstrap-pip.lock
COPY requirements/bootstrap-uv.lock /tmp/bootstrap-uv.lock
# Optional anonymous mirror for restricted networks; every install below is hash-locked.
ARG DS60_PYTHON_INDEX_URL
# Every later install uses uv, so the base interpreter's pip is removed once uv is in place.
RUN python -m pip install ${DS60_PYTHON_INDEX_URL:+--index-url "$DS60_PYTHON_INDEX_URL"} --no-cache-dir \
    --require-hashes -r /tmp/bootstrap-pip.lock \
    && python -m pip install ${DS60_PYTHON_INDEX_URL:+--index-url "$DS60_PYTHON_INDEX_URL"} --no-cache-dir \
    --require-hashes -r /tmp/bootstrap-uv.lock && rm /tmp/bootstrap-pip.lock /tmp/bootstrap-uv.lock \
    && python -m pip uninstall --yes pip
COPY pyproject.toml uv.lock README.md ./
COPY src/ds60sqlpy/docker_profiles.py /tmp/ds60-docker-profiles.py
ARG DS60_UV_CACHE_ID=ds60sqlpy-uv-v1
RUN --mount=type=cache,id=${DS60_UV_CACHE_ID},target=/root/.cache/uv \
    python /tmp/ds60-docker-profiles.py --profiles "$DS60_DOCKER_PROFILES"
COPY . .
COPY --from=lesson-tex /compile/compiled-tex.json /opt/course/src/ds60sqlpy/assets/vendor/textbook/compiled-tex.json
# Normalize only public source lacking read/traverse permissions. Keep ownership
# and write bits; prune the large dependency environment to avoid overlay copy-up.
# The learner pip never loads its vendored pkg_resources (importlib.metadata is
# pinned above), so it is removed and pip's SBOM, vendor.txt and RECORD rewritten.
RUN uv pip install --offline --python /opt/course/.venv/bin/python \
    --no-deps --no-build-isolation -e . \
    && /opt/course/.venv/bin/python docker/prune_pip_vendor.py \
    && python scripts/compile_lesson_tex.py --check-inputs \
    && find /opt/course -path /opt/course/.venv -prune -o \
        -type d ! -perm -055 -exec chmod go+rx {} + -o \
        -type f ! -perm -044 -exec chmod go+rX {} + \
    && mkdir /workspace && chown learner:learner /workspace
EXPOSE 8765
ENTRYPOINT ["python", "/opt/course/docker/entrypoint.py"]
CMD ["python", "/opt/course/docker/start_lab.py"]
# Keep the revision last so a new commit reuses every earlier cached layer.
ARG DS60_SOURCE_REVISION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}"
