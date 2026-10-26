# Contributor formatting toolchain

This directory is the build context for the Ubuntu formatting and linting
image. R uses a separate image to retain its compatible R system libraries.
Its `Dockerfile.r` builds from the repository root and copies only the existing
hash-locked R package list and installer; the root Docker ignore policy excludes
private state and Git history. No course files are copied into either image.
The host wrapper mounts the checkout and runs both prepared tools without
network access or an engine socket inside the containers.

The image supports Linux `amd64` and `arm64`. Windows contributors run the same
Linux image through WSL 2 and their Docker engine. It does not start classroom
services or change learner volumes.

## Shared entrypoints

Run from the repository root with a local Linux-container engine:

```sh
./scripts/format-repo
./scripts/format-repo --check
./scripts/lint-repo
./scripts/format-repo --list
```

The wrapper derives a local `ds60-formatting` image tag from its tool context,
excluding the separately owned R Dockerfile. `ds60-formatting-r` depends only
on that R Dockerfile and the shared R lock/installer, not lesson or runtime
source files. First use builds selected tools with visible logs; unchanged
preparation reuses them. `--build` explicitly rebuilds selected tools.
The unfiltered pass runs R first, then the remaining formatters, then refreshes
its owned generated views. A failed R pass stops that chain. Shared regeneration
compiles the lesson TeX before building readers;
`--language NAME` narrows source adapters and omits shared reader refresh.
Check/list/lint modes mount source read-only. Listing uses the existing inventory
without preparing the R image. `--language r` uses only the R image and does not
refresh shared readers. Mixed language selections run the relevant isolated
passes without duplicating R checks. The wrapper requires a local
Unix-socket context because a remote engine cannot safely interpret this
checkout's bind path. It never mounts an engine socket inside the tool container.

This README is excluded from the image build context and fingerprint. Updating
instructions therefore reuses the same tools. Dockerfile, locks, wrappers and
`.dockerignore` remain fingerprinted; a tool-input change selects a new image.

## Prepared tools

| Sources | Tool and pinned release |
| --- | --- |
| Python and Python notebook cells | Ruff 0.16.0 |
| R source (`.R` and `.r`) | R 4.6.1, styler 1.11.0 and lintr 3.4.0 in the separate R image |
| JavaScript, TypeScript, JSON, CSS, HTML and YAML | Prettier 3.6.2 |
| Java | prettier-plugin-java 2.7.7 |
| XML, including C# project files | @prettier/plugin-xml 3.4.2 |
| PHP | @prettier/plugin-php 0.26.0 |
| TOML | prettier-plugin-toml 2.0.6 |
| C, C++, CUDA C++ and C# | clang-format 21.1.8 |
| Go | gofmt from Go 1.27.3 |
| Rust | rustfmt from Rust 1.99.1, edition 2024 |
| Swift | swift-format from Swift 6.3.3 |
| Scala | Scalafmt 3.11.5, Scala 2.13 dialect |
| PostgreSQL | pgFormatter 5.11 |
| Shell | shfmt 3.12.0 |
| Dockerfiles | dockerfmt 0.5.4 |
| CMake | cmakelang 0.6.13 |

Markdown is deliberately outside Prettier formatting. Prose, bare technical
identifiers, inline code and ordinary fences retain their authored text. The
repository's reviewed prose and mathematical normalizers own permitted text
repairs. The separate statistics-book synchronizer updates only manifest-linked
complete Python fences after independently proving AST equivalence with the
styled example files. Other subjects' frozen fences remain unchanged.

R source checks use `Rscript --vanilla` and stdin. Formatting uses styler's
line-break scope and independently compares parsed expressions before any
write, preserving executable meaning and literal values. Invalid syntax or a
changed parse fails without replacing the source. Lint uses fixed lexical
lintr rules plus R's parser, with cache and ambient `.lintr` settings disabled.
It does not evaluate learner expressions, load `.Rprofile`, install packages,
or infer that an R model is statistically valid. R Markdown and Quarto prose
are not silently executed or reformatted by this source adapter.

The isolated image can run `python3 docker/formatting/smoke.py --r-only` with the
repository mounted. This checks idempotence, protected literal spacing, valid
and invalid parsing, lint and a source-side-effect sentinel without executing
the supplied source. The ordinary smoke command remains specific to the Ubuntu
toolchain.

JavaScript and TypeScript linting uses ESLint 9.39.1, typescript-eslint 8.47.0,
TypeScript 5.9.3 and globals 16.5.0. ShellCheck is supplied by Ubuntu 24.04.
Offline source parsing uses tree-sitter-language-pack 0.13.0 with its exact
compatible grammar dependencies. PostgreSQL parsing uses pglast 7.21.
These syntax checks do not compile, execute or type-check every language.
PHP parsing and CUDA C++ formatting do not qualify an HTTP server or a GPU.
Use actual profile checks for those execution claims.

The image also includes the source reader's locked latex2mathml and Pygments
versions so the formatting script can regenerate published readers. See the
root contributor documentation for the public commands and generated-file
policy.

## Deliberate upgrades

Language image references include release digests. npm uses `package-lock.json`
and disables package install scripts. Python uses exact versions and
`--require-hashes`; `requirements.lock` covers the supported Linux wheel
architectures. The pinned Go module versions are verified through Go's checksum
database. `install-downloads.py` verifies SHA-256 before installing the exact
Scalafmt and pgFormatter archives. Do not disable TLS verification or add local
proxy credentials or certificates to this directory.

To change a tool version, update its pin and applicable lockfile, run the
cross-language smoke check in the newly built image, apply the formatter, then
run formatting and lint checks again. Review semantic changes and regenerate
readers before committing. An operating-system security update can change base
utilities without changing formatter versions; the image is not claimed to be
bit-for-bit reproducible across all build dates.

The final image copies only the formatter and necessary Swift/Rust shared
libraries. Full build SDKs remain in discarded build stages. You can select a
public npm mirror with the Docker build argument `NPM_REGISTRY`; default builds
use the public npm registry. Registry overrides must still retain TLS and
lockfile integrity verification.

## Tool smoke check

After preparing the image, run the smoke script with the checkout mounted at
`/workspace` and the container network disabled:

```sh
docker run --rm --network none --read-only --tmpfs /tmp \
  --mount "type=bind,src=$PWD,dst=/workspace,readonly" \
  <your-formatting-image> python3 docker/formatting/smoke.py
```

It exercises the configured syntax formatters, checks that a second pass is
unchanged, and checks SQL literal and psql directive boundaries. Prose rendering
and owned-fence synchronization have separate repository gates. Replace `<your-formatting-image>` with the actual `ds60-formatting` tag prepared
by the wrapper and shown in the local image inventory; do not guess a version.
The public root script manages that fingerprinted tag. Use the smoke command when changing
the toolchain itself, alongside the repository checks.
