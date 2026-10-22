ARG DS60_BASE_IMAGE=python:3.12-slim-bookworm
FROM ${DS60_BASE_IMAGE}

LABEL org.opencontainers.image.title="DS60 Learning Lab" \
    org.opencontainers.image.version="0.3.0" \
    org.opencontainers.image.description="Local Python and PostgreSQL learning application" \
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
       > /etc/apt/sources.list.d/pgdg.sources \
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
RUN --mount=type=cache,target=/root/.cache/uv \
    python /tmp/ds60-docker-profiles.py --profiles "$DS60_DOCKER_PROFILES"
COPY . .
RUN uv pip install --offline --python /opt/course/.venv/bin/python \
       --no-deps --no-build-isolation -e . \
    && mkdir /workspace && chown learner:learner /workspace
EXPOSE 8765
ENTRYPOINT ["python", "/opt/course/docker/entrypoint.py"]
CMD ["python", "/opt/course/docker/start_lab.py"]
