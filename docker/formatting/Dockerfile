# Build from docker/formatting, so learner files and the Git database never enter
# the build context. Release digests match the classroom's reviewed toolchains.
ARG BASE_IMAGE=ubuntu:24.04@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac
ARG GO_IMAGE=golang:1.27.3-bookworm@sha256:972b4110ba0f47539a975c31e52c64765e1ff19f2d74469ae4a595c6676e80a5
ARG RUST_IMAGE=rust:1.99.1-bookworm@sha256:48b7f435b8fc6378ce43b44f15e3a47fd8919b2825f835c39bd4bd3da50af5b8
ARG NODE_IMAGE=node:24.22.1-bookworm-slim@sha256:55fb5f5a527ea2c5c4a95f963e48ef90aa38c7b346054fdc8ee9957a2b55d205
ARG SWIFT_IMAGE=swift:6.3.3-noble@sha256:c2f3ac2eb806ce43f68859c3d52bd3bb1cfc88672fb3a948b76e136d98e39278

FROM ${GO_IMAGE} AS go-tools
ENV CGO_ENABLED=0 GOTOOLCHAIN=local GOBIN=/opt/bin
RUN go install mvdan.cc/sh/v3/cmd/shfmt@v3.12.0 \
    && go install github.com/reteps/dockerfmt@v0.5.4

FROM ${RUST_IMAGE} AS rust-tools
RUN rustup component add rustfmt \
    && mkdir -p /opt/rust-format/bin /opt/rust-format/lib \
    && cp "$(rustup which rustfmt)" /opt/rust-format/bin/rustfmt \
    && cp "$(rustc --print sysroot)"/lib/*.so* /opt/rust-format/lib/

FROM ${NODE_IMAGE} AS node-tools
WORKDIR /opt/formatters
COPY package.json package-lock.json ./
ARG NPM_REGISTRY=https://registry.npmjs.org
RUN npm ci --ignore-scripts --no-audit --no-fund --registry=${NPM_REGISTRY}

FROM ${SWIFT_IMAGE} AS swift-tools
RUN mkdir -p /opt/swift-format/bin /opt/swift-format/lib \
    && cp "$(command -v swift-format)" /opt/swift-format/bin/swift-format \
    && ldd "$(command -v swift-format)" | awk '$3 ~ /\/lib\/swift\// { print $3 }' | xargs -r cp -L -t /opt/swift-format/lib/

FROM ${BASE_IMAGE}
ARG TARGETARCH
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git perl python3 python3-venv shellcheck libstdc++6 libatomic1 libzstd1 zlib1g \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/formatters
COPY requirements.lock ./
RUN python3 -m venv /opt/formatters/venv \
    && /opt/formatters/venv/bin/pip install --index-url https://pypi.org/simple --no-cache-dir --require-hashes --only-binary=:all: -r requirements.lock
COPY install-downloads.py ./
RUN TARGETARCH=${TARGETARCH} python3 install-downloads.py
COPY --from=go-tools /usr/local/go/bin/gofmt /usr/local/bin/gofmt
COPY --from=go-tools /opt/bin/ /usr/local/bin/
COPY --from=rust-tools /opt/rust-format/ /opt/rust-format/
RUN ln -s /opt/rust-format/bin/rustfmt /usr/local/bin/rustfmt
COPY --from=node-tools /usr/local/bin/node /usr/local/bin/node
COPY --from=node-tools /opt/formatters/node_modules/ /opt/formatters/node_modules/
COPY --from=swift-tools /opt/swift-format/ /opt/swift-format/
COPY swift-format /usr/local/bin/swift-format
COPY prettier /usr/local/bin/prettier
RUN ln -s /opt/formatters/node_modules/eslint/bin/eslint.js /usr/local/bin/eslint
ENV PATH=/opt/formatters/venv/bin:${PATH} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    RUFF_CACHE_DIR=/tmp/ruff-cache
RUN ruff --version && prettier --version && clang-format --version \
    && rustfmt --version && swift-format --version && scalafmt --version \
    && pg_format --version && shfmt --version && dockerfmt version \
    && cmake-format --version
WORKDIR /workspace
CMD ["python3", "scripts/format_repo.py", "--check"]
