# DS60 PostgreSQL: the pinned official image with current Debian security
# updates and gosu rebuilt from its tagged source with a patched Go toolchain.
# The upstream gosu binary was linked with an older Go standard library that
# image scanners flag; the source, flags and behavior are otherwise unchanged.
ARG DS60_GOSU_GO_IMAGE=golang:1.26-trixie@sha256:cff05dd6b81c901f2e8249eb6f91c69a60451d0f12c26bfef08e476a85b32d4d
ARG DS60_POSTGRES_BASE_IMAGE=postgres:17.12-trixie@sha256:223efeb196329b55b3b9a13db144956411dbc18e727e59f681c3e0aede6475cf

FROM ${DS60_GOSU_GO_IMAGE} AS gosu
ENV CGO_ENABLED=0 GOFLAGS=-trimpath
WORKDIR /src
# GitHub's archive of the gosu 1.20 tag; BuildKit verifies the digest before
# use and go.sum verifies every module the build downloads. gosu 1.20 pins
# golang.org/x/sys v0.1.0, which has fixed advisories, so the build moves it
# to a current release verified against the Go checksum database.
ADD --checksum=sha256:207a2045e890d3ca3326027c5f585733085960b401a49dbc00e3bb628c054cf8 \
    https://github.com/tianon/gosu/archive/refs/tags/1.20.tar.gz /tmp/gosu.tar.gz
RUN tar -xzf /tmp/gosu.tar.gz --strip-components=1 \
    && go get golang.org/x/sys@v0.50.0 \
    && go mod tidy \
    && go mod verify \
    && go build -ldflags='-s -w' -o /out/gosu . \
    && /out/gosu --version

FROM ${DS60_POSTGRES_BASE_IMAGE}
LABEL org.opencontainers.image.title="DS60 PostgreSQL" \
    org.opencontainers.image.version="2.1.0" \
    org.opencontainers.image.description="PostgreSQL 17 for the DS60 classroom with Debian security updates and gosu rebuilt from source" \
    org.opencontainers.image.source="https://github.com/sadatnfs/ds60sqlpy" \
    org.opencontainers.image.url="https://github.com/sadatnfs/ds60sqlpy" \
    org.opencontainers.image.licenses="PostgreSQL AND Apache-2.0" \
    org.opencontainers.image.created=""
# The pinned base can lag Debian security fixes; apply them at build time.
# GnuPG only verified the upstream apt keys, and postgresql-common needs
# sysusers and tmpfiles rather than the full systemd, so both are removed to
# shrink what the image ships and scans.
# hadolint ignore=DL3005
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        systemd-standalone-sysusers systemd-standalone-tmpfiles \
    && apt-get purge -y --auto-remove \
        dirmngr gnupg gnupg-l10n gpg gpg-agent gpgconf gpgsm systemd \
    && rm -rf /var/lib/apt/lists/*
COPY --from=gosu /out/gosu /usr/local/bin/gosu
RUN gosu --version && gosu nobody true
ARG DS60_SOURCE_REVISION=""
LABEL org.opencontainers.image.revision="${DS60_SOURCE_REVISION}"
