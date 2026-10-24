# Contributor formatting toolchain

This directory is the complete build context for the local formatting and
linting image. It contains tools and configuration only. Learner files, course
content and Git history are not copied into the image. The root formatting
script mounts the checkout and runs the prepared tools without network access.

The image supports Linux `amd64` and `arm64`. Windows contributors run the same
Linux image through WSL 2 and their Docker engine. It does not start classroom
services or change learner volumes.

## Prepared tools

| Sources | Tool and pinned release |
| --- | --- |
| Python and Python notebook cells | Ruff 0.16.0 |
| JavaScript, TypeScript, JSON, CSS, HTML and YAML | Prettier 3.6.2 |
| Java | prettier-plugin-java 2.7.7 |
| XML, including C# project files | @prettier/plugin-xml 3.4.2 |
| TOML | prettier-plugin-toml 2.0.6 |
| C, C++ and C# | clang-format 21.1.8 |
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

JavaScript and TypeScript linting uses ESLint 9.39.1, typescript-eslint 8.47.0,
TypeScript 5.9.3 and globals 16.5.0. ShellCheck is supplied by Ubuntu 24.04.
Offline source parsing uses tree-sitter-language-pack 0.13.0 with its exact
compatible grammar dependencies. PostgreSQL parsing uses pglast 7.21.
These syntax checks do not compile, execute or type-check every language.

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
and owned-fence synchronization have separate repository gates. The public root
script manages the actual local image tag. Use the smoke command when changing
the toolchain itself, alongside the repository checks.
