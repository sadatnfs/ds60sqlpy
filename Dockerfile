ARG DS60_BASE_IMAGE=python:3.12-slim-bookworm
ARG DS60_TEX_NODE_IMAGE=node:24.22.1-bookworm-slim@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205
FROM ${DS60_TEX_NODE_IMAGE} AS lesson-tex
WORKDIR /compile
COPY scripts/compile_lesson_tex.mjs scripts/compile_lesson_tex.mjs
COPY src/ds60sqlpy/assets/vendor/textbook/katex.js src/ds60sqlpy/assets/vendor/textbook/katex.js
COPY curriculum/tex-inputs.json /compile/tex-inputs.json
RUN node scripts/compile_lesson_tex.mjs <tex-inputs.json >compiled-tex.json

FROM ${DS60_BASE_IMAGE}

LABEL org.opencontainers.image.title="DS60 Learning Lab" \
    org.opencontainers.image.version="1.2.0" \
    org.opencontainers.image.description="Local classroom for programming, data science and machine learning" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy" \
    org.opencontainers.image.url="https://github.com/sadatnfs/ds60sqlpy" \
    org.opencontainers.image.licenses="Apache-2.0" \
    org.opencontainers.image.revision="" org.opencontainers.image.created=""

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DS60_CONTAINER=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gosu libgomp1 libexpat1 \
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
RUN python -m pip install --no-cache-dir uv==0.11.6
COPY pyproject.toml uv.lock README.md ./
COPY src/ds60sqlpy/docker_profiles.py /tmp/ds60-docker-profiles.py
ARG DS60_UV_CACHE_ID=ds60sqlpy-uv-v1
RUN --mount=type=cache,id=${DS60_UV_CACHE_ID},target=/root/.cache/uv \
    python /tmp/ds60-docker-profiles.py --profiles "$DS60_DOCKER_PROFILES"
COPY . .
COPY --from=lesson-tex /compile/compiled-tex.json /opt/course/src/ds60sqlpy/assets/vendor/textbook/compiled-tex.json
# Normalize only public source lacking read/traverse permissions. Keep ownership
# and write bits; prune the large dependency environment to avoid overlay copy-up.
RUN uv pip install --offline --python /opt/course/.venv/bin/python \
    --no-deps --no-build-isolation -e . \
    && python scripts/compile_lesson_tex.py --check-inputs \
    && find /opt/course -path /opt/course/.venv -prune -o \
        -type d ! -perm -055 -exec chmod go+rx {} + -o \
        -type f ! -perm -044 -exec chmod go+rX {} + \
    && mkdir /workspace && chown learner:learner /workspace
EXPOSE 8765
ENTRYPOINT ["python", "/opt/course/docker/entrypoint.py"]
CMD ["python", "/opt/course/docker/start_lab.py"]
