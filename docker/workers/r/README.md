# Locked R package builds and diagnostics

`install_packages.py` installs the reviewed, topologically ordered CRAN source
closure in `packages.lock.json`. Downloads remain SHA-256 verified and the R
version check remains mandatory. A failed installation stops the build; later
packages are not attempted.

CRAN can rate-limit simultaneous source builds. HTTP 429, 502, 503 and 504
responses retry the same reviewed URL at most five times, with bounded backoff
and a maximum 60-second numeric Retry-After delay. Every retry remains visible.
The original SHA-256 check still applies to successful downloads; no unverified
mirror or replacement version is selected. A missing archive retains the
existing explicit archive-URL fallback, and exhausted retries fail the build.

The locked `sass` package compiles vendored libsass. Its headers produce repeated
GCC `-Woverloaded-virtual` diagnostics across translation units. The installer
prints each distinct complete warning block, including its source excerpt,
notes and overload context, once per package build. It reports the number of
exact repeated blocks and lines summarized. This changes console presentation
only: compiler flags and warning policy are unchanged. Other packages, warning
categories, errors, compiler commands and unrecognized output remain visible.
A different note or source excerpt creates a distinct block and is printed.

Complete merged stdout/stderr is retained byte for byte in compressed logs at
`/usr/local/share/ds60-build-logs/r/`. Each package has a `.log.gz` and JSON
receipt recording its locked archive hash, raw log hash and size, compressed
log hash, exit status and summarized counts. `manifest.json` indexes completed
package attempts. These are build diagnostics, not learner state or runtime
qualification receipts. The retained files are small relative to the installed
R dependencies and contain no registry credentials.

On installation failure, the installer also replays that package's complete
original output to the build console. This preserves diagnostics in the hosted
job log even when Docker cannot export the failed layer. The original nonzero
exit code remains a failure. A successful source build still needs the ordinary
R worker reference, failure and lifecycle checks.

To inspect a successful prepared image without starting the worker, create an
owned stopped container, copy this directory out, then remove only that
container. For example, with an already available local image:

```sh
docker create --pull=never --name ds60-r-build-log-export --entrypoint /bin/true IMAGE
docker cp ds60-r-build-log-export:/usr/local/share/ds60-build-logs/r ./r-build-logs
docker rm ds60-r-build-log-export
python3 -m gzip -d r-build-logs/sass_0.4.10.log.gz
```

Use a unique owned container name and retain the `.json` receipts alongside the
logs. This procedure neither pulls images nor changes learner volumes. Hosted
publication should retain these files as build-log artifacts for each native
architecture; they do not replace numerical/runtime acceptance.
